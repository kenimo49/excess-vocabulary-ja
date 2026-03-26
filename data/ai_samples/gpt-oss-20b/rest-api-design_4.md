# REST API設計のベストプラクティス

エンジニアの皆さん、日々の開発で「REST APIをどう設計すべきか？」という悩みはありませんか？  
本記事では、実務で役立つベストプラクティスをまとめます。  
文字数は約1,500字で、ポイントを押さえつつ実例を添えて解説します。

---

## 1. 基本原則 ― リソース指向で一貫性を保つ

| 項目 | ポイント |
|------|----------|
| **リソース名は複数形** | `/users`, `/orders` |
| **HTTPメソッドを正しく使う** | `GET`・`POST`・`PUT`・`PATCH`・`DELETE` |
| **ステータスコードは意味を持つ** | 200, 201, 400, 404, 500 など |
| **状態を持たない設計** | 再現性のあるエンドポイントにする |

### 例: ユーザー取得
```http
GET /users/123
Accept: application/json
```

## 2. エンドポイント設計のコツ

### 2‑1. 名前規則
- パスは小文字とハイフン（kebab-case）を推奨
- 大文字・アンダースコアは混在させない

### 2‑2. バージョニング
- URLにバージョン番号を入れる（例 `/v1/users`）  
  → 変更時の影響を限定
- バージョン番号は主に重大変更時に上げる

## 3. レスポンス設計

### 3‑1. JSONで統一
```json
{
  "data": {
    "id": 123,
    "name": "山田太郎",
    "email": "taro@example.com"
  },
  "meta": {
    "timestamp": "2026-03-25T12:34:56Z"
  }
}
```

### 3‑2. エラーレスポンス
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "指定されたユーザーは存在しません。",
    "details": [
      { "field": "id", "value": "123" }
    ]
  }
}
```

## 4. パフォーマンスとセキュリティ

- **キャッシュ**: `ETag`・`Cache-Control` を活用し、GETはキャッシュ可能にする  
- **認証**: Bearer トークン（JWT）やOAuth2を採用  
- **入力検証**: SQLインジェクション・XSSを防ぐバリデーションを必須

## 5. ドキュメンテーション

### 5‑1. OpenAPI (Swagger) を使う
```yaml
openapi: 3.0.3
info:
  title: Sample API
  version: 1.0.0
paths:
  /users/{id}:
    get:
      summary: ユーザー取得
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: integer }
      responses:
        '200':
          description: 正常レスポンス
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id: { type: integer }
        name: { type: string }
```

## 6. テスト戦略

- **単体テスト**: メソッド単位でリクエスト/レスポンスを検証
- **統合テスト**: 実際にエンドポイントを叩いて動作確認
- **コントラクトテスト**: スキーマやステータスコードを契約として固定

---

## まとめ

1. **リソース指向**でHTTPメソッドとステータスコードを厳格に使う  
2. エンドポイントは **一貫性**・**バージョン管理**を徹底  
3. **JSON**で統一し、エラーレスポンスは構造化  
4. **キャッシュ**・**認証**・**入力検証**でパフォーマンスと安全性を確保  
5. **OpenAPI**でドキュメントを自動生成し、**テスト**で品質を保証  

この設計パターンをベースに、自社のプロジェクトに合わせて微調整してみてください。  
実装を始める前に「このAPIはこういう目的を持つ？」という問いを自分に投げかけることで、長期にわたって保守しやすいAPIが完成します。