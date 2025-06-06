# pdf_reader.py

import PyPDF2
import io

class PDFProcessError(Exception):
    """Custom exception for PDF processing errors"""
    pass

def extract_text_from_pdf(file):
    """
    Extract text from PDF with error handling for common issues.
    Raises PDFProcessError if the PDF is invalid, empty, or unreadable.
    """
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
            
        return text
        
    except PyPDF2.PdfReadError as e:
        raise PDFProcessError(f"Error reading PDF: The file might be corrupted or password protected. Details: {str(e)}")
    except Exception as e:
        raise PDFProcessError(f"Unexpected error processing PDF: {str(e)}")
