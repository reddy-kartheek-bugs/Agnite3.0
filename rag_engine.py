import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from config import GENERATION_CONFIG, SAFETY_SETTINGS

load_dotenv()

# ==============================
# 🔁 API KEY ROTATION SYSTEM
# ==============================

API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3"),
]

current_key_index = 0


def configure_gemini():
    global current_key_index

    if current_key_index >= len(API_KEYS):
        raise Exception("All API keys exhausted.")

    key = API_KEYS[current_key_index]
    genai.configure(api_key=key)
    print(f"Using API Key #{current_key_index + 1}")


def safe_embed(content, model_name):
    global current_key_index

    while current_key_index < len(API_KEYS):
        try:
            configure_gemini()
            return genai.embed_content(
                model=model_name,
                content=content
            )
        except ResourceExhausted:
            print(f"Embedding quota exhausted on Key #{current_key_index + 1}. Switching...")
            current_key_index += 1
            time.sleep(1)

    raise Exception("All API keys exhausted during embedding.")


def safe_generate(model_name, prompt):
    global current_key_index

    while current_key_index < len(API_KEYS):
        try:
            configure_gemini()
            model = genai.GenerativeModel(model_name)

            response = model.generate_content(
                prompt,
                generation_config=GENERATION_CONFIG,
                safety_settings=SAFETY_SETTINGS
            )
            return response

        except ResourceExhausted:
            print(f"Generation quota exhausted on Key #{current_key_index + 1}. Switching...")
            current_key_index += 1
            time.sleep(1)

    raise Exception("All API keys exhausted during generation.")


# ==============================
# Gemini Embedding Wrapper
# ==============================

VECTOR_PATH = "vectorstore"
INDEX_FILE = os.path.join(VECTOR_PATH, "index.faiss")


class GeminiEmbeddings(Embeddings):
    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            response = safe_embed(
                content=text,
                model_name="models/gemini-embedding-001"
            )
            embeddings.append(response["embedding"])
        return embeddings

    def embed_query(self, text):
        response = safe_embed(
            content=text,
            model_name="models/gemini-embedding-001"
        )
        return response["embedding"]


# ==============================
# Create Vector Store
# ==============================

def create_vector_store():
    print("Creating FAISS index...")

    loader = PyPDFLoader("data/fintech_master.pdf")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = splitter.split_documents(documents)

    embeddings = GeminiEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_PATH, exist_ok=True)
    vectorstore.save_local(VECTOR_PATH)

    print("FAISS index created successfully.")
    return vectorstore


# ==============================
# Load Vector Store
# ==============================

def load_vector_store():
    embeddings = GeminiEmbeddings()

    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError("FAISS index not found.")

    return FAISS.load_local(
        VECTOR_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ==============================
# Generate Answer
# ==============================

def generate_answer(query, vectorstore, system_prompt):
    docs = vectorstore.similarity_search(query, k=5)

    context = "\n\n".join(
        [
            f"(Page {doc.metadata.get('page', 'N/A')})\n{doc.page_content}"
            for doc in docs
        ]
    )

    prompt = f"""
    {system_prompt}

    Retrieved Context:
    {context}

    User Question:
    {query}

    Generate a structured and precise answer.
    """

    response = safe_generate(
        model_name="gemini-2.5-flash",
        prompt=prompt
    )

    return response.text, docs