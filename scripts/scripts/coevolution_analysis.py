#!/usr/bin/env python3
"""
coevolution_analysis.py — 共進化分析

人間の記事がAI登場後にAIっぽくなったかを検証。
Before (2020-2022, pre-LLM) vs After (2024-2026, post-LLM) の人間記事を比較し、
AIのexcess wordsが人間にも浸透しているかを分析する。
"""

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"


def load_json(name: str) -> dict:
    path = RESULTS_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    # ── データ読み込み ──
    word_freq_human_pre = load_json("word_freq_human.json")      # 2020-2022
    word_freq_human_post = load_json("word_freq_human_post.json") # 2024-2026
    word_freq_ai = load_json("word_freq_ai.json")
    excess_data = load_json("excess_words.json")

    # 総語数
    total_pre = sum(word_freq_human_pre.values())
    total_post = sum(word_freq_human_post.values())
    total_ai = sum(word_freq_ai.values())

    print(f"Pre-LLM人間コーパス: {total_pre:,}語 ({len(word_freq_human_pre):,}ユニーク)")
    print(f"Post-LLM人間コーパス: {total_post:,}語 ({len(word_freq_human_post):,}ユニーク)")
    print(f"AI生成コーパス: {total_ai:,}語")

    # ── Excess words上位50語を取得 ──
    excess_words = excess_data.get("excess", [])[:50]
    excess_word_list = [w["word"] for w in excess_words]

    print(f"\n分析対象: AIのexcess words上位{len(excess_word_list)}語")

    # ── Before→After頻度変化率を算出 ──
    results = []
    for ew in excess_words:
        word = ew["word"]
        pre_count = word_freq_human_pre.get(word, 0)
        post_count = word_freq_human_post.get(word, 0)
        ai_count = ew.get("ai_count", word_freq_ai.get(word, 0))

        pre_freq = pre_count / total_pre if total_pre > 0 else 0
        post_freq = post_count / total_post if total_post > 0 else 0
        ai_freq = ai_count / total_ai if total_ai > 0 else 0

        # 変化率 (post - pre) / pre; preが0なら∞扱い
        if pre_count > 0:
            change_rate = (post_freq - pre_freq) / pre_freq
        elif post_count > 0:
            change_rate = float('inf')
        else:
            change_rate = 0.0

        # χ²検定: Before vs Afterで出現頻度が変わったか
        # 2x2: [pre_count, total_pre - pre_count], [post_count, total_post - post_count]
        chi2_val = 0.0
        p_val = 1.0
        if pre_count + post_count >= 5:
            table = np.array([
                [pre_count, total_pre - pre_count],
                [post_count, total_post - post_count],
            ])
            try:
                chi2_val, p_val, _, _ = stats.chi2_contingency(table)
            except ValueError:
                pass

        results.append({
            "word": word,
            "ai_excess_score": ew.get("excess_score", 0),
            "pre_count": pre_count,
            "post_count": post_count,
            "pre_freq_per_10k": round(pre_freq * 10000, 4),
            "post_freq_per_10k": round(post_freq * 10000, 4),
            "ai_freq_per_10k": round(ai_freq * 10000, 4),
            "change_rate": round(change_rate, 4) if change_rate != float('inf') else "inf",
            "direction": "↑増加" if post_freq > pre_freq else ("↓減少" if post_freq < pre_freq else "→変化なし"),
            "chi2": round(chi2_val, 4),
            "p_value": p_val,
            "significant": bool(p_val < 0.05),
        })

    # ── ソート: 変化率で降順（増加した語が上） ──
    results_sorted = sorted(results, key=lambda x: x["change_rate"] if x["change_rate"] != "inf" else 9999, reverse=True)

    # ── 浸透度の定量指標 ──
    increased = [r for r in results if r["direction"] == "↑増加"]
    decreased = [r for r in results if r["direction"] == "↓減少"]
    significant_increase = [r for r in increased if r["significant"]]

    # 平均変化率（inf除外）
    finite_changes = [r["change_rate"] for r in results if r["change_rate"] != "inf" and isinstance(r["change_rate"], (int, float))]
    avg_change = np.mean(finite_changes) if finite_changes else 0

    # AI浸透スコア: excess wordsのうちpost-LLMで有意に増加した割合
    penetration_score = len(significant_increase) / len(results) * 100 if results else 0

    print(f"\n{'='*60}")
    print(f"📊 共進化分析結果")
    print(f"{'='*60}")
    print(f"  分析語数: {len(results)}")
    print(f"  増加した語: {len(increased)} ({len(increased)/len(results)*100:.1f}%)")
    print(f"  減少した語: {len(decreased)} ({len(decreased)/len(results)*100:.1f}%)")
    print(f"  有意に増加: {len(significant_increase)} ({penetration_score:.1f}%)")
    print(f"  平均変化率: {avg_change:+.2%}")

    print(f"\n🏆 人間にも浸透したAI語 Top 10:")
    for i, r in enumerate(results_sorted[:10], 1):
        cr = f"{r['change_rate']:+.1%}" if isinstance(r['change_rate'], float) else r['change_rate']
        sig = "***" if r['significant'] else ""
        print(f"  {i:2d}. {r['word']:<20s}  "
              f"Pre: {r['pre_freq_per_10k']:6.2f}/万  "
              f"Post: {r['post_freq_per_10k']:6.2f}/万  "
              f"変化: {cr} {sig}")

    # ── 結果をJSONで保存 ──
    output = {
        "summary": {
            "total_pre_tokens": total_pre,
            "total_post_tokens": total_post,
            "total_ai_tokens": total_ai,
            "excess_words_analyzed": len(results),
            "increased_count": len(increased),
            "decreased_count": len(decreased),
            "significant_increase_count": len(significant_increase),
            "avg_change_rate": round(avg_change, 4),
            "penetration_score_pct": round(penetration_score, 2),
        },
        "top_penetrated": results_sorted[:20],
        "all_results": results_sorted,
    }

    # numpy型をPython標準型に変換
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    out_path = RESULTS_DIR / "coevolution_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
    print(f"\n💾 結果保存: {out_path}")

    # ── 可視化 ──
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm

        # 日本語フォント設定
        jp_fonts = [f.name for f in fm.fontManager.ttflist if 'Noto Sans CJK' in f.name or 'IPAGothic' in f.name or 'Takao' in f.name]
        if jp_fonts:
            plt.rcParams['font.family'] = jp_fonts[0]
        else:
            plt.rcParams['font.family'] = 'DejaVu Sans'

        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

        # ── Figure 1: Before/After比較 (Top 20) ──
        fig, ax = plt.subplots(figsize=(14, 10))
        top20 = results_sorted[:20]
        words = [r["word"] for r in top20]
        pre_vals = [r["pre_freq_per_10k"] for r in top20]
        post_vals = [r["post_freq_per_10k"] for r in top20]

        y_pos = np.arange(len(words))
        bar_height = 0.35

        bars1 = ax.barh(y_pos + bar_height/2, pre_vals, bar_height, label="Pre-LLM (2020-2022)", color="#4C72B0", alpha=0.8)
        bars2 = ax.barh(y_pos - bar_height/2, post_vals, bar_height, label="Post-LLM (2024-2026)", color="#DD8452", alpha=0.8)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(words, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel("Frequency per 10,000 tokens", fontsize=12)
        ax.set_title("Coevolution: AI Excess Words in Human Writing\n(Before vs After LLM Era)", fontsize=14)
        ax.legend(fontsize=11)

        # 有意差マーク
        for i, r in enumerate(top20):
            if r["significant"]:
                max_val = max(r["pre_freq_per_10k"], r["post_freq_per_10k"])
                ax.text(max_val + 0.05, i, "★", fontsize=12, va="center", color="red")

        plt.tight_layout()
        fig_path = FIGURES_DIR / "coevolution.png"
        fig.savefig(fig_path, dpi=150, bbox_inches="tight")
        print(f"📈 可視化: {fig_path}")
        plt.close()

        # ── Figure 2: 変化率の分布 ──
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        finite_rates = [(r["word"], r["change_rate"]) for r in results_sorted
                        if isinstance(r["change_rate"], (int, float)) and abs(r["change_rate"]) < 50]

        if finite_rates:
            words_f, rates_f = zip(*finite_rates)
            colors = ["#DD8452" if r > 0 else "#4C72B0" for r in rates_f]
            ax2.barh(range(len(rates_f)), [r * 100 for r in rates_f], color=colors, alpha=0.8)
            ax2.set_yticks(range(len(words_f)))
            ax2.set_yticklabels(words_f, fontsize=8)
            ax2.invert_yaxis()
            ax2.set_xlabel("Change Rate (%)", fontsize=12)
            ax2.set_title("Frequency Change Rate: Pre-LLM → Post-LLM\n(AI Excess Words in Human Writing)", fontsize=13)
            ax2.axvline(x=0, color="black", linewidth=0.8)
            plt.tight_layout()
            fig2_path = FIGURES_DIR / "coevolution_change_rate.png"
            fig2.savefig(fig2_path, dpi=150, bbox_inches="tight")
            print(f"📈 可視化: {fig2_path}")
            plt.close()

    except ImportError as e:
        print(f"⚠ matplotlib未インストール: {e}")

    print("\n✅ 共進化分析完了")


if __name__ == "__main__":
    main()
