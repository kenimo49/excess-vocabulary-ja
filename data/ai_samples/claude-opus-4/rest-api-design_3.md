# REST API設計のベストプラクティス - 実践的なガイドライン

## はじめに

REST APIは現代のWebアプリケーション開発において不可欠な要素です。しかし、単にHTTPメソッドを使ってJSONを返すだけでは、優れたAPIとは言えません。本記事では、保守性が高く、使いやすいREST APIを設計するためのベストプラクティスを紹介します。

## 1. リソース指向の設計

### URLは名詞で構成する

REST APIの基本は**リソース**です。URLはリソースを表す名詞で構成し、動詞は使用しません。

```
# 良い例
GET    /users          # ユーザー一覧を取得
GET    /users/123      # 特定のユーザーを取得
POST   /users          # 新規ユーザーを作成
PUT    /users/123      # ユーザー情報を更新
DELETE /users/123      # ユーザーを削除

# 悪い例
GET    /getUsers
POST   /createUser
PUT    /updateUser/123
```

### 階層構造を活用する

リソース間の関係性を表現する場合は、階層構造を使用します。

```
GET /users/123/orders       # ユーザー123の注文一覧
GET /users/123/orders/456   # ユーザー123の注文456の詳細
```

## 2. HTTPメソッドの適切な使用

各HTTPメソッドには明確な役割があります：

- **GET**: リソースの取得（副作用なし）
- **POST**: 新規リソースの作成
- **PUT**: リソースの完全な更新
- **PATCH**: リソースの部分的な更新
- **DELETE**: リソースの削除

```javascript
// PUTの例（完全な更新）
PUT /users/123
{
  "name": "山田太郎",
  "email": "yamada@example.com",
  "age": 30
}

// PATCHの例（部分的な更新）
PATCH /users/123
{
  "email": "new-yamada@example.com"
}
```

## 3. ステータスコードの活用

適切なHTTPステータスコードを返すことで、APIの動作を明確に伝えられます。

```javascript
// 主要なステータスコード
200 OK                  // 成功
201 Created            // リソース作成成功
204 No Content         // 成功（レスポンスボディなし）
400 Bad Request        // クライアントエラー
401 Unauthorized       // 認証エラー
403 Forbidden          // 権限エラー
404 Not Found          // リソースが存在しない
409 Conflict           // リソースの競合
500 Internal Server Error // サーバーエラー
```

## 4. レスポンス形式の統一

### 成功時のレスポンス

```json
{
  "data": {
    "id": 123,
    "name": "山田太郎",
    "email": "yamada@example.com"
  },
  "meta": {
    "timestamp": "2024-01-01T10:00:00Z"
  }
}
```

### エラー時のレスポンス

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "指定されたユーザーが見つかりません",
    "details": {
      "userId": 123
    }
  }
}
```

## 5. バージョニング戦略

APIの進化に対応するため、バージョニングは必須です。

### URLパスでのバージョニング（推奨）
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

### ヘッダーでのバージョニング
```
Accept: application/vnd.example.v1+json
```

## 6. フィルタリング、ソート、ページネーション

大量のデータを扱う際は、これらの機能が重要です。

```
# フィルタリング
GET /users?status=active&age_gte=20

# ソート
GET /users?sort=created_at&order=desc

# ページネーション
GET /users?page=2&limit=20
```

レスポンスにはページネーション情報を含めます：

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## 7. セキュリティの考慮

### 認証・認可

```javascript
// Authorizationヘッダーを使用
Authorization: Bearer <token>
```

### レート制限

```javascript
// レート制限情報をヘッダーに含める
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## 8. その他のベストプラクティス

### 命名規則の統一

- URLパス: ケバブケース（kebab-case）
- クエリパラメータ: スネークケース（snake_case）
- JSONキー: キャメルケース（camelCase）またはスネークケース

### 冪等性の保証

GET、PUT、DELETEは冪等であるべきです。同じリクエストを複数回実行しても、結果は同じになるよう設計します。

### CORS対応

```javascript
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## まとめ

優れたREST API設計は、開発者にとって使いやすく、保守しやすいものでなければなりません。本記事で紹介したベストプラクティスを適用することで、より質の高いAPIを構築できるでしょう。

重要なのは、これらの原則を機械的に適用するのではなく、プロジェクトの要件に応じて適切に調整することです。一貫性を保ちつつ、実用的な判断を行うことが、成功するAPI設計の鍵となります。