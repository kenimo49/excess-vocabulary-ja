#!/usr/bin/env python3
"""
model_evolution.py — Claude世代間変化の深掘り分析

Claude 3 Haiku → Claude Sonnet 4 → Claude Opus 4 の3世代で:
- 各世代のexcess words Top 20比較
- slop語彙の変化（増減）
- 共通 vs 世代固有のslop語彙
- 語彙多様性指標（TTR等）
"""

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import japanize_matplotlib  # noqa: F401
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
AI_DIR = BASE_DIR / "data" / "ai_samples"
FIG_DIR = RESULTS_DIR / "figures"


def load_json(path: Path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


# Claude世代定義
CLAUDE_MODELS = {
    "claude-3-haiku": "Claude 3 Haiku (2024)",
    "claude-sonnet-4": "Claude Sonnet 4 (2025)",
    "claude-opus-4": "Claude Opus 4 (2025)",
}


def compute_model_excess(sub_freq: dict, human_freq: dict, model_key: str, min_count: int = 3) -> list:
    """特定モデルのexcess wordsを算出"""
    model_freq = sub_freq.get(model_key, {})
    if not model_freq:
        return []
    
    model_total = sum(model_freq.values())
    human_total = sum(human_freq.values())
    
    if model_total == 0 or human_total == 0:
        return []
    
    model_norm = {k: v / model_total for k, v in model_freq.items()}
    human_norm = {k: v / human_total for k, v in human_freq.items()}
    
    results = []
    for word, mnf in model_norm.items():
        if model_freq.get(word, 0) < min_count:
            continue
        hnf = human_norm.get(word, 0)
        if hnf > 0:
            excess = (mnf - hnf) / hnf
            results.append({
                "word": word,
                "excess_score": round(excess, 4),
                "model_freq": round(mnf, 8),
                "human_freq": round(hnf, 8),
                "model_count": model_freq[word],
            })
    
    results.sort(key=lambda x: x["excess_score"], reverse=True)
    return results


def compute_ttr(model_dir: Path) -> dict:
    """Type-Token Ratio等の語彙多様性指標を算出"""
    from scripts_common import get_tokenizer
    # Simple approach: count all words in model's files
    import re
    
    all_tokens = []
    files = list(model_dir.glob("*.md"))
    
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        # Simple tokenization: split by whitespace and punctuation
        tokens = re.findall(r'[\w]+', text)
        all_tokens.extend(tokens)
    
    if not all_tokens:
        return {"ttr": 0, "types": 0, "tokens": 0}
    
    types = len(set(all_tokens))
    tokens = len(all_tokens)
    ttr = types / tokens if tokens > 0 else 0
    
    # Hapax legomena (words appearing only once)
    freq = Counter(all_tokens)
    hapax = sum(1 for c in freq.values() if c == 1)
    
    return {
        "ttr": round(ttr, 4),
        "types": types,
        "tokens": tokens,
        "hapax": hapax,
        "hapax_ratio": round(hapax / types, 4) if types > 0 else 0,
    }


def compute_ttr_simple(model_dir: Path) -> dict:
    """Simple TTR calculation without MeCab dependency"""
    import re
    
    all_tokens = []
    files = list(model_dir.glob("*.md"))
    
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        # Split by various delimiters
        tokens = re.findall(r'[ぁ-んァ-ヶ一-龥a-zA-Zａ-ｚＡ-Ｚ]+', text)
        all_tokens.extend(tokens)
    
    if not all_tokens:
        return {"ttr": 0, "types": 0, "tokens": 0, "hapax": 0, "hapax_ratio": 0}
    
    types = len(set(all_tokens))
    tokens_count = len(all_tokens)
    ttr = types / tokens_count if tokens_count > 0 else 0
    
    freq = Counter(all_tokens)
    hapax = sum(1 for c in freq.values() if c == 1)
    
    return {
        "ttr": round(ttr, 4),
        "types": types,
        "tokens": tokens_count,
        "hapax": hapax,
        "hapax_ratio": round(hapax / types, 4) if types > 0 else 0,
    }


def plot_evolution(model_top_words: dict, model_ttr: dict):
    """世代間変化の可視化"""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    models = list(CLAUDE_MODELS.keys())
    model_labels = list(CLAUDE_MODELS.values())
    colors = ["#e74c3c", "#e67e22", "#2ecc71"]
    
    # 1. 各世代Top 15 excess words (grouped bar)
    ax = axes[0, 0]
    # Get all unique top words across models
    all_top = set()
    for m in models:
        words = model_top_words.get(m, [])
        for w in words[:15]:
            all_top.add(w["word"])
    all_top = sorted(all_top)[:20]
    
    x = np.arange(len(all_top))
    width = 0.25
    
    for i, m in enumerate(models):
        word_scores = {w["word"]: w["excess_score"] for w in model_top_words.get(m, [])}
        scores = [word_scores.get(w, 0) for w in all_top]
        ax.barh(x + i * width, scores, width, label=model_labels[i], color=colors[i], alpha=0.8)
    
    ax.set_yticks(x + width)
    ax.set_yticklabels(all_top, fontsize=8)
    ax.set_xlabel("Excess Score")
    ax.set_title("Claude世代別 Excess Words比較", fontweight="bold")
    ax.legend(fontsize=8)
    ax.invert_yaxis()
    
    # 2. Excess score分布 (violin/box plot)
    ax = axes[0, 1]
    data_for_box = []
    labels_for_box = []
    for i, m in enumerate(models):
        scores = [w["excess_score"] for w in model_top_words.get(m, []) if w["excess_score"] > 0]
        if scores:
            data_for_box.append(scores[:50])  # Top 50
            labels_for_box.append(model_labels[i].split(" (")[0])
    
    if data_for_box:
        bp = ax.boxplot(data_for_box, labels=labels_for_box, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors[:len(data_for_box)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.5)
    ax.set_ylabel("Excess Score")
    ax.set_title("Excess Score分布（世代別）", fontweight="bold")
    
    # 3. TTR comparison
    ax = axes[1, 0]
    ttr_vals = [model_ttr.get(m, {}).get("ttr", 0) for m in models]
    bars = ax.bar(model_labels, ttr_vals, color=colors, alpha=0.8, edgecolor="white")
    for bar, val in zip(bars, ttr_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f"{val:.4f}", ha="center", fontsize=10)
    ax.set_ylabel("Type-Token Ratio")
    ax.set_title("語彙多様性（TTR）", fontweight="bold")
    ax.tick_params(axis='x', rotation=15)
    
    # 4. Venn-like overlap visualization (text-based)
    ax = axes[1, 1]
    ax.axis("off")
    
    # Compute overlaps
    top20_sets = {}
    for m in models:
        words = model_top_words.get(m, [])
        top20_sets[m] = set(w["word"] for w in words[:20])
    
    common_all = top20_sets.get(models[0], set())
    for m in models[1:]:
        common_all &= top20_sets.get(m, set())
    
    text_lines = ["【Claude世代間 Excess Words 重複分析】", ""]
    text_lines.append(f"Top 20 共通語彙（全3世代）: {len(common_all)}語")
    if common_all:
        text_lines.append(f"  → {', '.join(sorted(common_all)[:10])}")
    text_lines.append("")
    
    for i, m in enumerate(models):
        unique = top20_sets.get(m, set()) - set().union(*[top20_sets.get(m2, set()) for m2 in models if m2 != m])
        text_lines.append(f"{model_labels[i]} 固有: {len(unique)}語")
        if unique:
            text_lines.append(f"  → {', '.join(sorted(unique)[:8])}")
    
    # Pairwise overlaps
    text_lines.append("")
    for i in range(len(models)):
        for j in range(i+1, len(models)):
            overlap = top20_sets.get(models[i], set()) & top20_sets.get(models[j], set())
            short_i = model_labels[i].split(" ")[1]
            short_j = model_labels[j].split(" ")[1]
            text_lines.append(f"{short_i}∩{short_j}: {len(overlap)}語")
    
    ax.text(0.05, 0.95, "\n".join(text_lines), transform=ax.transAxes,
            fontsize=10, verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    
    plt.suptitle("Claude世代間変化分析", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = FIG_DIR / "model_evolution.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {out_path}")


def main():
    print("🔄 Claude世代間変化分析\n")
    
    sub_freq = load_json(RESULTS_DIR / "sub_freq_ai.json")
    human_freq = load_json(RESULTS_DIR / "word_freq_human.json")
    
    if not sub_freq or not human_freq:
        print("❌ 必要なデータが見つかりません")
        return
    
    # 各Claude世代のexcess words算出
    model_top_words = {}
    for model_key, display_name in CLAUDE_MODELS.items():
        excess = compute_model_excess(sub_freq, human_freq, model_key)
        model_top_words[model_key] = excess
        print(f"  {display_name}: {len(excess)} excess words")
        if excess:
            top3 = excess[:3]
            for w in top3:
                print(f"    - {w['word']} ({w['excess_score']:+.4f})")
    
    # TTR算出
    print("\n── 語彙多様性 ──")
    model_ttr = {}
    for model_key, display_name in CLAUDE_MODELS.items():
        model_dir = AI_DIR / model_key
        if model_dir.exists():
            ttr = compute_ttr_simple(model_dir)
            model_ttr[model_key] = ttr
            print(f"  {display_name}: TTR={ttr['ttr']:.4f} "
                  f"(types={ttr['types']}, tokens={ttr['tokens']}, hapax={ttr['hapax']})")
    
    # 世代間比較
    print("\n── 世代間比較 ──")
    models = list(CLAUDE_MODELS.keys())
    
    # Top 20の重複分析
    top20_sets = {}
    for m in models:
        words = model_top_words.get(m, [])
        top20_sets[m] = set(w["word"] for w in words[:20])
    
    common_all = top20_sets.get(models[0], set())
    for m in models[1:]:
        common_all &= top20_sets.get(m, set())
    
    print(f"\n  全世代共通 Top 20: {len(common_all)}語")
    if common_all:
        print(f"    {', '.join(sorted(common_all))}")
    
    for m, display in CLAUDE_MODELS.items():
        unique = top20_sets.get(m, set()) - set().union(*[top20_sets.get(m2, set()) for m2 in models if m2 != m])
        print(f"  {display} 固有: {len(unique)}語 → {', '.join(sorted(unique)[:5])}")
    
    # Slop語彙は減ったか？
    print("\n── Slop語彙の変化 ──")
    for m, display in CLAUDE_MODELS.items():
        excess = model_top_words.get(m, [])
        if excess:
            avg_score = np.mean([w["excess_score"] for w in excess[:20]])
            max_score = excess[0]["excess_score"]
            print(f"  {display}: 平均excess(Top20)={avg_score:.4f}, 最大={max_score:.4f}")
    
    # 可視化
    print("\n── 可視化 ──")
    plot_evolution(model_top_words, model_ttr)
    
    # 結果保存
    output = {
        "claude_models": CLAUDE_MODELS,
        "model_excess_top20": {
            m: [w for w in words[:20]]
            for m, words in model_top_words.items()
        },
        "model_ttr": model_ttr,
        "common_all_top20": sorted(common_all),
        "model_unique_top20": {
            m: sorted(top20_sets.get(m, set()) - set().union(*[top20_sets.get(m2, set()) for m2 in models if m2 != m]))
            for m in models
        },
    }
    
    with open(RESULTS_DIR / "model_evolution.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 {RESULTS_DIR / 'model_evolution.json'}")
    
    print("\n✅ Claude世代間変化分析完了")


if __name__ == "__main__":
    main()
