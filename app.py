from file_uploader import upload_pdfs
from vectorizer import vectorize_documents
from qa_system import compare_cvs_job_description
from job_description_optimizer import optimize_job_description
from pathlib import Path
from langchain.prompts import PromptTemplate
import time
import streamlit as st 
import plotly.express as px
import pandas as pd
import os
import pandas as pd
import streamlit.components.v1 as components
import uuid



#============ S T A R T ===============================================================
#Final Project Group D
#Authors:
#-Lutz Clemens
#-Umair 
#-Lin Hao
#-El Roumi Mohamed


#This file is used for the user interface. The underlying logic
#is mostly implemented in other files and is imported respectively.
#Streamlit is a package that we use as it guarantees good usability 
#with limited complexity.
#=======================================================================================
 


#============ Set-up of user interface - include logos, headings, et cetera=============
st.set_page_config(
    page_title="CV Screening",
    page_icon="favicon.ico")


#=====Page selection for navigation between 'Main',  'Logs' and 'Prompt Settings' pages =====
page = st.sidebar.selectbox("Choose a page:", ["Main", "Log File Analysis", "Prompt Settings"])





#============ Prompt import ===============================================================

PROMPT_FILE = Path("prompt.txt")

FIXED_PREFIX = """You are screening CVs.

JOB DESCRIPTION:
{question}

CV EXCERPTS:
{context}

TASK:
"""

DEFAULT_DYNAMIC = "Rank the applicants and give short reasons (english)."

def load_prompt_text() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    PROMPT_FILE.write_text(DEFAULT_DYNAMIC, encoding="utf-8")
    return DEFAULT_DYNAMIC

def save_prompt_text(text: str) -> None:
    PROMPT_FILE.write_text(text.strip() + "\n", encoding="utf-8")

def build_prompt_template(dynamic_task_text: str) -> PromptTemplate:
    return PromptTemplate(
        input_variables=["context", "question"],
        template=FIXED_PREFIX + dynamic_task_text.strip() + "\n"
    )




#============Main Page (CV Upload and insertion Job Description)==============
if page == "Main":
    
    #======Selection of model used - ensure model is running======
    llm_model = st.sidebar.selectbox(
        'Choose model:',
        ('gemma3:12b', 'gemma3:4b', 'gemma3:1b', 'ministral-3:8b', 'ministral-3:14b', 'gpt-oss:120b'),
        index=0  # gemma3:12b set as default
    )
    
    #=========================================================================
    


    #Setting of logo + title
    st.image("title_logo_cv_screening_tool.png", width = 400)
    st.title("HR Tool - Job Finder")
    
    
    
    #=======Job Description insertion (+optimization)=========================
    st.subheader("Insert and optimize job description")
    
    


    #Set states - required for buttons optimize + undo
    
    
    st.session_state.setdefault("job_input", "")
    st.session_state.setdefault("original_text", "")
    st.session_state.setdefault("job_description", None)
    st.session_state.setdefault("optimized", False)
    st.session_state.setdefault("was_optimized", False)
    
    def set_optimized():
        st.session_state.original_text = st.session_state.job_input
        optimized_text = optimize_job_description(st.session_state.job_input, llm_model)
    
        st.session_state.job_input = optimized_text          # <-- gleicher Textbereich zeigt Ergebnis
        st.session_state.job_description = optimized_text    # <-- final speichern
    
        st.session_state.optimized = True                    # <-- lock input
        st.session_state.was_optimized = True
    
    def set_original():
        st.session_state.original_text = st.session_state.job_input
        st.session_state.job_description = st.session_state.job_input  # <-- final speichern
    
        st.session_state.optimized = False                   # <-- weiter editierbar!
        st.session_state.was_optimized = False
    
    def undo():
        st.session_state.job_input = st.session_state.original_text
        st.session_state.job_description = None
        st.session_state.optimized = False
        st.session_state.was_optimized = False
    
    st.text_area(
        "Insert Job Description",
        key="job_input",
        height=250,
        disabled=st.session_state.optimized
    )
    
    if not st.session_state.optimized:
        st.session_state.job_description = st.session_state.job_input
    
    job_description = st.session_state.job_description
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("Optimize Job Description", on_click=set_optimized, disabled=st.session_state.optimized)
    with col2:
        st.button("Use Original Text", on_click=set_original)
    
    if st.session_state.was_optimized:
        st.button("Undo", on_click=undo)

     
    #=========================================================================
    
        

    #============ Upload and store CV's ====================================================
    if job_description:
        uploaded_files = st.file_uploader("Upload up to 5 CV's", accept_multiple_files=True, type="pdf")
        MAX_FILES = 5

        if uploaded_files:
            if len(uploaded_files) > MAX_FILES:
                st.warning(f"Maximum {MAX_FILES} CV's allowed. Processing the first {MAX_FILES} files.")
                processed_files = uploaded_files[:MAX_FILES]
            else:
                processed_files = uploaded_files
        
            # Process processed_files here
            st.subheader("CV's to be screened:")
            file_number = 0
            for file in processed_files:
                file_number += 1
                st.write(f" CV Number {file_number}:  {file.name}")
            
            
            #Check, if files are uploaded
            if processed_files:
            
            #Show user feedback - overview how many files have been uploaded
                st.success(f"{len(processed_files)} CV's uploaded successfully!")
              
            
     
    
        
        
        
        
            if job_description and processed_files:
                
                #Button to start screening of CV's when files uploaded and job description given:
                if st.button("Start Screening CV's"):
                    run_id = str(uuid.uuid4())
                    st.session_state["last_run_id"] = run_id
                    
                    
                    
                    
                    
                    #============ Index and vectorize documents =======================================
                    #-Call function upload_pdfs from file_uploader.py
                    #-Store documents, Split into chunks, index together with metadata (document names)
                    #==================================================================================
                    
                    with st.spinner("Processing CV's (Vectorization)"):
                       
    
                        pdf_paths, docs = upload_pdfs(processed_files)
                
                        # Vectorization of index
                        vectorstore = vectorize_documents(docs)
                    
                    #==================================================================================
                    
                    
                    
                    
                    
                    
                    #============ Screen CV's and give recommendation =================================
                    #-Call function xy from xy.py
                    #-Give recommendation based on job description & CV's
                    #==================================================================================
                    
                    start_time = time.time()  # Start timer for log entry
           
                    with st.spinner("Comparing CV's with Job Description"):
                       # Call function and pass job_description and vectorstore
                       recommendation = compare_cvs_job_description(job_description, vectorstore, llm_model)
                       st.subheader("Recommendation:")
                       st.write(recommendation)
                       
                    end_time = time.time()  # End timer for log entry
                    analysis_time = end_time - start_time  # Calculate time analyzing
                   
                    # Calculation document size for log entry
                    document_size = sum([len(file.getbuffer()) for file in processed_files])  # Get size from file buffer
                
                    
                
                    #Read task_text (Prompt) for log entry
                    task_text = Path("prompt.txt").read_text(encoding="utf-8")
                
                
                    log_entry = {
                           "Run ID": run_id,
                           "Job Description": job_description,
                           "Recommendation": recommendation,
                           "Document Size (bytes)": document_size,
                           "Analysis Time (seconds)": analysis_time,
                           "LLM Model": llm_model,
                           "Feedback": "", #Set later
                           "Prompt Task": task_text
                        }
                        
                    if os.path.exists('log_file_cv_screening.csv'):
                           log_df = pd.read_csv('log_file_cv_screening.csv')
                    else:
                           log_df = pd.DataFrame(columns=list(log_entry.keys()))
                        
                    log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
                    log_df.to_csv('log_file_cv_screening.csv', index=False)
                    st.success("Log entry saved!")
                        
                        # --- Feedback UI direkt danach ---
                    st.subheader("Feedback")
                    st.write("How satisfied are you with the response?")
                    c1, c2 = st.columns(2)
                    
                        
                    def save_feedback(value: str):
                        run_id = st.session_state.get("last_run_id")
                        if not run_id:
                            return
                        df = pd.read_csv('log_file_cv_screening.csv')
                        df.loc[df["Run ID"] == run_id, "Feedback"] = value
                        df.to_csv('log_file_cv_screening.csv', index=False)
                        st.session_state["feedback_saved"] = True
                        
                    with c1:
                            st.button("👍", on_click=save_feedback, args=("positive",))
                    with c2:
                            st.button("👎", on_click=save_feedback, args=("negative",))
                        
                    if st.session_state.get("feedback_saved"):
                            st.success("Thanks! Feedback saved.")
                    
            











#------------ Log File Analysis Page (for viewing logs) ------------
elif page == "Log File Analysis":
    st.title("Log File Analysis")
    
    # Display logs if available
    if os.path.exists('log_file_cv_screening.csv'):
        log_df = pd.read_csv('log_file_cv_screening.csv')
        
        #Set column order
        log_df = log_df[["Run ID", "Prompt Task", "Job Description", "Recommendation",
                 "Document Size (bytes)", "Analysis Time (seconds)",
                 "LLM Model", "Feedback"]]

        #Log Table based on CSV file
        st.write("Previous log entries:")
        st.dataframe(log_df, use_container_width=True)

        
        #Data preparation
        model_counts = log_df["LLM Model"].value_counts().reset_index()
        model_counts.columns = ["LLM Model", "Count"]
    
        avg_time = log_df.groupby("LLM Model")["Analysis Time (seconds)"].mean().reset_index()
    
        sentiment_counts = log_df["Feedback"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
    
        # Layout
        col1, col2 = st.columns(2)
    
        with col1:
            fig_models = px.pie(model_counts, names="LLM Model", values="Count",
                                title="Model usage", height=280)
            st.plotly_chart(fig_models, use_container_width=True)
    
        with col2:
            fig_sentiment = px.pie(sentiment_counts, names="Sentiment", values="Count",
                                   title="User satisfaction", height=280)
            st.plotly_chart(fig_sentiment, use_container_width=True)
    
        fig_time = px.bar(avg_time, x="LLM Model", y="Analysis Time (seconds)",
                          title="Average analysis time per model (seconds)", height=280)
        st.plotly_chart(fig_time, use_container_width=True)
        
        
    else:
        st.write("No logs available yet. Perform some analysis on the 'Main' page to generate logs.")
  
        
  


elif page == "Prompt Settings":
    st.title("Prompt Settings")

    current_text = load_prompt_text()

    edited = st.text_area(
        "Editable prompt part (only TASK text):",
        value=current_text,
        height=220
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save"):
            save_prompt_text(edited)
            st.success("Saved to prompt.txt")

    with col2:
        if st.button("Reset to default"):
            save_prompt_text(DEFAULT_DYNAMIC)
            st.success("Reset done")

    st.divider()
    st.subheader("Preview (non editable part + custom prompt)")
    st.code(FIXED_PREFIX + edited.strip(), language="text")