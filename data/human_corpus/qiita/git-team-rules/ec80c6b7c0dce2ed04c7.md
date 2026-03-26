## はじめに

[2023年6月の Feature Summary](https://powerbi.microsoft.com/ja-jp/blog/power-bi-june-2023-feature-summary/) で、Power BI と Gitとの統合がプレビュー機能として公開されました。
人によっては待望の機能なのではないでしょうか。
わたしも、テキストベースでバージョン管理できたらいいなぁと思っていた内のひとりなので、今回のプレビュー機能はうれしい気持ちになりました。

とはいえ、落ち着いて冷静に、実際に使って見て所感など述べたいと思います。

## やってみる

### 使うもの

すべて無料の範囲内で使う。

* Power BI Desktop (2023年6月バージョン）
* Git
    * [Git for Windows](https://gitforwindows.org/)
* Gitのホスティングサービスのアカウント
    * Azure DevOps - Azure Repos
* Git操作のGUIツール
    * Visual Studio Code
        * プラグイン：
            * [Git Graph](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph)


### リモートリポジトリの作成

リポジトリは記事通りに `Azure DevOps` を使う。
Azure DevOps は使ったことなし。

https://azure.microsoft.com/ja-jp/pricing/details/devops/azure-devops-services/

今回は Azure DevOps の中の Azure Repos のみ使用するので、Basic プランに該当。
5ユーザーまでは無料で使えるようなので、記事通り Azure DevOps の Azure Repos を使う。
![01'_AzureDevOps_createRepo.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/3ba98b86-b4fa-c487-e061-760e98e0371e.png)

作成した organization 内の Repos を開き、リモートリポジトリの URL をコピーする。
![02'_AzureDevOps_Repos.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/444b44cd-2a54-620c-6c0e-1ad2be47bde4.png)

### ローカル へ クローン

Git 操作はこちらも記事通り、`Visual Studio Code` を使う。
VSCode は標準で Git連携機能が搭載されている（画面左側）ので、Gitがインストール済であればすぐに使える。
「リポジトリをクローン」を選び、先ほどコピーしたURLを指定する。
![03'_VSCode_URL.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/a1643a6b-5f86-71c6-12c7-a6426c7c0658.png)

クローン先のローカルフォルダ（空のフォルダ）を指定する。
![05'_リポジトリ_フォルダを指定.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/0a2ad455-4674-3087-6725-f86b73116bb9.png)

これで、クローンが完了。

### 機能を有効にする

Power BI Desktop (2023年6月のバージョン）を起動し、
オプション -> プレビュー機能 の中の「Power BI プロジェクト(.pbip)保存オプション」をオンにする。
![06’_プレビューオン.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/85679bc9-4e65-2b25-cac9-4b1035d5c221.png)

そのまま空のレポートを、
保存形式を **pbip** にして、先ほどのクローン先に指定したフォルダに保存する。

![08’_名前を付けて保存保存先クローンしたフォルダ.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/69a6558b-1a16-f620-916e-acb16eea5535.png)

フォルダを見ると、以下のように複数のファイルに分割され保存された。
![10_変更フォルダ.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/41b883e7-7607-929a-c1ca-cb8abe284b69.png)

VS Code 側も同様。
![09_変更VSCode.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/dd52b6c3-07f9-c008-295f-8f5c39bcb299.png)

### first commit の前に

最初のコミットは、今後の作業のベースとなるので一通りのファイルの内容を確認する。

https://learn.microsoft.com/ja-jp/power-bi/developer/projects/projects-dataset

https://learn.microsoft.com/ja-jp/power-bi/developer/projects/projects-report

#### デフォルトでよさそう

* Dataset/
    * item.config.json
    * item.metadata.json

* Report/
    * item.config.json
    * item.metadata.json

#### 開発環境・要件によっては要確認 ?

* Dataset/
    * definition.pbidataset
    * .pbi\editorSettings.json

* Report/
    * definition.pbir

Report > StaticResources > SharedResources > BaseThemes > xxx.json
についてはドキュメントを見つけることができなかった。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/06281585-a009-d9b4-d98f-13d42b1a62c4.png)

調べたら、レポートのベーステーマの情報のよう、これもいじる必要はなさそう。

model.bim と report.json は主な作業ファイルとなるので、
ベースとなる状態や、実際に作業していく中での管理などはチーム内で考える必要があると思う。


### first commit

VSCode の Git機能 タブに移動する。
最初なので、全ての変更をコミットしようと思う。全ての変更をステージングする。
![11‘_ステージング.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/cea0dd4d-6aa0-b765-d78b-eda4c8753b18.png)

コメントを書いて、コミットする。はじめてのこみっと。
![12_コミット.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/45bf5d39-fe14-67e7-b5fc-52a74d1be761.png)

コミット履歴をみる。※[Git Graph](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/b67a2e80-1faa-4470-d973-781b812bd3f9.png)

リモートリポジトリもみる。
![13_リモート.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/af6196ea-a371-f41d-96ea-90c6f4153ce0.png)

これで、バージョン管理の準備はOK。

### レポートを作っていく中で、どのような変更が加わるのか 

実際の操作に対し、どのような変更が加わるのかを少し細かく確認する。

とりあえず `master` ブランチを離れたいので、`develop` ブランチを作成。
![14_developブランチ.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/383b8555-3fe6-664e-1beb-218326f850c2.png)

今回はこちらのチュートリアルのレポートを作成する。

https://learn.microsoft.com/ja-jp/power-bi/create-reports/desktop-dimensional-model-report

#### データを取り込む

データソースを読み込んで、Power Query での ETL処理 を行い取り込む。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/354aacdc-4817-5d07-a473-478f009d18d2.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/93e0ed88-ad29-8262-02b7-1746bb688ab4.png)

ここまでを保存と、以下のファイルが変更された。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/bd330a4b-e002-cf84-280f-3eb21b975531.png)

developer-mode.Dataset

https://learn.microsoft.com/ja-jp/power-bi/developer/projects/projects-dataset


> model.bim
プロジェクト モデルの Tabular Model Scripting Language (TMSL) データベース オブジェクトの定義が含まれています。 
diagramLayout.json
レポートに関連付けられたデータセットの構造を定義するダイアグラムのメタデータが含まれています。 プレビュー中は、このファイルで外部編集はサポートされません。

developer-mode.Report

https://learn.microsoft.com/ja-jp/power-bi/developer/projects/projects-report

> report.json
ビジュアル、ページ レイアウト、意図した操作を含むレポートを定義します。 プレビュー中は、このファイルで外部編集はサポートされません。
datasetDiagramLayout.json
レポートに関連付けられているデータセットの構造を説明するデータ モデル図が含まれています。 プレビュー中は、このファイルで外部編集はサポートされません。

上記の4つのファイルに変更が入った。

#### モデルビューを見やすく配置する

モデルビューを以下のように見やすく動かして配置する。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/ff60ac26-3b87-90b5-a3e1-584adb89fa3c.png)

以下のファイルに変更が入った。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/bc1f2010-60c5-54cf-ed96-db72e78fd7be.png)

report.json の変更を見てみる。

変更前
```
"config": "{\"version\":\"5.44\",\"themeCollection\":{\"baseTheme\":{\"name\":\"CY23SU04\",\"version\":\"5.45\",\"type\":2}},\"activeSectionIndex\":0,\"defaultDrillFilterOtherVisuals\":true,\"linguisticSchemaSyncVersion\":0,\"settings\":{\"useNewFilterPaneExperience\":true,\"allowChangeFilterTypes\":true,\"useStylableVisualContainerHeader\":true,\"queryLimitOption\":6,\"exportDataMode\":1,\"useDefaultAggregateDisplayName\":true},\"objects\":{\"section\":[{\"properties\":{\"verticalAlignment\":{\"expr\":{\"Literal\":{\"Value\":\"'Top'\"}}}}}]}}",
```

変更後
```
"config": "{\"version\":\"5.44\",\"themeCollection\":{\"baseTheme\":{\"name\":\"CY23SU04\",\"version\":\"5.45\",\"type\":2}},\"activeSectionIndex\":0,\"defaultDrillFilterOtherVisuals\":true,\"linguisticSchemaSyncVersion\":2,\"settings\":{\"useNewFilterPaneExperience\":true,\"allowChangeFilterTypes\":true,\"useStylableVisualContainerHeader\":true,\"queryLimitOption\":6,\"exportDataMode\":1,\"useDefaultAggregateDisplayName\":true},\"objects\":{\"section\":[{\"properties\":{\"verticalAlignment\":{\"expr\":{\"Literal\":{\"Value\":\"'Top'\"}}}}}]}}",
```

`linguisticSchemaSyncVersion` が 0 -> 2 になっている。なぜここが変わるのか、わからない。

また、
* Dataset/diagramLayout.json
* Report/datasetDiagramLayout.json
は同一の内容だった。
（確認したら、最初から同じ内容でした。）

#### モデルに階層を追加

テーブルに階層を作成するたびに、

model.bim の変更のほか、

Layout.json の
 `diagrams` - `scrollPosition` と
 `diagrams` - `nodes` - ` zIndex`
に変更が入る。
 ```
{
  ...,
  "diagrams": [
    {
      ...,
      "scrollPosition": {
        "x": 52.209075176601246,    // 変更が入る
        "y": 205.76517863719315     // 変更が入る
      },
      "nodes": [
        {
          ...,
          "zIndex": 7               // 変更が入る
        },
        {...},
        {...}
    ]
    ...
}
```
これらはコミットしなくても良いのではないか、と思い、**model.bim だけコミット** して、
Layout.json の変更は破棄し Desktop を開き直すと、特に壊れた様子もなく開くことができた。

このような感じで、ビジュアルにタイトルを追加するところまで作業した。

https://learn.microsoft.com/ja-jp/power-bi/create-reports/desktop-dimensional-model-report#visual-1-add-a-title

ここまでの履歴

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2349908/c80c109a-ed9d-cc87-9db8-bc05138d2bdf.png)


## わかってきたこと

（あくまで、個人の見解です。今後使っていく中でブラッシュアップする部分です）

### コミット単位

コミットとして以下のファイル単位になりそう。

* model.bim の変更
    * モデルに関わる変更
* report.json の変更
    * ビジュアルに関わる変更
* *Layout.json の変更
    * モデルビューに関わる変更 ? 
* データ取込み時
    * 「閉じて適用」で取り込まれた時の状態


基本的にレイアウト変更（Layout.json）は実装（モデル・ビジュアル追加削除など）とは別の変更と考え、開発中は変更があってもコミット履歴に含まないほうがいいかもしれない。

データ取込み時以外で、
model.bim や report.json と一緒に含まないと動かないことがあるのだろうか…。

### 共同編集ができるようになったのか

これで同一レポートに対し**共同編集**ができるようになったのかについては、
結局、変更が加わるファイルが model.bim や report.json に限られているので、
同じファイルを触ることになりコンフリクトが常時発生するのではないかと思う。
運用次第かもしれないが、システム開発でいえばクラスファイルを分けるようなことができないので、
そうやり方に慣れていると同じファイルを複数で触るしかないのは腰が引けそう。

今後、作業ごとにファイルを分けるなどできるようになるなら、
Gitでのバージョン管理を採用した共同編集も実用に近くなるのではないかなぁと思った。

## おわりに

現状は、ひとりでレポートを作るときは使っていきブランチ戦略等考えていきたいと思います。
プレビュー機能なので、これからに期待です。
やってみた内容に関しては、間違っている部分があればご指摘お願いいたします。

## 参考

### Power BI Desktop Developer Mode について

https://learn.microsoft.com/ja-jp/power-bi/developer/projects/projects-overview

https://powerbi.microsoft.com/en-us/blog/deep-dive-into-power-bi-desktop-developer-mode-preview/

### 使用したサンプルデータ

https://learn.microsoft.com/ja-jp/power-bi/create-reports/desktop-dimensional-model-report
