FROM python:3.10-slim

# ---【★★ここが最終修正点★★】---
# llama-cpp-python のインストールに必要なビルドツールを導入
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 壊れたPythonキャッシュ(.pyc)が残る問題を解決するため、キャッシュを強制削除する
RUN find . -type d -name "__pycache__" -exec rm -r {} +

EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.headless=true"]
