

こんにちは :relaxed: 
経験値低めな自分は通っぽい(?)言い方されると :thinking: ってなります。
「新規ブランチを作成して」だとわかるけれど、「ブランチ切って」だとわからないことない??
「ヘッドから生やして」ってもっとわからなくない??
なので、この指示はこういう意味だよーというのを書きました。
大前提として、不安なら経験値ある人に意味を聞いたほうが良い、とは思いますが、
自分で当たりをつけてから質問するほうが気が楽だと思うので参考までに :relaxed: 


### 「フィーチャーブランチ切って」-意味:新規ブランチを作成すること。
#### 準備:事前にベースとなるブランチはどれか確認する
属しているチームがGitHub-flow or git-flowのどちらで運用しているか知っているならとても優秀 :relaxed: 
git-flowの場合はdevelopブランチを、GitHub-flowの場合は、mainブランチをベースにする。
そういう説明がなくて、かつ、誰も教えてくれなさそうな雰囲気がある場合は、gitHubで他の人が出したプルリクを見るとヒントがあるかも。


git-flowとGitHub-flowの違い：
https://atmarkit.itmedia.co.jp/ait/articles/1708/01/news015.html

#### 新規ブランチを作る
```zsh:コマンド
## 事前準備 (リモートリポジトリの情報を取得する)
git fetch

## Good!
git switch -c X-あなたが作りたいブランチ名-X Y-ベースブランチ名-Y

## こっちでも同じことができるが、ちょっと古い
`git checkout -b X-あなたが作りたいブランチ名-X Y-ベースブランチ名-Y`

## sample1. mainブランチから新規ブランチを作る場合
`git switch -c feature/from-main-branch origin/main`

## sample2. developブランチから新規ブランチを作る場合
`git switch -c feature/from-main-branch origin/develop`
```

:cactus: checkoutとswitchの違い
Git 2.23で、新しくswitchというコマンドが追加されていて、新しいブランチを作る場合は、こちらを使ったほうがよい。
ただcheckoutも同じように動くし、フレーズとしてcheckoutに慣れてしまっていると、「新しいフィーチャーブランチ、mainからcheckoutしてー」と言われることもあるので、同義だと認識しておくと言葉が通じてよさそう。
https://github.blog/2019-08-16-highlights-from-git-2-23/

:cactus: チームによってはブランチ名に命名規則があることもあるので、確認しておくとなおよし。

### 「プルリク出して」 - 意味：改修内容をリモートリポジトリにアップロードし、GitHub上でプルリクエストを作成すること。

#### 変更したファイルを確認する

```zsh
### 基本型
git status

### 新規ファイルを1つ追加、既存ファイルを1つ編集した場合は下記のような結果になる
XXXX@YYYYY directory % git status
On branch from-main-branch
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   app/init.py ### 編集したファイル

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	app/new-feature.py ### 新規作成したファイル

no changes added to commit (use "git add" and/or "git commit -a")
```

#### コミット対象のファイルをステージに上げる

```zsh
### 基本型
git add X-対象のファイル名-X

### 今変更している全てのファイルを全てステージに上げる
git add --all

### sample.app/init.pyをステージに上げる
git add app/init.py

### ステージに上げた後のステータス
XXXX@YYYYY directory % git status
On branch feature/from-main-branch
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   app/init.py ###　←コミット対象のものとして表示

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	app/new-feature.py ### ←相変わらず

```

ステージ=1回のコミットに含めるファイルをおく場所って感じかな。
コミットの粒度はチームや人それぞれですが、例えば、リファクタ(=機能はそのまま、いまいちなコードを素敵に変更する)と機能追加を一緒に対応した場合は、リファクタとして変更したファイルをadd& commit、機能追加で変更したファイルをadd&commitのように2回に分けたほうが好ましいと思います:relaxed:


#### コミットする

```zsh
### 基本型
git commit

### オプションでコメントをつけるとなおよし
git commit -m "コメント"

### sample:
git commit -m "feat: add new button"

### 変更後のステータス
XXXX@YYYYY directory % git status
On branch feature/from-main-branch
Your branch is ahead of 'origin/main' by 1 commit. ### ←コミットが増えている
  (use "git push" to publish your local commits)
 ### 変更したapp/init.pyがなくなっている
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	app/new-feature.py ###　←相変わらず

```

この状態で、git logコマンドを使うと自分のコミットが確認できる。
```zsh
### コマンド
git log
### 結果
commit 74e0e3ca3fea190c1ed28d7cfcb125b35f40273e (HEAD -> feature/from-main-branch) ### 自分のコミットが先頭になっていることがわかる
Author: me
Date:   Mon Oct 10 12:40:33 2022 +0900

    feat: add new button

commit 4835ff76d74243b23ac7dfc7a65c1f056478d07a (origin/main) 
Merge: b384c82 dbefadb
Author: others
Date:   Wed Aug 31 11:53:55 2022 +0900

    Merge pull request #16 from XXXX/feature/test_remote

    Feature/test remote

```

:cactus: チームによっては、コミットメッセージの冒頭に共通の文言をつける(プレフィックス,prefix)ルールがある場合ものあるので確認するとよさそう

### プルリクエストを作る

まずはリモートリポジトリに登録
```zsh
## 基本型
git push X-リモートリポジトリ名-X　X-自分が登録したいブランチ名-X

### sample
### originを指定すると、リモートリポジトリ上の同名ブランチに内容を登録してくれる。 
### 2回目のpush以降は同名ブランチに内容を追加してくれる。
XXXX@YYYYY directory % git push origin feature/from-main-branch
### 結果
Enumerating objects: 7, done.
Counting objects: 100% (7/7), done.
Delta compression using up to 8 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (4/4), 377 bytes | 377.00 KiB/s, done.
Total 4 (delta 0), reused 0 (delta 0)
remote:
remote: Create a pull request for 'feature/from-main-branch' on GitHub by visiting:
remote:      https://github.com/XXXX/リポジトリ名/pull/new/feature/from-main-branch
remote:
To github.com:XXXX/リポジトリ名.git
 * [new branch]      feature/from-main-branch -> feature/from-main-branch
```

コンソールに表示されたURLからアクセスするか、GitHubにアクセスすると、こんな感じにpull requestを作成する画面への誘導が出てくる！
あとは画面上でリクエストを作ればOK
![スクリーンショット 2022-10-23 11.00.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/482103/d537e4d2-8885-2273-2f4a-63e9c29ac3ca.png)

これでプルリクが出せたね:relaxed: 

### 「最新のmain取り込んでからプルリク出して」-意味：mainブランチの内容でmerge or rebaseすること。
mainブランチからfeatureブランチを作って作業していたとして、自分の作業中に他の人がmainに機能を追加することがあるよね。
でも、自分で取り込まないとfeatureブランチには反映されないので、下記のような作業をする必要があるよ。

リモートリポジトリ上のapp/init.pyの記述。赤枠部分が追加されていても、自分のブランチ上の同じ記述がないと仮定します。
![スクリーンショット 2022-10-23 11.40.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/482103/f5082ade-ff4c-df3f-69db-a42c9a57fe11.png)

```zsh
### 反映させたいブランチに切り替える。すでにいる場合はスキップ
git branch X-自分のブランチ名-X

### リモートリポジトリの情報をとってくる(反映はしない)
git fetch 

### mergeする場合
git merge origin/main

### rebaseする場合
git rebase origin/rebase

### sample マージした場合
XXXX@YYYYY directory % git fetch ## origin/mainの情報を取得
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (1/1), done.
From github.com:リポジトリ名/gitPractice
   ac7bdb3..76e744d  main       -> origin/main
XXXX@YYYYY directory % git merge origin/main ## mainの情報を自分のブランチに反映
Updating ac7bdb3..76e744d
Fast-forward
 app/init.py | 2 ++
 1 file changed, 2 insertions(+)

### この状態でapp/init.pyを開くと、赤枠の情報が追記されていることがわかるよ

```
:cactus: rebaseかmergeかはチームのルールや状況に合わせて使い分けるとよさそう。
個人的には初回のpush前はrebaseでmainの先頭に機能が追加された状態にする。 push後に取り込むときは、mergeを使うような使い分けをしています。

rebaseとmergeの違いは調べるとわかりやすい記事がたくさん出てくるからそちらを参考にしてね。親切な人が多くていい世の中:relaxed: 


### 「feature/Aブランチからブランチ切って。　」-意味：ベースブランチを指定して自分のブランチを作ること。
通常はmain or developブランチをベースにして、featureブランチを作ると思いますが、
大人数で開発をしていると、「AさんがDB更新の関数を作成してpullRequestを出した。まだマージされていないけれど、その関数を使った機能を別のところで作りたい。」みたいなことが起きるよ。そんな時に、Aさんが機能追加したブランチをベースにして、自分のブランチを作るとよさそう。

```zsh
### 事前準備 (リモートリポジトリの情報を取得する)
git fetch

### Aさんのブランチを見つける (リモートリポジトリのブランチの一覧を確認する）
git branch -r

### 特定のブランチをベースにブランチをきる
git switch -c X-あなたが作りたいブランチ名-X Y-Aさんのブランチ名-Y

### sample 
### リモートリポジトリ上のfeature/from-main-branch2から新しくブランチを作成する場合
XXXX@YYYYY gitPractice % git switch -c feature/from-main2-branch origin/feature/from-main-branch2 ##リモートリポジトリには「origin」を必ずつける
Branch 'feature/from-main2-branch' set up to track remote branch 'feature/from-main-branch2' from 'origin'.
Switched to a new branch 'feature/from-main2-branch'

```

:cactus: 特定のブランチから新しくブランチを作った場合は、ベースにしたブランチ→自分のブランチの順でmainにマージするか、ベースにしたブランチに自分のブランチの内容をマージしてから、ベースにしたブランチをmainにマージする必要があるよ。ベースにしたブランチのことを先行ブランチと呼んだりもします。


### 「feature/Aブランチに向けて、プルリク出して」-意味: pullRequestのマージ先を変更すること。
pullRequestの編集ページの上部に、どのブランチに向けてマージするかを指定できるよ。
![スクリーンショット 2022-10-23 11.01.36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/482103/1e7f0111-8874-99cb-83bc-3a5c95743025.png)

:cactus: プルリクを出した後で、feature/Aブランチがdevelopブランチにマージされると、自動で自分のブランチの向き先もdevelopに変わります。

---
自分の経験ベースなので、組織によって色々違うと思いますが、ご参考までに:relaxed:
他の言い方もご存じであれば、教えていただけると幸いです:relaxed:
