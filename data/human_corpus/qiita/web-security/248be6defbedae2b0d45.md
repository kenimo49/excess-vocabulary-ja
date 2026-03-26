# はじめに
こんにちは、株式会社シーエー・アドバンス技術統括本部の@syk_nakayamaです。
今回はセキュリティ診断時にハマった話をしようと思います。

某月某日の業務にて、Burp Suiteを使用しIntruderを実行しようとしたが、どうにもうまく回らない。
結果が全てエラーとなる。正常結果が返却される筈の場所もエラーとなる。
何か変だ、私の知らない改ざん検知に引っかかったのか？となり七転八倒。
原因判明まで時間を要してしまいました。

>Burp Suite (バープ スイート)は、PortSwigger Ltdが開発したJava アプリケーションである。
>Web アプリケーションのセキュリティや侵>入テストに使用されている。[1]　プロキシサーバ（Burp Proxy）、Webクローラ（Burp Spider）、侵入ツール（Burp Intruder）、脆弱性>スキャナ（Burp Scanner）、HTTPリピータ（Burp Repeater）などのツールから構成されている。
>Burp Proxyはアプリケーションの異常な動作を誘発し、バグや関連する脆弱性を特定することを目的として、不適合なデータを注入することが出来る。
>
>出典: フリー百科事典『ウィキペディア（Wikipedia）』
><a href="https://ja.wikipedia.org/wiki/Burp_Suite"> https://ja.wikipedia.org/wiki/Burp_Suite</a>

# なにが起きていたか
・ProxyタブからRepeaterへ設定、送信した場合は上手くいく
・Intruderを回すと、正常結果が返却されるべき箇所でもエラーとなる
・同じ箇所を改ざんしRepeaterで送信するとエラーとなる
・CSRF Tokenはない

# 原因
結論から言うと、原因はBurp SuiteのUserOption設定にありました。
文字化け対策としてUTF-8を設定していたのですが、該当箇所のリクエスト内にバイナリデータが含まれており、意図せずバイナリデータをUTF-8形式へ変換してしまい、結果リクエストに失敗するという動作になっていました。

Optionの箇所
![Burp001.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/666267/17987bb7-6aea-a86e-1f0b-2fb64179a057.png)

サンプルプロジェクトで動作を説明すると以下のようになります。

サンプルプロジェクトでは、
正常結果の場合、レスポンスのLocationヘッダが以下となります。
```
Location: https://myapp.localhost/merchant
```
不正データと判断された場合は、以下となります。
```
Location: https://myapp.localhost/merchant/service/create
```

ファイル名を改ざんしたリクエストを送信した場合、平文で見る限りなぜ不正データと判断されるのか分かりません。

改ざん箇所
正常値　　　：filename="10kb-01.jpg"
改ざん後の値：filename="10kb-02.jpg"

正常リクエスト
```
POST /merchant/service/create HTTP/1.1
Host: myapp.localhost
～省略～
------WebKitFormBoundaryWe0DIx0pmP9uuvI0
Content-Disposition: form-data; name="image"; filename="10kb-01.jpg"
Content-Type: image/jpeg

����
～省略～
```

正常レスポンス
```
HTTP/1.1 302 Found
～省略～
Location: https://myapp.localhost/merchant
～省略～
```

不正リクエスト
```
POST /merchant/service/create HTTP/1.1
Host: myapp.localhost
～省略～
------WebKitFormBoundaryWe0DIx0pmP9uuvI0
Content-Disposition: form-data; name="image"; filename="10kb-02.jpg"
Content-Type: image/jpeg

����
～省略～
```

不正レスポンス
```
HTTP/1.1 302 Found
～省略～
Location: https://myapp.localhost/merchant/service/create
～省略～
```

# 反省
結果を見ればなるほどと思うかもしれませんが、ハッシュ等で改ざんチェックされているのか？など色々疑ってしまい、苦労しました。
理由がない限り、Optionはデフォルト設定を利用した方がハマらないかもしれません。




