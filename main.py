from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import PyPDF2
import faiss
import numpy as np
import re
from typing import List
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Load text generation model and sentence embedding model
gen_model = pipeline("text2text-generation", model="google/flan-t5-base", max_length=256)
embed_model = SentenceTransformer('all-MiniLM-L6-v2')  # small and fast

# In-memory store
class NotesStore:
    chunks: List[str] = []
    embeddings: np.ndarray = None
    index: faiss.IndexFlatL2 = None

store = NotesStore()

# Pydantic input model
class Question(BaseModel):
    question: str

# Extract text
def extract_text(file: UploadFile) -> str:
    if file.filename.endswith(".txt"):
        return file.file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    else:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files supported.")

# Split into clean chunks
def chunk_text(text, chunk_size=200):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk.split()) + len(sentence.split()) < chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

@app.post("/upload")
async def upload_notes(file: UploadFile = File(...)):
    try:
        text = extract_text(file)
        chunks = chunk_text(text)
        embeddings = embed_model.encode(chunks, convert_to_numpy=True)
        
        # Create FAISS index
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        
        # Store in memory
        store.chunks = chunks
        store.embeddings = embeddings
        store.index = index

        return {"message": f"Uploaded and indexed {len(chunks)} chunks successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(query: Question):
    if store.index is None:
        raise HTTPException(status_code=400, detail="No notes uploaded yet.")

    try:
        # Embed question
        q_embedding = embed_model.encode([query.question])
        D, I = store.index.search(np.array(q_embedding), k=3)
        
        # Get top chunks
        relevant_chunks = [store.chunks[i] for i in I[0] if i < len(store.chunks)]
        context = " ".join(relevant_chunks)

        # Use FLAN-T5 for answer generation
        prompt = f"Answer the question based on the following notes:\n\n{context}\n\nQuestion: {query.question}"
        result = gen_model(prompt)[0]["generated_text"]

        return {"answer": result.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#to ask questions from text not as file    
@app.post("/ingest-text")
async def ingest_text(payload: dict):
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided.")

    try:
        chunks = chunk_text(text)
        embeddings = embed_model.encode(chunks, convert_to_numpy=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        store.chunks = chunks
        store.embeddings = embeddings
        store.index = index

        return {"message": f"Ingested and indexed {len(chunks)} text chunks successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

