# はじめに
Unityで文字を表示する方法には複数方法がありますが、私が思いついたものとしては、
- uGUIのLegacyの`Text`
- uGUIの`TextMeshPro`
- UIToolkitの`Label`

`TextMeshPro`がUnityで使用できるようになってから時間は経ちましたが、未だに`Unity 文字表示`と検索すると上位にはLegacyの機能を使用した解説が多くみられます。私も2024年にUnityを始めましたが初めて触ったのはLagacyの方です。Legacyは初心者にとっては始めやすい面もありますが、TextMeshProで使用できる機能がLegacyの方では使用できなかったり、文字がよりきれいに表示できるため初心者であってもお勧めしたいです。
# この記事の主な対象者
- 今までLegacyを使用してきたが`TextMeshPro`に挑戦したい方
- Unityではじめて文字を表示してみようと思っている方
# TextMeshProとは
> TextMeshPro は、Unity のための究極のテキストソリューションです。Unity の UI テキストと古いテキストメッシュの代わりに使用するのに最適です。
- 引用：Unity公式[TextMeshPro](https://docs.unity3d.com/ja/2022.3/Manual/com.unity.textmeshpro.html)

やはりLegacyよりも今始めるならTextMeshProな気がしますね。
# 環境
- Unity6.3(6000.3.11f1)
- Windows
# 計測タイムを画面右上に表示してみよう
実際の使用例とともにどのようにTextMeshProを使用していくか説明していきます。
## TextMeshProの準備
1. `GameObject > UI(Canvas) > Text - TextMeshPro`を追加
1. 現在のProjectで初めてTextMeshProを使用する際には上記のようなポップが出ると思います。その際には`Import TMP Essentials`だけはインポートしてください
![TMPImporter](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4381544/fad3026e-2a96-46b3-8fa7-c9f3cdcca315.png)
`Hierarchy`に`Canvas`とその子供に`Text(TMP)`が生成されます
1. `Text(TMP)`を選択後、`Moov Tool`(Wキー)で場所を調整させながら`Rect Tool`(Tキー)でWidthとHeightを変更して、`TextMeshPro - Text(UI) > FontSize`からフォントサイズを調整して、`TextMeshPro - Text(UI) > TextInput`で表示したい内容を入れる

補足ですが、`uGUI`の大きさを変えるときは`Scale Tool`(Rキー)ではなく`Rect Tool`がお勧めです。
| Tool名 | 仕様 |
|:-:|:-:|
| Scale Tool  | Scaleを変更  |
| Rect Tool  | Width,Heightを変更  |

![example](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4381544/73430204-51ce-40ff-a978-00d597b33fd8.png)

基本的には`Scale`は1のままでuGUIは編集すべきです。コンポーネントを使用する際などには`Scale`が1前提で作られているものが多いため思った動作にならないことがあります。私は何度か痛い目にあってきました。
## C#スクリプトの書き方
今回は後からコードで変更しますが、試しに`Time12min34.56sec`と入力してみました。
![スクリーンショット 2026-03-24 183655.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4381544/3001d0b6-c42f-4b0a-a0a6-9f69a28ab2d9.png)

Tips:リッチテキストタグを使用してみる
`Time:12<size=50%>min</size>34.56<size=50%>sec</size>`
![スクリーンショット 2026-03-24 183800.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4381544/74bb6000-d74b-4be6-90ee-34dac1955c9b.png)
`min`と`sec`の文字を他の文字と比較して50%の大きさにすることによって数字部分を目立たせてみました。リッチテキストタグの一部はlegacyの方でも使えますが、TextMeshProの方が使用できる種類が多いです。
- [サポートされるリッチテキストタグ](https://docs.unity3d.com/ja/current/Manual/UIE-supported-tags.html)

以下に時間を計測してTimeに表示できるスクリプトを用意しました。
```Timer.cs
using UnityEngine;
using TMPro;

public class Timer : MonoBehaviour
{
    float timer = 0f;
    TMP_Text textBox;
    void Start()
    {
        textBox = GetComponent<TMP_Text>();
    }
    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        int minute = (int)timer / 60;
        float second = timer % 60;
        textBox.text = $"Time:{minute}min{second:F2}sec";
    }
}
```
このスクリプトは`TextMeshPro`のGameObjectに対して追加してください。実行するとテキストが書き換わってタイマーのようになると思います。
0分であっても`0min`が表示されてしまうのでそこを改良してみてもよいかもしれません。
## C#スクリプトの解説
- `TMP_Text`
```.cs
TMP_Text textBox;
```
今回、`TextMeshPro - Text(UI)`コンポーネントを参照するために使用したクラス。他の記事では`TextMeshProUGUI`で使用されているものもあり、今回の場合ではどちらでも構いません。`TMP_Text`は`TextMeshProUGUI`(UI)と`TextMeshPro`(3D)の機能を併せ持つクラスです。
  - 参考：Unity公式[Class TMP_Text](https://docs.unity3d.com/Packages/com.unity.textmeshpro@4.0/api/TMPro.TMP_Text.html)
- `GetComponent`
```.cs
textBox = GetComponent<TMP_Text>();
```
`(GameObject).GetComponent<(Component名)>()`
指定したGameObjectについているコンポーネントを取得するために使用します。今回はこのスクリプトを保有しているGameObjectの別のコンポーネントを取得するためGameObjectの指定は必要ありません。`GetComponent`はInspectorの上から順番に参照して一致した段階で取得する動きをするため`Start`といった最小限の使用回数になるように心がけましょう。
- キャスト
```.cs
int minute = (int)timer / 60;
```
`(変更後の型)`
timerはfloat型です。float型をint型に直したいときはキャストという型変換を明示的に行う必要があります。
## TextMeshProを使用する際の注意
- 最初から使用されているフォントは日本語に対応していないため、自分でフォントを導入する必要があります。
  - 導入方法が分かりやすかった記事：[TextMeshProの使い方](https://qiita.com/hinagawa/items/b606c6a2fd56d559a375#textmeshpro%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9)
# 最後に
- 「はじめに」で紹介したUIToolkitですが、参考資料不足が目立つため記事を書きたいと思っています。完成しましたらこちらにリンクを追加したいと思います
- これが私にとっての初めての記事となるため分かりづらい箇所があると思います。不足内容等ありましたらコメントいただけますと幸いです
