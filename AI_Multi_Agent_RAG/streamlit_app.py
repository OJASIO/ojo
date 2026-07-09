# streamlit_app.py
# Run: python -m streamlit run streamlit_app.py

import streamlit as st
import time
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agents.retriever_agent import RetrieverAgent
from agents.summarizer_agent import SummarizerAgent
from agents.planner_agent import PlannerAgent
from agents.verifier_agent import VerifierAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.guardrails_agent import GuardrailsAgent

st.set_page_config(
    page_title="Policy Research Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: #FAFAF8;
    }
    [data-testid="stSidebar"] {
        background: #F4F2EE;
        border-right: 1px solid #E5E3DC;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 860px;
    }
    h1, h2, h3 {
        font-weight: 500;
        letter-spacing: -0.02em;
    }
    .page-title {
        font-size: 1.6rem;
        font-weight: 500;
        color: #1a1a18;
        letter-spacing: -0.03em;
        margin-bottom: 0.2rem;
    }
    .page-subtitle {
        font-size: 0.9rem;
        color: #888880;
        margin-bottom: 2rem;
    }
    .step-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #F0EEE8;
        font-size: 0.85rem;
        color: #888880;
    }
    .step-row.done {
        color: #3a3a38;
    }
    .step-row.active {
        color: #1a1a18;
        font-weight: 500;
    }
    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #D5D3CC;
        flex-shrink: 0;
    }
    .step-dot.done {
        background: #5C8A5C;
    }
    .step-dot.active {
        background: #1a1a18;
    }
    .answer-block {
        background: #FFFFFF;
        border: 1px solid #E5E3DC;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        line-height: 1.7;
        font-size: 0.95rem;
        color: #2a2a28;
    }
    .source-item {
        display: flex;
        align-items: baseline;
        gap: 8px;
        padding: 8px 0;
        border-bottom: 1px solid #F0EEE8;
        font-size: 0.83rem;
        color: #555550;
    }
    .source-num {
        color: #AAAAAA;
        font-size: 0.75rem;
        min-width: 18px;
    }
    .source-lang {
        font-size: 0.7rem;
        padding: 1px 6px;
        border-radius: 3px;
        background: #EEF0F5;
        color: #4A5070;
        font-weight: 500;
    }
    .score-card {
        background: #FFFFFF;
        border: 1px solid #E5E3DC;
        border-radius: 6px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .score-label {
        font-size: 0.72rem;
        color: #AAAAAA;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .score-value {
        font-size: 1.6rem;
        font-weight: 500;
        letter-spacing: -0.03em;
    }
    .score-note {
        font-size: 0.72rem;
        color: #888880;
        margin-top: 4px;
        line-height: 1.4;
    }
    .verdict-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.03em;
    }
    .verdict-EXCELLENT { background: #EAF3DE; color: #3B6D11; }
    .verdict-GOOD { background: #E6F1FB; color: #185FA5; }
    .verdict-ACCEPTABLE { background: #FAEEDA; color: #854F0B; }
    .verdict-POOR { background: #FCEBEB; color: #A32D2D; }
    .verdict-FAILED { background: #FCEBEB; color: #A32D2D; }
    .meta-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.78rem;
        color: #888880;
        padding: 4px 10px;
        background: #F4F2EE;
        border-radius: 20px;
    }
    .sidebar-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #AAAAAA;
        margin-bottom: 6px;
        margin-top: 16px;
    }
    .stButton > button {
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 400;
        border: 1px solid #D5D3CC;
        background: #FFFFFF;
        color: #2a2a28;
        transition: all 0.15s;
    }
    .stButton > button:hover {
        border-color: #AAAAAA;
        background: #F8F7F4;
    }
    div[data-testid="stTextArea"] textarea {
        border-radius: 6px;
        border: 1px solid #D5D3CC;
        background: #FFFFFF;
        font-size: 0.9rem;
        color: #1a1a18;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #AAAAAA;
        box-shadow: none;
    }
    .stSelectbox > div {
        font-size: 0.85rem;
    }
    [data-testid="stExpander"] {
        border: 1px solid #E5E3DC;
        border-radius: 6px;
        background: #FFFFFF;
    }
    .verification-row {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        padding: 7px 0;
        border-bottom: 1px solid #F0EEE8;
        font-size: 0.83rem;
        color: #555550;
        line-height: 1.5;
    }
    .v-badge {
        font-size: 0.68rem;
        font-weight: 500;
        padding: 2px 7px;
        border-radius: 3px;
        white-space: nowrap;
        margin-top: 2px;
    }
    .v-entailed { background: #EAF3DE; color: #3B6D11; }
    .v-neutral { background: #FAEEDA; color: #854F0B; }
    .v-contradiction { background: #FCEBEB; color: #A32D2D; }
    .divider { border: none; border-top: 1px solid #E5E3DC; margin: 1.5rem 0; }
    .section-heading {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #AAAAAA;
        margin: 1.5rem 0 0.8rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_agents():
    try:
        retriever = RetrieverAgent(
            index_name="policy-rag-index",
            dimension=1024,
            sbert_model="intfloat/multilingual-e5-large"
        )
        classical_output_path = "results/classical_output.json"
        if os.path.exists(classical_output_path):
            with open(classical_output_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            corpus = [c.get("content", "") for c in chunks if c.get("content")]
            retriever.fit_sparse_encoder(corpus)
        return {
            "retriever": retriever,
            "summarizer": SummarizerAgent(),
            "planner": PlannerAgent(),
            "verifier": VerifierAgent(),
            "evaluator": EvaluatorAgent(),
            "guardrails": GuardrailsAgent(),
            "loaded": True
        }
    except Exception as e:
        return {"loaded": False, "error": str(e)}


with st.sidebar:
    st.markdown('<div class="sidebar-label">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("", ["English", "Deutsch"], label_visibility="collapsed")
    lang_code = "en" if language == "English" else "de"

    st.markdown('<div class="sidebar-label">Retrieval balance</div>', unsafe_allow_html=True)
    alpha = st.slider(
        "", 0.0, 1.0, 0.5, 0.1,
        help="Left = keyword matching, right = meaning matching",
        label_visibility="collapsed"
    )
    st.markdown(
        f'<div style="font-size:0.75rem; color:#AAAAAA; margin-top:-8px;">'
        f'{"More keyword" if alpha < 0.4 else "More semantic" if alpha > 0.6 else "Balanced"}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-label">Results</div>', unsafe_allow_html=True)
    k = st.slider("", 3, 10, 5, label_visibility="collapsed")

    st.markdown('<div class="sidebar-label">Show</div>', unsafe_allow_html=True)
    show_evaluation = st.checkbox("Quality scores", value=True)
    show_verification = st.checkbox("Source verification", value=True)
    show_pipeline = st.checkbox("Processing steps", value=False)

    st.markdown('<hr style="border:none;border-top:1px solid #E5E3DC;margin:1.5rem 0">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Sources</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.8rem; color:#888880; line-height:1.8;">
        OECD policy documents<br>
        IMF reports<br>
        UN policy briefs<br>
        Bundesbank annual reports<br>
        KfW financial reports<br>
        Tagesschau news<br>
        Deutsche Welle
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label" style="margin-top:1.5rem">Built with</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.78rem; color:#AAAAAA; line-height:1.8;">
        Mistral-7B &middot; multilingual-e5-large<br>
        Pinecone &middot; BM25 hybrid retrieval<br>
        facebook/bart-large-mnli<br>
        Gemini 2.5 Flash &middot; Ollama
    </div>
    """, unsafe_allow_html=True)


st.markdown('<p class="page-title">Policy research assistant</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Ask questions across OECD, IMF, UN, Bundesbank, and KfW documents '
    '&mdash; in English or German.</p>',
    unsafe_allow_html=True
)

examples = {
    "en": [
        "How does the IMF approach climate finance in developing nations?",
        "What are OECD recommendations on digital taxation?",
        "How do international organisations handle AI governance?",
        "What supports the green transition in emerging economies?"
    ],
    "de": [
        "Wie bewertet die Bundesbank die Inflationsentwicklung?",
        "Welche Maßnahmen empfiehlt die KfW zur Klimafinanzierung?",
        "Wie reguliert die EU künstliche Intelligenz?",
        "Was sind die Empfehlungen zur digitalen Transformation?"
    ]
}

cols = st.columns(2)
for i, ex in enumerate(examples[lang_code]):
    if cols[i % 2].button(ex, key=f"ex_{lang_code}_{i}", use_container_width=True):
        st.session_state.query_input = ex

st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

query = st.text_area(
    "Your question",
    value=st.session_state.get("query_input", ""),
    height=72,
    placeholder="Type a question in English or German...",
    label_visibility="collapsed"
)

c1, c2 = st.columns([5, 1])
search_clicked = c1.button("Search", type="primary", use_container_width=True)
if c2.button("Clear", use_container_width=True):
    st.session_state.query_input = ""
    st.rerun()

if search_clicked and query.strip():
    agents = load_agents()

    if not agents["loaded"]:
        st.error(f"Could not load the pipeline: {agents.get('error', 'unknown error')}")
        st.info("Make sure Ollama is running and your API keys are set in .env")
        st.stop()

    start_time = time.time()

    if show_pipeline:
        st.markdown('<p class="section-heading">Processing</p>', unsafe_allow_html=True)
        step_container = st.empty()

    def render_steps(steps):
        if not show_pipeline:
            return
        html = ""
        for name, status in steps.items():
            dot_class = "done" if status == "done" else "active" if status == "running" else ""
            row_class = dot_class
            html += f'<div class="step-row {row_class}"><div class="step-dot {dot_class}"></div>{name}</div>'
        step_container.markdown(html, unsafe_allow_html=True)

    steps = {
        "Checking query safety": "pending",
        "Planning and decomposing": "pending",
        "Retrieving relevant passages": "pending",
        "Drafting answer": "pending",
        "Verifying against sources": "pending",
        "Scoring answer quality": "pending"
    }

    try:
        steps["Checking query safety"] = "running"
        render_steps(steps)
        guardrail_result = agents["guardrails"].process_guardrails(query, "")
        if guardrail_result.get("injection_detected"):
            st.warning("This query was flagged as potentially unsafe and was not processed.")
            st.stop()
        steps["Checking query safety"] = "done"

        steps["Planning and decomposing"] = "running"
        render_steps(steps)
        plan = agents["planner"].route_and_plan(query)
        steps["Planning and decomposing"] = "done"

        steps["Retrieving relevant passages"] = "running"
        render_steps(steps)
        retrieved_docs = agents["retriever"].hybrid_search(query=query, alpha=alpha, k=k)
        context_texts = [doc.page_content for doc in retrieved_docs]
        steps["Retrieving relevant passages"] = "done"

        steps["Drafting answer"] = "running"
        render_steps(steps)
        context_map = {}
        for doc in retrieved_docs:
            key = f"[{doc.metadata['source']} p.{doc.metadata['page']}]"
            context_map[key] = doc.page_content

        plan_for_summarizer = {
            "original_query": plan.get("original_query", query),
            "detected_language": plan.get("detected_language", "en"),
            "sub_queries": {q: [] for q in plan.get("sub_queries", [query])}
        }
        answer = agents["summarizer"].synthesize_summary(plan_for_summarizer, [
            {"text": doc.page_content, "source": doc.metadata["source"], "page": doc.metadata["page"]}
            for doc in retrieved_docs
        ])
        steps["Drafting answer"] = "done"

        steps["Verifying against sources"] = "running"
        render_steps(steps)
        verification_results = []
        if show_verification:
            verification_results = agents["verifier"].run_verification(answer, context_map)
        steps["Verifying against sources"] = "done"

        steps["Scoring answer quality"] = "running"
        render_steps(steps)
        evaluation = None
        if show_evaluation:
            evaluation = agents["evaluator"].evaluate(
                question=query, answer=answer,
                retrieved_contexts=context_texts, language=lang_code
            )
        steps["Scoring answer quality"] = "done"
        render_steps(steps)

        elapsed = time.time() - start_time

        st.markdown('<p class="section-heading">Answer</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer-block">{answer}</div>', unsafe_allow_html=True)

        meta_html = (
            f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin:0.5rem 0 1rem 0;">'
            f'<span class="meta-chip">{elapsed:.0f}s</span>'
            f'<span class="meta-chip">{len(retrieved_docs)} passages</span>'
            f'<span class="meta-chip">alpha {alpha:.1f}</span>'
            f'</div>'
        )
        st.markdown(meta_html, unsafe_allow_html=True)

        st.markdown('<p class="section-heading">Sources</p>', unsafe_allow_html=True)
        sources_html = ""
        for i, doc in enumerate(retrieved_docs):
            lang_tag = doc.metadata.get("language", "en")
            score = doc.metadata.get("score", 0)
            sources_html += (
                f'<div class="source-item">'
                f'<span class="source-num">{i+1}</span>'
                f'<span class="source-lang">{"DE" if lang_tag == "de" else "EN"}</span>'
                f'<span>{doc.metadata["source"]}, p.{doc.metadata["page"]}'
                f' &nbsp;<span style="color:#CCCCCC">&middot;</span>&nbsp; '
                f'score {score:.2f}</span>'
                f'</div>'
            )
        st.markdown(sources_html, unsafe_allow_html=True)

        with st.expander("Read passages", expanded=False):
            for i, doc in enumerate(retrieved_docs):
                st.markdown(
                    f"**{i+1}. {doc.metadata['source']} p.{doc.metadata['page']}**\n\n"
                    + (doc.page_content[:350] + "..." if len(doc.page_content) > 350 else doc.page_content)
                )
                if i < len(retrieved_docs) - 1:
                    st.markdown("---")

        if show_evaluation and evaluation:
            st.markdown('<p class="section-heading">Answer quality</p>', unsafe_allow_html=True)
            scores = evaluation.get("scores", {})
            reasoning = evaluation.get("reasoning", {})
            verdict = evaluation.get("verdict", "")
            overall = evaluation.get("overall_score", 0)

            verdict_html = f'<span class="verdict-pill verdict-{verdict}">{verdict}</span>'
            st.markdown(
                f'<div style="margin-bottom:1rem;">'
                f'{verdict_html}'
                f'<span style="font-size:0.85rem;color:#888880;margin-left:8px;">'
                f'Overall {overall}/5</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            criteria = [
                ("faithfulness", "Faithfulness"),
                ("relevancy", "Relevancy"),
                ("context_precision", "Precision"),
                ("completeness", "Completeness")
            ]
            cols_eval = st.columns(4)
            for (key, label), col in zip(criteria, cols_eval):
                score = scores.get(key, 0)
                note = reasoning.get(key, "")
                color = "#3B6D11" if score >= 4 else "#854F0B" if score >= 3 else "#A32D2D"
                col.markdown(
                    f'<div class="score-card">'
                    f'<div class="score-label">{label}</div>'
                    f'<div class="score-value" style="color:{color}">{score}/5</div>'
                    f'<div class="score-note">{note[:60] + "..." if len(note) > 60 else note}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        if show_verification and verification_results:
            st.markdown('<p class="section-heading">Source verification</p>', unsafe_allow_html=True)
            entailed = sum(1 for r in verification_results if r.get("factual_precision") == "FACTUAL_ENTAILED")
            total = len(verification_results)
            st.markdown(
                f'<div style="font-size:0.83rem;color:#888880;margin-bottom:0.5rem;">'
                f'{entailed} of {total} statements verified against source documents</div>',
                unsafe_allow_html=True
            )
            v_html = ""
            for r in verification_results[:6]:
                status = r.get("factual_precision", "")
                if "ENTAILED" in status:
                    badge = '<span class="v-badge v-entailed">verified</span>'
                elif "NEUTRAL" in status:
                    badge = '<span class="v-badge v-neutral">uncertain</span>'
                else:
                    badge = '<span class="v-badge v-contradiction">flagged</span>'
                stmt = r.get("statement", "")[:120]
                v_html += f'<div class="verification-row">{badge}<span>{stmt}{"..." if len(r.get("statement","")) > 120 else ""}</span></div>'
            st.markdown(v_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.exception(e)

elif search_clicked and not query.strip():
    st.warning("Enter a question to search.")

st.markdown("""
<div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid #E5E3DC;
font-size:0.75rem;color:#CCCCCA;text-align:center;">
    MSc Applied Data Science &middot; SRH Hochschule Heidelberg
</div>
""", unsafe_allow_html=True)
