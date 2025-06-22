Medical Notes Assistant app is a Medical Notes Question Answering App that  allows users to upload medical notes (PDF or TXT), or paste text manually, and then ask questions based on those notes. It built using FastAPI for the backend and Streamlit for the frontend.


IMPORTS:

FastAPI, UploadFile, File, HTTPException — FastAPI tools for handling API endpoints and file uploads.

BaseModel — From pydantic, used to define input data schemas.

pipeline — From HuggingFace Transformers to load FLAN-T5 for text generation.

PyPDF2 — Used to extract text from PDFs.

faiss — Facebook's similarity search library to quickly find relevant chunks using vector embeddings.

re — For regex-based sentence splitting.

numpy — For numerical operations.

SentenceTransformer — From sentence-transformers, used for sentence embeddings.



Models Used:

gen_model: FLAN-T5 (google/flan-t5-base) is used for generating answers based on context + question.

embed_model: all-MiniLM-L6-v2 is a small and fast model to embed text into vectors for similarity search.




HOW TO RUN THE APP? 


Step 1: install python.


step 2: Clone the repository.


step 3: intall all the requirements.
    
    pip install -r requirements.txt


step 4: Start the FastAPI backend:
    in the terminal of the VScode run the command "uvicorn main:app --reload"

    this command initializes the backend(might take some time).

    you will get  an output like:
    
    Uvicorn running on http://127.0.0.1:8000
    This means your FastAPI backend is now live at http://127.0.0.1:8000 


    Once the terminal displays "INFO:     Application startup complete.". do the step two.


step 5: Start the Streamlit Frontend:
    open a new terminal and run the command "streamlit run ui.py"

    this command will automatically guide you to the app.


step 3:Use the App
    
    1. In the web UI:

    Choose either Upload PDF/TXT or Paste Text Manually.

    Upload your notes or paste them.

    wait for the success message.


    2. Then ask a question in the "❓ Ask a Question" section.

    Click Ask Question to get an answer.

    Your question and answer will appear below in the Q&A history.
