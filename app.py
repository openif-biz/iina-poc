# FILE: app.py (2-Step UI with Dummy Analyzer)
# PURPOSE: To verify the multi-step UI flow on the Linode server.
# DESIGNER: Yuki (Project Owner) & ChatGPT
# ENGINEER: Gemini (Chief Engineer)

import json
import time
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="IINA PoC", page_icon="🤖", layout="wide")

# --- Session State Initialization ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "proposal" not in st.session_state:
    st.session_state.proposal = None
if "io_spec" not in st.session_state:
    st.session_state.io_spec = None

# --- Dummy Analyzer (to be replaced with your LLM call) ---
def analyze_first_prompt(user_text: str) -> dict:
    # This is a placeholder. Replace this with your actual model call (llama/StarCoder etc.)
    time.sleep(2) # Simulate AI thinking
    flow = [
        "ユーザー入力の正規化",
        "ルール抽出（IN/OUT/TOの初期推定）",
        "自動化候補タスクの列挙",
        "最小構成PoCの提示",
    ]
    proposals = [
        "無料ツール中心での最小自動化（Zapier無料枠やローカルスクリプト）",
        "将来拡張: 有料API連携でスケール（Gmail API / Slack / ストレージ等）",
    ]
    return {
        "summary": f"要点要約（ダミー）: {user_text[:60]}...",
        "flow": flow,
        "proposals": proposals,
    }

# --- JSON Saver (for SAVAN handoff) ---
def save_handoff(obj: dict, prefix: str) -> Path:
    out_dir = Path("./handoff")
    out_dir.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    p = out_dir / f"{prefix}_{ts}.json"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return p

# --- Header ---
st.title("IINA PoC（2ステップUI）")
st.caption("Step1: 分析 → Step2: 提案＆簡易フロー → 同意なら仕様ヒアリング（IN/OUT/TO）→ SAVANへハンドオフ")

# ========== STEP 1: User Input & Analysis ==========
if st.session_state.step == 1:
    st.subheader("Step 1｜課題入力")
    user_text = st.text_area(
        "あなたの業務課題や自動化したいことを日本語で書いてください。",
        height=180,
        key="first_prompt_text",
        placeholder="例）毎朝の売上CSV集計→グラフ→Slack共有を自動化したい… など",
    )
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("分析する（第1プロンプト）", type="primary", use_container_width=True):
            if not user_text.strip():
                st.warning("入力が空です。内容を入力してください。")
            else:
                with st.spinner("IINAが分析中です..."):
                    st.session_state.analysis = analyze_first_prompt(user_text.strip())
                st.session_state.step = 2
                st.rerun()
    with col2:
        if st.button("リセット", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ========== STEP 2: Proposal & Flow Display ==========
elif st.session_state.step == 2:
    a = st.session_state.analysis
    if not a:
        st.warning("分析結果が見つかりません。Step1からやり直してください。")
        if st.button("Step1へ戻る"):
            st.session_state.step = 1
            st.rerun()
    else:
        st.subheader("Step 2｜提案概要 & 簡易フロー（第1結果の可視化）")
        with st.expander("要点要約", expanded=True):
            st.write(a["summary"])
        colA, colB = st.columns([1,1])
        with colA:
            st.markdown("#### 簡易フロー")
            for i, step in enumerate(a["flow"], 1):
                st.write(f"{i}. {step}")
        with colB:
            st.markdown("#### 自動化の提案（概要）")
            for p in a["proposals"]:
                st.write(f"- {p}")

        st.divider()
        st.markdown("**この提案で具体化を進めますか？（IN/OUT/TOヒアリングへ）**")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("この提案で進める（第2プロンプトへ）", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
        with c2:
            if st.button("やり直す（Step1へ）", use_container_width=True):
                st.session_state.step = 1
                st.rerun()

# ========== STEP 3: Second Prompt (IN/OUT/TO Hearing) ==========
elif st.session_state.step == 3:
    st.subheader("Step 3｜仕様ヒアリング（IN / OUT / TO）")
    with st.form("io_form", clear_on_submit=False):
        st.markdown("**IN（入力データ）**")
        in_desc = st.text_area("どんなデータを取り込みますか？形式・取得元など", height=120)

        st.markdown("**OUT（出力）**")
        out_desc = st.text_area("生成物は？例：PDFレポート/CSV/Slack投稿 など", height=120)

        st.markdown("**TO（保存・送付先）**")
        to_place = st.selectbox(
            "保存・送付先",
            ["ローカルPC", "Linodeサーバー", "メール送付", "S3互換ストレージ"],
        )

        st.markdown("**追加条件**")
        budget = st.radio("有料アカウントの利用", ["できるだけ無料", "必要なら有料OK"], index=0)
        note = st.text_input("補足（任意）")

        submitted = st.form_submit_button("仕様を確定してSAVANへ渡す")
    if submitted:
        spec = {
            "analysis": st.session_state.analysis,
            "io_spec": {
                "IN": in_desc,
                "OUT": out_desc,
                "TO": to_place,
                "BUDGET": budget,
                "NOTE": note,
            },
            "timestamp": time.time(),
        }
        st.session_state.io_spec = spec
        path = save_handoff(spec, prefix="iina_spec")
        st.success(f"仕様を保存しました: {path}")
        st.json(spec, expanded=False)

        st.info("次：SAVANがこの仕様JSONを取りに来てコード生成 → あなたに試作品を返す想定です。")
        if st.button("最初の画面へ戻る"):
            st.session_state.clear()
            st.rerun()

