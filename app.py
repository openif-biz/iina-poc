# FILE: app.py
# PURPOSE: IINA PoC Web Frontend (Reception Desk) - Final Version
# DESIGNER: Yuki (Project Owner)
# ENGINEER: Gemini (Chief Engineer)

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
import datetime
import os
import pandas as pd

# --- Configuration ---
# These environment variables are set by docker-compose.yml
TARGET_FOLDER_ID = os.environ.get("TARGET_FOLDER_ID", "")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

# --- Google Drive Authentication ---
@st.cache_resource
def get_gdrive_service():
    """Connects to Google Drive API using Application Default Credentials."""
    try:
        scopes = ['https://www.googleapis.com/auth/drive']
        
        if not GOOGLE_APPLICATION_CREDENTIALS:
             st.error("Google認証情報(GOOGLE_APPLICATION_CREDENTIALS)が設定されていません。")
             return None

        creds = Credentials.from_service_account_file(
            GOOGLE_APPLICATION_CREDENTIALS,
            scopes=scopes
        )
        service = build('drive', 'v3', credentials=creds)
        st.success("Google Driveへの接続に成功しました。")
        return service
    except FileNotFoundError:
        st.error(f"認証ファイルが見つかりません: {GOOGLE_APPLICATION_CREDENTIALS}")
        st.error("サーバー上にiina-key.jsonが正しく配置されているか、docker-compose.ymlのvolumes設定を確認してください。")
        return None
    except Exception as e:
        st.error(f"Google Driveへの接続中にエラーが発生しました: {e}")
        st.error("認証情報(iina-key.json)の内容や、Google Drive APIの権限、フォルダの共有設定を確認してください。")
        return None

# --- Function to save data to Google Drive ---
def save_to_drive(service, folder_id, filename, data):
    """Saves a dictionary as a text file to the specified Google Drive folder."""
    try:
        from io import StringIO
        import googleapiclient.http

        if not folder_id:
            st.error("保存先のGoogle Drive フォルダIDが設定されていません。")
            return None

        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        content = json.dumps(data, ensure_ascii=False, indent=2)
        media = googleapiclient.http.MediaIoBaseUpload(StringIO(content), mimetype='text/plain; charset=utf-8')
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    except Exception as e:
        st.error(f"Google Driveへのファイル保存中にエラーが発生しました: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="IINA PoC - 受付", layout="wide")
st.title("IINA PoC - 課題受付フォーム")
st.markdown("AIコンサルタントIINAが分析するため、以下のアンケートにご協力ください。")

gdrive_service = get_gdrive_service()

if gdrive_service:
    with st.form("iina_reception_form", clear_on_submit=True):
        st.header("自動化・効率化アンケート")
        
        fields = {
            "インプット": "例: 各社オリジナル形式の請求書のPDF",
            "現状": "例: 一帳票づつ読取って手作業での入力に時間がかかっている",
            "課題": "例: 入力ミスが多く、確認作業に追われ、他の業務が滞る",
            "目的": "例: 差配対応などのマネジメントに集中したい",
            "理想の状態": "例: 進行中の全受注案件の進捗管理の精度を上げる",
            "制約条件": "例: 新たな有料サービスを利用することは望まない",
            "アウトプット": "例: 請求台帳に指定項目をGoogleスプレッドシートへ入力"
        }
        
        input_data = {}
        for field, caption_text in fields.items():
            st.subheader(field)
            st.caption(caption_text)
            unique_key = f"input_{field}"
            if field in ["現状", "課題", "目的", "理想の状態", "アウトプット"]:
                input_data[field] = st.text_area(unique_key, label_visibility="collapsed")
            else:
                input_data[field] = st.text_input(unique_key, label_visibility="collapsed")

        submitted = st.form_submit_button("IINAに送信する", type="primary")

    if submitted:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iina_input_{timestamp}.txt"
        
        non_empty_data = {k: v for k, v in input_data.items() if v}
        
        if not non_empty_data:
            st.warning("いずれかの項目に入力してください。")
        else:
            with st.spinner(f"データをGoogle Driveに安全に送信しています..."):
                file_id = save_to_drive(gdrive_service, TARGET_FOLDER_ID, filename, non_empty_data)
            
            if file_id:
                st.success("お客様の課題を承りました。")
                st.info("ローカルPC上のIINAエンジンが、間もなく分析を開始します。")
                st.balloons()
            else:
                st.error("送信に失敗しました。お手数ですが、もう一度お試しください。")
else:
    st.warning("現在、受付システムがメンテナンス中です。しばらくしてから再度お試しください。")

