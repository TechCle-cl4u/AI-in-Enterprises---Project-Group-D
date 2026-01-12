#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 20:36:14 2026

@author: clemenslutz
"""

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from ollama import Client
from pathlib import Path



def cloud_call(prompt_text, llm_model, temperature=0.4):
    
    api_key = Path("api_key.txt").read_text(encoding="utf-8").strip()
    client = Client(
         host='https://ollama.com',
         headers={"Authorization": f"Bearer {api_key}"}

     )


    messages = [{"role": "user", "content": prompt_text}]

    full_text = ""
    
    for part in client.chat(llm_model, messages=messages, stream=True):
        full_text += part.message.content or ""

    return full_text

def optimize_job_description(text: str, llm_model: str) -> str:
    prompt = PromptTemplate(
        input_variables=["query"],
        template="""
        You are a tool tasked with optimizing a job description.
        
        INPUT:
        {query}
        
        TASK:
        Give a job description including required skills for this position (English).
        Try to assume the required skills based on the input given.
        Include:
        - Job title
        - Short summary
        - Responsibilities
        - Required skills (must-have)
        - Preferred skills (nice-to-have)
        
        INSTRUCTION:
        Give back the job description without any markdown elements.
        """
    )
        
    prompt_text = prompt.format(query=text)

    if llm_model == "gpt-oss:120b":
        return cloud_call(prompt_text, llm_model, temperature=0.1)

    else:
        llm = ChatOllama(model=llm_model, temperature=0.1)
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"query": text})