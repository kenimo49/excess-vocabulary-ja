今回はセキュリティ担当が普段何をしているかをおおざっぱに話をしようかと思います。

## 自己紹介
こんにちは。JINSで社内セキュリティを担当している吉田といいます。
セキュリティというとパッと思いつくのは脆弱性診断とかマルウェア解析とか有名セキュリティベンダーが実施しているような業務かと思いますが、今回はユーザ企業に所属しているセキュリティ担当がどんな仕事をしているかを書こうと思います。

## 社内PCの調査
JINSは日本、海外それぞれに拠点があり、もちろん各従業員が貸与されたPCを使っているので1000台以上の端末数があります。
中には更新が止まってしまっていたり、部署で独自のソフトウェアをインストールしていたりするので、それらを是正、整理するのが日々の業務の1つです。(地味です。。。)
もし変な使われ方をしているPCあれば、設定を確認したりアップデートかけたりアプリをアンインストールしたりしますが、複数台あると確認したりするのが結構つらいです。
あとは調査以外でも、PCに常駐させるセキュリティソフトの一斉入れ替えなど行うことあるので、その場合は社内PC全台が対象になります。

## スクリプトを書こう！
というわけで代わりに色々やってくれるスクリプトを書くことがよくあります。
といっても自分で調べながら手で書くのは面倒なので生成系AIに頼っちゃいます。

例えばこんなの。

### 監視ツール作成したい

特に気になるところをちゃんと指示出ししつつお願いしてみます。
この辺人間にお願いするのと同じですね。
(ちなみに最初の回答でセキュリティ面について釘を刺されました)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632473/c9707402-5bfa-67d0-6db1-60e362f29970.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632473/00275b6b-7ec5-c2ad-abed-37b00606b7d7.png)


ただ実は1回ではすんなり出してくれず、何回か指示を出しなおしました。
  - Chrome拡張とGo言語プログラムが連携されず別々のものを出されたので、連携させるよう再度指示
  - 次に出されたGo言語プログラムがローカルWebサーバを立てて待ち受ける方法だったので、Native messagingを使いたいと再度指示

この辺、やはり100%希望のものは出てこないと実感したところです。
GPT3.5で試してますが、体感で一度に1つの単純なことだけ指示するならいい感じの回答出してくれるのですが、少し複雑な指示を出すとこちらの期待と食い違ってきます。
この辺GPT4.0相当のものならもっとすんなり作れますかね？

最終的に出てきたものに対し、自分でも修正を加え以下になりました。

```manifest.json
{
    "manifest_version": 3,
    "name": "Confidential Info Monitor",
    "version": "1.0",
    "permissions": ["nativeMessaging", "activeTab"],
    "content_scripts": [
      {
        "matches": ["https://test.sample.com/*"],
        "js": ["contentScript.js"]
      }
    ],
    "background": {
      "service_worker": "background.js"
    }
  }
```

```contentScript.js
window.addEventListener("load", main, false);

// content.js: 特定のDOM要素やキーワードの検出と通知
function main(e) {
  if (document.body.textContent.includes("内部から不正送信されそうな機密情報のキーワード")) {
      chrome.runtime.sendMessage({ type: "alert", message: "found Internal fraud" });
    }
  };
```

```background.js
chrome.runtime.onMessage.addListener((request) => {
  chrome.runtime.sendNativeMessage('confidential_info_native_messaging_app', {name: "ping", body: "test"})
});
```

```confidential_info_native_messaging_app.json
{
    "name": "confidential_info_native_messaging_app",
    "description": "Confidential Info Monitor",
    "path":"./app.exe",
    "type": "stdio",
    "allowed_origins": ["chrome-extension://'chrome拡張のID'/"]
    }
```

```main.go
package main

import (
	"bufio"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image/png"
	"io"
	"os"

	"github.com/kbinani/screenshot"
)

func main() {
	fmt.Println("Start App")
	stdin := bufio.NewReader(os.Stdin)

	for {
		var length uint32
		if err := binary.Read(stdin, binary.LittleEndian, &length); err != nil {
			fmt.Fprintln(os.Stderr, "デコードエラー:", err)
			break
		}
		payload := make([]byte, length)
		if _, err := io.ReadFull(stdin, payload); err != nil {
			fmt.Fprintln(os.Stderr, "デコードエラー:", err)
			break
		}

		// すべてのディスプレイのスクリーンショットを取得
		numDisplays := screenshot.NumActiveDisplays()
		for i := 0; i < numDisplays; i++ {
			// 各ディスプレイの画像を取得
			img, err := screenshot.CaptureDisplay(i)
			if err != nil {
				fmt.Println("スクリーンショットの取得に失敗しました:", err)
				return
			}

			// ファイルに保存
			fileName := fmt.Sprintf("screenshot%d.png", i)
			file, err := os.Create(fileName)
			if err != nil {
				fmt.Println("ファイルの作成に失敗しました:", err)
				return
			}
			defer file.Close()

			err = png.Encode(file, img)
			if err != nil {
				fmt.Println("PNGエンコードに失敗しました:", err)
				return
			}

			fmt.Printf("スクリーンショットを %s に保存しました\n", fileName)
		}

	}
}
```

取得したスクリーンショットをどこか外部に保存するのか、付随して他の情報も取得したいか、そもそもこのChrome拡張を配信のためにChromeウェブストアにUpする許可をGoogleからもらえるのか…
など懸念点があり今回はただのお試しですが、今までChrome拡張もGo言語も知らなかったのでそこから1つ1つ調べるよりかなり楽だと感じました。
とはいえ、もちろん丸投げは無理だったので自分でも勉強は必要ですね！

## まとめ

今回ほとんど生成系AIの話しかしませんでしたが、ほっておいたらどんどんぐちゃぐちゃになる社内のIT機器のセキュリティ実態を調査整理する業務とイメージしていただけたら幸いです。
ChatGPT3.5でお手軽に試してみましたが、他のAIサービスで本格的に試してみてもいいかもですね。

また業務としては他にも、WAFのアラート分析やチューニング、EDRのアラート調査、サーバのセキュリティ強化、外部ベンダーによる脆弱性診断の手配なども行っています。
記事の形にまとめられるものあれば、いつかそちらも紹介できればと思います。

明日は@Onami_Iさん、よろしくおねがいします！
