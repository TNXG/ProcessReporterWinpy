import os
import time
import requests
import ctypes
import yaml
import asyncio
import logging
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--path", help="指定配置项路径")
args = parser.parse_args()
path = args.path

if not os.path.exists(path + '/logs/'):
    os.makedirs(path + '/logs/')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=os.path.join(path + '/logs/', f"{time.strftime('%Y-%m-%d', time.localtime())}.log"))


async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:
        info = await current_session.try_get_media_properties_async()
        info_dict = {song_attr: getattr(info, song_attr) for song_attr in dir(info) if not song_attr.startswith('_')}
        info_dict['genres'] = list(info_dict['genres'])
        return info_dict


def get_active_window_process_and_title():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    window_title = ctypes.create_unicode_buffer(255)
    ctypes.windll.user32.GetWindowTextW(hwnd, window_title, ctypes.sizeof(window_title))
    process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    process_handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, process_id.value)
    process_name = ctypes.create_unicode_buffer(255)
    ctypes.windll.psapi.GetModuleBaseNameW(process_handle, None, process_name, ctypes.sizeof(process_name))
    return process_name.value, window_title.value


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


async def main(keywords_to_exclude):
    api_url, api_key, report_time, keywords, replace, replace_to = read_config(path)
    while True:
        media_update = {}
        media_info = await get_media_info()
        process_name, window_title = get_active_window_process_and_title()
        if media_info and not any(keyword in media_info['title'] for keyword in keywords_to_exclude):
            media_update['title'] = media_info['title']
            media_update['artist'] = media_info['artist']
        process_name = process_name.replace('.exe', '')
        # 替换process_name
        for i in range(len(replace)):
            if process_name == replace[i]:
                process_name = replace_to[i]
                break
        report(process_name, media_update, api_key, api_url)
        await asyncio.sleep(report_time)


def read_config(config_path):
    if not config_path:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')
    else:
        config_path = os.path.join(config_path, 'config.yml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    api_url = config['config']['api_url']
    api_key = config['config']['api_key']
    report_time = int(config['config']['report_time'])
    keywords = config['config']['keywords']
    process_replace = config['config']['replace']
    process_replace_to = config['config']['replace_to']
    return api_url, api_key, report_time, keywords, process_replace, process_replace_to


if __name__ == "__main__":
    asyncio.run(main(read_config(path)[3]))
