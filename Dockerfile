# Dockerfile For IINA PoC Frontend on Linode

# 1. ベースとなる環境を選択
# Python 3.10 の軽量なOSイメージを使用します
FROM python:3.10-slim

# 2. アプリケーションを格納するフォルダを作成
WORKDIR /app

# 3. 必要なライブラリをインストールするためのリストをコピー
# まず requirements.txt だけをコピーすることで、Dockerのキャッシュが効率的に機能します
COPY requirements.txt .

# 4. ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# 5. アプリケーションの全コードをコピー
COPY . .

# 6. Streamlitが使用するポートを開放
EXPOSE 8501

# 7. コンテナ起動時に実行されるコマンド
# --- ▼▼▼【変更点】▼▼▼ ---
# 起動対象のファイルを 'linode_frontend.py' から 'app.py' に修正
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
# --- ▲▲▲【変更点】▲▲▲ ---