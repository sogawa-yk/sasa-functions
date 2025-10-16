# Development Container for Vue.js

このプロジェクトは VS Code Dev Containers を使用した開発環境を提供します。

## 使用方法

1. VS Code で Dev Containers 拡張機能をインストール
2. プロジェクトフォルダを開く
3. コマンドパレット（Ctrl+Shift+P / Cmd+Shift+P）から「Dev Containers: Reopen in Container」を実行

## 含まれる機能

- Node.js 20
- Vue.js 開発に必要な拡張機能
- 自動的な npm install の実行
- Vite 開発サーバーの自動起動
- ポート転送の設定

## ポート設定

- 5173: Vite 開発サーバー
- 3000: Node.js アプリケーション
- 8080: 代替ポート

## カスタマイズ

必要に応じて`.devcontainer/devcontainer.json`を編集してください。
追加のシステムパッケージが必要な場合は、`.devcontainer/Dockerfile`を使用してください。
