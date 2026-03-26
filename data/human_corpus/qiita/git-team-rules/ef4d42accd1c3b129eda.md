# この記事を書いたきっかけ

筆者は普段Flutterでモバイルアプリの開発をしたり、Next.jsやLaravelでウェブアプリケーションの開発をしています。基本的に似たような開発をする方達は、Gitを使うためにGithubやBitbacketなどは必ずと言っていいほど用いるはずです。

しかし、WordPress制作をするWebサイト制作のようなプロジェクトではGitの扱いが蔑ろになっており、直接ファイルをサーバーにアップロードするようなチームも存在しました。

筆者も過去にWebサイト制作の仕事を個人で受注した際、「ローカル環境」や「Git」は存在しない上、「タスク管理」もエクセルの表でなんとなくされていました。
そのプロジェクトに「Git」は導入することができたものの、「ローカル環境」が用意しきれなかったため結局ファイルのアップロードは直接テスト用のサーバーに上げるしかなかったのです。

# 記事の対象者

- Wordpressで普段開発をしていて以下の悩みを抱えている方
    - Gitを使ってみたい
    - 手動アップロードして先祖返りを経験した
    - 修正したはずの作業のバックアップが無くて苦しい経験をした etc...<br>


- 普段Web制作をしていないがこれからWordpress環境で開発してみたい方


# 環境全体図

まずは、環境の全体図を表示してみます。

![qiita-img.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/eec49474-5132-d7d5-94da-a22d3e8ce58e.png)


### ローカル環境

ローカル環境は、WordPress専用の「Local」というアプリケーションがあるのでそちらを利用します。

https://localwp.com/

### ソースコード・資材管理
今回はGithubを用います。

アカウントが未設定の方はこちらから作成してくださいね
（P.S. Githubのアカウント作成時はとてもワクワクします）

https://github.com/

Githubでは、1つのプロジェクトを「リポジトリ」といいます。
しかし、単純にリポジトリを作ってしまうと個人のプロジェクトとして扱われてしまいます。
これをチームで扱うために、Organizationというものを設定します。

### アップロードサーバー
こちらは当然WordPressです。
細かい設定などは他のQiita記事や技術ブログに委ねます。

テスト用と本番用2つのサーバーを用意する必要はありません。

https://apps.wordpress.com/ja/d/osx-silicon/


# ⚒️ 環境構築編 ⚒️

:::note warn
筆者はMacOS環境で動かしているため、Windows, Linuxユーザーは適宜ディレクトリパスやコマンドを置き換えてください。
:::

## 1. Githubの準備をしましょう

### 1-1. Organizationの作成

まずは、Organiaztion（チーム）を作成しましょう。
右上のアイコンをクリックしたらメニューが出るので、「Your Organizations」をクリックしてください。

![スクリーンショット 2023-11-18 17.04.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/3e2f1616-53a8-44aa-e8c8-c333e6203217.png)

次に、「New Organization」をクリックし、作成をしてください。特段こだわりがなければ一旦Freeプランで良いでしょう。無料プランであっても大きい制約やセキュリティの問題は発生しません。

### 1-2. リポジトリの作成
Orcanizationの登録が完了し、Orcanizationのトップ画面へ行くと以下のような画面が出るため、こちらのNewをクリックしてリポジトリ（プロジェクト）の作成をしておきましょう。リポジトリの作成をする際、「public（一般公開）」「private（非公開）」の選択を迫られるため、「private（非公開）」を選択してください。

![スクリーンショット 2023-11-18 17.07.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/ed01d994-7c70-a580-1598-1dc91a938f3e.png)

### 1-3. チームメンバーの招待
次に、チームメンバーの招待をします。
リポジトリのヘッダーにこのようなバーがあるので、一番右のSettingsをクリックしてください

![スクリーンショット 2023-11-18 17.15.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/ef732b83-aedb-1fa6-0147-7d3adfd6634b.png)

次に、「Collaborators and Teams」をクリックしたら以下のような画面になると思うので、「Add People」で誘いたいメンバーを招待してください。

Githubの検索は、「その人のメールアドレス」もしくは「Githubアカウント名」で登録が可能です。

![スクリーンショット 2023-11-18 17.14.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/19e6b8f1-c9fd-9327-1a6c-b9566e43a9a9.png)

## 2. ローカル環境の準備
それではまず、Localアプリをダウンロードしましょう。

https://localwp.com/

自分の環境に合うものを選択してください。

![スクリーンショット 2023-11-18 17.20.30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/8ec2bcea-a94d-d3e5-ea95-f4f25d30a0ee.png)

## 2-1. アカウント設定

次に、アプリを立ち上げたらアカウント作成を要求されます。
問題なければ、GithubもしくはGoogle連携でアカウントを作成しておきましょう。
（もちろんメールアドレスで設定しても問題ないです）

完了したら、今度はLocalを立ち上げて左上のアイコンからログインをしましょう。

## 2-2. プロジェクトの作成

Localは、Localでプロジェクトを立てるやり方と、WordPressからzipでプロジェクトを共有するやり方があります。今回は、Localでプロジェクトを立てます。
Create a new siteをクリックします。

![スクリーンショット 2023-11-18 17.24.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/a66f03b0-a6f7-b84b-d5a8-c92ab1448a7f.png)

次に、左のメニューを選択し、右下のContinueをクリックしてください。

![スクリーンショット 2023-11-18 17.26.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/b703abba-08e2-b010-438d-b834241ad528.png)

進んでいくと、PHP, ウェブサーバー, MySQLのバージョン等聞かれます。
指定するものがあればCustomから指定し、特段ないのであればPreferredのまま進んでください。

![スクリーンショット 2023-11-18 17.29.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/60f8497d-d61f-dceb-e2ee-b92fdc941558.png)

登録が完了したら、自分のローカルに以下のようにローカルにワードプレス環境ができていると思います。私の場合、「kurogoma」というサイト名で作ったためこのようになっています。

<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/442a2bf0-0740-ef7a-6944-20bc1baeb7dc.png" width="300" >

### 2-3. Gitにアップロードしよう

ちなみに、Localでプロジェクトを作成する際、「どのディレクトリに保存するか」という設定もありましたが、Mac OSの場合デフォルトで以下に格納されていると思います

```
/Users/あなたのユーザー名/Local Sites
```
その中に、先ほど作成したローカルプロジェクトがあるためそれをターミナル（コマンドプロンプト）で開いてください。以下のように`pwd`コマンドで対象プロジェクトの場所にいればOKです。

```
% pwd
/Users/あなたのユーザー名/Local Sites/kurogoma
```

では次に、先ほど作成したGithubのリポジトリを見てみましょう。
以下のような画面が出ているはずです。

![スクリーンショット 2023-11-18 17.46.43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/d63fe126-6542-74fb-ae7c-56fd0a3db477.png)

ただ、一旦ここは無視して大丈夫です。以下のように上から順番にコマンドを入力してください。
```bash
% git init
% git add .
% git commit -m "🚀 first commit 🚀"
% git branch -M main
% git remote add origin リポジトリのURL
% git push -u origin main
```
以下のコマンドについては、Githubの画面にも出ているはずなのでそのままコピペしていただければ良いと思います
```bash
git remote add origin リポジトリのURL
```

最後のコマンドまで実行した後、Githubのページをリロードしてみてください。以下のように反映されていると思います。

![スクリーンショット 2023-11-18 17.50.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/863184e7-dadb-2222-f372-ec20a5fe7e32.png)

ここまでできれば、ローカル環境の完成です。

# 💻 本番環境構築編 💻

WordPressを構築するため、まずは以下のリンクからデスクトップアプリをインストールしてください

https://apps.wordpress.com/ja/d/osx-silicon/

インストールできたらWordPressにログインし、新規サイトを立ち上げてください。
立ち上げが完了したら以下のような画面になると思います。
（サイト名は、先ほどLocalで作成したものと同様に設定します）

![スクリーンショット 2023-11-18 18.11.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/5639fe03-d352-1c12-d790-57d0fa0e5186.png)

試しに、右上にある「サイトを表示」をクリックしたら以下のようなデフォルトのサイトが表示されると思います。

![スクリーンショット 2023-11-18 18.12.18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/fe77a0a4-558c-1b23-eea4-3a6329436ba0.png)

ここまでできれば一旦完了です。
基本的に直接本番環境を触ることはせず、次のセクションでLocal -> 本番への連動を自動化しましょう。

# 🌏 Local → 本番への連携 🌏

まず、Localの状態を確認します。
右上のOpen siteをクリックしてみてください。

![スクリーンショット 2023-11-18 18.14.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/bfad2ade-d18a-c479-0c95-e5e1754b2b83.png)

そうすると、以下のようにこちらもデフォルトサイトが表示されます。

![スクリーンショット 2023-11-18 18.17.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/bfbef5a9-b3b0-7c61-33bf-d34b7b93c6e4.png)

では、こちらをうまく連動するようにしましょう。
なんと、Localと本番を繋げられる便利なプラグインがあります。
手動でも構いませんが、こちらを使うことでボタン操作のみで簡単に配信できます。

https://www.satokobo.net/1338

# 🌳 ブランチ運用モデル（開発フロー） 🌳
最終的に本番で確認したい場合は、先ほどのAll-in-one-Migrationのツールを活用してください。

ここでは、ローカルで開発する際にどのようにすればスムーズな開発ができるか示します。
Github（Git）には、ブランチという概念があり、個人の作業環境を分けることができます。
かなりありきたりな話なので、ブランチの詳細については以下の記事を参照してください。

https://backlog.com/ja/git-tutorial/stepup/01/

また、ブランチにはそれぞれ「ブランチモデル」というものが存在します。
「git branch model」のように検索すればそれっぽい記事がある程度出てきますが、今回は以下のようなブランチモデルを紹介します。

### ブランチモデル

- mainブランチ
    - 先ほどのAll-in-One-Migrationをしてデータ移行をするブランチ。つまり、「本番環境と完全に一致している環境」を指します。子には`develop`ブランチを持ちます
- developブランチ
    - Local環境は全てこのブランチを親とします。`main`が親となります
- releaseブランチ
    - こちらは必須でないのですが、プロジェクトの方針として10/1リリースと11/1リリースのページがそれぞれあるとしたら必要になるでしょう。親は`develop`です
- featureブランチ
    - 基本的な機能開発で使うブランチです。親は、`feature`もしくは`develop`です
- bugfixブランチ
    - 不具合対応系のブランチです。親は`feature`もしくは`develop`です
- hotfixブランチ
    - 緊急対応用ブランチです。親は`develop`が好ましいですが、`main`を直接の親としても構いません。しかし、その場合は`develop`への更新も忘れないようにしてください

それでは、上記の内容をツリー形式で整理してみます。

```
main
├── develop
│   ├── release
│   │   └── feature
│   ├── feature # releaseブランチが不要な場合
│   │   └── bugfix
│   └── hotfix
└── hotfix # 相当緊急の場合
```

運用については、以下の流れで運用します。
### 共通
1. これまでの環境構築をした直後の場合、mainが最新です
1. エンジニアが作業に入る前までにdevelopブランチを作成します

ブランチの作成方法は、2つあります。
#### コマンドラインでブランチを作成する
コマンドでブランチを作成する場合、以下のコマンドで作成可能です
```bash
# 現在のブランチを確認
$ git branch
* main # *がついている行が現在選択されているブランチです

# 作成＋切り替え
$ git checkout -b 作りたいブランチ名
# リモートへの反映
$ git push --set-upstream origin 作りたいブランチ名
```

#### Githubブラウザ上でブランチを作成
まず、Githubでリポジトリのページを開いてください。そうすると、以下のようなブランチのボタンがあるのでクリックしてください（mainと書いてあるところ）

![スクリーンショット 2023-12-10 20.23.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/a400eeee-b74e-90c6-0882-1f5f745781f5.png)

次に、`Find or create a branch...`と書いてある箇所に作りたいブランチ名を書きましょう。
そのご`Create branch: ブランチ名 from main`と表示されている箇所をクリックして作成してください。

![スクリーンショット 2023-12-10 20.25.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/735195/3a551872-32d5-f5d4-7ba2-3797904e091f.png)

💡 ローカルへの反映

これだけでは、まだ手元の環境（ローカルリポジトリ）に反映されていません。
ローカルへの反映はコマンド操作で行いましょう

```bash
$ git fetch --prune
$ git switch 作ったブランチ名
```

それでは、上記を前提にブランチモデルの解説をします。

### releaseブランチありの場合
1. リリース時期、もしくは機能単位で以下のようなブランチを切ります
    1. `release/xxx-xxxx`（機能名を英語で）
    1. `release/yyyyMMdd`（リリース日を記載）
1. 上記ブランチから、`feature`ブランチを以下のように切る
    1. `feature/xxx-xxx`（機能名を英語で）
    1. `feature/チケット番号`
        1. Github Issuesの場合、`feature/issue-10`
        1. Jiraの場合、`feature/JIR-123`
1. `feature`ブランチから`release`ブランチにプルリクエストをする
1. `release`向けの機能が全て揃い次第、`develop`ブランチへ代表者がプルリクエストをする
1. 上記PRの差分を確認し、マージをする
1. 動作確認をする
1. `main`ブランチへ代表者がプルリクエストをする
1. 差分を確認し、マージをする
1. `All-in-One-Migration`で本番へ反映する
    1. プラグインの確認
    1. その他設定項目の確認
1. 最終的な動作確認をする
1. リリース 🎊


### releaseブランチなしの場合
1. `develop`ブランチから`feature`ブランチを切る
1. `feature`から`develop`へプルリクエストをする
1. 全ての機能が揃ったら`develop`の状態でテストをする
1. 完了したら、代表者が`develop`から`main`へプルリクエストをする
1. 差分が正しいか確認し、マージする
1. `All-in-One-Migration`で本番へ反映する
    1. プラグインの確認
    1. その他設定項目の確認
1. 最終的な動作確認をする
1. リリース 🎊

<br>

## 最後に
長かったと思いますが、読んでいただきありがとうございました。
もし、「ここがわかりにくい」「この説明を増やしてほしい」などリクエストがあれば
どんどん更新していこうと思います！

Happy Coding!

