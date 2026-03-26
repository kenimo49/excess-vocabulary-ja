#!/usr/bin/env python3
"""
collect_control_corpus.py — 初心者 vs 上級者テキスト収集

StackOverflow日本語版APIから回答を収集:
  - 低評価(score 0-1) = 初心者
  - 高評価(score 10+) = 上級者
フォールバック: Qiita記事をLGTM数で分類
"""

import json
import time
import re
import html
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError

BASE_DIR = Path(__file__).resolve().parent.parent
BEGINNER_DIR = BASE_DIR / "data" / "control_corpus" / "beginner"
EXPERT_DIR = BASE_DIR / "data" / "control_corpus" / "expert"
TARGET_COUNT = 100
MIN_BODY_LEN = 200  # 短すぎる回答を除外


def strip_html(text: str) -> str:
    """HTMLタグ除去"""
    text = html.unescape(text)
    text = re.sub(r'<pre><code>.*?</code></pre>', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<code>.*?</code>', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_so_answers(min_score: int, max_score: int | None, target: int, label: str) -> list:
    """StackOverflow API v2.3 で日本語版回答を取得"""
    collected = []
    page = 1
    max_pages = 30

    while len(collected) < target and page <= max_pages:
        params = {
            "order": "desc",
            "sort": "creation",
            "site": "ja.stackoverflow",
            "filter": "withbody",
            "pagesize": 100,
            "page": page,
            "min": min_score,
        }
        if max_score is not None:
            params["max"] = max_score

        url = f"https://api.stackexchange.com/2.3/answers?{urlencode(params)}"
        print(f"  [{label}] page {page}: fetching... ", end="", flush=True)

        try:
            req = Request(url, headers={"Accept-Encoding": "identity"})
            with urlopen(req, timeout=30) as resp:
                import gzip
                raw = resp.read()
                try:
                    data = json.loads(gzip.decompress(raw))
                except:
                    data = json.loads(raw)
        except HTTPError as e:
            print(f"❌ HTTP {e.code}")
            if e.code == 429:
                print("  Rate limited, waiting 60s...")
                time.sleep(60)
                continue
            break
        except Exception as e:
            print(f"❌ {e}")
            break

        items = data.get("items", [])
        print(f"{len(items)} answers", end="")

        for item in items:
            body = strip_html(item.get("body", ""))
            if len(body) < MIN_BODY_LEN:
                continue
            collected.append({
                "answer_id": item["answer_id"],
                "score": item["score"],
                "body": body,
            })

        remaining = data.get("quota_remaining", "?")
        print(f" (total: {len(collected)}, quota: {remaining})")

        if not data.get("has_more", False):
            break
        page += 1
        time.sleep(1)

    return collected[:target]


def try_qiita_fallback(target: int = 100) -> tuple:
    """Qiita APIでLGTM数による分類"""
    from urllib.request import urlopen, Request
    import os

    token = os.environ.get("QIITA_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    beginner = []
    expert = []

    # 上級者: LGTM 50+
    print("  [Qiita expert] fetching...")
    for page in range(1, 11):
        url = f"https://qiita.com/api/v2/items?page={page}&per_page=100&query=stocks:>50"
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=30) as resp:
                items = json.loads(resp.read())
            for item in items:
                body = item.get("body", "")
                if len(body) >= MIN_BODY_LEN and len(expert) < target:
                    expert.append({
                        "id": item["id"],
                        "likes": item.get("likes_count", 0),
                        "body": body[:5000],
                    })
            if len(expert) >= target:
                break
            time.sleep(1)
        except Exception as e:
            print(f"  Qiita error: {e}")
            break

    # 初心者: LGTM 0-2
    print("  [Qiita beginner] fetching...")
    for page in range(1, 11):
        url = f"https://qiita.com/api/v2/items?page={page}&per_page=100&query=stocks:<3"
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=30) as resp:
                items = json.loads(resp.read())
            for item in items:
                body = item.get("body", "")
                if len(body) >= MIN_BODY_LEN and len(beginner) < target:
                    beginner.append({
                        "id": item["id"],
                        "likes": item.get("likes_count", 0),
                        "body": body[:5000],
                    })
            if len(beginner) >= target:
                break
            time.sleep(1)
        except Exception as e:
            print(f"  Qiita error: {e}")
            break

    return beginner[:target], expert[:target]


def save_texts(items: list, out_dir: Path, id_key: str = "answer_id"):
    """テキストをファイルに保存"""
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, item in enumerate(items):
        fid = item.get(id_key, item.get("id", i))
        path = out_dir / f"{fid}.md"
        path.write_text(item["body"], encoding="utf-8")


def main():
    print("📊 コントロールコーパス収集\n")

    # StackOverflow日本語版を試す
    print("── StackOverflow ja ──")
    beginner_items = fetch_so_answers(0, 1, TARGET_COUNT, "beginner")
    expert_items = fetch_so_answers(10, None, TARGET_COUNT, "expert")

    if len(beginner_items) >= 50 and len(expert_items) >= 50:
        print(f"\n✅ StackOverflow: 初心者{len(beginner_items)}件, 上級者{len(expert_items)}件")
        save_texts(beginner_items, BEGINNER_DIR)
        save_texts(expert_items, EXPERT_DIR)
    else:
        print(f"\n⚠ StackOverflow不足（初心者{len(beginner_items)}, 上級者{len(expert_items)}）→ Qiitaフォールバック")
        beginner_items, expert_items = try_qiita_fallback(TARGET_COUNT)
        print(f"✅ Qiita: 初心者{len(beginner_items)}件, 上級者{len(expert_items)}件")
        save_texts(beginner_items, BEGINNER_DIR, id_key="id")
        save_texts(expert_items, EXPERT_DIR, id_key="id")

    # メタデータ保存
    meta = {
        "beginner_count": len(beginner_items),
        "expert_count": len(expert_items),
        "source": "stackoverflow" if len(beginner_items) >= 50 else "qiita",
    }
    meta_path = BASE_DIR / "data" / "control_corpus" / "metadata.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 保存完了: {meta_path.parent}/")


if __name__ == "__main__":
    main()
