ある日、あるプロジェクトの`docker-compose build`が通らなかった。

```
$ docker-compose build
Building db
[+] Building 3.4s (5/6)                                                                                                                                                                                                                  
 => [internal] load build definition from Dockerfile                                                                                                                                                                                0.1s
 => => transferring dockerfile: 37B                                                                                                                                                                                                 0.0s
 => [internal] load .dockerignore                                                                                                                                                                                                   0.0s
 => => transferring context: 2B                                                                                                                                                                                                     0.0s
 => [internal] load metadata for docker.io/library/mysql:5.7                                                                                                                                                                        2.9s
 => CACHED [1/3] FROM docker.io/library/mysql:5.7@sha256:94fe67...........................................................                                                                                                          0.0s
 => ERROR [2/3] RUN apt-get update &&     apt-get install -y locales &&     rm -rf /var/lib/apt/lists/* &&     echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen &&     locale-gen ja_JP.UTF-8                                             0.4s
------
 > [2/3] RUN apt-get update &&     apt-get install -y locales &&     rm -rf /var/lib/apt/lists/* &&     echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen &&     locale-gen ja_JP.UTF-8:
#5 0.334 /bin/sh: apt-get: command not found
------
executor failed running [/bin/sh -c apt-get update &&     apt-get install -y locales &&     rm -rf /var/lib/apt/lists/* &&     echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen &&     locale-gen ja_JP.UTF-8]: exit code: 127
ERROR: Service 'db' failed to build
```

`ERROR: Service 'db' failed to build`とあったので、docker-compose.ymlでdbのところが何か間違えているのかと思いましたが、ここではなくて。

```docker:docker-compose.yml
version: '2'
services:
  db:
    build: ./db
    environment:
      - MYSQL_ROOT_PASSWORD=pass
      - MYSQL_DATABASE=myapp
      - MYSQL_USER=user
      - MYSQL_PASSWORD=pass
    ports:
      - 3308:3306
    volumes:
      - sql-data:/var/lib/mysql
```

`apt-get: command not found`と出ている方に注目すべきだった模様。
apt-getとは、パッケージの操作、管理を行うLinuxnコマンド。僕はMacOSでbrewを使ってアプリなどをインストールしたりしているが、あれのLinuxバージョンみたいなものらしい。

> apt-getコマンドは、Debian系のディストリビューション（DebianやUbuntu）のパッケージ管理システムであるAPT（Advanced Package Tool）ライブラリを利用してパッケージを操作・管理するコマンドです。
Linux入門「apt-get - パッケージの操作・管理 - Linuxコマンド」
出典 https://webkaru.net/linux/apt-get-command/


Dockerfileを見てみる。

```docker:db/Dockerfile
# Dockerfile_MySQL
FROM mysql:5.7

# Set debian default locale to ja_JP.UTF-8
RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen ja_JP.UTF-8
ENV LC_ALL ja_JP.UTF-8
```

## 結論
DockerfileのFROMのとこに、`-debian`を付けてあげればいい。

```docker:db/Dockerfile
# Dockerfile_MySQL
FROM mysql:5.7-debian

# Set debian default locale to ja_JP.UTF-8
RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen ja_JP.UTF-8
ENV LC_ALL ja_JP.UTF-8
```

参考にしたのはこちら。

https://stackoverflow.com/questions/72946649/dockerfile-running-from-mysql-cannot-access-apt-get

このstackoverflowによると、Oracle社が2010年にMySQLを買収してから、彼らはMySQLのデフォルトのパッケージをDebianからOracleに切り替えているために、齟齬が起きてうまくいかないことがあるらしい。上記のように`debian`と明示してあげるとうまくいった。

## 最後に

@Y_uuu　さんに助けられました！
