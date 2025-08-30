# ベースとなる公式Pythonイメージを選択
FROM python:3.10-slim

# 作業ディレクトリを設定
WORKDIR /app

# ビルドに必要なツールをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# 必要なライブラリをインストールするため、requirements.txtを先にコピー
COPY requirements.txt .

# pipをアップグレードし、requirements.txtに基づいてライブラリをインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# Streamlitが使用するポートを開放
EXPOSE 8080

# コンテナ起動時に実行するコマンド
# Cloud Runが提供するPORT環境変数を使用し、CORS保護を無効化
CMD ["streamlit", "run", "app.py", "--server.port", "$PORT", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]