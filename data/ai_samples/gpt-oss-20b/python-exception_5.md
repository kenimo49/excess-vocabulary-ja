# Pythonの例外処理のベストプラクティス

Python で安全にコードを書き、予期せぬエラーを最小限に抑えるために、例外処理は欠かせません。  
ここでは、実務で使えるベストプラクティスをまとめます。  

---

## 1. 例外を“捕まえる”目的を明確にする  

- **エラーを隠すのではなく、原因を把握して対処する**  
  - `print()` で止めるのではなく、**ログ**に stack‑trace を残す  
- **リソース解放は必ず実行**  
  - `finally` ブロックや **context manager** (`with` 句) を利用する  

---

## 2. 具体的な例外を捕まえる

```python
try:
    value = int(input("整数を入力: "))
except ValueError as e:
    logging.error("入力が整数ではありません: %s", e)
```

- `except:` や `except Exception:` は「何が起きたか」分からないので避ける  
- 標準例外を細かく捕まえることで、適切なリカバリができる  

---

## 3. `else` を活用する  

```python
try:
    result = risky_operation()
except SpecificError:
    handle_error()
else:
    # 成功した場合のみ実行
    process(result)
```

- `else` に成功時の処理を書けば、try‑except の可読性が上がる  
- `finally` はリソース解放専用に使い、実行順序が保証される  

---

## 4. 例外を再スローする際は `from` を使う  

```python
try:
    f = open("data.txt")
except FileNotFoundError as e:
    raise RuntimeError("必要なファイルが見つかりません") from e
```

- `from e` により元の原因を保持しつつ、意味のある例外に変換できる  
- `raise ... from None` でコンテキストを消したい場合は注意して使用  

---

## 5. コンテキストマネージャでリソース管理

```python
with open("log.txt", "a") as f:
    f.write("エラー発生\n")
```

- `finally` を自分で書くより、`with` で安全にリソースが解放される  
- 標準ライブラリはほとんどがコンテキストマネージャに対応している  

---

## 6. カスタム例外を定義する  

```python
class DataValidationError(Exception):
    """入力データのバリデーション失敗時に投げる例外"""

def validate(data):
    if not isinstance(data, int):
        raise DataValidationError("整数が必要です")
```

- **意味を持つ例外名** によって呼び出し側がエラー種別を把握できる  
- 例外階層を整理し、汎用 `Exception` で包み込むと安全  

---

## 7. ロギングの活用

- `logging.exception()` は例外の stack‑trace を自動で出力  
- 開発環境と本番環境でログレベルを切り替えて、詳細情報を隠す  

```python
except Exception:
    logging.exception("予期しないエラー")
    raise
```

---

## 8. 実践的なチェックリスト

| 目的 | チェック項目 |
|------|--------------|
| エラーを把握 | `except SpecificError as e:` を使う |
| リソース確実解放 | `finally` / `with` で管理 |
| 意味あるエラー | カスタム例外を定義 |
| コンテキスト保全 | `raise ... from e` |
| ログ管理 | `logging.exception()` を使う |

---

## まとめ

- **例外は“捕まえる”だけでなく、“理解する”こと** が重要  
- 具体例外、`else`、`finally`、`raise from`、コンテキストマネージャを駆使  
- ログとカスタム例外で可読性・保守性を向上  

エラーが発生しても、原因を速やかに特定し対処できるコードを書きましょう。