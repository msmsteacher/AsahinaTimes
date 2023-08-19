from typing import List
import requests
from bs4 import BeautifulSoup

def categorize_routes(route_list: dict) -> tuple[list, list, list]:
    delay_list = []
    suspend_list = []
    trouble_list = []

    for name, status in route_list.items():
        if status in ["運転状況", "運転情報", "列車遅延", "運転再開"]:
            delay_list.append(name)
        elif status == "運転見合わせ":
            suspend_list.append(name)
        else:
            trouble_list.append(name)
    
    return suspend_list, delay_list, trouble_list

def generate_message(route_type: str, route_names: List[str]) -> str:
    if not route_names:
        return ""
    
    message = f"{route_type}は次のとおりです。"
    message += "、".join(route_names)
    message += "、以上です。"
    return message

"""
遅延情報を取得する
area_numには地域の番号を入れる(関東地方は4)
遅延情報取得は以下のyahooのHTMLページから遅延している路線をピックアップしている
https://transit.yahoo.co.jp/diainfo
"""
def get_train_operation_information(area_num: int = 4):
    html_data = None
    try:
        # 運行状況のURL
        url = f'https://transit.yahoo.co.jp/diainfo/area/{area_num}'
        html_data = requests.get(url)
        html_data.raise_for_status()
    except Exception as e:
        print(e.message)
        text = "遅延情報が読み込めませんでした。すみません。"
        return text, {
            "suspend_list": None, 
            "delay_list": None, 
            "trouble_list": None
        }

    # BeautifulSoupで解析
    soup = BeautifulSoup(html_data.text, 'html.parser')

    # 現在運行情報のある路線の<li>要素を抜き出す
    current_routes = soup.find('dt', class_='title trouble').find_next('dd').find_all('li')

    route_list = {}
    # 路線名とその状態を抜き出す
    for route in current_routes:
        route_name = route.find('dt', class_='title').get_text(strip=True)
        alert = route.find('dd', class_=lambda x: x and 'subText colTrouble' in x).text
        route_list[route_name] = alert

    if len(route_list) == 0:
        text = "現在、遅延情報はありません。"
    else:
        # 路線名と状態が入っているリストを運転見合わせ、遅延、お知らせで分類する
        suspend_list, delay_list, trouble_list = categorize_routes(route_list)
        text = ""
        text += generate_message("運転を見合わせている路線", suspend_list)
        text += generate_message("遅延をしている路線", delay_list)
        text += generate_message("何らかのお知らせが出ている路線", trouble_list)

    return text, {
        "suspend_list": suspend_list, 
        "delay_list": delay_list, 
        "trouble_list": trouble_list
    }

if __name__ == "__main__":
    get_train_operation_information()