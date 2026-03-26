本記事は、ハンズラボ Advent Calendar 2022 20日目の記事です。

# はじめに
みなさん、令和は好きですか。
巷では**令和ちゃん**と呼ばれることもしばしば。昭和や平成に比べ親しみやすい印象があります。

さて、寒い日には「気温の調整が下手くそだ」などと貶されている令和ちゃんですが、本当にその日の令和ちゃんは悪者だったのでしょうか。日本のどこかでひっそりと令和ちゃんに感謝している人はいなかったのでしょうか。毀誉褒貶をもれなく伝える場があってもいいのではないでしょうか。

そこで私は考えました。

**今日の令和ちゃんがいい子だったか悪い子だったかを投票してもらおう**

と。

これは、令和ちゃんのために人生で初めて1からwebアプリを作成した男の物語です。

# 欲しい機能
まず、欲しい機能を洗い出します。
兎にも角にも**令和ちゃんを評価する機能**はマストです。これがないと話になりません。
**過去の令和ちゃんの評価をグラフで表示**して、特定の日付の**評価の一覧**も表示できたら嬉しいですね。
これはすごく大切なことなのですが、**なぜその評価なのか**がわからないと令和ちゃんも納得できません。これも実装しましょう。

ということで、以下の3要素を満たすwebアプリをFlaskで作成します。
- 評価登録(理由含む)
- 過去の評価のグラフ表示
- 特定日付の評価一覧表示
# いざ製造
## 注意
Flaskでのwebアプリケーションの立ち上げ方など、全てを書いていると時間がかかりすぎるので適宜省略させていただきます。
ページ下部の「参考」に参考にさせていただいたページのリンクをまとめたので、そちらをご参照ください。
とにかく自分のアイディアを形にすることに重きを置いたため、DB設計やコーディングなどでかなりお見苦しい点が散見しますがご勘弁を。

## ディレクトリ構造
```bash
.
├── __init__.py
├── constant
│   └── const.py
├── db.py
├── main.py
├── static
│   ├── images
│   │   ├── bad.png
│   │   ├── bg.png
│   │   └── good.png
│   ├── js
│   │   └── graph.js
│   └── style.css
└── templates
    ├── base.html
    ├── complete.html
    ├── detail.html
    ├── graph.html
    └── index.html
```

## DB
テーブルが複数個必要なアプリケーションではないので、シンプルに1つにまとめます。
- id
- 評価タイプ
    - 好き(高評価)
    - 嫌い(低評価)
- コメント
- 作成日時
の4つがあれば十分そうです。

sqlalchemyを使用してDB操作をしたいので、以下のようにしました。
```python:db.py

from sqlalchemy import DATETIME, Boolean, Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from reiwa_gb.constant.const import CONST

engine = create_engine(f'sqlite:///{CONST.DATABASE}')
Base = declarative_base()


class ReiwaGB(Base):
    __tablename__ = 'reiwa_gb'
    id = Column(String, primary_key=True, unique=True, nullable=False)
    eval_type = Column(Boolean, nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DATETIME, nullable=False)


def create_table():
    Base.metadata.create_all(bind=engine)


session = scoped_session(
    sessionmaker(
        autoflush=True,
        bind=engine
    )
)

```

サーバー起動時にテーブルを作成したいので、`__init__.py`でテーブル作成用関数を呼び出します。
```python:__init__.py
from flask import Flask

from reiwa_gb import db

app = Flask(__name__)
import reiwa_gb.main

# テーブル作成
db.create_table()
```

`flask run`でサーバーを起動後、テーブルが作成されていることが確認できました。
```bash
sqlite> .tables
reiwa_gb
```

## 評価登録(理由含む)
### 登録画面
完成した画面がこちらです。
![完成した画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/ce152635-dd2d-eb37-799a-c34fe02e961b.png)

間違った評価をされては令和ちゃんに申し訳ないので、なるべくシンプルでわかりやすいものにしました。
ここまでデカデカと表示されていれば、ほぼ全ての誤クリックは防げそうです。
例外処理なんてものは知りません。

コードは以下です。
```python:main.py
@app.route('/register', methods=['POST'])
def register():
    # 高評価は0、低評価は1
    eval_type = int(request.form['eval_type'])
    # コメントは一旦空文字を登録
    comment = ''
    session.begin()
    reiwa_gb = ReiwaGB()
    reiwa_gb.id = str(uuid.uuid4())
    reiwa_gb.eval_type = eval_type
    reiwa_gb.comment = comment
    reiwa_gb.created_at = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    session.add(reiwa_gb)
    session.commit()
    session.close()

    return redirect(url_for('complete'))

```

```html:templates/index.html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8"/>
    <title>令和ちゃんお疲れ様</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  </head>
  <body>
    <h1>今日の令和ちゃんは？</h1>
    <form method="post" action="{{ url_for('register') }}">
      <div class="container">
        <td><input type="image" src="static/images/good.png" name="eval_type" value="0" width="350" height="350" style="margin-right:250px;"></td>
        <td><input type="image" src="static/images/bad.png" name="eval_type" value="1" width="350" height="350"></td><br>
      </div>
    </form>
  </body>
</html>

```

高評価と低評価を1回ずつクリックした後のテーブルです。
ちゃんと登録されていますね。
```bash
sqlite> select * from reiwa_gb;
3b916b97-c711-44b1-be00-ffd4df2d0741|0||2022-12-14 16:24:12.483689
1890fa1a-2c64-43aa-845f-010d30763ae7|1||2022-12-14 16:25:04.250639
```
ちなみに評価ボタンクリック後には登録完了ページに遷移します。
TOPにも戻れないどうしようもない子です。せっかく作ったので紹介しますが、これはない方がマシです。
ここには評価別に「喜んでいる令和ちゃん」と「悲しんでいる令和ちゃん」のイラストを入れたかったのですが、断念しました。理由は後ほど。

こんなもののソースは載せません。
![登録完了](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/254d9ec5-e385-27c2-3eb9-6ebec9363f0a.png)

### 評価理由の入力欄
無事評価の登録までは実装できたので、評価理由の入力欄を作成します。
完成した画面はこちら。
![評価入力欄](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/9cc84604-383d-fcf1-2cd7-f3fd098c1103.png)

これまたどでかい入力欄＋主張の激しいプレースホルダーのおかげで、なんとかユーザーに意図を汲み取っていただけそうです。
ユーザーに頼り切りのUIですが、なんだか愛着が湧いてきました。

コードは以下です。
```python:main.py
@app.route('/register', methods=['POST'])
def register():
    eval_type = int(request.form['eval_type'])
    # 入力欄から取得するように変更
    comment = request.form['comment']
    session.begin()
    reiwa_gb = ReiwaGB()
    reiwa_gb.id = str(uuid.uuid4())
    reiwa_gb.eval_type = eval_type
    reiwa_gb.comment = comment
    reiwa_gb.created_at = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    session.add(reiwa_gb)
    session.commit()
    session.close()

    return redirect(url_for('complete'))
```
```html:templates/index.html
<!DOCTYPE html>
<html lang="ja">

  <head>
    <meta charset="UTF-8"/>
    <title>令和ちゃんお疲れ様</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  </head>

  <body>
    <h1>今日の令和ちゃんは？</h1>
    <form method="post" action="{{ url_for('register') }}">
      <!-- ここから -->
      <div class="container">
        <input type="text" name="comment" class="bigtxt" placeholder="理由も教えて！">
      </div>
      <!-- ここまで追加 -->
      <div class="container">
        <td><input type="image" src="static/images/good.png" name="eval_type" value="0" width="350" height="350" style="margin-right:250px;"></td>
        <td><input type="image" src="static/images/bad.png" name="eval_type" value="1" width="350" height="350"></td><br>
      </div>
    </form>
  </body>

</html>
```

実際にコメントを入力して、評価ボタンを１回ずつクリックしてみました。
それぞれちゃんとコメントが登録されています。
```bash
sqlite> select * from reiwa_gb;
3b916b97-c711-44b1-be00-ffd4df2d0741|0||2022-12-14 16:24:12.483689
1890fa1a-2c64-43aa-845f-010d30763ae7|1||2022-12-14 16:25:04.250639
5121b45c-085e-49d3-926c-ce9fed1324d9|0|過ごしやすい気温|2022-12-14 16:42:05.760632
8333c6f6-457b-4698-9a03-e860b415ffbc|1|寒すぎ|2022-12-14 16:42:10.777860
```

## 過去の評価のグラフ表示
これで理由付きで投票することができるようになりました。
次に、過去のデータをグラフで表示できるようにしましょう。
グラフと言えばこれだろ！という安直な考えでmatplotlibを使用するつもりでしたが、特定の値のデータ一覧の表示をさせるにはchart.jsの方が相性が良さそうだったのでそちらに挑戦してみました。

完成した画面がこちら。
データは全て削除したので、0になっています。
![グラフ表示](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/6a5c1166-9a2d-3992-744d-c416d74ec832.png)

jsとpythonでの値のやり取りに困ったので、これはかなり力技で解決しました。
鳥頭のため、もうこの段階ではsqlalchemyのことを忘れていました。

```python:main.py
@app.route('/graph')
def chart_do():

    con = sqlite3.connect(CONST.DATABASE)
    # 日付のリストを取得
    created_dates = con.execute("select strftime('%Y-%m-%d', created_at) as day from reiwa_gb group by day")

    chart_labels = []
    chart_good_data = []
    chart_bad_data = []

    for created_date in created_dates:
        chart_labels.append(created_date[0])
        good_data = con.execute(
            f'select count(*) from reiwa_gb where strftime("%Y-%m-%d", created_at) = "{created_date[0]}" and eval_type = 0')
        for good_datum in good_data:
            chart_good_data.append(str(good_datum[0]))

        bad_data = con.execute(
            f'select count(*) from reiwa_gb where strftime("%Y-%m-%d", created_at) = "{created_date[0]}" and eval_type = 1')
        for bad_datum in bad_data:
            chart_bad_data.append(str(bad_datum[0]))

    chart_title = '過去のデータ'
    chart_labels = ','.join(chart_labels)
    chart_good = {
        'chart_good_data': ','.join(chart_good_data),
        'chart_good_target': '好き',
    }
    chart_bad = {
        'chart_bad_data': ','.join(chart_bad_data),
        'chart_bad_target': '嫌い',
    }

    return render_template('graph.html', chart_title=chart_title, chart_labels=chart_labels, chart_good=chart_good, chart_bad=chart_bad)

```

```html:templates/graph.html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="../static/css/style.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <title>令和ちゃんお疲れ様</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.1/Chart.min.js"></script>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
  </head>
  <div class="container">
    <div class="row my-4">
      <canvas id="myChart"></canvas>
    </div>
    <input type="hidden" id="chart_title" name="chart_title" value="{{ chart_title }}">
    <input type="hidden" id="chart_labels" name="chart_labels" value="{{ chart_labels }}">

    <input type="hidden" id="chart_good_target" name="chart_good_target" value="{{ chart_good.chart_good_target }}">
    <input type="hidden" id="chart_good_data" name="chart_good_data" value="{{ chart_good.chart_good_data }}">

    <input type="hidden" id="chart_bad_target" name="chart_bad_target" value="{{ chart_bad.chart_bad_target }}">
    <input type="hidden" id="chart_bad_data" name="chart_bad_data" value="{{ chart_bad.chart_bad_data }}">
  </div>
  <script type="text/javascript" src="static/js/graph.js"></script>
</html>

```

```js:stasic/js/graph.js
let title = document.getElementById('chart_title').value;

let dlabel = String(document.getElementById('chart_labels').value);
let larr = dlabel.split(',');

let good_target = document.getElementById('chart_good_target').value;
let bad_target = document.getElementById('chart_bad_target').value;

let good_dstr = String(document.getElementById('chart_good_data').value);
let good_darr = good_dstr.split(',');

let bad_dstr = String(document.getElementById('chart_bad_data').value);
let bad_darr = bad_dstr.split(',');

let canvasP = document.getElementById('myChart')
let ctx = canvasP.getContext('2d');

let myLineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: larr,
        datasets: [{
            data:good_darr,
            backgroundColor: "rgba(0,0,255,0.2)",
            borderColor: "blue",
            borderWidth: 2,
            pointStyle: "rect",
            pointRadius: 3,
            pointBorderColor: "blue",
            pointBorderWidth: 2,
            pointBackgroundColor: "blue",
            pointLabelFontSize: 20,
            label: good_target
            }, {
                data:bad_darr,
                backgroundColor: "rgba(255,0,0,0.2)",
                borderColor: "red",
                borderWidth: 2,
                pointStyle: "rect",
                pointRadius: 3,
                pointBorderColor: "red",
                pointBorderWidth: 2,
                pointBackgroundColor: "red",
                pointLabelFontSize: 20,
                label: bad_target
            }
        ]
    },
    options: {
        responsive: true,
        title: {
            display: true,
            fontSize: 20,
            text: title
        },
        legend: {
            position: 'bottom',
            labels: {
                fontSize: 20,
            },
        }
    }
});

```

テストデータを登録して、グラフが表示されるか見てみましょう。
![グラフ表示](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/70827617-6e0c-8456-4093-c55339d9380e.png)
「嫌い」が多すぎる気がしますが、しっかり表示されているのでよしとします。

## 特定日付の評価一覧表示
最後のステップです。
グラフの特定箇所をクリックした際、その日付のデータ一覧を表示させます。

完成した画面がこちら。
![一覧画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/f4b1aee3-33ed-58b3-2292-e9206f9aa39b.png)

愛嬌がありますね。

以下コードです。
鳥頭のくせに、sqlalchemyを使っていたことを思い出したようです。
```python:main.py
@app.route('/detail', methods=['GET'])
def detail():
    date = datetime.datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    date_start = datetime.datetime.combine(date, datetime.time(hour=0, minute=0, second=0))
    date_end = datetime.datetime.combine(date, datetime.time(hour=23, minute=59, second=59))
    session.begin()
    reiwa_gb = session.query(
        ReiwaGB,
    ).filter(
        ReiwaGB.created_at >= str(date_start), ReiwaGB.created_at < str(date_end)
    ).all()

    session.close()

    return render_template(
        'detail.html',
        records=reiwa_gb
    )

```
```html:detail.html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8"/>
    <title>令和ちゃんお疲れ様</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  </head>
  <body>
    <h1>詳細画面</h1>
    <table>
      <tr>
        <th>評価</th>
        <th>コメント</th>
      </tr>
      {% for record in records %}
        <tr>
          {% if record.eval_type == 0 %}
            <td>好き</td>
          {% elif record.eval_type == 1 %}
            <td>嫌い</td>
          {% endif %}
          <td>{{record.comment}}</td>
        </tr>
      {% endfor %}
    </table>
  </body>
</html>

```
```js:static/js/graph.js
let title = document.getElementById('chart_title').value;

let dlabel = String(document.getElementById('chart_labels').value);
let larr = dlabel.split(',');

let good_target = document.getElementById('chart_good_target').value;
let bad_target = document.getElementById('chart_bad_target').value;

let good_dstr = String(document.getElementById('chart_good_data').value);
let good_darr = good_dstr.split(',');

let bad_dstr = String(document.getElementById('chart_bad_data').value);
let bad_darr = bad_dstr.split(',');

let canvasP = document.getElementById('myChart')
let ctx = canvasP.getContext('2d');

let myLineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: larr,
        datasets: [{
            data:good_darr,
            backgroundColor: "rgba(0,0,255,0.2)",
            borderColor: "blue",
            borderWidth: 2,
            pointStyle: "rect",
            pointRadius: 3,
            pointBorderColor: "blue",
            pointBorderWidth: 2,
            pointBackgroundColor: "blue",
            pointLabelFontSize: 20,
            label: good_target
            }, {
                data:bad_darr,
                backgroundColor: "rgba(255,0,0,0.2)",
                borderColor: "red",
                borderWidth: 2,
                pointStyle: "rect",
                pointRadius: 3,
                pointBorderColor: "red",
                pointBorderWidth: 2,
                pointBackgroundColor: "red",
                pointLabelFontSize: 20,
                label: bad_target
            }
        ]
    },
    options: {
        responsive: true,
        title: {
            display: true,
            fontSize: 20,
            text: title
        },
        legend: {
            position: 'bottom',
            labels: {
                fontSize: 20,
            },
        }
    }
});

// ここから
canvasP.onclick = function(evt){
    var activePoint = myLineChart.getElementAtEvent(evt);
    var firstPoint = activePoint[0];
    // クリックされたグラフのラベルを取得
    // 2022-11-01とか
    var label = myLineChart.data.labels[firstPoint._index];
    console.log(label)
    window.open().location.href = "detail?date="+label;
};
//ここまで追加

```

出来上がり！

## 完成
なんとか完成させることができました。
完成した画面を触った動画です。
![令和ちゃん.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/7dc8a9ff-a56d-ee35-79d7-cb03b62044b2.gif)
グラフ表示時のアニメーションも想像通りで、やりたいことは概ね達成できました。

## そのほかにやったこと+やりたかったこと
実は、せっかくの機会なのでこのほかにも色々なことを試してみました。
やりたかったけど断念したこともありました。
### stable diffusionでの画像生成(一部断念)
令和ちゃんと言えばピンク髪の少女を思い浮かべる人も多いはず。当初このアプリケーションには令和ちゃんのイラストをたくさん載せる予定でした。令和ちゃんのイメージを統一することで、「**この子に対する投票なんだ**」という意識が生まれると考えたからです。

しかし先述の通り私はデザインをはじめとしたアーティスティックな領域に自信がなく、ネットに転がっている画像を無断使用するわけにもいかなかったため**stable diffusionちゃん**にお任せすることにしました。

先人たちの知恵をお借りして自動生成の環境を整えることはできましたが、いわゆる**呪文**の詠唱がうまくいかず私の想像する令和ちゃんとはあまりにもかけ離れたものばかり出力されます。まさに魑魅魍魎。**このままでは私が令和ちゃんを嫌いになってしまうのではないか**。そう考えた私は断腸の思いで自動生成を諦めました。泣いて馬謖、もといstable diffusionちゃんを斬ったのです。

せっかくなので、生成された令和ちゃん(仮)を何**体**か紹介します。
アプリケーション製造中に生成したものたちは既に削除済みなので、記事執筆時に同じ**呪文**で生成したものたちです。
しかし、私の苦悩を説明する材料としては十二分にその役目を果たしてくれることでしょう。
お気に入りは3枚目です。この画像が生成された時に「あぁ、私の判断は間違っていなかったのだな」と胸を撫で下ろしました。

![20221215_053639.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/7c0b7177-bc56-80bd-1fc5-147d9c4d121c.png)
![20221215_053824.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/ae407767-8068-7a79-4b7d-76a122e378fe.png)
![20221215_053918.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/197112/b55c3360-6416-306b-b18c-04968cd86282.png)

熟練のstable diffusionユーザーの方、どうかかわいい令和ちゃんの生成を・・・

### htmlファイルの快適なオートフォーマット
業務でhtmlファイルを使用することはほとんどないので、アプリケーションの製造にあたりオートフォーマットを設定しました。
今回はjinja2を使用するということでmustache記法に対応したものにしたく、`{{% for %}}`などのブロック内のインデント下げも自動でやってくれるものを探しました。アプリケーションの動きには全く関係ない部分ですので省略しますが、以下の記事を参考にさせていただきました。

https://qiita.com/ajim/items/b46292e21cc8d0160b06#3-pretty-diff-unibeautify

https://unibeautify.com/docs/beautifier-pretty-diff
### アプリケーションの公開(断念)
お気づきの方も多いでしょうが、今回のwebアプリケーションはどこにも公開していません。
公開できるクオリティとは程遠いものであるからです。
これでは誰にも投票してもらえません。令和ちゃんには私個人の偏った意見しか届けられません。
しかしご安心を。なるべく「好き」の投票することを約束します。

もしかしたらいつかの私がなんとかしてくれるかもしれません。

## 終わりに
昔から、ふとした時に浮かぶアイディアを形にすることが億劫でメモ帳にためていました。

アドカレは漠然とした「いつかやろう」という気持ちに向き合う、いい機会でした。
私が私である限り「いつかやる」のは私以外の何者でもなく、私がメモをためて満足している人間である限りこのアイディアたちが世に出ることはないのだなと気づくまで、随分と時間がかかりました。より正確に言うのであれば、最初から分かりきっていたことを受け入れるまでに随分と長い時間がかかりました。

私のメモ帳には、くだらないものから誰かの役に立ちそうなものまで残り385件のアイディアが眠っています。
いくつかは既に誰かのもとで実現されていますが、この眠っているアイディアたちを蔑ろにせず、今後も日本人らしくものづくりに勤しみます。

拙文最後までお読みいただきありがとうございました。

良い令和を。

# 参考
https://www.youtube.com/watch?v=EQIAzH0HvzQ

https://coffee-blue-mountain.com/python-flask-sqlalchemy-orm-1/

https://jajaaan.co.jp/css/css-headline/

https://icooon-mono.com/

https://murasan-net.com/index.php/2022/11/26/stable-diffusion-2-pythoncode/

https://qiita.com/kubochiro/items/874ccddb564c7e684000
