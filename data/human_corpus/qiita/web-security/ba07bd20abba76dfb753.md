## はじめに

本記事は [Snykを使ってコードをセキュアにした記事を投稿しよう！ by Snyk Advent Calendar 2023](https://qiita.com/advent-calendar/2023/snyk) の 17日目の記事になります。 [^1]

[^1]: 執筆時点で17日が空いてましたので後埋めしています

## 脆弱なAWS環境とは？

意図しないS3バケットの公開、不完全なセキュリティグループ、ロギングの欠如など、脆弱性を作り込んでしまった環境になります。

## CloudGoatとは？

Rhino Security Labs社が提供している脆弱性が作り込まれたAWS環境をデプロイすることができるツールです。
複数のシナリオが用意されており、攻撃者視点に立ってシナリオを進めることで、攻撃者がどこに着目して攻撃をするのかを学習することができます。

シナリオの例はNEC社が公開しておりますので興味のある方はご参照ください。

https://jpn.nec.com/cybersecurity/blog/211001/index.html

## チェックする

### Snyk CLIをインストールする　

Snyk CLIをインストールします。

```console
$ brew install snyk-cli
$ snyk --version
1.1260.0
```

brewを使用しましたが環境にあわせて複数の方法が提供されていますので、お好みの方法でインストールをしてください。

https://docs.snyk.io/snyk-cli/install-or-update-the-snyk-cli

### CloudGoatをダウンロードする

事前にチェックするため[CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat)をダウンロードします。

```console
$ git clone https://github.com/RhinoSecurityLabs/cloudgoat
$ cloudgoat
$ git log --oneline -n 1
7333d0f (HEAD -> master, origin/master, origin/HEAD) Update ec2.tf to use latest Linux AMI
```

### Snykの認証設定をする

以下のコマンドを実行して認証をします。ブラウザが起動するためSnykにログインして認証することでコマンドが使用できます。

```console
$ snyk auth
```

詳細は以下の公式マニュアルをご参照ください。

https://docs.snyk.io/snyk-cli/authenticate-the-cli-with-your-account

### チェックする

ここまでで準備が整いましたので、テストをします。
テスト対象はNECさまのブログでも紹介されてます[ec2_ssrf](https://github.com/RhinoSecurityLabs/cloudgoat/blob/master/scenarios/ec2_ssrf/README.md)です。

```console
$ cd scenarios/ec2_ssrf
$ snyk iac test

Snyk Infrastructure as Code

✔ Test completed.

Issues

Low Severity Issues: 12

  [Low] EC2 API termination protection is not enabled
  Info:    To prevent instance from being accidentally terminated using Amazon
           EC2, you can enable termination protection for the instance. Without
           this setting enabled the instances can be terminated by accident.
           This setting should only be used for instances with high availability
           requirements. Enabling this may prevent IaC workflows from updating
           the instance, for example terraform will not be able to terminate the
           instance to update instance type
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-AWS-426
  Path:    resource > aws_instance[cg-ubuntu-ec2] > disable_api_termination
  File:    terraform/ec2.tf
  Resolve: Set `disable_api_termination` attribute  with value `true`

  [Low] EC2 instance accepts IMDSv1
  Info:    Instance Metadata Service v2 is not enforced. Metadata service may be
           vulnerable to reverse proxy/open firewall misconfigurations and
           server side request forgery attacks
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-130
  Path:    resource > aws_instance[cg-ubuntu-ec2] > metadata_options
  File:    terraform/ec2.tf
  Resolve: Set `metadata_options.http_tokens` attribute to `required`

  [Low] Resource has public IP assigned
  Info:    AWS resource could be accessed externally via public IP. Increases
           attack vector reachability
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-51
  Path:    resource > aws_instance[cg-ubuntu-ec2] > associate_public_ip_address
  File:    terraform/ec2.tf
  Resolve: Set `associate_public_ip_address` attribute to `false`

  [Low] AWS Security Group allows open egress
  Info:    The inline security group rule allows open egress. Open egress can be
           used to exfiltrate data to unauthorized destinations, and enable
           access to potentially malicious resources
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-73
  Path:    resource > aws_security_group[cg-ec2-http-security-group] > egress
  File:    terraform/ec2.tf
  Resolve: Set `egress.cidr_blocks` attribute to specific ranges e.g.
           `192.168.1.0/24`

  [Low] AWS Security Group allows open egress
  Info:    The inline security group rule allows open egress. Open egress can be
           used to exfiltrate data to unauthorized destinations, and enable
           access to potentially malicious resources
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-73
  Path:    resource > aws_security_group[cg-ec2-ssh-security-group] > egress
  File:    terraform/ec2.tf
  Resolve: Set `egress.cidr_blocks` attribute to specific ranges e.g.
           `192.168.1.0/24`

  [Low] IAM Policy attached to user
  Info:    The IAM policy is directly attached to a user. Increases the security
           management overhead
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-116
  Path:    resource > aws_iam_user_policy_attachment[cg-solus-attachment]
  File:    terraform/iam.tf
  Resolve: Attach policy to a group or role, instead of user. For example, use
           `aws_iam_group_policy_attachment` resource

  [Low] IAM Policy attached to user
  Info:    The IAM policy is directly attached to a user. Increases the security
           management overhead
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-116
  Path:    resource > aws_iam_user_policy_attachment[cg-shepard-attachment]
  File:    terraform/iam.tf
  Resolve: Attach policy to a group or role, instead of user. For example, use
           `aws_iam_group_policy_attachment` resource

  [Low] IAM Policy attached to user
  Info:    The IAM policy is directly attached to a user. Increases the security
           management overhead
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-116
  Path:    resource > aws_iam_user_policy_attachment[cg-wrex-attachment]
  File:    terraform/iam.tf
  Resolve: Attach policy to a group or role, instead of user. For example, use
           `aws_iam_group_policy_attachment` resource

  [Low] X-ray tracing is disabled for Lambda function
  Info:    Amazon X-Ray tracing is not enabled for Lambda function. Trace logs
           will not be available during investigation
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-133
  Path:    resource > aws_lambda_function[cg-lambda-function] > tracing_config
  File:    terraform/lambda.tf
  Resolve: Set `tracing_config.mode` attribute to `Active` or `PassThrough`

  [Low] S3 bucket versioning disabled
  Info:    S3 bucket versioning is disabled. Changes or deletion of objects will
           not be reversible
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-124
  Path:    resource > aws_s3_bucket[cg-secret-s3-bucket] > versioning > enabled
  File:    terraform/s3.tf
  Resolve: For AWS provider < v4.0.0, set `versioning.enabled` attribute to
           `true`. For AWS provider >= v4.0.0, add aws_s3_bucket_versioning
           resource.

  [Low] S3 bucket MFA delete control disabled
  Info:    S3 bucket will not enforce MFA login on delete requests. Object could
           be deleted without stronger MFA authorization
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-127
  Path:    resource > aws_s3_bucket[cg-secret-s3-bucket] > versioning >
           mfa_delete
  File:    terraform/s3.tf
  Resolve: Follow instructions in `https://docs.aws.amazon.com/AmazonS3/latest/u
           serguide/MultiFactorAuthenticationDelete.html` to manually configure
           the MFA setting. For AWS provider < v4.0.0 set
           `versioning.mfa_delete` attribute to `true` in aws_s3_bucket
           resource. For AWS provider >= v4.0.0 set
           'versioning_configuration.mfa_delete` attribute to `Enabled`. The
           terraform change is required to reflect the setting in the state file

  [Low] S3 server access logging is disabled
  Info:    The s3 access logs will not be collected. There will be no audit
           trail of access to s3 objects
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-45
  Path:    input > resource > aws_s3_bucket[cg-secret-s3-bucket] > logging
  File:    terraform/s3.tf
  Resolve: For AWS provider < v4.0.0, add `logging` block attribute. For AWS
           provider >= v4.0.0, add aws_s3_bucket_logging resource.

Medium Severity Issues: 1

  [Medium] Non-Encrypted root block device
  Info:    The root block device for ec2 instance is not encrypted. That should
           someone gain unauthorized access to the data they would be able to
           read the contents.
  Rule:    https://security.snyk.io/rules/cloud/SNYK-CC-TF-53
  Path:    resource > aws_instance[cg-ubuntu-ec2] > root_block_device >
           encrypted
  File:    terraform/ec2.tf
  Resolve: Set `root_block_device.encrypted` attribute to `true`

-------------------------------------------------------

Test Summary

  Organization: **********
  Project name: ec2_ssrf

✔ Files without issues: 6
✗ Files with issues: 4
  Ignored issues: 0
  Total issues: 13 [ 0 critical, 0 high, 1 medium, 12 low ]

-------------------------------------------------------

Tip

  New: Share your test results in the Snyk Web UI with the option --report
```

## 結果を確認する

### Low

Lowレベルを確認しましたが、有益ではあるものの致命的な脆弱性を検出はしてくれませんでした。 

- AWS Security Group allows open egress: すべての宛先への通信が許可されている
- EC2 API termination protection is not enabled: 終了保護が有効化されていないため謝ってインスタンスが終了する可能性がある
- EC2 instance accepts IMDSv1： IMDSv1が許容されている
- IAM Policy attached to user: IAMポリシーがIAMユーザに直接添付されている
- Resource has public IP assigned: インスタンスにパブリックIPがアサインされているため攻撃を受ける可能性がある
- S3 bucket MFA delete control disabled: S3のバケット削除にMFAが有効化されていない
- S3 bucket versioning disabled: S3のバージョニングが無効化
- S3 server access logging is disabled: S3のアクセスログが無効化
- X-ray tracing is disabled for Lambda function: X-Rayが無効化

### Medium

MediumレベルもLowと同様に有益ではあるものの、致命的な脆弱性を検出はしてくれませんでした。 

- Non-Encrypted root block device: ルートブロックデバイスが暗号化されていない

## 検出してほしかった脆弱性

`ec2_ssrf`では漏洩したIAMユーザのクレデンシャル情報を利用し、情報を確認していくのですが、そのなかでlambda functionの情報を確認することができます。

lambda functionの環境変数にEC2にアクセスするための情報を環境変数で平文で渡しているため、攻撃者にさらなる攻撃の糸口を与えてしまい、被害が拡大してしまいます。

コードを見ると以下のとおり環境変数に渡していることが確認できました。

```tf:RhinoSecurityLabs/cloudgoat/blob/master/scenarios/ec2_ssrf/terraform/lambda.tf
resource "aws_lambda_function" "cg-lambda-function" {
  filename = "../assets/lambda.zip"
  function_name = "cg-lambda-${var.cgid}"
  role = "${aws_iam_role.cg-lambda-role.arn}"
  handler = "lambda.handler"
  source_code_hash = "${data.archive_file.cg-lambda-function.output_base64sha256}"
  runtime = "python3.9"
  environment {
      variables = {
          EC2_ACCESS_KEY_ID = "${aws_iam_access_key.cg-wrex.id}"
          EC2_SECRET_KEY_ID = "${aws_iam_access_key.cg-wrex.secret}"
      }
  }
```

https://github.com/RhinoSecurityLabs/cloudgoat/blob/master/scenarios/ec2_ssrf/terraform/lambda.tf

PoCの段階では環境変数+平文といった実装を見かけることもありますが、そのままプロダクションに反映されてしまいますと、脆弱性が残存した状態になりますので、暗号化して渡すなり、AWS Systems Manager Parameter Store　/ AWS Secrets Managerの利用が重要になります。

これらの使い方についてはFlatt Security社のブログで解説がありました。

https://blog.flatt.tech/entry/lambda_secret_security

## まとめ

今回はSnykを使ってTerraformでデプロイされる脆弱なAWS環境(CloudGoat)を事前にチェックできるか実験してみました。

期待する脆弱性は検知できませんでしたが、よくあるセキュリティの設定ミス(とくにロギング周りの設定漏れが検出できたのは大きい)がチェックできていることが確認できました。[^2]

[^2]: 執筆時点の情報になります。Snykは進化が早いので今後に期待

デプロイされてからのチェックは大変だと思いますので、`snyk iac`を使ってデプロイ前にチェックし、セキュアな環境をデプロイできるようにしていきましょう！

