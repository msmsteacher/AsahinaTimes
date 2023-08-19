import requests
from requests import Response

"""
天気情報を取得する
city_numは都市番号を入れる(130010は東京都東京)
APIの詳細は以下を参照
https://weather.tsukumijima.net/
"""
def get_wether_infomation(city_num: int = 130010):
    text = ""
    try:
        # 天気APIを呼び出す
        response: Response = requests.get(f"https://weather.tsukumijima.net/api/forecast/city/{city_num}")
        response.raise_for_status()
        json = response.json()
    except Exception as e:
        # 読み込めなかった場合は、メッセージだけ返す
        print(e.message)
        text = "気象庁が発信しているデータが読み込めませんでした。すみません。"
        return text, {
            "location": "エラー",
            "today_weather": None,
            "today_temp": None,
            "today_mark": None,
            "tomorrow_weather": None,
            "tomorrow_temp": None,
            "tomorrow_mark": None
        }
    
    # どこの天気情報かを示す
    text += f'気象庁が発信している{json["title"]}情報です。'
    
    # 本日の天気を読み込む
    today_forecast = json["forecasts"][0]
    text += f'本日の天気は{today_forecast["telop"]}で、'
    
    # 15時頃を過ぎると最高気温情報がなくなるため条件分岐させる
    if (today_forecast["temperature"]["max"]["celsius"] == None):
        text += f'最高気温は読み込めませんでした。すみません。'
        today_forecast["temperature"]["max"]["celsius"] = "--"
    else:
        text += f'最高気温は{today_forecast["temperature"]["max"]["celsius"]}度です。'

    # 明日の天気を読み込む
    tomorrow_forecast = json["forecasts"][1]
    text += f'明日の天気は{tomorrow_forecast["telop"]}で、'
    
    # ここの最高気温は基本は読み込めるはずだが念のため条件分岐させる
    if (tomorrow_forecast["temperature"]["max"]["celsius"] == None):
        text += f'最高気温は読み込めませんでした。すみません。'
        tomorrow_forecast["temperature"]["max"]["celsius"] = "--"
    else:
        text += f'最高気温は{tomorrow_forecast["temperature"]["max"]["celsius"]}度です。'
        
    # 気象の詳細情報、分量が多いため省略
    # text += f'気象庁からの文章を読み上げます。{json["description"]["text"]'
    # text += ' 以上が天気情報でした。  \n'
    
    return text, {
        "location": json["title"].split("の")[0],
        "today_weather": today_forecast["telop"],
        "today_temp": today_forecast["temperature"]["max"]["celsius"],
        "today_mark": today_forecast["image"]["url"],
        "tomorrow_weather": tomorrow_forecast["telop"],
        "tomorrow_temp": tomorrow_forecast["temperature"]["max"]["celsius"],
        "tomorrow_mark": tomorrow_forecast["image"]["url"],
    }