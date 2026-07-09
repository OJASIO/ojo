# Implementation Guide — RAG Project Improvements

## Files Delivered

| File | What it does | Replaces / New |
|---|---|---|
| `evaluator_agent.py` | LLM-as-judge with 4 criteria | Replaces empty file |
| `preprocessor_agent.py` | Bilingual EN+DE spaCy | Replaces English-only version |
| `retriever_agent_multilingual.py` | multilingual-e5-large embeddings | Replaces all-MiniLM-L6-v2 |
| `german_news_ingestion.py` | Free German news RSS + PDF dedup fix | New file |
| `streamlit_app.py` | Full demo UI | New file |

---

## Step 1 — Copy Files Into Your Project

```bash
# Copy improved agents
cp evaluator_agent.py your_project/src/agents/evaluator_agent.py
cp preprocessor_agent.py your_project/src/agents/preprocessor_agent.py
cp retriever_agent_multilingual.py your_project/src/agents/retriever_agent.py
cp german_news_ingestion.py your_project/src/agents/german_news_ingestion.py
cp streamlit_app.py your_project/streamlit_app.py
```

---

## Step 2 — Install New Dependencies

```bash
pip install feedparser beautifulsoup4 langdetect
python -m spacy download de_core_news_sm
python -m spacy download en_core_web_sm
```

---

## Step 3 — IMPORTANT: Re-index Pinecone

Because you changed the embedding model from all-MiniLM-L6-v2 (384 dim)
to multilingual-e5-large (1024 dim), your existing Pinecone index
has the WRONG dimension. You must delete it and re-index.

```python
# Run this ONCE to delete the old index
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pc.delete_index("your-index-name")  # replace with your index name
print("Old index deleted. Re-run your ingestion pipeline.")
```

Then re-run your run_task_1.py and run_task_3.py to re-index
all documents with the new multilingual model.

---

## Step 4 — Fix Duplicate PDFs

In your run_task_1.py, add deduplication:

```python
from agents.german_news_ingestion import deduplicate_pdfs
import glob

# Before processing:
pdf_paths = glob.glob("Data/*.pdf")
pdf_paths = deduplicate_pdfs(pdf_paths)  # Add this line
```

---

## Step 5 — Add German News

```python
from agents.german_news_ingestion import GermanNewsIngestionAgent

# Fetch German news
news_agent = GermanNewsIngestionAgent(max_articles_per_feed=20)
news_chunks = news_agent.run()

# Add to your existing PDF chunks before indexing
all_chunks = pdf_chunks + news_chunks
retriever.index_documents(all_chunks)
```

---

## Step 6 — Run the Streamlit UI

```bash
streamlit run streamlit_app.py
```

Access at: http://localhost:8501

---

## Step 7 — Deploy for Free (Hugging Face Spaces)

1. Create account at huggingface.co
2. Create new Space — select Streamlit
3. Upload your project files
4. Add secrets (PINECONE_API_KEY etc.) in Space settings
5. Your live demo URL: https://huggingface.co/spaces/YOUR_NAME/policy-rag

Put this URL in your CV and LinkedIn.

---

## Updated requirements.txt

```
# Core
pdfplumber
langchain
langchain-core
spacy
langdetect

# Embeddings — multilingual
sentence-transformers>=2.6.0

# Vector DB
pinecone
pinecone-text
rank-bm25

# LLM
ollama

# Planning
google-genai
pydantic

# Verification
transformers
torch

# Evaluation (new)
# EvaluatorAgent uses same Ollama — no new deps

# German news (new)
feedparser
beautifulsoup4

# Graph
networkx

# UI (new)
streamlit
plotly

# Utils
numpy
matplotlib
scipy
scikit-learn
python-dotenv
```

---

## What to Say in Interviews About These Improvements

**On the EvaluatorAgent:**
"I implemented LLM-as-judge evaluation with four criteria — faithfulness,
relevancy, context precision, and completeness — each scored 1-5 by Mistral-7B
using structured JSON prompts. The overall score and verdict are stored in
evaluation history, enabling aggregate metrics across all pipeline runs."

**On multilingual support:**
"I upgraded from all-MiniLM-L6-v2 to multilingual-e5-large, which maps English
and German text into the same 1024-dimensional vector space. This enables
cross-lingual retrieval — a German query can surface relevant English policy
documents and vice versa. The model requires explicit 'query:' and 'passage:'
prefixes which I implemented in the encode methods."

**On German news:**
"I integrated German RSS feeds from Tagesschau and Deutsche Welle using feedparser,
with HTML stripping via BeautifulSoup and content-hash based deduplication.
The output format matches the existing PDF chunk schema exactly, so the same
preprocessor and retriever handle both source types without modification."

**On the Streamlit UI:**
"The demo is deployed publicly on Hugging Face Spaces. It shows the full pipeline
execution step by step, retrieval sources with language tags and relevance scores,
LLM-as-judge scores as a visual dashboard, and NLI verification results with
entailment rate. Anyone can query it live during an interview."
