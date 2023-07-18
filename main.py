import os
import time
import requests
import ctypes
import yaml
import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager


async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:
        info = await current_session.try_get_media_properties_async()
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}
        info_dict['genres'] = list(info_dict['genres'])
        return info_dict


def get_active_window_process_and_title():
    # 获取活动窗口的句柄
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    # 获取窗口标题
    window_title = ctypes.create_unicode_buffer(255)
    ctypes.windll.user32.GetWindowTextW(hwnd, window_title, ctypes.sizeof(window_title))
    # 获取进程 ID
    process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    # 获取进程句柄
    process_handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, process_id.value)
    # 获取进程名
    process_name = ctypes.create_unicode_buffer(255)
    ctypes.windll.psapi.GetModuleBaseNameW(process_handle, None, process_name, ctypes.sizeof(process_name))
    return process_name.value, window_title.value


def report(process_name, media_updata, api_key, api_url):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; TokaiTeio) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82 iykrzu/114.514'
    }
    timestamp = int(time.time())
    if media_updata:
        updata = {
            'timestamp': timestamp,
            'process': process_name,
            'media': {'title': media_updata['title'], 'artist': media_updata['artist']},
            'key': api_key
        }
    else:
        updata = {
            'timestamp': timestamp,
            'process': process_name,
            'key': api_key
        }

    response = requests.post(api_url, json=updata, headers=headers)
    response = response.json()
    print(response)


async def main(keywords_to_exclude):
    api_url, api_key, report_time, keywords = read_config()
    while True:
        media_updata = {}
        media_info = await get_media_info()
        process_name, window_title = get_active_window_process_and_title()
        if media_info and not any(keyword in media_info['title'] for keyword in keywords_to_exclude):
            media_updata['title'] = media_info['title']
            media_updata['artist'] = media_info['artist']
        report(process_name.replace('.exe', ''), media_updata, api_key, api_url)
        time.sleep(report_time)


def read_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    api_url = config['config']['api_url']
    api_key = config['config']['api_key']
    report_time = int(config['config']['report_time'])
    keywords = config['config']['keywords']
    return api_url, api_key, report_time, keywords


if __name__ == "__main__":
    asyncio.run(main(read_config()[3]))
