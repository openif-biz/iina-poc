# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# FastAPI インスタンス
app = FastAPI(title="IINA PoC API")

# CORS 設定（ブラウザからのアクセス許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストボディの型
class AnalysisRequest(BaseModel):
    インプット: str
    現状: str
    課題: str
    目的: str
    理想の状態: str
    制約条件: str
    アウトプット: str

# レスポンス型
class AnalysisResponse(BaseModel):
    summary: str
    flow: List[str]
    proposals: List[str]

# 簡易分析エンドポイント
@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    # ここは PoC 用のダミー処理
    summary = f"{request.課題} を解決するための提案概要です。"
    flow = [
        "入力データを収集",
        "自動解析",
        "結果を整理",
        "出力先に反映"
    ]
    proposals = [
        "Googleスプレッドシート自動入力",
        "メール通知機能追加"
    ]
    return AnalysisResponse(summary=summary, flow=flow, proposals=proposals)

# 健康チェック
@app.get("/")
def root():
    return {"status": "ok"}
