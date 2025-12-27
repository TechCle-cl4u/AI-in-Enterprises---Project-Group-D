import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def upload_pdfs(uploaded_files):
    pdf_paths = []
    all_docs = []
    
    for uploaded_file in uploaded_files:
        # Temporarily save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name
            pdf_paths.append(pdf_path)

        # Load PDF and split into documents
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        # Split into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Maximale Chunk-Größe
            chunk_overlap=50,  # Überlappung der Chunks
            separators=[".", "\n", " ", ","] )
        docs = text_splitter.split_documents(docs)

        # Add document name to the metadata of each chunk
        for doc in docs:
            doc.metadata["document_name"] = uploaded_file.name  # Ensure correct document name assignment

        all_docs.extend(docs)

    return pdf_paths, all_docs
