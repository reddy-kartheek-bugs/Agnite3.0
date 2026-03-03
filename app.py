import streamlit as st
import os
from rag_engine import create_vector_store, load_vector_store, generate_answer
from guardrails import is_forbidden
from prompts import SYSTEM_PROMPT

VECTOR_PATH = "vectorstore"
INDEX_FILE = os.path.join(VECTOR_PATH, "index.faiss")

st.set_page_config(page_title="FinTech Compliance AI", layout="wide")

st.title("💳 FinTech Compliance & Payment Workflow RAG Assistant")

# -----------------------------
# Safe Vector Store Handling
# -----------------------------

try:
    if not os.path.exists(INDEX_FILE):
        st.info("Creating vector database for the first time...")
        vectorstore = create_vector_store()
    else:
        vectorstore = load_vector_store()

except Exception as e:
    st.error(f"Vector store error: {e}")
    st.stop()

# -----------------------------
# Query Section
# -----------------------------

query = st.text_input("Ask your question:")

if query:
    if is_forbidden(query):
        st.error("⚠️ Query violates compliance policy. No response generated.")
        st.stop()

    with st.spinner("Generating response..."):
        answer, sources = generate_answer(query, vectorstore, SYSTEM_PROMPT)

    st.markdown("### 📘 Answer")
    st.write(answer)

    st.markdown("### 📚 Sources Used")
    for i, doc in enumerate(sources):
        page = doc.metadata.get("page", "N/A")
        st.write(f"Source {i+1} - Page {page}")