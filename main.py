from core.replace import replace_process_name
from core.upload import report
from core.search import search
from core.get_process_name import get_active_window_process_and_title
from core.get_media_info import get_media_info
from argparse import ArgumentParser

import os
import sys
import yaml
import time
import shutil
import asyncio
import logging

parser = ArgumentParser()
parser.add_argument("--path", help="指定配置项路径")
args = parser.parse_args()
path = args.path

if not path:
    path = os.path.dirname(os.path.realpath(sys.argv[0]))

if not os.path.exists(path + '/logs/'):
    os.makedirs(path + '/logs/')

if not os.path.exists(path + '/cache/'):
    os.makedirs(path + '/cache/')
else:
    shutil.rmtree(path + '/cache/')
    os.makedirs(path + '/cache/')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=os.path.join(path + '/logs/', f"{time.strftime('%Y-%m-%d', time.localtime())}.log"))

first_play = True


def read_config(config_path=None):
    if not config_path:
        config_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'config.yml')
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
    netease_autu_report_enable = config['config']['special']['netease_autu_report']['enable']
    netease_autu_report_cookies = config['config']['special']['netease_autu_report']['cookies']
    netease_autu_report_apiurl = config['config']['special']['netease_autu_report']['api_url']
    return api_url, api_key, report_time, keywords, process_replace, process_replace_to


async def main():
    media_update = {}
    # 读取配置文件
    api_url, api_key, report_time, keywords, process_replace, process_replace_to = read_config()
    # 获取当前活动窗口的进程名和标题
    process_name, window_title = get_active_window_process_and_title()
    # 如果process_name为空，使用window_title
    if not process_name:
        process_name = window_title
    # 将exe干掉
    process_name = process_name.replace('.exe', '')
    # 替换进程名
    process_name = replace_process_name(
        process_name, process_replace, process_replace_to)
    # 获取媒体信息
    media_info = await get_media_info()
    if media_info and not any(keyword in media_info['title'] for keyword in keywords):
        media_update['title'] = media_info['title']
        media_update['artist'] = media_info['artist']
    cloudmusic = search('cloudmusic.exe')
    if cloudmusic:
        if ' - ' in cloudmusic:
            media_update['title'] = cloudmusic.split(' - ')[0]
            media_update['artist'] = cloudmusic.split(' - ')[1]
        else:
            media_update['title'] = cloudmusic
            media_update['artist'] = None
    # 上传信息
    report(process_name, media_update, api_key, api_url)
    # 休息report_time秒
    await asyncio.sleep(report_time)

if __name__ == "__main__":
    # 无数次的运行！
    while True:
        asyncio.run(main())
