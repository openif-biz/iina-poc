import os
import streamlit as st
import requests

st.set_page_config(page_title="IINA PoC - 受付", layout="wide")
st.title("IINA PoC - 課題受付フォーム")
st.markdown("ローカルのIINA（ngrok経由）にデータを送り、提案概要を受け取ります。")

NGROK_URL = os.environ.get("NGROK_URL", "").rstrip("/")
IINA_KEY_PATH = os.environ.get("IINA_KEY_PATH", "")

if not NGROK_URL:
    st.error("ローカルAIエンジンへの接続トンネル (NGROK_URL) が設定されていません。")
else:
    st.success(f"ローカルAIエンジン ({NGROK_URL}) への接続準備が完了しました。")

    with st.form("iina_reception_form"):
        st.header("自動化・効率化アンケート（例を参考に記入）")

        fields = {
            "インプット": "例: 各社オリジナル形式の請求書のPDF",
            "現状": "例: 一帳票ずつ読み取り→手入力で時間がかかる",
            "課題": "例: 入力ミスが多く確認作業に追われる",
            "目的": "例: マネジメントに集中したい",
            "理想の状態": "例: 受注管理が自動化される",
            "制約条件": "例: 追加コストを抑えたい（無料優先）",
            "アウトプット": "例: Googleスプレッドシートへ自動入力"
        }

        input_data = {}
        for field, hint in fields.items():
            st.subheader(field)
            st.caption(hint)
            key = f"f_{field}"
            if field in ["現状", "課題", "目的", "理想の状態", "アウトプット"]:
                input_data[field] = st.text_area(key, height=110)
            else:
                input_data[field] = st.text_input(key)

        submitted = st.form_submit_button("ローカルIINAに送信する")

    if submitted:
        is_empty = all(isinstance(v, str) and v.strip() == "" for v in input_data.values())
        if is_empty:
            st.warning("いずれかの項目に入力してください。")
        else:
            with st.spinner("ローカルAIエンジンへ送信中..."):
                try:
                    post_url = NGROK_URL + "/analyze"
                    resp = requests.post(post_url, json=input_data, timeout=60)
                    resp.raise_for_status()
                    result = resp.json()

                    st.success("ローカルAIエンジンからの応答を受け取りました。")

                    st.markdown("## 提案概要")
                    st.write(result.get("summary", "（要約がありません）"))

                    st.markdown("## 簡易フロー")
                    flow = result.get("flow", [])
                    if flow:
                        for i, s in enumerate(flow, 1):
                            st.write(f"{i}. {s}")
                    else:
                        st.write("（簡易フローがありません）")

                    st.markdown("## 追加提案")
                    for p in result.get("proposals", []):
                        st.write("- " + p)

                    st.json(result)  # デバッグ用

                except requests.exceptions.RequestException as e:
                    st.error(f"ローカルAIエンジンへの送信中にエラー: {e}")
                    st.error(f"確認: ローカルPCでngrokとIINA(FastAPI)が起動しているか、NGROK_URL={NGROK_URL} が正しいか")
