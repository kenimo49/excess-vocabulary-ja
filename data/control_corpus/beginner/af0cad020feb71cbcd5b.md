# 【物流AI #3】量子コンピュータで配送ルートを最適化：QAOA × VRP 入門

## Vehicle Routing Problem（VRP）とは

配送センターから複数顧客へ、複数トラックで配送する最適経路を求める問題。顧客数が増えると組み合わせが爆発し、古典的な厳密解法では現実的な時間内に解けない（NP困難）。

QAOA（量子近似最適化アルゴリズム）は量子ビットの重ね合わせを利用して近似最適解を探索する。

## QUBO へ変換する

量子コンピュータで解くには、問題を **QUBO（2値変数の2次最小化）** に変換する。

変数: $x_{ik} \in \{0,1\}$ ＝「顧客 $i$ をトラック $k$ が担当」

```python
import numpy as np

def build_qubo(dist, demands, cap, nc, nv,
               lam1=100.0, lam2=50.0) -> np.ndarray:
    n = nc * nv
    Q = np.zeros((n, n))
    ix = lambda i, k: i * nv + k

    # コスト: 顧客間距離
    for k in range(nv):
        for i in range(nc):
            for j in range(nc):
                if i != j:
                    Q[ix(i,k), ix(j,k)] += 0.5 * dist[i+1, j+1]

    # 制約1: 各顧客をちょうど1台が担当
    for i in range(nc):
        for k in range(nv):
            Q[ix(i,k), ix(i,k)] -= lam1
        for k1 in range(nv):
            for k2 in range(k1+1, nv):
                Q[ix(i,k1), ix(i,k2)] += 2 * lam1

    # 制約2: 積載量超過ペナルティ
    for k in range(nv):
        for i in range(nc):
            for j in range(i+1, nc):
                if demands[i] + demands[j] > cap:
                    Q[ix(i,k), ix(j,k)] += lam2
    return Q
```

## QUBO エネルギーの計算

```python
def qubo_energy(Q: np.ndarray, bits: np.ndarray) -> float:
    return float(bits @ Q @ bits)
```

## ペナルティ係数の選び方

| パラメータ | 説明 | 推奨値 |
|---|---|---|
| `lam1` | 1回訪問制約の強さ | コスト最大値の 5〜10倍 |
| `lam2` | 積載量違反ペナルティ | `lam1` の 0.5倍 |

`lam1` が小さすぎると制約違反解が最適解になる。大きすぎるとコスト項を無視してしまう。

次回は Qiskit で QAOA 回路を構築して量子シミュレータで求解する。

---
*シリーズ: 物流・倉庫 AI 実装ガイド 2026 (3/6)*
