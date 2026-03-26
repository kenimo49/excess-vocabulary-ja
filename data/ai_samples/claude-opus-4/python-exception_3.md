# Pythonの例外処理のベストプラクティス

## はじめに

Pythonプログラミングにおいて、例外処理は堅牢なアプリケーションを構築する上で欠かせない要素です。適切な例外処理を実装することで、予期しないエラーからの回復、デバッグの効率化、そしてユーザーエクスペリエンスの向上が実現できます。

本記事では、Pythonの例外処理におけるベストプラクティスを実践的な例とともに解説します。

## 1. 具体的な例外をキャッチする

### ❌ 悪い例
```python
try:
    user_input = int(input("数値を入力してください: "))
    result = 100 / user_input
except:  # すべての例外をキャッチ
    print("エラーが発生しました")
```

### ✅ 良い例
```python
try:
    user_input = int(input("数値を入力してください: "))
    result = 100 / user_input
except ValueError:
    print("無効な入力です。数値を入力してください")
except ZeroDivisionError:
    print("ゼロでの除算はできません")
```

具体的な例外をキャッチすることで、エラーの種類に応じた適切な処理が可能になります。

## 2. EAFP原則を活用する

Pythonでは「許可を求めるより謝罪を求めよ（EAFP: Easier to Ask for Forgiveness than Permission）」という原則があります。

### ❌ LBYL（Look Before You Leap）アプローチ
```python
if os.path.exists(filename):
    with open(filename) as f:
        data = f.read()
else:
    print("ファイルが存在しません")
```

### ✅ EAFP アプローチ
```python
try:
    with open(filename) as f:
        data = f.read()
except FileNotFoundError:
    print("ファイルが存在しません")
```

EAFPアプローチは、Pythonicであり、競合状態を避けることができます。

## 3. finallyブロックでリソースをクリーンアップ

```python
def process_file(filename):
    file_handle = None
    try:
        file_handle = open(filename, 'r')
        data = file_handle.read()
        # データ処理
        return process_data(data)
    except IOError as e:
        print(f"ファイル処理エラー: {e}")
        return None
    finally:
        if file_handle:
            file_handle.close()
```

ただし、コンテキストマネージャーを使用する方がより推奨されます：

```python
def process_file(filename):
    try:
        with open(filename, 'r') as f:
            data = f.read()
            return process_data(data)
    except IOError as e:
        print(f"ファイル処理エラー: {e}")
        return None
```

## 4. カスタム例外クラスを定義する

アプリケーション固有のエラーには、カスタム例外クラスを定義しましょう。

```python
class ValidationError(Exception):
    """入力値の検証エラー"""
    pass

class InsufficientFundsError(Exception):
    """残高不足エラー"""
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"残高不足: 残高 {balance} < 必要額 {amount}")

def withdraw(balance, amount):
    if amount <= 0:
        raise ValidationError("引き出し金額は正の数である必要があります")
    if balance < amount:
        raise InsufficientFundsError(balance, amount)
    return balance - amount
```

## 5. 例外の再発生とチェイン

### 例外の再発生
```python
def process_data(data):
    try:
        # 何らかの処理
        result = risky_operation(data)
    except SpecificError as e:
        logger.error(f"データ処理中にエラー: {e}")
        raise  # 元の例外をそのまま再発生
```

### 例外チェイン
```python
def convert_to_int(value):
    try:
        return int(value)
    except ValueError as e:
        raise TypeError(f"整数への変換に失敗: {value}") from e
```

## 6. ロギングとモニタリング

```python
import logging

logger = logging.getLogger(__name__)

def critical_operation():
    try:
        # 重要な処理
        perform_operation()
    except Exception as e:
        logger.exception("重大なエラーが発生しました")
        # 必要に応じてメトリクスを記録
        metrics.increment('critical_operation.error')
        raise
```

## 7. 実践的な例：API クライアントの実装

```python
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API関連のエラーの基底クラス"""
    pass

class APIConnectionError(APIError):
    """API接続エラー"""
    pass

class APIResponseError(APIError):
    """APIレスポンスエラー"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"API Error {status_code}: {message}")

class APIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
    
    def get_data(self, endpoint: str) -> Optional[Dict]:
        """APIからデータを取得"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"タイムアウト: {url}")
            raise APIConnectionError(f"接続タイムアウト: {self.timeout}秒")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"接続エラー: {url}")
            raise APIConnectionError("APIサーバーに接続できません") from e
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTPエラー: {e.response.status_code}")
            raise APIResponseError(
                e.response.status_code,
                e.response.text
            ) from e
            
        except ValueError as e:
            logger.error(f"JSONパースエラー: {e}")
            raise APIResponseError(200, "無効なJSONレスポンス") from e
```

## まとめ

Pythonの例外処理のベストプラクティスをまとめると：

1. **具体的な例外をキャッチ**し、予期しないエラーを隠蔽しない
2. **EAFP原則**に従い、Pythonicなコードを書く
3. **finallyブロック**やコンテキストマネージャーでリソースを確実に解放
4. **カスタム例外**でドメイン固有のエラーを表現
5. **適切なロギング**でデバッグとモニタリングを容易に
6. **例外チェイン**で元のエラー情報を保持

これらの原則を守ることで、保守性が高く、デバッグしやすいPythonアプリケーションを構築できます。