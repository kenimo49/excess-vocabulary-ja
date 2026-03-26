[NTTデータ ソリューション事業本部 デジタルサクセスソリューション事業部](https://www.nttdata.com/jp/ja/services/data-and-intelligence/) の nttd-nagano です。

[前回の記事](https://qiita.com/nttd-nagano/items/a9b17b1aa26622f07d65) で、Informaticaのクラウドデータマネージメントプラットフォーム「[Intelligent Data Management Cloud](https://www.informatica.com/jp/platform.html)」（※1）をご紹介しましたが、**今回は、そのIDMCのデータ統合サービスである「[Cloud Data Integration](https://www.informatica.com/jp/products/cloud-integration/cloud-data-integration.html)」（※2）と、同社の旧来のデータ統合製品である「[PowerCenter](https://www.informatica.com/jp/products/data-integration/powercenter.html)」を比べ、その違いをまとめてみました。**

**記事が長くなってしまったため、全4回に分割してご説明します。**
**今回は第1回目として「まとめのまとめ」「差異の概要」「コンポーネントレベルでの比較」をご説明します。**

<details><summary>※1. Intelligent Data Management Cloud</summary>
略称はIDMC。旧称はIICS。クラウドデータマネジメントプラットフォーム。以下IDMCと記載。
</details>

<details><summary>※2. Cloud Data Integration</summary>
略称はCDI。データ統合サービス。ETL処理（※3）やELT処理（※4）を担う。以下CDIと記載。
</details>

![idmc_summary.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3031738/4e66c255-cf99-e960-8c4d-f2e577a30672.png)
![cdi_summary.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3031738/6e38a376-f7c9-0904-99ef-c5a45a65ac39.png)


「データ統合」というのは、ETL（※3）と呼ばれていたこともある領域の処理です。

<details><summary>※3. ETL処理</summary>
データベースなどに蓄積されたデータから必要なものを抽出（Extract）し、目的に応じて変換（Transform）し、データを必要とするシステムに格納（Load）すること。
</details>

<details><summary>※4. ELT処理</summary>
ETL処理（※3）と対比して使われることが多い言葉。データ統合処理の順序を従来型のE→T→Lの順ではなく、E→L→Tの順でおこなう。近年ではDBMSの性能が爆発的に向上したことから、その性能を有効活用するために使われる手法｡
</details>

なお、IDMCにはCDIをはじめ様々なサービスがありますが、本記事はPowerCenterとの比較であるため、CDIのみにフォーカスしてご説明していきます。

# まとめのまとめ

1. コンポーネントレベルで比較すると、下表のような対応関係になります。
    |PowerCenterのコンポーネント|IDMCのCDIのコンポーネント|
    |---|---|
    |クライアントツール<ul><li>Repository Manager</li><li>PowerCenter Designer</li><li>Workflow Manager</li><li>Workflow Monitor</li></ul>|Informatica Cloud Services|
    |コアサービス<ul><li>Log Service</li><li>Configuration Service</li><li>Gateway Service</li><li>Authentication Service</li><li>Administration Service</li><li>Domain Service</li></ul>|同上|
    |Repository Database|同上|
    |PowerCenter Integration Service|Informatica Secure Agent|

1. データ統合の定義体レベルで比較すると、下表のような対応関係になります。
    |PowerCenterの定義体|IDMCのCDIの定義体|
    |---|---|
    |ワークフロー|タスクフロー|
    |セッション|マッピングタスク|
    |マッピング|マッピング|
    |マップレット|マップレット|

# 差異の概要

公式の動画「[IICS for PowerCenter Developers: How to Navigate IICS](https://youtu.be/z0h3yEOS8F4)」 をベースに筆者の解釈を交えて説明します。
![cdi_summary.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3031738/6e38a376-f7c9-0904-99ef-c5a45a65ac39.png)

1. PowerCenterはクライアント/サーバーベースの製品でした。一方、**CDIはネイティブクラウドサービス**です。
1. PowerCenterで開発する際には、PCにクライアントツールをインストールしておく必要がありました。一方、**CDIで開発する際に使うのはウェブブラウザのみです。**
1. PowerCenterのクライアントツールでログインする際にはPowerCenterリポジトリに対してログインしていました。一方、**CDIでは各ログインはOrganization（略称：Org）に対してログインすることになります**。
1. CDIにログインすると、まず、アプリケーションピッカーが表示されます。PowerCenterのRepository ManagerやInformatica Administratorでやっていたような**管理者作業は、CDIでは、アプリケーションピッカーで「管理者」をクリックすると表示される「管理者」画面にておこないます**。
1. **PowerCenterの「マッピング」に相当する定義体は、CDIでも「マッピング」です**。マッピングの詳細は [公式ドキュメント](https://docs.informatica.com/ja_jp/integration-cloud/cloud-data-integration/current-version/_mappings_cloud-data-integration_current-version_ditamap/GUID-77317084-6A22-4BDC-920E-A5741F2A5BF9.html) をご覧ください。
1. CDIの「マッピング」を作るためには、アプリケーションピッカーにて「データ統合」をクリックし、「新規」＞「マッピング」をクリックします。すると、マッピングデザイナーが表示されます。これはPowerCenter Designerに非常に近いものです。
1. CDIのマッピングデザイナーの左側にトランスフォーメーション一覧が表示されています。PowerCenterで慣れ親しんだトランスフォーメーションの他に、CDIには新しいトランスフォーメーションもあります。
1. PowerCenterでは、トランスフォーメーション内に「ポート」があり、他のトランスフォーメーションの「ポート」と接続していました。一方、**CDIのトランスフォーメーションには「ポート」という概念がありません。「フィールドルール」と「フィールドマッピング」にて接続します。**
1. **PowerCenterでの「セッション」に相当する定義体は、CDIでは「マッピングタスク」です**。
1. PowerCenterでは、「セッション」を作るのにクライアントツールをWorkflow Managerに切り替える必要がありました。一方、CDIの「マッピングタスク」を作るためには、マッピングキャンバスのままで、画面左で「新規」＞「マッピングタスク」をクリックすると作れます。
1. **PowerCenterの「ワークフロー」に相当する定義体は、CDIでは「タスクフロー」です**。
1. CDIでは、マッピングデザイナーのままで、画面左で「新規」＞「タスクフロー」をクリックすると作れます。
1. PowerCenterでは、実行結果を確認するためにWorkflow Managerを使用していました。一方、**CDIでは画面左の「マイジョブ」をクリックすると実行結果を確認できます**。
1. PowerCenterでは、マッピングにおいてパラメーターファイルを使用することができました。一方、**CDIでも、パラメータファイルを使用することができます。**
1. PowerCenterでは、マッピングやワークフローをコマンドで実行できました。一方、**CDIでも、タスクやタスクフローをコマンドで実行できます。**
1. PowerCenterでは、チームベース開発オプションを購入している場合、バージョン管理ができました。一方、**CDIではデフォルトで、「[GitHub](https://github.com/)」または「[Azure DevOps Git](https://learn.microsoft.com/ja-jp/azure/devops/repos/git/create-new-repo?view=azure-devops)」によるバージョン管理に対応しています。**
1. PowerCenterでは、リポジトリ内のオブジェクトをファイルにエクスポート/インポートできました。一方、**CDIでもCloud Servicesのリポジトリ内のアセットをファイルにエクスポート/インポートできます。**
1. PowerCenterでは、アップグレードしたい場合、サポートを通じてアップグレードリクエストを作成する必要がありました。そして、ソフトウェアをインストールする必要がありました。一方、**CDIでは、アップグレードは自動的に開始します。**

# コンポーネントレベルでの比較

公式の動画「[PowerCenter to IICS Basics - Component Architecture](https://youtu.be/EkIIsn5zZHU)」をベースに筆者の解釈を交えて説明します。

![cdi_architecture.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3031738/f88fb0d8-a668-9335-ee04-b15196d92719.png)

1. PowerCenterのクライアントツール（Repository Manager、PowerCenter Designer、Workflow Manager、Workflow Monitor）は、各開発者のPCにインストールされたファットなソフトウェアでした。開発者はそれらを使い、メタデータを作成し、そのメタデータはRDB上のリポジトリデータベースに格納されていました。実行時にはPowerCenter Intergration Serviceがメタデータを解釈し、統合タスクを実行していました。この他に、ドメインレベルでホストされているコアサービス（Log Service、Configuration Service、Gateway Service、Authentication Service、Administration Service、Domain Service）がありました。
1. 一方、**CDIには2つの主要なコンポーネントがあります。Informatica Cloud ServicesとInformatica Secure Agentです。** **Cloud Servicesはマルチテナントメタデータリポジトリ**であり、リポジトリの管理とメンテナンスはInformaticaがおこないます。アップグレードもInformaticaがおこないます。**Cloud Servicesは開発用のブラウザUIも提供します。** **実行時にはSecure Agentが統合タスクを実行します。** Secure Agentも自動的にセルフアップデートされます。
1. CDIのSecure Agentはクラウドにもオンプレにデプロイできます。あるいは完全にInformaticaのネットワーク上のマシンにホストされたAgentを使うこともできます。
1. **CDIのSecure Agentは、Cloud Servicesからメタデータを取得し、連携元（ソース）や連携先（ターゲット）と実データをやり取りして処理します。**（**通常のSecure Agentでは、実データはCloud Services側に送信されない。** 他のAgentでは送信されることもある ）
1. CDIのコンポーネントの詳細は、「[Informatica’s Intelligent Data Management Cloud - Security Architecture Overview](https://knowledge.informatica.com/s/article/DOC-18220?language=en_US)」をご覧ください。


# おわりに

以上、「PowerCenterとCDIの違いをまとめてみた」の第1回目でした。
**次回の第2回目は、「ソースやターゲットの設定の比較」「トランスフォーメーションの種類や使用方法の比較」「トランスフォーメーション間の接続の方法の比較」をご説明します。**
**<font color="orange">※.2022.12.20追記：第2回目を投稿しました。</font>** → **<font color="orange">[Informatica PowerCenterとCloud Data Integrationの違いをまとめてみた（第2回/全4回）](https://qiita.com/nttd-nagano/items/d97970562480724fee60)</font>**

**[IDMCのCDIは30日間の無料体験ができる](https://www.informatica.com/jp/trials/informatica-cloud.html)** ので、この機会に試してみてはいかがでしょうか。

IDMCには今回ご紹介したCDIの他にも、API統合、マスターデータ管理、データガバナンス関連など様々なサービスがあります。
**これらについても、今後、[当Organization](https://qiita.com/organizations/nttdata) の記事でご紹介していく予定ですので、ご興味がございましたらご覧ください。**

## 仲間募集

NTTデータ ソリューション事業本部 では、以下の職種を募集しています。

<details><summary>1. クラウド技術を活用したデータ分析プラットフォームの開発・構築(ITアーキテクト/クラウドエンジニア)</summary>

クラウド／プラットフォーム技術の知見に基づき、DWH、BI、ETL領域におけるソリューション開発を推進します。
https://enterprise-aiiot.nttdata.com/recruitment/career_sp/cloud_engineer

</details>

<details><summary>2. データサイエンス領域（データサイエンティスト／データアナリスト）</summary>

データ活用／情報処理／AI／BI／統計学などの情報科学を活用し、よりデータサイエンスの観点から、データ分析プロジェクトのリーダーとしてお客様のDX／デジタルサクセスを推進します。
https://enterprise-aiiot.nttdata.com/recruitment/career_sp/datascientist

</details>

<details><summary>3.お客様のAI活用の成功を推進するAIサクセスマネージャー</summary>

DataRobotをはじめとしたAIソリューションやサービスを使って、
お客様のAIプロジェクトを成功させ、ビジネス価値を創出するための活動を実施し、
お客様内でのAI活用を拡大、NTTデータが提供するAIソリューションの利用継続を推進していただく人材を募集しています。
https://nttdata-career.jposting.net/u/job.phtml?job_code=804

</details>

<details><summary>4.DX／デジタルサクセスを推進するデータサイエンティスト《管理職/管理職候補》</summary>
データ分析プロジェクトのリーダとして、正確な課題の把握、適切な評価指標の設定、分析計画策定や適切な分析手法や技術の評価・選定といったデータ活用の具現化、高度化を行い分析結果の見える化・お客様の納得感醸成を行うことで、ビジネス成果・価値を出すアクションへとつなげることができるデータサイエンティスト人材を募集しています。

https://nttdata-career.jposting.net/u/job.phtml?job_code=898

</details>

## ソリューション紹介

<details><summary> Trusted Data Foundationについて</summary><div>

～データ資産を分析活用するための環境をオールインワンで提供するソリューション～
https://www.nttdata.com/jp/ja/lineup/tdf/
最新のクラウド技術を採用して弊社が独自に設計したリファレンスアーキテクチャ（Datalake+DWH+AI/BI）を顧客要件に合わせてカスタマイズして提供します。
可視化、機械学習、DeepLearningなどデータ資産を分析活用するための環境がオールインワンで用意されており、これまでとは別次元の量と質のデータを用いてアジリティ高くDX推進を実現できます。

</div></details>


<details><summary> TDFⓇ-AM（Trusted Data Foundation - Analytics Managed Service）について</summary><div>

～データ活用基盤の段階的な拡張支援（Quick Start) と保守運用のマネジメント（Analytics Managed）をご提供することでお客様のDXを成功に導く、データ活用プラットフォームサービス～
https://www.nttdata.com/jp/ja/lineup/tdf_am/
TDFⓇ-AMは、データ活用をQuickに始めることができ、データ活用の成熟度に応じて段階的に環境を拡張します。プラットフォームの保守運用はNTTデータが一括で実施し、お客様は成果創出に専念することが可能です。また、日々最新のテクノロジーをキャッチアップし、常に活用しやすい環境を提供します。なお、ご要望に応じて上流のコンサルティングフェーズからAI/BIなどのデータ活用支援に至るまで、End to Endで課題解決に向けて伴走することも可能です。

</div></details>

<details><summary> NTTデータとInformaticaについて</summary><div>

データ連携や処理方式を専門領域として10年以上取り組んできたプロ集団であるNTTデータは、データマネジメント領域でグローバルでの高い評価を得ているInformatica社とパートナーシップを結び、サービス強化を推進しています。
https://www.nttdata.com/jp/ja/lineup/informatica/

</div></details>

<details><summary>NTTデータとTableauについて </summary><div>

ビジュアル分析プラットフォームのTableauと2014年にパートナー契約を締結し、自社の経営ダッシュボード基盤への採用や独自のコンピテンシーセンターの設置などの取り組みを進めてきました。さらに2019年度にはSalesforceとワンストップでのサービスを提供開始するなど、積極的にビジネスを展開しています。

これまでPartner of the Year, Japanを4年連続で受賞しており、2021年にはアジア太平洋地域で最もビジネスに貢献したパートナーとして表彰されました。
また、2020年度からは、Tableauを活用したデータ活用促進のコンサルティングや導入サービスの他、AI活用やデータマネジメント整備など、お客さまの企業全体のデータ活用民主化を成功させるためのノウハウ・方法論を体系化した「デジタルサクセス」プログラムを提供開始しています。
https://www.nttdata.com/jp/ja/lineup/tableau/

</div></details>

<details><summary>NTTデータとAlteryxについて </summary><div>
Alteryxは、業務ユーザーからIT部門まで誰でも使えるセルフサービス分析プラットフォームです。

Alteryx導入の豊富な実績を持つNTTデータは、最高位にあたるAlteryx Premiumパートナーとしてお客さまをご支援します。

導入時のプロフェッショナル支援など独自メニューを整備し、特定の業種によらない多くのお客さまに、Alteryxを活用したサービスの強化・拡充を提供します。

https://www.nttdata.com/jp/ja/lineup/alteryx/

</div></details>

<details><summary>NTTデータとDataRobotについて </summary><div>
DataRobotは、包括的なAIライフサイクルプラットフォームです。

NTTデータはDataRobot社と戦略的資本業務提携を行い、経験豊富なデータサイエンティストがAI・データ活用を起点にお客様のビジネスにおける価値創出をご支援します。

https://www.nttdata.com/jp/ja/lineup/datarobot/

</div></details>

<details><summary>NTTデータとDatabricksについて </summary><div>
NTTデータでは、Databricks Inc.とソリューションパートナー契約を締結し、クラウド・データプラットフォーム「Databricks」の導入・構築、および活用支援を開始しています。

NTTデータではこれまでも、独自ノウハウに基づき、ビッグデータ・AIなど領域に係る市場競争力のあるさまざまなソリューションパートナーとともにエコシステムを形成し、お客さまのビジネス変革を導いてきました。
Databricksは、これら先端テクノロジーとのエコシステムの形成に強みがあり、NTTデータはこれらを組み合わせることでお客さまに最適なインテグレーションをご提供いたします。

https://www.nttdata.com/jp/ja/lineup/databricks/

</div></details>
