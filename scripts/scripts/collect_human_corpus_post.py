#!/usr/bin/env python3
"""
collect_human_corpus_post.py — 2024-2026年の人間記事を収集（共進化分析用）

既存のcollect_human_corpus.pyを基に、日付範囲を2024-2026に変更。
保存先: data/human_corpus_post_llm/
"""

import os
import json
import time
import re
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BASE_DIR / "data" / "human_corpus_post_llm"

JST = timezone(timedelta(hours=9))

# 同じ10テーマ
THEME_TAGS = {
    "python-exception": {
        "qiita_query": "tag:Python 例外処理",
        "zenn_topic": "python",
    },
    "docker-intro": {
        "qiita_query": "tag:Docker 入門",
        "zenn_topic": "docker",
    },
    "git-team-rules": {
        "qiita_query": "tag:Git チーム運用",
        "zenn_topic": "git",
    },
    "rest-api-design": {
        "qiita_query": "tag:API REST設計",
        "zenn_topic": "api",
    },
    "web-security": {
        "qiita_query": "tag:Security Webセキュリティ",
        "zenn_topic": "security",
    },
    "rdb-design": {
        "qiita_query": "tag:Database データベース設計",
        "zenn_topic": "database",
    },
    "cicd-pipeline": {
        "qiita_query": "tag:CI CD パイプライン",
        "zenn_topic": "cicd",
    },
    "code-review": {
        "qiita_query": "コードレビュー",
        "zenn_topic": "codereview",
    },
    "test-strategy": {
        "qiita_query": "tag:テスト ソフトウェアテスト",
        "zenn_topic": "testing",
    },
    "team-dev": {
        "qiita_query": "チーム開発 開発プロセス",
        "zenn_topic": "team",
    },
}

DATE_START = "2024-01-01"
DATE_END = "2026-03-26"


def fetch_qiita_articles(query: str, token: str, per_page: int = 30, max_pages: int = 3) -> list:
    """Qiita APIで記事を検索（2024-2026年）"""
    articles = []
    for page in range(1, max_pages + 1):
        full_query = f"{query} created:>={DATE_START} created:<={DATE_END}"
        params = urllib.parse.urlencode({
            "query": full_query,
            "per_page": per_page,
            "page": page,
        })
        url = f"https://qiita.com/api/v2/items?{params}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data:
                    break
                articles.extend(data)
        except Exception as e:
            print(f"  ⚠ Qiita APIエラー (page {page}): {e}")
            break
        time.sleep(1)
    return articles


def fetch_zenn_articles(topic: str, max_pages: int = 5) -> list:
    """Zenn APIで記事を取得"""
    articles = []
    next_page = None
    for _ in range(max_pages):
        params = {"topicname": topic, "order": "latest"}
        if next_page:
            params["next"] = next_page
        query = urllib.parse.urlencode(params)
        url = f"https://zenn.dev/api/articles?{query}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("articles", [])
                if not items:
                    break
                articles.extend(items)
                next_page = data.get("next_page")
                if not next_page:
                    break
        except Exception as e:
            print(f"  ⚠ Zenn APIエラー: {e}")
            break
        time.sleep(1)
    return articles


def fetch_zenn_article_body(slug: str) -> str:
    """Zenn記事の本文を取得"""
    url = f"https://zenn.dev/api/articles/{slug}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            article = data.get("article", data)
            body_md = article.get("body_md", "")
            if body_md:
                return body_md
            body_html = article.get("body_html", "")
            if body_html:
                import html
                text = html.unescape(body_html)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                return text
            return ""
    except Exception as e:
        print(f"  ⚠ Zenn本文取得エラー ({slug}): {e}")
        return ""


def filter_by_date(articles: list, date_key: str = "published_at") -> list:
    """日付でフィルタ"""
    filtered = []
    for a in articles:
        published = a.get(date_key, "") or a.get("created_at", "")
        if published:
            date_str = published[:10]
            if DATE_START <= date_str <= DATE_END:
                filtered.append(a)
    return filtered


def load_metadata() -> list:
    meta_path = CORPUS_DIR / "metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return []


def save_metadata(entries: list):
    meta_path = CORPUS_DIR / "metadata.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_already_collected(metadata: list, source: str, article_id: str) -> bool:
    return any(e["source"] == source and e["article_id"] == article_id for e in metadata)


def main():
    parser = argparse.ArgumentParser(description="2024-2026年 人間コーパス収集")
    parser.add_argument("--themes", nargs="*")
    parser.add_argument("--qiita-only", action="store_true")
    parser.add_argument("--zenn-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for env_path in [
        Path.home() / "repos" / "sns-operations" / ".env",
    ]:
        if env_path.exists():
            load_dotenv(env_path, override=False)

    qiita_token = os.environ.get("QIITA_TOKEN", "")
    if not qiita_token and not args.zenn_only:
        print("⚠ QIITA_TOKEN未設定 → Qiitaスキップ")

    target_themes = args.themes or list(THEME_TAGS.keys())
    metadata = load_metadata()

    total_qiita = 0
    total_zenn = 0

    for theme_slug in target_themes:
        config = THEME_TAGS[theme_slug]
        print(f"\n{'='*50}")
        print(f"📚 テーマ: {theme_slug}")

        # ── Qiita ──
        if not args.zenn_only and qiita_token:
            print(f"  🔍 Qiita: {config['qiita_query']}")
            articles = fetch_qiita_articles(config["qiita_query"], qiita_token)
            # Filter by min chars
            articles = [a for a in articles if len(a.get("body", "")) >= 500]
            print(f"  → {len(articles)}件取得")

            saved = 0
            out_dir = CORPUS_DIR / "qiita" / theme_slug
            out_dir.mkdir(parents=True, exist_ok=True)

            for a in articles[:20]:
                aid = a["id"]
                if is_already_collected(metadata, "qiita", aid):
                    continue

                body = a.get("body", "")
                out_path = out_dir / f"{aid}.md"
                out_path.write_text(body, encoding="utf-8")

                entry = {
                    "source": "qiita",
                    "article_id": aid,
                    "theme_slug": theme_slug,
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "author": a.get("user", {}).get("id", ""),
                    "created_at": a.get("created_at", ""),
                    "char_count": len(body),
                    "collected_at": datetime.now(JST).isoformat(),
                    "file": str(out_path.relative_to(BASE_DIR)),
                    "period": "post_llm",
                }
                metadata.append(entry)
                saved += 1

            save_metadata(metadata)
            total_qiita += saved
            print(f"  ✅ Qiita: {saved}本保存")

        # ── Zenn ──
        if not args.qiita_only:
            print(f"  🔍 Zenn: topic={config['zenn_topic']}")
            articles = fetch_zenn_articles(config["zenn_topic"])
            articles = filter_by_date(articles)
            print(f"  → {len(articles)}件（2024-2026年）")

            saved = 0
            out_dir = CORPUS_DIR / "zenn" / theme_slug
            out_dir.mkdir(parents=True, exist_ok=True)

            for a in articles[:10]:
                slug = a.get("slug", "")
                if not slug:
                    continue
                if is_already_collected(metadata, "zenn", slug):
                    continue

                body = fetch_zenn_article_body(slug)
                if len(body) < 500:
                    continue
                time.sleep(1)

                out_path = out_dir / f"{slug}.md"
                out_path.write_text(body, encoding="utf-8")

                entry = {
                    "source": "zenn",
                    "article_id": slug,
                    "theme_slug": theme_slug,
                    "title": a.get("title", ""),
                    "url": f"https://zenn.dev/{a.get('user', {}).get('username', '')}/articles/{slug}",
                    "author": a.get("user", {}).get("username", ""),
                    "created_at": a.get("published_at", "") or a.get("created_at", ""),
                    "char_count": len(body),
                    "collected_at": datetime.now(JST).isoformat(),
                    "file": str(out_path.relative_to(BASE_DIR)),
                    "period": "post_llm",
                }
                metadata.append(entry)
                saved += 1

            save_metadata(metadata)
            total_zenn += saved
            print(f"  ✅ Zenn: {saved}本保存")

    print(f"\n{'='*50}")
    print(f"📊 合計: Qiita {total_qiita}本 + Zenn {total_zenn}本 = {total_qiita + total_zenn}本")
    print(f"メタデータ: {CORPUS_DIR / 'metadata.json'} ({len(metadata)}件)")


if __name__ == "__main__":
    main()
