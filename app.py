# FILE: app.py (Local_IINA - PoC 本番)
# PURPOSE: Local AI engine for IINA PoC
# Handles external server requests, analyzes user input, returns proposal + flow

from flask import Flask, request, jsonify
from llama_cpp import Llama
import os
import json
import time

# --- Configuration ---
MODEL_PATH = "../models/starcoder2-7b-Q4_K_M.gguf"
MODEL_CTX = 4096

# --- Load Local AI Model ---
def load_model():
    absolute_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), MODEL_PATH))
    if not os.path.exists(absolute_model_path):
        raise FileNotFoundError(f"モデルが見つかりません: {absolute_model_path}")
    llm = Llama(model_path=absolute_model_path, n_ctx=MODEL_CTX, n_gpu_layers=-1)
    return llm

llm = load_model()

# --- Prompt Generation ---
def create_prompt(user_input: str) -> str:
    return f"""
あなたは優秀なAIコンサルタント『IINA』です。
ユーザー課題を分析し、提案概要と簡易業務フローをJSON形式で返してください。
課題: {user_input}
出力例:
{{
  "proposal": {{
    "purpose": "目的を簡潔に記述",
    "solution_name": "解決策名",
    "summary": "概要説明"
  }},
  "workflow": [
    {{"actor": "【貴社】", "action": "ステップ1"}},
    {{"actor": "【IINA】", "action": "ステップ2"}},
    {{"actor": "【IINA】", "action": "ステップ3"}}
  ]
}}
"""

# --- JSON Extraction ---
import re
def extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    else:
        return {}

# --- Flask App ---
app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    if "user_input" not in data:
        return jsonify({"error": "user_input missing"}), 400
    
    user_input = data["user_input"]
    prompt = create_prompt(user_input)
    
    try:
        output = llm(prompt, max_tokens=1024, stop=["\n"], echo=False)
        text_response = output['choices'][0]['text']
        result_json = extract_json(text_response)
        return jsonify(result_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run Server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
