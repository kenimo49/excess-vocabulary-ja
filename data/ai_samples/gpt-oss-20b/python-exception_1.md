# Pythonの例外処理のベストプラクティス

エンジニアとして日常的に書くコードは「例外が起きても安全に動作する」ことが不可欠です。  
ここではPythonにおける例外処理の「やるべきこと」「やらない方がいいこと」をまとめ、実践的なサンプルを添えて解説します。

---

## 1. 基本原則

| ルール | 理由 |
|--------|------|
| **例外は可能な限り具体的に捕捉する** | 予期しないエラーを見逃さない。 |
| **`except Exception` のみで捕捉しない** | システムの致命的エラー（`SystemExit`, `KeyboardInterrupt` 等）を無視してしまう。 |
| **`except` のあとに `else` と `finally` を活用する** | 成功時の処理とリソース解放を明確に分離できる。 |
| **例外チェイニング (`raise ... from ...`) を使う** | 原因を追跡しやすくなる。 |
| **独自例外を定義する** | エラーの意味を明確化し、呼び出し側で分岐しやすくなる。 |
| **ロギングで詳細情報を残す** | デバッグと運用の両面で役立つ。 |

---

## 2. 具体的なベストプラクティス

### 2-1. 明示的な例外を捕捉

```python
try:
    result = int(user_input)            # 文字列→整数変換
except ValueError as e:                 # 失敗時は ValueError
    logger.error("入力が整数ではありません: %s", user_input)
    raise
```

`except Exception:` で全てを捕捉してしまうと、`KeyboardInterrupt` など正常に停止させるべき例外も捕捉されてしまう恐れがあります。

### 2-2. `else` と `finally`

```python
try:
    with open('data.txt', 'r') as f:
        data = f.read()
except FileNotFoundError:
    logger.warning('ファイルが存在しません')
else:
    logger.info('ファイル読み込み成功')
finally:
    logger.debug('処理終了')
```

- **`else`** は例外が発生しなかった場合にのみ実行される。
- **`finally`** は例外の有無に関わらず実行され、リソース解放やクリーンアップに使う。

### 2-3. 例外チェイニング

```python
def read_config(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"設定ファイルの構文エラー: {path}") from e
```

`from e` により、元の例外 (`json.JSONDecodeError`) の情報が保持され、スタックトレースが分かりやすくなる。

### 2-4. 独自例外の定義

```python
class AppError(Exception):
    """アプリケーションで発生する汎用エラー"""

class InvalidInputError(AppError):
    """ユーザー入力が不正"""

# 呼び出し側
try:
    process(user_input)
except InvalidInputError as e:
    notify_user(str(e))
```

独自例外は `Exception` のサブクラスであれば、`except Exception` で捕捉できるが、意味を持たせることでエラーハンドリングが明確になる。

### 2-5. ロギングと例外の再スロー

```python
try:
    db.execute(query)
except sqlite3.DatabaseError as e:
    logger.exception("データベース操作失敗")
    raise
```

`logger.exception` は例外情報を含むログを出力し、`raise` で元の例外を再スローして呼び出し側に伝える。

---

## 3. まとめ

- 例外は **具体的に捕捉** し、`except Exception` で汎用捕捉は最小限に。
- `else` と `finally` を使って処理フローを整理。
- **例外チェイニング** と **独自例外** でエラーの意味を明確化。
- **ロギング** を併用し、運用時のトラブルシューティングを容易に。

例外処理は「エラーを許容する」だけでなく、「エラーの原因を正確に把握し、必要に応じて安全に回復・停止させる」ための重要な仕組みです。  
上記のベストプラクティスを意識してコードを書けば、堅牢で保守しやすいPythonアプリケーションが実現できます。