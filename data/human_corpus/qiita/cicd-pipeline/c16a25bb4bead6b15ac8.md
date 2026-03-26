Oracle が提供する Wercker が、2022年10月31日をもってサービスを終了するというアナウンスがありました。

> Important Notice: Wercker service will be shutdown on October 31st, 2022 . We recommend you to use OCI DevOps service. Thank you for using Wercker. 
>
> 引用元: https://devcenter.wercker.com

私が所属する会社では Wercker を使用して CI を実行していたので、他 CI ツールへの移行が必要でした。
そこで移行先の検討に伴い、以下のサービスを調査し、最も安く済むのはどれかをまとめました。

- [AWS CodeBuild](https://aws.amazon.com/codebuild/)
- [CircleCI](https://circleci.com/)
- [GitHub Actions](https://github.co.jp/features/actions)

## 前提

以下の開発状況を前提に調査を行なっています。

- CI 実行にかかっている時間
    - 1度の CI 実行で **約60分** ほどかかっている。
    - 1ヶ月に **約200回** ほど CI を実行している。
    - つまり、CI 実行にかかる時間は **1ヶ月で約12,000分** ほどである。
- GitHub プラン
    - GitHub アカウントは **Pro プラン** で契約をしている。

## 結論
私が所属する会社の開発状況においては **GitHub Actions** を使用することで最も安く済むことがわかりました。

||AWS CodeBuild|CircleCI|GitHub Actions|
|:--|:--:|:--:|:--:|
|OS|Linux|Docker/Linux|Linux|
|メモリ|7GB|8GB|7GB|
|CPU|4|4|2|
|1ヶ月の固定額|$5 (=1+4)|$19 (=15+4)|$4|
|1ヶ月の無料時間枠|100分|2750分|3000分|
|1ヶ月あたり有料で賄う時間|11,900分|9,250分|9,000分|
|1分あたりの料金|$0.01|$0.012|$0.008|
|1ヶ月の支払額($)|$124|$130|$76|

**備考**
- OS とメモリを近い条件にして比較しています。
- AWS CodeBuild は AWS CodePipeline との併用を前提とし、その利用料を固定額に含めています。
- AWS CodeBuild は `US East(N. Virginia)` リージョンで計算しています。
- AWS CodeBuild と CircleCI は別途 GitHub の利用が必要なので Pro プランの固定費も含めています。

## 調査内容
### AWS CodeBuild

**利用するサービス**

調査したところ、 [AWS CodePipeline](https://aws.amazon.com/codepipeline/) を利用して、 AWS CodeBuild を設定するというのが一般的のようでした。
なので、利用するサービスは以下になります。

- GitHub
- AWS CodePipeline
- AWS CodeBuild

<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/186009/8c7f90c0-4e94-f28f-06ae-1b98c6647e64.png" style="text-align:center;">

**GitHub の利用料金**

Pro アカウントを利用しているので、1ヶ月で **$4** かかります。 

**AWS CodePipeline の利用料金**

毎月アクティブなパイプライン1つにつき **$1** かかります。

**AWS CodeBuild の1分あたりの利用料金**

1分あたり `$0.001` かかります。

**AWS CodeBuild の無料枠**

毎月 100分 まで、無料で利用することができます。

**1ヶ月の CI 実行にかかる費用**

1分あたり `$0.001` かかるので、無料枠を差し引いた 11,900分 利用すると、 **$119** かかる計算になります。

**📝参考サイト**

- https://aws.amazon.com/free
- https://aws.amazon.com/codebuild/pricing/
- https://aws.amazon.com/codepipeline/pricing/
- https://onetech.jp/blog/what-is-aws-ci-cd-12718
- https://qiita.com/tatsuya___/items/cf81a11fdb7e54bb3890
- https://www.stylez.co.jp/columns/flow_of_cicd_implementation_using_aws/

### CircleCI

**GitHub の利用料金**

Pro アカウントを利用しているので、1ヶ月で **$4** かかります。 

**CircleCI の利用プラン**

メモリ 8GB のマシンを利用する場合、1分で 20credit 消費されます。
Free プランは毎月 30,000credit まで利用可能なので、時間に換算すると 1,500分 までしか利用できません。
よって、 Performance プランを選択する必要がありました。

**Performance プランの利用料金**

固定で1ヶ月で `$15` がかかります。

**Performance プランの無料枠**

また 55,000credit が無料枠として付与されるので、時間換算で 2,750分 は無料枠でまかなえます。

**従量課金部分の料金体系**

無料枠を使い終わった後は、 25,000credit を `$15` で追加購入する形となります。

**1分あたりの利用料金**

メモリ 8GB のマシンで 25,000credit を利用すると、 1,250分 を CI 実行に利用できます。
つまり、 12,500分 で `$15` かかることになるので、1分あたり `$0.012` かかるとわかります。

**1ヶ月の CI 実行にかかる費用**

1分あたり `$0.012` かかるので、無料枠を差し引いた 9,250分 利用すると、 **$111** かかる計算になります。


**📝参考サイト**

- https://circleci.com/pricing/
- https://circleci.com/product/features/resource-classes/

### GitHub Actions

**GitHub の利用料金**

Pro アカウントを利用しているので、1ヶ月で **$4** かかります。

**GitHub Actions の無料枠**

Pro アカウントだと 3,000分 の無料枠が付与されます。

**1分あたりの利用料金**

Linux OS の場合ですが、1分あたり `$0.008` がかかります。
（macOS だと `$0.08` 、 Windows だと `$0.016` かかります。）

**1ヶ月の CI 実行にかかる費用**

1分あたり `$0.008` かかるので、無料枠を差し引いた 9,000分 利用すると、 **$72** かかる計算になります。

**📝参考サイト**

- https://docs.github.com/en/get-started/learning-about-github/githubs-products
- https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners
- https://docs.github.com/en/enterprise-cloud@latest/billing/managing-billing-for-github-actions/about-billing-for-github-actions

