AUTOSAR (AUTomotive Open System ARchitecture)
http://autosar.org

は、２０１９年以降は、毎年１１月に新しい標準を発行している。
今年も一般公開を始めた。

Explanation of ARA Applications in Rust, AUTOSAR 1079, R23-11, AP
https://qiita.com/kaizen_nagoya/items/3d3e3349e00a598a5718

参考文献のNo.13は、

[13] Rust analyzer 
https://rust-analyzer.github.io/

書いてあることをdocker, macOS(M2)で動作させてみる。bookが、本に書いてあること。その次のbashが自分の機材での動作。

<この項は書きかけです。順次追記します。>
This article is not completed. I will add some words in order.
# docker
```macOS:bash
$ docker run -it rust /bin/bash

# apt update; apt -y upgrade
# apt install vim
```

UbuntuにVSCodeをインストールする3つの方法
https://qiita.com/yoshiyasu1111/items/e21a77ed68b52cb5f7c8

```bash
# curl -L https://go.microsoft.com/fwlink/?LinkID=760868 -o vscode.deb
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100   162  100   162    0     0    376      0 --:--:-- --:--:-- --:--:--  1058
100 91.5M  100 91.5M    0     0  9543k      0  0:00:09  0:00:09 --:--:-- 10.1M
root@ffc652d1f3f8:/rust-analyzer# apt install ./vscode.deb
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Note, selecting 'code:amd64' instead of './vscode.deb'
Some packages could not be installed. This may mean that you have
requested an impossible situation or if you are using the unstable
distribution that some required packages have not yet been created
or been moved out of Incoming.
The following information may help to resolve the situation:

The following packages have unmet dependencies:
 code:amd64 : Depends: libasound2:amd64 (>= 1.0.17) but it is not installable
              Depends: libatk-bridge2.0-0:amd64 (>= 2.5.3) but it is not installable
              Depends: libatk1.0-0:amd64 (>= 2.2.0) but it is not installable
              Depends: libatspi2.0-0:amd64 (>= 2.9.90) but it is not installable
              Depends: libc6:amd64 (>= 2.14) but it is not installable
              Depends: libc6:amd64 (>= 2.16) but it is not installable
              Depends: libc6:amd64 (>= 2.17) but it is not installable
              Depends: libc6:amd64 (>= 2.2.5) but it is not installable
              Depends: libcairo2:amd64 (>= 1.6.0) but it is not installable
              Depends: libcurl3-gnutls:amd64 but it is not installable or
                       libcurl3-nss:amd64 but it is not installable or
                       libcurl4:amd64 but it is not installable or
                       libcurl3:amd64 but it is not installable
              Depends: libdbus-1-3:amd64 (>= 1.5.12) but it is not installable
              Depends: libdrm2:amd64 (>= 2.4.75) but it is not installable
              Depends: libexpat1:amd64 (>= 2.0.1) but it is not installable
              Depends: libgbm1:amd64 (>= 17.1.0~rc2) but it is not installable
              Depends: libglib2.0-0:amd64 (>= 2.37.3) but it is not installable
              Depends: libgssapi-krb5-2:amd64 but it is not installable
              Depends: libgtk-3-0:amd64 (>= 3.9.10) but it is not installable
              Depends: libgtk-3-0:amd64 (>= 3.9.10) but it is not installable or
                       libgtk-4-1:amd64 but it is not installable
              Depends: libkrb5-3:amd64 but it is not installable
              Depends: libnspr4:amd64 (>= 2:4.9-2~) but it is not installable
              Depends: libnss3:amd64 (>= 2:3.30) but it is not installable
              Depends: libnss3:amd64 (>= 3.26) but it is not installable
              Depends: libpango-1.0-0:amd64 (>= 1.14.0) but it is not installable
              Depends: libx11-6:amd64 but it is not installable
              Depends: libx11-6:amd64 (>= 2:1.4.99.1) but it is not installable
              Depends: libxcb1:amd64 (>= 1.9.2) but it is not installable
              Depends: libxcomposite1:amd64 (>= 1:0.4.4-1) but it is not installable
              Depends: libxdamage1:amd64 (>= 1:1.1) but it is not installable
              Depends: libxext6:amd64 but it is not installable
              Depends: libxfixes3:amd64 but it is not installable
              Depends: libxkbcommon0:amd64 (>= 0.4.1) but it is not installable
              Depends: libxkbfile1:amd64 but it is not installable
              Depends: libxrandr2:amd64 but it is not installable
              Recommends: libvulkan1:amd64 but it is not installable
E: Unable to correct problems, you have held broken packages.
root@ffc652d1f3f8:/rust-analyzer# 

# snap install --classic code
bash: snap: command not found
root@ffc652d1f3f8:/rust-analyzer# apt install snap
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following NEW packages will be installed:
  snap
0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
Need to get 374 kB of archives.
After this operation, 2719 kB of additional disk space will be used.
Get:1 http://deb.debian.org/debian bookworm/main arm64 snap arm64 2013-11-29-11 [374 kB]
Fetched 374 kB in 1s (334 kB/s)
debconf: delaying package configuration, since apt-utils is not installed
Selecting previously unselected package snap.
(Reading database ... 25441 files and directories currently installed.)
Preparing to unpack .../snap_2013-11-29-11_arm64.deb ...
Unpacking snap (2013-11-29-11) ...
Setting up snap (2013-11-29-11) ...
root@ffc652d1f3f8:/rust-analyzer# snap install --classic code
bash: snap: command not found
```

# 参考資料(reference)
Programming Rust on docker(149)
https://qiita.com/kaizen_nagoya/items/d71b2c1932562ac1ecfc

dockerでRUST
https://qiita.com/kaizen_nagoya/items/c07350f6ab6ec656c42c

初めてのRUST
https://qiita.com/kaizen_nagoya/items/dd8f5e3b218d48fb79e1

Rust入門
https://qiita.com/kaizen_nagoya/items/b3a42bf5a849dabe52c5

## 補足資料（Additions）
2023 Countdown Calendar 主催・参加一覧
https://qiita.com/kaizen_nagoya/items/c4c2f08ac97f38d08543

CountDownCalendar月間　いいねをいただいた記事群　views　順
https://qiita.com/kaizen_nagoya/items/583c5cbc225dac23398a

物理記事　上位100
https://qiita.com/kaizen_nagoya/items/66e90fe31fbe3facc6ff

数学関連記事１００
https://qiita.com/kaizen_nagoya/items/d8dadb49a6397e854c6d

言語・文学記事　１００
https://qiita.com/kaizen_nagoya/items/42d58d5ef7fb53c407d6

医工連携関連記事一覧
https://qiita.com/kaizen_nagoya/items/6ab51c12ba51bc260a82

通信記事１００
https://qiita.com/kaizen_nagoya/items/1d67de5e1cd207b05ef7

自動車　記事　１００
https://qiita.com/kaizen_nagoya/items/f7f0b9ab36569ad409c5

Qiita(0)Qiita関連記事一覧（自分）
https://qiita.com/kaizen_nagoya/items/58db5fbf036b28e9dfa6

鉄道（０）鉄道のシステム考察はてっちゃんがてつだってくれる
https://qiita.com/kaizen_nagoya/items/26bda595f341a27901a0

日本語（０）一欄
https://qiita.com/kaizen_nagoya/items/7498dcfa3a9ba7fd1e68

英語(0) 一覧
https://qiita.com/kaizen_nagoya/items/680e3f5cbf9430486c7d

転職(0)一覧
https://qiita.com/kaizen_nagoya/items/f77520d378d33451d6fe

仮説（0）一覧（目標100現在40）
https://qiita.com/kaizen_nagoya/items/f000506fe1837b3590df

安全（0）安全工学シンポジウムに向けて: 21
https://qiita.com/kaizen_nagoya/items/c5d78f3def8195cb2409

Error一覧 error(0)
https://qiita.com/kaizen_nagoya/items/48b6cbc8d68eae2c42b8

Ethernet 記事一覧　Ethernet(0)
https://qiita.com/kaizen_nagoya/items/88d35e99f74aefc98794

Wireshark 一覧 wireshark(0)、Ethernet(48) 
https://qiita.com/kaizen_nagoya/items/fbed841f61875c4731d0

線網（Wi-Fi）空中線(antenna)(0) 記事一覧(118/300目標)
https://qiita.com/kaizen_nagoya/items/5e5464ac2b24bd4cd001

OSEK OS設計の基礎　OSEK(100)
https://qiita.com/kaizen_nagoya/items/7528a22a14242d2d58a3

官公庁・学校・公的団体（NPOを含む）システムの課題、官（０）
https://qiita.com/kaizen_nagoya/items/04ee6eaf7ec13d3af4c3

Error一覧(C/C++, python, bash...) Error(0)
https://qiita.com/kaizen_nagoya/items/48b6cbc8d68eae2c42b8

C++ Support(0)　
https://qiita.com/kaizen_nagoya/items/8720d26f762369a80514

Coding Rules(0) C Secure , MISRA and so on 
https://qiita.com/kaizen_nagoya/items/400725644a8a0e90fbb0

なぜdockerで機械学習するか 書籍・ソース一覧作成中 (目標100)
https://qiita.com/kaizen_nagoya/items/ddd12477544bf5ba85e2

言語処理100本ノックをdockerで。python覚えるのに最適。:10+12
https://qiita.com/kaizen_nagoya/items/7e7eb7c543e0c18438c4

プログラムちょい替え（0）一覧:4件
https://qiita.com/kaizen_nagoya/items/296d87ef4bfd516bc394

TOPPERSまとめ　#名古屋のIoTは名古屋のOSで
https://qiita.com/kaizen_nagoya/items/9026c049cb0309b9d451

自動制御、制御工学一覧（０）
https://qiita.com/kaizen_nagoya/items/7767a4e19a6ae1479e6b

プログラマが知っていると良い「公序良俗」
https://qiita.com/kaizen_nagoya/items/9fe7c0dfac2fbd77a945

一覧の一覧( The directory of directories of mine.) Qiita(100)
https://qiita.com/kaizen_nagoya/items/7eb0e006543886138f39

自動制御、制御工学一覧（０）
https://qiita.com/kaizen_nagoya/items/7767a4e19a6ae1479e6b

Rust(0) 一覧　
https://qiita.com/kaizen_nagoya/items/5e8bb080ba6ca0281927

小川清最終講義、小川清最終講義（再）計画, Ethernet(100) 英語(100) 安全(100)
https://qiita.com/kaizen_nagoya/items/e2df642e3951e35e6a53

＜この記事は個人の過去の経験に基づく個人の感想です。現在所属する組織、業務とは関係がありません。＞
This article is an individual impression based on the individual's experience. It has nothing to do with the organization or business to which I currently belong.
### 文書履歴(document history)
ver. 0.01 初稿 　20231231
### 最後までおよみいただきありがとうございました。
いいね　💚、フォローをお願いします。
#### Thank you very much for reading to the last sentence.
Please press the like icon 💚　and follow me for your happy life.
