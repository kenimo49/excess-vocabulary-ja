# Gitチーム運用ルール：効率的な開発フローを実現するベストプラクティス

## はじめに

複数人でのソフトウェア開発において、Gitの運用ルールを明確にすることは、コードの品質維持と開発効率向上に不可欠です。統一されたルールがないと、コンフリクトの頻発、履歴の混乱、レビュープロセスの破綻など、様々な問題が発生します。

本記事では、実際のチーム開発で効果的なGit運用ルールを紹介し、その導入方法と運用のポイントについて解説します。

## ブランチ戦略

### Git Flow vs GitHub Flow

チームの規模や開発サイクルに応じてブランチ戦略を選択することが重要です。

**Git Flow（大規模・長期開発向け）**
- `main`: 本番環境のコード
- `develop`: 開発統合ブランチ
- `feature/*`: 機能開発ブランチ
- `release/*`: リリース準備ブランチ
- `hotfix/*`: 緊急修正ブランチ

**GitHub Flow（小規模・高頻度リリース向け）**
- `main`: 常にデプロイ可能な状態
- `feature/*`: 機能開発ブランチのみ

```bash
# GitHub Flowの例
git checkout main
git pull origin main
git checkout -b feature/user-authentication
# 開発作業
git add .
git commit -m "feat: add user authentication"
git push origin feature/user-authentication
# プルリクエスト作成 → レビュー → マージ
```

## コミットメッセージ規約

### Conventional Commits の採用

統一されたコミットメッセージフォーマットにより、変更内容の理解と自動化が容易になります。

**基本フォーマット:**
```
<type>(<scope>): <description>

<body>

<footer>
```

**主なtype一覧:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードフォーマット
- `refactor`: リファクタリング
- `test`: テストコード
- `chore`: ビルド・設定ファイル更新

**良い例:**
```
feat(auth): add JWT token validation

- Implement token expiration check
- Add refresh token mechanism
- Update error handling for invalid tokens

Closes #123
```

**悪い例:**
```
fix bug
update code
WIP
```

## プルリクエスト（マージリクエスト）運用

### PRの作成ルール

1. **1PR = 1機能**: 変更範囲を明確にし、レビューしやすくする
2. **テンプレートの活用**: 必要な情報を漏れなく記載
3. **適切なサイズ**: 300行以下を目安とする

**PRテンプレート例:**
```markdown
## 概要
<!-- 何を変更したか簡潔に説明 -->

## 変更内容
- [ ] 機能A の実装
- [ ] テストコード追加
- [ ] ドキュメント更新

## 確認事項
- [ ] テストが通ること
- [ ] コーディング規約に準拠していること
- [ ] 破壊的変更がないこと

## 関連Issue
Closes #123
```

### レビューガイドライン

**レビュアーのチェックポイント:**
- [ ] 機能要件を満たしているか
- [ ] コードの可読性・保守性
- [ ] パフォーマンスに影響がないか
- [ ] セキュリティ上の問題がないか
- [ ] テストカバレッジが十分か

**レビューコメントのマナー:**
```markdown
// 良い例
suggestion: この処理は関数として切り出すと再利用しやすくなると思います

// 避けるべき例
ここダメです
なんでこんなコード書いたの？
```

## マージポリシー

### マージ方法の統一

**Squash and Merge（推奨）**
- 機能単位で履歴がまとまり、mainブランチが整理される
- コミット履歴が分かりやすくなる

```bash
# Squash Mergeの結果
* feat: add user authentication feature
* feat: implement file upload functionality  
* fix: resolve login validation bug
```

**Merge Commit**
- 開発履歴を詳細に残したい場合に使用
- ブランチの分岐・マージが明確になる

### マージ前の必須条件

1. **CI/CDパイプラインの通過**: 全テストとビルドが成功
2. **必要な承認数**: 最低1名（重要な変更は2名以上）
3. **コンフリクトの解決**: マージ前に必ず解決
4. **ブランチの最新化**: mainブランチの最新変更を取り込み

## 運用上の注意点とトラブルシューティング

### よくある問題と対処法

**コンフリクトの頻発**
```bash
# 定期的なリベースでコンフリクトを最小化
git checkout feature/my-feature
git rebase origin/main
# コンフリクト解決後
git rebase --continue
```

**コミット履歴の汚染**
```bash
# インタラクティブリベースでコミットを整理
git rebase -i HEAD~3
# pick, squash, editなどでコミットを調整
```

**誤ったマージの取り消し**
```bash
# マージコミットの取り消し
git revert -m 1 <merge-commit-hash>
```

### チーム内でのルール共有

1. **README.mdへの記載**: リポジトリにルールを明文化
2. **定期的なレビュー会**: ルールの見直しと改善
3. **新メンバーへのオンボーディング**: ルールの説明と実践
4. **ツールによる自動化**: commitlint、husky等でルール遵守を強制

## まとめ

効果的なGit運用ルールの確立は、チーム開発の生産性向上に直結します。重要なポイントは：

- **チームの状況に適したブランチ戦略の選択**
- **統一されたコミットメッセージ規約の採用**
- **効率的なプルリクエストフローの構築**
- **明確なマージポリシーの設定**

ルールは一度決めて終わりではなく、チームの成長や開発の変化に応じて継続的に見直し、改善していくことが大切です。まずは基本的なルールから始めて、チーム全体で合意形成を図りながら運用を進めていきましょう。