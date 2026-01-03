#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 20:36:14 2026

@author: clemenslutz
"""

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

def optimize_job_description(text: str, llm_model: str) -> str:
    prompt = PromptTemplate(
        input_variables=["query"],
        template="""
You are a tool tasked with creating a job description.

INPUT:
{query}

TASK:
Give a job description including required skills for this position (English).
Include:
- Job title
- Short summary
- Responsibilities
- Required skills (must-have)
- Preferred skills (nice-to-have)
"""
    )

    llm = ChatOllama(model=llm_model, temperature=0.1)

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"query": text})
