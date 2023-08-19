import requests
import json

host = "127.0.0.1" 
port = 50021

def audio_query(text, speaker):
    query_payload = {"text": text, "speaker": speaker}
    r = requests.post(f"http://{host}:{port}/audio_query", 
                    params=query_payload)
    if r.status_code == 200:
        query_data = r.json()
        return query_data
    return None

def synthesis(speaker, query_data):
    synth_payload = {"speaker": speaker}
    r = requests.post(f"http://{host}:{port}/synthesis", params=synth_payload, 
                        data=json.dumps(query_data))
    if r.status_code == 200:
        return r.content
    return None

def text_to_speech(text, speaker=8):
    query_data = audio_query(text,speaker)
    voice_data=synthesis(speaker,query_data)
    
    return voice_data