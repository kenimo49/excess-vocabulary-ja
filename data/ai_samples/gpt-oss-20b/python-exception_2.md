# Pythonの例外処理のベストプラクティス

Pythonは**例外**でエラー処理を柔軟に行える言語ですが、乱暴に`try/except`を書き回すと「何が起きているか分からない」状態になりがちです。  
この記事では、エンジニアが実務で直面する典型的な課題を解決するためのベストプラクティスを紹介します。  
実装例も併せて示すので、すぐに自分のプロジェクトに取り入れられるはずです。

---

## 1. 例外は**「何が失敗したか」**を正確に伝えるものにする

### 1‑1. カスタム例外を定義する

```python
class DataValidationError(RuntimeError):
    """データバリデーション失敗時に投げる例外"""

    def __init__(self, field, message):
        self.field = field
        super().__init__(f"[{field}] {message}")
```

- **メリット**  
  - `except`側で `isinstance(e, DataValidationError)` で判定しやすい  
  - エラーメッセージを一貫したフォーマットで出力できる  
  - ログレベルや通知先を柔軟に切り替えられる

### 1‑2. 標準例外を使い分ける

| 例外 | 用途 |
|------|------|
| `ValueError` | 値が不適切（型は正しいが意味不明） |
| `TypeError`  | 型が不適切 |
| `IOError`（`OSError`） | ファイル/ネットワーク操作失敗 |
| `KeyError` | 辞書に存在しないキー参照 |
| `IndexError` | リスト/タプルに不正インデックス |

「何が失敗したか」を**正確に**表現することで、デバッグ時に追跡しやすくなります。

---

## 2. 例外を**狭く**捕捉する

```python
# ❌ 典型的なミス
try:
    data = json.loads(raw)
    value = data["price"]
    do_something(value)
except Exception:
    handle_error()
```

- `Exception` を捕捉すると **すべて** のエラーを丸めてしまい、意図しない失敗が隠れます。  
- 代わりに `JSONDecodeError`, `KeyError`, `ValueError` など、**予想される例外**だけを列挙しましょう。

```python
# ✅ より安全
try:
    data = json.loads(raw)
    value = data["price"]
    do_something(value)
except json.JSONDecodeError as e:
    logger.error("JSON parse failed: %s", e)
    raise
except KeyError as e:
    logger.error("Missing key: %s", e)
    raise
```

---

## 3. **`else`** と **`finally`** を活用する

```python
try:
    conn = acquire_connection()
    result = conn.execute(query)
except DBError:
    handle_db_error()
else:
    # 正常時のみ実行
    process(result)
finally:
    # リソース解放は必ず実行
    conn.close()
```

- `else` は**例外が発生しなかった**時に実行されるため、`try` 内での副作用（リソース確保）が成功した後にのみ処理を行いたいときに便利です。  
- `finally` は例外の有無に関わらず必ず実行されるので、ファイルやネットワークのクローズ、ロック解放に最適です。

---

## 4. 例外を**再投げ（`raise`）**して情報を失わない

```python
def parse_config(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        # 追加情報を付与して再投げ
        raise ValueError(f"config {path} is invalid") from e
```

- `raise` だけで再投げするとスタックトレースが失われるため、`raise ... from e` を使うと**原因チェーン**が保持されます。  
- これにより、上位層でエラーをハンドリングする際に「どの段階で失敗したか」を把握できます。

---

## 5. 例外を**ログ**に残す

```python
try:
    do_work()
except SpecificError as e:
    logger.exception("Unexpected failure in do_work")
```

- `logger.exception()` はスタックトレースを自動で含めるので、デバッグに役立ちます。  
- ただし、**機密情報**（パスワードやAPIキー）はログに出さないように注意してください。  
- 必要に応じてログレベル（`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`）を分け、モニタリングシステムへ通知を送るようにします。

---

## 6. 例外でなくても**バリデーション**を行う

- たとえば `assert` は **デバッグビルドで無効**になる可能性があります。  
- 代わりに明示的に検証し、失敗時は `ValueError` などを投げるべきです。

```python
def set_age(age):
    if not isinstance(age, int) or age < 0:
        raise ValueError("age must be a non‑negative integer")
    ...
```

---

## 7. 例外は **“失敗時の処理”** に留め、ロジックを例外で分岐させない

```python
# ❌ 例外でループ制御
try:
    while True:
        item = get_next()
        process(item)
except StopIteration:
    pass
```

- `StopIteration` は**イテレータ**の内部で使用すべきで、外部ロジックで捕捉して制御フローに利用するのは可読性が低下します。  
- 代わりに `for item in iterable:` のように **Pythonic** な構文を使うべきです。

---

## 8. 実践例：小規模 API クライアント

```python
import requests
import logging

log = logging.getLogger(__name__)

class APIError(RuntimeError):
    """外部 API から返却されたエラー"""

    def __init__(self, status, msg):
        self.status = status
        super().__init__(f"API error {status}: {msg}")

def get_user(user_id: int) -> dict:
    url = f"https://api.example.com/users/{user_id}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.Timeout:
        log.warning("Timeout when accessing %s", url)
        raise
    except requests.HTTPError as exc:
        log.error("HTTP error %s for %s", exc.response.status_code, url)
        raise APIError(exc.response.status_code, exc.response.text) from exc

    try:
        data = resp.json()
    except ValueError:
        log.error("Invalid JSON from %s", url)
        raise APIError(resp.status_code, "Invalid JSON") from None

    if "error" in data:
        log.error("API returned error: %s", data["error"])
        raise APIError(resp.status_code, data["error"])

    return data
```

- **timeout**・**HTTP status**・**JSON parse**・**API レスポンス**の 4 つの失敗パターンを個別に処理。  
- 失敗時に**原因チェーン**を保持しつつ、呼び出し側へは `APIError` を投げる。

---

## まとめ

| ポイント | 実装時にチェックすべきこと |
|----------|-----------------------------|
| カスタム例外 | 伝える情報を具体化、継承階層を整理 |
| 例外捕捉 | 予想される例外だけを列挙、`Exception` は避ける |
| `else`/`finally` | 成功時とリソース解放を分離 |
| 再投げ | `raise ... from e` で原因チェーンを保持 |
| ログ | `logger.exception()` でスタックトレースを残す |
| バリデーション | 明示的に例外を投げる、`assert` は避ける |
| 例外で制御しない | Pythonic ループ・条件分岐を優先 |

例外処理は「エラーを捕まえる」だけでなく、**コードの可読性**と**メンテナンス性**を高めるための手段です。  
上記のベストプラクティスをプロジェクトに取り入れ、エラーが発生した際に即座に原因を特定できる堅牢なシステムを構築しましょう。