## 2. 環境構築とライブラリ概要

```bash
# Python 3.11環境を想定
pip install pennylane==0.38.0 pennylane-qiskit==0.38.0
pip install qiskit==1.3.0 qiskit-aer==0.15.0
pip install qiskit-nature==0.7.0
pip install torch==2.3.0 numpy==1.26.4
pip install rdkit-pypi==2023.9.5
pip install scikit-learn==1.4.2
pip install matplotlib==3.8.4 seaborn==0.13.2
```

```python
# 動作確認
import pennylane as qml
import qiskit
import torch
import numpy as np

print(f"PennyLane: {qml.__version__}")
print(f"Qiskit: {qiskit.__version__}")
print(f"PyTorch: {torch.__version__}")
print(f"NumPy: {np.__version__}")
```

---
