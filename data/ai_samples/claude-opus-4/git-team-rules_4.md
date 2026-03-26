# Gitチーム運用ルール：効率的なコラボレーションのためのベストプラクティス

## はじめに

チーム開発において、Gitの運用ルールを明確にすることは、コードの品質維持と開発効率の向上に不可欠です。本記事では、実践的なGitチーム運用ルールについて解説します。

## ブランチ戦略

### 基本ブランチ構成

```
main (or master)
├── develop
├── feature/*
├── release/*
├── hotfix/*
└── bugfix/*
```

### ブランチの役割

- **main**: 本番環境にデプロイされるコード
- **develop**: 開発の最新状態を保持
- **feature/\***: 新機能開発用（例：`feature/user-authentication`）
- **release/\***: リリース準備用（例：`release/1.2.0`）
- **hotfix/\***: 緊急修正用（例：`hotfix/critical-security-patch`）
- **bugfix/\***: バグ修正用（例：`bugfix/login-error`）

## コミットルール

### コミットメッセージの形式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 実例

```bash
feat(auth): ユーザー認証機能を追加

- JWTトークンによる認証を実装
- ログイン/ログアウトAPIを追加
- セッション管理機能を実装

Closes #123
```

### タイプ一覧

- **feat**: 新機能
- **fix**: バグ修正
- **docs**: ドキュメントのみの変更
- **style**: フォーマット修正（コードの動作に影響しない）
- **refactor**: リファクタリング
- **test**: テストの追加・修正
- **chore**: ビルドプロセスやツールの変更

## プルリクエスト（PR）のルール

### PRテンプレート例

```markdown
## 概要
変更内容の簡潔な説明

## 変更内容
- [ ] 機能A の実装
- [ ] テストの追加
- [ ] ドキュメントの更新

## 確認項目
- [ ] コードレビューを依頼した
- [ ] テストが全て通過している
- [ ] ドキュメントを更新した

## 関連Issue
Closes #456
```

### レビュープロセス

1. **最低1名以上のレビュー必須**
2. **CIが全て通過していることを確認**
3. **コンフリクトを解消してからマージ**

## 実践的な運用フロー

### 機能開発の流れ

```bash
# 1. developブランチから作業ブランチを作成
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 開発作業
# ... コードの変更 ...

# 3. 変更をコミット
git add .
git commit -m "feat(module): 新機能を追加"

# 4. リモートにプッシュ
git push origin feature/new-feature

# 5. PRを作成してレビューを依頼
```

### コンフリクト解決の手順

```bash
# 1. 最新のdevelopをマージ
git checkout develop
git pull origin develop
git checkout feature/your-feature
git merge develop

# 2. コンフリクトを解決
# ... コンフリクトを手動で解決 ...

# 3. 解決後コミット
git add .
git commit -m "chore: developブランチとのコンフリクトを解決"
```

## タグ管理

### セマンティックバージョニング

```bash
# バージョンタグの付け方
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

形式：`vMAJOR.MINOR.PATCH`
- **MAJOR**: 後方互換性のない変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: 後方互換性のあるバグ修正

## 禁止事項とベストプラクティス

### ❌ やってはいけないこと

- `git push --force` を共有ブランチで使用
- 大きなバイナリファイルをコミット
- 秘密情報（APIキー、パスワード）をコミット
- mainブランチへの直接コミット

### ✅ 推奨される習慣

- こまめなコミット（1機能1コミット）
- 定期的なリベース or マージでブランチを最新に保つ
- `.gitignore` の適切な設定
- コミット前のコードレビュー

## トラブルシューティング

### よくある問題と解決策

```bash
# 誤ってコミットした場合の取り消し
git reset --soft HEAD~1

# 特定のコミットを取り消し
git revert <commit-hash>

# ブランチを間違えて作業した場合
git stash
git checkout correct-branch
git stash pop
```

## まとめ

効果的なGitチーム運用には、明確なルールと全メンバーの理解が不可欠です。以下のポイントを押さえることで、チームの生産性を大幅に向上させることができます：

1. **明確なブランチ戦略**の採用
2. **統一されたコミットメッセージ**の徹底
3. **レビュープロセス**の確立
4. **定期的なルールの見直し**と改善

これらのルールは、チームの規模や特性に応じて調整することが重要です。定期的に振り返りを行い、より良い運用方法を模索していきましょう。