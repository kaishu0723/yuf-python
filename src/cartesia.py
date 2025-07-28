import requests,os,pyaudio
from dotenv import load_dotenv

load_dotenv()
apiKey=os.getenv("CARTESIA_API_KEY")

def cartesia(text,lang):
    apiURL=os.getenv("CARTESIA_API_ENDPOINT_URL")
    payload={
        "model_id":"sonic-2",
        "transcript":f"{text}",
        "voice":{
            "mode":"id",
            "id":"c85c2df5-c4d8-4309-8e16-753bb31ed61a"
        },
        "output_format":{
            "container":"wav",
            "encoding":"pcm_s16le",
            "sample_rate":44100
        },
        "language":f"{lang}"
    }

    headers={
        "Cartesia-Version":"2025-04-16",
        "Authorization":f"Bearer {apiKey}",
        "Content-Type":"application/json"
    }

    response=requests.post(apiURL,json=payload,headers=headers)
    return response

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

if __name__=="__main__":
    sampleText="""
    深く切り立った岩壁が約12kmも続き、狭いところでは幅2mほど、もっとも深いところでは高さが60mにもなります。
幽玄とか幻想とか形容される美しい峡谷です。

峡谷降り口から入ってすぐは、水の流れも緩やかで、春夏には子供たちが水遊びをする歓声が賑やかさをみせます。
秋から冬にかけては静かな峡谷に魅せられた写真家の方が多く、写真家の聖地とまで言われることもあります。
峡谷深部には数万年は落ちずにあるチョックストーンが神秘の景色を見せていて、近年はここを目指す峡谷探検が盛んになっています。

アクティビティも多くの事業者が企画しており、パックラフトツアーやキャニオニングツアーなどもよく催行されています。
    """
    audioData=cartesia(sampleText,"ja")
    playSound(audioData.content)