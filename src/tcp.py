import socket,json,threading

HOST='127.0.0.1'
PORT=30010
sendData={
        'message':'test clear!',
        'audioTime':7
        }
def tcp_server_setup():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((HOST,PORT))
    server.listen(1)
    print('WaitStartGame')
    conn,addr=server.accept()
    data_updated_event=threading.Event()
    data_lock=threading.Lock()
    return conn,server

def sendMessage(data_lock,data_updated_event,conn):
    while True:
        data_updated_event.wait()
        
        with data_lock:
            data_updated_event.clear()
            current_data=sendData.copy()
        
        try:
            conn.sendall(json.dumps(current_data).encode('utf-8'))
        except(ConnectionResetError,BrokenPipeError):
            break
        
def eventHandler(data_lock,data_updated_event,data):
    with data_lock:
        sendData['audioTime']=data
    data_updated_event.set()


def main_thread(conn,server,targetFunction):
    input_thread=threading.Thread(target=targetFunction,daemon=True)
    input_thread.start()
    try:
        while True:
            data=conn.recv(1)
            if not data:
                break
    except(ConnectionResetError,BrokenPipeError):
        print('client disconnected')
    finally:
        conn.close()
        server.close()
        print('server close.')