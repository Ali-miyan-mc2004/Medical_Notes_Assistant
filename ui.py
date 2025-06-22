import streamlit as st
import requests

if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

API_URL = "http://127.0.0.1:8000"



st.set_page_config(page_title="Medical Notes QA", layout="centered")
st.title("🩺 Medical Notes Assistant")

# Input Mode Switch
mode = st.radio("Choose Input Mode", ["📤 Upload PDF/TXT", "✍️ Paste Text Manually"])

if mode == "📤 Upload PDF/TXT":
    uploaded_file = st.file_uploader("Upload a file (.pdf or .txt)", type=["pdf", "txt"])
    if uploaded_file:
        st.info("Uploading file to backend...")
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        res = requests.post(f"{API_URL}/upload", files=files)
        if res.status_code == 200:
            st.success(res.json()["message"])
        else:
            st.error(f"Upload failed: {res.json().get('detail')}")
else:
    text_input = st.text_area("Paste your notes here")
    if st.button("Submit Text"):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            st.info("Sending text to backend...")
            res = requests.post(f"{API_URL}/ingest-text", json={"text": text_input})
            if res.status_code == 200:
                st.success(res.json()["message"])
            else:
                st.error(f"Ingest failed: {res.json().get('detail')}")

# Question Asking
st.header("❓ Ask a Question")
question = st.text_input("What would you like to know?")

if st.button("Ask Question"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        st.info("Getting answer...")
        res = requests.post(f"{API_URL}/ask", json={"question": question})
        if res.status_code == 200:
            answer = res.json()["answer"]
            st.success("Answer:")
            st.write(answer)
            # Save Q&A to session history
            st.session_state.qa_history.append({
                "question": question,
                "answer": answer
            })
        elif res.status_code == 400 and res.json().get("detail") == "No notes uploaded yet.":
            st.error("❌ Please upload a file or enter text before asking a question.")
        else:
            st.error(f"Error: {res.json().get('detail')}")

if st.session_state.qa_history:
    st.header("📜 Previous Questions & Answers")
    for i, qa in enumerate(reversed(st.session_state.qa_history), 1):
        st.markdown(f"**Q{i}: {qa['question']}**")
        st.markdown(f"🔹 {qa['answer']}")
        st.markdown("---")


if st.button("🧹 Clear History"):
    st.session_state.qa_history = []
    st.success("History cleared.")
