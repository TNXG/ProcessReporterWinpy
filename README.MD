# Process Reporter For Windows Python

Process Reporter for Winpy 是一个使用Python开发的Windows应用程序。它旨在实时报告当前用户在PC上正在使用的前台应用程序的名称，以及正在播放的任何媒体信息，并将报告发送到[Shiro](https://github.com/Innei/Shiro)。

该程序的实现借鉴了[Linux版本](https://github.com/ttimochan/processforlinux)的报告程序。

[获取媒体播放信息](https://stackoverflow.com/questions/65011660/how-can-i-get-the-title-of-the-currently-playing-media-in-windows-10-with-python)

## 使用方法

这里提供了三种使用方法：

### 1. 使用源代码

```bash
git clone https://github.com/TNXG/ProcessReporterWinpy.git
cd ProcessReporterWinpy
pip install -r requirements.txt
```

在`config.yml`文件中填写配置项。

然后运行`main.py`即可：

```bash
python main.py
```

### 2. 使用发布版本

您可以从[Releases页面](https://github.com/TNXG/ProcessReporterWinpy/releases)下载已发布的版本。

在`config.yml`文件中填写配置项。

```bash
processforwinpy.exe --path "运行目录的路径"
```
### 3. ProcessReporterWinpy Launcher
我们提供了一个简单的启动器，您可以在[Releases页面](https://github.com/TNXG/ProcessReporterWinpy/releases)下载已发布的版本。
ProcessReporterWinpy Launcher可以帮助您在后台运行ProcessReporterWinpy，最小化到托盘，而无需打开命令行窗口。

## 配置项

在`config.yml`文件中，您可以配置以下选项：

```yaml
config:
  api_url: 'apiurl'  # 上报API的URL，例如 https://api.example.com/api/v2/ps/update
  api_key: 'apikey'  # 您的API密钥
  report_time: '10'  # 上报时间间隔，单位为秒
  keywords:         # 屏蔽的关键词列表，以数组形式提供
    - 'pronxxxxx'
```

## 其他系统的报告程序

- [MacOS](https://github.com/mx-space/ProcessReporterMac)
- [Linux](https://github.com/ttimochan/processforlinux)

请根据您的需求选择适合的版本和使用方法。如果有任何问题，请随时提问。
