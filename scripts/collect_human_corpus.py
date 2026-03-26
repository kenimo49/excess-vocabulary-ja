#!/usr/bin/env python3
"""
collect_human_corpus.py — Qiita/Zenn APIで2020-2022年の技術記事を収集

各テーマ20本目標（Qiita 10-15本 + Zenn 5-10本）
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
CORPUS_DIR = BASE_DIR / "data" / "human_corpus"

JST = timezone(timedelta(hours=9))

# テーマ → 検索キーワード/タグのマッピング
THEME_TAGS = {
    "python-exception": {
        "qiita_query": "tag:Python 例外処理",
        "qiita_tags": ["Python"],
        "zenn_topic": "python",
    },
    "docker-intro": {
        "qiita_query": "tag:Docker 入門",
        "qiita_tags": ["Docker"],
        "zenn_topic": "docker",
    },
    "git-team-rules": {
        "qiita_query": "tag:Git チーム運用",
        "qiita_tags": ["Git"],
        "zenn_topic": "git",
    },
    "rest-api-design": {
        "qiita_query": "tag:API REST設計",
        "qiita_tags": ["API", "REST"],
        "zenn_topic": "api",
    },
    "web-security": {
        "qiita_query": "tag:Security Webセキュリティ",
        "qiita_tags": ["Security"],
        "zenn_topic": "security",
    },
    "rdb-design": {
        "qiita_query": "tag:Database データベース設計",
        "qiita_tags": ["Database", "SQL"],
        "zenn_topic": "database",
    },
    "cicd-pipeline": {
        "qiita_query": "tag:CI CD パイプライン",
        "qiita_tags": ["CI", "CD"],
        "zenn_topic": "cicd",
    },
    "code-review": {
        "qiita_query": "コードレビュー",
        "qiita_tags": [],
        "zenn_topic": "codereview",
    },
    "test-strategy": {
        "qiita_query": "tag:テスト ソフトウェアテスト",
        "qiita_tags": ["テスト"],
        "zenn_topic": "testing",
    },
    "team-dev": {
        "qiita_query": "チーム開発 開発プロセス",
        "qiita_tags": [],
        "zenn_topic": "team",
    },
}

# ── Qiita API ────────────────────────────────────────

def fetch_qiita_articles(query: str, token: str, per_page: int = 20, max_pages: int = 3) -> list:
    """Qiita APIで記事を検索（2020-2022年フィルタ付き）"""
    articles = []
    for page in range(1, max_pages + 1):
        full_query = f"{query} created:>=2019-01-01 created:<=2023-12-31"
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

        time.sleep(1)  # レート制限: 1リクエスト/秒

    return articles


def filter_qiita_articles(articles: list, min_chars: int = 500) -> list:
    """Qiita記事をフィルタ（短すぎる記事を除外）"""
    filtered = []
    for a in articles:
        body = a.get("body", "")
        if len(body) >= min_chars:
            filtered.append(a)
    return filtered


# ── Zenn API ─────────────────────────────────────────

def fetch_zenn_articles(topic: str, max_pages: int = 3) -> list:
    """Zenn APIで記事を取得"""
    articles = []
    next_page = None

    for _ in range(max_pages):
        params = {"topicname": topic, "order": "daily"}
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
    """Zenn記事の本文を取得（body_html → テキスト変換）"""
    url = f"https://zenn.dev/api/articles/{slug}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            article = data.get("article", data)
            # body_md がある場合はそのまま使用
            body_md = article.get("body_md", "")
            if body_md:
                return body_md
            # body_html から HTMLタグを除去してテキスト化
            body_html = article.get("body_html", "")
            if body_html:
                import html
                import re as _re
                text = html.unescape(body_html)
                text = _re.sub(r'<[^>]+>', ' ', text)
                text = _re.sub(r'\s+', ' ', text).strip()
                return text
            return ""
    except Exception as e:
        print(f"  ⚠ Zenn本文取得エラー ({slug}): {e}")
        return ""


def filter_zenn_by_date(articles: list, start: str = "2019-01-01", end: str = "2023-12-31") -> list:
    """Zenn記事を日付でフィルタ"""
    filtered = []
    for a in articles:
        published = a.get("published_at", "") or a.get("created_at", "")
        if published:
            date_str = published[:10]  # YYYY-MM-DD
            if start <= date_str <= end:
                filtered.append(a)
    return filtered


# ── メタデータ管理 ────────────────────────────────────

def load_metadata() -> list:
    meta_path = CORPUS_DIR / "metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return []


def save_metadata(entries: list):
    meta_path = CORPUS_DIR / "metadata.json"
    meta_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_already_collected(metadata: list, source: str, article_id: str) -> bool:
    return any(e["source"] == source and e["article_id"] == article_id for e in metadata)


# ── メイン ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="人間コーパス収集")
    parser.add_argument("--themes", nargs="*", help="収集するテーマslug（省略時は全テーマ）")
    parser.add_argument("--qiita-only", action="store_true")
    parser.add_argument("--zenn-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # .envからキーを読み込み
    for env_path in [
        Path.home() / "repos" / "sns-operations" / ".env",
        Path.home() / ".openclaw" / "workspace-anthropic" / ".env",
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
        if theme_slug not in THEME_TAGS:
            print(f"⚠ 不明なテーマ: {theme_slug}")
            continue

        config = THEME_TAGS[theme_slug]
        print(f"\n{'='*50}")
        print(f"📚 テーマ: {theme_slug}")

        # ── Qiita ──
        if not args.zenn_only and qiita_token:
            print(f"  🔍 Qiita: {config['qiita_query']}")
            articles = fetch_qiita_articles(config["qiita_query"], qiita_token, per_page=30, max_pages=3)
            articles = filter_qiita_articles(articles)
            print(f"  → {len(articles)}件取得")

            saved = 0
            out_dir = CORPUS_DIR / "qiita" / theme_slug
            out_dir.mkdir(parents=True, exist_ok=True)

            for a in articles[:30]:  # 最大30本
                aid = a["id"]
                if is_already_collected(metadata, "qiita", aid):
                    continue
                if args.dry_run:
                    print(f"    [dry-run] {a['title'][:40]}...")
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
                }
                metadata.append(entry)
                saved += 1

            if not args.dry_run:
                save_metadata(metadata)
            total_qiita += saved
            print(f"  ✅ Qiita: {saved}本保存")

        # ── Zenn ──
        if not args.qiita_only:
            print(f"  🔍 Zenn: topic={config['zenn_topic']}")
            articles = fetch_zenn_articles(config["zenn_topic"], max_pages=5)
            articles = filter_zenn_by_date(articles)
            print(f"  → {len(articles)}件（2020-2022年）")

            saved = 0
            out_dir = CORPUS_DIR / "zenn" / theme_slug
            out_dir.mkdir(parents=True, exist_ok=True)

            for a in articles[:20]:  # 最大20本
                slug = a.get("slug", "")
                if not slug:
                    continue
                if is_already_collected(metadata, "zenn", slug):
                    continue
                if args.dry_run:
                    print(f"    [dry-run] {a.get('title', '')[:40]}...")
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
                }
                metadata.append(entry)
                saved += 1

            if not args.dry_run:
                save_metadata(metadata)
            total_zenn += saved
            print(f"  ✅ Zenn: {saved}本保存")

    print(f"\n{'='*50}")
    print(f"📊 合計: Qiita {total_qiita}本 + Zenn {total_zenn}本 = {total_qiita + total_zenn}本")
    print(f"メタデータ: {CORPUS_DIR / 'metadata.json'} ({len(metadata)}件)")


if __name__ == "__main__":
    main()
