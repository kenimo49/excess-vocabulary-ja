# Pythonの例外処理のベストプラクティス  

Pythonの例外処理は「失敗を黙って無視する」よりも「失敗を明示的に扱う」ことが望ましい設計哲学に基づいています。本記事では、実務で役立つベストプラクティスをコード例とともに解説します。  

---

## 1. 基本的な構文  
```python
try:
    # 失敗する可能性がある処理
    result = int(input("数値を入力: "))
except ValueError as e:
    # 具体的な例外を捕捉して再試行などを行う
    print("入力が不正です:", e)
else:
    # 例外が発生しなかったときのみ実行
    print("結果:", result)
finally:
    # 例外の有無に関係なく必ず実行
    print("処理を終了しました")
```
* **try‑except** でエラーを捕捉  
* **except *Exception* as e** は汎用的だが、可能な限り具体的に  
* **else** は例外が発生しなかった時に実行  
* **finally** はリソース解放などに使用  

---

## 2. 例外の選択と具体化  

1. **適切な標準例外を使う**  
   * `FileNotFoundError`, `PermissionError`, `ValueError`, `IndexError` など  
   * 例外名が原因を示してくれるので、デバッグが楽になる。  

2. **汎用的な `except Exception` は最小限に**  
   * 何が起きたか分からないと、意図しない例外を隠してしまう。  
   * デバッグの根源が失われるリスクがある。  

3. **カスタム例外を定義して意味を付与**  
   ```python
   class InvalidConfigurationError(RuntimeError):
       """設定ファイルが無効な場合に発生"""
   ```
   * ライブラリ利用者に対して直感的なエラーメッセージを提供。  

---

## 3. 例外の再送出（リロウ）  

例外を捕捉したら、**処理できない場合は再送出**。  
```python
try:
    open_file(path)
except FileNotFoundError:
    # ログを残して再送出
    logger.error("ファイルが見つかりません: %s", path)
    raise  # これで呼び出し側へ例外を伝搬
```
* `raise` だけで再送出するとスタックトレースが失われるので、  
  * `raise e` で元の例外を保持  
  * `raise Exception("追加情報") from e` でチェーンできる  

---

## 4. finally とリソース管理  

`finally` で必ずリソースを解放するのは古典的手法だが、Python 3.5+ では **コンテキストマネージャ** がより洗練されたパターン。  

```python
with open("log.txt", "a") as f:
    f.write("ログを書き込み\n")
```

`with` は内部で `__enter__` / `__exit__` を呼び出し、例外が起きても必ず `__exit__` が実行される。  
* 例外の伝搬は自動で行われる  
* `finally` よりも可読性が高い  

---

## 5. ロギングと例外  

例外発生時に **ログ** を残すことは、後から問題を追跡する際に不可欠。  

```python
import logging

logger = logging.getLogger(__name__)

try:
    process_data()
except Exception as e:
    logger.exception("データ処理中にエラーが発生しました")
    raise
```

`logger.exception()` は自動的にスタックトレースを出力し、デバッグ情報が揃う。  

---

## 6. 例外処理のテスト  

1. **pytestの `raises` ユーティリティ**  
   ```python
   from pytest import raises

   def test_invalid_input():
       with raises(ValueError):
           int("abc")
   ```
2. **例外メッセージを確認**  
   ```python
   with raises(ValueError) as excinfo:
       int("abc")
   assert "invalid literal" in str(excinfo.value)
   ```
3. **Mock を使って外部依存を模擬**  
   * ファイルI/O、ネットワーク、データベースの失敗を再現できる  

---

## 7. まとめ  

| ベストプラクティス | 目的 |
|---------------------|------|
| **具体的な例外を捕捉** | デバッグ容易 |
| **except Exception を極力避ける** | 隠れたエラー防止 |
| **finally より `with` を活用** | リソース解放の安全性 |
| **例外を再送出** | 失われた情報を保持 |
| **ロギングで詳細を残す** | 問題追跡 |
| **テストで例外を検証** | コード品質向上 |

Python の例外は「エラーを黙って無視するよりも、発生した事象を正しく伝える」設計哲学に根ざしています。上記のパターンを日常的に取り入れることで、バグの発見・修正が速く、保守性の高いコードを書けます。  

ぜひ、あなたのプロジェクトで試してみてください。 Happy coding! 🚀  