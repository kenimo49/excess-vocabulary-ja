## 5. QAOAによるロボット経路最適化

### 5.1 QAOA概要

QAOA（Quantum Approximate Optimization Algorithm）は組み合わせ最適化問題を量子回路で解くアルゴリズムです。製造ロボットのタスク割り当てを**Max-Cut問題**に変換して解きます。

```python
import pennylane as qml, numpy as np, networkx as nx
from itertools import combinations

class RobotTaskScheduler:
    """QAOAでロボットタスクスケジューリングを最適化"""
    def __init__(self, n_tasks=6, n_robots=2):
        self.n_tasks = n_tasks
        self.n_robots = n_robots
        self.n_qubits = n_tasks
        self.task_graph = None
        self.device = qml.device("default.qubit", wires=n_tasks)

    def build_conflict_graph(self, seed=42):
        """タスク競合グラフを構築（同一ロボット/干渉エリア使用タスク間エッジ）"""
        np.random.seed(seed)
        G = nx.Graph()
        G.add_nodes_from(range(self.n_tasks))
        for i, j in combinations(range(self.n_tasks), 2):
            if np.random.random() > 0.4:
                G.add_edge(i, j, weight=np.random.uniform(0.5, 2.0))
        self.task_graph = G
        print(f"競合グラフ: {self.n_tasks}ノード, {G.number_of_edges()}エッジ")
        return G

    def _qaoa_cost_layer(self, gamma):
        """コスト層: H_C = Σ_{(i,j)∈E} w_{ij}(1-ZiZj)/2"""
        for i, j, d in self.task_graph.edges(data=True):
            qml.ZZPhase(-gamma * d.get('weight',1.0), wires=[i, j])

    def _qaoa_mixer_layer(self, beta):
        """ミキサー層: H_B = Σ_i X_i"""
        for i in range(self.n_qubits):
            qml.RX(2 * beta, wires=i)
```
