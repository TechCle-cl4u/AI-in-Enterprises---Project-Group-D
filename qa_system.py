from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama

def answer_question(question, vectorstore, model):
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""Use the following context to answer the question clearly and logically.
Think silently first (do not output) and then only give the final answer.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER (structured, precise, in English):"""
    )

    llm = ChatOllama(model=model, temperature=0.1)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa.invoke({"query": question})

    answer = result["result"]
    sources = [{"page": doc.metadata.get("page", "?"), 
                "content": doc.page_content,
                "document_name": doc.metadata.get("document_name", "Unknown Document")} 
               for doc in result["source_documents"]]

    return answer, sources
