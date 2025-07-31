from flask import Flask,jsonify,request
from flask_cors import CORS
import pandas as pd,threading,socket,json,time
from src.realtimeRecord import sampleRealtimeRecord
from src.playWav import play_wav

# --- setup ---
app=Flask(__name__)
CORS(app)
templeteData=[]
df=pd.read_csv('./data/templete.csv')
for _,row in df.iterrows():
    item={
        'id':row['id'],
        'query':row['query'],
        'response':row['response'],
    }
    templeteData.append(item)

HOST='127.0.0.1'
PORT=30010
sendData={
        'message':'test clear!',
        'audioTime':7
        }
data_updated_event=threading.Event()
data_lock=threading.Lock()
UE_conn=None


# --- routers ---
# /api/templeteData
@app.route('/api/templeteData',methods=['GET'])
def get_templeteData():
    return jsonify({'templeteData':templeteData})

# /api/audio
@app.route('/api/audio',methods=['POST'])
def play_audio():
    eventHandler(5)
    audioId=request.json
    data=df[df['id']==audioId['id']]
    audioData=data['audioData'].values[0]
    play_wav(f'./data/audioData/{audioData}')
    return jsonify({'message':'hello from flask!'},200)

# /api/realtime
@app.route('/api/realtime',methods=['POST'])
def realtimeGenerate():
    received=request.json
    print(received['message'])
    sampleRealtimeRecord()
    response={
        'answer':'Hello this is a test.'
    }
    return jsonify(response,200)

# --- UE server ---
def UE_server():
    global UE_conn
    try:
        server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST,PORT))
        server.listen(1)
        print('WaitStartGame')
        UE_conn,addr=server.accept()
        print(type(UE_conn))
        try:
            while True:
                data=UE_conn.recv(1)
                if not data:
                    break
        except(ConnectionResetError,BrokenPipeError):
            print('client disconnected')
        finally:
            UE_conn.close()
            server.close()
            print('server close.')
    except OSError as e:
        print(f"UE server error: {e}")
        print("Port 30010 might be in use. Please check if another instance is running.")

def sendMessage():
    while True:
        data_updated_event.wait()
        
        with data_lock:
            data_updated_event.clear()
            current_data=sendData.copy()
        
        
        try:
            print(type(UE_conn))
            UE_conn.sendall(json.dumps(current_data).encode('utf-8'))
        except(ConnectionResetError,BrokenPipeError):
            break
        
def eventHandler(data):
    print(type(UE_conn))
    with data_lock:
        sendData['audioTime']=data
    data_updated_event.set()
    


if __name__=='__main__':
    send_thread=threading.Thread(target=sendMessage,daemon=True)
    send_thread.start()
    UE_thread=threading.Thread(target=UE_server,daemon=True)
    UE_thread.start()
    app.run(debug=True,port=5000)