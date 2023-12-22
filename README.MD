# Process Reporter For Windows Python

Process Reporter for Winpy 是一个使用Python开发的Windows应用程序。它旨在实时报告当前用户在PC上正在使用的前台应用程序的名称，以及正在播放的任何媒体信息，并将报告发送到 [Shiro](https://github.com/Innei/Shiro)。

该程序的实现借鉴了 [Linux版本](https://github.com/ttimochan/processforlinux) 的报告程序。

[获取媒体播放信息](https://stackoverflow.com/questions/65011660/how-can-i-get-the-title-of-the-currently-playing-media-in-windows-10-with-python)

[使用Python获取网易云正在播放的音乐](https://egg.moe/2020/07/get-netease-cloudmusic-playing/)

## 使用方法

这里提供了三种使用方法：

### 1. 使用源代码

```bash
git clone https://github.com/TNXG/ProcessReporterWinpy.git
cd ProcessReporterWinpy
pip install -r requirements.txt
```

将`example_config.yml`重命名为 `config.yml`，并在`config.yml`文件中填写配置项。

然后运行`main.py`即可：

```bash
python main.py --path "运行目录的路径"
```

### 2. 使用发布版本

您可以从 [Releases页面](https://github.com/TNXG/ProcessReporterWinpy/releases) 下载已发布的版本。

将`example_config.yml`重命名为 `config.yml`，并在`config.yml`文件中填写配置项。

```bash
processforwinpy.exe --path "运行目录的路径"
```

### 3. ProcessReporterWinpy Launcher

我们提供了一个简单的启动器，您可以在 [Releases 页面](https://github.com/TNXG/ProcessReporterWinpy/releases) 下载已发布的版本。
ProcessReporterWinpy Launcher 可以帮助您在后台运行 ProcessReporterWinpy，最小化到托盘，而无需打开命令行窗口。

在 0.0.2-rc2 之前的版本，`--path`为必填项。

## 配置项

将`example_config.yml`重命名为 `config.yml`，并在`config.yml`文件中填写配置项。

```yaml
config:
  api_url: 'apiurl' # https://api.example.com/api/v2/fn/ps/update
  api_key: 'apikey' # 设置的key
  report_time: '10' # 上报时间间隔，单位秒
  keywords: # 关键词屏蔽，数组形式
    - 'pronhub'

  # replace的第一行与replace_to的第一行对应，以此类推，`cloudmusic`会被替换为`网易云音乐`，`msedge`会被替换为`Microsoft Edge`
  # 请不要删除配置项中默认替换的项目
  # 更多替换项查看`Innei/Shiro/blob/main/src/components/layout/header/internal/Activity.tsx`
  replace:
    - 'cloudmusic'
    - 'msedge'
  replace_to:
    - '网易云音乐'
    - 'Microsoft Edge'
```

## 其他系统的报告程序

- [macOS](https://github.com/mx-space/ProcessReporterMac)
- [Linux](https://github.com/ttimochan/processforlinux)

请根据您的需求选择适合的版本和使用方法。如果有任何问题，请随时提问。

提问前请先阅读[tvvocold/How-To-Ask-Questions-The-Smart-Way: How To Ask Questions The Smart Way 《提问的智慧》中文版 (github.com)](https://github.com/tvvocold/How-To-Ask-Questions-The-Smart-Way)
