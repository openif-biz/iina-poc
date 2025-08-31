# Step 1: ベースとなるPythonの環境を選択
FROM python:3.10-slim

# Step 2: コンテナ内の作業ディレクトリを設定
WORKDIR /app

# ★★★【最終修正点】★★★
# Step 3: 専門的なPythonライブラリを組み立てるための「工具」をインストールする
# apt-get update: インストール可能なパッケージ一覧を最新の状態に更新します
# apt-get install -y: 確認なしでパッケージをインストールします
# build-essential: C/C++コンパイラなど、ビルドに必要な基本的なツールセットです
# cmake: llama-cpp-pythonがビルドに必要とするツールです
RUN apt-get update && apt-get install -y build-essential cmake

# Step 4: 必要なライブラリの一覧ファイルをコピー
COPY requirements.txt .

# Step 5: 必要なライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: アプリケーションのソースコードをすべてコピー
COPY . .

# Step 7: コンテナが使用するポートを外部に通知
EXPOSE 8080

# Step 8: コンテナ起動時に実行するコマンドを定義
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.headless=true"]
