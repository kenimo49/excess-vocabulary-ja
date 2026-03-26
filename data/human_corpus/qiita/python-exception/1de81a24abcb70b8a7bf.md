# はじめに
LINE WORKSのカレンダーに登録された予定をAPIを通して取得する方法についての紹介です。

指定した期間内の予定一覧を取得して、そのユーザーのどの時間帯に予定が入っているのかをPythonを使ってチェックしてみます。

# 利用するAPI
以下のAPIで、指定したユーザーの予定のリストを取得します。

- [基本カレンダーの予定リストの取得](https://developers.worksmobile.com/jp/docs/calendar-default-event-user-list )

注意点として、**繰り返し予定は1つにまとめられてしまう**ため、予定ありの時間帯を全て取るためには繰り返し予定を処理する必要があります。

# 繰り返し予定の扱い
繰り返し予定の情報にある `recurrence` に繰返しのルールが格納されており、これは iCalendarの [RRULE (Recurrence Rule)](https://dateutil.readthedocs.io/en/stable/rrule.html) の形式が使われています。

このルールをもとに、指定した期間内に作られる予定の一覧を取得します。

その処理も含めて、Pythonにて予定一覧取得をしてみました。

# 実装
言語: Python 3.9

必要なライブラリ

```sh
pip install requests
pip install python-dateutil
pip install pytz
```

以下、予定ありの時間帯を取得するコードです。

[カレンダーの予定リスト取得API](https://developers.worksmobile.com/jp/docs/calendar-default-event-user-list ) を通して、11月の予定リストを取得し、かつ、「予定あり」の時間帯をリストします。

```python
import requests

from dateutil.rrule import rrulestr
from datetime import datetime, date, time
import pytz

BASE_API_URL = "https://www.worksapis.com/v1.0"

def get_calendar_default_event_user_list(
    from_date: str,
    until_date: str,
    user_id: str,
    access_token: str,
):
    """Get events"""

    url = "{}/users/{}/calendar/events".format(BASE_API_URL, user_id)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(access_token),
    }

    params = {"fromDateTime": from_date, "untilDateTime": until_date}

    r = requests.get(url=url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()


def get_calendar_occupied_times(
    from_date: str,
    until_date: str,
    user_id: str,
    access_token: str,
):
    # 予定取得
    res_events = get_calendar_default_event_user_list(from_date, until_date, user_id, access_token)

    # 検索範囲をdatetime / date へ変換
    ## 日時の場合
    from_dt = datetime.fromisoformat(from_date)
    until_dt = datetime.fromisoformat(until_date)
    ## 終日の場合
    from_d = datetime.combine(from_dt.date(), time())
    until_d = datetime.combine(until_dt.date(), time())

    occupied_times = []

    # 予定確認
    for et in res_events["events"]:
        for e in et["eventComponents"]:
            # 空き時間としている予定ならスキップ
            if e["transparency"] == "TRANSPARENT":
                continue

            is_all_day = False

            # 開始日時
            start_obj = e["start"]
            if "dateTime" in start_obj:
                start_datetime = datetime.fromisoformat(start_obj["dateTime"])
                start_timezone = pytz.timezone(start_obj["timeZone"])
                start_datetime = start_datetime.astimezone(tz=start_timezone)
            else:
                # 終日予定の場合
                is_all_day = True
                start_datetime = datetime.fromisoformat(start_obj["date"])

            # 終了日時
            end_obj = e["end"]
            if "dateTime" in end_obj:
                end_datetime = datetime.fromisoformat(end_obj["dateTime"])
                end_timezone = pytz.timezone(end_obj["timeZone"])
                end_datetime = end_datetime.astimezone(tz=end_timezone)
            else:
                # 終日予定の場合
                is_all_day = True
                end_datetime = datetime.fromisoformat(end_obj["date"])

            # 繰り返し予定の場合
            if "recurrence" in e and e["recurrence"] is not None and len(e["recurrence"]) > 0:

                # 繰り返し終日予定の時
                if is_all_day:
                    rule_after_dt = from_d
                    rule_before_dt = until_d
                # 繰り返し日時予定の時
                else:
                    rule_after_dt = from_dt
                    rule_before_dt = until_dt

                # 予定の期間を取得
                period = end_datetime - start_datetime

                # RRULE処理
                rules = "\n".join(e["recurrence"])
                ruleset = rrulestr(rules, forceset=True, dtstart=start_datetime)

                # 検索範囲内の全ての繰り返し予定を取得
                re_start_times = ruleset.between(rule_after_dt, rule_before_dt)

                for st in re_start_times:
                    # それぞれ格納
                    occupied_times.append((st, st + period))

            # 繰り返し予定ではない場合
            else:
                occupied_times.append((start_datetime, end_datetime))

    return occupied_times


if __name__ == "__main__":
    import os

    from_date = "2023-11-01T00:00:00+09:00"
    until_date = "2023-11-30T23:59:59+09:00"
    user_id = "me"
    access_token = os.environ.get("ACCESS_TOKEN")

    # 予定ありの時間帯を取得
    data = get_calendar_occupied_times(
        from_date,
        until_date,
        user_id,
        access_token,
    )
    for d in data:
        print(d[0].isoformat(), d[1].isoformat())

```

# 実行してみる
今回は例として、2023年11月を範囲としてこのような予定をいれてます。

- `11/7 13:30-16:30` 毎週火曜繰り返し予定
    - ただし、`11/14` の予定は個別に編集され、例外となっている。
- `11/15 14:00-15:00` 単発の予定
- `11/20 14:00-15:00` 単発の予定。ただし、空き時間表示。
- `11/9` 〜 `11/20`までの毎週月〜金の繰り返し終日予定
    - ただし、`11/15` の予定は個別に編集され、例外となっており、この予定以外の終日予定は空き時間表示。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/241369/9226bec3-475a-9f18-0047-67913cf2bd94.png)

結果として以下が出力されます。

```text
2023-11-07T13:30:00+09:00 2023-11-07T16:30:00+09:00
2023-11-21T13:30:00+09:00 2023-11-21T16:30:00+09:00
2023-11-28T13:30:00+09:00 2023-11-28T16:30:00+09:00
2023-11-14T15:30:00+09:00 2023-11-14T16:30:00+09:00
2023-11-15T14:00:00+09:00 2023-11-15T15:00:00+09:00
2023-11-15T00:00:00 2023-11-16T00:00:00
```

正しく、`11/14` の予定は個別で取得され、`11/20`の単発の予定および`11/15`以外の終日予定は出力されていません。


# まとめ
LINE WORKSのカレンダーAPIで予定ありとなっている時間帯をPythonで取得してみました。繰り返し予定は1つにまとめられてしまいますが、`recurrence` に含まれているRRULEをみて展開することができます。

その人の予定が入っている時間帯や空き時間を抽出したい場合、参考になればと思います。
