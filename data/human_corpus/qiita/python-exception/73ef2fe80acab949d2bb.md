# はじめに
この記事はNEアドベントカレンダーの14日目の記事です。

会社の懇親会でブロックチェーンについての話題で盛り上がって、最低限ブロックチェーンとはなにかを理解しておこうかな。という気運が高まっています。(なにをいまさら... ではあるんですが)

その過程でP2Pという通信形式が出てきたのでそれをとりあえず触って理解してみようというお話しです。

# P2P　(Peer to Peer)
P2Pは、複数のコンピュータ同士が直接通信する通信方式です。
![P2P型ネットワーク](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/065c4ebe-3c9e-b085-cd5d-74d00ae61925.png)

一方で、多くのWebサービスのように、サーバとそれに接続するクライアントがある通信方式をクライアント・サーバ方式と言います。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/edb51f8c-e45f-0643-fc92-6a788fe15bd4.png)
[Peer to Peer|Wikipedia](https://ja.wikipedia.org/wiki/Peer_to_Peer)

つまり、P2Pでは１台のコンピュータがサーバにもクライアントにもなるということです。
一時期騒がれたファイル共有ソフトやLINEのようなIP電話などで採用されています。

> P2PはSNSアプリ「LINE」で利用されています。LINEというと友達や家族との間で写真や動画の共有ができますが、その共有の仕組みにP2P技術が使われています。
P2Pで共有されているため、大規模なサーバーが不要でコストがかからないことも、LINEアプリが無料で使える要因の一つなっています。
https://www.lrm.jp/security_magazine/about_p2p/

先ほど冒頭で少し触れたブロックチェーンもこのP2Pを使って、各コンピュータに他のコンピュータと同じ情報(ブロックチェーン)を分散して保持しているようです。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/a7b16899-ed42-f366-6c0c-e1a911d269c7.png)
[ブロックチェーンの仕組み|NTTData](https://www.nttdata.com/jp/ja/services/blockchain/002/)

# 実装はどうなってるのか？
P2P自体はあくまで端末同士が直接通信するだけのことを指しているので、お互いサーバであり、クライアントであるという状態を実現すればいいはずです。

ネットワークの話まで拡張すると理解が追いつかなくなるので、(どうやって接続相手を見つけるのか、等)今回は、ソケット通信を用いて、ローカル環境に建てたサーバ同士でやりとりをすることを考えます。

## ソケット通信
ソケット通信に関しては、この記事がわかりやすかったです。
[今更ながらソケット通信に入門する（Pythonによる実装例付き）](https://qiita.com/t_katsumura/items/a83431671a41d9b6358f)

ソケットとは、ひとことで説明すると、アプリケーションを通じてコンピュータ同士が通信するときに使う通信の口のことです。
Webでよく使う、HTTPSやFTPなどの「アプリケーション層」の1つ下のレイヤーである、「トランスポート層」のレベルのTCPやUDPの通信がソケット通信です。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/ec2ab466-7011-2977-5713-99f2ac0bcec6.png)
[TCP/IPとは？通信プロトコルの階層モデルを図解で解説
](https://www.itmanage.co.jp/column/tcp-ip-protocol/)

HTTPはリクエストが処理されると接続が切断されてしまいますが、ソケット通信では一度疎通すれば通信状態を維持し続けるので、リアルタイムでのやりとりに使われます。
[Pythonでp2p通信対戦を行うゲームの基盤作った](https://qiita.com/hayama17/items/5b1291d111e43edcbdd5)

# Pythonでソケット通信を使ってみる
## サーバとクライアントを立てる。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/3a30014e-d6ab-b1f8-8e2d-2633f53449bc.png)
[今更ながらソケット通信に入門する（Pythonによる実装例付き）](https://qiita.com/t_katsumura/items/a83431671a41d9b6358f)より。

[PythonソケットによるTCP通信入門](https://nayutari.com/python-socket)
ここら辺の記事を参考にしながら、サーバとクライアントを構築しました。

といっても上記のイラスト通り、サーバとクライアントで順番に処理を実装していくだけなのでシンプルです。
今回は、curlからリクエストを送ったら、それをきっかけにサーバAとサーバBが交互に数をカウントしていく処理を考えます。

まずはじめに、シンプルなサーバを立ててcurlでリクエストを投げてみようと思います。
```python:server.py

import sys
import json
import socket
import time

IP_ADDR = "127.0.0.1"

class Server:
    def __init__(self, ip_addr, port):
        self.ip_addr = ip_addr
        self.port = port
        # TCPで接続
        self.sock = socket.socket(socket.AF_INET)
        self.sock.bind((self.ip_addr, self.port))
        self.sock.listen()
    
    def start(self):
        sock_cl, addr = self.sock.accept()
        self.recv_client(sock_cl, addr)
    
    def close(self):
        self.sock.close()
    
    def recv_client(self, sock, addr):
        while True:
            try:
                data = sock.recv(1024)
                # レスポンスが見やすいように
                for d in data.decode('utf-8').split('\n'):
                    print(d)
                if data == b"":
                    break
                post_params = self.get_post_data(data)
                # とりあえず送られてきたJSON文字列を返す
                sock.send(self.get_json_data(post_params).encode('utf-8'))
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except ConnectionResetError:
                break
            except OSError:
                break
        return

    def get_post_data(self, data):
        data_str = data.decode('utf-8')
        # POSTパラメータのみ取り出す
        post_params = data_str.split('\n')[-1]
        post_params = json.loads(post_params)
        if (type(post_params) is not dict):
            post_params = json.loads(post_params)
        return post_params

    def get_json_data(self, data):
        return json.dumps(data)

if __name__ == '__main__':
    port = sys.argv[1]
    server = Server(IP_ADDR, int(port))  
    server.start()

```

ここで立てたサーバに対して、以下のように適当にJSON付きのPOSTリクエストを送ると、
```
curl --verbose -H "Content-Type: application/json" -d '{"command": "count", "value": 20}' localhost:8080
```

以下のようなPOSTリクエストがサーバに届いていることを確認できます。今回はTCPで接続しているので、HTTPのリクエストそのものです。
```
POST / HTTP/1.1
Host: localhost:8080
User-Agent: curl/7.64.1
Accept: */*
Content-Type: application/json
Content-Length: 33

{"command": "count", "value": 20}

```

このサーバからのレスポンスは送られたJSONになっていることが確認できます。(--verboseをつけてリクエストヘッダーも出している)

```
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 8080 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8080 (#0)
> POST / HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.64.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 33
>
* upload completely sent off: 33 out of 33 bytes
* Closing connection 0
{"command": "count", "value": 20}
```

> class socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)
アドレスファミリー、ソケットタイプ、プロトコル番号を指定してソケットを作成します。アドレスファミリーには AF_INET (デフォルト値), AF_INET6, AF_UNIX, AF_CAN, AF_PACKET, AF_RDS を指定することができます。ソケットタイプには SOCK_STREAM (デフォルト値), SOCK_DGRAM, SOCK_RAW または他の SOCK_ 定数の何れかを指定します。プロトコル番号は通常省略するか、または0を指定しますが、アドレスファミリーに AF_CAN を指定した場合は、プロトコル番号には const:CAN_RAW, CAN_BCM, CAN_ISOTP, CAN_J1939 のいずれかを指定すべきです。
[sockets](https://docs.python.org/ja/3/library/socket.html#creating-sockets)

TCPと明示的に指定はしてませんが、デフォルトでSOCK_STREAMが指定されていてこれがTCPに該当するので、AF_INET(IPV4の意味)だけの指定で問題なく動作しているようです。

> ソケット・タイプ
説明
SOCK_DGRAM
その信頼性が保証されていない、固定最大長のコネクションレス・メッセージ であるデータグラムを提供します。データグラムでは、破壊、順序が狂った受信、紛失、または複数回の 送達が起こる場合があります。このタイプは、AF_INET、AF_INET6、および AF_UNIX ドメインでサポートされています。
SOCK_RAW
内部プロトコル (IP および ICMP など) のインターフェース を提供します。このタイプは AF_INET および AF_INET6 ドメインで サポートされています。 このタイプを使用するためには、スーパーユーザーでなければなりません。
SOCK_STREAM
信頼性があり接続指向であるシーケンス化された両方向バイト・ストリームを提供します。アウト・オブ・バンドのデータのメカニズムがサポートされます。このタイプは、AF_INET、AF_INET6、および AF_UNIX ドメインでサポートされています。

[socket() - ソケットの作成](https://www.ibm.com/docs/ja/zos/2.3.0?topic=functions-socket-create-socket)

ソケット通信のクライアントも実装しておきます。
こちらもシンプルで、JSON形式で入力するとそれをそのままサーバ側に表示するものです。

```python:client.py

import sys,json
import socket

IP_ADDR = "127.0.0.1"

class Client:
    def __init__(self, ip_addr, port):
        self.sock = socket.socket(socket.AF_INET)
        self.sock.connect((ip_addr, port))
    
    def send(self, message):
        try:
            self.sock.send(json.dumps(message).encode('utf-8'))
        except ConnectionResetError as e:
            raise Exception(e)

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

if __name__ == '__main__':
    port = sys.argv[1]
    print(f"{IP_ADDR},{port}")
    while True:
        client = Client(IP_ADDR, int(port))
        data = input("> ")
        if data == 'exit':
            break
        try:
            client.send(data)
            client.close()
        except Exception:
            client.close()
            break
```

以下のように入力すると、それがそのままprintされることが確認できます。
```sh:client

127.0.0.1,8080
> {"message":"OK"}
> 
```

```sh:server

"{\"message\":\"OK\"}"
```

## サーバに命令を送って、命令を実行させてみる。
ここまでで以下のことを確認しました。
* curlでサーバへリクエストが送れること
* client.pyからserver.pyへリクエストが送れて処理できること

ここで、POSTするJSON文字列を解釈して処理を変えるということをやってみます。
といっても、送るのは先ほどのリクエストで、1~20までの数を数えなさいということを指示してみます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/2f99856e-3183-c766-de5a-b7c479a1f5f4.png)


```
curl -H "Content-Type: application/json" -d '{"command": "count", "value": 20}' localhost:8080
```

そのために、JSONを読み取って、commandに対応したメソッドを実行し、他のサーバにリクエストを投げるクラスを実装します。つまり、"count"コマンドを受け取ると、以下のようなリクエストパラメータを生成し、別のサーバにリクエストを投げるようにします。
```
{'command':'count_up', 'value':{'count':1, 'end_count':end_count}}
```

また、"count_up"というコマンドは、送られてきたJSONのcountを+1して返すということを命じるコマンドで、これを実行すると、end_countに指定された数になるまでサーバ同士でカウントアップします。
```
{'command':'count_up', 'value': {'count':count, 'end_count':value['end_count']}}
```

```python:syncdata.py
import json
import ast
from client import Client

class Syncdata:
    def __init__(self, ip_addr, port):
        self.ip_addr = ip_addr
        self.port = port

    def send(self, data):
        if data == {}:
            return
        client = Client(self.ip_addr, self.port)
        print(data['value'])
        client.send(data)
        client.close()

    def execute(self, args):
        if 'command' not in args.keys() and 'value' not in args.keys():
            return {'command':{}, 'message':{}}
        command = args['command']
        value = args['value']
        return getattr(self, command)(value)

    def count(self, end_count):
        response = {'result':'success', 'message':'count start'}
        command = {'command':'count_up', 'value':{'count':1, 'end_count':end_count}}
        return {'command':command ,'message':response}

    def count_up(self, value):
        if value['count'] >= value['end_count']:
            return {'command':{}, 'message':{}}
        count = int(value['count'])+1
        command = {'command':'count_up', 'value': {'count':count, 'end_count':value['end_count']}}
        return {'command':command, 'message':{}}

    def fizzbuzz(self, end_count):
        response = {'result':'success', 'message':'fizzbuzz start'}
        command = {'command':'fizzbuzz_up', 'value':{'count':1, 'fizzbuzz':1, 'end_count':end_count}}
        return {'command':command ,'message':response}

    def fizzbuzz_up(self, value):
        if value['count'] >= value['end_count']:
            return {'command':{}, 'message':{}}
        count = int(value['count'])+1
        fizzbuzz_str = 'fizz' if count%3 == 0 else ''
        fizzbuzz_str += 'buzz' if count%5 == 0 else ''
        fizzbuzz_str += str(count) if fizzbuzz_str == '' else ''
        command = {'command':'fizzbuzz_up', 'value': {'count': count, 'fizzbuzz':fizzbuzz_str, 'end_count':value['end_count']}}
        return {'command':command, 'message':{}}

```

この処理を呼び出すようにserver.pyに手を加えたものが以下のコードです。

```python:server.py

import sys
import json
import socket
import threading
import time
from syncdata import Syncdata

IP_ADDR = "127.0.0.1"

class Server:
    def __init__(self, ip_addr, port):
        self.sock = socket.socket(socket.AF_INET)
        self.ip_addr = ip_addr
        self.port = port
        self.invoke_instance = None
        self.sock.bind((self.ip_addr, self.port))
        self.sock.listen()

    def set_invoke_instance(self, instance):
        self.invoke_instance = instance
    
    def start(self):
        sock_cl, addr = self.sock.accept()
        thread = threading.Thread(target=self.recv_client, args=(sock_cl, addr))
        thread.start()
        thread.join()
    
    def close(self):
        self.sock.close()

    def get_post_data(self, data):
        data_str = data.decode('utf-8')
        # POSTパラメータのみ取り出す
        post_params = data_str.split('\n')[-1]
        post_params = json.loads(post_params)
        if (type(post_params) is not dict):
            post_params = json.loads(post_params)
        return post_params

    def get_json_data(self, data):
        return json.dumps(data)
    
    def recv_client(self, sock, addr):
        while True:
            try:
                data = sock.recv(1024)
                if data == b"":
                    break
                post_params = self.get_post_data(data)
                # なにかするやつ。
                self.invoke(post_params, sock)
                # とりあえず結果を返す
                sock.send(self.get_json_data(post_params).encode('utf-8'))
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except ConnectionResetError:
                break
            except OSError:
                break
        return

    def invoke(self, args:dict, sock):
        # 2サーバ間でおしゃべりしてその結果(command)を返す
        response = self.invoke_instance.execute(args)
        command = response['command']
        message = response['message']
        self.invoke_instance.send(command)
        # 呼び出し元にレスポンスを返す
        if message is not {}:
            sock.send(self.get_json_data(message).encode('utf-8'))

if __name__ == '__main__':
    port = sys.argv[1]
    target_port = sys.argv[2]
    print(f"{IP_ADDR}, {port}")
    server = Server(IP_ADDR, int(port))
    server.set_invoke_instance(Syncdata(IP_ADDR, int(target_port)))  
    
    # 無限ループ防止のためのcount,この数よりも小さい接続数で済むようにする必要あり。
    count = 0
    while count < 100:
        try:      
            server.start()
            count += 1
        except Exception as e:
            time.sleep(5)
    server.close()

```

主な変更点はこちらの部分で、JSONを受け取って処理を動的に選択する処理を追加しています。
また、呼び出し元にちゃんとレスポンスを返す必要がある(curlでリクエストした時のみ)ときにレスポンスが返るようにしています。

```python

    def invoke(self, args:dict, sock):
        # 2サーバ間でおしゃべりしてその結果(command)を返す
        response = self.invoke_instance.execute(args)
        command = response['command']
        message = response['message']
        self.invoke_instance.send(command)
        # 呼び出し元にレスポンスを返す
        if message is not {}:
            sock.send(self.get_json_data(message).encode('utf-8'))
```

実際に、localhost:8080, localhost:8081でサーバを起動し、curlからlocalhost:8080にリクエストを投げてみると以下のようにレスポンスが返ってきて、数を数えられていることがわかります。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/b515f8a9-f426-4135-a628-85223a6bab6e.png)

curlからも以下のようなレスポンスが確認できました。
```
curl -H "Content-Type: application/json" -d '{"command": "count", "value": 30}' localhost:8080
{"result": "success", "message": "count start"}{"command": "count", "value": 30}
```

どうせなら、ということで、fizzbuzzもやらせてみましょう。(既に実装済みなのでコマンド指定だけで動きます)

```
curl -H "Content-Type: application/json" -d '{"command": "fizzbuzz", "value": 30}' localhost:8080
{"result": "success", "message": "fizzbuzz start"}{"command": "fizzbuzz", "value": 30}
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/71289/76f8259b-09c3-dac9-cb50-abfca4d70d8c.png)

# まとめ
ブロックチェーンで使われているというP2Pという通信方式を少しでも理解するために、ソケット通信を試してみました。
クライアントからサーバにリクエストしてレスポンスが返ってくるクライアント・サーバ方式に慣れている私からするとなかなかとっつきにくい概念でした。
ソケット通信で立てたサーバにcurlでリクエストしたときにHTTPリクエストが確認できたので、HTTP通信の正体はソケット通信のTCPでの連携であるということがはっきりしたのが面白かったかもしれません。
また、簡易ではありますがサーバを構築しているときに、コネクションが切れてしまったり、例外で処理が落ちた時にコネクションが占有されたままですぐには再実行ができない、サーバ間での通信で無限ループを作ってしまい、コネクション使い切って処理が落ちるなど、ここら辺の辛みも少しだけ理解できたような気がします...

```
y", line 16, in __init__
    self.sock.bind((self.ip_addr, self.port))
OSError: [Errno 48] Address already in use
```

実際のブロックチェーンでは、ブロック追加のリクエストが入った時に、そのリクエストを近くのノードに伝搬していき、ノード同士で情報を共有するということをやっているようなので、これで少し理解が深まったのかな、と思います。(どのノードにつなぐことができるのか、などはネットワークのしくみの勉強が必要なんだろうな...とは思いますが)
全然普段の業務には関係ないことですが、知っておいて損はないのかな、と思いました。



