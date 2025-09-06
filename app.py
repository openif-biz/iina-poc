import json
import requests
import streamlit as st

# ====== 設定 ======
LOCAL_AI_URL = "http://localhost:8000/analyze"  
# ↑ ローカルAI (AIPC) 側のAPIエンドポイント
# SSHトンネルで接続する場合:
# ssh -L 8000:localhost:8000 user@AIPC

st.set_page_config(page_title="IINA PoC", page_icon="🤖", layout="wide")

# ====== セッション初期化 ======
if "step" not in st.session_state:
    st.session_state.step = 1
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# ====== ローカルAI呼び出し ======
def call_local_ai(user_text: str) -> dict:
    payload = {"text": user_text}
    try:
        resp = requests.post(LOCAL_AI_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": f"ローカルAI呼び出し失敗: {e}"}

# ====== ヘッダー ======
st.title("IINA PoC（Linode窓口サーバー）")
st.caption("Step1: 課題入力 → Step2: 提案概要 & 簡易フロー")

# ========== STEP 1: ユーザー入力 ==========
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
        if st.button("分析する", type="primary", use_container_width=True):
            if not user_text.strip():
                st.warning("入力が空です。内容を入力してください。")
            else:
                with st.spinner("ローカルAIが分析中です..."):
                    result = call_local_ai(user_text.strip())
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.session_state.analysis = result
                    st.session_state.step = 2
                    st.rerun()
    with col2:
        if st.button("リセット", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ========== STEP 2: 提案表示 ==========
elif st.session_state.step == 2:
    a = st.session_state.analysis
    if not a:
        st.warning("分析結果が見つかりません。Step1からやり直してください。")
        if st.button("Step1へ戻る"):
            st.session_state.step = 1
            st.rerun()
    else:
        st.subheader("Step 2｜提案概要 & 簡易フロー")
        if "summary" in a:
            with st.expander("要点要約", expanded=True):
                st.write(a["summary"])
        if "flow" in a:
            st.markdown("#### 簡易フロー")
            for i, step in enumerate(a["flow"], 1):
                st.write(f"{i}. {step}")
        if "proposals" in a:
            st.markdown("#### 自動化の提案（概要）")
            for p in a["proposals"]:
                st.write(f"- {p}")

        st.divider()
        if st.button("最初に戻る", use_container_width=True):
            st.session_state.clear()
            st.rerun()
