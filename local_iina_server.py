# 【通番02改】local_iina_server.py
import streamlit as st
from llama_cpp import Llama
import json
import os

# --- AIモデル設定 ---
# --- ▼▼▼【変更点】▼▼▼ ---
# ワークスペースルートを基準とした、堅牢なパス構築に変更
def get_model_path_for_iina():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = current_dir
    while not os.path.isdir(os.path.join(workspace_root, 'models')):
        parent_dir = os.path.dirname(workspace_root)
        if parent_dir == workspace_root:
            raise FileNotFoundError("Could not find the 'models' directory in any parent path.")
        workspace_root = parent_dir
    return os.path.join(workspace_root, "models", "starcoder2-7b-Q4_K_M.gguf")

LOCAL_MODEL_PATH = get_model_path_for_iina()
# --- ▲▲▲【変更点】▲▲▲ ---

@st.cache_resource
def load_iina_model():
    if not os.path.exists(LOCAL_MODEL_PATH):
        st.error(f"モデルファイルが見つかりません: {LOCAL_MODEL_PATH}")
        st.stop()
    try:
        llm = Llama(model_path=LOCAL_MODEL_PATH, n_ctx=4096, n_gpu_layers=-1, verbose=False)
        return llm
    except Exception as e:
        st.error(f"モデルのロード中にエラーが発生しました: {e}")
        st.stop()

# --- (以降のコードは変更なしのため省略) ---
# ... (前回の提案と同様の、プロンプト生成、JSON抽出、Streamlit UIのコード) ...
def create_iina_prompt(inputs: dict):
    prompt = f"""
あなたは、ユーザーの課題を分析し、以下の簡易フローJSONを返すAIです。
出力は厳密にJSON形式のみとしてください。

入力データ:
{json.dumps(inputs, ensure_ascii=False, indent=2)}

出力フォーマット:
{{
  "workflow": [
    {{"actor": "【貴方】", "action": "請求書アップロード"}},
    {{"actor": "【ＡＩ】", "action": "請求書読取"}},
    {{"actor": "【ＡＩ】", "action": "請求台帳入力"}},
    {{"actor": "【ＡＩ】", "action": "入力完了通知"}},
    {{"actor": "【貴方】", "action": "台帳と請求書の照合"}}
  ]
}}
"""
    return prompt
def extract_json_object(text: str):
    try:
        first_brace = text.find('{')
        if first_brace == -1: return None
        count = 0
        for i, c in enumerate(text[first_brace:]):
            if c == '{': count += 1
            elif c == '}': count -= 1
            if count == 0: return text[first_brace:first_brace+i+1]
        return None
    except: return None
st.set_page_config(page_title="IINA PoC", layout="wide")
st.title("IINA PoC - 課題分析 & 自動化提案")
tab1, tab2 = st.tabs(["課題入力 & AI簡易フロー", "自動化提案概要"])
with tab1:
    st.subheader("課題入力フォーム")
    llm = load_iina_model()
    with st.form("iina_form"):
        input_data = {}
        input_data["インプット"] = st.text_input("インプット", "例: 各社オリジナル形式の請求書PDF")
        input_data["現状"] = st.text_area("現状", "例: 手作業で請求台帳に入力中")
        input_data["課題"] = st.text_area("課題", "例: 入力ミスが多く確認作業に追われる")
        input_data["目的"] = st.text_area("目的", "例: マネジメントに集中したい")
        input_data["理想の状態"] = st.text_area("理想の状態", "例: 進行中案件の進捗管理精度向上")
        input_data["制約条件"] = st.text_input("制約条件", "例: 新サービス利用は不可")
        input_data["アウトプット"] = st.text_area("アウトプット", "例: 台帳に自動入力")
        submitted = st.form_submit_button("AIに分析を依頼")
    if submitted:
        st.subheader("簡易業務フロー")
        with st.spinner("AIが分析中..."):
            try:
                prompt = create_iina_prompt(input_data)
                output = llm(prompt, max_tokens=512, stop=None, echo=False)
                raw_text = output['choices'][0]['text']
                json_string = extract_json_object(raw_text)
                if json_string:
                    workflow_json = json.loads(json_string)
                    for step in workflow_json.get("workflow", []):
                        st.markdown(f"**{step['actor']}** → {step['action']}")
                else:
                    st.error("AIがJSONを返しませんでした。")
                    st.text(raw_text)
            except Exception as e:
                st.error(f"AI分析中にエラーが発生しました: {e}")
with tab2:
    st.subheader("自動化提案概要")
    st.markdown("〇〇フォルダへ請求書をアップロードしていただけたら、\n「案件名」「請求先企業名」「請求金額」「振込口座番号」を自動で読取り、\n指定の△△フォルダの請求管理台帳のGoogleスプレッドシートへ自動入力します。")