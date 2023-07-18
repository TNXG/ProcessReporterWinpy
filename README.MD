# Process Reporter For Windows Python

Process Reporter for Winpy 是一个使用 Python 的 Windows 应用程序。它旨在实时报告当前用户在 PC
上正在使用的前台应用程序的名称，以及正在播放的任何媒体信息并向[Shiro](https://github.com/Innei/Shiro)上报

实现原理参考了[Linux](https://github.com/ttimochan/processforlinux)版本的上报程序

[获取媒体播放信息](https://stackoverflow.com/questions/65011660/how-can-i-get-the-title-of-the-currently-playing-media-in-windows-10-with-python)

## 配置项
```yaml
config:
  api_url: 'apiurl' # https://api.example.com/api/v2/ps/update
  api_key: 'apikey' # 设置的key
  report_time: '10' # 上报时间间隔，单位秒
  keywords: # 关键词屏蔽，数组形式
    - 'pronhub'
```

## 其他系统的上报程序

- [MacOS](https://github.com/mx-space/ProcessReporterMac)
- [Linux](https://github.com/ttimochan/processforlinux)
