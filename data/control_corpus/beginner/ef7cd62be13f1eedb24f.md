# 【物流AI #19】オンライン学習で概念ドリフトに追従する

## 概念ドリフトとは

季節変動・トレンド変化・新商品投入などで需要の統計的性質が変わることを**概念ドリフト**と呼ぶ。一度学習したモデルは徐々に劣化する。オンライン学習で常に最新データに追従させる。

## ADWIN によるドリフト検出

```python
from river.drift import ADWIN

detector = ADWIN(delta=0.002)

def monitor_drift(y_true, y_pred):
    error = abs(y_true - y_pred)
    detector.update(error)
    if detector.drift_detected:
        print(f"ドリフト検出！— 再学習を開始")
        return True
    return False
```

## River による逐次学習

```python
from river import linear_model, preprocessing, metrics

model  = preprocessing.StandardScaler() | \
         linear_model.PARegressor()     # Passive-Aggressive
metric = metrics.MAE()

for t, (x, y) in enumerate(data_stream):
    y_pred = model.predict_one(x)
    metric.update(y, y_pred)
    model.learn_one(x, y)

    if monitor_drift(y, y_pred):
        model = preprocessing.StandardScaler() | \
                linear_model.PARegressor()     # リセット
        print(f"t={t}: モデルリセット, MAE={metric.get():.2f}")
```

## PyTorch モデルの継続的更新

```python
from collections import deque
import torch

class OnlineUpdater:
    def __init__(self, model, lr=1e-4, buf_size=500):
        self.model = model
        self.opt   = torch.optim.Adam(model.parameters(), lr)
        self.buf   = deque(maxlen=buf_size)
        self.loss  = torch.nn.HuberLoss()

    def update(self, x, y):
        self.buf.append((x, y))
        if len(self.buf) < 64: return
        batch = list(self.buf)[-64:]
        bx = torch.FloatTensor([b[0] for b in batch])
        by = torch.FloatTensor([b[1] for b in batch])
        pred = self.model(bx)
        loss = self.loss(pred, by)
        self.opt.zero_grad(); loss.backward()
        # 小さい学習率でパラメータを微調整（破滅的忘却を抑制）
        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(), 0.1)
        self.opt.step()
        return loss.item()
```

## ドリフト対策の選択ガイド

| ドリフトの種類 | 推奨手法 |
|---|---|
| 急激な変化（イベント） | ADWIN 検出 + モデルリセット |
| 緩やかなトレンド | 指数移動平均・オンライン更新 |
| 周期的変化（季節） | 時刻特徴量を追加 + EWC |
| 分布未知 | Ensemble + 多数決 |

## 監視ダッシュボードの指標

```python
def drift_dashboard(errors: list) -> dict:
    arr = np.array(errors[-100:])
    return {
        "mae_recent":    arr.mean(),
        "mae_trend":     np.polyfit(range(len(arr)),arr,1)[0],
        "drift_flag":    monitor_drift(arr[-1], 0),
        "p99_error":     np.percentile(arr, 99),
    }
```

---
*シリーズ: 物流・倉庫 AI 実装ガイド 2026 (19/20)*
