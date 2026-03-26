#!/usr/bin/env python3
"""
classifier.py — Excess wordsベースのAI/人間テキスト分類器

Features: excess score上位100語の出現頻度ベクトル
Models: ロジスティック回帰 + ランダムフォレスト
"""

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import MeCab
import unidic_lite
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import japanize_matplotlib  # noqa: F401

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, roc_curve, classification_report)
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
FIG_DIR = RESULTS_DIR / "figures"
AI_DIR = BASE_DIR / "data" / "ai_samples"
HUMAN_DIR = BASE_DIR / "data" / "human_corpus"
DIVERSE_DIR = BASE_DIR / "data" / "ai_samples_diverse"

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


def load_documents(directory: Path, tokenizer: Tokenizer) -> list:
    """ディレクトリ内の全.mdファイルを読んで単語カウントを返す"""
    docs = []
    for f in sorted(directory.rglob("*.md")):
        if f.name == "metadata.json":
            continue
        text = clean_text(f.read_text(encoding="utf-8"))
        if len(text) < 100:
            continue
        words = tokenizer.extract_words(text)
        if len(words) < 20:
            continue
        counter = Counter(words)
        total = sum(counter.values())
        freq = {k: v / total for k, v in counter.items()}
        docs.append(freq)
    return docs


def main():
    print("📊 Classifier構築\n")

    tokenizer = Tokenizer()

    # Excess words上位100語をfeatureとして使用
    excess_data = json.loads((RESULTS_DIR / "excess_words.json").read_text(encoding="utf-8"))
    feature_words = [w["word"] for w in excess_data.get("excess", [])[:100]]
    print(f"Feature words: {len(feature_words)}語")

    # AIテキスト読み込み
    print("── AI文書読み込み ──")
    ai_docs = load_documents(AI_DIR, tokenizer)
    # 多様化ジャンルも含める（あれば）
    if DIVERSE_DIR.exists():
        diverse_docs = load_documents(DIVERSE_DIR, tokenizer)
        ai_docs.extend(diverse_docs)
    print(f"  AI文書: {len(ai_docs)}")

    # 人間テキスト読み込み
    print("── 人間文書読み込み ──")
    human_docs = load_documents(HUMAN_DIR, tokenizer)
    print(f"  人間文書: {len(human_docs)}")

    # Feature行列構築
    all_docs = ai_docs + human_docs
    labels = [1] * len(ai_docs) + [0] * len(human_docs)

    X = np.zeros((len(all_docs), len(feature_words)))
    for i, doc_freq in enumerate(all_docs):
        for j, word in enumerate(feature_words):
            X[i, j] = doc_freq.get(word, 0)

    y = np.array(labels)
    print(f"\n全体: {len(all_docs)}文書 (AI={len(ai_docs)}, Human={len(human_docs)})")
    print(f"Feature matrix: {X.shape}")

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # スケーリング
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    # ロジスティック回帰
    print("\n── ロジスティック回帰 ──")
    lr = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    lr.fit(X_train_scaled, y_train)
    lr_pred = lr.predict(X_test_scaled)
    lr_prob = lr.predict_proba(X_test_scaled)[:, 1]

    lr_metrics = {
        "accuracy": round(accuracy_score(y_test, lr_pred), 4),
        "precision": round(precision_score(y_test, lr_pred), 4),
        "recall": round(recall_score(y_test, lr_pred), 4),
        "f1": round(f1_score(y_test, lr_pred), 4),
        "auc_roc": round(roc_auc_score(y_test, lr_prob), 4),
    }
    results["logistic_regression"] = lr_metrics
    print(f"  Accuracy: {lr_metrics['accuracy']}")
    print(f"  F1: {lr_metrics['f1']}")
    print(f"  AUC-ROC: {lr_metrics['auc_roc']}")

    # ランダムフォレスト
    print("\n── ランダムフォレスト ──")
    rf = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
    rf.fit(X_train, y_train)  # RFはスケーリング不要
    rf_pred = rf.predict(X_test)
    rf_prob = rf.predict_proba(X_test)[:, 1]

    rf_metrics = {
        "accuracy": round(accuracy_score(y_test, rf_pred), 4),
        "precision": round(precision_score(y_test, rf_pred), 4),
        "recall": round(recall_score(y_test, rf_pred), 4),
        "f1": round(f1_score(y_test, rf_pred), 4),
        "auc_roc": round(roc_auc_score(y_test, rf_prob), 4),
    }
    results["random_forest"] = rf_metrics
    print(f"  Accuracy: {rf_metrics['accuracy']}")
    print(f"  F1: {rf_metrics['f1']}")
    print(f"  AUC-ROC: {rf_metrics['auc_roc']}")

    # Feature importance (RF)
    importances = rf.feature_importances_
    feat_imp = sorted(zip(feature_words, importances), key=lambda x: x[1], reverse=True)
    results["top_features"] = [{"word": w, "importance": round(imp, 6)} for w, imp in feat_imp[:30]]

    # LR coefficients
    lr_coefs = sorted(zip(feature_words, lr.coef_[0]), key=lambda x: abs(x[1]), reverse=True)
    results["lr_top_coefficients"] = [{"word": w, "coefficient": round(c, 6)} for w, c in lr_coefs[:30]]

    results["dataset"] = {
        "total_docs": len(all_docs),
        "ai_docs": len(ai_docs),
        "human_docs": len(human_docs),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "n_features": len(feature_words),
    }

    # 結果保存
    out_path = RESULTS_DIR / "classifier_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 {out_path}")

    # ROC曲線
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))

    lr_fpr, lr_tpr, _ = roc_curve(y_test, lr_prob)
    rf_fpr, rf_tpr, _ = roc_curve(y_test, rf_prob)

    ax.plot(lr_fpr, lr_tpr, label=f"Logistic Regression (AUC={lr_metrics['auc_roc']:.3f})",
            linewidth=2, color="#e74c3c")
    ax.plot(rf_fpr, rf_tpr, label=f"Random Forest (AUC={rf_metrics['auc_roc']:.3f})",
            linewidth=2, color="#3498db")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random (AUC=0.500)")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("AI/Human Classifier — ROC Curve")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

    fig_path = FIG_DIR / "classifier_roc.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {fig_path}")

    # Feature importance図
    fig, ax = plt.subplots(figsize=(10, 8))
    top20 = feat_imp[:20]
    words = [w for w, _ in top20][::-1]
    imps = [imp for _, imp in top20][::-1]
    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(words)))
    ax.barh(range(len(words)), imps, color=colors)
    ax.set_yticks(range(len(words)))
    ax.set_yticklabels(words)
    ax.set_xlabel("Feature Importance (Random Forest)")
    ax.set_title("Top 20 重要特徴量（AI検出に効く語）")

    fig_path = FIG_DIR / "classifier_features.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {fig_path}")


if __name__ == "__main__":
    main()
