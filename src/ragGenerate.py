from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
import chromadb
from langchain_chroma import Chroma
import pickle
from langchain.retrievers import EnsembleRetriever
from dotenv import load_dotenv


load_dotenv()
sampleQuery='おすすめの観光スポットを知りたい'

# --- retriever ---
def retriever(query):
    with open('./bm25.pkl','rb') as f:
        bm25_retriever=pickle.load(f)

    embedding=OpenAIEmbeddings(model='text-embedding-ada-002')
    client=chromadb.PersistentClient(path='./vectorstore')
    vectorstore=Chroma(
        collection_name='yuf-data',
        embedding_function=embedding,
        client=client
    )
    vector_retriever=vectorstore.as_retriever()

    ensemble_retriever=EnsembleRetriever(
        retrievers=[vector_retriever,bm25_retriever],
        weights=[0.5,0.5]
    )
    context_list=ensemble_retriever.invoke(query)
    
    return context_list


# --- generate ---
def generate(query):
    context_list=retriever(query)
    context="\n---\n".join(doc.page_content for doc in context_list)
    prompt_template=f"""
    以下の情報のみに基づいて、質問に回答してください。情報に答えがない場合は、「わかりません」と答えてください。
    
    「情報」
    {context}

    [質問]
    {query}
    """
    
    llm=ChatOpenAI(model='gpt-4',temperature=0)
    response=llm.invoke(prompt_template)
    
    return response.content

if __name__=='__main__':
    print(generate(sampleQuery))