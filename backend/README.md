# OCI Functions を使った ToDo アプリ バックエンド

このプロジェクトは、Oracle Cloud Infrastructure (OCI) Functions と NoSQL Database Service を使用したサーバレス構成の ToDo アプリケーションのバックエンド実装です。

## 構成

本プロジェクトは 4 つの独立した Function で構成されています：

- **add-task**: タスク追加 (POST /add)
- **delete-task**: タスク削除 (POST /delete)
- **edit-task**: タスク編集 (POST /edit)
- **list-tasks**: タスクリスト取得 (GET /list)

## ディレクトリ構造

```
backend/
├── add-task/
│   ├── func.py            # タスク追加Function
│   ├── func.yaml          # Function設定
│   └── requirements.txt   # 依存関係
├── delete-task/
│   ├── func.py            # タスク削除Function
│   ├── func.yaml          # Function設定
│   └── requirements.txt   # 依存関係
├── edit-task/
│   ├── func.py            # タスク編集Function
│   ├── func.yaml          # Function設定
│   └── requirements.txt   # 依存関係
├── list-tasks/
│   ├── func.py            # タスクリスト取得Function
│   ├── func.yaml          # Function設定
│   └── requirements.txt   # 依存関係
└── README.md             # このファイル
```

## API 仕様

### 1. タスク追加 (add-task)

- **エンドポイント**: `POST /tasks`
- **HTTP メソッド**: `POST`
- **リクエストボディ**:
  ```json
  {
    "title": "買い物に行く",
    "description": "牛乳とパンを買う"
  }
  ```
- **レスポンス**:
  ```json
  {
    "task_id": "uuid-string",
    "title": "買い物に行く",
    "description": "牛乳とパンを買う",
    "created_at": "2025-10-14T12:00:00Z",
    "completed": false
  }
  ```

### 2. タスク削除 (delete-task)

- **エンドポイント**: `DELETE /tasks?id=<task_id>`
- **HTTP メソッド**: `DELETE`
- **レスポンス**:
  ```json
  {
    "message": "Task 'uuid-string' deleted successfully"
  }
  ```

### 3. タスク編集 (edit-task)

- **エンドポイント**: `PATCH /tasks?id=<task_id>`
- **HTTP メソッド**: `PATCH`
- **リクエストボディ**:
  ```json
  {
    "title": "更新されたタイトル",
    "description": "更新された説明",
    "completed": true
  }
  ```
- **レスポンス**: 更新されたタスクオブジェクト

### 4. タスクリスト取得 (list-tasks)

- **エンドポイント**: `GET /tasks`
- **HTTP メソッド**: `GET`
- **レスポンス**:
  ```json
  [
    {
      "task_id": "uuid-string",
      "title": "タスク1",
      "description": "説明1",
      "created_at": "2025-10-14T12:00:00Z",
      "completed": false
    },
    ...
  ]
  ```

## データモデル

NoSQL Database の各レコードは以下の構造を持ちます：

### データベース構造

```json
{
  "id": "uuid-string", // プライマリキー (STRING)
  "content": "{...}" // タスクデータ (JSON文字列)
}
```

### content フィールド内の JSON 構造

```json
{
  "title": "タスクのタイトル",
  "description": "タスクの説明",
  "created_at": "2025-10-14T12:00:00Z",
  "completed": false
}
```

### API レスポンス形式

```json
{
  "id": "uuid-string",
  "title": "タスクのタイトル",
  "description": "タスクの説明",
  "created_at": "2025-10-14T12:00:00Z",
  "completed": false
}
```

## 前提条件

### 1. OCI NoSQL Database Service

- NoSQL Database テーブルが作成されている
- テーブルのプライマリキーが `id` (STRING) として設定されている
- テーブルに `content` (JSON) カラムが設定されている

### 2. 環境変数

各 Function に以下の環境変数を設定してください：

- `NOSQL_TABLE_NAME`: NoSQL Database のテーブル名

### 3. 認証

- Resource Principal 認証が有効になっている
- Function が NoSQL Database Service にアクセスする権限を持っている

## デプロイ手順

1. **OCI CLI と fn CLI の設定**

   ```bash
   # OCI CLI設定（事前設定済みと仮定）
   # fn CLIコンテキスト設定
   fn use context <your-context>
   ```

2. **各 Function のデプロイ**

   ```bash
   # add-task Function
   cd add-task
   fn deploy --app <your-app-name>

   # delete-task Function
   cd ../delete-task
   fn deploy --app <your-app-name>

   # edit-task Function
   cd ../edit-task
   fn deploy --app <your-app-name>

   # list-tasks Function
   cd ../list-tasks
   fn deploy --app <your-app-name>
   ```

3. **環境変数の設定**
   ```bash
   fn config function <app-name> add-task NOSQL_TABLE_NAME <your-table-name>
   fn config function <app-name> delete-task NOSQL_TABLE_NAME <your-table-name>
   fn config function <app-name> edit-task NOSQL_TABLE_NAME <your-table-name>
   fn config function <app-name> list-tasks NOSQL_TABLE_NAME <your-table-name>
   ```

## テスト

各 Function は以下のコマンドでテストできます：

```bash
# タスク追加
echo '{"title": "テストタスク", "description": "テスト説明"}' | fn invoke <app-name> add-task

# タスクリスト取得
echo '' | fn invoke <app-name> list-tasks

# タスク編集（task_idは実際の値に置き換えてください）
echo '{"completed": true}' | fn invoke <app-name> edit-task --query id=<task-id>

# タスク削除（task_idは実際の値に置き換えてください）
echo '' | fn invoke <app-name> delete-task --query id=<task-id>
```

## エラーハンドリング

各 Function は以下の HTTP ステータスコードを返します：

- **200**: 正常処理（削除、編集、リスト取得）
- **201**: 作成成功（タスク追加）
- **400**: バリデーションエラー
- **404**: タスクが見つからない
- **500**: サーバー内部エラー

## 注意事項

- Resource Principal 認証を使用するため、Function は適切なコンパートメント内にデプロイする必要があります
- NoSQL Database のテーブルへの読み書き権限が必要です
- 各 Function は独立してスケールします
- list-tasks は作成日時の降順でタスクを返します

## トラブルシューティング

1. **環境変数エラー**: `NOSQL_TABLE_NAME`が正しく設定されているか確認
2. **認証エラー**: Resource Principal 設定と IAM ポリシーを確認
3. **NoSQL エラー**: テーブル名とスキーマ定義を確認
