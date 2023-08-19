import math
import datetime as datetime
import matplotlib.pyplot as plt
import pandas as pd

from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError

def stock_price_percentage_message(percentage: str) -> str:
    text = ""
    # 文字列から数値を取得
    percentage = float(percentage.strip('%'))
    # 前日終値が読み込めない等の問題でpercentageが計算できなかった場合
    if math.isnan(percentage):
        text += "前回終値との比較はできませんでした。すみません。"
    else:
        if percentage > 0:
            text += f'前回終値と比較するとプラス{percentage}%上昇しています。'
        elif percentage < 0:
            # 読み上げの時にマイナスを消すためにマイナスを掛け算する
            percentage *= -1
            text += f'前回終値と比較するとマイナス{percentage}%下落しています。'
        else:
            text += f'前回終値と同じ株価になっています。'

    return text

"""
株価情報を取得する
share_numには銘柄番号、share_nameには銘柄の名称を入れる
名称は表示名になるため何でも良い
株価情報取得にはyahoo_finance_api2を使用
"""
def get_stock_price_infomation(share_num: str = '^N225', share_name: str = '日経平均'):
    text = ""
    try:
        my_share = share.Share(share_num)
        # 株価を読み込む
        # 7日前までのデータを5分おきに取得する(取引時間外の場合データが取得できないため多めに取ってくる)
        # 1日おきのデータも取得する理由は、正確な終値のデータが欲しいため
        # ※ 5分おきのデータの最後の要素は14:55～14:59までのデータしかなく15:00の終値が取得できない
        price_data_5min = my_share.get_historical(share.PERIOD_TYPE_DAY, 7, share.FREQUENCY_TYPE_MINUTE, 5)
        price_data_1day = my_share.get_historical(share.PERIOD_TYPE_DAY, 7, share.FREQUENCY_TYPE_DAY, 1)
    except YahooFinanceError as e:
        print(e.message)
        text = f"{share_name}の株価情報は読み込めませんでした。すみません。"
        return text, {
            "stock_price_name": share_name,
            "latest_close_price": "エラー",
            "latest_close_price_date": None,
            "percentage_change": None
        }

    # 日本時間にするためにプラス9時間にし、datetimeをindexとして登録する
    df_price_data_5min = pd.DataFrame(price_data_5min)
    df_price_data_5min["datetime"] = pd.to_datetime(df_price_data_5min.timestamp, unit="ms") + datetime.timedelta(hours=9)
    df_price_data_5min.index = pd.to_datetime(df_price_data_5min['datetime'], format='%Y/%m月%d日-%H:%M').values

    # 1日おきのデータに対しても同様の処理をする
    df_price_data_1day = pd.DataFrame(price_data_1day)
    df_price_data_1day ["datetime"] = pd.to_datetime(df_price_data_1day.timestamp, unit="ms") + datetime.timedelta(hours=9)
    df_price_data_1day.index = pd.to_datetime(df_price_data_1day['datetime'], format='%Y/%m月%d日-%H:%M').values

    now = datetime.datetime.now()
    # 最新日のデータを取得
    latest_price_data_5min = df_price_data_5min.iloc[-1]
    latest_price_data_1day = df_price_data_1day.iloc[-1]
    # 最新のデータが15時以降のものもしくは、昨日のデータであれば15:00の終値を5分おきのデータに追記する
    if((latest_price_data_1day['datetime'].hour >= 15) or (latest_price_data_5min['datetime'].day < now.day)):
        data_to_add = {
            'close': latest_price_data_1day["close"],
            'datetime': latest_price_data_5min['datetime'] + datetime.timedelta(minutes=5)
        }
        df_data_to_add = pd.DataFrame([data_to_add])
        df_data_to_add.index = pd.to_datetime(df_data_to_add['datetime'], format='%Y/%m月%d日-%H:%M').values
        df_price_data_5min = pd.concat([df_price_data_5min, df_data_to_add])

    # 最新の終値を取得
    latest_close_price = latest_price_data_1day['close']

    # 前日の終値を取得
    previous_close_price = df_price_data_1day.iloc[-2]['close']
    
    # 最新のデータ時刻－6時間～最新のデータ時刻の間の株価を取り出してグラフ化する
    # マイナス6時間の理由は株式市場が閉じる15時の時点で、開場時間の9時からのデータが取得できるようにするため
    ax = df_price_data_5min[df_price_data_5min.iloc[-1]['datetime'] - datetime.timedelta(hours=6) : df_price_data_5min.iloc[-1]['datetime']].plot(x="datetime",y="close")
    plt.title(f"The stock price of {share_num}")
    # 前日終値が読み込めていたら、破線を描く
    if previous_close_price is not None:
        ax.axhline(y=previous_close_price, color='r', linestyle='--', label='Previous Day Close')
    # HTML表示用に書き出す
    plt.savefig(f"./static/{share_num}_stock_price.png", format="png", dpi=65)
    
    # 前日終値との変化率を計算
    percentage_change = ((latest_close_price - previous_close_price) / previous_close_price) * 100
    
    # 現在株価と変化率のメッセージを作成
    latest_price_data_datetime = latest_price_data_1day['datetime']
    text += f'{share_name}株価は、'
    text += f'{latest_price_data_datetime.year}年{latest_price_data_datetime.month}月{latest_price_data_datetime.day}日{latest_price_data_datetime.hour}時{latest_price_data_datetime.minute}分時点で、'
    text += f'{round(latest_close_price, 2)}円となっています。'
    text += stock_price_percentage_message(f'{percentage_change:.2f}%')

    return text, {
        "stock_price_name": share_name,
        "latest_close_price": f"{round(latest_close_price, 2)}",
        "latest_close_price_date": f'{latest_price_data_datetime.year}年{latest_price_data_datetime.month}月{latest_price_data_datetime.day}日{latest_price_data_datetime.hour}時{latest_price_data_datetime.minute}分',
        "percentage_change": f'+{percentage_change:.2f}%' if percentage_change >= 0 else f'{percentage_change:.2f}%',
        "stock_price_image": f'./static/{share_num}_stock_price.png'
    }