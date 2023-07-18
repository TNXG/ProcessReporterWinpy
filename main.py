import os
import time
import requests
import ctypes
import yaml


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


def report(process_name, media_title, api_key, api_url):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; TokaiTeio) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82 iykrzu/114.514'
    }
    timestamp = int(time.time())
    if media_title:
        updata = {
            'timestamp': timestamp,
            'process': process_name,
            'key': api_key
        }

    response = requests.post(api_url, json=updata, headers=headers)
    response = response.json()
    print(response)


def main():
    api_url, api_key, report_time = read_config()
    while True:
        process_name, window_title = get_active_window_process_and_title()
        media_title = "None"  # Todo: 媒体标题获取
        report(process_name.replace('.exe', ''), media_title, api_key, api_url)
        time.sleep(report_time)


def read_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    api_url = config['config']['api_url']
    api_key = config['config']['api_key']
    report_time = int(config['config']['report_time'])
    return api_url, api_key, report_time


if __name__ == "__main__":
    main()
