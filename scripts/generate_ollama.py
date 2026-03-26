#!/usr/bin/env python3
"""Ollama専用サンプル生成スクリプト（SSH経由）"""

import json
import time
import subprocess
import base64
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "ai_samples"
JST = timezone(timedelta(hours=9))

OLLAMA_SSH_CMD = "sshpass -p 'Ken096906261' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 autocrew_user@100.72.192.8"
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

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

MODELS = {
    "gpt-oss-20b": {
        "api_id": "gpt-oss:20b",
        "display_name": "GPT-OSS 20B (Ollama)",
    },
    "llama3.2-1b": {
        "api_id": "llama3.2:1b",
        "display_name": "Llama 3.2 1B (Ollama)",
    },
}

TRIALS = 5


def load_metadata():
    meta_path = DATA_DIR / "metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return []


def save_metadata(entries):
    meta_path = DATA_DIR / "metadata.json"
    meta_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def is_already_generated(metadata, model_key, theme_slug, trial):
    return any(
        e["model_key"] == model_key and e["theme_slug"] == theme_slug and e["trial"] == trial
        for e in metadata
    )


def call_ollama(model_id, prompt, timeout=300):
    payload = json.dumps({
        "model": model_id,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 4096},
    })
    b64 = base64.b64encode(payload.encode()).decode()
    cmd = (
        f"{OLLAMA_SSH_CMD} "
        f"\"echo '{b64}' | base64 -d | curl -s -X POST {OLLAMA_ENDPOINT} "
        f"-H 'Content-Type: application/json' -d @-\""
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"SSH/curl error: {result.stderr[:300]}")
    if not result.stdout.strip():
        raise RuntimeError("Empty response from Ollama")
    resp = json.loads(result.stdout)
    return resp.get("response", "")


def main():
    metadata = load_metadata()
    theme_map = {slug: name for name, slug in THEMES}

    # Build plan
    plan = []
    for model_key in MODELS:
        for _, theme_slug in THEMES:
            for trial in range(1, TRIALS + 1):
                if not is_already_generated(metadata, model_key, theme_slug, trial):
                    plan.append((model_key, theme_slug, trial))

    print(f"📊 生成プラン: {len(plan)}サンプル")
    if not plan:
        print("✅ 全サンプル生成済み")
        return

    success = 0
    errors = 0
    for i, (model_key, theme_slug, trial) in enumerate(plan, 1):
        model = MODELS[model_key]
        theme_name = theme_map[theme_slug]
        prompt = PROMPT_TEMPLATE.format(theme=theme_name)

        print(f"\n[{i}/{len(plan)}] {model['display_name']} / {theme_name} / trial-{trial}")

        max_retries = 3
        text = None
        for attempt in range(max_retries):
            try:
                text = call_ollama(model["api_id"], prompt)
                if text and len(text.strip()) >= 50:
                    break
                print(f"  ⚠ 短すぎ ({len(text) if text else 0}字), リトライ {attempt+1}/{max_retries}")
                text = None
                time.sleep(3)
            except Exception as e:
                print(f"  ⚠ エラー (attempt {attempt+1}): {e}")
                time.sleep(5)

        if not text or len(text.strip()) < 50:
            print(f"  ❌ スキップ (生成失敗)")
            errors += 1
            continue

        # Save
        out_dir = DATA_DIR / model_key
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{theme_slug}_{trial}.md"
        out_path.write_text(text, encoding="utf-8")

        entry = {
            "model_key": model_key,
            "model_api_id": model["api_id"],
            "model_display_name": model["display_name"],
            "provider": "ollama",
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
        time.sleep(2)

    print(f"\n{'='*50}")
    print(f"完了: {success}成功 / {errors}エラー / {len(plan)}計画")


if __name__ == "__main__":
    main()
