# REST API設計のベストプラクティス

RESTfulなAPIは現代のWebアプリケーションにおいて不可欠な存在です。適切に設計されたAPIは開発者にとって使いやすく、保守性が高く、スケーラブルなシステムの基盤となります。本記事では、実践的なREST API設計のベストプラクティスを解説します。

## 1. リソースベースのURL設計

### 名詞を使用し、動詞は避ける

URLはリソースを表現すべきです。HTTPメソッドが動作を表現するため、URL内に動詞を含める必要はありません。

```
❌ Bad
/api/getUsers
/api/createUser
/api/updateUser/123

✅ Good
GET /api/users
POST /api/users
PUT /api/users/123
```

### 複数形を使用する

一貫性を保つため、リソース名は複数形を使用します。

```
❌ Bad
/api/user
/api/product

✅ Good
/api/users
/api/products
```

### 階層構造を適切に表現する

リソース間の関係性は階層構造で表現します。

```
/api/users/123/posts          # ユーザー123の投稿一覧
/api/users/123/posts/456      # ユーザー123の投稿456
/api/orders/789/items         # 注文789のアイテム一覧
```

## 2. HTTPメソッドの適切な使用

各HTTPメソッドには明確な責任があります：

| メソッド | 用途 | 冪等性 | 安全性 |
|---------|------|--------|--------|
| GET | リソースの取得 | ✅ | ✅ |
| POST | リソースの作成 | ❌ | ❌ |
| PUT | リソースの完全更新/作成 | ✅ | ❌ |
| PATCH | リソースの部分更新 | ❌ | ❌ |
| DELETE | リソースの削除 | ✅ | ❌ |

### 実装例

```javascript
// GET: リソース取得
GET /api/users/123
Response: { "id": 123, "name": "田中太郎", "email": "tanaka@example.com" }

// POST: 新規作成
POST /api/users
Body: { "name": "佐藤花子", "email": "sato@example.com" }
Response: { "id": 124, "name": "佐藤花子", "email": "sato@example.com" }

// PUT: 完全更新
PUT /api/users/123
Body: { "name": "田中太郎", "email": "tanaka.taro@example.com" }

// PATCH: 部分更新
PATCH /api/users/123
Body: { "email": "tanaka.taro@example.com" }

// DELETE: 削除
DELETE /api/users/123
```

## 3. HTTPステータスコードの正しい使用

適切なステータスコードを返すことで、クライアント側で適切なエラーハンドリングが可能になります。

### よく使用されるステータスコード

```
成功レスポンス:
200 OK              - 正常な取得・更新
201 Created         - リソースの新規作成成功
204 No Content      - 正常だがレスポンスボディなし（DELETE等）

クライアントエラー:
400 Bad Request     - リクエストが不正
401 Unauthorized    - 認証が必要
403 Forbidden       - アクセス権限なし
404 Not Found       - リソースが存在しない
409 Conflict        - リソースの競合

サーバーエラー:
500 Internal Server Error - サーバー内部エラー
503 Service Unavailable   - サービス利用不可
```

## 4. エラーハンドリングの統一

エラーレスポンスは一貫した形式で提供すべきです。

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データが無効です",
    "details": [
      {
        "field": "email",
        "message": "有効なメールアドレスを入力してください"
      }
    ]
  }
}
```

## 5. ページネーション

大量のデータを扱う場合、ページネーションは必須です。

### Offset-based Pagination

```
GET /api/users?page=2&limit=20
{
  "data": [...],
  "pagination": {
    "current_page": 2,
    "total_pages": 15,
    "total_count": 300,
    "per_page": 20
  }
}
```

### Cursor-based Pagination

```
GET /api/users?cursor=eyJpZCI6MTIzfQ&limit=20
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTQzfQ",
    "has_next": true
  }
}
```

## 6. バージョニング

APIの変更時に後方互換性を保つためのバージョニング戦略：

### URL Path Versioning

```
/api/v1/users
/api/v2/users
```

### Header Versioning

```
GET /api/users
Accept: application/vnd.api+json;version=1
```

## 7. セキュリティの考慮

### 認証・認可

```javascript
// JWTトークンを使用した認証例
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

// APIキーを使用した認証例
X-API-Key: your-api-key-here
```

### レート制限

```javascript
// レスポンスヘッダーでレート制限情報を提供
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1609459200
```

## 8. ドキュメント化

OpenAPI（Swagger）を使用してAPIドキュメントを自動生成・管理することを強く推奨します。

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: ユーザー一覧取得
      parameters:
        - name: page
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: 成功
```

## まとめ

良いREST API設計は：

1. **直感的** - URLとメソッドから機能が予測できる
2. **一貫性** - 命名規則とレスポンス形式が統一されている
3. **拡張性** - バージョニングとページネーションに対応
4. **セキュア** - 適切な認証・認可機能を実装
5. **文書化** - 利用方法が明確に文書化されている

これらのベストプラクティスを参考に、開発者にとって使いやすく、保守性の高いAPIを設計してください。