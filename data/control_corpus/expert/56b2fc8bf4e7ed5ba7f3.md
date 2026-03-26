**Claude Codeの設定、なんとなくで使っていませんか？**

Hooks、Skills、CLAUDE.md、settings.json、MCP、権限管理…… 2026年のClaude Codeは機能が爆発的に増えた。でも**全部を正しく設定しているエンジニアは1%もいない**。

この記事では、すべての機能を網羅した「本番運用できる設定ファイル一式」を提供する。コピペで即使える。

:::note info
**今すぐ使いたい人向け：** この記事の設定をすべてパッケージ化したリポジトリを公開している。ワンコマンドで任意のプロジェクトにプロビジョニングできる。

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/babushkai/claude-code-config/main/setup.sh)
```

GitHub: https://github.com/babushkai/claude-code-config
:::

## 結論から言うと

Claude Codeの設定は**7つのレイヤー**で構成されている：

1. **CLAUDE.md** - Claudeへの指示書（チーム共有 / 個人用）
2. **Auto Memory** - Claudeが自動で学習するメモ
3. **.claude/rules/** - モジュール型のルールファイル
4. **settings.json** - 権限・許可ツール・環境設定
5. **Hooks** - ライフサイクルイベントの自動化（17イベント）
6. **Skills** - カスタムスラッシュコマンド
7. **MCP** - 外部ツール連携（GitHub, DB, Sentry等）

これら全部を正しく設定して初めて「本番運用」と言える。

## ディレクトリ構成の全体像

まず、完成形のディレクトリ構成を見よう：

```
your-project/
├── CLAUDE.md                    # プロジェクト指示書（git管理）
├── CLAUDE.local.md              # 個人用指示書（gitignore）
├── .mcp.json                    # チーム共有MCP設定（git管理）
├── .claude/
│   ├── CLAUDE.md                # 別名配置OK（CLAUDE.mdと同等）
│   ├── settings.json            # 共有設定（git管理）
│   ├── settings.local.json      # 個人設定（gitignore）
│   ├── rules/                   # モジュール型ルール
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   ├── security.md
│   │   └── frontend/
│   │       ├── react.md
│   │       └── styles.md
│   ├── skills/                  # カスタムスキル
│   │   ├── deploy/
│   │   │   └── SKILL.md
│   │   ├── review-pr/
│   │   │   └── SKILL.md
│   │   └── fix-issue/
│   │       └── SKILL.md
│   ├── agents/                  # カスタムサブエージェント
│   │   └── security-reviewer/
│   │       └── AGENT.md
│   └── hooks/                   # Hookスクリプト
│       ├── lint-on-save.sh
│       ├── block-secrets.sh
│       └── notify-slack.sh
│
├── ~/.claude/                   # ユーザーグローバル設定
│   ├── CLAUDE.md                # 全プロジェクト共通の個人指示
│   ├── settings.json            # グローバル設定
│   ├── settings.local.json      # ローカルのみ
│   ├── rules/                   # 個人ルール
│   │   └── preferences.md
│   └── skills/                  # 個人スキル
│       └── explain-code/
│           └── SKILL.md
```

## 1. CLAUDE.md - Claudeへの指示書

CLAUDE.mdは**Claudeの脳にインストールするプロジェクトのDNA**だ。

### メモリ階層（優先度順）

| 優先度 | 種類 | パス | 用途 |
|--------|------|------|------|
| 最高 | 管理ポリシー | `/Library/Application Support/ClaudeCode/CLAUDE.md` | 組織全体のルール |
| 高 | プロジェクト | `./CLAUDE.md` | チーム共有の指示 |
| 高 | ルール | `.claude/rules/*.md` | モジュール型指示 |
| 中 | ユーザー | `~/.claude/CLAUDE.md` | 個人のグローバル設定 |
| 低 | ローカル | `./CLAUDE.local.md` | 個人のプロジェクト固有設定 |
| 自動 | Auto Memory | `~/.claude/projects/<project>/memory/` | Claudeの自動学習メモ |

### CLAUDE.mdの黄金律：「人間だけが知っていること」を書く

:::note warn
**最も多いミス：ソースコードから読み取れる情報をCLAUDE.mdに書くこと。**

Claudeは`package.json`を読めばビルドコマンドがわかる。`tsconfig.json`を読めばTypeScriptの設定がわかる。ディレクトリを探索すればアーキテクチャがわかる。`.eslintrc`を読めばコーディング規約がわかる。

**これらをCLAUDE.mdに書くのはトークンの無駄遣いだ。**
:::

CLAUDE.mdには**Claudeがソースコードを読んでも絶対にわからない情報**だけを書く：

| 書くべき（人間の頭の中にしかない） | 書くべきでない（コードから推論できる） |
|---|---|
| なぜこのアーキテクチャを選んだのか | `packages/`配下のディレクトリ一覧 |
| 過去のインシデントで学んだ禁止事項 | `pnpm build`でビルドできること |
| ビジネス上の制約や優先順位 | TypeScriptを使っていること |
| デプロイ先の環境情報 | ESLintのルール |
| チーム間の取り決め・ワークフロー | 依存パッケージの一覧 |
| 「このコードは触るな」の暗黙知 | テストフレームワークがVitestであること |

### 本番用CLAUDE.mdテンプレート

```markdown
# プロジェクトの意思決定

## なぜこの構成なのか
- モノレポを採用した理由：フロント・バック間の型共有でバグを3件/週→0にした
- Honoを選んだ理由：Cloudflare Workersでのコールドスタートが50ms以下
- PlanetScaleを使う理由：本番DBのスキーマ変更をブランチで安全にできる

## 絶対にやってはいけないこと
- `packages/shared/src/legacy/` は旧APIとの互換層。リファクタしたくなるが触るな（顧客3社が依存中、2026年Q3に廃止予定）
- Stripeの webhook handler は冪等性を壊すと二重課金が発生する。過去に$12,000の事故があった
- `users`テーブルの`email`カラムにUNIQUE制約がない。歴史的経緯で重複がある。アプリ層でバリデーションしている

## デプロイと環境
- staging: Cloudflare Workers（`wrangler deploy --env staging`）
- production: 本番デプロイはGitHub Actionsのみ。手動デプロイ禁止
- DB migration: `pnpm db:migrate`は必ずstagingで先に実行して確認

## チームワークフロー
- PRは必ず1人以上のレビューを通す
- `feat/`ブランチはsquash merge、`fix/`ブランチは通常merge
- 金曜日の15時以降は本番デプロイ禁止（週末対応を避けるため）

## ビジネスコンテキスト
- エンタープライズ顧客はレスポンス200ms以内のSLAがある
- GDPR対応必須。ユーザーデータは必ず論理削除（物理削除禁止）
- 月次レポート生成は毎月1日深夜にcronで実行。この日はDB負荷が高い
```

:::note info
**このテンプレートのポイント**
- `pnpm install`や`pnpm test`は書いていない → Claudeは`package.json`を読めばわかる
- ディレクトリ構成は書いていない → Claudeは`ls`すればわかる
- 代わりに「なぜ」「やるな」「過去の事故」を書いている → これはコードに書いてない
:::

### @importで外部ファイルを参照

CLAUDE.mdから他のファイルをインポートできる：

```markdown
プロジェクトの概要は @README.md を参照。
利用可能なコマンドは @package.json を確認。
Git運用ルールは @docs/git-workflow.md に従う。

# 個人設定
- @~/.claude/my-project-instructions.md
```

:::note info
**importの注意点**
- 相対パスはCLAUDE.mdがあるディレクトリを起点に解決される
- 最大5階層までの再帰importが可能
- コードブロック内の`@`はimportとして解釈されない
- 初回はインポート許可ダイアログが表示される
:::

### .claude/rules/ - 条件付きルール

特定のファイルパターンに対してだけ適用されるルールが書ける：

```markdown
# .claude/rules/api-rules.md
---
paths:
  - "packages/backend/src/routes/**/*.ts"
---

# API開発ルール

- 全エンドポイントにzodバリデーションを入れる
- エラーレスポンスはRFC 7807形式にする
- レスポンスにはページネーション情報を含める
- レートリミットのヘッダーを返す
```

```markdown
# .claude/rules/react-rules.md
---
paths:
  - "packages/frontend/src/**/*.{tsx,ts}"
---
