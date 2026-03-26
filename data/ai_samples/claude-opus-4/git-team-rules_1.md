# Gitチーム運用ルール：効率的なチーム開発のためのベストプラクティス

## はじめに

チーム開発において、Gitの運用ルールを明確にすることは、コードの品質維持と開発効率の向上に欠かせません。本記事では、実践的なGitチーム運用ルールについて解説します。

## ブランチ戦略

### Git Flowをベースにした運用

```
main (master)
├── develop
│   ├── feature/user-authentication
│   ├── feature/payment-system
│   └── feature/dashboard-ui
├── release/v1.2.0
└── hotfix/critical-bug-fix
```

### ブランチの役割

- **main**: 本番環境にデプロイされるブランチ
- **develop**: 開発の主軸となるブランチ
- **feature/**: 機能開発用ブランチ
- **release/**: リリース準備用ブランチ
- **hotfix/**: 緊急修正用ブランチ

## ブランチ命名規則

```bash
# 機能開発
feature/issue-123-user-authentication
feature/add-payment-gateway

# バグ修正
bugfix/issue-456-login-error
hotfix/critical-security-patch

# リリース
release/v2.1.0
release/2023-12-sprint
```

### 命名のポイント

- 小文字とハイフンを使用
- issue番号を含める（トラッキング可能にするため）
- 簡潔で分かりやすい説明を付ける

## コミットメッセージのルール

### フォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 実例

```bash
feat(auth): ユーザー認証機能を追加

- JWTトークンベースの認証を実装
- リフレッシュトークン機能を追加
- セッション管理のロジックを改善

Closes #123
```

### タイプ一覧

| タイプ | 説明 |
|--------|------|
| feat | 新機能 |
| fix | バグ修正 |
| docs | ドキュメントのみの変更 |
| style | コードの意味に影響しない変更 |
| refactor | バグ修正や機能追加を伴わないコード変更 |
| test | テストの追加や修正 |
| chore | ビルドプロセスやツールの変更 |

## プルリクエスト（PR）の運用

### PRテンプレート例

```markdown
## 概要
このPRで実装した内容の概要を記載

## 変更内容
- [ ] ユーザー認証APIの実装
- [ ] テストコードの追加
- [ ] ドキュメントの更新

## 確認項目
- [ ] コードレビューを依頼する
- [ ] CIが通ることを確認
- [ ] 関連するissueをリンク

## スクリーンショット（UIの変更がある場合）

## 関連issue
Closes #123
```

### レビューのポイント

1. **コードの品質**
   - 命名規則の遵守
   - 適切なエラーハンドリング
   - パフォーマンスへの配慮

2. **テストの確認**
   - 単体テストの網羅性
   - 統合テストの実施

3. **ドキュメントの更新**
   - READMEの更新
   - APIドキュメントの整備

## マージ戦略

### Squash and Merge を推奨

```bash
# 複数のコミットを1つにまとめてマージ
# feature/user-auth -> develop
git merge --squash feature/user-auth
```

### マージ時の注意点

- developブランチは常にデプロイ可能な状態を保つ
- マージ前に最新のdevelopをpullして競合を解決
- CIが通ることを確認してからマージ

## 日常的な作業フロー

```bash
# 1. 最新のdevelopを取得
git checkout develop
git pull origin develop

# 2. featureブランチを作成
git checkout -b feature/new-feature

# 3. 開発・コミット
git add .
git commit -m "feat: 新機能を追加"

# 4. リモートにpush
git push origin feature/new-feature

# 5. PRを作成してレビューを依頼
```

## トラブルシューティング

### よくある問題と対処法

```bash
# コンフリクトの解決
git checkout develop
git pull origin develop
git checkout feature/my-feature
git merge develop
# コンフリクトを手動で解決
git add .
git commit -m "resolve: developとのコンフリクトを解決"

# 誤ったコミットの取り消し
git reset --soft HEAD~1  # 直前のコミットを取り消し（変更は維持）
git reset --hard HEAD~1  # 直前のコミットを完全に取り消し
```

## チーム内での合意事項

1. **強制pushの禁止**
   - `git push -f` は原則使用しない
   - 必要な場合はチームに事前連絡

2. **定期的なリベース**
   - 長期間のfeatureブランチは週1回developをマージ

3. **コードレビューの必須化**
   - 最低1人のapproveが必要
   - セルフマージは禁止

## まとめ

Gitチーム運用ルールを明確にすることで、以下のメリットが得られます：

- コードの品質向上
- 開発効率の改善
- チーム間のコミュニケーション円滑化
- トラブルの早期発見と対処

これらのルールは、チームの規模や開発スタイルに応じて調整することが重要です。定期的にチームで振り返りを行い、より良い運用方法を模索していきましょう。