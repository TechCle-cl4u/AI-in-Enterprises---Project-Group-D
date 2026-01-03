from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama

def compare_cvs_job_description(job_description, vectorstore, model):

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are screening CVs.

JOB DESCRIPTION:
{question}

CV EXCERPTS:
{context}

TASK:
Rank the applicants and give short reasons (english).
"""
    )

    llm = ChatOllama(model=model, temperature=0.1)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    result = qa.invoke({"query": job_description})  # "query" bleibt so
    return result["result"]
