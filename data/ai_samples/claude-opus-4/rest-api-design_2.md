# REST API設計のベストプラクティス：実践的なガイドライン

REST APIは現代のWebアプリケーション開発において不可欠な要素です。しかし、優れたAPIを設計することは簡単ではありません。本記事では、保守性が高く、使いやすいREST APIを設計するためのベストプラクティスを解説します。

## 1. リソース指向のURL設計

### ✅ 良い例
```
GET    /users              # ユーザー一覧取得
GET    /users/123          # 特定ユーザー取得
POST   /users              # ユーザー作成
PUT    /users/123          # ユーザー更新
DELETE /users/123          # ユーザー削除
```

### ❌ 悪い例
```
GET    /getUsers
GET    /getUserById?id=123
POST   /createUser
POST   /updateUser?id=123
POST   /deleteUser?id=123
```

**ポイント**: 
- 名詞を使い、動詞は避ける
- 複数形で統一する
- 階層構造は`/`で表現する

## 2. HTTPメソッドの適切な使用

| メソッド | 用途 | 冪等性 | 安全性 |
|---------|------|--------|--------|
| GET | リソースの取得 | ✓ | ✓ |
| POST | リソースの作成 | ✗ | ✗ |
| PUT | リソースの完全な更新 | ✓ | ✗ |
| PATCH | リソースの部分更新 | ✓ | ✗ |
| DELETE | リソースの削除 | ✓ | ✗ |

## 3. HTTPステータスコードの活用

```javascript
// 成功系
200 OK                    // 正常処理
201 Created              // リソース作成成功
204 No Content           // 正常処理（レスポンスボディなし）

// クライアントエラー系
400 Bad Request          // リクエスト不正
401 Unauthorized         // 認証エラー
403 Forbidden           // 権限エラー
404 Not Found           // リソース未発見

// サーバーエラー系
500 Internal Server Error // サーバー内部エラー
503 Service Unavailable   // サービス利用不可
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
    "timestamp": "2024-01-15T10:00:00Z"
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
      "userId": 999
    }
  }
}
```

## 5. バージョニング戦略

### URLパスによるバージョニング（推奨）
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

### ヘッダーによるバージョニング
```
Accept: application/vnd.example.v1+json
```

## 6. ページネーションの実装

```
GET /users?page=2&limit=20

{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

## 7. フィルタリングとソート

```
# フィルタリング
GET /users?status=active&role=admin

# ソート
GET /users?sort=created_at&order=desc

# 複合条件
GET /users?status=active&sort=name&order=asc&limit=50
```

## 8. セキュリティの考慮

### 認証・認可
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### CORS設定
```javascript
// レスポンスヘッダー
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

## 9. API設計のチェックリスト

- [ ] RESTfulな命名規則に従っているか
- [ ] HTTPメソッドを適切に使用しているか
- [ ] ステータスコードは正確か
- [ ] エラーレスポンスは統一されているか
- [ ] バージョニング戦略は明確か
- [ ] 認証・認可は実装されているか
- [ ] レート制限は設定されているか
- [ ] ドキュメントは充実しているか

## まとめ

REST API設計は、単なる技術的な実装以上の意味を持ちます。優れたAPI設計は、開発効率を向上させ、保守性を高め、利用者の満足度を向上させます。

本記事で紹介したベストプラクティスを参考に、一貫性があり、使いやすいAPIを設計していきましょう。また、これらの原則は絶対的なものではなく、プロジェクトの要件に応じて柔軟に適用することが重要です。

## 参考リンク

- [REST API設計のベストプラクティス - Google Cloud](https://cloud.google.com/apis/design)
- [RESTful API設計ガイド - Microsoft](https://docs.microsoft.com/ja-jp/azure/architecture/best-practices/api-design)
- [OpenAPI Specification](https://www.openapis.org/)