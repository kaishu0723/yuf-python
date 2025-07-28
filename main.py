from src.tcp import serverSetup,makeSendData
from src.ragGenerate import generate

# ---send and recive---
conn=serverSetup()
while True:
    recvData=conn.recv(1024)
    if not recvData:
        break
    query=recvData
    print(query+' from UE')
    answer=generate(query)
    sendData=makeSendData(answer)
    conn.sendall(sendData.encode())
conn.close()