# run_task_1.py
import os
import re
from src.agents.pdf_ingestion_agent import PDFIngestionAgent
from src.agents.preprocessor_agent import PreprocessorAgent
from src.agents.german_news_ingestion import GermanNewsIngestionAgent
from src.utils import save_json, load_pdf_paths

PDF_DIR = 'D:/NLP_Final_Project/Examination-master/Data'
OUTPUT_FILE = 'D:/NLP_Final_Project/Examination-master/results/classical_output.json'

def run_task_1():
    print("--- Starting Task 1: PDF Ingestion & Pre-Processing ---")

    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 1. Get all PDF paths
    pdf_paths = load_pdf_paths(PDF_DIR)
    print(f"Found {len(pdf_paths)} PDF files")

    # 2. Deduplicate by filename stem
    seen_stems = set()
    unique_paths = []
    for path in pdf_paths:
        stem = re.sub(
            r'\s*\(\d+\)\s*$',
            '',
            os.path.splitext(os.path.basename(path))[0]
        )
        if stem not in seen_stems:
            seen_stems.add(stem)
            unique_paths.append(path)
        else:
            print(f"Skipping duplicate: {os.path.basename(path)}")

    pdf_paths = unique_paths
    print(f"After deduplication: {len(pdf_paths)} unique PDFs")

    if not pdf_paths:
        print(f"ERROR: No PDFs found in {PDF_DIR}.")
        return

    # 3. Ingest PDFs (English + German)
    ingestion_agent = PDFIngestionAgent(chunk_size=1000, chunk_overlap=200)
    pdf_chunks = ingestion_agent.process_pdfs(pdf_paths)
    print(f"PDF chunks: {len(pdf_chunks)}")

    # 4. Fetch German news and convert to chunks
    print("\nFetching German news from RSS feeds...")
    news_agent = GermanNewsIngestionAgent(max_articles_per_feed=20)
    news_chunks = news_agent.run()
    print(f"News chunks: {len(news_chunks)}")

    # 5. Combine ALL chunks
    all_chunks = pdf_chunks + news_chunks
    print(f"\nTotal combined chunks: {len(all_chunks)}")

    if not all_chunks:
        print("No content found. Stopping.")
        return

    # 6. Preprocess ALL chunks bilingually
    # PreprocessorAgent auto-detects EN vs DE per chunk
    preprocessor_agent = PreprocessorAgent()
    final_output = preprocessor_agent.process_chunks(all_chunks)

    # 7. Save
    save_json(final_output, OUTPUT_FILE)
    print("--- Task 1 Completed Successfully ---")

if __name__ == "__main__":
    run_task_1()