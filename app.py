import streamlit as st
import json
import time
import requests  # SSHトンネル経由やHTTP経由でローカルAIへアクセス

st.set_page_config(page_title="IINA PoC", layout="wide")
st.title("IINA PoC - 本番仕様 (Linode窓口)")

# --- セッション状態初期化 ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# --- ローカルAI呼び出し関数 ---
def call_local_iina(user_text: str, timeout=60) -> dict:
    """
    ローカルAIにHTTPまたはSSHトンネル経由でアクセスし、分析結果を取得
    """
    try:
        # ★ 実際はSSHトンネル経由やHTTPリクエストをここで実装
        # 仮例: requests.post("http://localhost:5000/analyze", json={"text": user_text})
        # 下記はサンプル構造
        response = {
            "summary": f"提案概要: {user_text[:60]}...",
            "flow": [
                "入力データの整理",
                "自動化可能タスクの特定",
                "提案フロー作成",
                "確認用レポート生成"
            ],
            "proposals": [
                "無料ツール中心での最小自動化",
                "将来拡張: 有料API連携でスケール"
            ]
        }
        time.sleep(3)  # 疑似処理時間
        return response
    except Exception as e:
        return {"error": str(e)}

# --- STEP 1: 課題入力 ---
if st.session_state.step == 1:
    st.subheader("Step1｜課題入力")
    user_text = st.text_area(
        "業務課題や自動化したいことを日本語で入力してください",
        height=180
    )
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("分析実行"):
            if not user_text.strip():
                st.warning("入力が空です")
            else:
                with st.spinner("ローカルAIで分析中…"):
                    st.session_state.analysis = call_local_iina(user_text.strip())
                st.session_state.step = 2
                st.rerun()
    with col2:
        if st.button("リセット"):
            st.session_state.clear()
            st.rerun()

# --- STEP 2: 提案概要 & 簡易フロー表示 ---
elif st.session_state.step == 2:
    a = st.session_state.analysis
    if not a:
        st.warning("分析結果がありません。Step1からやり直してください。")
        if st.button("Step1へ戻る"):
            st.session_state.step = 1
            st.rerun()
    elif "error" in a:
        st.error(f"AI呼び出しでエラー: {a['error']}")
        if st.button("Step1へ戻る"):
            st.session_state.step = 1
            st.rerun()
    else:
        st.subheader("Step2｜提案概要 & 簡易フロー")
        with st.expander("提案概要", expanded=True):
            st.write(a["summary"])
        colA, colB = st.columns([1,1])
        with colA:
            st.markdown("#### 簡易フロー")
            for i, step in enumerate(a["flow"], 1):
                st.write(f"{i}. {step}")
        with colB:
            st.markdown("#### 自動化提案")
            for p in a["proposals"]:
                st.write(f"- {p}")

        st.divider()
        if st.button("Step1へ戻る"):
            st.session_state.step = 1
            st.rerun()
