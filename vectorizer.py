from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

def vectorize_documents(docs):
    embeddings = OllamaEmbeddings(model="embeddinggemma")
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore
