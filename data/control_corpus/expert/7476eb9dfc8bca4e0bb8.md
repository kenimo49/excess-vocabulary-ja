
2025年12月、Anthropicが「Agent Skills」というオープン標準を公開しました。SKILL.mdというMarkdownファイルにエージェントへの指示を書けば、対応するどのツールでもそのスキルが動く、という仕組みです。

注目すべきは、その採用速度です。公開からわずか2か月で、Claude Code、GitHub Copilot、OpenAI Codex CLI、Google Gemini CLI、Cursorという主要5ツールがすべて対応を表明しました。さらに[agentskills.io](https://agentskills.io)の採用ツール一覧を見ると、Roo Code、Amp、TRAE、Mistral Vibe、Databricksなど、27を超えるツール・プラットフォームがロゴを並べています。

この記事では、Agent Skillsとは何か、なぜこれだけ急速に広まったのかを整理した上で、主要5ツールの実装の違いを詳しく比較します。

## Agent Skillsとは何か

Agent Skillsは、AIコーディングエージェントに**手続き的な知識**を渡すためのフォーマットです。

公式サイト（[agentskills.io](https://agentskills.io)）の定義を引用します。

> Agent Skills are folders of instructions, scripts, and resources that agents can discover and use to do things more accurately and efficiently.
>
> （Agent Skillsは、エージェントが発見して利用できる指示・スクリプト・リソースのフォルダです）

これまでも、各ツールには「カスタム命令」のような機能がありました。Claude CodeのCLAUDE.md、CursorのRules、CopilotのGitHub Copilot Instructions──いずれもエージェントにコンテキストを与える手段です。

Agent Skillsがこれらと異なるのは、以下の3点です。

**1. タスク単位で分離できる。** 1つのスキルが1つのフォルダに対応し、コードレビュー、デプロイ、テスト生成といったタスクごとに独立して管理できます。CLAUDE.mdやRulesのように1つのファイルにすべてを詰め込む必要がありません。

**2. 必要なときだけロードされる。** 後述するProgressive Disclosureの仕組みにより、スキルの全文は必要になるまでコンテキストに読み込まれません。これにより、数十のスキルを登録してもコンテキストウィンドウを圧迫しません。

**3. ツール間でポータブルである。** SKILL.mdのフォーマットが標準化されているため、Claude Codeで作ったスキルをCopilotやCursorでもそのまま使えます。

### SKILL.mdの構造

Agent Skillsの中核は `SKILL.md` ファイルです。YAMLフロントマターとMarkdown本文で構成されます。

```yaml
---
name: code-review
description: レビュー観点に沿ってコードレビューを行う。PRレビューやコード品質チェックの際に使用する。
---

## レビュー手順

1. 変更されたファイルの差分を確認する
2. セキュリティ上の問題がないか確認する
3. テストが十分に書かれているか確認する
4. パフォーマンスへの影響を評価する
```

フロントマターの仕様は以下の通りです。

| フィールド | 必須 | 説明 |
|---|---|---|
| `name` | Yes | スキル名。小文字・数字・ハイフンのみ。最大64文字。親ディレクトリ名と一致させる |
| `description` | Yes | スキルの説明。何をするか、いつ使うかを書く。最大1024文字 |
| `license` | No | ライセンス名またはライセンスファイルへの参照 |
| `compatibility` | No | 動作環境の要件（対象ツール、必要なパッケージなど） |
| `metadata` | No | 任意のキーバリュー（author、versionなど） |
| `allowed-tools` | No | スキル実行時に許可するツールのリスト（実験的） |

ディレクトリ構造は以下のようになります。

```text
code-review/
├── SKILL.md          # メインの指示（必須）
├── references/       # 詳細なリファレンス（オプション）
│   └── REFERENCE.md
├── scripts/          # 実行可能なスクリプト（オプション）
│   └── check.sh
└── assets/           # テンプレートやデータ（オプション）
    └── template.md
```

### Progressive Disclosure──段階的な読み込み

Agent Skillsの設計上の特徴が**Progressive Disclosure（段階的開示）** です。仕様書では以下の3段階が定義されています。

| 段階 | ロードされる内容 | トークン目安 | タイミング |
|---|---|---|---|
| Level 1 | `name` と `description` のみ | ~100トークン | エージェント起動時 |
| Level 2 | SKILL.md の全文 | 5,000トークン以下推奨 | スキルが関連すると判断されたとき |
| Level 3 | `scripts/`、`references/`、`assets/` 内のファイル | 必要に応じて | Level 2の内容から参照されたとき |

この仕組みのおかげで、エージェントは起動時にスキル名と概要だけを把握し、ユーザーの質問内容にマッチしたスキルだけを全文ロードします。50個のスキルを登録しても、実際にコンテキストを消費するのは発動した数個だけです。

## 主要5ツールの実装比較

ここからが本題です。同じAgent Skills標準に対応していても、各ツールの実装にはかなりの個性があります。

### Claude Code（Anthropic）

Agent Skillsの発祥元であり、最も機能が充実しています。

| 項目 | 内容 |
|---|---|
| 種別 | CLI（ターミナルエージェント） |
| 成熟度 | GA |
| プロジェクトスキル | `.claude/skills/` |
| 個人スキル | `~/.claude/skills/` |

**検出方式**: Progressive Disclosureに忠実な実装です。起動時に全スキルの`name`と`description`をシステムプロンプトに読み込み、ユーザーの入力内容にマッチしたスキルだけをフルロードします。

**呼び出し方法**: 3つの手段があります。

1. **自動検出** ── ユーザーの入力内容からClaude Codeが判断して自動発動
2. **スラッシュコマンド** ── `/skill-name` で明示的に呼び出し
3. **サブエージェント実行** ── `context: fork` を指定すると、メイン会話とは独立したサブエージェントで実行

**独自機能**: Claude Codeならではの拡張がいくつかあります。

`context: fork`によるサブエージェント実行は、スキルの内容をサブエージェントのプロンプトとして渡し、メインの会話コンテキストとは隔離された環境で実行する機能です。`agent: Explore`のようにエージェントの種類を指定でき、リサーチやコード探索を本筋の会話に影響を与えずに行えます。

`disable-model-invocation: true`を指定すると、そのスキルはユーザーが明示的に`/skill-name`で呼び出したときだけ発動し、Claude Codeが自動的に発動させることはなくなります。デプロイやコミットなど、副作用のあるスキルに適しています。

逆に`user-invocable: false`を指定すると、スラッシュコマンドには表示されなくなり、Claude Codeだけが自動発動できるバックグラウンド知識として機能します。

スキル本文に「ultrathink」という単語を含めると、拡張思考（Extended Thinking）モードが有効になります。複雑な推論を要するスキルで活用できます。

動的コンテキスト注入（`` !`command` ``構文）により、スキル実行前にシェルコマンドを実行し、その結果をプロンプトに埋め込むこともできます。

```yaml
---
name: pr-summary
description: PRの変更内容を要約する
context: fork
agent: Explore
---

## PRコンテキスト
- PR差分: !`gh pr diff`
- 変更ファイル: !`gh pr diff --name-only`

上記の情報をもとにPRを要約してください。
```

- [公式ドキュメント](https://code.claude.com/docs/en/skills)
- [Agent Skills発表ブログ](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)
- [Introducing Agent Skills（リリース発表）](https://www.anthropic.com/news/skills)（2025年12月18日）
- [スキルカタログ](https://github.com/anthropics/skills)

---

### GitHub Copilot（GitHub / Microsoft）

IDE統合・CLI・クラウドエージェントの3面で展開しており、Agent Skillsへの対応も複数のインターフェースにまたがります。

| 項目 | 内容 |
|---|---|
| 種別 | IDE拡張（VS Code）+ CLI + Coding Agent |
| 成熟度 | GA |
| プロジェクトスキル | `.github/skills/`（`.claude/skills/`、`.agents/skills/` も対応） |
| 個人スキル | `~/.copilot/skills/`（`~/.claude/skills/`、`~/.agents/skills/` も対応） |

**検出方式**: Claude Codeと同様のProgressive Disclosure。フロントマターの`name`と`description`をまず読み、マッチ時にSKILL.mdの全文をロードします。

**呼び出し方法**: VS Code 1.109以降では`/skill-name`のスラッシュコマンドに対応。CLIでは`/skills list`でインストール済みスキルの一覧を確認できます。

**独自機能**: 特筆すべきは**後方互換の広さ**です。Copilotは`.github/skills/`に加えて`.claude/skills/`と`.agents/skills/`の3つのディ