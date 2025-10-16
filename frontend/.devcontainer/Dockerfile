# Dockerfileによるカスタマイズが必要な場合の例
FROM mcr.microsoft.com/devcontainers/javascript-node:1-20-bullseye

# システムパッケージのインストール
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # 必要に応じて追加パッケージをここに記述
    curl \
    wget \
    git \
    && apt-get autoremove -y && apt-get clean -y

# グローバルnpmパッケージのインストール
RUN npm install -g @vue/cli vite

# ユーザー設定
USER node