#!/usr/bin/env python3
"""
diverse_analysis.py — ジャンル別excess words分析

技術ブログ（既存データ）と3つの追加ジャンル（日記、ビジネス、雑談）で
excess wordsの共通性/差異を検証する。
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
DIVERSE_DIR = BASE_DIR / "data" / "ai_samples_diverse"
AI_DIR = BASE_DIR / "data" / "ai_samples"
HUMAN_NOTE_DIR = BASE_DIR / "data" / "human_corpus_diverse"

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
                    lemma = features[7] if len(features) > 7 and features[7] != "*" else node.surface
                    if lemma not in STOPWORDS and len(lemma) > 1:
                        words.append(lemma)
            node = node.next
        return words


def count_dir(directory: Path, tokenizer: Tokenizer) -> tuple:
    counter = Counter()
    docs = 0
    for f in sorted(directory.rglob("*.md")):
        text = clean_text(f.read_text(encoding="utf-8"))
        words = tokenizer.extract_words(text)
        counter.update(words)
        docs += 1
    return counter, docs


def normalize(counter: Counter) -> dict:
    total = sum(counter.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in counter.items()}


def compute_excess(target_freq: dict, baseline_freq: dict) -> list:
    results = []
    for word, tf in target_freq.items():
        bf = baseline_freq.get(word, 0)
        if bf == 0:
            continue
        excess = (tf - bf) / bf
        results.append({"word": word, "excess_score": round(excess, 4)})
    results.sort(key=lambda x: x["excess_score"], reverse=True)
    return results


def main():
    print("📊 ジャンル多様化分析\n")

    tokenizer = Tokenizer()

    # 人間コーパス（ベースライン）
    human_freq_path = RESULTS_DIR / "word_freq_human.json"
    human_raw = json.loads(human_freq_path.read_text(encoding="utf-8"))
    human_freq = normalize(Counter(human_raw))

    # 既存AI excess words（技術ブログ）
    excess_data = json.loads((RESULTS_DIR / "excess_words.json").read_text(encoding="utf-8"))
    tech_excess_words = set(w["word"] for w in excess_data.get("excess", [])[:100])

    # 技術ブログAIの頻度（既存）
    ai_freq_raw = json.loads((RESULTS_DIR / "word_freq_ai.json").read_text(encoding="utf-8"))
    tech_freq = normalize(Counter(ai_freq_raw))
    tech_excess = compute_excess(tech_freq, human_freq)

    genre_results = {
        "tech_blog": {
            "excess_top50": tech_excess[:50],
            "top_words": set(w["word"] for w in tech_excess[:100] if w["excess_score"] > 0),
        }
    }

    # 追加ジャンルの分析
    genres = ["diary", "business", "casual"]
    genre_labels = {"diary": "日記・エッセイ", "business": "ビジネスメール", "casual": "雑談・カジュアル", "tech_blog": "技術ブログ"}

    for genre in genres:
        genre_dir = DIVERSE_DIR / genre
        if not genre_dir.exists():
            print(f"  ⚠ {genre} ディレクトリなし、スキップ")
            continue

        counter, docs = count_dir(genre_dir, tokenizer)
        freq = normalize(counter)
        excess = compute_excess(freq, human_freq)
        top_words = set(w["word"] for w in excess[:100] if w["excess_score"] > 0)

        genre_results[genre] = {
            "doc_count": docs,
            "token_count": sum(counter.values()),
            "excess_top50": excess[:50],
            "top_words": top_words,
        }
        print(f"  [{genre_labels[genre]}] {docs}文書, {sum(counter.values())}トークン")

    # ジャンル間重複度マトリクス
    all_genres = [g for g in ["tech_blog"] + genres if g in genre_results]
    overlap_matrix = {}
    for g1 in all_genres:
        overlap_matrix[g1] = {}
        w1 = genre_results[g1]["top_words"]
        for g2 in all_genres:
            w2 = genre_results[g2]["top_words"]
            if len(w1) > 0 and len(w2) > 0:
                jaccard = len(w1 & w2) / len(w1 | w2)
            else:
                jaccard = 0
            overlap_matrix[g1][g2] = round(jaccard, 4)

    # note人間コーパスがあれば追加分析
    human_diverse_info = None
    if HUMAN_NOTE_DIR.exists():
        counter, docs = count_dir(HUMAN_NOTE_DIR, tokenizer)
        if docs > 0:
            human_diverse_info = {"doc_count": docs, "token_count": sum(counter.values())}

    # 結果保存
    output = {
        "genres": {
            g: {
                "label": genre_labels.get(g, g),
                "doc_count": genre_results[g].get("doc_count", "N/A"),
                "token_count": genre_results[g].get("token_count", "N/A"),
                "excess_top50": genre_results[g].get("excess_top50", []),
            }
            for g in all_genres
        },
        "overlap_jaccard": overlap_matrix,
        "human_diverse_corpus": human_diverse_info,
        "finding": "ジャンル間のexcess words重複度が高ければドメイン非依存、低ければドメイン依存",
    }

    out_path = RESULTS_DIR / "diverse_analysis.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2, default=list), encoding="utf-8")
    print(f"\n💾 {out_path}")

    # 可視化
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # 1. ジャンル別excess top10比較
    genre_colors = {"tech_blog": "#e74c3c", "diary": "#3498db", "business": "#2ecc71", "casual": "#f39c12"}
    bar_width = 0.2
    all_top_words = []
    for g in all_genres:
        excess_list = genre_results[g].get("excess_top50", [])
        all_top_words.extend(w["word"] for w in excess_list[:10])
    unique_words = list(dict.fromkeys(all_top_words))[:15]

    if unique_words:
        x = np.arange(len(unique_words))
        for i, g in enumerate(all_genres):
            excess_dict = {w["word"]: w["excess_score"] for w in genre_results[g].get("excess_top50", [])}
            scores = [excess_dict.get(w, 0) for w in unique_words]
            axes[0].barh(x + i * bar_width, scores, bar_width,
                        label=genre_labels.get(g, g), color=genre_colors.get(g, "#999"))
        axes[0].set_yticks(x + bar_width * (len(all_genres) - 1) / 2)
        axes[0].set_yticklabels(unique_words)
        axes[0].set_xlabel("Excess Score")
        axes[0].set_title("ジャンル別 Excess Words 比較")
        axes[0].legend(loc="lower right")

    # 2. Jaccard重複度ヒートマップ
    if len(all_genres) > 1:
        matrix = np.array([[overlap_matrix[g1][g2] for g2 in all_genres] for g1 in all_genres])
        im = axes[1].imshow(matrix, cmap="YlOrRd", vmin=0, vmax=1)
        axes[1].set_xticks(range(len(all_genres)))
        axes[1].set_xticklabels([genre_labels.get(g, g) for g in all_genres], rotation=45, ha="right")
        axes[1].set_yticks(range(len(all_genres)))
        axes[1].set_yticklabels([genre_labels.get(g, g) for g in all_genres])
        axes[1].set_title("Excess Words Jaccard類似度")
        for i in range(len(all_genres)):
            for j in range(len(all_genres)):
                axes[1].text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center",
                           color="white" if matrix[i,j] > 0.5 else "black")
        plt.colorbar(im, ax=axes[1])

    plt.tight_layout()
    fig_path = FIG_DIR / "genre_comparison.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {fig_path}")

    # サマリー
    print(f"\n── Jaccard類似度 ──")
    for g1 in all_genres:
        for g2 in all_genres:
            if g1 < g2:
                print(f"  {genre_labels.get(g1,g1)} × {genre_labels.get(g2,g2)}: {overlap_matrix[g1][g2]:.4f}")


if __name__ == "__main__":
    main()
