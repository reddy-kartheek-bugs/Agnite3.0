# FinTech Compliance & Payment Workflow RAG Assistant 🏦💳

A Retrieval-Augmented Generation (RAG) assistant built specifically for the Financial Technology (FinTech) domain. The app helps summarize and query complex FinTech compliance processes and payment workflows using LangChain, Google Gemini API, and FAISS vector database.

## Features ✨

- **Intelligent RAG**: Powered by LangChain, a FAISS local vector database, and Google Generative AI (Gemini Flash).
- **API Key Rotation**: Automatically rotates through multiple Google API Keys to handle API quota limits via `ResourceExhausted` safe fallback.
- **Strict Compliance Guardrails**: Validates user inputs and ensures queries on topics like "bypassing KYC" or "money laundering" are explicitly blocked before processing.
- **Structured Answers**: Uses system prompts to return structured, precise, and concise answers, formatted with headings and bullet points based purely on provided context.
- **Source Tracing**: Identifies and links the exact source chunks (with page numbers) used for every generated answer.

## Tech Stack 🛠️

- **Frontend**: Streamlit
- **LLM/Embeddings**: Google Gemini (`gemini-2.5-flash` for generation, `gemini-embedding-001` for vector embeddings)
- **Vector Database**: FAISS (in-memory & local-filesystem persistence via CPU)
- **Orchestration**: LangChain, PyPDFLoader

## Setup Instructions 🚀

### 1. Requirements

Ensure you have Python 3.9+ installed.

```bash
git clone <your-repo>
cd system-directory
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create a `.env` file in the root directory and add your Google Gemini API keys. (The system supports rotating through up to 3 keys).

```env
GOOGLE_API_KEY_1=your_first_gemini_api_key_here
GOOGLE_API_KEY_2=your_second_gemini_api_key_here
GOOGLE_API_KEY_3=your_third_gemini_api_key_here
```

### 4. Provide the Knowledge Base

Ensure you have a PDF file named `fintech_master.pdf` outlining your FinTech documents, workflows, and compliance processes.

Place this file into the `data/` directory:

```bash
mkdir -p data
# Copy your document into the directory
cp /path/to/your/fintech_master.pdf data/fintech_master.pdf
```

### 5. Run the Application

Start the Streamlit development server:

```bash
streamlit run app.py
```

The app will become available at `http://localhost:8501`.

_Note: On the first successful query, the app will automatically ingest your `fintech_master.pdf` into a FAISS index stored in `vectorstore/`. Subsequent queries will load the generated FAISS index directly._
