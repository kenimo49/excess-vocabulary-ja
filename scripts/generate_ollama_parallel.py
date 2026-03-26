#!/usr/bin/env python3
"""Ollama専用サンプル生成 - 指定モデルのみ"""

import json
import time
import subprocess
import base64
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "ai_samples"
META_LOCK = DATA_DIR / ".meta_lock"
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

ALL_MODELS = {
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


def save_metadata_entry(entry):
    """Append a single entry to metadata.json (file-level atomic)"""
    import fcntl
    meta_path = DATA_DIR / "metadata.json"
    lock_path = DATA_DIR / ".metadata.lock"
    
    with open(lock_path, 'w') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            if meta_path.exists():
                data = json.loads(meta_path.read_text(encoding="utf-8"))
            else:
                data = []
            data.append(entry)
            meta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def is_file_exists(model_key, theme_slug, trial):
    return (DATA_DIR / model_key / f"{theme_slug}_{trial}.md").exists()


def call_ollama(model_id, prompt, timeout=600):
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
        raise RuntimeError("Empty response")
    resp = json.loads(result.stdout)
    return resp.get("response", "")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <model_key>")
        print(f"Available: {', '.join(ALL_MODELS.keys())}")
        sys.exit(1)
    
    model_key = sys.argv[1]
    if model_key not in ALL_MODELS:
        print(f"Unknown model: {model_key}")
        sys.exit(1)
    
    model = ALL_MODELS[model_key]
    theme_map = {slug: name for name, slug in THEMES}

    # Build plan (check file existence instead of metadata to avoid race conditions)
    plan = []
    for _, theme_slug in THEMES:
        for trial in range(1, TRIALS + 1):
            if not is_file_exists(model_key, theme_slug, trial):
                plan.append((theme_slug, trial))

    print(f"📊 [{model['display_name']}] 生成プラン: {len(plan)}サンプル")
    if not plan:
        print("✅ 全サンプル生成済み")
        return

    success = 0
    errors = 0
    for i, (theme_slug, trial) in enumerate(plan, 1):
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

        # Save file
        out_dir = DATA_DIR / model_key
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{theme_slug}_{trial}.md"
        out_path.write_text(text, encoding="utf-8")

        # Save metadata
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
        save_metadata_entry(entry)

        print(f"  ✅ {len(text)}字 → {out_path.name}")
        success += 1
        time.sleep(2)

    print(f"\n{'='*50}")
    print(f"[{model['display_name']}] 完了: {success}成功 / {errors}エラー / {len(plan)}計画")


if __name__ == "__main__":
    main()
