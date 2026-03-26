## はじめに

```
$ whoami
linux_engineer
$ uname -a
Linux prod-server 5.15.0 #1 SMP x86_64 GNU/Linux
```

「Windowsのセキュリティ？ 情シスやPC管理者の仕事でしょ？」

そう思っているLinuxエンジニアの方に、まず一つ質問させてください。

**あなたの会社のActive Directoryが侵害されたとき、Linuxサーバーは安全でいられますか？**

現代のエンタープライズ環境において、「Linuxだけで完結するシステム」はほぼ存在しません。バックエンドがLinuxであっても、運用管理端末はWindows、認証基盤はActive Directory（AD）、開発者の手元にはWindows PCがある——これが現実です。

攻撃者は防御が薄く特権が集中した「Windows認証基盤」を起点に、あなたが管理するLinuxサーバーへと侵入経路を広げます。実際、2023年のMOVEit Transfer脆弱性や、SolarWindsサプライチェーン攻撃など、近年の大規模インシデントの多くはWindows基盤への侵害を含んでいました。

本連載では、CLIを愛するLinuxエンジニアの視点から、Windowsセキュリティの本質を**全50回**にわたって解剖していきます。

---

## 1. Linuxエンジニアが陥る「Windowsの罠」

Linuxの世界では、設定変更は `/etc` 以下のテキストファイルを編集し、`systemctl restart` で完結します。しかしWindowsを触り始めると、いくつかの「文化の壁」にぶつかります。

### 罠①：「とりあえず管理者で実行」の危うさ

Linuxで `sudo` を多用するのが危険なように、Windowsで常に管理者権限（Administrator）で作業することは重大なリスクです。

Linuxの `root` と一見似ていますが、Windowsには**整合性レベル（Integrity Level）** という独自の概念があります。

| 整合性レベル | 相当するLinuxの概念 | 主な用途 |
|---|---|---|
| System | root（カーネル領域） | OS中枢プロセス |
| High | sudo 実行時 | 管理者権限が必要な処理 |
| Medium | 一般ユーザー実行 | 通常のアプリケーション |
| Low | 制限付き環境 | サンドボックス（ブラウザ等） |

攻撃者は管理者権限で動作するプロセスに「プロセスインジェクション」や「トークン奪取（Token Impersonation）」を仕掛けます。常時Administratorで作業することは、攻撃対象領域（Attack Surface）を不必要に広げることと同義です。

### 罠②：GUIの裏側が見えない不安

「コントロールパネルのここをチェックしてください」

Linuxエンジニアが本当に知りたいのは「そのチェックによってどのレジストリ値が変わり、どのAPIの挙動が制限されるか」です。

本連載では可能な限り、GUI操作と対応するPowerShellコマンド・内部構造を併記します。たとえばWindowsDefenderのリアルタイム保護は、GUIのスイッチ一つですが、内部では以下と等価です：

```powershell
# Defender リアルタイム保護の状態確認（Linux の systemctl status 相当）
Get-MpPreference | Select-Object DisableRealtimeMonitoring

# auditd のルール確認に相当する操作
Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusEnabled
```

---

## 2. 概念の「翻訳」：Linux vs Windows

LinuxとWindowsは思想が異なりますが、セキュリティの根本概念は対応しています。まず全体像を掴みましょう。

| カテゴリ | Linux（CentOS/RHELなど） | Windows | 本連載での解説回 |
|---|---|---|---|
| ユーザー識別子 | UID（User ID） | SID（Security Identifier） | 第2〜3回 |
| 権限昇格 | sudo / su | UAC（User Account Control） | 第5回 |
| ファイル権限 | パーミッション（rwxrwxrwx） | DACL（Discretionary ACL） | 第6回 |
| 認証情報の保存 | /etc/shadow（SHA-512） | SAMデータベース / NTLM hash | 第2回 |
| 共有ディレクトリ | NFS / Bind Mount | SMB（\\server\share） | 第8回 |
| 設定管理 | /etc/*.conf | Registry / Group Policy | 第9〜10回 |
| ログ確認 | journalctl / /var/log | Event Log（イベントビューアー） | 第15回 |
| プロセス監査 | auditd | Audit Policy / Sysmon | 第16〜17回 |
| パケットフィルタ | iptables / nftables | Windows Firewall（WFP） | 第11回 |

> **注意：** WindowsのACLは「DACL（Discretionary ACL）」と「SACL（System ACL）」の2種類があります。原文にある「ACL」という表記だけでは、監査用のSACLと混同しやすいため、本連載では明示的に使い分けます。

---

## 3. この連載で何が身につくのか

全50回の道のりは長いですが、完走する頃には以下のスキルが身についています。

### 🔒 Windows OSの堅牢化（Hardening）
不要なサービスの停止、SMBv1の無効化、AppLockerによる実行制御、レジストリを用いた制限。Linuxの `/etc/sysctl.conf` による堅牢化と対比しながら学びます。

### 🔑 認証基盤の防御
Active Directoryへの代表的な攻撃手法（Pass-the-Hash、Kerberoasting、DCSync）を理解し、それを防ぐ「Tierモデル（管理階層モデル）」を構築します。

### 🔍 不審な挙動の検知
SysmonとEvent Logを組み合わせ、`auditd` 以上に詳細なプロセス・ネットワーク監視を実装します。MITRE ATT&CKフレームワークへのマッピングも扱います。

### ⚙️ モダンな管理手法
PowerShellとDSC（Desired State Configuration）を使った、Infrastructure as Code（IaC）ベースのセキュリティ管理。Ansibleと組み合わせた構成管理も紹介します。

---

## 今回の「エンジニアの知恵」

WindowsでLinuxの `strace` や `lsof` に相当することをしたいとき、以下の2つのツールが出発点になります。

```powershell
# 1. PowerShellでコマンドを探す（man / apropos 相当）
Get-Command -Noun *Firewall*
Get-Help Set-NetFirewallRule -Examples

# 2. 実行中プロセスが開いているファイル/ポートを確認（lsof 相当）
Get-Process -Name svchost | Select-Object Id, Name
netstat -ano | findstr "ESTABLISHED"
```

GUIがどのレジストリを操作しているか知りたい場合は、**Process Monitor（Procmon）** でフィルタリングします。これはLinuxで `inotifywait` や `auditctl` を使う感覚に近い作業です。

```
# Procmon のフィルタ設定例（GUIのチェックボックスに相当するレジストリ操作を特定）
Process Name → contains → mmc.exe
Operation    → contains → RegSetValue
```

セキュリティの本質——**最小権限の原則（PoLP）** と **多層防御（Defense in Depth）**——はOSが違っても変わりません。Windowsは「方言が違う」だけで、同じ思想で守れます。

---

## おわりに

次回（第2回）は **「OS構造の比較 —— `/etc/shadow` と SAMデータベースの違い」** です。

Windowsのパスワードハッシュ（NTLMハッシュ）がどこに、どのような形式で保存されているか。なぜLMハッシュは2008年以降に廃止されたのか。LinuxエンジニアならSHA-512との違いが気になるはずです。「パスワードの裏側」から、Windows内部構造の理解を深めていきましょう。

---

*本連載はセキュリティの理解と防御を目的としています。記載する攻撃手法は、自身が管理する環境での検証、またはCTF（Capture The Flag）等の学習用途に限定してください。*
