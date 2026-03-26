# Gitチーム運用ルール ― エンジニア向け実践ガイド

開発チームがスムーズに動くために欠かせないのが **Git の運用ルール** です。  
個々が自由にコミットしてしまうと、メンテナンス性が下がったり、レビューが煩雑になったりします。  
この記事では、実際にチームで導入しやすいルールとその根拠、設定例を紹介します。  
※ 文字数は約1,600文字です。  

---

## 1. なぜルールが必要か

| 事例 | 影響 | ルールで解決 |
|------|------|-------------|
| 1. **混在ブランチ**（`master` で直接開発） | 本番と開発が混ざり、デプロイ失敗 | `main` は常にデプロイ可能にする |
| 2. **乱れたコミットメッセージ** | バグトラッキングが困難 | 公式フォーマットを強制 |
| 3. **レビュー無しでマージ** | バグ混入 | PR/レビュー必須ルール |

> **結論**  
> ルールは「作業を標準化し、障害の早期検知を可能にする」役割を果たします。

---

## 2. 基本構成

1. **ブランチ戦略**  
2. **コミットメッセージ規格**  
3. **Pull Request（PR）ルール**  
4. **Git Hook の活用**  
5. **CI/CD 連携**  

---

## 3. ブランチ戦略

### 3‑1. GitFlow + Release Branch

| ブランチ | 目的 | 保守方法 |
|----------|------|----------|
| `main` | 本番リリース | `--force-with-lease` で更新、レビュー必須 |
| `develop` | 次リリースの集約 | PR でマージ |
| `feature/*` | 個別機能 | `develop` から分岐し、PR で `develop` へ戻す |
| `release/*` | リリース前の安定化 | `develop` から分岐し、`main` と `develop` にマージ |
| `hotfix/*` | 本番バグ修正 | `main` から分岐し、両方にマージ |

> **ポイント**  
> * ブランチ名は `feature/`、`hotfix/` で始める  
> * PR のタイトルは `feat: <概要>` など **Conventional Commits** を採用  

---

## 4. コミットメッセージ規格

### 4‑1. Conventional Commits

```text
<type>[optional scope]: <short summary>

[optional body]

[optional footer(s)]
```

| type | 例 | 用途 |
|------|----|------|
| `feat` | `feat: add login API` | 新機能 |
| `fix` | `fix: resolve null pointer` | バグ修正 |
| `docs` | `docs: update README` | ドキュメント |
| `style` | `style: format code` | コード整形 |
| `refactor` | `refactor: optimize query` | リファクタリング |
| `test` | `test: add unit tests` | テスト追加 |
| `chore` | `chore: bump version` | ビルド関連 |

> **例**  
> ```git
> git commit -m "feat: add OAuth2 support"
> ```
> これにより `git log --oneline --graph --all --decorate` が見やすくなります。

### 4‑2. コミット制限

* 1 コミット＝1 変更点（機能・修正）  
* 大規模変更は **複数コミット** に分割  
* **不要なコミット**（`git reset --soft` でコミット前にまとめる）

---

## 5. Pull Request（PR）ルール

| 要件 | 説明 |
|------|------|
| **必須レビュー** | 1 人以上のレビューアが承認 |
| **CI パス必須** | すべてのテストが Pass |
| **タイトル & 本文** | タイプを明示し、変更点を要約 |
| **チェックリスト** | `<---` で必須項目を記載 |
| **ファイルの範囲** | `git diff --name-status` で変更ファイルを限定 |

```markdown
## チェックリスト
- [ ] 変更点を README に反映
- [ ] コードフォーマットが統一されている
- [ ] ユニットテストが増えている
- [ ] 変更に伴うデプロイ手順が記載
```

> **実装例**  
> GitHub Actions で `pull_request` イベント時に **Lint & Test** を自動実行し、失敗すればマージ不可にする設定。

---

## 6. Git Hook での自動チェック

| Hook | 目的 | 実装例 |
|------|------|--------|
| `pre-commit` | コーディング規約、Lint | `pre-commit install`（https://pre-commit.com/） |
| `commit-msg` | メッセージフォーマット | `commitlint` で Conventional Commits を検証 |
| `pre-push` | テスト失敗でプッシュ不可 | `npm test` 実行 |

```bash
# commit-msg の例
#!/bin/sh
npx --no-install commitlint --edit $1
```

> **メリット**  
> エラーが即座に分かり、チーム全体の品質を担保。

---

## 7. CI/CD 連携

* **CI**:  
  * `lint`, `test`, `build` を自動実行  
  * PR 時に `build` 成功が必須  
* **CD**:  
  * `main` へのマージで自動デプロイ  
  * バージョンタグ作成でリリースノート生成

```yaml
# GitHub Actions 例
name: CI

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm test
```

---

## 8. まとめ

| ルール | 期待効果 |
|--------|----------|
| **ブランチ戦略** | デプロイ前のバグ混入を防止 |
| **コミット規格** | 履歴の可読性向上 |
| **PR 必須** | コード品質の一貫性 |
| **Git Hook** | 手作業ミスを減らす |
| **CI/CD** | 早期フィードバック |

> **実践のコツ**  
> 1. **小さく始める**：まずはコミットメッセージと PR チェックリストを導入。  
> 2. **教育**：チーム全員にルールと理由を共有。  
> 3. **継続的改善**：ルールに対するフィードバックを定期的にレビュー。

チームの Git 運用は「規則を守ること」だけでなく「みんなが同じリズムで動くこと」が成功の鍵です。  
ぜひ、この記事を基に自分たちの開発フローに合わせてルールを設計し、品質とスピードを両立させてください。