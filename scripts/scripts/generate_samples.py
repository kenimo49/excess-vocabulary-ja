#!/usr/bin/env python3
"""
generate_samples.py — 6モデル × 10テーマ × 5試行 = 300サンプルのAI文章生成

モデル:
  1. Claude 3 Haiku (claude-3-haiku-20240307)
  2. Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
  3. Claude Sonnet 4 (claude-sonnet-4-20250514)
  4. GPT-4o (gpt-4o)
  5. GPT-OSS 20B (gpt-oss:20b) — Ollama @ autocrew-wsl
  6. Llama 3.2 1B (llama3.2:1b) — Ollama @ autocrew-wsl
"""

import os
import sys
import json
import time
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# ── 設定 ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "ai_samples"

THEMES = [
    ("Pythonの例外処理のベストプラクティス", "python-exception"),
    ("Docker入門ガイド", "docker-intro"),
    ("Gitチーム運用ルール", "git-team-rules"),
    ("REST API設計のベストプラクティス", "rest-api-design"),
    ("Webアプリケーションのセキュリティ対策", "web-security"),
    ("リレーショナルデータベース設計の基本", "rdb-design"),
    ("CI/CDパイプラインの構築方法", "cicd-pipeline"),
    ("コードレビューの効果的なやり方", "code-review"),
    ("ソフトウェアテスト戦略の立て方", "test-strategy"),
    ("チーム開発を円滑に進めるコツ", "team-dev"),
]

PROMPT_TEMPLATE = """以下のテーマについて、技術ブログ記事を書いてください。
テーマ: {theme}
対象読者: エンジニア
文字数: 1000-2000字程度
形式: Markdown"""

TRIALS = 5

# モデル定義
MODELS = {
    "claude-3-haiku": {
        "api_id": "claude-3-haiku-20240307",
        "provider": "anthropic",
        "display_name": "Claude 3 Haiku",
    },
    "claude-opus-4": {
        "api_id": "claude-opus-4-20250514",
        "provider": "anthropic",
        "display_name": "Claude Opus 4",
    },
    "claude-sonnet-4": {
        "api_id": "claude-sonnet-4-20250514",
        "provider": "anthropic",
        "display_name": "Claude Sonnet 4 (latest)",
    },
    "gpt-4o": {
        "api_id": "gpt-4o",
        "provider": "openai",
        "display_name": "GPT-4o",
    },
    "gpt-3.5-turbo": {
        "api_id": "gpt-3.5-turbo",
        "provider": "openai",
        "display_name": "GPT-3.5 Turbo",
    },
    "gpt-oss-20b": {
        "api_id": "gpt-oss:20b",
        "provider": "ollama",
        "display_name": "GPT-OSS 20B (Ollama)",
    },
    "llama3.2-1b": {
        "api_id": "llama3.2:1b",
        "provider": "ollama",
        "display_name": "Llama 3.2 1B (Ollama)",
    },
}

# Ollama SSH設定
OLLAMA_SSH_CMD = "sshpass -p 'Ken096906261' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 autocrew_user@100.72.192.8"
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

JST = timezone(timedelta(hours=9))

# ── API呼び出し ───────────────────────────────────────

def retry(fn, max_retries=3):
    """Exponential backoff リトライ"""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt * 2  # 2s, 4s, 8s
            print(f"  ⚠ リトライ {attempt+1}/{max_retries}: {e} ({wait}s待機)")
            time.sleep(wait)


def call_anthropic(model_id: str, prompt: str) -> str:
    """Anthropic API呼び出し"""
    import anthropic
    client = anthropic.Anthropic()

    def _call():
        response = client.messages.create(
            model=model_id,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    return retry(_call)


def call_openai(model_id: str, prompt: str) -> str:
    """OpenAI API呼び出し"""
    import openai
    client = openai.OpenAI()

    def _call():
        response = client.chat.completions.create(
            model=model_id,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    return retry(_call)


def call_ollama(model_id: str, prompt: str) -> str:
    """Ollama API呼び出し（SSH経由）"""
    # JSONペイロードをエスケープ
    payload = json.dumps({
        "model": model_id,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 4096},
    })
    # シングルクォート内でのエスケープを避けるためbase64経由
    import base64
    b64 = base64.b64encode(payload.encode()).decode()

    def _call():
        cmd = (
            f"{OLLAMA_SSH_CMD} "
            f"\"echo '{b64}' | base64 -d | curl -s -X POST {OLLAMA_ENDPOINT} "
            f"-H 'Content-Type: application/json' -d @-\""
        )
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Ollama SSH error: {result.stderr[:200]}")
        resp = json.loads(result.stdout)
        return resp.get("response", "")

    return retry(_call)


PROVIDERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "ollama": call_ollama,
}


# ── Ollama接続チェック ─────────────────────────────────

def check_ollama_available() -> bool:
    """autocrew-wslのOllamaに接続できるか確認"""
    try:
        base_url = OLLAMA_ENDPOINT.replace("/generate", "")
        cmd = f'{OLLAMA_SSH_CMD} \'curl -s -o /dev/null -w "%{{http_code}}" {base_url}\''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.returncode == 0 and "200" in result.stdout
    except Exception as e:
        print(f"⚠ Ollama接続チェック失敗: {e}")
        return False


# ── メタデータ管理 ────────────────────────────────────

def load_metadata() -> list:
    meta_path = DATA_DIR / "metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return []


def save_metadata(entries: list):
    meta_path = DATA_DIR / "metadata.json"
    meta_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_already_generated(metadata: list, model_key: str, theme_slug: str, trial: int) -> bool:
    return any(
        e["model_key"] == model_key
        and e["theme_slug"] == theme_slug
        and e["trial"] == trial
        for e in metadata
    )


# ── メイン ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI文章サンプル生成")
    parser.add_argument("--models", nargs="*", help="生成するモデルキー（省略時は全モデル）")
    parser.add_argument("--themes", nargs="*", help="生成するテーマslug（省略時は全テーマ）")
    parser.add_argument("--trials", type=int, default=TRIALS, help="試行回数")
    parser.add_argument("--dry-run", action="store_true", help="実行せずプラン表示")
    args = parser.parse_args()

    # .envからキーを読み込み
    for env_path in [
        Path.home() / ".openclaw" / "workspace-anthropic" / ".env",
        Path.home() / "repos" / "sns-operations" / ".env",
    ]:
        if env_path.exists():
            load_dotenv(env_path, override=False)

    # 対象モデルのフィルタ
    target_models = args.models or list(MODELS.keys())
    target_themes = args.themes or [slug for _, slug in THEMES]

    # Ollama接続チェック
    ollama_models = [k for k in target_models if MODELS.get(k, {}).get("provider") == "ollama"]
    ollama_ok = False
    if ollama_models:
        print("🔌 autocrew-wsl Ollama接続チェック...")
        ollama_ok = check_ollama_available()
        if ollama_ok:
            print("  ✅ Ollama接続OK")
        else:
            print("  ❌ Ollama接続不可 → Ollamaモデルをスキップします")
            target_models = [k for k in target_models if k not in ollama_models]

    metadata = load_metadata()
    theme_map = {slug: name for name, slug in THEMES}

    # 生成プラン
    plan = []
    for model_key in target_models:
        if model_key not in MODELS:
            print(f"⚠ 不明なモデル: {model_key} → スキップ")
            continue
        for theme_slug in target_themes:
            if theme_slug not in theme_map:
                print(f"⚠ 不明なテーマ: {theme_slug} → スキップ")
                continue
            for trial in range(1, args.trials + 1):
                if not is_already_generated(metadata, model_key, theme_slug, trial):
                    plan.append((model_key, theme_slug, trial))

    print(f"\n📊 生成プラン: {len(plan)}サンプル "
          f"({len(target_models)}モデル × {len(target_themes)}テーマ × {args.trials}試行, "
          f"既存スキップ済み)")

    if args.dry_run:
        for m, t, tr in plan[:20]:
            print(f"  {m} / {t} / trial-{tr}")
        if len(plan) > 20:
            print(f"  ... 他{len(plan)-20}件")
        return

    if not plan:
        print("✅ 全サンプル生成済み")
        return

    # 生成実行
    success = 0
    errors = 0
    for i, (model_key, theme_slug, trial) in enumerate(plan, 1):
        model = MODELS[model_key]
        theme_name = theme_map[theme_slug]
        prompt = PROMPT_TEMPLATE.format(theme=theme_name)

        print(f"\n[{i}/{len(plan)}] {model['display_name']} / {theme_name} / trial-{trial}")

        try:
            call_fn = PROVIDERS[model["provider"]]
            text = call_fn(model["api_id"], prompt)

            if not text or len(text.strip()) < 100:
                print(f"  ⚠ 生成テキストが短すぎます ({len(text) if text else 0}字) → スキップ")
                errors += 1
                continue

            # 保存
            out_dir = DATA_DIR / model_key
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{theme_slug}_{trial}.md"
            out_path.write_text(text, encoding="utf-8")

            # メタデータ追記
            entry = {
                "model_key": model_key,
                "model_api_id": model["api_id"],
                "model_display_name": model["display_name"],
                "provider": model["provider"],
                "theme": theme_name,
                "theme_slug": theme_slug,
                "trial": trial,
                "char_count": len(text),
                "generated_at": datetime.now(JST).isoformat(),
                "file": str(out_path.relative_to(BASE_DIR)),
            }
            metadata.append(entry)
            save_metadata(metadata)

            print(f"  ✅ {len(text)}字 → {out_path.name}")
            success += 1

            # レート制限対策
            time.sleep(1)

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"完了: {success}成功 / {errors}エラー / {len(plan)}計画")
    print(f"メタデータ: {DATA_DIR / 'metadata.json'} ({len(metadata)}件)")


if __name__ == "__main__":
    main()
