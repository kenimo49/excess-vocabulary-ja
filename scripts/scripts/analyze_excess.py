#!/usr/bin/env python3
"""
analyze_excess.py — Excess Word Score算出

手法:
  1. 人間コーパスでの単語の正規化頻度（ベースライン）
  2. AI生成テキストでの同じ単語の正規化頻度
  3. excess_score = (AI_freq - human_freq) / human_freq
  4. 上位を「Japanese AI Slop Words」として出力
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
JST = timezone(timedelta(hours=9))

# ── ユーティリティ ─────────────────────────────────────

def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def normalize_freq(freq: dict) -> dict:
    """絶対頻度を正規化（合計=1.0）"""
    total = sum(freq.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in freq.items()}


def compute_excess_scores(ai_freq: dict, human_freq: dict, min_ai_count: int = 5,
                          min_human_count: int = 2) -> list:
    """
    Excess Score算出

    - min_ai_count: AI側で最低この回数出現した語のみ対象
    - min_human_count: 人間側でこの回数未満の語は「AI固有語」として別扱い
    """
    # 正規化前の絶対頻度を保持
    ai_raw = ai_freq
    human_raw = human_freq

    ai_norm = normalize_freq(ai_freq)
    human_norm = normalize_freq(human_freq)

    results = []
    ai_only_words = []

    for word, ai_nf in ai_norm.items():
        ai_count = ai_raw.get(word, 0)
        if ai_count < min_ai_count:
            continue

        human_count = human_raw.get(word, 0)
        human_nf = human_norm.get(word, 0)

        if human_count < min_human_count:
            # 人間コーパスにほぼ存在しない → AI固有語
            ai_only_words.append({
                "word": word,
                "ai_freq_norm": round(ai_nf, 8),
                "ai_count": ai_count,
                "human_count": human_count,
            })
            continue

        excess = (ai_nf - human_nf) / human_nf
        results.append({
            "word": word,
            "excess_score": round(excess, 4),
            "ai_freq_norm": round(ai_nf, 8),
            "human_freq_norm": round(human_nf, 8),
            "ai_count": ai_count,
            "human_count": human_count,
            "ratio": round(ai_nf / human_nf, 4) if human_nf > 0 else float("inf"),
        })

    results.sort(key=lambda x: x["excess_score"], reverse=True)
    ai_only_words.sort(key=lambda x: x["ai_count"], reverse=True)

    return results, ai_only_words


def compute_model_comparison(sub_freq_path: Path, human_freq: dict) -> dict:
    """モデル間比較: 各モデルのexcess上位語を算出"""
    sub_freq = load_json(sub_freq_path)
    human_norm = normalize_freq(human_freq)

    comparison = {}
    for model_key, freq in sub_freq.items():
        model_norm = normalize_freq(freq)
        scores = {}
        for word, mnf in model_norm.items():
            if freq.get(word, 0) < 3:
                continue
            hnf = human_norm.get(word, 0)
            if hnf > 0:
                scores[word] = round((mnf - hnf) / hnf, 4)

        # 上位50語
        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:50]
        comparison[model_key] = dict(top)

    return comparison


def generate_report(excess_words: list, excess_ngrams: list, ai_only: list,
                    model_comparison: dict, starter_excess: list) -> str:
    """分析レポートを生成"""
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Excess Vocabulary 分析レポート",
        f"",
        f"生成日時: {now}",
        f"",
        f"## 手法",
        f"",
        f"- 人間コーパス（Qiita/Zenn 2020-2022年記事）をベースラインとし、",
        f"  AI生成テキストで過剰に出現する語を excess_score = (AI_freq - human_freq) / human_freq で定量化。",
        f"",
        f"## Excess Words Top 30（AI Slop Words 候補）",
        f"",
        f"| 順位 | 語 | excess_score | AI頻度 | 人間頻度 | AI出現数 |",
        f"|------|-----|-------------|--------|---------|---------|",
    ]
    for i, w in enumerate(excess_words[:30], 1):
        lines.append(
            f"| {i} | {w['word']} | {w['excess_score']:+.4f} | "
            f"{w['ai_freq_norm']:.6f} | {w['human_freq_norm']:.6f} | {w['ai_count']} |"
        )

    lines += [
        f"",
        f"## AI固有語 Top 20（人間コーパスにほぼ出現しない語）",
        f"",
        f"| 語 | AI出現数 | 人間出現数 |",
        f"|----|---------|-----------|",
    ]
    for w in ai_only[:20]:
        lines.append(f"| {w['word']} | {w['ai_count']} | {w['human_count']} |")

    lines += [
        f"",
        f"## Excess N-grams Top 20",
        f"",
        f"| 順位 | N-gram | excess_score |",
        f"|------|--------|-------------|",
    ]
    for i, w in enumerate(excess_ngrams[:20], 1):
        lines.append(f"| {i} | {w['word'].replace('_', ' ')} | {w['excess_score']:+.4f} |")

    lines += [
        f"",
        f"## 文頭パターン Excess Top 15",
        f"",
        f"| 順位 | 文頭語 | excess_score |",
        f"|------|--------|-------------|",
    ]
    for i, w in enumerate(starter_excess[:15], 1):
        lines.append(f"| {i} | {w['word']} | {w['excess_score']:+.4f} |")

    lines += [
        f"",
        f"## モデル間比較",
        f"",
    ]
    for model, top_words in model_comparison.items():
        top5 = list(top_words.items())[:5]
        words_str = ", ".join(f"{w}({s:+.2f})" for w, s in top5)
        lines.append(f"- **{model}**: {words_str}")

    return "\n".join(lines) + "\n"


# ── メイン ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Excess Word Score算出")
    parser.add_argument("--min-ai-count", type=int, default=5)
    parser.add_argument("--min-human-count", type=int, default=2)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("📊 Excess Word Score算出\n")

    # 1. 単語レベル
    print("── 単語 excess score ──")
    ai_word = load_json(RESULTS_DIR / "word_freq_ai.json")
    human_word = load_json(RESULTS_DIR / "word_freq_human.json")

    if not ai_word or not human_word:
        print("❌ word_freq_ai.json / word_freq_human.json が見つかりません")
        print("   先に tokenize_mecab.py を実行してください")
        return

    excess_words, ai_only = compute_excess_scores(
        ai_word, human_word, args.min_ai_count, args.min_human_count
    )
    print(f"  Excess words: {len(excess_words)}語")
    print(f"  AI固有語: {len(ai_only)}語")

    with open(RESULTS_DIR / "excess_words.json", "w", encoding="utf-8") as f:
        json.dump({"excess": excess_words, "ai_only": ai_only}, f, ensure_ascii=False, indent=2)

    # Top 10プレビュー
    print("\n  📋 Top 10 Excess Words:")
    for i, w in enumerate(excess_words[:10], 1):
        print(f"    {i}. {w['word']} (score: {w['excess_score']:+.4f}, "
              f"AI: {w['ai_count']}, Human: {w['human_count']})")

    # 2. N-gramレベル
    print("\n── N-gram excess score ──")
    ai_ngram = load_json(RESULTS_DIR / "ngram_ai.json")
    human_ngram = load_json(RESULTS_DIR / "ngram_human.json")

    excess_ngrams_all = []
    for gram_type in ["bigram", "trigram"]:
        ai_g = ai_ngram.get(gram_type, {})
        human_g = human_ngram.get(gram_type, {})
        scores, _ = compute_excess_scores(ai_g, human_g, min_ai_count=3, min_human_count=2)
        excess_ngrams_all.extend(scores)

    excess_ngrams_all.sort(key=lambda x: x["excess_score"], reverse=True)
    print(f"  Excess N-grams: {len(excess_ngrams_all)}件")

    with open(RESULTS_DIR / "excess_ngrams.json", "w", encoding="utf-8") as f:
        json.dump(excess_ngrams_all, f, ensure_ascii=False, indent=2)

    # 3. 文頭パターン
    print("\n── 文頭パターン excess score ──")
    ai_starters = load_json(RESULTS_DIR / "starters_ai.json")
    human_starters = load_json(RESULTS_DIR / "starters_human.json")
    starter_excess, _ = compute_excess_scores(ai_starters, human_starters, min_ai_count=3, min_human_count=2)
    print(f"  Excess starters: {len(starter_excess)}件")

    # 4. モデル間比較
    print("\n── モデル間比較 ──")
    model_comparison = compute_model_comparison(RESULTS_DIR / "sub_freq_ai.json", human_word)

    with open(RESULTS_DIR / "model_comparison.json", "w", encoding="utf-8") as f:
        json.dump(model_comparison, f, ensure_ascii=False, indent=2)

    for model, words in model_comparison.items():
        top3 = list(words.items())[:3]
        print(f"  {model}: {', '.join(f'{w}({s:+.2f})' for w, s in top3)}")

    # 5. レポート生成
    print("\n── レポート生成 ──")
    report = generate_report(excess_words, excess_ngrams_all, ai_only,
                             model_comparison, starter_excess)
    report_path = RESULTS_DIR / "analysis_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"  📄 {report_path}")

    print("\n✅ 分析完了")


if __name__ == "__main__":
    main()
