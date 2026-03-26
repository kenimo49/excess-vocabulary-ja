#!/usr/bin/env python3
"""
embedding_analysis.py — Excess wordsの意味的クラスタリング

- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- t-SNE + UMAP で2D投影
- K-meansクラスタリング
- Hierarchical clustering（Ward法）+ デンドログラム
- クラスタの解釈（代表語、品詞分布、クラスタ間距離）
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

from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist, squareform

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
FIG_DIR = RESULTS_DIR / "figures"


def get_pos(word: str) -> str:
    """MeCabで単語の品詞を取得"""
    tagger = MeCab.Tagger(f"-d {unidic_lite.DICDIR}")
    node = tagger.parseToNode(word)
    while node:
        features = node.feature.split(",")
        if node.surface == word and len(features) >= 1:
            pos = features[0]
            sub = features[1] if len(features) >= 2 else ""
            if pos in ("名詞", "動詞", "形容詞", "副詞", "接続詞"):
                return f"{pos}" + (f"-{sub}" if sub and sub != "*" else "")
        node = node.next
    return "不明"


def main():
    print("📊 Embedding分析（拡張版）\n")

    # Excess words上位100語
    excess_data = json.loads((RESULTS_DIR / "excess_words.json").read_text(encoding="utf-8"))
    excess_words = [w["word"] for w in excess_data.get("excess", [])[:100]]
    excess_scores = {w["word"]: w["excess_score"] for w in excess_data.get("excess", [])[:100]}
    print(f"対象語数: {len(excess_words)}")

    # 品詞取得
    print("── 品詞解析 ──")
    word_pos = {}
    for word in excess_words:
        word_pos[word] = get_pos(word)

    # Embeddingモデル読み込み
    print("── モデル読み込み ──")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    print("  ✅ モデル読み込み完了")

    # Embedding取得
    print("── Embedding計算 ──")
    embeddings = model.encode(excess_words, show_progress_bar=True, batch_size=32)
    print(f"  Embedding shape: {embeddings.shape}")

    # ═══════════════════════════════════════════════════════
    # t-SNE
    # ═══════════════════════════════════════════════════════
    print("── t-SNE ──")
    perplexity = min(30, len(excess_words) - 1)
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity, max_iter=1000)
    coords_tsne = tsne.fit_transform(embeddings)
    print(f"  完了: {coords_tsne.shape}")

    # ═══════════════════════════════════════════════════════
    # UMAP
    # ═══════════════════════════════════════════════════════
    print("── UMAP ──")
    import umap
    reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.1,
        metric='cosine',
        random_state=42,
    )
    coords_umap = reducer.fit_transform(embeddings)
    print(f"  完了: {coords_umap.shape}")

    # ═══════════════════════════════════════════════════════
    # K-means（最適クラスタ数探索: 5-15）
    # ═══════════════════════════════════════════════════════
    print("── K-means（5-15クラスタ探索） ──")
    silhouette_results = {}
    best_k = 5
    best_score = -1
    for k in range(5, 16):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        silhouette_results[k] = round(score, 4)
        print(f"  k={k}: silhouette={score:.4f}")
        if score > best_score:
            best_score = score
            best_k = k

    print(f"  最適クラスタ数: {best_k} (silhouette: {best_score:.4f})")

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    cluster_labels = km_final.fit_predict(embeddings)

    # UMAP上のsilhouette score
    umap_silhouette = silhouette_score(coords_umap, cluster_labels)
    print(f"  UMAP空間のsilhouette: {umap_silhouette:.4f}")

    # ═══════════════════════════════════════════════════════
    # Hierarchical Clustering（Ward法）
    # ═══════════════════════════════════════════════════════
    print("── Hierarchical Clustering ──")
    linkage_matrix = linkage(embeddings, method='ward', metric='euclidean')

    # 最適クラスタ数（silhouette score で 5-15 比較）
    best_hc_k = 5
    best_hc_score = -1
    hc_silhouette_results = {}
    for k in range(5, 16):
        hc_labels = fcluster(linkage_matrix, t=k, criterion='maxclust')
        score = silhouette_score(embeddings, hc_labels)
        hc_silhouette_results[k] = round(score, 4)
        if score > best_hc_score:
            best_hc_score = score
            best_hc_k = k
    print(f"  HC最適クラスタ数: {best_hc_k} (silhouette: {best_hc_score:.4f})")

    hc_labels_final = fcluster(linkage_matrix, t=best_hc_k, criterion='maxclust')

    # ═══════════════════════════════════════════════════════
    # クラスタ解釈
    # ═══════════════════════════════════════════════════════
    print("\n── クラスタ解釈（K-means） ──")
    clusters = {}
    for i, (word, label) in enumerate(zip(excess_words, cluster_labels)):
        label = int(label)
        if label not in clusters:
            clusters[label] = []
        clusters[label].append({
            "word": word,
            "excess_score": excess_scores.get(word, 0),
            "pos": word_pos.get(word, "不明"),
            "x_tsne": round(float(coords_tsne[i, 0]), 4),
            "y_tsne": round(float(coords_tsne[i, 1]), 4),
            "x_umap": round(float(coords_umap[i, 0]), 4),
            "y_umap": round(float(coords_umap[i, 1]), 4),
        })

    cluster_summary = {}
    for label, words_in_cluster in sorted(clusters.items()):
        words_in_cluster.sort(key=lambda x: x["excess_score"], reverse=True)
        top_words = [w["word"] for w in words_in_cluster[:10]]

        # 品詞分布
        pos_counter = Counter(w["pos"] for w in words_in_cluster)
        pos_dist = {pos: count for pos, count in pos_counter.most_common()}

        cluster_summary[f"cluster_{label}"] = {
            "size": len(words_in_cluster),
            "top_words": top_words,
            "all_words": [w["word"] for w in words_in_cluster],
            "avg_excess_score": round(np.mean([w["excess_score"] for w in words_in_cluster]), 4),
            "pos_distribution": pos_dist,
        }
        print(f"  Cluster {label} ({len(words_in_cluster)}語): {', '.join(top_words[:5])}")
        print(f"    品詞: {pos_dist}")

    # クラスタ間距離（centroid間）
    print("\n── クラスタ間距離 ──")
    centroids = km_final.cluster_centers_
    centroid_dist = squareform(pdist(centroids, metric='cosine'))
    cluster_distances = {}
    for i in range(best_k):
        for j in range(i + 1, best_k):
            key = f"cluster_{i}_vs_{j}"
            dist = round(float(centroid_dist[i, j]), 4)
            cluster_distances[key] = dist
            print(f"  Cluster {i} ↔ Cluster {j}: {dist:.4f}")

    # ═══════════════════════════════════════════════════════
    # 結果保存
    # ═══════════════════════════════════════════════════════
    results = {
        "n_words": len(excess_words),
        "kmeans": {
            "n_clusters": best_k,
            "silhouette_score": round(best_score, 4),
            "umap_silhouette_score": round(umap_silhouette, 4),
            "silhouette_by_k": silhouette_results,
            "clusters": cluster_summary,
            "cluster_distances_cosine": cluster_distances,
        },
        "hierarchical": {
            "n_clusters": best_hc_k,
            "silhouette_score": round(best_hc_score, 4),
            "silhouette_by_k": hc_silhouette_results,
        },
        "word_coordinates": [
            {
                "word": word,
                "cluster_kmeans": int(cluster_labels[i]),
                "cluster_hierarchical": int(hc_labels_final[i]),
                "pos": word_pos.get(word, "不明"),
                "x_tsne": round(float(coords_tsne[i, 0]), 4),
                "y_tsne": round(float(coords_tsne[i, 1]), 4),
                "x_umap": round(float(coords_umap[i, 0]), 4),
                "y_umap": round(float(coords_umap[i, 1]), 4),
                "excess_score": excess_scores.get(word, 0),
            }
            for i, word in enumerate(excess_words)
        ],
    }

    out_path = RESULTS_DIR / "embedding_analysis.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 {out_path}")

    # ═══════════════════════════════════════════════════════
    # 可視化
    # ═══════════════════════════════════════════════════════
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # --- 1. t-SNEプロット（既存の改善版） ---
    fig, ax = plt.subplots(figsize=(14, 10))
    cmap = plt.cm.get_cmap("tab10", best_k)
    for label in range(best_k):
        mask = cluster_labels == label
        xs = coords_tsne[mask, 0]
        ys = coords_tsne[mask, 1]
        top3 = cluster_summary[f"cluster_{label}"]["top_words"][:3]
        ax.scatter(xs, ys, c=[cmap(label)], s=80, alpha=0.7,
                   label=f"Cluster {label}: {', '.join(top3)}", edgecolors="white", linewidth=0.5)
    for i, word in enumerate(excess_words[:40]):
        ax.annotate(word, (coords_tsne[i, 0], coords_tsne[i, 1]),
                    fontsize=7, alpha=0.8, xytext=(5, 5), textcoords="offset points")
    ax.set_title(f"Excess Words 意味クラスタリング (t-SNE + K-means, k={best_k})")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.2)
    plt.savefig(FIG_DIR / "embedding_clusters.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {FIG_DIR / 'embedding_clusters.png'}")

    # --- 2. UMAPプロット ---
    fig, ax = plt.subplots(figsize=(14, 10))
    for label in range(best_k):
        mask = cluster_labels == label
        xs = coords_umap[mask, 0]
        ys = coords_umap[mask, 1]
        top3 = cluster_summary[f"cluster_{label}"]["top_words"][:3]
        ax.scatter(xs, ys, c=[cmap(label)], s=80, alpha=0.7,
                   label=f"Cluster {label}: {', '.join(top3)}", edgecolors="white", linewidth=0.5)
    for i, word in enumerate(excess_words[:40]):
        ax.annotate(word, (coords_umap[i, 0], coords_umap[i, 1]),
                    fontsize=7, alpha=0.8, xytext=(5, 5), textcoords="offset points")
    ax.set_title(f"Excess Words 意味クラスタリング (UMAP + K-means, k={best_k}, silhouette={umap_silhouette:.3f})")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.2)
    plt.savefig(FIG_DIR / "embedding_umap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {FIG_DIR / 'embedding_umap.png'}")

    # --- 3. デンドログラム ---
    fig, ax = plt.subplots(figsize=(18, 8))
    dendrogram(
        linkage_matrix,
        labels=excess_words,
        leaf_rotation=90,
        leaf_font_size=7,
        color_threshold=linkage_matrix[-(best_hc_k - 1), 2],
        ax=ax,
    )
    ax.set_title(f"Excess Words 階層的クラスタリング（Ward法, 最適k={best_hc_k}）")
    ax.set_ylabel("距離")
    plt.savefig(FIG_DIR / "embedding_dendrogram.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {FIG_DIR / 'embedding_dendrogram.png'}")

    # --- 4. Silhouette scoreの推移 ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ks = sorted(silhouette_results.keys())
    axes[0].plot(ks, [silhouette_results[k] for k in ks], 'o-', color='#e74c3c', linewidth=2)
    axes[0].axvline(x=best_k, color='gray', linestyle='--', alpha=0.7, label=f'Best k={best_k}')
    axes[0].set_xlabel("クラスタ数 (k)")
    axes[0].set_ylabel("Silhouette Score")
    axes[0].set_title("K-means Silhouette Score")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    hc_ks = sorted(hc_silhouette_results.keys())
    axes[1].plot(hc_ks, [hc_silhouette_results[k] for k in hc_ks], 'o-', color='#3498db', linewidth=2)
    axes[1].axvline(x=best_hc_k, color='gray', linestyle='--', alpha=0.7, label=f'Best k={best_hc_k}')
    axes[1].set_xlabel("クラスタ数 (k)")
    axes[1].set_ylabel("Silhouette Score")
    axes[1].set_title("Hierarchical Clustering Silhouette Score")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "embedding_silhouette_scores.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 {FIG_DIR / 'embedding_silhouette_scores.png'}")


if __name__ == "__main__":
    main()
