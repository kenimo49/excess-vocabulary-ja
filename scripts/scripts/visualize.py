#!/usr/bin/env python3
"""
visualize.py — Excess Vocabulary 結果を可視化

出力:
  - results/figures/excess_words_top30.png    ← 横棒グラフ
  - results/figures/model_heatmap.png         ← モデル別ヒートマップ
  - results/figures/excess_ngrams_top20.png   ← N-gram excess
  - results/figures/sentence_starters.png     ← 文頭パターン比較
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import japanize_matplotlib  # noqa: F401
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
FIG_DIR = RESULTS_DIR / "figures"


def load_json(path: Path) -> dict | list:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def plot_excess_words_top30():
    """Excess Words Top 30 横棒グラフ"""
    data = load_json(RESULTS_DIR / "excess_words.json")
    if not data:
        print("⚠ excess_words.json not found")
        return

    words_data = data.get("excess", [])[:30]
    if not words_data:
        print("⚠ No excess words data")
        return

    words = [w["word"] for w in reversed(words_data)]
    scores = [w["excess_score"] for w in reversed(words_data)]

    fig, ax = plt.subplots(figsize=(10, 10))
    colors = ["#e74c3c" if s > 0 else "#3498db" for s in scores]
    ax.barh(words, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Excess Score", fontsize=12)
    ax.set_title("日本語 AI Slop Words — Excess Score Top 30", fontsize=14, fontweight="bold")
    ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.5)

    for i, (w, s) in enumerate(zip(words, scores)):
        ax.text(s + 0.01 if s > 0 else s - 0.01, i, f"{s:.2f}",
                va="center", ha="left" if s > 0 else "right", fontsize=8)

    plt.tight_layout()
    out_path = FIG_DIR / "excess_words_top30.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out_path}")


def plot_model_heatmap():
    """モデル別 Excess Words ヒートマップ"""
    comparison = load_json(RESULTS_DIR / "model_comparison.json")
    if not comparison:
        print("⚠ model_comparison.json not found")
        return

    # 全モデルのTop 15語を集める
    all_words = set()
    for model, words in comparison.items():
        top = list(words.keys())[:15]
        all_words.update(top)

    all_words = sorted(all_words)[:30]  # 最大30語
    models = list(comparison.keys())

    # マトリクス構築
    matrix = np.zeros((len(all_words), len(models)))
    for j, model in enumerate(models):
        for i, word in enumerate(all_words):
            matrix[i, j] = comparison[model].get(word, 0)

    fig, ax = plt.subplots(figsize=(max(8, len(models) * 2), max(8, len(all_words) * 0.4)))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(all_words)))
    ax.set_yticklabels(all_words, fontsize=9)

    # 値を表示
    for i in range(len(all_words)):
        for j in range(len(models)):
            val = matrix[i, j]
            if val != 0:
                color = "white" if val > matrix.max() * 0.6 else "black"
                ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                        fontsize=7, color=color)

    ax.set_title("モデル別 Excess Words ヒートマップ", fontsize=14, fontweight="bold")
    plt.colorbar(im, ax=ax, label="Excess Score")
    plt.tight_layout()
    out_path = FIG_DIR / "model_heatmap.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out_path}")


def plot_excess_ngrams_top20():
    """N-gram Excess Top 20"""
    ngrams = load_json(RESULTS_DIR / "excess_ngrams.json")
    if not ngrams:
        print("⚠ excess_ngrams.json not found")
        return

    top20 = ngrams[:20]
    labels = [w["word"].replace("_", " ") for w in reversed(top20)]
    scores = [w["excess_score"] for w in reversed(top20)]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(labels, scores, color="#e67e22", edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Excess Score", fontsize=12)
    ax.set_title("Excess N-grams Top 20", fontsize=14, fontweight="bold")
    ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.5)

    plt.tight_layout()
    out_path = FIG_DIR / "excess_ngrams_top20.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out_path}")


def plot_sentence_starters():
    """文頭パターン比較（AI vs 人間）"""
    ai_starters = load_json(RESULTS_DIR / "starters_ai.json")
    human_starters = load_json(RESULTS_DIR / "starters_human.json")

    if not ai_starters or not human_starters:
        print("⚠ starters data not found")
        return

    # 上位15語の比較
    top_words = list(ai_starters.keys())[:15]

    ai_total = sum(ai_starters.values())
    human_total = sum(human_starters.values())

    ai_ratios = [ai_starters.get(w, 0) / ai_total * 100 for w in top_words]
    human_ratios = [human_starters.get(w, 0) / human_total * 100 for w in top_words]

    x = np.arange(len(top_words))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, ai_ratios, width, label="AI", color="#e74c3c", alpha=0.8)
    bars2 = ax.bar(x + width/2, human_ratios, width, label="人間", color="#3498db", alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(top_words, fontsize=10)
    ax.set_ylabel("出現率 (%)", fontsize=12)
    ax.set_title("文頭パターン比較 (AI vs 人間)", fontsize=14, fontweight="bold")
    ax.legend()

    plt.tight_layout()
    out_path = FIG_DIR / "sentence_starters.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out_path}")


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    print("📊 可視化開始\n")

    plot_excess_words_top30()
    plot_model_heatmap()
    plot_excess_ngrams_top20()
    plot_sentence_starters()

    print(f"\n✅ 可視化完了 → {FIG_DIR}/")


if __name__ == "__main__":
    main()
