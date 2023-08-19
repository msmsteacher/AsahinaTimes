import datetime
from enum import Enum

class UseVoicevoxOption(str, Enum):
    """
    VOICEVOXはどの方法を使うかの設定値
    """

    # エンジンを使用する
    # この場合エンジンのディレクトリで以下を先に実行しておく必要がある
    # run.exe --use_gpu
    ENGINE = "ENGINE"
    
    # ローカルコードを使用する
    # 事前準備は不要
    LOCALCODE = "LOCALCODE"

# VoicevoxCoreで使用する設定値
USE_VOICEVOX_OPTION: UseVoicevoxOption = UseVoicevoxOption.LOCALCODE
SPEAKER_ID: str = 20

# datetimeの曜日情報
WEEKDAY_NAMES: list[str] = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

# はじめの挨拶(時間ごとに変動)
def greet_by_time(current_time: datetime) -> str:
    if 5 <= current_time.hour < 10:
        return "おはようございます"
    elif 10 <= current_time.hour < 17:
        return "こんにちは"
    else:
        return "こんばんは"

# 締めの挨拶(時間ごとに変動)
def last_message_by_time(current_time: datetime) -> str:
    if 5 <= current_time.hour < 12:
        return "今日も一日頑張りましょう！"
    elif 12 <= current_time.hour < 14:
        return "午後からも頑張りましょう！"
    elif 14 <= current_time.hour < 17:
        return "今日も残り少し、頑張りましょう！"
    elif 17 <= current_time.hour < 24:
        return "今日も一日お疲れ様でした！"
    else:
        return "夜遅くまでご苦労さまです！"