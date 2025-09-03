# FILE: app.py (Linode Web Frontend - Direct Forwarding Version)
# PURPOSE: To act as a reception desk on the Linode server.
# DESIGNER: Yuki (Project Owner)
# ENGINEER: Gemini (Chief Engineer)
# ARCHITECTURE: This app captures user input via a Streamlit form and forwards it directly
# to the local IINA engine running on the user's PC via an ngrok tunnel.

import streamlit as st
import requests
import json
import os

# --- Configuration ---
# The ngrok URL is now the single most important secret.
# It will be passed as an environment variable from the GitHub Actions workflow.
NGROK_URL = os.environ.get("NGROK_URL", "")

# --- Streamlit UI ---
st.set_page_config(page_title="IINA PoC - 受付", layout="wide")
st.title("IINA PoC - 課題受付フォーム")
st.markdown("AIコンサルタントIINAが分析するため、以下のアンケートにご協力ください。")

if not NGROK_URL:
    st.error("ローカルAIエンジンへの接続トンネル(ngrok URL)が設定されていません。")
    st.warning("現在、受付システムがメンテナンス中です。しばらくしてから再度お試しください。")
else:
    st.success("ローカルAIエンジンへの接続準備が完了しました。")

    with st.form("iina_reception_form"):
        st.header("自動化・効率化アンケート")

        input_data = {}
        fields = {
            "インププット": "例: 各社オリジナル形式の請求書のPDF",
            "現状": "例: 一帳票づつ読取って手作業での入力に時間がかかっている",
            "課題": "例: 入力ミスが多く、確認作業に追われ、他の業務が滞る",
            "目的": "例: 差配対応などのマネジメントに集中したい",
            "理想の状態": "例: 進行中の全受注案件の進捗管理の精度を上げる",
            "制約条件": "例: 新たな有料サービスを利用することは望まない",
            "アウトプット": "例: 請求台帳に指定項目をGoogleスプレッドシートへ入力"
        }

        for field, caption_text in fields.items():
            st.subheader(field)
            st.caption(caption_text)
            unique_key = f"input_{field}"
            if field in ["現状", "課題", "目的", "理想の状態", "アウトプット"]:
                input_data[field] = st.text_area(unique_key, label_visibility="collapsed")
            else:
                input_data[field] = st.text_input(unique_key, label_visibility="collapsed")

        submitted = st.form_submit_button("ローカルIINAに送信する", type="primary")

    if submitted:
        # Check if all fields are empty
        if all(value == "" for value in input_data.values()):
            st.warning("分析を開始するには、いずれかの項目に内容を入力してください。")
        else:
            with st.spinner("お客様の声をローカルAIエンジンに安全に送信しています..."):
                try:
                    # Send the data as a JSON payload to the ngrok URL
                    api_endpoint = f"{NGROK_URL}/process" # Assuming the local app has a /process endpoint
                    response = requests.post(api_endpoint, json=input_data, timeout=60)
                    response.raise_for_status() 

                    st.success("ローカルAIエンジンからの応答を受信しました！")
                    st.header("IINAによる分析結果")
                    
                    analysis_result = response.json()
                    st.json(analysis_result)
                    st.balloons()

                except requests.exceptions.RequestException as e:
                    st.error(f"ローカルAIエンジンへの送信中にエラーが発生しました: {e}")
                    st.error("ヒント: ローカルPCでngrokとstreamlitアプリが両方とも起動しているか確認してください。")

