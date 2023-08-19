import datetime
import pandas_datareader.data as pdr
import yfinance as yf

# pdrでyfが使えるように設定
# 参考：https://yottagin.com/?p=9963
yf.pdr_override()

def get_date_range(days: int) -> tuple[str, str]:
    dt_end = datetime.datetime.now()
    dt_start = dt_end - datetime.timedelta(days=days)
    return dt_start.strftime('%Y-%m-%d'), dt_end.strftime('%Y-%m-%d')

def get_exchange_rate(pair: str) -> float:
    # 7日前まで取得する(取引時間外の場合データが取得できないため)
    start, end = get_date_range(7)
    
    # 為替pairを所定の形に変更
    code = f'{pair}=X'

    # dataの取得
    data = pdr.get_data_yahoo(code, start, end)

    # 最新日の終値を返す
    return data['Close'][-1]

"""
為替情報を取得する
exchangeには円から変換したい通貨コードを、nameには通貨の名称を入れる
名称は表示名になるため何でも良い
為替情報取得にはyfinanceを使用
"""
def get_exchange_rate_infomation(exchange: str = "USD", name: str = "ドル"):
    try:
        exchange_rate = round(get_exchange_rate(f"{exchange}JPY"), 2)
        text = f'{name}に対しては現在1{name}{exchange_rate}円で取引されています。'
    except Exception as e:
        print(e.message)
        text = f"{name}に対する為替情報が読み込めませんでした。すみません。"
        exchange_rate = None
        
    return text, {
        "name": name,
        "exchange_rate": exchange_rate
    }