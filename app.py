import streamlit as st
from llama_cpp import Llama
import os

# --- モデルパス設定 ---
LOCAL_MODEL_PATH = "C:/Users/Owner/local_savan/models/starcoder2-7b-Q4_K_M.gguf"

# --- Llamaモデルロード（CPUのみ） ---
llm = Llama(
    model_path=LOCAL_MODEL_PATH,
    n_ctx=4096,
    n_gpu_layers=0,
    verbose=False
)

# --- Streamlit UI ---
st.set_page_config(page_title="IINA PoC - 課題分析 & 自動化提案", layout="wide")
st.title("IINA PoC - 課題分析 & 自動化提案")
st.write("下記のフォームに課題を入力してください。記入例を参考にしてください。")

with st.form("課題入力フォーム"):
    st.subheader("インプット")
    st.write("例: 各社オリジナル形式の請求書のPDF")
    input_インプット = st.text_area("記入欄：", key="input1")

    st.subheader("現状")
    st.write("例: 一帳票づつ読取って手作業での入力に時間がかかっている")
    input_現状 = st.text_area("記入欄：", key="input2")

    st.subheader("課題")
    st.write("例: 入力ミスが多く、確認作業（表面化できない工数）に追われ、他の業務が滞る")
    input_課題 = st.text_area("記入欄：", key="input3")

    st.subheader("目的")
    st.write("例: 差配対応（問合せ対応、各種調整と指示、進捗管理）などのマネジメントに集中できず、作業精度を落としているから")
    input_目的 = st.text_area("記入欄：", key="input4")

    st.subheader("理想の状態")
    st.write("例: 進行中の全ての受注案件の進捗管理の精度を上げることができる")
    input_理想 = st.text_area("記入欄：", key="input5")

    st.subheader("制約条件・ルール")
    st.write("例: 課題を解決して業務効率化はしたいが、新たな有料サービスを利用すること望まない。")
    input_制約 = st.text_area("記入欄：", key="input6")

    st.subheader("アウトプット")
    st.write("例: 請求台帳に「案件名」「請求先企業名」「請求金額」「振込口座番号」を Googleスプレッドへ入力して欲しい")
    input_アウトプット = st.text_area("記入欄：", key="input7")

    submitted = st.form_submit_button("課題を送信して自動化提案を生成")

# --- AIによる自動化提案 ---
if submitted:
    st.success("課題を受け付けました。以下に自動化提案を表示します。")

    # 自動化提案概要専用プロンプト
    prompt_summary = f"""
以下の課題情報をもとに、自動化提案概要だけを文章で作成してください。
簡易フローは無視してください。
課題情報:
インプット: {input_インプット}
現状: {input_現状}
課題: {input_課題}
目的: {input_目的}
理想の状態: {input_理想}
制約条件・ルール: {input_制約}
アウトプット: {input_アウトプット}
文章形式で、各ステップで誰が何をするかを簡潔に記載してください。
"""

    # Llamaで生成
    response_summary = llm(prompt_summary, max_tokens=1024)
    output_summary = response_summary['choices'][0]['text'].strip()

    # 結果表示（概要のみ）
    st.subheader("自動化提案概要")
    st.text_area("AIによる提案概要", value=output_summary, height=250)

    # 簡易フローは従来通り表示
    st.subheader("簡易フロー")
    st.text_area("AIによる簡易フロー", value="既存コードで生成された簡易フローを表示", height=200)
