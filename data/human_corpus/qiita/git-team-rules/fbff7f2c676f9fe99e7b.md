# はじめに
gitは使っているけど、GitHubのマージの方法の違いやPull Requestの差分はどこを見ているのかなどが曖昧な方向けの記事です。

[git-flow](https://www.atlassian.com/ja/git/tutorials/comparing-workflows/gitflow-workflow)を採用している開発チームは多いと思いますが、以前git-flowのhotfix対応でのマージ方法で迷ってしまったので、改めて周辺知識の理解とhotfix対応でのマージ方法を備忘録として残します。

GitHubでPRを作成し、マージする際には下記の3種類からマージ方法を選択できます。
- Create a merge commit
- Squash and merge
- Rebase and merge

Create a merge commitが基本のマージ方法だと思いますが、
私のチームではfeatureブランチをdevelopブランチへマージする際にsquash and mergeを採用しています。理由は、「featureブランチには開発時の細かいコミットが含まれており、1つの機能の開発を1つのコミットにまとめてコミット履歴をきれいに保つため」という理解をしていました。

では、hotfix対応の時（hotfix→master）はどちらのコミット方法を採用するべきでしょうか？上記の理解のみだとhotfix→master時にもsquash and mergeを選択しそうになります（余計なコミットが1つに結合されるため）。
私自身がhotfix対応時にsquash and mergeを選択し、余計な対応を後からする必要があったので備忘録として下記の内容を解説します。

- 前提知識1: Create a merge commitとSquash and merge commitの違い（※ Rebase and mergeは省略）
- 前提知識2: ツードット比較とスリードット比較の違い
- Hotfix対応でのマージの種類の選び方

※ 注意：各開発チームでgitの運用が異なります。私の場合はこのパターンに当てはまったという理解で書いていますので、ご理解お願いします。

# Create a merge commitとSquash and mergeの違い
マージ方法を選択する上で必要な前提知識の1つ目はそれぞれのマージ方法の違いです。
※ 説明は簡略化しますので、それぞれのマージ方法の詳細や使い分けは下記資料を参考にしてください。
[GithubでのWeb上からのマージの仕方3種とその使いどころ](https://qiita.com/ko-he-8/items/94e872f2154829c868df)

下記のようなブランチワークを前提に説明します。
Aブランチから派生したBブランチで新たにb1, b2のコミットを実施し、Aブランチにマージすることを想定します。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/265a8abb-6de1-c195-9fed-960c40ad5cb4.png" width="300">

## Create a merge commit
Create a merge commit後は下記の状態になります。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/255fd07f-6247-63bc-8fc6-f8bac963b0df.png" width="500">

Aブランチには新たなa3というマージコミットが作られます。
マージコミットa3には変更差分がなく、実際の変更差分はb1, b2のコミットがコミット履歴に残ります。

## Squash and merge
Squash and merge後は下記のような状態になります。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/c939f87e-19b2-e0c7-e01c-8435fbd6ded4.png" width="500">
Bブランチでのコミットはa3コミットにまとめられAブランチにマージされます。
そのため、a3ブランチにはb1, b2の修正差分は含まれますが、b1, b2のコミットは含まれません。

# ツードット比較とスリードット比較の違い
マージ方法を選択する上で必要な前提知識の2つ目は「GitHubのプルリクエストではどこの差分を見ているのか」の話です。
※ こちらも説明は簡略化しますので、詳細は下記資料を参考にしてください。
[GitHubのプルリクエストの差分はどこと比較しているか？(git diffの".."と"..."の違い)](https://qiita.com/m-yamazaki/items/e57e357116e95ae370dc)


gitの差分比較にはツードット比較（..）とスリードット比較(...)の2種類があります。
[GitHub公式ドキュメント](https://docs.github.com/ja/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-comparing-branches-in-pull-requests#three-dot-and-two-dot-git-diff-comparisons "GitHub Docs")を参照しながら説明します。

下記のようなブランチの状態を前提とし、BブランチをAブランチにマージすることを想定します。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/dde32db4-db60-c75e-9b19-08bb6b741ccd.png" width="500">

## ツードット比較
> ツードット比較では、ベース ブランチ (main など) の最新状態とトピック ブランチの最新バージョンの差分が表示されます。

すなわち、ベースブランチの最新状態であるコミットa4とトピックブランチの最新バージョンであるコミットb2の差分が比較されます。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/711d8bfe-28eb-c876-8879-230390c31cc8.png" width="500">


## スリードット比較
> スリードット比較では、両方のブランチ (マージ ベース) の最新共通コミットとトピック ブランチの最新バージョンの差分が表示されます。

すなわち、両ブランチの最新の共通コミットa2とトピックブランチの最新バージョンであるコミットb2が比較されます。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/9fa58ae6-6645-cc7c-43b6-f90f33d1169d.png" width="500">

## GitHubのプルリクエストはツードット？スリードット？
**GitHubのプルリクエストはスリードット比較を行っています。**

> スリードット比較はマージ ベースと比較するため、"pull request によって何が導入されるか" に焦点を当てています。

# Hotfix対応でのmergeの種類の選び方
ここまでGitHubでのマージ方法の違いとGitHubのプルリクエストが何を比較しているかの前提知識の説明をしました。

では本題の**Hotfix対応の時にCreate a merge commitとSquash and mergeのどちらの方法でマージするべきか**という話に戻ります。

「コミットを1つにまとめる」という利点だけ考えるとSquash and mergeを選択したくなりますが、これが落とし穴でした。
これだと、Hotfix対応自体は問題ないのですが、その後のdevelop→master時に差分がおかしくなったり、コンフリクトが発生したりします。


下記のブランチの状態を想定して説明します。
hotfixブランチをdevelopブランチにマージする前にdevelopブランチでは同じファイルの修正コミット（d1）がある場合を想定します。（チーム開発ではよくある状況だと思います。）
hotfixの手順としては下記の通りです。

1. masterブランチからhotfixブランチを切る
2. hotfixブランチでソースコードを修正する
3. hotfixブランチをmasterブランチにマージする
4. hotfixブランチにdevelopブランチの内容をマージしてコンフリクト修正する
5. hotfixブランチをdevelopブランチにマージする
6. developブランチをmasterブランチにマージする

6の工程を経て、developブランチとmasterブランチの状態が一致し、hotfix対応が終了となります。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/27259160-2cf7-9224-ed6d-0a53c4ff6746.png" width="400">

## Squash and mergeの場合
Squash and mergeの場合、下記のgit graphになり、develop→master時にコンフリクトが発生します。
コンフリクトを修正したら良いのですが、基本的にdevelopとmasterは同じ状態を保つのが基本であり、matserマージ時にはコンフリクト修正はしたくありません。（developマージ時にコンフリクト修正すべきだと思います。）

また、仮に同じファイルの修正差分（d1）がない状態であっても、develop→master時に差分が出ます。ソースコードの状態は一致しているのに、差分が出るというのも少し違和感があります。

※ コンフリクト修正後にhotfix→masterをするとコンフリクトは回避できそうですが、hotfixは緊急対応以外に実施すべきではなく、masterブランチへの直マージはできるだけ避けたいはずです。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/8a75d899-5910-a831-118c-5b0cc6528888.png" width="500">

## Create a merge commitの場合
Create a merge commitの場合、下記のgit graphになり、コンフリクトが発生しません。
よって、hotfix後の通常のブランチワークもスムーズにいきます。
なので、Create a merge commitを採用した方が良さそうです。
<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/612702/5cf46bd2-6834-373e-6cea-2fa03a57e28b.png" width="500">

# おわりに
なんだかんだイレギュラーなことが起きると焦るgit。
改めて理解して図示してみると理解が深まりました。
今回は前提知識も含めてざっくりと説明しました。説明も省いてありますので、必要に応じて参考サイトで補っていただければ幸いです。

※ 注意：各開発チームでgitの運用が異なります。私の場合はこのパターンに当てはまったという理解で書いていますので、ご理解お願いします。

# 参考サイト
- [Gitflow ワークフロー](https://www.atlassian.com/ja/git/tutorials/comparing-workflows/gitflow-workflow)
- [GithubでのWeb上からのマージの仕方3種とその使いどころ](https://qiita.com/ko-he-8/items/94e872f2154829c868df)
- [GitHubのプルリクエストの差分はどこと比較しているか？(git diffの".."と"..."の違い)](https://qiita.com/m-yamazaki/items/e57e357116e95ae370dc)
- [プルリクエスト中でのブランチの比較について](https://docs.github.com/ja/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-comparing-branches-in-pull-requests#three-dot-and-two-dot-git-diff-comparisons)

