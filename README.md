# Chinese-Subtitle-Recognition 中文字幕生成
Chinese Subtitle Recognition, Chinese translation, speech recognition <br>
本程序的功能是将视频文件转换成音频，然后使用model进行识别并输出相应时间轴的中文字幕，可用于识别任何中文语言的视频，技术层面使用OpenAI whisper <br>
# 系统需求
请安装Python，如果不知道什么是Python请不要运行此程序，根据系统选择合适的Python下载 https://www.python.org/downloads/windows/ <br>
<b>不要使用太过老旧的Python版本，因为未经过测试，程序包含所有Python依赖，如果你的显卡没有CUDA请在这里安装 https://developer.nvidia.com/cuda-12-1-0-download-archive <br>
本程序使用了两种不同程度的模型可供选择，默认加载小模型（small model），在第一次运行软件时下载，约300MB大小，至少需要你的显卡有3GB以上显存 <br>
可在软件内切换大模型（large model），首次切换需要下载，大模型约4GB大小，如果你的网络速度不佳可能需要几十分钟，下载过程中请不要终止程序，大模型有更好的识别效果，需要显存至少有12G以上 <br>
# 为什么要开发？
兰酱有个中国朋友喜欢听asmr，他吐槽女生说话声音难听清，所以就做了这个。(其实兰科有时做一些视频的时候也需要语音识别啦)
# 赞助 Donate
爱发电：https://afdian.com/a/xmlans
Ko-fi：https://ko-fi.com/stardreamcommunity
