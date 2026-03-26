#!/usr/bin/env python3
"""
generate_diverse_prompts.py — 3ジャンル × 3テーマ × 3モデル × 10試行 = 270サンプル生成

ジャンル:
  1. 日記・エッセイ
  2. ビジネスメール
  3. 雑談・カジュアル
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "ai_samples_diverse"

# .env読み込み（APIキーは sns-operations/.env に集約）
for env_path in [
    Path.home() / "repos" / "sns-operations" / ".env",
    BASE_DIR.parent / ".env",
    BASE_DIR / ".env",
]:
    if env_path.exists():
        load_dotenv(env_path, override=False)

# ── ジャンル定義 ──────────────────────────────────────

GENRES = {
    "diary": {
        "name": "日記・エッセイ",
        "prompt_prefix": "今日あった出来事について、個人的な日記を書いてください。テーマ: ",
        "themes": [
            ("新しい趣味を始めた話", "new-hobby"),
            ("失敗から学んだこと", "lesson-from-failure"),
            ("季節の変わり目に感じること", "changing-seasons"),
        ],
    },
    "business": {
        "name": "ビジネスメール",
        "prompt_prefix": "以下の状況のビジネスメールを書いてください。状況: ",
        "themes": [
            ("プロジェクト遅延の報告", "project-delay"),
            ("新規提案", "new-proposal"),
            ("お礼メール", "thank-you"),
        ],
    },
    "casual": {
        "name": "雑談・カジュアル",
        "prompt_prefix": "友人との会話のように、カジュアルに書いてください。テーマ: ",
        "themes": [
            ("最近ハマっているもの", "recent-obsession"),
            ("おすすめの映画", "movie-recommendation"),
            ("週末の過ごし方", "weekend-plans"),
        ],
    },
}

MODELS = {
    "claude-sonnet-4": {
        "api_id": "claude-sonnet-4-20250514",
        "provider": "anthropic",
    },
    "gpt-4o": {
        "api_id": "gpt-4o",
        "provider": "openai",
    },
    "claude-3-haiku": {
        "api_id": "claude-3-haiku-20240307",
        "provider": "anthropic",
    },
}

TRIALS = 10


def call_anthropic(model_id: str, prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model_id,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def call_openai(model_id: str, prompt: str) -> str:
    import openai
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model_id,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


PROVIDERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
}


def main():
    total = 0
    skipped = 0

    for genre_key, genre in GENRES.items():
        for model_key, model in MODELS.items():
            provider_fn = PROVIDERS[model["provider"]]
            for theme_name, theme_slug in genre["themes"]:
                for trial in range(1, TRIALS + 1):
                    out_dir = DATA_DIR / genre_key / model_key
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_file = out_dir / f"{theme_slug}_trial{trial}.md"

                    if out_file.exists() and out_file.stat().st_size > 100:
                        skipped += 1
                        continue

                    prompt = genre["prompt_prefix"] + theme_name
                    if genre_key == "diary":
                        prompt += "\n\n800〜1500字程度で、自分の体験として書いてください。"
                    elif genre_key == "business":
                        prompt += "\n\n適切な敬語を使い、実務的なメールとして書いてください。"
                    elif genre_key == "casual":
                        prompt += "\n\n500〜1000字程度で、くだけた口調で書いてください。"

                    print(f"  [{genre_key}] {model_key} / {theme_slug} trial{trial} ...", end=" ", flush=True)
                    try:
                        text = provider_fn(model["api_id"], prompt)
                        out_file.write_text(text, encoding="utf-8")
                        total += 1
                        print(f"✅ ({len(text)}字)")
                    except Exception as e:
                        print(f"❌ {e}")

                    time.sleep(1)

    print(f"\n✅ 生成完了: {total}件 (スキップ: {skipped}件)")


if __name__ == "__main__":
    main()
