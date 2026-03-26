#!/usr/bin/env python3
"""
control_analysis.py — 初心者 vs 上級者 vs AI のexcess score比較分析

「AIっぽい語 = 初心者っぽい語」なのかを検証する。
"""

import json
import re
from collections import Counter
from pathlib import Path

import MeCab
import unidic_lite
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import japanize_matplotlib  # noqa: F401
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
FIG_DIR = RESULTS_DIR / "figures"
CONTROL_DIR = BASE_DIR / "data" / "control_corpus"
BEGINNER_DIR = CONTROL_DIR / "beginner"
EXPERT_DIR = CONTROL_DIR / "expert"

# tokenize_mecab.py と同じ設定
TARGET_POS = {"名詞", "動詞", "形容詞", "副詞", "接続詞"}
EXCLUDE_NOUN_SUB = {"数詞", "非自立可能", "代名詞", "助数詞"}
STOPWORDS = {
    "する", "為る", "いる", "居る", "ある", "有る", "なる", "成る",
    "できる", "出来る", "れる", "られる",
    "こと", "事", "もの", "物", "ため", "為", "よう", "様",
    "それ", "これ", "ここ", "其れ", "此れ", "此処",
    "の", "に", "は", "を", "が", "と", "で", "も", "か",
    "や", "へ", "から", "まで", "より", "etc", "##",
}
MD_NOISE = re.compile(r'```[\s\S]*?```|`[^`]+`|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|#{1,6}\s|[*_~`>|]|\|.*\|')
URL_PATTERN = re.compile(r'https?://\S+')


def clean_text(text: str) -> str:
    text = MD_NOISE.sub(" ", text)
    text = URL_PATTERN.sub(" ", text)
    return re.sub(r'\s+', ' ', text).strip()


class Tokenizer:
    def __init__(self):
        self.tagger = MeCab.Tagger(f"-d {unidic_lite.DICDIR}")

    def extract_words(self, text: str) -> list:
        words = []
        node = self.tagger.parseToNode(text)
        while node:
            features = node.feature.split(",")
            if len(features) >= 4:
                pos = features[0]
                if pos in TARGET_POS:
                    if pos == "名詞" and len(features) >= 2 and features[1] in EXCLUDE_NOUN_SUB:
                        node = node.next
                        continue
                    # lemmaを使用（unidic-liteではfeatures[7]）
                    lemma = features[7] if len(features) > 7 and features[7] != "*" else node.surface
                    if lemma not in STOPWORDS and len(lemma) > 1:
                        words.append(lemma)
            node = node.next
        return words


def count_words(directory: Path, tokenizer: Tokenizer) -> Counter:
    counter = Counter()
    docs = 0
    for f in sorted(directory.glob("*.md")):
        text = clean_text(f.read_text(encoding="utf-8"))
        words = tokenizer.extract_words(text)
        counter.update(words)
        docs += 1
    return counter, docs


def normalize_freq(counter: Counter) -> dict:
    total = sum(counter.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in counter.items()}


def compute_excess(target_freq: dict, baseline_freq: dict, min_count: int = 3) -> list:
    """target vs baselineのexcess score"""
    results = []
    for word, tf in target_freq.items():
        bf = baseline_freq.get(word, 0)
        if bf == 0:
            continue
        excess = (tf - bf) / bf
        results.append({"word": word, "excess_score": round(excess, 4),
                        "target_freq": round(tf, 8), "baseline_freq": round(bf, 8)})
    results.sort(key=lambda x: x["excess_score"], reverse=True)
    return results


def main():
    print("📊 コントロール実験分析\n")
    
    if not BEGINNER_DIR.exists() or not EXPERT_DIR.exists():
        print("❌ control_corpus が見つかりません。先に collect_control_corpus.py を実行してください。")
        return

    tokenizer = Tokenizer()

    # 人間コーパス（ベースライン）の頻度を読み込み
    human_freq_path = RESULTS_DIR / "word_freq_human.json"
    if not human_freq_path.exists():
        print("❌ word_freq_human.json が見つかりません")
        return
    human_raw = json.loads(human_freq_path.read_text(encoding="utf-8"))
    human_freq = normalize_freq(Counter(human_raw))

    # AI excess wordsを読み込み
    excess_data = json.loads((RESULTS_DIR / "excess_words.json").read_text(encoding="utf-8"))
    ai_excess_words = {w["word"] for w in excess_data.get("excess", [])[:200]}

    # 初心者・上級者の頻度計算
    print("── 初心者テキスト分析 ──")
    beginner_counter, beg_docs = count_words(BEGINNER_DIR, tokenizer)
    beginner_freq = normalize_freq(beginner_counter)
    print(f"  {beg_docs}文書, {sum(beginner_counter.values())}トークン, {len(beginner_counter)}ユニーク語")

    print("── 上級者テキスト分析 ──")
    expert_counter, exp_docs = count_words(EXPERT_DIR, tokenizer)
    expert_freq = normalize_freq(expert_counter)
    print(f"  {exp_docs}文書, {sum(expert_counter.values())}トークン, {len(expert_counter)}ユニーク語")

    # excess score計算（vs 全人間コーパス基準）
    beginner_excess = compute_excess(beginner_freq, human_freq)
    expert_excess = compute_excess(expert_freq, human_freq)

    # AI excess wordsとの重複度
    beginner_excess_words = {w["word"] for w in beginner_excess[:200] if w["excess_score"] > 0}
    expert_excess_words = {w["word"] for w in expert_excess[:200] if w["excess_score"] > 0}

    overlap_beginner_ai = ai_excess_words & beginner_excess_words
    overlap_expert_ai = ai_excess_words & expert_excess_words
    overlap_beginner_expert = beginner_excess_words & expert_excess_words

    results = {
        "beginner": {
            "doc_count": beg_docs,
            "token_count": sum(beginner_counter.values()),
            "top_excess_words": beginner_excess[:50],
        },
        "expert": {
            "doc_count": exp_docs,
            "token_count": sum(expert_counter.values()),
            "top_excess_words": expert_excess[:50],
        },
        "overlap": {
            "ai_beginner": {
                "count": len(overlap_beginner_ai),
                "ratio_of_ai": round(len(overlap_beginner_ai) / max(len(ai_excess_words), 1), 4),
                "words": sorted(overlap_beginner_ai)[:30],
            },
            "ai_expert": {
                "count": len(overlap_expert_ai),
                "ratio_of_ai": round(len(overlap_expert_ai) / max(len(ai_excess_words), 1), 4),
                "words": sorted(overlap_expert_ai)[:30],
            },
            "beginner_expert": {
                "count": len(overlap_beginner_expert),
                "words": sorted(overlap_beginner_expert)[:30],
            },
        },
        "conclusion": {
            "ai_beginner_overlap_pct": round(len(overlap_beginner_ai) / max(len(ai_excess_words), 1) * 100, 1),
            "ai_expert_overlap_pct": round(len(overlap_expert_ai) / max(len(ai_excess_words), 1) * 100, 1),
        }
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "control_analysis.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 {out_path}")

    # 可視化
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1. 初心者 excess top20
    beg_top = beginner_excess[:20]
    if beg_top:
        words = [w["word"] for w in beg_top][::-1]
        scores = [w["excess_score"] for w in beg_top][::-1]
        colors = ["#e74c3c" if w in ai_excess_words else "#3498db" for w in words]
        axes[0].barh(range(len(words)), scores, color=colors)
        axes[0].set_yticks(range(len(words)))
        axes[0].set_yticklabels(words)
        axes[0].set_title("初心者 Excess Words Top 20\n(赤=AI excess wordsと重複)")
        axes[0].set_xlabel("Excess Score")

    # 2. 上級者 excess top20
    exp_top = expert_excess[:20]
    if exp_top:
        words = [w["word"] for w in exp_top][::-1]
        scores = [w["excess_score"] for w in exp_top][::-1]
        colors = ["#e74c3c" if w in ai_excess_words else "#2ecc71" for w in words]
        axes[1].barh(range(len(words)), scores, color=colors)
        axes[1].set_yticks(range(len(words)))
        axes[1].set_yticklabels(words)
        axes[1].set_title("上級者 Excess Words Top 20\n(赤=AI excess wordsと重複)")
        axes[1].set_xlabel("Excess Score")

    # 3. 重複度比較
    categories = ["AI∩初心者", "AI∩上級者", "初心者∩上級者"]
    counts = [len(overlap_beginner_ai), len(overlap_expert_ai), len(overlap_beginner_expert)]
    colors = ["#e74c3c", "#2ecc71", "#9b59b6"]
    axes[2].bar(categories, counts, color=colors)
    axes[2].set_title("Excess Words 重複度")
    axes[2].set_ylabel("重複語数")
    for i, v in enumerate(counts):
        axes[2].text(i, v + 0.5, str(v), ha="center", fontweight="bold")

    plt.tight_layout()
    fig_path = FIG_DIR / "control_comparison.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {fig_path}")

    # サマリー出力
    print(f"\n── 結果サマリー ──")
    print(f"AI excess words (Top200): {len(ai_excess_words)}語")
    print(f"初心者 excess words (Top200, score>0): {len(beginner_excess_words)}語")
    print(f"上級者 excess words (Top200, score>0): {len(expert_excess_words)}語")
    print(f"AI∩初心者 重複: {len(overlap_beginner_ai)}語 ({results['conclusion']['ai_beginner_overlap_pct']}%)")
    print(f"AI∩上級者 重複: {len(overlap_expert_ai)}語 ({results['conclusion']['ai_expert_overlap_pct']}%)")


if __name__ == "__main__":
    main()
