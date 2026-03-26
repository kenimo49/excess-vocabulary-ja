#!/usr/bin/env python3
"""
english_comparison.py — 英語excess wordsとの対照表

Geng & Trotta 2024の英語excess wordsに対応する日本語excess wordsをマッピング
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# Geng & Trotta 2024 主要英語excess words → 日本語対応候補（手動マッピング）
ENGLISH_JAPANESE_MAP = {
    "delve": {
        "meaning": "深く掘り下げる",
        "ja_candidates": ["掘り下げる", "深掘り", "探求", "深堀り", "掘り下げ", "詳しく見る"],
        "category": "探究・分析",
    },
    "intricate": {
        "meaning": "複雑な、精巧な",
        "ja_candidates": ["複雑", "精巧", "緻密", "巧妙", "入り組む"],
        "category": "複雑性",
    },
    "commendable": {
        "meaning": "称賛に値する",
        "ja_candidates": ["称賛", "素晴らしい", "賞賛", "優れる"],
        "category": "評価・賞賛",
    },
    "innovative": {
        "meaning": "革新的な",
        "ja_candidates": ["革新的", "革新", "イノベーション", "画期的"],
        "category": "革新性",
    },
    "meticulous": {
        "meaning": "几帳面な、細心の",
        "ja_candidates": ["緻密", "細心", "丁寧", "慎重", "綿密"],
        "category": "注意深さ",
    },
    "notably": {
        "meaning": "特に、注目すべきことに",
        "ja_candidates": ["特に", "注目", "顕著", "とりわけ"],
        "category": "強調",
    },
    "comprehensive": {
        "meaning": "包括的な",
        "ja_candidates": ["包括的", "網羅的", "総合的", "包括", "網羅"],
        "category": "包括性",
    },
    "pivotal": {
        "meaning": "極めて重要な",
        "ja_candidates": ["重要", "不可欠", "極めて", "中核", "核心"],
        "category": "重要性",
    },
    "underscore": {
        "meaning": "強調する",
        "ja_candidates": ["強調", "下線", "際立つ", "浮き彫り"],
        "category": "強調",
    },
    "nuanced": {
        "meaning": "ニュアンスのある",
        "ja_candidates": ["ニュアンス", "微妙", "繊細", "奥深い"],
        "category": "微妙さ",
    },
    "landscape": {
        "meaning": "景観、状況",
        "ja_candidates": ["ランドスケープ", "状況", "動向", "全体像", "概観"],
        "category": "概況",
    },
    "realm": {
        "meaning": "領域、分野",
        "ja_candidates": ["領域", "分野", "世界", "範囲"],
        "category": "領域",
    },
    "foster": {
        "meaning": "促進する、育てる",
        "ja_candidates": ["促進", "育成", "醸成", "涵養", "養う"],
        "category": "促進・育成",
    },
    "testament": {
        "meaning": "証、証明",
        "ja_candidates": ["証", "証明", "証拠", "裏付け"],
        "category": "証明",
    },
    "multifaceted": {
        "meaning": "多面的な",
        "ja_candidates": ["多面的", "多角的", "多様", "様々"],
        "category": "多面性",
    },
    "harnessing": {
        "meaning": "活用する",
        "ja_candidates": ["活用", "活かす", "利活用", "駆使"],
        "category": "活用",
    },
    "showcasing": {
        "meaning": "紹介する、披露する",
        "ja_candidates": ["紹介", "披露", "提示", "ショーケース"],
        "category": "提示",
    },
    "facilitating": {
        "meaning": "促進する、容易にする",
        "ja_candidates": ["促進", "容易", "円滑", "ファシリテート"],
        "category": "促進",
    },
    "paramount": {
        "meaning": "最重要の",
        "ja_candidates": ["最重要", "不可欠", "極めて重要", "肝要"],
        "category": "重要性",
    },
    "leveraging": {
        "meaning": "てこ入れする、活用する",
        "ja_candidates": ["活用", "レバレッジ", "駆使", "活かす"],
        "category": "活用",
    },
}


def find_matches_in_excess(excess_words: list, candidates: list) -> list:
    """excess words内から候補語を検索"""
    excess_map = {w["word"]: w for w in excess_words}
    matches = []
    for c in candidates:
        if c in excess_map:
            matches.append(excess_map[c])
    return matches


def generate_comparison_table(excess_data: dict) -> str:
    """英語↔日本語対照表をMarkdown生成"""
    excess_words = excess_data.get("excess", [])
    ai_only = excess_data.get("ai_only", [])
    
    # excess wordsとai_onlyを統合した検索用辞書
    all_words = {}
    for w in excess_words:
        all_words[w["word"]] = {
            "excess_score": w.get("excess_score", "N/A"),
            "ai_count": w.get("ai_count", 0),
            "human_count": w.get("human_count", 0),
            "type": "excess",
        }
    for w in ai_only:
        all_words[w["word"]] = {
            "excess_score": "AI固有",
            "ai_count": w.get("ai_count", 0),
            "human_count": w.get("human_count", 0),
            "type": "ai_only",
        }
    
    lines = [
        "# 英語 AI Slop Words ↔ 日本語 対照表",
        "",
        "## 概要",
        "",
        "Geng & Trotta (2024) が特定した英語のAI excess words 20語について、",
        "本実験（011-excess-vocabulary-ja）で検出された日本語excess wordsとのマッピングを行った。",
        "",
        "## 対照表",
        "",
        "| 英語 | 意味 | カテゴリ | 日本語候補 | 検出状況 | excess_score | AI出現数 |",
        "|------|------|---------|-----------|---------|-------------|---------|",
    ]
    
    found_count = 0
    for en_word, info in ENGLISH_JAPANESE_MAP.items():
        # 候補語の中からexcess wordsに含まれるものを検索
        detected = []
        best_match = None
        for ja in info["ja_candidates"]:
            if ja in all_words:
                w = all_words[ja]
                detected.append(f"**{ja}** ({w['excess_score']})")
                if best_match is None or (isinstance(w['excess_score'], (int, float)) and 
                    (best_match[1] == "AI固有" or w['excess_score'] > best_match[1])):
                    best_match = (ja, w['excess_score'], w['ai_count'])
        
        if detected:
            found_count += 1
            detected_str = ", ".join(detected)
            score = best_match[1] if best_match else "—"
            ai_count = best_match[2] if best_match else "—"
        else:
            detected_str = "未検出"
            score = "—"
            ai_count = "—"
        
        candidates_str = ", ".join(info["ja_candidates"][:4])
        lines.append(
            f"| {en_word} | {info['meaning']} | {info['category']} | "
            f"{candidates_str} | {detected_str} | {score} | {ai_count} |"
        )
    
    lines += [
        "",
        f"## サマリ",
        "",
        f"- 英語excess words 20語中、日本語で対応が検出されたもの: **{found_count}語**",
        f"- 検出されなかったもの: **{20 - found_count}語**",
        "",
        "## 考察",
        "",
        "### 共通パターン（英語・日本語で共通するAI slop傾向）",
        "",
        "1. **過剰な強調表現**: comprehensive/包括的、pivotal/重要、paramount/不可欠",
        "2. **活用・促進系**: leveraging/活用、harnessing/駆使、facilitating/促進",
        "3. **複雑性の誇張**: intricate/複雑、nuanced/繊細、multifaceted/多面的",
        "",
        "### 日本語固有のパターン",
        "",
        "英語にない日本語固有のAI slop傾向として:",
        "- 「〜を行う」「〜を実施する」などの冗長な動詞表現",
        "- 「適切な」「効果的な」などの形容詞の過剰使用",
        "- 丁寧語・敬語マーカーの過剰（「ございます」「させていただく」）",
        "",
        "### 「delve」に相当する日本語",
        "",
        "英語で最も有名なAI slop word「delve」に直接対応する日本語excess wordの検出状況:",
    ]
    
    delve_candidates = ENGLISH_JAPANESE_MAP["delve"]["ja_candidates"]
    for ja in delve_candidates:
        if ja in all_words:
            w = all_words[ja]
            lines.append(f"- **{ja}**: excess_score={w['excess_score']}, AI出現={w['ai_count']}, 人間出現={w['human_count']}")
        else:
            lines.append(f"- {ja}: excess wordsリストに未検出")
    
    lines.append("")
    lines.append("---")
    lines.append("*データソース: 011-excess-vocabulary-ja実験結果*")
    
    return "\n".join(lines) + "\n"


def main():
    print("🌐 英語↔日本語 excess words 対照表作成\n")
    
    excess_data = load_json(RESULTS_DIR / "excess_words.json")
    if not excess_data:
        print("❌ excess_words.json が見つかりません")
        return
    
    report = generate_comparison_table(excess_data)
    
    out_path = RESULTS_DIR / "english_japanese_comparison.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"  💾 {out_path}")
    
    # サマリ表示
    excess_words = excess_data.get("excess", [])
    ai_only = excess_data.get("ai_only", [])
    all_words_set = set(w["word"] for w in excess_words) | set(w["word"] for w in ai_only)
    
    found = 0
    for en_word, info in ENGLISH_JAPANESE_MAP.items():
        if any(ja in all_words_set for ja in info["ja_candidates"]):
            found += 1
    
    print(f"\n  英語20語中、日本語対応検出: {found}語")
    print("\n✅ 対照表作成完了")


def load_json(path: Path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


if __name__ == "__main__":
    main()
