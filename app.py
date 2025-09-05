from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 設定（任意。ブラウザから自由にアクセスできるように）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルート：入力フォーム表示
@app.get("/", response_class=HTMLResponse)
def read_form():
    html_content = """
    <html>
        <head>
            <title>IINA PoC - 課題受付フォーム</title>
        </head>
        <body>
            <h1>IINA PoC - 課題受付フォーム</h1>
            <form action="/analyze" method="post">
                <label>インプット:</label><br>
                <input type="text" name="インプット"><br><br>

                <label>現状:</label><br>
                <textarea name="現状" rows="4" cols="50"></textarea><br><br>

                <label>課題:</label><br>
                <textarea name="課題" rows="4" cols="50"></textarea><br><br>

                <label>目的:</label><br>
                <textarea name="目的" rows="4" cols="50"></textarea><br><br>

                <label>理想の状態:</label><br>
                <textarea name="理想の状態" rows="4" cols="50"></textarea><br><br>

                <label>制約条件:</label><br>
                <input type="text" name="制約条件"><br><br>

                <label>アウトプット:</label><br>
                <textarea name="アウトプット" rows="4" cols="50"></textarea><br><br>

                <input type="submit" value="分析実行">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# /analyze：フォームデータ受け取り・簡易分析
@app.post("/analyze", response_class=HTMLResponse)
async def analyze_form(
    インプット: str = Form(...),
    現状: str = Form(...),
    課題: str = Form(...),
    目的: str = Form(...),
    理想の状態: str = Form(...),
    制約条件: str = Form(...),
    アウトプット: str = Form(...)
):
    # 仮の分析処理（ここで本物のIINA解析に接続可能）
    summary = f"【仮分析】入力「{インプット}」に対する提案を生成しました。"
    flow = [
        "ステップ1: データ取得",
        "ステップ2: 入力確認",
        "ステップ3: 自動化処理",
    ]
    proposals = [
        "提案1: 手作業を削減",
        "提案2: Googleスプレッドシートに自動入力",
    ]

    # 結果表示用HTML
    html_result = f"""
    <html>
        <head><title>分析結果</title></head>
        <body>
            <h1>提案概要</h1>
            <p>{summary}</p>

            <h2>簡易フロー</h2>
            <ol>
                {''.join(f'<li>{s}</li>' for s in flow)}
            </ol>

            <h2>追加提案</h2>
            <ul>
                {''.join(f'<li>{p}</li>' for p in proposals)}
            </ul>

            <br><a href="/">戻る</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_result)
