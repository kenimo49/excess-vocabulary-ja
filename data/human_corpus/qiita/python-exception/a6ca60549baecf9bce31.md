## はじめに
例外処理の備忘録です💁
初心者です😅
間違えてる部分多々あると思います。
もし見つけた場合、ツッコミいただけると助かります🙇

## 🦁 結論 🦁
:::note info
押さえておくべき点
* 例外処理を使う理由はエラーが起きた原因を特定しやすいようにコンテキスト（様々な要因）を用意して、そのエラーに処理などを加えてエラー対応ができるようにするため
* 例外情報は基本、ロギングする
* 必要最小限のコードをtryブロックに含める
* tryブロック、exceptブロック、elseブロック、finallyブロックに分かれて処理する
* 
:::

:::note warn
タイミング
* 処理でエラーが発生しそうなコードの記述した際には使う。
:::

:::note alert
注意点
* exceptを多くしてしまいすぎると可読性が下がる
* ログもしっかり残すようにすることも大事
* Exceptionのエラーは全てのエラーの親要素的なとなるエラー
* Exceptionを捕捉することは、特定のエラータイプを区別せず、あらゆる例外をキャッチすることになる
* Exceptionはあまり使わない（具体的なエラーでないとエラーを拾えない）
* Python3以降はIOErrorとOSErrorは統合された。OSErrorで表示されることが多い。
:::

## 内容

## 基本構文
```python:sample.py
try:
    # 例外が発生する可能性のあるコード
except エラータイプ1 as e1:
    # エラータイプ1に対応する例外をキャッチして処理
except エラータイプ2 as e2:
    # エラータイプ2に対応する例外をキャッチして処理
else:
    # エラーが発生しなかった場合の処理
finally:
    # 最終的なクリーンアップコード
```
:::note info
基本構文で押さえておくべき点
* tryブロックはエラーが発生する可能性があるコードが配置
* exceptブロックはtry ブロック内でエラーが発生した場合、対応するエラータイプを指定して except ブロックでエラーをキャッチし、適切な処理を行う
* 2つ目のエラーが予測できる場合、exceptブロックを2つ目を書く
* elseブロックはtry ブロック内でエラーが発生しなかった場合に実行されるコード（処理が成功など）
* finallyブロックはtry ブロック内でエラーの有無に関係なく、最終的に実行されるクリーンアップコードを記述する
* 必要最小限のコードをtryブロックに含める
:::

### 必要最小限のコードをtryブロックに含める:
#### tryブロックには、例外が発生する可能性のあるコードのみを含める。
#### これにより、どの部分のコードが問題を引き起こしたのかを特定しやすくなる。

### finallyブロックを使用してリソースをクリーンアップする:
#### ファイル操作やネットワーク接続など、開放が必要なリソースを扱う場合には、finallyブロックを使用して確実にリソースを解放する。
```python:sample.py
try:
    file = open("some_file.txt")
    # ファイル操作
finally:
    file.close()
```

## よくあるエラー
1.	NameError: 未定義の変数や関数を使用しようとした場合に発生
```python:sample.py
try:
    print(未定義の変数)
except NameError as e:
    print(f"NameErrorが発生しました: {e}")
```

2.	TypeError: 型に関する不正な操作を行った場合に発生
```python:sample.py
try:
    '2' + 2
except TypeError as e:
    print(f"TypeErrorが発生しました: {e}")
```

3.	ValueError: 引数として渡された値が不適切な場合に発生
```python:sample.py
try:
    int('文字列')
except ValueError as e:
    print(f"ValueErrorが発生しました: {e}")
```

4.	FileNotFoundError: 指定したファイルが見つからない場合に発生
```python:sample.py
try:
    with open('存在しないファイル.txt', 'r') as file:
        read_data = file.read()
except FileNotFoundError as e:
    print(f"FileNotFoundErrorが発生しました: {e}")
```

5.	ZeroDivisionError: 0で割り算をしようとした場合に発生
あくまで0だけ。noneはTypeErrorになる。
```python:sample.py
try:
    division = 1 / 0
except ZeroDivisionError as e:
    print(f"ZeroDivisionErrorが発生しました: {e}")
```

6.	IndexError: シーケンスの範囲外のインデックスを参照しようとした場合に発生
```python:sample.py
try:
    リスト = [1, 2, 3]
    print(リスト[3])
except IndexError as e:
    print(f"IndexErrorが発生しました: {e}")
```

7.	KeyError: 辞書に存在しないキーを参照しようとした場合に発生
```python:sample.py
try:
    辞書 = {'key1': 'value1', 'key2': 'value2'}
    print(辞書['存在しないキー'])
except KeyError as e:
    print(f"KeyErrorが発生しました: {e}")
```

8.	ModuleNotFoundError: 存在しないモジュールをインポートしようとした場合に発生
```python:sample.py
try:
    import 存在しないモジュール
except ModuleNotFoundError as e:
    print(f"ModuleNotFoundErrorが発生しました: {e}")
```

9.	AttributeError: 存在しない属性を持つオブジェクトにアクセスしようとした場合に発生
```python:sample.py
try:
    class クラス:
        pass
    インスタンス = クラス()
    インスタンス.存在しないメソッド()
except AttributeError as e:
    print(f"AttributeErrorが発生しました: {e}")
```

10.	IOError: 入出力操作（ファイルの読み書きなど）でエラーが発生した場合。
こちらは書き込みの権限がなかったためIOError。
ハードディスクへのアクセスができない
ネットワーク経由のファイルアクセスができない時もある
```python:sample.py
try:
    with open('ファイルパス', 'w') as file:
        file.write('何かのテキスト')
except PermissionError as e:
    print(f"アクセス権限エラーが発生しました: {e}")
except IOError as e:
    print(f"入出力エラーが発生しました: {e}")
```

11.	OSError: オペレーティングシステムレベルでのエラー、例えばサーバーからファイルのやり取りでのネットワークエラーなど。（他のエラーと混同することもある）
※Python3以降はIOErrorとOSErrorは統合された。OSErrorで表示されることが多い。
```python:sample.py
try:
    # サーバーからファイルを取得する処理
except OSError as e:
    print(f"OSエラーが発生しました: {e}")
```

12.	RuntimeError: 他のカテゴリには当てはまらない一般的な実行時エラー。
```python:sample.py
try:
    raise RuntimeError('意図的に発生させたランタイムエラー')
except RuntimeError as e:
    print(f"RuntimeErrorが発生しました: {e}")
```

13.	TimeoutError:一般的にシステム関連の操作が指定された時間内に完了しなかった場合に発生します。例えば、ネットワーク操作やファイルの読み書きなどがタイムアウトする場合にこのエラーが発生
```python:sample.py
try:
    # 長時間実行される処理
except TimeoutError as e:
    print(f"TimeoutErrorが発生しました: {e}")
```
