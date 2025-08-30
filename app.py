# FILE: iina_poc_streamlit/app.py
# 目的: IINAの初期PoCを実現するStreamlitアプリケーション。
#       クラウド環境で動作し、Cloud Storageからモデルを動的に読み込む。

import streamlit as st
from llama_cpp import Llama
import os
import json
import re
import pandas as pd
from google.cloud import storage # 【変更点】GCSライブラリをインポート

# --- 【変更点】クラウド設定 ---
# ユキ様専用のバケット名を設定
BUCKET_NAME = "openif_20250827" 
# Cloud Storage上のモデルファイル名
MODEL_FILE_NAME = "starcoder2-7b-Q4_K_M.gguf" 
# コンテナ内に保存する際のパス
LOCAL_MODEL_PATH = f"./{MODEL_FILE_NAME}"

# --- 【変更点】AIモデルのダウンロード＆ロード機能 ---
@st.cache_resource
def load_iina_model():
    """
    モデルがローカルに存在しない場合、GCSからダウンロードし、その後ロードする。
    """
    # 1. ローカルにモデルファイルが存在するかチェック
    if not os.path.exists(LOCAL_MODEL_PATH):
        try:
            with st.spinner(f"AIモデルをクラウドからダウンロード中です...（数分かかる場合があります）"):
                # 2. GCSクライアントを初期化
                storage_client = storage.Client()
                bucket = storage_client.bucket(BUCKET_NAME)
                blob = bucket.blob(MODEL_FILE_NAME)

                # 3. GCSからファイルをダウンロード
                blob.download_to_filename(LOCAL_MODEL_PATH)
            st.success("AIモデルのダウンロードが完了しました。")
        except Exception as e:
            st.error(f"モデルのダウンロード中にエラーが発生しました: {e}")
            st.error("GCSバケット名が正しいか、Cloud Runの権限が設定されているか確認してください。")
            st.stop()

    # 4. モデルをメモリにロード
    try:
        with st.spinner("AIモデルを起動しています..."):
            llm = Llama(model_path=LOCAL_MODEL_PATH, n_ctx=4096, n_gpu_layers=0, verbose=False) # クラウドではGPUなし(n_gpu_layers=0)を想定
        return llm
    except Exception as e:
        st.error(f"モデルのロード中にエラーが発生しました: {e}")
        st.stop()


# --- プロンプトの生成 (JSON出力指示) ---
def create_iina_prompt(inputs):
    """ユーザーの入力から、AIにJSON形式で思考結果を出力させるプロンプトを生成する"""
    prompt = f"""
### 指示 ###
あなたは、ユーザーの課題を分析し、解決策の要点を構造化されたJSONデータとして出力するAIです。
警告: 解説、挨拶、その他の余計な文章は一切含めず、JSONオブジェクトのみを厳密に出力してください。

### 思考プロセス ###
1.  まず、「クライアントの相談内容」の「インプット」「アウトプット」「目的」を深く理解する。
2.  次に、「インプット」から「アウトプット」に至るまでの、具体的な作業工程を頭の中でリストアップする。（例：PDFを読み取る、必要な項目を抽出する、台帳に入力する、完了を通知する）
3.  リストアップした作業工程を、「workflow」の各ステップに割り振る。その際、**「誰が（担当者）」、「何をするか（作業内容）」を明確にすること。** 特に、**最初のステップは「【貴社】」によるインプットの提供**とし、**最後のステップは「【貴社】」による確認作業**とするなど、一連の業務の流れを意識すること。
4.  「proposal」セクションは、相談内容全体を要約して記述する。特に「summary」には、「インプット」の情報を含めること。
5.  JSONフォーマットの手本に厳密に従うこと。

### 出力JSONフォーマットと手本 ###
{{
  "proposal": {{
    "purpose": "相談内容の「目的」を簡潔に要約したもの",
    "solution_name": "課題を解決するソリューションの具体的な名前",
    "summary": "（例：各社オリジナル形式のPDF請求書から、指定された項目を自動で読み取り、請求管理台帳へ入力するソリューションです。）"
  }},
  "workflow": [
    {{"actor": "【貴社】", "action": "請求書PDFを共有フォルダにアップロード"}},
    {{"actor": "【IINA】", "action": "請求書の内容を自動で読み取り"}},
    {{"actor": "【IINA】", "action": "請求管理台帳へデータを自動で入力"}},
    {{"actor": "【IINA】", "action": "処理完了をメールで自動通知"}},
    {{"actor": "【貴社】", "action": "（任意）台帳と請求書の最終照合"}}
  ]
}}

### クライアントの相談内容 ###
{json.dumps(inputs, ensure_ascii=False, indent=2)}

### 出力JSON ###
"""
    return prompt

# --- 堅牢なJSON抽出機能 ---
def extract_json_object(text):
    """
    AIの出力テキストから、最初に出現する完全なJSONオブジェクトを抽出する。
    """
    try:
        first_brace_index = text.find('{')
        if first_brace_index == -1:
            return None
        brace_count = 0
        for i in range(first_brace_index, len(text)):
            char = text[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            if brace_count == 0:
                return text[first_brace_index : i + 1]
        return None
    except Exception:
        return None


# --- レポート整形機能 ---
def format_report(report_data):
    """AIが生成したJSONデータから、人間が見やすいレポートを生成する"""
    try:
        st.subheader("1. 自動化提案")
        proposal = report_data.get("proposal", {})
        st.markdown(f"**目的:** {proposal.get('purpose', '（目的の記述がありません）')}")
        st.markdown(f"**提案ソリューション:** {proposal.get('solution_name', '（名称の記述がありません）')}")
        st.markdown(f"**概要:** {proposal.get('summary', '（概要の記述がありません）')}")

        st.subheader("2. 導入後の簡易業務フロー")
        workflow = report_data.get("workflow", [])
        if not workflow:
            st.warning("簡易業務フローが生成されませんでした。")
            return

        flow_data = {"ステップ": [], "担当者": [], "作業内容": []}
        for i, step in enumerate(workflow):
            flow_data["ステップ"].append(f"Step {i+1}")
            flow_data["担当者"].append(step.get('actor', 'N/A'))
            flow_data["作業内容"].append(step.get('action', 'N/A'))
        
        df = pd.DataFrame(flow_data)
        df = df.set_index("ステップ")
        st.table(df)
        
        return True
    except Exception as e:
        st.error(f"レポートの整形中にエラーが発生しました: {e}")
        st.json(report_data)
        return False

# --- Streamlit UI ---
st.set_page_config(page_title="IINA PoC", layout="wide")
st.title("IINA PoC - 課題解決ソリューション (Step 1)")
st.markdown("AIコンサルタントIINAが、あなたの課題を分析し、解決策を提案します。")

llm = load_iina_model()

if llm:
    with st.form("iina_form"):
        st.header("自動化・効率化アンケート")
        
        st.subheader("インプット")
        st.caption("記入例: 各社オリジナル形式の請求書のPDF")
        input_インプット = st.text_input("インプット_input", label_visibility="collapsed")

        st.subheader("現状")
        st.caption("記入例: 一帳票づつ読取って手作業での入力に時間がかかっている")
        input_現状 = st.text_area("現状_input", label_visibility="collapsed")

        st.subheader("課題")
        st.caption("記入例: 入力ミスが多く、確認作業に追われ、他の業務が滞る")
        input_課題 = st.text_area("課題_input", label_visibility="collapsed")

        st.subheader("目的")
        st.caption("記入例: 差配対応などのマネジメントに集中したい")
        input_目的 = st.text_area("目的_input", label_visibility="collapsed")

        st.subheader("理想の状態（ゴール）")
        st.caption("記入例: 進行中の全受注案件の進捗管理の精度を上げる")
        input_理想の状態 = st.text_area("理想の状態_input", label_visibility="collapsed")

        st.subheader("制約条件・ルール")
        st.caption("記入例: 新たな有料サービスを利用することは望まない")
        input_制約条件 = st.text_input("制約条件_input", label_visibility="collapsed")

        st.subheader("アウトプット")
        st.caption("記入例: 請求台帳に指定項目をGoogleスプレッドシートへ入力")
        input_アウトプット = st.text_area("アウトプット_input", label_visibility="collapsed")
        submitted = st.form_submit_button("IINAに分析を依頼する", type="primary")

    if submitted:
        input_data = {
            "インプット": input_インプット, "現状": input_現状, "課題": input_課題,
            "目的": input_目的, "理想の状態": input_理想の状態, "制約条件": input_制約条件,
            "アウトプット": input_アウトプット,
        }

        st.header("IINAによる分析結果")
        with st.spinner("IINAが思考エンジンを稼働中です..."):
            prompt = create_iina_prompt(input_data)
            try:
                output = llm(prompt, max_tokens=1024, stop=["### クライアントの相談内容 ###"], echo=False)
                raw_response = output['choices'][0]['text']
                
                json_string = extract_json_object(raw_response)
                
                if json_string:
                    try:
                        report_json = json.loads(json_string)
                        format_report(report_json)
                    except json.JSONDecodeError:
                        st.error("AIが有効なJSONを返しませんでした。（抽出後のパースに失敗）")
                        st.text("--- AIの生データ ---")
                        st.text(raw_response)
                        st.text("--- 抽出されたJSON文字列 ---")
                        st.text(json_string)
                else:
                    st.error("AIがJSONを返しませんでした。（出力からJSONを発見できず）")
                    st.text("--- AIの生データ ---")
                    st.text(raw_response)

            except Exception as e:
                st.error(f"レポート生成中にエラーが発生しました: {e}")
else:
    st.error("AIモデルのロードに失敗しました。アプリケーションを再起動してください。")
