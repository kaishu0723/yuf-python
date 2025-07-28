import socket,base64,json
from .cartesia import cartesia

HOST='127.0.0.1'
PORT=30010

# ---server setup---
def serverSetup():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((HOST,PORT))
    server.listen(1)
    print('WaitStartGame')
    conn,addr=server.accept()
    return conn

answer_templates=[]
# ---make sendData---
def makeSendData(text):
    audioData=base64.b64encode(cartesia(text,'ja').content).decode('utf-8')
    sendData={'message':f'{text}','audio':audioData}
    sendJsonData=json.dumps(sendData)
    return sendJsonData
