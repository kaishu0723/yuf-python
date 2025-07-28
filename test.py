import whisper

model=whisper.load_model('base')
result=model.transcribe('./data/output.wav')
print(result['text'])