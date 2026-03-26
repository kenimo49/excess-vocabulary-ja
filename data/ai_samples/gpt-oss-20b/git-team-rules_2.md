# Gitチーム運用ルール

## はじめに
Git は分散型バージョン管理の定番ツールですが、プロジェクトが増えると「誰がいつ何をコミットしたか」が曖昧になりがちです。  
ここでは、エンジニアが日常的に使う Git の運用ルールをまとめ、ミスを減らし作業をスムーズにするためのベストプラクティスを紹介します。

## 目的
- **可読性**: コミット履歴を簡単に追える
- **安全性**: 破壊的変更が入る前にレビューできる
- **一貫性**: チーム全員が同じ作業フローを共有

## 1. 基本ルール

| 項目 | 内容 |
|------|------|
| **ブランチ名は短く** | `feature/xxxx` / `bugfix/xxxx` / `hotfix/xxxx` |
| **コミットは小さく** | 1 つの変更点に対して 1 回のコミット |
| **PR は必ず作成** | 直接 `main` に push しない |
| **レビューは 2 人** | 1 人が作業者、もう 1 人がレビュアー |
| **CI が通っていることを確認** | PR マージ前にすべてのビルドが成功していること |

## 2. ブランチ戦略

### 2‑1. Git Flow（軽量版）
```
main (production) ←  → release → hotfix
dev  ←  → feature ←  → bugfix
```

- **`main`** は常にデプロイ可能状態
- **`dev`** は開発中の統合ブランチ
- **`feature/*`**, **`bugfix/*`** は短期間で完結させ、`dev` にマージ

### 2‑2. Trunk Based Development
- `main` を 1 つだけ持ち、`feature/*` も短期的に作成・マージ
- CI が失敗したらすぐにロールバック
- 大規模な機能は **feature flag** でリリース

## 3. コミットメッセージ

```
[タイプ] 説明（50文字以内）
（空行）
詳細（任意、80文字単位で改行）
```

| タイプ | 例 |
|--------|----|
| feat | Add login page |
| fix | Fix crash on null check |
| docs | Update README |
| style | Reformat code |
| test | Add unit test for utils |
| refactor | Simplify pagination logic |

- **Jira/Trello などのタスク番号** を含めるとトレーサビリティが向上
  ```
  feat: Add search API (#123)
  ```

## 4. Pull Request（PR）のルール

| 項目 | 具体例 |
|------|--------|
| **タイトル** | タスク番号＋概要 |
| **本文** | 変更点、理由、テスト手順 |
| **レビュアー** | 少なくとも 1 人 |
| **コメント** | 変更箇所を明確に指摘 |
| **マージ** | `git merge --no-ff` で履歴を残す |

### 4‑1. PR でのコードレビュー
- **一度に 20 行以下** を確認
- **機能、ロジック、テスト、ドキュメント** すべてチェック
- **自動化**: Lint、Unit Test、Coverage が必須

## 5. CI/CD の連携

- **GitHub Actions / GitLab CI** でビルド・テストを自動化
- `pre-commit` フックでフォーマッタを走らせる
- PR 時点で **静的解析** と **Unit Test** を必須に

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install deps
        run: npm ci
      - name: Lint
        run: npm run lint
      - name: Test
        run: npm test -- --coverage
```

## 6. タグ（Release）

- **Semantic Versioning**: `vMAJOR.MINOR.PATCH`
- **Release ブランチ** は `main` から作り、タグを付与
- GitHub の **Release ページ** に changelog を添付

```bash
git tag -a v1.2.0 -m "Add new auth flow"
git push origin v1.2.0
```

## 7. マージ戦略

| 戦略 | 使い方 | メリット |
|------|--------|----------|
| **Merge commit** | `git merge` | 履歴が分かりやすい |
| **Rebase** | `git rebase` | クリーンな直線履歴 |
| **Squash** | PR の `Squash & merge` | 一つのコミットにまとめる |

- 重要: **`--ff-only`** を使って fast‑forward のみ許可し、マージコミットは残すかしないかで統一

## 8. コラボレーションのポイント

1. **リポジトリ設定**  
   - **Protected branches** で直接 push を制限  
   - **Branch protection rules** で CI 失敗時はマージ不可

2. **Issue テンプレート**  
   - バグ報告と機能要望を統一  
   - 必要情報（再現手順、期待動作、環境）を必ず入力

3. **ドキュメント**  
   - `CONTRIBUTING.md` にルールを明記  
   - `docs/` に設計・インフラ構成を整理

## 9. トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| **コンフリクトが頻発** | 大きな機能ブランチで長期開発 | 小さく頻繁にマージ、`rebase` で解消 |
| **CI 失敗後のマージ** | ビルドキャッシュが古い | `--force` で再ビルド、キャッシュ無効化 |
| **コミット履歴が乱雑** | 無計画な PR | `git rebase -i` で整理、`git filter-branch` でクリーンアップ |

## 10. まとめ

Git チーム運用は「ツール自体」よりも「人とルール」によって品質が左右されます。  
上記のルールをベースに、プロジェクトの規模や文化に合わせて微調整し、**コードレビュー、CI、タグ付け** をしっかり連携させることで、開発効率と品質を大幅に向上できます。

---

> **Tip**  
> 初期段階では「無理に完璧を目指さない」ことも重要です。  
> 小さな失敗を通じてルールを改善し、チーム全員が快適に使える運用を構築しましょう。