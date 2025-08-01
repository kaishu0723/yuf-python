import requests,os,pyaudio
from dotenv import load_dotenv

load_dotenv()
apiKey=os.getenv("CARTESIA_API_KEY")

def cartesia(text):
    apiURL=os.getenv("CARTESIA_API_ENDPOINT_URL")
    payload={
        "model_id":"sonic-2",
        "transcript":f"{text}",
        "voice":{
            "mode":"id",
            "id":"bf0a246a-8642-498a-9950-80c35e9276b5"
        },
        "output_format":{
            "container":"wav",
            "encoding":"pcm_f32le",
            "sample_rate":44100
        },
        "language":"en"
    }

    headers={
        "Cartesia-Version":"2025-04-16",
        "Authorization":f"Bearer {apiKey}",
        "Content-Type":"application/json"
    }

    response=requests.post(apiURL,json=payload,headers=headers)
    return response.content

def playSound(audioData):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    output=True)
    try:
        stream.write(audioData)
    except Exception as e:
        print(f"Error occurred:{str(e)}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
