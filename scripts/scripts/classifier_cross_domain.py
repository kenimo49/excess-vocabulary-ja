#!/usr/bin/env python3
"""
classifier_cross_domain.py — Cross-domain evaluation

Train: 技術ブログ (AI + Human)
Test:  日記/ビジネスメール/雑談 AI + 技術ブログ Human holdout(20%)

Reports:
  - in-domain performance (tech blog train/test split)
  - cross-domain performance (tech → other genres)
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
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score, roc_curve)
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
    """ディレクトリ内の全.mdファイルを読んで(freq_dict, filepath)のリストを返す"""
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


def docs_to_matrix(docs: list, feature_words: list) -> np.ndarray:
    """ドキュメント頻度辞書リストをfeature行列に変換"""
    X = np.zeros((len(docs), len(feature_words)))
    for i, doc_freq in enumerate(docs):
        for j, word in enumerate(feature_words):
            X[i, j] = doc_freq.get(word, 0)
    return X


def evaluate(model, X, y, label=""):
    """モデルの予測結果を評価"""
    pred = model.predict(X)
    prob = model.predict_proba(X)[:, 1]
    metrics = {
        "accuracy": round(accuracy_score(y, pred), 4),
        "f1": round(f1_score(y, pred, zero_division=0), 4),
    }
    try:
        metrics["auc_roc"] = round(roc_auc_score(y, prob), 4)
    except ValueError:
        metrics["auc_roc"] = None  # 単一クラスの場合
    metrics["n_samples"] = len(y)
    metrics["n_positive"] = int(y.sum())
    metrics["n_negative"] = int(len(y) - y.sum())
    return metrics, pred, prob


def main():
    print("📊 Cross-domain Classifier評価\n")

    tokenizer = Tokenizer()

    # Feature words
    excess_data = json.loads((RESULTS_DIR / "excess_words.json").read_text(encoding="utf-8"))
    feature_words = [w["word"] for w in excess_data.get("excess", [])[:100]]
    print(f"Feature words: {len(feature_words)}語")

    # ═══════════════════════════════════════════════════════
    # データ読み込み
    # ═══════════════════════════════════════════════════════
    print("\n── データ読み込み ──")

    # 技術ブログ AI
    tech_ai_docs = load_documents(AI_DIR, tokenizer)
    print(f"  Tech AI: {len(tech_ai_docs)}")

    # 技術ブログ Human
    tech_human_docs = load_documents(HUMAN_DIR, tokenizer)
    print(f"  Tech Human: {len(tech_human_docs)}")

    # Diverse AI（ジャンル別）
    genres = ["diary", "business", "casual"]
    genre_labels = {"diary": "日記", "business": "ビジネスメール", "casual": "雑談"}
    diverse_ai_docs = {}
    for genre in genres:
        genre_dir = DIVERSE_DIR / genre
        if genre_dir.exists():
            docs = load_documents(genre_dir, tokenizer)
            diverse_ai_docs[genre] = docs
            print(f"  {genre_labels[genre]} AI: {len(docs)}")
        else:
            diverse_ai_docs[genre] = []
            print(f"  ⚠ {genre} not found")

    # ═══════════════════════════════════════════════════════
    # In-domain: 技術ブログのみ（従来と同じ）
    # ═══════════════════════════════════════════════════════
    print("\n══ In-domain評価（技術ブログ） ══")

    X_tech_ai = docs_to_matrix(tech_ai_docs, feature_words)
    X_tech_human = docs_to_matrix(tech_human_docs, feature_words)

    X_indomain = np.vstack([X_tech_ai, X_tech_human])
    y_indomain = np.array([1] * len(tech_ai_docs) + [0] * len(tech_human_docs))

    X_train_in, X_test_in, y_train_in, y_test_in = train_test_split(
        X_indomain, y_indomain, test_size=0.2, random_state=42, stratify=y_indomain
    )

    scaler = StandardScaler()
    X_train_in_s = scaler.fit_transform(X_train_in)
    X_test_in_s = scaler.transform(X_test_in)

    # LR
    lr = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    lr.fit(X_train_in_s, y_train_in)
    in_lr, in_lr_pred, in_lr_prob = evaluate(lr, X_test_in_s, y_test_in, "In-domain LR")
    print(f"  LR: Acc={in_lr['accuracy']}, F1={in_lr['f1']}, AUC={in_lr['auc_roc']}")

    # RF
    rf = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
    rf.fit(X_train_in, y_train_in)
    in_rf, in_rf_pred, in_rf_prob = evaluate(rf, X_test_in, y_test_in, "In-domain RF")
    print(f"  RF: Acc={in_rf['accuracy']}, F1={in_rf['f1']}, AUC={in_rf['auc_roc']}")

    # ═══════════════════════════════════════════════════════
    # Cross-domain: 技術ブログで学習 → 他ジャンルでテスト
    # ═══════════════════════════════════════════════════════
    print("\n══ Cross-domain評価 ══")

    # Train: 技術ブログAI全部 + Human 80%
    # Test Human: 技術ブログ Human 20% holdout
    human_train_idx, human_test_idx = train_test_split(
        range(len(tech_human_docs)), test_size=0.2, random_state=42
    )
    human_train = [tech_human_docs[i] for i in human_train_idx]
    human_test = [tech_human_docs[i] for i in human_test_idx]

    X_train_ai = docs_to_matrix(tech_ai_docs, feature_words)
    X_train_human = docs_to_matrix(human_train, feature_words)
    X_cross_train = np.vstack([X_train_ai, X_train_human])
    y_cross_train = np.array([1] * len(tech_ai_docs) + [0] * len(human_train))

    print(f"  Cross-domain Train: {len(X_cross_train)} (AI={len(tech_ai_docs)}, Human={len(human_train)})")

    # Human holdout for test
    X_human_holdout = docs_to_matrix(human_test, feature_words)
    print(f"  Human holdout: {len(human_test)}")

    # Scaler for cross-domain
    scaler_cd = StandardScaler()
    X_cross_train_s = scaler_cd.fit_transform(X_cross_train)

    # Train models
    lr_cd = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    lr_cd.fit(X_cross_train_s, y_cross_train)

    rf_cd = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
    rf_cd.fit(X_cross_train, y_cross_train)

    cross_results = {}
    roc_data = {}

    # 各ジャンルでテスト
    for genre in genres:
        if not diverse_ai_docs[genre]:
            continue

        X_genre_ai = docs_to_matrix(diverse_ai_docs[genre], feature_words)
        # テストセット: genre AI + human holdout
        X_test_cd = np.vstack([X_genre_ai, X_human_holdout])
        y_test_cd = np.array([1] * len(diverse_ai_docs[genre]) + [0] * len(human_test))
        X_test_cd_s = scaler_cd.transform(X_test_cd)

        print(f"\n  ── {genre_labels[genre]} ──")
        print(f"    Test: {len(X_test_cd)} (AI={len(diverse_ai_docs[genre])}, Human={len(human_test)})")

        cd_lr, _, cd_lr_prob = evaluate(lr_cd, X_test_cd_s, y_test_cd)
        cd_rf, _, cd_rf_prob = evaluate(rf_cd, X_test_cd, y_test_cd)

        print(f"    LR: Acc={cd_lr['accuracy']}, F1={cd_lr['f1']}, AUC={cd_lr['auc_roc']}")
        print(f"    RF: Acc={cd_rf['accuracy']}, F1={cd_rf['f1']}, AUC={cd_rf['auc_roc']}")

        cross_results[genre] = {
            "label": genre_labels[genre],
            "logistic_regression": cd_lr,
            "random_forest": cd_rf,
        }
        roc_data[genre] = {
            "y_true": y_test_cd,
            "lr_prob": cd_lr_prob,
            "rf_prob": cd_rf_prob,
        }

    # All-genre combined test
    all_genre_ai = []
    for genre in genres:
        all_genre_ai.extend(diverse_ai_docs.get(genre, []))
    if all_genre_ai:
        X_all_genre_ai = docs_to_matrix(all_genre_ai, feature_words)
        X_test_all = np.vstack([X_all_genre_ai, X_human_holdout])
        y_test_all = np.array([1] * len(all_genre_ai) + [0] * len(human_test))
        X_test_all_s = scaler_cd.transform(X_test_all)

        print(f"\n  ── 全ジャンル統合 ──")
        print(f"    Test: {len(X_test_all)} (AI={len(all_genre_ai)}, Human={len(human_test)})")

        all_lr, _, all_lr_prob = evaluate(lr_cd, X_test_all_s, y_test_all)
        all_rf, _, all_rf_prob = evaluate(rf_cd, X_test_all, y_test_all)

        print(f"    LR: Acc={all_lr['accuracy']}, F1={all_lr['f1']}, AUC={all_lr['auc_roc']}")
        print(f"    RF: Acc={all_rf['accuracy']}, F1={all_rf['f1']}, AUC={all_rf['auc_roc']}")

        cross_results["all_genres"] = {
            "label": "全ジャンル統合",
            "logistic_regression": all_lr,
            "random_forest": all_rf,
        }
        roc_data["all_genres"] = {
            "y_true": y_test_all,
            "lr_prob": all_lr_prob,
            "rf_prob": all_rf_prob,
        }

    # ═══════════════════════════════════════════════════════
    # 結果保存
    # ═══════════════════════════════════════════════════════
    output = {
        "in_domain": {
            "description": "技術ブログ train/test split (80/20)",
            "logistic_regression": in_lr,
            "random_forest": in_rf,
        },
        "cross_domain": cross_results,
        "dataset": {
            "tech_ai_docs": len(tech_ai_docs),
            "tech_human_docs": len(tech_human_docs),
            "human_train": len(human_train),
            "human_holdout": len(human_test),
            "diverse_ai": {genre: len(docs) for genre, docs in diverse_ai_docs.items()},
            "n_features": len(feature_words),
        },
    }

    out_path = RESULTS_DIR / "classifier_cross_domain.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 {out_path}")

    # ═══════════════════════════════════════════════════════
    # ROC曲線（Cross-domain）
    # ═══════════════════════════════════════════════════════
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    colors = {"diary": "#3498db", "business": "#2ecc71", "casual": "#f39c12", "all_genres": "#e74c3c"}

    for ax, model_name, prob_key in [
        (axes[0], "Logistic Regression", "lr_prob"),
        (axes[1], "Random Forest", "rf_prob"),
    ]:
        # In-domain ROC
        if model_name == "Logistic Regression":
            fpr, tpr, _ = roc_curve(y_test_in, in_lr_prob)
            auc_val = in_lr["auc_roc"]
        else:
            fpr, tpr, _ = roc_curve(y_test_in, in_rf_prob)
            auc_val = in_rf["auc_roc"]
        ax.plot(fpr, tpr, '--', color='#95a5a6', linewidth=2,
                label=f"In-domain (AUC={auc_val:.3f})")

        # Cross-domain ROCs
        for key, data in roc_data.items():
            label = cross_results[key]["label"]
            auc_val = cross_results[key]["logistic_regression" if prob_key == "lr_prob" else "random_forest"]["auc_roc"]
            if auc_val is None:
                continue
            fpr, tpr, _ = roc_curve(data["y_true"], data[prob_key])
            ax.plot(fpr, tpr, color=colors.get(key, '#999'), linewidth=2,
                    label=f"{label} (AUC={auc_val:.3f})")

        ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title(f"Cross-domain ROC — {model_name}")
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig_path = FIG_DIR / "classifier_cross_domain_roc.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {fig_path}")

    # Summary table
    print("\n══ サマリー ══")
    print(f"{'ドメイン':<20} {'LR Acc':>8} {'LR F1':>8} {'LR AUC':>8} {'RF Acc':>8} {'RF F1':>8} {'RF AUC':>8}")
    print("-" * 80)
    print(f"{'In-domain (Tech)':<20} {in_lr['accuracy']:>8.4f} {in_lr['f1']:>8.4f} {in_lr['auc_roc'] or 'N/A':>8} {in_rf['accuracy']:>8.4f} {in_rf['f1']:>8.4f} {in_rf['auc_roc'] or 'N/A':>8}")
    for key, res in cross_results.items():
        label = res["label"]
        lr_r = res["logistic_regression"]
        rf_r = res["random_forest"]
        lr_auc = f"{lr_r['auc_roc']:.4f}" if lr_r['auc_roc'] else "N/A"
        rf_auc = f"{rf_r['auc_roc']:.4f}" if rf_r['auc_roc'] else "N/A"
        print(f"{label:<20} {lr_r['accuracy']:>8.4f} {lr_r['f1']:>8.4f} {lr_auc:>8} {rf_r['accuracy']:>8.4f} {rf_r['f1']:>8.4f} {rf_auc:>8}")


if __name__ == "__main__":
    main()
