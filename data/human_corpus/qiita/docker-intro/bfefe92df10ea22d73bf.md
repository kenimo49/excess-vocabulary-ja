# はじめに
セキュリティに係る仕事をしています。2023年も終わりが近づいていますが、今年に入ってからSBOMの単語を聞く機会が増えた1年だったと感じました。

本記事執筆時点でGoogle トレンドで検索すると、以下のような結果が確認できました。

![スクリーンショット 2023-12-18 19.50.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/221759/3d56224d-9c37-cac3-8aee-c1615b681074.png)

2021年の12月頃からGoogle トレンドの変化が見受けられます。近年SBOMが注目されるようになったのには、何か理由があるのでしょうか？

本記事では、背景からSBOMを理解するためにSBOMの基礎的なことについてまとめています。

## SBOM
**SBOM**は、Software Bill of Materialsの略称です。

ソフトウェア製品に含まれるコンポーネントやライブラリ、依存関係などの情報をリスト化した文書またはデータ（JSONやXMLなど）のことを指します。

2021年、米国商務省の機関である[National Telecommunications and Information Administration](https://en.wikipedia.org/wiki/National_Telecommunications_and_Information_Administration)（以下、NTIA）によって、SBOMが果たす重要な役割を記載した[SBOM at a Glance](https://www.ntia.gov/files/ntia/publications/sbom_at_a_glance_apr2021.pdf)が発行されています。日本語訳は、[SBOM at a Glance（翻訳）](https://www.ntia.gov/files/ntia/publications/sbom_at_a_glance_ja.pdf)から閲覧できます。

::: note
SBOMを活用することで、ソフトウェアに関する最新の依存関係の情報を確保することができます。また、標準化されたフォーマットを用いてレビューを簡素化します。
:::

### 背景
2020年12月頃に発覚した米国の[SolarWinds](https://en.wikipedia.org/wiki/SolarWinds)社の製品であるOrion Platformに仕掛けられたバックドアのサイバー攻撃が発端と言われています。詳細については、以下の記事が参考になります。

- [米露関係におけるSolarWinds社サイバーセキュリティ事案](https://www.jiia.or.jp/research-report/russia-fy2021-01.html)

上記米国でのサイバー攻撃を踏まえて、2021年5月、大統領令として以下**Executive Order (EO) 14028**が署名及び公開されました。

- [M-22-18](https://www.whitehouse.gov/wp-content/uploads/2022/09/M-22-18.pdf)

従ってこの事件によって米国政府機関も攻撃対象になったことから、注目を集めることになり、**ソフトウェアサプライチェーンの透明性**が重要視されることとなりました。上記M-22-18の文書は、ソフトウェアサプライチェーンのセキュリティの強化という主題になっています。

また、2022年9月14日、大統領行政府の機関の一つである[Office of Management and Budget](https://en.wikipedia.org/wiki/Office_of_Management_and_Budget)（以下、OMB）によって、[Enhancing the Security of the Software Supply Chain to Deliver a Secure Government Experience](https://www.whitehouse.gov/omb/briefing-room/2022/09/14/enhancing-the-security-of-the-software-supply-chain-to-deliver-a-secure-government-experience/)のガイダンスが公開されてます。

::: note
2023年6月9日、上記M-22-18は[M-23-16](https://www.whitehouse.gov/wp-content/uploads/2023/06/M-23-16-Update-to-M-22-18-Enhancing-Software-Security-1.pdf)へアップデートされています。Mから始まる番号は、OMBによって管理されています。
:::

### 目的
SBOMの目的は、セキュリティの観点から法的コンプライアンスや脆弱性管理などリスク評価を行うことです。

従ってソフトウェアの構成要素を正確に識別し、その関係性や依存関係を明確にするために使用されます。

昨今では、ソフトウェアサプライチェーンの透明性を高める手段としても注目されています。

SBOMを開発プロセスに導入することで、以下のようなメリットが挙げられます。

- 脆弱性管理
    - 脆弱性を持つコンポーネントの早期検出及び脆弱性が公表された際にSBOMの情報と突合することで、迅速な対応を実現
- ライセンス管理
    - OSSや商用ライブラリの使用に関するコンプライアンスの確保及びライセンス管理の工数削減
- 開発生産性向上
    - 透明性・再利用性・依存関係の把握など間接的な開発生産性向上をもたらす

![SBOM.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/221759/3bc3edf8-5f8d-6f91-c678-321943567f21.png)

::: note
製造業で使われている[トレーサビリティ](https://ja.wikipedia.org/wiki/%E3%83%88%E3%83%AC%E3%83%BC%E3%82%B5%E3%83%93%E3%83%AA%E3%83%86%E3%82%A3)の仕組みに似ていますが、食品の成分表に例えられることが多く見受けられます。
:::

### 国内の動向
経済産業省から[ソフトウェア管理に向けたSBOM（Software Bill of Materials）の導入に関する手引 Ver. 1.0](https://www.meti.go.jp/press/2023/07/20230728004/20230728004-1-2.pdf)が公開されています。

SBOMに関する基本的な情報を提供するとともに、SBOMを実際に導入するにあたって認識・実施すべきポイントが記載されています。手引きが策定された背景については、[「ソフトウェア管理に向けたSBOM（Software Bill of Materials）の導入に関する手引」を策定しました](https://www.meti.go.jp/press/2023/07/20230728004/20230728004.html)をご参照ください。

以下のリンクからSBOMに関するタスクフォースの検討資料が参照できます。

https://www.meti.go.jp/shingikai/mono_info_service/sangyo_cyber/wg_seido/wg_bunyaodan/software/index.html

### データフォーマット
SBOMを表現するためには、データフォーマットの仕様が定められています。

[SBOM at a Glance](https://www.ntia.gov/files/ntia/publications/sbom_at_a_glance_apr2021.pdf)を踏まえて、以下のような種類が存在します。

| データ形式 | 仕様 | ツール |
|:-----------|:------------|:------------|
| SPDX       |[The Software Package Data Exchange® (SPDX®) Specification Version 2.3](https://spdx.github.io/spdx-spec/)|[Tooling Ecosystem working with SPDX](https://tiny.cc/SPDX)|
| CycloneDX  |[CycloneDX](https://cyclonedx.org/)|[Tooling Ecosystem working with CycloneDX](https://tiny.cc/CycloneDX) |
| SWID       |[ISO/IEC 19770-2:2015](https://www.iso.org/standard/65666.html) | [Tooling Ecosystem working with SWID](https://docs.google.com/document/d/1oebYvHcOhtMG8Uhnd5he0l_vhty7MsTjp6fYCOwUmwM/edit)|

::: note
歴史の長いSPDX形式が業界標準としてリードしていうように思われます。

参考：[SPDX Becomes Internationally Recognized Standard for Software Bill of Materials](https://www.linuxfoundation.org/press/featured/spdx-becomes-internationally-recognized-standard-for-software-bill-of-materials)
:::

#### SPDX
**SPD**Xは、[Software Package Data Exchange](https://ja.wikipedia.org/wiki/Software_Package_Data_Exchange)の略称です。

Linux Foundationの傘下のプロジェクトととして、SBOMに関する仕様を策定しています。また、国際標準の仕様として、[ISO/IEC 5962:2021](https://www.iso.org/standard/81870.html)が発行されています。

https://spdx.dev/

SPDXの目的は、ソフトウェア パッケージに関連するコンポーネント、ライセンス、著作権を伝達するための標準形式です。SPDXを用いることで、コンプライアンスを合理化し改善します。SPDX形式で生成される文書の説明については、[Overview](https://spdx.dev/learn/overview/)をご参照ください。

SPDXの仕様はGitHubに公開されています。[MkDocs](https://www.mkdocs.org/)で生成されているため、ローカルからも確認できます。本記事執筆時点ではSPDX 2.3が現行バージョンとなっていますが、既に次世代のSPDX 3.0が発表されています。

- [Capturing Software Vulnerability Data in SPDX 3.0](https://spdx.dev/capturing-software-vulnerability-data-in-spdx-3-0/)

https://github.com/spdx/spdx-spec

SPDXでは、**SPDX-License-Identifier**が重要視されています。例えば、[linux](https://github.com/torvalds/linux)のリポジトリを覗くと、ヘッダに以下のような記述が確認できます。

>\# SPDX-License-Identifier: GPL-2.0

SPDX-License-Identifierは、OSSライセンスをユニークな識別子で表現する仕組みです。詳細については、[Handling License Info](https://spdx.dev/learn/handling-license-info/)をご参照ください。

また、[SPDX License List](https://spdx.org/licenses/)からSPDXで管理しているライセンスのリストが確認できます。

::: note
Linuxと共に歴史を歩んできたSPDXゆえにOSSのライセンスに対するコンプライアンスの考え方が重要とされてきました。
:::

#### CycloneDX
**CycloneDX**は、Open Web Application Security Project (OWASP)が策定しているSBOMに関する仕様です。

CycloneDXの大きな特徴として、SBOMに脆弱性情報が含まれていることです。
また特定のソフトウェアコンポーネントが脆弱性の影響を受けるかどうかの判断に使われる、NTIAが定めた[**Vulnerability Exploitability eXchange (VEX)**](https://cyclonedx.org/capabilities/vex/)と呼ばれるコンテキストが含まれています。

https://cyclonedx.org/

::: note
CycloneDXはBOM内へのVEX情報の埋め込みもサポートしているため、インベントリとVEXデータの両方を記述する単一のアーティファクトが得られます。
:::

## SBOMツール
SBOMツールについて以下に記載しています。

### Microsoft
Microsoftから以下のsbom-toolが公開されています。

https://github.com/microsoft/sbom-tool

データフォーマットは、本記事執筆時点でSPDX2.2互換となっています。

spdxのリポジトリにチュートリアルとして使えるサンプルがあるので、試してみましょう。

https://github.com/spdx/spdx-examples/tree/master/software

以下はコマンドの実行例です。サンプルとして、上記spdx-examplesのexample1を使用しています。

- example
`sbom-tool generate -b <drop path> -bc <build components path> -pn <package name> -pv <package version> -ps <package supplier> -nsb <namespace uri base>`

- 実行例（macOS）
`./sbom-tool-osx-x64　generate -b ~/Downloads/spdx-examples/software/example1 -pn example1 -pv 0 -ps "spdx"`

```console
┌────────────────────────────────┬────────────────────────────────┬────────────────────────────────┬────────────────────────────────┐
│ Component Detector Id          │ Detection Time                 │ # Components Found             │ # Explicitly Referenced        │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ CocoaPods                      │ 0.13 seconds                   │ 0                              │ 0                              │
│ Go                             │ 0.13 seconds                   │ 0                              │ 0                              │
│ Gradle                         │ 0.13 seconds                   │ 0                              │ 0                              │
│ Ivy (Beta)                     │ 0.13 seconds                   │ 0                              │ 0                              │
│ Linux                          │ 0.009 seconds                  │ 0                              │ 0                              │
│ MvnCli                         │ 0.12 seconds                   │ 0                              │ 0                              │
│ Npm                            │ 0.12 seconds                   │ 0                              │ 0                              │
│ NpmLockfile3 (Beta)            │ 0.12 seconds                   │ 0                              │ 0                              │
│ NpmWithRoots                   │ 0.12 seconds                   │ 0                              │ 0                              │
│ NuGet                          │ 0.12 seconds                   │ 0                              │ 0                              │
│ NuGetPackagesConfig            │ 0.12 seconds                   │ 0                              │ 0                              │
│ NuGetProjectCentric            │ 0.13 seconds                   │ 0                              │ 0                              │
│ Pip                            │ 0.32 seconds                   │ 0                              │ 0                              │
│ Pnpm                           │ 0.12 seconds                   │ 0                              │ 0                              │
│ Poetry (Beta)                  │ 0.12 seconds                   │ 0                              │ 0                              │
│ Ruby                           │ 0.12 seconds                   │ 0                              │ 0                              │
│ RustCrateDetector              │ 0.12 seconds                   │ 0                              │ 0                              │
│ SPDX22SBOM                     │ 0.12 seconds                   │ 0                              │ 0                              │
│ Vcpkg (Beta)                   │ 0.12 seconds                   │ 0                              │ 0                              │
│ Yarn                           │ 0.12 seconds                   │ 0                              │ 0                              │
│ ────────────────────────────── │ ────────────────────────────── │ ────────────────────────────── │ ────────────────────────────── │
│ Total                          │ 0.35 seconds                   │ 0                              │ 0                              │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
##[warning]There were no packages detected during the generation workflow.
```

コマンドを実行すると、`_manifest/spdx_2.2`というフォルダが作成されます。フォルダ内を確認すると、`manifest.spdx.json`と、`manifest.spdx.json.sha256`のファイルが生成されています。

<details><summary>出力例</summary>

```json
{
  "files": [
    {
      "fileName": "./spdx2.2/example1.spdx",
      "SPDXID": "SPDXRef-File--spdx2.2-example1.spdx-6AEFFF94620BAD23A11A7134243FBD639677E9D2",
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "aadb99cbf33ebf7a83c4f6a03af7017831d4203fe401f3217584a0560d342036"
        },
        {
          "algorithm": "SHA1",
          "checksumValue": "6aefff94620bad23a11a7134243fbd639677e9d2"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseInfoInFiles": [
        "NOASSERTION"
      ],
      "copyrightText": "NOASSERTION"
    },
    {
      "fileName": "./.DS_Store",
      "SPDXID": "SPDXRef-File--.DS-Store-8CB8B61191EF7A52CB149E0503F8C72158ADB12D",
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "51d0a9b1781e5ccad916a715b8c3abdb06f790c22eeeb7d28dace0b09ef4252d"
        },
        {
          "algorithm": "SHA1",
          "checksumValue": "8cb8b61191ef7a52cb149e0503f8c72158adb12d"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseInfoInFiles": [
        "NOASSERTION"
      ],
      "copyrightText": "NOASSERTION"
    },
    {
      "fileName": "./content/src/Makefile",
      "SPDXID": "SPDXRef-File--content-src-Makefile-69A2E85696FFF1865C3F0686D6C3824B59915C80",
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "5da19033ba058e322e21c90e6d6d859c90b1b544e7840859c12cae5da005e79c"
        },
        {
          "algorithm": "SHA1",
          "checksumValue": "69a2e85696fff1865c3f0686d6c3824b59915c80"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseInfoInFiles": [
        "NOASSERTION"
      ],
      "copyrightText": "NOASSERTION"
    },
    {
      "fileName": "./content/build/hello",
      "SPDXID": "SPDXRef-File--content-build-hello-20291A81EF065FF891B537B64D4FDCCAF6F5AC02",
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "83a33ff09648bb5fc5272baca88cf2b59fd81ac4cc6817b86998136af368708e"
        },
        {
          "algorithm": "SHA1",
          "checksumValue": "20291a81ef065ff891b537b64d4fdccaf6f5ac02"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseInfoInFiles": [
        "NOASSERTION"
      ],
      "copyrightText": "NOASSERTION"
    },
    {
      "fileName": "./content/src/hello.c",
      "SPDXID": "SPDXRef-File--content-src-hello.c-20862A6D08391D07D09344029533EC644FAC6B21",
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "b4e5ca56d1f9110ca94ed0bf4e6d9ac11c2186eb7cd95159c6fdb50e8db5a823"
        },
        {
          "algorithm": "SHA1",
          "checksumValue": "20862a6d08391d07d09344029533ec644fac6b21"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseInfoInFiles": [
        "NOASSERTION"
      ],
      "copyrightText": "NOASSERTION"
    },
    {
      "fileName": "./README.md",
      "SPDXID": "SPDXRef-File--README.md-2AD48C71F53C4B392621CA9569AC0FD72FFA9B7A",
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "eb1a5e9f8c6c57d3617868ba698f17b3b69047a8f4069a27b13cc9af0346a1fe"
        },
        {
          "algorithm": "SHA1",
          "checksumValue": "2ad48c71f53c4b392621ca9569ac0fd72ffa9b7a"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseInfoInFiles": [
        "NOASSERTION"
      ],
      "copyrightText": "NOASSERTION"
    }
  ],
  "packages": [
    {
      "name": "example1",
      "SPDXID": "SPDXRef-RootPackage",
      "downloadLocation": "NOASSERTION",
      "packageVerificationCode": {
        "packageVerificationCodeValue": "c4c41cda58bc87560482ca00472310c77f3e5176"
      },
      "filesAnalyzed": true,
      "licenseConcluded": "NOASSERTION",
      "licenseInfoFromFiles": [
        "NOASSERTION"
      ],
      "licenseDeclared": "NOASSERTION",
      "copyrightText": "NOASSERTION",
      "versionInfo": "0",
      "externalRefs": [
        {
          "referenceCategory": "PACKAGE-MANAGER",
          "referenceType": "purl",
          "referenceLocator": "pkg:swid/spdx/spdx.org/example1@0?tag_id=f52a504c-79e3-4fee-8ff5-087201cfe430"
        }
      ],
      "supplier": "Organization: spdx",
      "hasFiles": [
        "SPDXRef-File--spdx2.2-example1.spdx-6AEFFF94620BAD23A11A7134243FBD639677E9D2",
        "SPDXRef-File--content-src-Makefile-69A2E85696FFF1865C3F0686D6C3824B59915C80",
        "SPDXRef-File--README.md-2AD48C71F53C4B392621CA9569AC0FD72FFA9B7A",
        "SPDXRef-File--.DS-Store-8CB8B61191EF7A52CB149E0503F8C72158ADB12D",
        "SPDXRef-File--content-build-hello-20291A81EF065FF891B537B64D4FDCCAF6F5AC02",
        "SPDXRef-File--content-src-hello.c-20862A6D08391D07D09344029533EC644FAC6B21"
      ]
    }
  ],
  "externalDocumentRefs": [],
  "relationships": [
    {
      "relationshipType": "DESCRIBES",
      "relatedSpdxElement": "SPDXRef-RootPackage",
      "spdxElementId": "SPDXRef-DOCUMENT"
    }
  ],
  "spdxVersion": "SPDX-2.2",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "example1 0",
  "documentNamespace": "https://spdx.org/spdxdocs/sbom-tool-1.8.1-446c605d-9122-4d45-9388-580d50d77512/example1/0/TSzy22bWtEaxmEZ6lQlgOw",
  "creationInfo": {
    "created": "2023-11-09T08:05:37Z",
    "creators": [
      "Organization: spdx",
      "Tool: Microsoft.SBOMTool-1.8.1"
    ]
  },
  "documentDescribes": [
    "SPDXRef-RootPackage"
  ]
}
```

</details>

example1の例では、以下のようなことが解析できます。

- **files**：個々のファイル毎にファイルの一意の識別子（SPDXID）、チェックサム (検証用の SHA1 および SHA256)、ライセンス、および著作権テキストがリスト出力されます。本記事の例では「licenseConcluded」、「licenseInfoInFiles」、および「copyrightText」はすべて「**NOASSERTION**」であり、これらのファイルに対して特定のライセンス情報が決定されていないことを示しています。
- **packages**：「example1」という名前のパッケージに関する情報が含まれています。「packageVerificationCode」は、パッケージ全体を表す単一のチェックサムです。「filesAnalyzed」フィールドは、ファイル分析が実行されたかどうか (true または false) を示します。ファイルと同様に、パッケージのライセンス情報はアサートされません。
- **externalRefs**：ソフトウェアまたはそのコンポーネントを外部から参照できる場所 (パッケージ マネージャーや他のデータベースなど) への追加のコンテキストまたはリンクを提供します。
- **relationships**：SBOMのさまざまな要素が相互にどのように関係するかを説明します。
- **spdxVersion**：SPDX-2.2のバージョンに準拠しています。
- **dataLicense**：このSBOMデータが提供されるライセンスを示します。 
- **creationInfo**：ドキュメントがいつ、誰によって作成されたかを示します。
- **documentDescribes**：通常はパッケージまたは製品が出力されます。

### GitHub
2023年3月28日、GitHubでもSBOMのエクスポート機能がリリースされています。

https://github.blog/2023-03-28-introducing-self-service-sboms/

対応しているのは、SPDX形式などいくつか制限はありますが、無料で利用できます。

SBOMのエクスポートは簡単です。リポジトリを選択して「Insights」の「Dependency graph」から「Export SBOM」を押すだけです。

### AWS
AWSでは、Amazon Inspectorの機能を用いてEC2インスタンスなどのSBOMのエクスポートができます。

Amazon Inspectorについては、以前書いた[5分で理解するAmazon Inspector](https://qiita.com/Brutus/items/eee466564134ebda3b36)をご参照ください。

なお、SBOMのエクスポートの実行は簡単ですが、事前にS3バケットとKMS（AWS Key Management Service）を作成して、それぞれ適切なアクセス制御の設定が必要です。

詳細については、公式ドキュメントの[Amazon Inspector による SBOM のエクスポート](https://docs.aws.amazon.com/ja_jp/inspector/latest/user/findings-managing-exporting-reports.html)をご確認ください。

KMSのポリシーの例を以下に記載します。


```json
{
    "Version": "2012-10-17",
    "Id": "allow-inspector",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow Amazon Inspector to use the key",
            "Effect": "Allow",
            "Principal": {
                "Service": "inspector2.amazonaws.com"
            },
            "Action": [
                "kms:Decrypt",
                "kms:GenerateDataKey*"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "123456789012"
                },
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:inspector2:ap-northeast-1:123456789012:report/*"
                }
            }
        }
    ]
}
```


::: note warn
ポリシーの設定を編集する場合は、JSONの構文エラーにご注意ください。KMSのポリシーを編集後、エラーが出力される場合は[「Policy contains a statement with one or more invalid principals (1 つ以上の無効なプリンシパルを持つステートメントがポリシーに含まれています)」という AWS KMS キーポリシーエラーを解決する方法を教えてください。](https://repost.aws/ja/knowledge-center/kms-policy-error-invalid-principals)の記事をご参照ください。
:::

以下はAmazon InspectorからSBOMのエクスポートを行う例です。

SBOM export settingsからCycloneDXまたは、SPDXのファイルタイプを選択します。Export locationについては、「S3 URI」と「KMS key」選択して、最後に「Export」を押します。

![スクリーンショット 2023-11-09 18.36.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/221759/4fd017b4-1fe1-1740-50f3-a6d6c7d12e71.png)

以下はAmazon Linux 2023のインスタンスに対して、SPDXのファイル形式でSBOMをエクスポートした例です。エクスポートしたSBOMは`.text`のファイル形式で出力されるため、json形式で出力し直しています。

- systemdのパッケージ

```json
 "packages": [
        {
            "name": "systemd",
            "versionInfo": "252.4-1161.amzn2023.0.4",
            "downloadLocation": "NOASSERTION",
            "sourceInfo": "/var/lib/rpm/Packages",
            "filesAnalyzed": false,
            "externalRefs": [
                {
                    "referenceCategory": "PACKAGE-MANAGER",
                    "referenceType": "purl",
                    "referenceLocator": "pkg:rpm/systemd@252.4-1161.amzn2023.0.4?arch=X86_64&epoch=0&upstream=systemd-252.4-1161.amzn2023.0.4.src.rpm"
                }
            ],
            "SPDXID": "SPDXRef-Package-rpm-systemd-bf566dd18100dbab408dcc7db7e42aef"
        },
```

- grub2-commonのパッケージ

```json
{
    "name": "grub2-common",
    "versionInfo": "2.06-61.amzn2023.0.7",
    "downloadLocation": "NOASSERTION",
    "sourceInfo": "/var/lib/rpm/Packages",
    "filesAnalyzed": false,
    "externalRefs": [
        {
            "referenceCategory": "PACKAGE-MANAGER",
            "referenceType": "purl",
            "referenceLocator": "pkg:rpm/grub2-common@2.06-61.amzn2023.0.7?arch=NOARCH&epoch=1&upstream=grub2-common-2.06-61.amzn2023.0.7.src.rpm"
        },
        {
            "referenceCategory": "SECURITY",
            "referenceType": "vulnerability",
            "referenceLocator": "CVE-2023-4693"
        },
        {
            "referenceCategory": "SECURITY",
            "referenceType": "vulnerability",
            "referenceLocator": "CVE-2023-4692"
        }
    ],
    "SPDXID": "SPDXRef-Package-rpm-grub2-common-a73d845f4a0af305a5847ecd9efce9ad"
},
```

### Google Cloud
GoogleもSBOMに取り組んでいます。

- [SLSA と SBOM はいかに医療分野におけるサイバーセキュリティのレジリエンスに貢献できるか](https://cloud.google.com/blog/ja/products/identity-security/identity-securityhow-slsa-and-sbom-can-help-healthcare-resiliency)

公式ドキュメントの[SBOM overview](https://cloud.google.com/artifact-analysis/docs/sbom-overview)を踏まえて、コンテナイメージをArtifact Registryに保存するときにSBOMを生成できます。また、生成されたSBOMはCloud Storageに保存されます。

::: note
Google Cloudでコンテナのイメージを管理するにあたって、Container Registryは非推奨になり、Artifact Registryに置き換わります。詳細は以前書いた[Container RegistryからArtifact Registryに移行する方法](https://qiita.com/Brutus/items/75e52a803afb4d427d8b)をご参照ください。
:::

### Docker
Dockerも2022年頃からSBOMに対する取り組みが始まっています。

- [Docker SBOMの発表:Dockerイメージの可視性を高めるための一歩](https://www.docker.com/ja-jp/blog/announcing-docker-sbom-a-step-towards-more-visibility-into-docker-images/)

現在実験段階のため、変更または将来のリリースから削除される可能性がありますが、`docker sbom`というCLIコマンドが利用できます。

https://docs.docker.com/engine/sbom/

以下は`docker sbom neo4j:4.4.5`の出力例です。

<details><summary>出力例</summary>

```console
Syft v0.43.0
 ✔ Pulled image            
 ✔ Loaded image            
 ✔ Parsed image            
 ✔ Cataloged packages      [385 packages]
NAME                                VERSION                                    TYPE         
CodePointIM                         11.0.16                                    java-archive  
FastInfoset                         1.2.16                                     java-archive  
FileChooserDemo                     11.0.16                                    java-archive  
Font2DTest                          11.0.16                                    java-archive  
HdrHistogram                        2.1.9                                      java-archive  
J2Ddemo                             11.0.16                                    java-archive  
Metalworks                          11.0.16                                    java-archive  
Notepad                             11.0.16                                    java-archive  
RoaringBitmap                       0.7.17                                     java-archive  
ST4                                 4.1                                        java-archive  
SampleTree                          11.0.16                                    java-archive  
Stylepad                            11.0.16                                    java-archive  
SwingSet2                           11.0.16                                    java-archive  
TableExample                        11.0.16                                    java-archive  
TransparentRuler                    11.0.16                                    java-archive  
WMI4Java                            1.6.3                                      java-archive  
accessors-smart                     2.4.2                                      java-archive  
adduser                             3.118                                      deb           
animal-sniffer-annotations          1.17                                       java-archive  
annotations                         4.4.5                                      java-archive  
antlr-runtime                       3.5.2                                      java-archive  
antlr4                              4.7.2                                      java-archive  
antlr4-runtime                      4.7.2                                      java-archive  
apoc                                4.4.0.3-core                               java-archive  
apt                                 2.2.4                                      deb           
argparse4j                          0.8.1                                      java-archive  
arrow-format                        6.0.0                                      java-archive  
arrow-memory-core                   6.0.0                                      java-archive  
arrow-memory-netty                  6.0.0                                      java-archive  
arrow-vector                        6.0.0                                      java-archive  
base-files                          11.1+deb11u4                               deb           
base-passwd                         3.5.51                                     deb           
bash                                5.1-2+deb11u1                              deb           
bcpkix-jdk15on                      1.69                                       java-archive  
bcprov-jdk15on                      1.69                                       java-archive  
bcutil-jdk15on                      1.69                                       java-archive  
bsdutils                            1:2.36.1-8+deb11u1                         deb           
ca-certificates                     20210119                                   deb           
caffeine                            3.0.3                                      java-archive  
commons-beanutils                   1.9.4                                      java-archive  
commons-codec                       1.14                                       java-archive  
commons-collections                 3.2.2                                      java-archive  
commons-collections4                4.2                                        java-archive  
commons-compress                    1.21                                       java-archive  
commons-configuration2              2.7                                        java-archive  
commons-io                          2.11.0                                     java-archive  
commons-io                          2.9.0                                      java-archive  
commons-lang3                       3.12.0                                     java-archive  
commons-lang3                       3.9                                        java-archive  
commons-logging                     1.2                                        java-archive  
commons-math3                       3.6.1                                      java-archive  
commons-text                        1.8                                        java-archive  
commons-text                        1.9                                        java-archive  
coreutils                           8.32-4+b1                                  deb           
cypher-ast-factory                  4.4.5                                      java-archive  
cypher-literal-interpreter          4.4.5                                      java-archive  
cypher-shell                        4.4.5                                      java-archive  
dash                                0.5.11+git20200708+dd9ef66-5               deb           
debconf                             1.5.77                                     deb           
debian-archive-keyring              2021.1.1                                   deb           
debianutils                         4.11.2                                     deb           
diffutils                           1:3.7-5                                    deb           
dpkg                                1.20.11                                    deb           
e2fsprogs                           1.46.2-2                                   deb           
eclipse-collections                 10.4.0                                     java-archive  
eclipse-collections-api             10.4.0                                     java-archive  
error_prone_annotations             2.2.0                                      java-archive  
failureaccess                       1.0                                        java-archive  
findutils                           4.8.0-1                                    deb           
flatbuffers-java                    1.12.0                                     java-archive  
gcc-10-base                         10.2.1-6                                   deb           
gcc-9-base                          9.3.0-22                                   deb           
gosu                                1.12-1+b6                                  deb           
gpgv                                2.2.27-2+deb11u2                           deb           
grep                                3.6-1                                      deb           
guava                               27.0-jre                                   java-archive  
gzip                                1.10-4+deb11u1                             deb           
hk2-api                             2.6.1                                      java-archive  
hk2-locator                         2.6.1                                      java-archive  
hk2-utils                           2.6.1                                      java-archive  
hostname                            3.23                                       deb           
init-system-helpers                 1.60                                       deb           
ipaddress                           5.3.3                                      java-archive  
istack-commons-runtime              3.0.8                                      java-archive  
j2objc-annotations                  1.1                                        java-archive  
jPowerShell                         3.0                                        java-archive  
jProcesses                          1.6.5                                      java-archive  
jackson-annotations                 2.11.4                                     java-archive  
jackson-annotations                 2.12.4                                     java-archive  
jackson-core                        2.11.4                                     java-archive  
jackson-core                        2.12.4                                     java-archive  
jackson-databind                    2.11.4                                     java-archive  
jackson-databind                    2.12.4                                     java-archive  
jackson-jaxrs-base                  2.12.4                                     java-archive  
jackson-jaxrs-json-provider         2.12.4                                     java-archive  
jackson-module-jaxb-annotations     2.12.4                                     java-archive  
jakarta.activation-api              1.2.1                                      java-archive  
jakarta.annotation-api              1.3.5                                      java-archive  
jakarta.inject                      2.6.1                                      java-archive  
jakarta.validation-api              2.0.2                                      java-archive  
jakarta.ws.rs-api                   2.1.6                                      java-archive  
jamm                                0.3.3                                      java-archive  
jansi                               2.3.2                                      java-archive  
javassist                           3.25.0-GA                                  java-archive  
javax.servlet-api                   3.1.0                                      java-archive  
javax.ws.rs-api                     2.1.1                                      java-archive  
jaxb-api                            2.3.0                                      java-archive  
jaxb-runtime                        2.3.2                                      java-archive  
jctools-core                        3.1.0                                      java-archive  
jctools-core                        3.3.0                                      java-archive  
jersey-client                       2.34                                       java-archive  
jersey-common                       2.34                                       java-archive  
jersey-container-servlet            2.34                                       java-archive  
jersey-container-servlet-core       2.34                                       java-archive  
jersey-hk2                          2.34                                       java-archive  
jersey-server                       2.34                                       java-archive  
jettison                            1.4.1                                      java-archive  
jetty-http                          9.4.43.v20210629                           java-archive  
jetty-io                            9.4.43.v20210629                           java-archive  
jetty-security                      9.4.43.v20210629                           java-archive  
jetty-server                        9.4.43.v20210629                           java-archive  
jetty-servlet                       9.4.43.v20210629                           java-archive  
jetty-util                          9.4.43.v20210629                           java-archive  
jetty-webapp                        9.4.43.v20210629                           java-archive  
jetty-xml                           9.4.43.v20210629                           java-archive  
jline-reader                        3.20.0                                     java-archive  
jline-terminal                      3.20.0                                     java-archive  
jline-terminal-jansi                3.20.0                                     java-archive  
jna                                 5.9.0                                      java-archive  
jq                                  1.6-2.1                                    deb           
jrt-fs                              11.0.16                                    java-archive  
json-smart                          2.4.2                                      java-archive  
jsr305                              3.0.2                                      java-archive  
libacl1                             2.2.53-10                                  deb           
libapt-pkg6.0                       2.2.4                                      deb           
libattr1                            1:2.4.48-6                                 deb           
libaudit-common                     1:3.0-2                                    deb           
libaudit1                           1:3.0-2                                    deb           
libblkid1                           2.36.1-8+deb11u1                           deb           
libbz2-1.0                          1.0.8-4                                    deb           
libc-bin                            2.31-13+deb11u3                            deb           
libc6                               2.31-13+deb11u3                            deb           
libcap-ng0                          0.7.9-2.2+b1                               deb           
libcom-err2                         1.46.2-2                                   deb           
libcrypt1                           1:4.4.18-4                                 deb           
libdb5.3                            5.3.28+dfsg1-0.8                           deb           
libdebconfclient0                   0.260                                      deb           
libext2fs2                          1.46.2-2                                   deb           
libffi7                             3.3-6                                      deb           
libgcc-s1                           10.2.1-6                                   deb           
libgcrypt20                         1.8.7-6                                    deb           
libgmp10                            2:6.2.1+dfsg-1+deb11u1                     deb           
libgnutls30                         3.7.1-5+deb11u1                            deb           
libgpg-error0                       1.38-2                                     deb           
libgssapi-krb5-2                    1.18.3-6+deb11u1                           deb           
libhogweed6                         3.7.3-1                                    deb           
libidn2-0                           2.3.0-5                                    deb           
libjq1                              1.6-2.1                                    deb           
libk5crypto3                        1.18.3-6+deb11u1                           deb           
libkeyutils1                        1.6.1-2                                    deb           
libkrb5-3                           1.18.3-6+deb11u1                           deb           
libkrb5support0                     1.18.3-6+deb11u1                           deb           
liblz4-1                            1.9.3-2                                    deb           
liblzma5                            5.2.5-2.1~deb11u1                          deb           
libmount1                           2.36.1-8+deb11u1                           deb           
libnettle8                          3.7.3-1                                    deb           
libnsl2                             1.3.0-2                                    deb           
libonig5                            6.9.6-1.1                                  deb           
libp11-kit0                         0.23.22-1                                  deb           
libpam-modules                      1.4.0-9+deb11u1                            deb           
libpam-modules-bin                  1.4.0-9+deb11u1                            deb           
libpam-runtime                      1.4.0-9+deb11u1                            deb           
libpam0g                            1.4.0-9+deb11u1                            deb           
libpcre2-8-0                        10.36-2                                    deb           
libpcre3                            2:8.39-13                                  deb           
libpsl5                             0.21.0-1.2                                 deb           
libseccomp2                         2.5.1-1+deb11u1                            deb           
libselinux1                         3.1-3                                      deb           
libsemanage-common                  3.1-1                                      deb           
libsemanage1                        3.1-1+b2                                   deb           
libsepol1                           3.1-1                                      deb           
libsmartcols1                       2.36.1-8+deb11u1                           deb           
libss2                              1.46.2-2                                   deb           
libssl1.1                           1.1.1n-0+deb11u3                           deb           
libstdc++6                          10.2.1-6                                   deb           
libsystemd0                         247.3-7                                    deb           
libtasn1-6                          4.16.0-2                                   deb           
libtinfo6                           6.2+20201114-2                             deb           
libtirpc-common                     1.3.1-1                                    deb           
libtirpc3                           1.3.1-1                                    deb           
libudev1                            247.3-7                                    deb           
libunistring2                       0.9.10-4                                   deb           
libuuid1                            2.36.1-8+deb11u1                           deb           
libxxhash0                          0.8.0-2                                    deb           
libzstd1                            1.4.8+dfsg-2.1                             deb           
listenablefuture                    9999.0-empty-to-avoid-conflict-with-guava  java-archive  
log4j-api                           2.17.1                                     java-archive  
log4j-core                          2.17.1                                     java-archive  
login                               1:4.8.1-1                                  deb           
logsave                             1.46.2-2                                   deb           
lsb-base                            11.1.0                                     deb           
lucene-analyzers-common             8.9.0                                      java-archive  
lucene-backward-codecs              8.9.0                                      java-archive  
lucene-core                         8.9.0                                      java-archive  
lucene-queryparser                  8.9.0                                      java-archive  
magnolia_2.12                       0.17.0                                     java-archive  
mawk                                1.3.4.20200120-2                           deb           
mercator_2.12                       0.2.1                                      java-archive  
mount                               2.36.1-8+deb11u1                           deb           
ncurses-base                        6.2+20201114-2                             deb           
ncurses-bin                         6.2+20201114-2                             deb           
neo4j                               4.4.5                                      java-archive  
neo4j-ast                           4.4.5                                      java-archive  
neo4j-batch-insert                  4.4.5                                      java-archive  
neo4j-bolt                          4.4.5                                      java-archive  
neo4j-browser                       4.4.3                                      java-archive  
neo4j-buffers                       4.4.5                                      java-archive  
neo4j-capabilities                  4.4.5                                      java-archive  
neo4j-codegen                       4.4.5                                      java-archive  
neo4j-collections                   4.4.5                                      java-archive  
neo4j-command-line                  4.4.5                                      java-archive  
neo4j-common                        4.4.5                                      java-archive  
neo4j-concurrent                    4.4.5                                      java-archive  
neo4j-configuration                 4.4.5                                      java-archive  
neo4j-consistency-check             4.4.5                                      java-archive  
neo4j-csv                           4.4.5                                      java-archive  
neo4j-cypher                        4.4.5                                      java-archive  
neo4j-cypher-ast-factory            4.4.5                                      java-archive  
neo4j-cypher-config                 4.4.5                                      java-archive  
neo4j-cypher-expression-evaluator   4.4.5                                      java-archive  
neo4j-cypher-interpreted-runtime    4.4.5                                      java-archive  
neo4j-cypher-ir                     4.4.5                                      java-archive  
neo4j-cypher-javacc-parser          4.4.5                                      java-archive  
neo4j-cypher-logical-plans          4.4.5                                      java-archive  
neo4j-cypher-macros                 4.4.5                                      java-archive  
neo4j-cypher-planner                4.4.5                                      java-archive  
neo4j-cypher-planner-spi            4.4.5                                      java-archive  
neo4j-cypher-runtime-util           4.4.5                                      java-archive  
neo4j-data-collector                4.4.5                                      java-archive  
neo4j-dbms                          4.4.5                                      java-archive  
neo4j-diagnostics                   4.4.5                                      java-archive  
neo4j-exceptions                    4.4.5                                      java-archive  
neo4j-expressions                   4.4.5                                      java-archive  
neo4j-fabric                        4.4.5                                      java-archive  
neo4j-front-end                     4.4.5                                      java-archive  
neo4j-fulltext-index                4.4.5                                      java-archive  
neo4j-graph-algo                    4.4.5                                      java-archive  
neo4j-graphdb-api                   4.4.5                                      java-archive  
neo4j-id-generator                  4.4.5                                      java-archive  
neo4j-import-tool                   4.4.5                                      java-archive  
neo4j-import-util                   4.4.5                                      java-archive  
neo4j-index                         4.4.5                                      java-archive  
neo4j-io                            4.4.5                                      java-archive  
neo4j-java-driver                   4.4.3                                      java-archive  
neo4j-kernel                        4.4.5                                      java-archive  
neo4j-kernel-api                    4.4.5                                      java-archive  
neo4j-layout                        4.4.5                                      java-archive  
neo4j-lock                          4.4.5                                      java-archive  
neo4j-logging                       4.4.5                                      java-archive  
neo4j-lucene-index                  4.4.5                                      java-archive  
neo4j-monitoring                    4.4.5                                      java-archive  
neo4j-native                        4.4.5                                      java-archive  
neo4j-parser                        4.4.5                                      java-archive  
neo4j-procedure                     4.4.5                                      java-archive  
neo4j-procedure-api                 4.4.5                                      java-archive  
neo4j-push-to-cloud                 4.4.5                                      java-archive  
neo4j-record-storage-engine         4.4.5                                      java-archive  
neo4j-resource                      4.4.5                                      java-archive  
neo4j-rewriting                     4.4.5                                      java-archive  
neo4j-schema                        4.4.5                                      java-archive  
neo4j-security                      4.4.5                                      java-archive  
neo4j-server                        4.4.5                                      java-archive  
neo4j-spatial-index                 4.4.5                                      java-archive  
neo4j-ssl                           4.4.5                                      java-archive  
neo4j-storage-engine-api            4.4.5                                      java-archive  
neo4j-storage-engine-util           4.4.5                                      java-archive  
neo4j-token-api                     4.4.5                                      java-archive  
neo4j-unsafe                        4.4.5                                      java-archive  
neo4j-util                          4.4.5                                      java-archive  
neo4j-values                        4.4.5                                      java-archive  
neo4j-wal                           4.4.5                                      java-archive  
netty-buffer                        4.1.68.Final                               java-archive  
netty-buffer                        4.1.73.Final                               java-archive  
netty-codec                         4.1.73.Final                               java-archive  
netty-codec-http                    4.1.73.Final                               java-archive  
netty-common                        4.1.68.Final                               java-archive  
netty-common                        4.1.73.Final                               java-archive  
netty-handler                       4.1.73.Final                               java-archive  
netty-resolver                      4.1.73.Final                               java-archive  
netty-tcnative-classes              2.0.46.Final                               java-archive  
netty-transport                     4.1.73.Final                               java-archive  
netty-transport-classes-epoll       4.1.73.Final                               java-archive  
netty-transport-native-epoll        4.1.73.Final                               java-archive  
netty-transport-native-unix-common  4.1.73.Final                               java-archive  
opencsv                             4.6                                        java-archive  
openssl                             1.1.1n-0+deb11u3                           deb           
p11-kit                             0.23.22-1                                  deb           
p11-kit-modules                     0.23.22-1                                  deb           
parboiled-core                      1.2.0                                      java-archive  
parboiled-scala_2.12                1.2.0                                      java-archive  
passwd                              1:4.8.1-1                                  deb           
perl-base                           5.32.1-4+deb11u2                           deb           
picocli                             4.6.1                                      java-archive  
publicsuffix                        20211207.1025-0+deb11u1                    deb           
reactive-streams                    1.0.3                                      java-archive  
reactor-core                        3.4.11                                     java-archive  
scala-library                       2.12.13                                    java-archive  
scala-reflect                       2.12.13                                    java-archive  
sed                                 4.7-1                                      deb           
server-api                          4.4.5                                      java-archive  
shiro-cache                         1.8.0                                      java-archive  
shiro-config-core                   1.8.0                                      java-archive  
shiro-config-ogdl                   1.8.0                                      java-archive  
shiro-core                          1.8.0                                      java-archive  
shiro-crypto-cipher                 1.8.0                                      java-archive  
shiro-crypto-core                   1.8.0                                      java-archive  
shiro-crypto-hash                   1.8.0                                      java-archive  
shiro-event                         1.8.0                                      java-archive  
shiro-lang                          1.8.0                                      java-archive  
slf4j-api                           1.7.25                                     java-archive  
slf4j-api                           1.7.30                                     java-archive  
slf4j-nop                           1.7.30                                     java-archive  
snakeyaml                           1.26                                       java-archive  
stax-ex                             1.8.1                                      java-archive  
sysvinit-utils                      2.96-7+deb11u1                             deb           
tar                                 1.34+dfsg-1                                deb           
tini                                0.19.0-1                                   deb           
txw2                                2.3.2                                      java-archive  
tzdata                              2021a-1+deb11u4                            deb           
util-linux                          2.36.1-8+deb11u1                           deb           
wget                                1.21-1+deb11u1                             deb           
zlib1g                              1:1.2.11.dfsg-2+deb11u1                    deb           
zstd-jni                            1.5.0-4                                    java-archive  
zstd-proxy                          4.4.5                                      java-archive 
```
</details>

オプションを使用して、SPDXまたはCycloneDX形式で出力ができます。以下はalpineイメージについて、SPDXでSBOMを生成する例です。

`docker sbom alpine:latest --format spdx-json --output alpine-sbom.json`

また、Docker Desktop 4.18以降のバージョンでは[Docker Scout](https://docs.docker.com/scout/)の機能を介してSBOMを生成することもできます。

https://docs.docker.com/engine/reference/commandline/scout_sbom/

`docker scout sbom`コマンドの引数にイメージ名を指定して実行します。

- Nginxの例
`docker scout sbom nginx`

### Trivy
Trivyは、コンテナイメージなどをスキャン可能なセキュリティスキャナーです。

現在はAqua Security社の元、引き続きOSSとして利用が可能です。

https://github.com/aquasecurity/trivy

以下のようなコマンドを実行することで、SBOMを出力できます。SPDXと、CycloneDX形式それぞれサポートされています。

`$ trivy image --format spdx-json --output spdx.json alpine:3.16.0`

### syftとgrype
syftは、コンテナイメージやファイルシステムからSBOMを生成することができるCLIツールです。

https://github.com/anchore/syft

grypeと連携することも可能です。

https://github.com/anchore/grype

## 課題
SBOMについては導入に関する課題が活発に議論されています。

NTIAで公開されている参考文献の一部を中心に見てみましょう。

### Software Suppliers Playbook:SBOM Production and Provision
2021年、[Software Suppliers Playbook:SBOM Production and Provision](https://www.ntia.gov/files/ntia/publications/software_suppliers_sbom_production_and_provision_-_final.pdf)の文書が公開されています。

この文書では、SBOM作成手順やSBOM作成に当たって考慮すべき事項及びSBOMに関する補足事項についてまとめられています。

- SBOM作成手順
    - コンポーネントの特定
    - コンポーネント情報を取得
    - SBOM形式への出力
    - SBOMの検証
- SBOM作成に当たって考慮すべき事項
    - SBOM作成の自動化
    - コンテナイメージに対するSBOMの作成
    - SBOM作成日時の明確化
    - SBOMに含まれる情報の明確化
    - 外部サービスの明確化
- SBOMに関する補足事項
    - SBOMの知的財産/機密性
    - SBOMフォーマットの検証
    - コンポーネント情報の検証

### SBOM Myths vs. Facts
2021年、[SBOM Myths vs. Facts](https://www.ntia.gov/files/ntia/publications/sbom_myths_vs_facts_nov2021.pdf)の文書が公開されています。

翻訳すると「SBOMの神話と事実」とうタイトルで、SBOMに関する誤解と事実について語れています。

経済産業省の公開している[ソフトウェア管理に向けたSBOMの導入に関する手引](https://www.meti.go.jp/press/2023/07/20230728004/20230728004-1-2.pdf)のp27から、翻訳した内容が確認できます。

### Survey of Existing SBOM　Formats and Standards
2019年、[Survey of Existing SBOM Formats and Standards](https://www.ntia.gov/files/ntia/publications/ntia_sbom_formats_and_standards_whitepaper_-_version_20191025.pdf)の文書が公開されています。

この文書はNTIAのワーキンググループが既存のSBOMフォーマットについて調査した内容を報告書としてまとめた文書です。

従ってこの文書を読むことで、今から数年前の時点でどのような課題が見えていたのかが分かります。

p19以降を見ると、以下のような課題が取り上げられていました。

- Software Identifier challenges
- Tooling challenges
- SBOM Delivery and Distribution challenges
- Software Component Modification
- SBOM formats for higher trust and provenance

### Other
米国のセキュリティ会社であるReversingLabs社のブログの[Docker's BuildKit adds SBOM attestation capabilities: How they work — and key limitations](https://www.reversinglabs.com/blog/dockers-buildkit-adds-supply-chain-security-features)から、ビルド時の認証が重要視されていることが分かります。

# おわりに
SBOMは、Society 5.0と呼ばれるサイバー空間（仮想空間）とフィジカル空間（現実空間）を高度に融合したシステムによって、経済発展と社会的課題の解決を両立する新しい未来社会を実現するために必要な要素です。

昨今はChatGPTなどLLMに目が行きがちですが、セキュリティも日々発展しています。

ソフトウェア開発を行うにあたり、プロダクトのセキュリティを高めるための手段として、ご参考になれば幸いです。
