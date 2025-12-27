import streamlit as st
from file_uploader import upload_pdfs
from vectorizer import vectorize_documents
from qa_system import answer_question
import time
import os
import pandas as pd
import streamlit.components.v1 as components


#============ S T A R T ===================
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
#======================================================



#============ Set-up of user interface - include logos, headings, et cetera============ 
st.set_page_config(
    page_title="Ollama",
    page_icon="/Users/clemenslutz/Documents/FH Studium/1. Semester/AI in Enterprises/rag_pdf_chat_project/favicon.png")# Pfad zu Ihrer Favicon-Datei


#============ Page selection for navigation between 'Main' and 'Logs' pages =============
page = st.sidebar.selectbox("Choose a page:", ["Main", "Log File Analysis"])

#------------ Main Page (for PDF Upload and Question) ------------
if page == "Main":
    
    
    #st.image("https://upload.wikimedia.org/wikipedia/de/thumb/a/a2/Blum-gmbh.svg/2560px-Blum-gmbh.svg.png", width = 300)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/FH_Technikum_Wien_logo.svg/2560px-FH_Technikum_Wien_logo.svg.png", width = 300)
    st.title("Document Summary Tool")
    st.write("Upload one or more PDFs and ask questions about them.")
    
    llm_model = st.sidebar.selectbox(
        'Choose model:',
        ('gemma3:12b', 'gemma3:4b', 'ministral-3:8b', 'ministral-3:14b'),
        index=0  # gemma3:12b set as default
    )
    
    
    #============ Upload and store PDF ====================================================
    uploaded_files = st.file_uploader("Choose one or more PDF files", type=["pdf"], accept_multiple_files=True)
    
    
    #Check, if files are uploaded
    if uploaded_files:
        
        #Show user feedback - overview how many files have been uploaded
        st.success(f"{len(uploaded_files)} PDFs uploaded successfully!")
        
        
        #============ Index and vectorize documents =======================================
        #-Call function upload_pdfs from file_uploader.py
        #-Store documents, Split into chunks, index together with metadata (document names)
        #==================================================================================
        
        with st.spinner("Processing PDFs (Vectorization)"):
           

            pdf_paths, docs = upload_pdfs(uploaded_files)
    
            # Vectorization of index
            vectorstore = vectorize_documents(docs)
        
        
    
        #============ User question and response generation ===============================
        #When files uploaded and vectorized --> Ask user question on documents.
        #==================================================================================
    
        
        
        
        if llm_model:
            question = st.text_input("Ask a question about the Documents:")
        
        if question:
            
            start_time = time.time()  # Start timer for log entry
   
            with st.spinner("Analyzing documents..."):
               # Call function and pass question and vectorstore
               answer, sources = answer_question(question, vectorstore, llm_model)
        
            end_time = time.time()  # End timer for log entry
            analysis_time = end_time - start_time  # Calculate time analyzing
           
            # Calculation document size for log entry
            document_size = sum([len(file.getbuffer()) for file in uploaded_files])  # Get size from file buffer
        
            # Display generated answer and source documents
            st.subheader("Generated Answer:")
            st.write(answer)
        
            st.subheader("Source Documents:")
            for doc in sources:
                document_name = doc.get('document_name', 'Unknown Document')
                page = doc.get('page', '?')
                
                # Erstelle einen Expander mit dem Dokumentnamen und der Seite
                with st.expander(f"Document: **{document_name}** | Page **{page}**"):
                    # Zeige den Inhalt des Dokuments an, wenn der Expander geöffnet ist
                    st.write(doc['content'])
                
                st.markdown("---")

        
        
           # Log the data for later analysis
            log_entry = {
               "Question": question,
               "Document Size (bytes)": document_size,
               "Analysis Time (seconds)": analysis_time,
               "LLM Model": llm_model
           }
        
           # Save the log entry to a CSV file or dataframe
            if os.path.exists('log_file.csv'):
               log_df = pd.read_csv('log_file.csv')
            else:
               log_df = pd.DataFrame(columns=["Question", "Document Size (bytes)", "Analysis Time (seconds)", "LLM Model"])
        
           # Use pd.concat to add the new log entry
            log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        
           # Save the updated log to the CSV file
            log_df.to_csv('log_file.csv', index=False)
            st.success("Log entry saved!")
            
            

#------------ Log File Analysis Page (for viewing logs) ------------
elif page == "Log File Analysis":
    st.title("Log File Analysis")
    
    # Display logs if available
    if os.path.exists('log_file.csv'):
        log_df = pd.read_csv('log_file.csv')
        st.write("Previous log entries:")
        st.dataframe(log_df)
    else:
        st.write("No logs available yet. Perform some analysis on the 'Main' page to generate logs.")
