# Chinese-Subtitle-Recognition 中文字幕生成
Chinese Subtitle Recognition, Chinese translation, speech recognition <br>
本程序的功能是将视频文件转换成音频，然后使用model进行识别并输出相应时间轴的中文字幕，可用于识别任何中文语言的视频，技术层面使用OpenAI whisper <br>
# 下载并运行程序
exe打包有点小毛病懒得弄了，有点技术就直接下载Releases内完成的Python脚本start.py，并安装环境 (ffmpeg.exe放到发布包了，请一起下载和python文件放到一个目录) <br>
<code>pip install PyQt6 openai-whisper torch torchaudio ffmpeg-python</code> <br>
安装完环境之后，运行以下命令即可 <br>
<code>python start.py</code>
# 系统需求
Win10,11均经过测试 请安装Python，如果不知道什么是Python请不要运行此程序，根据系统选择合适的Python下载 https://www.python.org/downloads/windows/ <br>
<b>不要使用太过老旧的Python版本</b>，因为未经过测试，程序包含所有Python依赖，如果你的显卡没有CUDA请在这里安装 https://developer.nvidia.com/cuda-12-1-0-download-archive <br>
本程序使用了两种不同程度的模型可供选择，默认加载小模型（small model），在第一次运行软件时下载，约300MB大小，至少需要你的显卡有3GB以上显存 基础程序需要至少3G空余磁盘空间<br>
可在软件内切换大模型（large model），首次切换需要下载，大模型约4GB大小，如果你的网络速度不佳可能需要几十分钟，下载过程中请不要终止程序，大模型有更好的识别效果，需要显存至少有12G以上 安装large模型需要至少7G空余磁盘空间<br>
# 为什么要开发？
兰酱有个中国朋友喜欢听asmr，他吐槽女生说话声音难听清，所以就做了这个。(其实兰科有时做一些视频的时候也需要语音识别啦)
# 赞助 Donate
爱发电：https://afdian.com/a/xmlans
Ko-fi：https://ko-fi.com/stardreamcommunity
