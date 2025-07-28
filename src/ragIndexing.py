import pandas as pd
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import chromadb
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
import pickle
from dotenv import load_dotenv

load_dotenv()

file_path='./data/spot-data.csv'

# --- make doc objects ---
df=pd.read_csv(file_path)
documents=[]
for _,row in df.iterrows():
    page_content=f'spot:{row['Title']}\ndescription:{row['spot_editor']}'
    metadata={
        'source':file_path,
        'spot':row['Title']
    }
    doc=Document(page_content=page_content,metadata=metadata)
    documents.append(doc)

# --- make vectorstore ---
embedding=OpenAIEmbeddings(model='text-embedding-ada-002')
client=chromadb.PersistentClient(path='./vectorstore')
vectorstore=Chroma(
    collection_name='yuf-data',
    embedding_function=embedding,
    client=client
)
vectorstore.add_documents(documents)

# --- make bm25 ---
bm25_retriever=BM25Retriever.from_documents(documents)
with open("./bm25.pkl",'wb') as f:
    pickle.dump(bm25_retriever,f)