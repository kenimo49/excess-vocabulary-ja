#!/usr/bin/env python3
"""
tokenize_mecab.py — MeCab形態素解析 + 単語/N-gram頻度算出

全テキスト（AI + 人間）をMeCabで解析し、
品詞フィルタ・ストップワード除外・N-gram・文頭パターン分析を行う。
"""

import json
import re
import argparse
from collections import Counter, defaultdict
from pathlib import Path

import MeCab
import unidic_lite

BASE_DIR = Path(__file__).resolve().parent.parent
AI_DIR = BASE_DIR / "data" / "ai_samples"
HUMAN_DIR = BASE_DIR / "data" / "human_corpus"
HUMAN_POST_DIR = BASE_DIR / "data" / "human_corpus_post_llm"
RESULTS_DIR = BASE_DIR / "results"

# 対象品詞 (unidic-lite uses more granular POS)
TARGET_POS = {"名詞", "動詞", "形容詞", "副詞", "接続詞"}

# 除外する名詞サブカテゴリ (unidic-lite style)
EXCLUDE_NOUN_SUB = {"数詞", "非自立可能", "代名詞", "助数詞"}

# ストップワード（頻出すぎて分析ノイズになる語）
STOPWORDS = {
    "する", "為る", "いる", "居る", "ある", "有る", "なる", "成る",
    "できる", "出来る", "れる", "られる",
    "こと", "事", "もの", "物", "ため", "為", "よう", "様",
    "それ", "これ", "ここ", "其れ", "此れ", "此処",
    "の", "に", "は", "を", "が", "と", "で", "も", "か",
    "や", "へ", "から", "まで", "より", "etc", "##",
}

# Markdownノイズ除去パターン
MD_NOISE = re.compile(r'```[\s\S]*?```|`[^`]+`|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|#{1,6}\s|[*_~`>|]|\|.*\|')
URL_PATTERN = re.compile(r'https?://\S+')


def clean_text(text: str) -> str:
    """Markdown記法とURLを除去"""
    text = MD_NOISE.sub(" ", text)
    text = URL_PATTERN.sub(" ", text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_sentences(text: str) -> list:
    """文を分割"""
    return [s.strip() for s in re.split(r'[。！？\n]', text) if s.strip()]


class MeCabTokenizer:
    def __init__(self):
        self.tagger = MeCab.Tagger(f"-d {unidic_lite.DICDIR}")
        self.tagger.parse("")  # 初期化

    def tokenize(self, text: str) -> list:
        """テキストをトークナイズし、(表層形, 品詞, 品詞細分類, 原形) のリストを返す
        
        unidic-lite feature format (parseToNode):
          [0]=品詞, [1]=品詞細分類1, [2]=品詞細分類2, [3]=品詞細分類3,
          [4]=活用型, [5]=活用形, [6]=読み, [7]=原形(lemma漢字表記)
        """
        tokens = []
        node = self.tagger.parseToNode(text)
        while node:
            if node.surface:
                features = node.feature.split(",")
                pos = features[0] if len(features) > 0 else ""
                pos_sub = features[1] if len(features) > 1 else ""
                # unidic-lite: index 7 = lemma (漢字原形)
                base = features[7] if len(features) > 7 else node.surface
                if base == "*" or not base:
                    base = node.surface
                tokens.append((node.surface, pos, pos_sub, base))
            node = node.next
        return tokens

    def extract_words(self, text: str) -> list:
        """品詞フィルタ + ストップワード除外した原形リストを返す"""
        tokens = self.tokenize(text)
        words = []
        for surface, pos, pos_sub, base in tokens:
            if pos not in TARGET_POS:
                continue
            if pos == "名詞" and pos_sub in EXCLUDE_NOUN_SUB:
                continue
            # unidic: 非自立可能 includes する/いる etc
            if pos == "動詞" and pos_sub == "非自立可能":
                continue
            if base in STOPWORDS or surface in STOPWORDS:
                continue
            if len(base) == 1 and not base.isalpha():
                continue
            words.append(base)
        return words

    def extract_sentence_starters(self, text: str) -> list:
        """各文の最初の形態素（原形）を抽出"""
        sentences = split_sentences(text)
        starters = []
        for sent in sentences:
            tokens = self.tokenize(sent)
            # 最初の意味のある形態素を取得
            for surface, pos, pos_sub, base in tokens:
                if pos in TARGET_POS or pos in {"接続詞", "副詞"}:
                    starters.append(base)
                    break
                elif pos == "記号" or pos == "助詞":
                    continue
                else:
                    starters.append(base)
                    break
        return starters


def get_ngrams(words: list, n: int) -> list:
    """N-gramを生成"""
    return ["_".join(words[i:i+n]) for i in range(len(words) - n + 1)]


def analyze_corpus(directory: Path, tokenizer: MeCabTokenizer, label: str) -> dict:
    """コーパスを解析して頻度データを返す"""
    word_counter = Counter()
    bigram_counter = Counter()
    trigram_counter = Counter()
    starter_counter = Counter()
    punct_counter = Counter()
    total_chars = 0
    total_docs = 0

    # モデル別（AI）/ ソース別（人間）の集計
    sub_counters = defaultdict(Counter)

    md_files = list(directory.rglob("*.md"))
    print(f"  📁 {label}: {len(md_files)}ファイル")

    for f in md_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if len(text) < 100:
            continue

        # サブカテゴリ判定（親ディレクトリ名）
        sub_key = f.parent.name

        cleaned = clean_text(text)
        total_chars += len(cleaned)
        total_docs += 1

        # 単語抽出
        words = tokenizer.extract_words(cleaned)
        word_counter.update(words)
        sub_counters[sub_key].update(words)

        # N-gram
        bigrams = get_ngrams(words, 2)
        trigrams = get_ngrams(words, 3)
        bigram_counter.update(bigrams)
        trigram_counter.update(trigrams)

        # 文頭パターン
        starters = tokenizer.extract_sentence_starters(cleaned)
        starter_counter.update(starters)

        # 記号・句読点
        for ch in text:
            if ch in "、。！？…―（）「」『』【】・":
                punct_counter[ch] += 1

    return {
        "word_freq": dict(word_counter.most_common()),
        "bigram_freq": dict(bigram_counter.most_common()),
        "trigram_freq": dict(trigram_counter.most_common()),
        "starter_freq": dict(starter_counter.most_common()),
        "punct_freq": dict(punct_counter.most_common()),
        "sub_freq": {k: dict(v.most_common()) for k, v in sub_counters.items()},
        "total_chars": total_chars,
        "total_docs": total_docs,
    }


def save_results(data: dict, prefix: str):
    """分析結果をJSONで保存"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 単語頻度
    with open(RESULTS_DIR / f"word_freq_{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(data["word_freq"], f, ensure_ascii=False, indent=2)

    # N-gram頻度
    ngram_data = {
        "bigram": data["bigram_freq"],
        "trigram": data["trigram_freq"],
    }
    with open(RESULTS_DIR / f"ngram_{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(ngram_data, f, ensure_ascii=False, indent=2)

    # 文頭パターン
    with open(RESULTS_DIR / f"starters_{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(data["starter_freq"], f, ensure_ascii=False, indent=2)

    # 句読点
    with open(RESULTS_DIR / f"punct_{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(data["punct_freq"], f, ensure_ascii=False, indent=2)

    # サブカテゴリ別
    with open(RESULTS_DIR / f"sub_freq_{prefix}.json", "w", encoding="utf-8") as f:
        json.dump(data["sub_freq"], f, ensure_ascii=False, indent=2)

    print(f"  💾 {prefix}: {data['total_docs']}文書, {data['total_chars']}文字, "
          f"{len(data['word_freq'])}ユニーク語")


def main():
    parser = argparse.ArgumentParser(description="MeCab形態素解析")
    parser.add_argument("--ai-only", action="store_true")
    parser.add_argument("--human-only", action="store_true")
    args = parser.parse_args()

    tokenizer = MeCabTokenizer()
    print("🔤 MeCab形態素解析開始\n")

    if not args.human_only:
        print("── AI生成テキスト ──")
        ai_data = analyze_corpus(AI_DIR, tokenizer, "AI")
        save_results(ai_data, "ai")

    if not args.ai_only:
        print("\n── 人間コーパス (Pre-LLM) ──")
        human_data = analyze_corpus(HUMAN_DIR, tokenizer, "Human")
        save_results(human_data, "human")

        if HUMAN_POST_DIR.exists():
            print("\n── 人間コーパス (Post-LLM 2024-2026) ──")
            human_post_data = analyze_corpus(HUMAN_POST_DIR, tokenizer, "Human-Post")
            save_results(human_post_data, "human_post")

    print("\n✅ 形態素解析完了")
    print(f"出力: {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
