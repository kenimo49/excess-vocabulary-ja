# Gitチーム運用ルール：効率的な開発を実現するベストプラクティス

## はじめに

チーム開発においてGitの運用ルールを明確にすることは、コードの品質維持と開発効率の向上に不可欠です。本記事では、実践的なGitチーム運用ルールについて、具体例を交えながら解説します。

## ブランチ戦略

### 基本的なブランチ構成

```
main (or master)
├── develop
├── feature/xxx
├── release/xxx
└── hotfix/xxx
```

#### 各ブランチの役割

- **main**: 本番環境にデプロイされるブランチ
- **develop**: 開発の最新状態を保持するブランチ
- **feature**: 機能開発用ブランチ
- **release**: リリース準備用ブランチ
- **hotfix**: 緊急修正用ブランチ

### ブランチ命名規則

```bash
# 機能開発
feature/add-user-authentication
feature/improve-search-performance

# バグ修正
bugfix/fix-login-error
bugfix/resolve-memory-leak

# リリース
release/v1.2.0
release/2024-01-15

# ホットフィックス
hotfix/critical-payment-bug
```

## コミットルール

### コミットメッセージのフォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 実例

```bash
feat(auth): ユーザー認証機能を追加

- JWTトークンによる認証を実装
- ログイン/ログアウトAPIを追加
- セッション管理機能を実装

Closes #123
```

### コミットタイプ

| タイプ | 説明 | 例 |
|--------|------|-----|
| feat | 新機能追加 | `feat: 検索機能を追加` |
| fix | バグ修正 | `fix: ログインエラーを修正` |
| docs | ドキュメント変更 | `docs: READMEを更新` |
| style | コードスタイルの変更 | `style: インデントを修正` |
| refactor | リファクタリング | `refactor: 認証処理を最適化` |
| test | テスト関連 | `test: ユニットテストを追加` |
| chore | ビルド処理等の変更 | `chore: dependenciesを更新` |

## プルリクエスト運用

### PRテンプレート例

```markdown
## 概要
このPRで実装した内容を簡潔に記載

## 変更内容
- [ ] 機能A を実装
- [ ] バグB を修正
- [ ] テストを追加

## 動作確認
1. 環境構築手順
2. 動作確認手順
3. 期待される結果

## スクリーンショット
（UI変更がある場合）

## レビューポイント
- 特に確認してほしい箇所
- 懸念事項

## 関連Issue
Closes #xxx
```

### レビュープロセス

1. **セルフレビュー**: PR作成前に自分でコードを確認
2. **自動テスト**: CI/CDでテストを実行
3. **コードレビュー**: 最低1名以上のレビューを必須化
4. **承認とマージ**: レビュー承認後にマージ

## マージ戦略

### マージ方法の使い分け

```bash
# feature → develop: Squash and merge
# （複数の開発コミットを1つにまとめる）
git merge --squash feature/xxx

# develop → main: Create a merge commit
# （マージコミットを作成して履歴を保持）
git merge --no-ff develop

# hotfix → main: Fast-forward merge
# （可能な場合は高速マージ）
git merge hotfix/xxx
```

## 実践的な運用Tips

### 1. 定期的なリベース

```bash
# developブランチの最新を取り込む
git checkout feature/xxx
git rebase develop
```

### 2. コミットの整理

```bash
# 直近3つのコミットを整理
git rebase -i HEAD~3
```

### 3. プッシュ前の確認事項

- [ ] テストが全て通っているか
- [ ] 不要なデバッグコードが含まれていないか
- [ ] コミットメッセージが適切か
- [ ] .gitignoreが適切に設定されているか

## チーム内ルールの例

### 日次運用

- 作業開始前に`develop`ブランチを最新化
- 1日の終わりに進捗をプッシュ（WIPでも可）

### 週次運用

- 金曜日にdevelopブランチのコードレビュー会
- 不要なブランチの削除

### 禁止事項

- `force push`の原則禁止（例外は個人ブランチのみ）
- mainブランチへの直接プッシュ
- 大きすぎるファイル（100MB以上）のコミット

## まとめ

Gitチーム運用ルールは、チームの規模や開発スタイルに応じてカスタマイズすることが重要です。ここで紹介したルールをベースに、チーム内で議論を重ね、プロジェクトに最適な運用ルールを確立していくことをお勧めします。

運用ルールは一度決めたら終わりではなく、定期的に振り返り、改善していくことが大切です。チーム全体で継続的に改善していくことで、より効率的で品質の高い開発を実現できるでしょう。