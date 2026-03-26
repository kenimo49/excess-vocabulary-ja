# Gitチーム運用ルール：チーム開発を成功に導くベストプラクティス

チーム開発において、Gitの運用ルールを明確に定めることは、プロジェクトの成功に直結します。この記事では、実際のチーム開発で効果的なGit運用ルールについて解説します。

## なぜGit運用ルールが必要なのか

複数人で開発を行う際、統一されたルールがないと以下のような問題が発生します：

- コミット履歴が混乱し、変更内容が追跡困難になる
- 競合（conflict）の頻発と解決の困難化
- リリース時の品質管理が困難になる
- レビュー効率の低下

これらの問題を解決するために、チーム全体で統一されたGit運用ルールが必要です。

## ブランチ戦略

### Git Flow

多くのチームで採用されているGit Flowでは、以下のブランチ構成を推奨します：

```
main (master)     # 本番環境用
├─ develop        # 開発統合用
   ├─ feature/    # 機能開発用
   ├─ release/    # リリース準備用
   └─ hotfix/     # 緊急修正用
```

### GitHub Flow（シンプルな運用の場合）

```
main              # 本番環境用
├─ feature/login  # 機能開発用
├─ feature/api    # 機能開発用
└─ hotfix/bug123  # 緊急修正用
```

## コミットルール

### コミットメッセージの書き方

Conventional Commitsに基づいたフォーマットを推奨します：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### typeの種類
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット修正
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: その他

#### 良いコミットメッセージの例

```bash
feat(auth): ユーザーログイン機能を追加

- JWT認証の実装
- ログイン画面のUI作成
- バリデーション機能の追加

Closes #123
```

```bash
fix(api): ユーザー情報取得時のnullポインタエラーを修正

ユーザーが存在しない場合のエラーハンドリングを追加

Fixes #456
```

### コミット粒度の原則

1. **1コミット1機能**: 関連する変更をまとめ、無関係な変更は分ける
2. **ビルド可能な状態**: 各コミットでビルドが通る状態を保つ
3. **適切なサイズ**: 大きすぎず小さすぎない、レビューしやすい粒度

## プルリクエスト（マージリクエスト）ルール

### PRの作成基準

```markdown
## 概要
この機能の目的と実装内容を簡潔に説明

## 変更内容
- [ ] 新機能の追加
- [ ] バグ修正
- [ ] テストの追加

## 確認事項
- [ ] 関連するテストが通っている
- [ ] ドキュメントを更新した
- [ ] セルフレビューを実施した

## 関連Issue
Closes #123
```

### レビューガイドライン

#### レビュアーの責任
- **コード品質**: 可読性、保守性の確認
- **設計**: アーキテクチャや設計原則への準拠
- **テスト**: 適切なテストの実装確認
- **セキュリティ**: 脆弱性のチェック

#### レビュー時の注意点
```bash
# 建設的なフィードバック例
# Good
この処理はextractメソッドでメソッド抽出すると可読性が向上しそうです

# Bad  
このコードは汚い
```

## マージ戦略

### Squash and Merge（推奨）
```bash
# 機能ブランチの複数コミットを1つにまとめてマージ
git checkout main
git merge --squash feature/login
git commit -m "feat(auth): ユーザーログイン機能を追加"
```

### Merge Commit
```bash
# マージコミットを作成（履歴を保持）
git checkout main
git merge --no-ff feature/login
```

## CI/CD連携ルール

### 自動チェック項目

```yaml
# GitHub Actions example
name: CI
on:
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: npm test
      - name: Lint check
        run: npm run lint
      - name: Type check
        run: npm run type-check
```

### マージ条件
- すべてのCIが通過
- 最低1人以上のレビュー承認
- 競合（conflict）の解消済み
- ブランチが最新状態

## 日常的な運用Tips

### コードレビューの効率化
```bash
# レビュー前の自己チェック
git log --oneline origin/main..HEAD  # 変更内容の確認
git diff origin/main..HEAD           # 差分の確認
```

### トラブル時の対処法
```bash
# 間違ったコミットの修正
git commit --amend -m "正しいコミットメッセージ"

# 直前のコミットを取り消し
git reset --soft HEAD^

# 強制プッシュ（※チーム開発では要注意）
git push --force-with-lease origin feature/branch
```

## まとめ

効果的なGit運用ルールの確立により、チーム開発の品質と効率を大幅に向上できます。重要なポイントは：

1. **チーム全体での合意**: ルールはチーム全員で決めて共有する
2. **継続的な改善**: 定期的にルールを見直し、チームに適した形に改善
3. **自動化の活用**: CIツールやGitフックを活用して、ルールの遵守を自動化
4. **教育とサポート**: 新メンバーへのルール説明と継続的なサポート

これらのルールを参考に、あなたのチームに最適なGit運用を確立してください。