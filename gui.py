import sys
import os
import threading
import subprocess
import whisper
import ffmpeg
import torchaudio
import torch
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QLabel, QComboBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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
        self.setGeometry(200, 200, 600, 500)
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

    def extract_audio(self, video_path, output_audio="audio.wav"):
        output_path = os.path.join(os.path.dirname(video_path), output_audio)
        try:
            subprocess.run([
                "ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", output_path, "-y"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            self.update_text_signal.emit(f"音訊提取失敗: {e}")
            return None
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            self.update_text_signal.emit("提取的音訊檔案無效或為空！")
            return None
        
        return output_path

    def generate_subtitles(self):
        if not self.video_path:
            self.text_output.setText("請先選擇影片檔案！")
            return
        
        self.update_text_signal.emit("正在提取音訊...")
        audio_path = self.extract_audio(self.video_path)
        
        if not audio_path:
            return
        
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            if waveform.numel() == 0:
                self.update_text_signal.emit("提取的音訊無效，音訊為空！")
                return
        except Exception as e:
            self.update_text_signal.emit(f"音訊載入失敗: {e}")
            return
        
        self.update_text_signal.emit("正在識別字幕...")
        
        def transcribe():
            try:
                result = self.model.transcribe(audio_path, language="zh", temperature=0)
                self.subtitle_text = ""
                
                for i, segment in enumerate(result["segments"]):
                    start_time = segment["start"]
                    end_time = segment["end"]
                    text = segment["text"]
                    self.subtitle_text += f"{i+1}\n{start_time:.2f} --> {end_time:.2f}\n{text}\n\n"
                
                self.update_text_signal.emit(self.subtitle_text)
                
                with open("output.srt", "w", encoding="utf-8") as f:
                    f.write(self.subtitle_text)
            except RuntimeError as e:
                self.update_text_signal.emit(f"字幕生成失敗: {e}")
        
        thread = threading.Thread(target=transcribe)
        thread.start()

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
    app = QApplication(sys.argv)
    window = SubtitleGenerator()
    window.show()
    sys.exit(app.exec())
