import sys
import os
import threading
import subprocess
import whisper
import torchaudio
import torch
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel, QComboBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class SubtitleWorker(QThread):
    finished_signal = pyqtSignal(str)

    def __init__(self, model, audio_path):
        super().__init__()
        self.model = model
        self.audio_path = audio_path

    def run(self):
        try:
            result = self.model.transcribe(self.audio_path, language="zh", temperature=0, logprob_threshold=-2.0, no_speech_threshold=0.1)
            subtitle_text = ""

            for i, segment in enumerate(result["segments"]):
                start_time = segment["start"]
                end_time = segment["end"]
                text = segment["text"]
                subtitle_text += f"{i+1}\n{start_time:.2f} --> {end_time:.2f}\n{text}\n\n"

            self.finished_signal.emit(subtitle_text)
        except RuntimeError as e:
            self.finished_signal.emit(f"字幕生成失敗: {e}")

class SubtitleGenerator(QWidget):
    update_text_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.model_options = ["small", "large"]
        self.selected_model = "small"
        self.initUI()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(self.selected_model, device=device)
        self.update_text_signal.connect(self.update_text)

    def initUI(self):
        self.setWindowTitle("Chinese-Subtitle-Recognition By Star Dream Studio")
        self.setGeometry(200, 200, 600, 550)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))

        layout = QVBoxLayout()

        self.logo_label = QLabel(self)
        self.logo_label.setPixmap(QPixmap(resource_path("logo.png")))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        self.label = QLabel("請選擇影片檔案")
        layout.addWidget(self.label)

        self.btn_select = QPushButton("選擇影片")
        self.btn_select.clicked.connect(self.select_video)
        layout.addWidget(self.btn_select)

        self.model_label = QLabel("選擇模型:")
        layout.addWidget(self.model_label)

        self.model_selector = QComboBox()
        self.model_selector.addItems(self.model_options)
        self.model_selector.currentTextChanged.connect(self.change_model)
        layout.addWidget(self.model_selector)

        self.btn_download_small = QPushButton("下載 Small 模型")
        self.btn_download_small.clicked.connect(lambda: self.download_model("small"))
        layout.addWidget(self.btn_download_small)

        self.btn_download_large = QPushButton("下載 Large 模型")
        self.btn_download_large.clicked.connect(lambda: self.download_model("large"))
        layout.addWidget(self.btn_download_large)

        self.btn_generate = QPushButton("生成字幕")
        self.btn_generate.clicked.connect(self.generate_subtitles)
        layout.addWidget(self.btn_generate)

        self.text_output = QTextEdit()
        layout.addWidget(self.text_output)

        self.btn_save = QPushButton("儲存字幕")
        self.btn_save.clicked.connect(self.save_subtitles)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)
        self.video_path = ""
        self.subtitle_text = ""

    def update_text(self, text):
        self.text_output.setText(text)

    def select_video(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "選擇影片檔案", "", "影片檔案 (*.mp4 *.mkv *.avi)")
        if file_path:
            self.video_path = file_path
            self.label.setText(f"選取檔案: {file_path}")

    def change_model(self, text):
        self.selected_model = text
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(self.selected_model, device=device)

    def download_model(self, model_name):
        def download():
            self.update_text_signal.emit(f"正在下載 {model_name} 模型，請稍候...")
            self.btn_download_small.setEnabled(False)
            self.btn_download_large.setEnabled(False)
            try:
                whisper.load_model(model_name)
                self.update_text_signal.emit(f"{model_name} 模型下載完成！")
            except Exception as e:
                self.update_text_signal.emit(f"下載失敗: {e}")
            finally:
                self.btn_download_small.setEnabled(True)
                self.btn_download_large.setEnabled(True)

        thread = threading.Thread(target=download)
        thread.start()

    def extract_audio(self, video_path, output_audio="audio.wav"):
        output_path = os.path.join(os.path.dirname(video_path), output_audio)
        ffmpeg_path = resource_path("ffmpeg.exe")

        if not os.path.exists(ffmpeg_path):
            self.update_text_signal.emit(" 未找到 ffmpeg.exe，請確保它和 .exe 在同一目錄！")
            return None

        cmd = [
    ffmpeg_path, "-i", video_path, "-vn", "-acodec", "pcm_s16le",
    "-ar", "16000", "-ac", "1", output_path, "-y"
        ]


        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
            else:
                return None
        except subprocess.CalledProcessError as e:
            return None

    def generate_subtitles(self):
        if not self.video_path:
            self.text_output.setText("請先選擇影片檔案！")
            return

        self.update_text_signal.emit("正在提取音訊...")
        audio_path = self.extract_audio(self.video_path)

        if not audio_path:
            return

        self.update_text_signal.emit("正在識別字幕...")
        self.worker = SubtitleWorker(self.model, audio_path)
        self.worker.finished_signal.connect(self.handle_subtitle_result)
        self.worker.start()

    def handle_subtitle_result(self, text):
        self.subtitle_text = text
        self.update_text_signal.emit(self.subtitle_text)
        with open("output.srt", "w", encoding="utf-8") as f:
            f.write(self.subtitle_text)

    def save_subtitles(self):
        if not self.subtitle_text:
            self.text_output.setText("沒有可儲存的字幕！")
            return

        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(self, "儲存字幕", "", "字幕檔案 (*.srt)")
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.subtitle_text)
            self.text_output.setText(f"字幕已儲存至: {save_path}")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = SubtitleGenerator()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(str(e))  
        print(f"程序崩溃！错误已写入 error.log：{e}")