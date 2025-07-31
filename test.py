import socket
import threading
import time
from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)
templeteData=[]
df=pd.read_csv('./data/templete.csv')
for _,row in df.iterrows():
    item={
        'id':row['id'],
        'query':row['query'],
        'response':row['response'],
    }
    templeteData.append(item)

# --- TCP Socket Server Configuration ---
TCP_HOST = '127.0.0.1'  # UEクライアントが接続するIPアドレス
TCP_PORT = 30010       # UEクライアントが接続するポート

# 接続中のTCPクライアントソケットを保持
# グローバル変数として定義し、Noneで初期化
ue_conn = None
ue_addr = None
ue_socket_lock = threading.Lock() # ue_connへのアクセスを保護するロック

# --- TCP Server Functions ---
def handle_ue_connection():
    """
    UEクライアントからの単一のTCP接続を管理する関数。
    このスレッドは、接続が確立されるとループでデータの送受信を試みる。
    """
    global ue_conn, ue_addr
    
    # TCPサーバーソケットの作成と設定
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # ポート再利用
    
    try:
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(1) # 1つの接続のみ待ち受ける
        print(f"UEサーバーが {TCP_HOST}:{TCP_PORT} でリッスンを開始しました...")
        
        while True:
            # 既に接続がある場合は、それを閉じて次の接続を待つ (このアプリケーションは単一接続想定)
            if ue_conn:
                try:
                    ue_conn.close()
                    print(f"既存のUEクライアント接続 ({ue_addr}) を閉じました。")
                except Exception as e:
                    print(f"既存接続のクローズ中にエラー: {e}")
                finally:
                    with ue_socket_lock:
                        ue_conn = None
                        ue_addr = None

            print("UEクライアント接続待ち...")
            # クライアントからの接続を待機
            current_conn, current_addr = server_socket.accept()
            
            with ue_socket_lock:
                ue_conn = current_conn
                ue_addr = current_addr
            
            print(f"UEクライアントが接続しました: {ue_addr}")

            try:
                # 接続中のループ：UEからデータを受信しないが、接続維持のため
                # 定期的に小さなデータを受信試行したり、送信を待機したりする
                while True:
                    # ここではUEがデータを送らないため、受信はしない
                    # ただし、接続が切れたことを検知するためにrecvを試すことも可能
                    # 例: data = ue_conn.recv(1) # ブロッキングされるため注意
                    time.sleep(1) # CPU使用率を下げるための待機
                    
            except (ConnectionResetError, BrokenPipeError):
                print(f"UEクライアント {ue_addr} が切断されました。")
            except Exception as e:
                print(f"UEクライアント {ue_addr} との通信でエラーが発生しました: {e}")
            finally:
                # 接続が切れたらグローバル変数をリセット
                with ue_socket_lock:
                    if ue_conn == current_conn: # 念のため確認
                        ue_conn.close()
                        ue_conn = None
                        ue_addr = None
                print(f"UEクライアント {current_addr} との接続が終了しました。次の接続を待ちます。")

    except Exception as e:
        print(f"UEサーバーの起動または実行中に致命的なエラー: {e}")
    finally:
        if server_socket:
            server_socket.close()
        print("UEサーバーを閉じました。")

def send_data_to_ue(data_to_send):
    """
    接続中の単一のUEクライアントにデータを送信する関数
    """
    with ue_socket_lock:
        if ue_conn:
            try:
                # UEが認識できるようにJSON形式でエンコードし、改行コードを追加
                message_bytes = (data_to_send + '\n').encode('utf-8') 
                ue_conn.sendall(message_bytes)
                print(f"UEクライアント ({ue_addr}) にデータを送信しました: {data_to_send}")
            except (ConnectionResetError, BrokenPipeError):
                print(f"UEクライアント ({ue_addr}) への送信中に接続が切断されました。")
                # 接続が切れた場合は、handle_ue_connectionスレッドが新しい接続を待つ
                ue_conn = None # 接続状態をリセット
                ue_addr = None
            except Exception as e:
                print(f"UEクライアント ({ue_addr}) への送信中に予期せぬエラーが発生しました: {e}")
        else:
            print("UEクライアントが接続されていません。データは送信されませんでした。")

# --- Flask Routes (Main Thread) ---
@app.route('/api/templeteData',methods=['GET'])
def get_templeteData():
    return jsonify({'templeteData':templeteData})

@app.route('/api/audio', methods=['POST'])
def api_send_data():
    """
    Next.jsなどからのHTTPリクエストを受け取り、UEにデータを送信するエンドポイント
    """
    request_json = request.json
    if not request_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    # リクエストからデータを取得。例として'message'と'value'を送信
    message = request_json.get('message', 'Default message')
    value = request_json.get('value', 0)

    data_for_ue = f'{{"message": "{message}", "value": {value}}}' # JSON文字列としてフォーマット

    # UEへのデータ送信は、HTTPリクエストをブロックしないように別スレッドで実行
    # ここでは send_data_to_ue がロックを使うので直接呼び出しでも問題ないが、
    # 処理が重くなる可能性があれば、さらにスレッドを立てる
    threading.Thread(target=send_data_to_ue, args=(data_for_ue,)).start()
    
    return jsonify({"status": "success", "data_sent_to_ue": data_for_ue}), 200

# --- Main Execution ---
if __name__ == '__main__':
    # UEクライアントからのTCP接続を管理するスレッドを開始
    ue_tcp_thread = threading.Thread(target=handle_ue_connection)
    ue_tcp_thread.daemon = True # メインスレッド終了時にこのスレッドも終了
    ue_tcp_thread.start()

    # Flaskアプリケーションをメインスレッドで実行
    # use_reloader=False は、開発中にポート競合を防ぐため。
    # ファイル変更時の自動リロードは行われない。
    app.run( port=5000, debug=True, use_reloader=False)