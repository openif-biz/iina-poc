# FILE: app.py
# PURPOSE: IINA PoC Web Frontend (Reception Desk)
# DESIGNER: Yuki (Project Owner)
# ENGINEER: Gemini (Chief Engineer)
# ARCHITECTURE: This app runs on a Linode server, captures user input via a Streamlit form,
# and saves the data as a text file to a shared Google Drive folder for processing by a local AI engine.

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
import datetime
import os # osモジュールをインポート

# --- Configuration ---
# ★★★【最終修正点】★★★
# st.secretsからではなく、os.environ（環境変数）から秘密情報を読み込むように変更
GOOGLE_CREDENTIALS_JSON_STR = os.environ.get("GOOGLE_CREDENTIALS_JSON_STR", "{}")
TARGET_FOLDER_ID = os.environ.get("TARGET_FOLDER_ID", "") # The ID of the 'iina_inbox' folder on Google Drive

# --- Google Drive Authentication ---
@st.cache_resource
def get_gdrive_service():
    """Connects to Google Drive API using service account credentials."""
    try:
        # Check if credentials are provided
        if not GOOGLE_CREDENTIALS_JSON_STR or GOOGLE_CREDENTIALS_JSON_STR == "{}":
            st.error("Google認証情報が設定されていません。")
            return None
        if not TARGET_FOLDER_ID:
            st.error("Google DriveのフォルダIDが設定されていません。")
            return None

        # Load credentials from the string
        creds_json = json.loads(GOOGLE_CREDENTIALS_JSON_STR)
        scopes = ['https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        st.success("Google Driveへの接続に成功しました。")
        return service
    except json.JSONDecodeError:
        st.error("Google認証情報のフォーマットが正しくありません。(JSON Decode Error)")
        return None
    except Exception as e:
        st.error(f"Google Driveへの接続中にエラーが発生しました: {e}")
        st.error("認証情報(iina-key.json)の内容や、Google Drive APIの権限を確認してください。")
        return None

# --- Function to save data to Google Drive ---
def save_to_drive(service, folder_id, filename, data):
    """Saves a dictionary as a text file to the specified Google Drive folder."""
    try:
        from io import StringIO
        import googleapiclient.http

        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        # Convert dictionary to a formatted string
        content = json.dumps(data, ensure_ascii=False, indent=2)
        media = googleapiclient.http.MediaIoBaseUpload(StringIO(content), mimetype='text/plain')
        
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
    with st.form("iina_reception_form"):
        st.header("自動化・効率化アンケート")
        
        input_data = {}
        fields = {
            "インプット": "例: 各社オリジナル形式の請求書のPDF",
            "現状": "例: 一帳票づつ読取って手作業での入力に時間がかかっている",
            "課題": "例: 入力ミスが多く、確認作業に追われ、他の業務が滞る",
            "目的": "例: 差配対応などのマネジメントに集中したい",
            "理想の状態": "例: 進行中の全受注案件の進捗管理の精度を上げる",
            "制約条件": "例: 新たな有料サービスを利用することは望まない",
            "アウトプット": "例: 請求台帳に指定項目をGoogleスプレッドシートへ入力"
        }

        for field, placeholder in fields.items():
            if field in ["現状", "課題", "目的", "理想の状態", "アウトプット"]:
                input_data[field] = st.text_area(field, placeholder=placeholder)
            else:
                input_data[field] = st.text_input(field, placeholder=placeholder)

        submitted = st.form_submit_button("IINAに送信する", type="primary")

    if submitted:
        # Generate a unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iina_input_{timestamp}.txt"
        
        with st.spinner(f"データをGoogle Driveに安全に送信しています..."):
            file_id = save_to_drive(gdrive_service, TARGET_FOLDER_ID, filename, input_data)
        
        if file_id:
            st.success("お客様の課題を承りました。")
            st.info("ローカルPC上のIINAエンジンが、間もなく分析を開始します。")
            st.balloons()
        else:
            st.error("送信に失敗しました。お手数ですが、もう一度お試しください。")
else:
    st.warning("現在、受付システムがメンテナンス中です。しばらくしてから再度お試しください。")
