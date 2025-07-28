import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import sys
import os

# 録音設定
SAMPLE_RATE = 44100  # サンプリングレート
CHANNELS = 1         # モノラル
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '../data/output.wav')

print("録音を開始します。Ctrl+Cで終了します。")

frames = []

def callback(indata, frames_count, time, status):
    if status:
        print(status, file=sys.stderr)
    frames.append(indata.copy())

try:
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
        while True:
            sd.sleep(1000)
except KeyboardInterrupt:
    print("\n録音を終了し、ファイルに保存します...")
    audio = np.concatenate(frames, axis=0)
    wav.write(OUTPUT_PATH, SAMPLE_RATE, (audio * 32767).astype(np.int16))
    print(f"保存しました: {OUTPUT_PATH}")
except Exception as e:
    print(f"エラーが発生しました: {e}")
