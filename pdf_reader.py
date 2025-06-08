# pdf_reader.py

import PyPDF2
import io
import re
from docx import Document

class PDFProcessError(Exception):
    """Custom exception for PDF processing errors"""
    pass

def sanitize_text(text):
    """
    Basic PDF text sanitization:
    - Remove lines that are just numbers (page numbers)
    - Remove lines like 'Page X' or 'Page X of Y'
    - Remove repeated headers/footers (if any)
    - Remove blank lines and excessive whitespace
    - Optionally join lines that are likely part of the same sentence
    """
    lines = text.splitlines()
    cleaned_lines = []
    header_footer_candidates = {}
    for line in lines:
        l = line.strip()
        # Remove blank lines
        if not l:
            continue
        # Remove lines that are just numbers (page numbers)
        if re.fullmatch(r"\d+", l):
            continue
        # Remove lines like 'Page X' or 'Page X of Y'
        if re.match(r"^Page \d+( of \d+)?$", l, re.IGNORECASE):
            continue
        # Track repeated lines (possible header/footer)
        header_footer_candidates[l] = header_footer_candidates.get(l, 0) + 1
        cleaned_lines.append(l)
    # Remove lines that repeat too often (likely header/footer)
    threshold = max(2, len(lines) // 10)  # If a line appears on >10% of pages, treat as header/footer
    filtered_lines = [l for l in cleaned_lines if header_footer_candidates[l] <= threshold]
    # Remove excessive whitespace and join lines
    filtered_text = "\n".join(filtered_lines)
    filtered_text = re.sub(r"[ \t]+", " ", filtered_text)  # Collapse spaces
    filtered_text = re.sub(r"\n{2,}", "\n", filtered_text)  # Collapse multiple blank lines
    return filtered_text

def extract_docx_text(file):
    """
    Extract text from a .docx file.
    """
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        # Sanitize text (reuse PDF sanitization)
        return sanitize_text(text)
    except Exception as e:
        raise PDFProcessError(f"Error reading DOCX: {str(e)}")

def extract_text_from_file(file):
    """
    Extract text from a PDF or DOCX file, with error handling.
    """
    if hasattr(file, 'name') and file.name.lower().endswith('.docx'):
        return extract_docx_text(file)
    else:
        # Default to PDF extraction
        try:
            # Check if file is empty
            file_content = file.read()
            if len(file_content) == 0:
                raise PDFProcessError("The uploaded file is empty.")
            
            # Reset file pointer and try to read as PDF
            file.seek(0)
            pdf = PyPDF2.PdfReader(file)
            
            # Check if PDF has pages
            if len(pdf.pages) == 0:
                raise PDFProcessError("The PDF file contains no pages.")
                
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
            # Check if any text was extracted
            if not text.strip():
                raise PDFProcessError("No readable text found in the PDF. The file might be scanned images or corrupted.")
            
            # Sanitize text before returning
            text = sanitize_text(text)
            return text
            
        except PyPDF2.PdfReadError as e:
            raise PDFProcessError(f"Error reading PDF: The file might be corrupted or password protected. Details: {str(e)}")
        except Exception as e:
            raise PDFProcessError(f"Unexpected error processing PDF: {str(e)}")

def extract_text_from_files(files):
    """
    Extract and combine text from multiple PDF/DOCX files.
    Adds a separator after each file's content for clarity.
    Returns a single combined string.
    """
    combined_texts = []
    for file in files:
        # Get filename for separator (handle both UploadedFile and file-like objects)
        filename = getattr(file, 'name', 'UnknownFile')
        try:
            text = extract_text_from_file(file)
        except PDFProcessError as e:
            text = f"[Error extracting {filename}: {str(e)}]"
        combined_texts.append(text)
        combined_texts.append(f"\n--- End of File: {filename} ---\n")
    return "\n\n".join(combined_texts)
