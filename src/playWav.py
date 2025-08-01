import wave
import pyaudio

def play_wav(filename):
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()

def get_wav_duration(filename):
    with wave.open(filename,'rb') as f:
        frames=f.getnframes()
        rate=f.getframerate()
        duration=frames/float(rate)
        second=int(duration)
    return second

if __name__=='__main__':
    print(type(get_wav_duration('./data/output.wav')))