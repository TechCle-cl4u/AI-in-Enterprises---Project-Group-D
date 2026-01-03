import streamlit as st
from file_uploader import upload_pdfs
from vectorizer import vectorize_documents
from qa_system import compare_cvs_job_description
from job_description_optimizer import optimize_job_description
import time
import os
import pandas as pd
import streamlit.components.v1 as components



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




#============Main Page (CV Upload and insertion Job Description)==============
if page == "Main":
    
    #======Selection of model used - ensure model is running======
    llm_model = st.sidebar.selectbox(
        'Choose model:',
        ('gemma3:12b', 'gemma3:4b', 'ministral-3:8b', 'ministral-3:14b'),
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
                
                    
                    
                
                
                   # Log the data for later analysis
                    log_entry = {
                       "Job Description": job_description,
                       "Recommendation": recommendation,
                       "Document Size (bytes)": document_size,
                       "Analysis Time (seconds)": analysis_time,
                       "LLM Model": llm_model
                   }
                
                   # Save the log entry to a CSV file or dataframe
                    if os.path.exists('log_file_cv_screening.csv'):
                       log_df = pd.read_csv('log_file_cv_screening.csv')
                    else:
                       log_df = pd.DataFrame(columns=["Job Description", "Document Size (bytes)", "Analysis Time (seconds)", "LLM Model", "Feedback"])
                
                   # Use pd.concat to add the new log entry
                    log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
                
                   # Save the updated log to the CSV file
                    log_df.to_csv('log_file_cv_screening.csv', index=False)
                    st.success("Log entry saved!")
                
            











#------------ Log File Analysis Page (for viewing logs) ------------
elif page == "Log File Analysis":
    st.title("Log File Analysis")
    
    # Display logs if available
    if os.path.exists('log_file_cv_screening.csv'):
        log_df = pd.read_csv('log_file_cv_screening.csv')
        st.write("Previous log entries:")
        st.dataframe(log_df)
    else:
        st.write("No logs available yet. Perform some analysis on the 'Main' page to generate logs.")
        
elif page == "Prompt Settings:":
    st.title("Prompt Settings")
