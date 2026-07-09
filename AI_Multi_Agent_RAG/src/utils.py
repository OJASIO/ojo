# src/utils.py
import json
from typing import List, Dict, Any
import os
import glob

def save_json(data: Any, filepath: str):
    """Saves data to a JSON file, creating directories if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Successfully saved output to {filepath}")

def load_pdf_paths(pdf_dir: str = 'D:/NLP_Final_Project/Examination-master/Data') -> List[str]:
    """Finds all PDF files in the specified directory."""
    return glob.glob(os.path.join(pdf_dir, '*.pdf'))