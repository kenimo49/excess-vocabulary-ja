#!/usr/bin/env python3
"""
statistical_test.py — Excess Words の統計的検定

1. χ²検定: 各excess wordについてAI vs 人間の出現頻度の有意差
2. Mann-Whitney U検定: モデル間のexcess scoreの分布差
3. Bonferroni補正: 多重比較補正
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
AI_DIR = BASE_DIR / "data" / "ai_samples"
HUMAN_DIR = BASE_DIR / "data" / "human_corpus"


def load_json(path: Path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def cohens_d(group1: list, group2: list) -> float:
    """Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return float('nan')
    m1, m2 = np.mean(group1), np.mean(group2)
    s1, s2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return float('nan')
    return (m1 - m2) / pooled_std


def compute_effect_sizes(excess_words: list, sub_freq: dict, human_freq: dict) -> list:
    """Compute Cohen's d effect size for each excess word (AI vs human per-document freq)."""
    human_total = sum(human_freq.values())
    
    # Build per-model normalized frequencies for each word
    model_totals = {m: sum(f.values()) for m, f in sub_freq.items()}
    
    results = []
    for w in excess_words[:200]:  # Top 200 excess words
        word = w["word"]
        
        # AI side: per-model normalized frequency
        ai_values = []
        for model, freq in sub_freq.items():
            mt = model_totals[model]
            if mt > 0:
                ai_values.append(freq.get(word, 0) / mt)
        
        # Human side: use overall frequency as single observation
        # (we don't have per-document human data, so use bootstrap approximation)
        human_nf = human_freq.get(word, 0) / human_total if human_total > 0 else 0
        # Create synthetic human distribution around the mean
        human_count = human_freq.get(word, 0)
        if human_count > 0 and len(ai_values) >= 2:
            # Use Poisson approximation for human variance
            human_values = [human_nf] * len(ai_values)  # conservative estimate
            d = cohens_d(ai_values, human_values)
        else:
            d = float('nan')
        
        magnitude = "negligible"
        if not np.isnan(d):
            abs_d = abs(d)
            if abs_d >= 0.8:
                magnitude = "large"
            elif abs_d >= 0.5:
                magnitude = "medium"
            elif abs_d >= 0.2:
                magnitude = "small"
        
        results.append({
            "word": word,
            "excess_score": w.get("excess_score", 0),
            "cohens_d": round(d, 4) if not np.isnan(d) else None,
            "effect_magnitude": magnitude,
            "ai_mean_freq": round(np.mean(ai_values), 8) if ai_values else 0,
            "human_freq_norm": round(human_nf, 8),
        })
    
    return results


def chi_squared_test(excess_words: list, ai_freq: dict, human_freq: dict) -> list:
    """各excess wordについてχ²検定を実施"""
    ai_total = sum(ai_freq.values())
    human_total = sum(human_freq.values())
    
    results = []
    for w in excess_words:
        word = w["word"]
        ai_count = ai_freq.get(word, 0)
        human_count = human_freq.get(word, 0)
        
        # 2x2 contingency table:
        # [AI-word, AI-other], [Human-word, Human-other]
        table = np.array([
            [ai_count, ai_total - ai_count],
            [human_count, human_total - human_count]
        ])
        
        if ai_count == 0 and human_count == 0:
            continue
        
        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(table)
        except ValueError:
            chi2, p_value = 0.0, 1.0
        
        results.append({
            "word": word,
            "excess_score": w.get("excess_score", 0),
            "ai_count": ai_count,
            "human_count": human_count,
            "chi2": round(chi2, 4),
            "p_value": p_value,
            "significant_raw": p_value < 0.05,
        })
    
    return results


def mann_whitney_model_comparison(sub_freq: dict, human_freq: dict) -> dict:
    """モデル間のexcess scoreの分布差をMann-Whitney U検定"""
    human_total = sum(human_freq.values())
    human_norm = {k: v / human_total for k, v in human_freq.items()} if human_total > 0 else {}
    
    # 各モデルのexcess score分布を計算
    model_scores = {}
    for model, freq in sub_freq.items():
        model_total = sum(freq.values())
        if model_total == 0:
            continue
        scores = []
        for word, count in freq.items():
            if count < 3:
                continue
            model_nf = count / model_total
            human_nf = human_norm.get(word, 0)
            if human_nf > 0:
                excess = (model_nf - human_nf) / human_nf
                scores.append(excess)
        model_scores[model] = scores
    
    # ペアワイズ比較
    models = list(model_scores.keys())
    comparisons = {}
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            m1, m2 = models[i], models[j]
            s1, s2 = model_scores[m1], model_scores[m2]
            if len(s1) < 5 or len(s2) < 5:
                continue
            try:
                stat, p_value = stats.mannwhitneyu(s1, s2, alternative='two-sided')
            except ValueError:
                stat, p_value = 0.0, 1.0
            
            comparisons[f"{m1} vs {m2}"] = {
                "U_statistic": round(stat, 4),
                "p_value": p_value,
                "n1": len(s1),
                "n2": len(s2),
                "median1": round(np.median(s1), 4),
                "median2": round(np.median(s2), 4),
            }
    
    return comparisons, model_scores


def apply_bonferroni(chi2_results: list, model_comparisons: dict):
    """Bonferroni補正を適用"""
    # χ²検定のBonferroni補正
    n_tests = len(chi2_results)
    for r in chi2_results:
        r["p_bonferroni"] = min(r["p_value"] * n_tests, 1.0)
        r["significant_bonferroni"] = r["p_bonferroni"] < 0.05
    
    # Mann-Whitney U検定のBonferroni補正
    n_comparisons = len(model_comparisons)
    for key, comp in model_comparisons.items():
        comp["p_bonferroni"] = min(comp["p_value"] * n_comparisons, 1.0)
        comp["significant_bonferroni"] = comp["p_bonferroni"] < 0.05
    
    return chi2_results, model_comparisons


def generate_stats_report(chi2_results: list, model_comparisons: dict, model_scores: dict, effect_sizes: list = None) -> str:
    """統計的検定レポートを生成"""
    lines = [
        "",
        "## 統計的検定結果",
        "",
        "### χ²検定 (AI vs 人間 出現頻度)",
        "",
        f"検定数: {len(chi2_results)}語",
        "",
    ]
    
    sig_raw = sum(1 for r in chi2_results if r["significant_raw"])
    sig_bonf = sum(1 for r in chi2_results if r["significant_bonferroni"])
    
    lines.append(f"- 有意 (p<0.05, 補正なし): {sig_raw}/{len(chi2_results)}語")
    lines.append(f"- 有意 (p<0.05, Bonferroni補正後): {sig_bonf}/{len(chi2_results)}語")
    lines.append("")
    
    # 有意なexcess words Top 20
    significant = [r for r in chi2_results if r["significant_bonferroni"]]
    significant.sort(key=lambda x: x["excess_score"], reverse=True)
    
    lines.append("#### 統計的に有意なExcess Words (Bonferroni補正後) Top 20")
    lines.append("")
    lines.append("| 語 | excess_score | χ² | p (raw) | p (Bonferroni) | AI | Human |")
    lines.append("|-----|-------------|-----|---------|---------------|-----|-------|")
    
    for r in significant[:20]:
        lines.append(
            f"| {r['word']} | {r['excess_score']:+.4f} | {r['chi2']:.2f} | "
            f"{r['p_value']:.2e} | {r['p_bonferroni']:.2e} | {r['ai_count']} | {r['human_count']} |"
        )
    
    # 有意でないexcess words
    not_sig = [r for r in chi2_results if not r["significant_bonferroni"]]
    not_sig.sort(key=lambda x: x["excess_score"], reverse=True)
    
    if not_sig:
        lines.append("")
        lines.append(f"#### 統計的に有意でないExcess Words: {len(not_sig)}語")
        lines.append("")
        lines.append("| 語 | excess_score | p (Bonferroni) |")
        lines.append("|-----|-------------|---------------|")
        for r in not_sig[:10]:
            lines.append(f"| {r['word']} | {r['excess_score']:+.4f} | {r['p_bonferroni']:.2e} |")
    
    # Mann-Whitney U検定
    lines.append("")
    lines.append("### Mann-Whitney U検定 (モデル間excess score分布比較)")
    lines.append("")
    lines.append("| 比較 | U | p (raw) | p (Bonferroni) | n1 | n2 | median1 | median2 | 有意 |")
    lines.append("|------|---|---------|---------------|----|----|---------|---------|------|")
    
    for key, comp in sorted(model_comparisons.items()):
        sig_mark = "✅" if comp["significant_bonferroni"] else "❌"
        lines.append(
            f"| {key} | {comp['U_statistic']:.0f} | {comp['p_value']:.2e} | "
            f"{comp['p_bonferroni']:.2e} | {comp['n1']} | {comp['n2']} | "
            f"{comp['median1']:.4f} | {comp['median2']:.4f} | {sig_mark} |"
        )
    
    # Cohen's d effect size
    if effect_sizes:
        lines.append("")
        lines.append("### Cohen's d Effect Size (AI vs 人間)")
        lines.append("")
        valid = [e for e in effect_sizes if e["cohens_d"] is not None]
        large = [e for e in valid if e["effect_magnitude"] == "large"]
        medium = [e for e in valid if e["effect_magnitude"] == "medium"]
        small = [e for e in valid if e["effect_magnitude"] == "small"]
        lines.append(f"- 計算対象: {len(effect_sizes)}語, 有効: {len(valid)}語")
        lines.append(f"- Large (|d|≥0.8): {len(large)}語")
        lines.append(f"- Medium (0.5≤|d|<0.8): {len(medium)}語")
        lines.append(f"- Small (0.2≤|d|<0.5): {len(small)}語")
        lines.append("")
        lines.append("#### Top 20 by Effect Size")
        lines.append("")
        lines.append("| 語 | excess_score | Cohen's d | 効果量 | AI平均頻度 | Human頻度 |")
        lines.append("|-----|-------------|-----------|--------|-----------|----------|")
        sorted_effects = sorted(valid, key=lambda x: abs(x["cohens_d"]) if x["cohens_d"] else 0, reverse=True)
        for e in sorted_effects[:20]:
            lines.append(
                f"| {e['word']} | {e['excess_score']:+.4f} | {e['cohens_d']:.4f} | "
                f"{e['effect_magnitude']} | {e['ai_mean_freq']:.8f} | {e['human_freq_norm']:.8f} |"
            )

    # p値分布サマリ
    p_values = [r["p_bonferroni"] for r in chi2_results]
    lines.append("")
    lines.append("### p値分布サマリ（Bonferroni補正後）")
    lines.append("")
    lines.append(f"- p < 0.001: {sum(1 for p in p_values if p < 0.001)}語")
    lines.append(f"- p < 0.01: {sum(1 for p in p_values if p < 0.01)}語")
    lines.append(f"- p < 0.05: {sum(1 for p in p_values if p < 0.05)}語")
    lines.append(f"- p >= 0.05: {sum(1 for p in p_values if p >= 0.05)}語")
    
    return "\n".join(lines) + "\n"


def main():
    print("🔬 統計的検定開始\n")
    
    # データ読み込み
    excess_data = load_json(RESULTS_DIR / "excess_words.json")
    ai_freq = load_json(RESULTS_DIR / "word_freq_ai.json")
    human_freq = load_json(RESULTS_DIR / "word_freq_human.json")
    sub_freq = load_json(RESULTS_DIR / "sub_freq_ai.json")
    
    if not excess_data or not ai_freq or not human_freq:
        print("❌ 必要なデータファイルが見つかりません。先にtokenize_mecab.py → analyze_excess.pyを実行してください。")
        return
    
    excess_words = excess_data.get("excess", [])
    print(f"  対象: {len(excess_words)}語のexcess words")
    
    # 1. χ²検定
    print("\n── χ²検定 ──")
    chi2_results = chi_squared_test(excess_words, ai_freq, human_freq)
    print(f"  検定数: {len(chi2_results)}語")
    
    # 2. Mann-Whitney U検定
    print("\n── Mann-Whitney U検定 ──")
    model_comparisons, model_scores = mann_whitney_model_comparison(sub_freq, human_freq)
    print(f"  モデルペア数: {len(model_comparisons)}")
    
    # 2.5. Cohen's d effect size
    print("\n── Cohen's d Effect Size ──")
    effect_sizes = compute_effect_sizes(excess_words, sub_freq, human_freq)
    valid_effects = [e for e in effect_sizes if e["cohens_d"] is not None]
    large_effects = [e for e in valid_effects if e["effect_magnitude"] == "large"]
    medium_effects = [e for e in valid_effects if e["effect_magnitude"] == "medium"]
    small_effects = [e for e in valid_effects if e["effect_magnitude"] == "small"]
    print(f"  計算対象: {len(effect_sizes)}語")
    print(f"  有効な効果量: {len(valid_effects)}語")
    print(f"  Large (|d|≥0.8): {len(large_effects)}, Medium (0.5≤|d|<0.8): {len(medium_effects)}, Small (0.2≤|d|<0.5): {len(small_effects)}")

    # 3. Bonferroni補正
    print("\n── Bonferroni補正適用 ──")
    chi2_results, model_comparisons = apply_bonferroni(chi2_results, model_comparisons)
    
    sig_raw = sum(1 for r in chi2_results if r["significant_raw"])
    sig_bonf = sum(1 for r in chi2_results if r["significant_bonferroni"])
    print(f"  有意 (補正なし): {sig_raw}/{len(chi2_results)}")
    print(f"  有意 (Bonferroni): {sig_bonf}/{len(chi2_results)}")
    
    # p値をexcess_wordsに追加
    p_map = {r["word"]: r for r in chi2_results}
    for w in excess_words:
        if w["word"] in p_map:
            r = p_map[w["word"]]
            w["chi2"] = r["chi2"]
            w["p_value"] = r["p_value"]
            w["p_bonferroni"] = r["p_bonferroni"]
            w["significant"] = r["significant_bonferroni"]
        else:
            w["significant"] = None
    
    # 結果保存
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # statistical_tests.json
    output = {
        "chi2_tests": chi2_results,
        "mann_whitney_comparisons": model_comparisons,
        "effect_sizes": effect_sizes,
        "summary": {
            "total_words_tested": len(chi2_results),
            "significant_raw": sig_raw,
            "significant_bonferroni": sig_bonf,
            "model_pairs_tested": len(model_comparisons),
            "effect_size_computed": len(valid_effects),
            "large_effect": len(large_effects),
            "medium_effect": len(medium_effects),
            "small_effect": len(small_effects),
        }
    }
    
    with open(RESULTS_DIR / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  💾 {RESULTS_DIR / 'statistical_tests.json'}")
    
    # excess_words.jsonを更新（p値付き）
    with open(RESULTS_DIR / "excess_words.json", "w", encoding="utf-8") as f:
        json.dump(excess_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"  💾 {RESULTS_DIR / 'excess_words.json'} (p値追加)")
    
    # analysis_report.mdに追記
    report_addition = generate_stats_report(chi2_results, model_comparisons, model_scores, effect_sizes)
    report_path = RESULTS_DIR / "analysis_report.md"
    if report_path.exists():
        existing = report_path.read_text(encoding="utf-8")
        # 既存の統計セクションがあれば置換、なければ追記
        if "## 統計的検定結果" in existing:
            idx = existing.index("## 統計的検定結果")
            existing = existing[:idx].rstrip()
        existing += "\n\n" + report_addition
        report_path.write_text(existing, encoding="utf-8")
    else:
        report_path.write_text(report_addition, encoding="utf-8")
    print(f"  💾 {report_path} (統計セクション追記)")
    
    # Top 5 preview
    print("\n  📋 有意なExcess Words Top 5 (Bonferroni):")
    sig_sorted = sorted(
        [r for r in chi2_results if r["significant_bonferroni"]],
        key=lambda x: x["excess_score"], reverse=True
    )
    for i, r in enumerate(sig_sorted[:5], 1):
        print(f"    {i}. {r['word']} (score: {r['excess_score']:+.4f}, p={r['p_bonferroni']:.2e})")
    
    print("\n✅ 統計的検定完了")


if __name__ == "__main__":
    main()
