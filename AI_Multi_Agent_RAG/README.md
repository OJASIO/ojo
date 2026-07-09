# Policy Research Assistant

A question-answering system built over international policy documents from OECD, IMF, UN, Bundesbank, and KfW. Ask a question in English or German and get a cited, verified answer drawn from the actual source material — not generated from memory.


**Built as part of:** NLP Exam Evaluation at SRH Hochschule Heidelberg

---

## What it does

Policy documents are long, cross-referential, and spread across institutions. Finding a specific recommendation buried in an 800-page IMF report takes hours. This system makes the entire corpus searchable through natural language — in both English and German.

You type a question. The system finds the most relevant passages across all documents, drafts a structured answer with citations, checks each factual claim against the source material, and scores the answer on four quality dimensions. Every step is visible.

---

## Document coverage

| Institution | Documents | Language |
|---|---|---|
| OECD | Well-being report, AI strategy toolkit, policy briefs | English |
| IMF | Labour market analysis, fiscal policy reports | English |
| UN / UNCTAD | Health equity reports, trade development reports | English |
| Bundesbank | Annual reports 2023, 2024, 2025 | German |
| KfW | Financial reports 2023, 2024, 2025 | German |
| Tagesschau, Deutsche Welle, Zeit | Current news articles | German / English |

Total: 12,063 passages indexed across 17 source documents

---

## How a query moves through the system

```
Your question
      |
      v
Safety check
(scans for injection attempts, redacts personal data)
      |
      v
Query planning
(Gemini 2.5 Flash decomposes complex questions
 into sub-queries covering each angle)
      |
      v
Passage retrieval
(combines keyword matching and meaning-based search
 across the full bilingual document corpus)
      |
      v
Answer drafting
(Mistral-7B synthesises retrieved passages
 into a structured answer with source citations)
      |
      v
Factual verification
(each claim checked against source text
 using a natural language inference model)
      |
      v
Quality scoring
(a second model judges the answer on
 faithfulness, relevancy, precision, completeness)
      |
      v
Your answer — with citations, scores, and sources
```

14 components handle these steps, coordinated through a state-based workflow that routes between them based on what each step returns.

---

## Results

**Evaluation on live queries using LLM-as-judge methodology:**

| Dimension | Score | What it measures |
|---|---|---|
| Faithfulness | 5.0 / 5 | Are all claims grounded in the source documents? |
| Relevancy | 5.0 / 5 | Does the answer address what was actually asked? |
| Context precision | 5.0 / 5 | Were the right passages retrieved? |
| Completeness | 5.0 / 5 | Did the answer use all available relevant information? |

**Verification on sample run:** 4 of 4 factual statements confirmed as entailed by source documents using facebook/bart-large-mnli.

**Retrieval ablation** across alpha values 0.2 to 0.8 — the balance between keyword and semantic matching is tunable and logged per run. An adaptive memory component adjusts this parameter automatically based on verification scores from previous queries.

---

## Bilingual retrieval

The embedding model (intfloat/multilingual-e5-large) maps English and German text into the same vector space. This means:

- A question in English can surface a relevant passage from a German Bundesbank report
- A question in German can pull from English OECD documents
- The system responds in whichever language the question was asked

German text is preprocessed using a dedicated German spaCy pipeline (`de_core_news_sm`), and German news articles are fetched live from Tagesschau and Deutsche Welle via RSS.

---

## Technical components

**Retrieval**
Combines BM25 sparse retrieval (exact keyword matching) with dense semantic search via Pinecone. A tunable alpha parameter controls the balance between the two. The BM25 component handles precise terminology; the semantic component handles conceptual similarity. Both run over the same 12,063-chunk index.

**Preprocessing**
Each document is chunked with 200-token overlap. Language is detected per chunk (langdetect), and the appropriate spaCy model is applied for tokenisation, lemmatisation, POS tagging, and named entity recognition. Duplicate documents are removed by filename stem before ingestion.

**Query decomposition**
Complex multi-part questions are broken into independent sub-queries using Gemini 2.5 Flash with structured JSON output. A simple question routes directly to retrieval; a complex comparative question is decomposed first.

**Answer generation**
Mistral-7B via Ollama synthesises retrieved passages into a structured policy brief with inline citations in `[src: document.pdf, p.X]` format. Two debate agents argue opposing interpretations before a consensus draft is produced.

**Verification**
facebook/bart-large-mnli checks each factual statement in the answer against the retrieved source passages. Statements are labelled as entailed, neutral, or contradicted. This runs independently of the generation step.

**Evaluation**
A second Mistral-7B instance acts as an independent judge, scoring the answer on four criteria using structured prompts that force JSON output. Scores are stored in evaluation history for aggregate reporting across multiple runs.

**Memory and adaptation**
A memory component logs entailment rates, retrieval latency, and alpha values per run. If the entailment rate falls below a threshold, alpha is adjusted toward more semantic retrieval on the next run. Parameters are persisted to disk between sessions.

**GraphRAG**
An alternative retrieval mode builds a knowledge graph from entity co-occurrence across documents using NetworkX. Degree centrality identifies the most connected concepts. This handles queries that require connecting information across multiple sources.

---

## Running locally

**Requirements**
- Python 3.11
- Ollama with Mistral-7B pulled (`ollama pull mistral:7b`)
- Pinecone account (free tier sufficient)
- Gemini API key (free via Google AI Studio)

**Setup**

```bash
git clone https://github.com/your-username/your-repo-name
cd your-repo-name

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download de_core_news_sm
```

Copy `.env.example` to `.env` and fill in your keys:

```
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-east-1
GEMINI_API_KEY=your_key_here
```

**Build the index**

```bash
python run_task_1.py   # ingest and preprocess documents
python run_task_3.py   # embed and index into Pinecone
```

Note: `run_task_3.py` downloads multilingual-e5-large on first run (~2.2 GB). Subsequent runs use the local cache.

**Run remaining pipeline steps**

```bash
python run_task_2.py   # topic modelling and visualisations
python run_task_4.py   # query planning
python run_task_5.py   # answer generation and debate
python run_task_6.py   # verification and guardrails
python run_task_7.py   # memory and parameter adaptation
python run_task_8.py   # retrieval comparison
```

**Launch the interface**

```bash
python -m streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`

---

## Project layout

```
.
├── src/
│   └── agents/
│       ├── pdf_ingestion_agent.py       document parsing and chunking
│       ├── preprocessor_agent.py        bilingual NLP pipeline
│       ├── embedding_agent.py           sentence embedding
│       ├── retriever_agent.py           hybrid BM25 + semantic retrieval
│       ├── retriever_experiment_agent.py  GraphRAG via NetworkX
│       ├── planner_agent.py             query decomposition
│       ├── summarizer_agent.py          answer generation with citations
│       ├── debate_agent.py              dual-perspective synthesis
│       ├── verifier_agent.py            NLI-based factual verification
│       ├── guardrails_agent.py          input safety and PII redaction
│       ├── evaluator_agent.py           LLM-as-judge quality scoring
│       ├── memory_agent.py              run logging and parameter adaptation
│       ├── visualizer_agent.py          embeddings and graph visualisation
│       ├── topic_model_agent.py         NMF topic modelling
│       └── german_news_ingestion.py     live RSS news pipeline
├── run_task_1.py through run_task_8.py  pipeline execution scripts
├── streamlit_app.py                     web interface
├── results/                             outputs, plots, metrics
├── Data/                                source PDFs
├── requirements.txt
├── .env.example
└── README.md
```

---

## Stack

Python 3.11, LangChain, LangGraph, Pinecone, rank-bm25, sentence-transformers (multilingual-e5-large), Ollama (Mistral-7B), Google Gemini 2.5 Flash, spaCy (en + de), facebook/bart-large-mnli, NetworkX, Streamlit, feedparser, pdfplumber

---

## Contact

**Ojas Indulkar**  
MSc Applied Data Science and Analytics  
SRH Hochschule Heidelberg  
[your LinkedIn] · [your email]
