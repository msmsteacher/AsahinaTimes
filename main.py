import datetime
import matplotlib

from infomation.stock_price import get_stock_price_infomation
from infomation.weather import get_wether_infomation
from infomation.exchange_rate import get_exchange_rate_infomation
from infomation.train_operation import get_train_operation_information
from infomation.news import get_news_infomation

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
# from pprint import pprint
from starlette.staticfiles import StaticFiles
from util.util import *
from util.voicevox_engine import text_to_speech
from voicevox_core import AccelerationMode, VoicevoxCore, METAS

# matplotlibのバックエンドを指定
matplotlib.use('Agg')

# fastapiの設定
app = FastAPI()

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # 許可するオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル(HTMLファイル)を提供するためのディレクトリを指定
static_dir: Path = Path("static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# VoicevoxCoreの初期化(ローカルコードを使用する場合)
if USE_VOICEVOX_OPTION == UseVoicevoxOption.LOCALCODE:
    # どのspeaker_idを使いたいか調べる場合はこのprintを使う
    # pprint(METAS)
    core: VoicevoxCore = VoicevoxCore(acceleration_mode=AccelerationMode.GPU, open_jtalk_dict_dir=Path("open_jtalk_dic_utf_8-1.11"))
    if not core.is_model_loaded(SPEAKER_ID):  # モデルが読み込まれていない場合
        core.load_model(SPEAKER_ID)  # 指定したidのモデルを読み込む

"""
HTMLを返す
"""
@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(static_dir / "index.html")

"""
メッセージを生成する
"""
@app.get("/message")
def get_message():
    # 本日の日時、明日の日時を取得
    now: datetime = datetime.datetime.now()
    tomorrow: datetime = now + datetime.timedelta(days=1)
    
    text = ""
    text += f"{greet_by_time(now)}、朝日奈です。\n"
    text += f"本日は{now.year}年{now.month}月{now.day}日{WEEKDAY_NAMES[now.weekday()]}、時刻は{now.hour}時{now.minute}分です。\n"
    text += "天気、株価、為替、遅延情報、主なニュースについてお伝えします。\n"

    # 天気情報を取得
    weather_text, weather_info = get_wether_infomation()
    text += weather_text

    # 株価情報を取得
    text += "\n次に株価情報です。\n"
    stock_price1_text, stock_price1_info = get_stock_price_infomation("^N225", "日経平均")
    text += stock_price1_text
    stock_price2_text, stock_price2_info = get_stock_price_infomation("9984.T", "ソフトバンクグループ")
    text += stock_price2_text
    
    # 為替情報を取得
    text += '\n次に為替情報です。\n'
    exchange_rate1_text, exchange_rate1_info = get_exchange_rate_infomation("USD", "ドル")
    text += exchange_rate1_text
    exchange_rate2_text, exchange_rate2_info = get_exchange_rate_infomation("EUR", "ユーロ")
    text += exchange_rate2_text

    # 遅延情報の取得
    text += "\n次に遅延情報です。\n"
    train_operation_text, train_operation_info = get_train_operation_information()
    text += train_operation_text
    
    # ニュースの取得
    text += "\n最後にニュース情報です。\n"
    news_text, news_info = get_news_infomation()
    text += news_text
    
    text += "\nこちらで以上になります。\n"
    text += f"{last_message_by_time(now)}"
    print("text作成完了")

    try:
        voice_url = "./static/output.wav"
        voice_data = None
        # 音声合成を行う
        if USE_VOICEVOX_OPTION == UseVoicevoxOption.LOCALCODE:
            voice_data = core.tts(text=text, speaker_id=SPEAKER_ID)
        elif USE_VOICEVOX_OPTION == UseVoicevoxOption.ENGINE:
            voice_data = text_to_speech(text=text, speaker=SPEAKER_ID)
        else:
            print("use_voicevox_optionを正しく選択してください")
            
        with open(voice_url, "wb") as f:
            f.write(voice_data)  # ファイルに書き出す
        print("合成音声作成完了")
    except Exception as e:
        voice_url = ""
        print(e.message)
        print("合成音声エラー")

    return {
        "text": text, 
        "today_with_time": f"{now.year}年{now.month}月{now.day}日 ({WEEKDAY_NAMES[now.weekday()]}) {now.hour}時{now.minute}分",
        "today": f"{now.year}年{now.month}月{now.day}日 ({WEEKDAY_NAMES[now.weekday()]})",
        "tomorrow": f"{tomorrow.year}年{tomorrow.month}月{tomorrow.day}日 ({WEEKDAY_NAMES[tomorrow.weekday()]})",
        "weather_info": weather_info,
        "stock_price1_info": stock_price1_info,
        "stock_price2_info": stock_price2_info,
        "exchange_rate1_info": exchange_rate1_info,
        "exchange_rate2_info": exchange_rate2_info,
        "train_operation_info": train_operation_info,
        "news_info": news_info,
        "voice_url": voice_url
    }
    
