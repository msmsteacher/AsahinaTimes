from bs4 import BeautifulSoup
import requests

"""
ニュース情報を取得する
ニュース情報取得は以下のyahooのHTMLページから主要の項目からピックアップしている
https://news.yahoo.co.jp/
"""
def get_news_infomation():
    html_data = None
    try:
        # ニュースのURL
        url = 'https://news.yahoo.co.jp/'
        html_data = requests.get(url)
        html_data.raise_for_status()
    except Exception as e:
        print(e.message)
        text = "ニュース情報が読み込めませんでした。すみません。"
        return text, {"news_list": ["読み込めませんでした"]}

    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html_data.text, 'html.parser')

    # ニュースに関連するセクションを特定
    news_section = soup.find('section', class_='topics')

    # セクション内のすべてのリンクを取得
    news_links = news_section.find_all('a')

    # ニュースのテキストを取り出す
    news_text_list = [link.get_text() for link in news_links]

    news_list = []
    text = "この時間の主要なニュースは次の通りです。"
    for itr, news_text in enumerate(news_text_list):
        if (news_text == "もっと見る" or itr >= 6):
            break
        text += f"「{news_text}」、"
        news_list.append(news_text)
    text += f"などのニュースが入っています。\n" 
    return text, {
        "news_list": news_list
    }