from flask import Flask,jsonify,request
from flask_cors import CORS
import pandas as pd

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


@app.route('/api/templeteData',methods=['GET'])
def get_templeteData():
    return jsonify({'templeteData':templeteData})

@app.route('/api/audio',methods=['POST'])
def play_audio():
    audioId=request.json
    print(audioId['id'])
    return jsonify({'message':'hello from flask!'},200)


if __name__=='__main__':
    app.run(debug=True,port=5000)