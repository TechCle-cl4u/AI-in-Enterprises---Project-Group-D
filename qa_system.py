from langchain_classic.chains import RetrievalQA
from ollama import Client
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from pathlib import Path




def cloud_call(prompt_text, model, temperature=0.1):
    api_key = Path("api_key.txt").read_text(encoding="utf-8").strip()
    if not api_key:
        raise ValueError("Issue with API Key")
    
    client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {api_key}"},
)


    messages = [{"role": "user", "content": prompt_text}]

    full_text = ""
    
    for part in client.chat(model, messages=messages, stream=True):
        full_text += part.message.content or ""

    return full_text

def compare_cvs_job_description(job_description, vectorstore, model):
    task_text = Path("prompt.txt").read_text(encoding="utf-8")

    prompt = PromptTemplate(
        input_variables=["context", "question"],          
        partial_variables={"task_text": task_text},       
        template=(
            "You are screening CVs.\n\n"
            "JOB DESCRIPTION:\n{question}\n\n"
            "CV EXCERPTS:\n{context}\n\n"
            "TASK:\n{task_text}\n"
        ),
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 🔀 Regelbasierter Switch
    if model == "gpt-oss:120b":
        docs = retriever.get_relevant_documents(job_description)
        context = "\n\n".join(d.page_content for d in docs)
        formatted_prompt = prompt.format(context=context, question=job_description)

        text = cloud_call(formatted_prompt, model=model, temperature=0.1)

        return text

    # 🧠 Lokales Ollama über LangChain
    llm = ChatOllama(model=model, temperature=0.1)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
    )

    out = qa.invoke({"query": job_description})
    return out["result"]