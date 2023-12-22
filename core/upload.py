import requests
import time
import logging

def report(process_name, media_update, api_key, api_url):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; TokaiTeio) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82 iykrzu/114.514'
    }
    timestamp = int(time.time())
    if media_update:
        update_data = {
            'timestamp': timestamp,
            'process': process_name,
            'media': {'title': media_update['title'], 'artist': media_update['artist']},
            'key': api_key
        }
    else:
        update_data = {
            'timestamp': timestamp,
            'process': process_name,
            'key': api_key
        }
    try:
        # 发送post请求，5秒超时
        response = requests.post(api_url, json=update_data, headers=headers, timeout=5)
        response = response.json()
        logging.info(response)
        print(response)
    except Exception as e:
        logging.error(e)
        print(e)