# src/agents/pdf_ingestion_agent.py
import os
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any

class PDFIngestionAgent:
    """Parses PDFs, extracts content using pdfplumber, and chunks the content semantically."""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # Initializing the text splitter remains the same, using the new import path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def _extract_text_and_metadata(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extracts text content and basic metadata (source, page) from a single PDF using pdfplumber."""
        extracted_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        extracted_data.append({
                            "page_content": text,
                            "metadata": {
                                "source": os.path.basename(pdf_path),
                                "page": i  # pdfplumber uses 0-based index for pages
                            }
                        })
            return extracted_data
        except Exception as e:
            print(f"Error extracting text from {pdf_path} using pdfplumber: {e}")
            return []

    def process_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """Loads and chunks multiple PDFs."""
        all_final_chunks = []
        
        # 1. Load and Concatenate Text (The replacement for loader.load())
        all_documents = []
        for path in pdf_paths:
            print(f"Extracting text from: {path}")
            # Use the new helper method to get page-level content and metadata
            page_data = self._extract_text_and_metadata(path)
            all_documents.extend(page_data)

        # 2. Chunk Semantically (The replacement for split_documents())
        # We need to adapt the standard split_text method to handle our new structure.
        
        for doc in all_documents:
            # Split the raw text from the page
            # This returns a List[str] containing the split text chunks
            text_chunks = self.text_splitter.split_text(doc["page_content"])
            
            # Format the chunks and attach metadata
            for chunk_content in text_chunks:
                # Create a new, clean copy of the original page metadata for each chunk
                chunk_metadata = doc["metadata"].copy()
                
                all_final_chunks.append({
                    "content": chunk_content,
                    "metadata": chunk_metadata
                })

        print(f"Finished chunking. Total chunks generated: {len(all_final_chunks)}")
        return all_final_chunks