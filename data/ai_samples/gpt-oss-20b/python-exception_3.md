# Pythonの例外処理のベストプラクティス

## はじめに  
例外はバグを隠す恐れもあるため、適切に扱うことが品質向上の鍵です。この記事では、エンジニアが日常的に使える具体的なベストプラクティスを紹介します。

## 1. 具体的な例外を捕捉する  
```python
try:
    value = int(input("数値を入力: "))
except ValueError:          # 例外を限定
    print("数値以外が入力されました")
```
`except Exception:` のように汎用例外を捕捉すると、デバッグが難しくなります。必要な例外だけを指定しましょう。

## 2. 空の except はやめる  
```python
try:
    open("file.txt")
except:                     # ← 何が失敗したかわからない
    pass
```
空の except はバグを消すだけでなく、予期しない例外を隠してしまいます。何か処理を入れましょう（例：ログ出力）。

## 3. finally でリソースを解放  
```python
file = open("log.txt", "a")
try:
    file.write("ログを追加\n")
finally:
    file.close()            # 例外が起きても必ず実行
```
finally は例外の有無にかかわらず実行されるため、ファイルやネットワークなどのクリーンアップに最適です。

## 4. コンテキストマネージャでリソース管理  
Python では `with` 文が標準です。  
```python
with open("data.csv", "r") as f:
    for line in f:
        process(line)
```
内部で `__enter__` と `__exit__` が呼ばれ、例外時でも自動的にクローズされます。

## 5. 例外を再スローして上位層へ伝える  
```python
try:
    risky_operation()
except SpecificError as e:
    log_error(e)
    raise            # 同じ例外を再送信
```
必要なら `raise e` でスタックトレースを保ったまま再送信できます。

## 6. ログに traceback を残す  
```python
import logging, traceback
try:
    do_something()
except Exception as e:
    logging.error("エラーが発生: %s\n%s", e, traceback.format_exc())
```
開発・運用時に原因追跡がしやすくなります。

## 7. カスタム例外でドメインを明示  
```python
class InvalidUserError(Exception):
    """ユーザーが無効な状態です"""
```
プロジェクト特有の失敗を表す例外を定義することで、ハンドリングが明確になります。

## まとめ  
- **具体例外を捕捉**  
- **空の except を避ける**  
- **finally / with でリソース解放**  
- **例外再送信は traceback を残す**  
- **ログに traceback を出力**  
- **カスタム例外でドメインを表現**  

これらを守ることで、例外処理が安全かつ可読性の高いコードになります。エンジニアとして日々の開発に取り入れ、堅牢なアプリケーションを作りましょう。