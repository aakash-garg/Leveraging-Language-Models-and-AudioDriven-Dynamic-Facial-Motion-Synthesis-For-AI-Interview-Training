
import textract
import pdfplumber
import fitz  # PyMuPDF
import string
from collections import Counter
from .summarize import summarize_pdf

from PyPDF2 import PdfReader

def read_pdf_with_pypdf2(file_path):
    pdf = PdfReader(file_path)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text


def read_pdf_with_textract(file_path):
    return textract.process(file_path).decode()

def read_pdf_with_pdfplumber(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def read_pdf_with_pymupdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Define text quality evaluation functions
def evaluate_text_quality(text):
    counter = Counter(text)
    special_char_ratio = sum(count for char, count in counter.items() if char not in string.printable) / len(text)
    whitespace_ratio = sum(count for char, count in counter.items() if char.isspace()) / len(text)
    if special_char_ratio > 0.05 or whitespace_ratio < 0.1:
        return False
    else:
        return True

def evaluate_text_quality_advanced(text):
    counter = Counter(text)
    special_char_ratio = sum(count for char, count in counter.items() if char not in string.printable) / len(text)
    whitespace_ratio = sum(count for char, count in counter.items() if char.isspace()) / len(text)
    words = text.split()
    avg_word_len = sum(len(word) for word in words) / len(words) if words else 0
    lines = text.split('\n')
    avg_line_len = sum(len(line) for line in lines) / len(lines) if lines else 0
    most_common_char = counter.most_common(1)[0][0]
    most_common_char_is_letter = most_common_char.isalpha()
    if (
        special_char_ratio > 0.05 
        or whitespace_ratio < 0.1 
        or not (1 <= avg_word_len <= 15) 
        or not (10 <= avg_line_len <= 200) 
        or not most_common_char_is_letter
    ):
        return False
    else:
        return True

# Define function to extract and select the best text
def extract_and_select_best_advanced_with_fallback(file_path):
    pypdf2_text = read_pdf_with_pypdf2(file_path)
    pdftextract_text = read_pdf_with_textract(file_path)
    pdfplumber_text = read_pdf_with_pdfplumber(file_path)
    pymupdf_text = read_pdf_with_pymupdf(file_path)
    extractions = [
        (pypdf2_text, evaluate_text_quality_advanced(pypdf2_text), len(pypdf2_text.split())),
        (pdftextract_text, evaluate_text_quality_advanced(pdftextract_text), len(pdftextract_text.split())),
        (pdfplumber_text, evaluate_text_quality_advanced(pdfplumber_text), len(pdfplumber_text.split())),
        (pymupdf_text, evaluate_text_quality_advanced(pymupdf_text), len(pymupdf_text.split()))
    ]
    try:
        best_text = max((text for text, is_good, word_count in extractions if is_good), key=len)
        print ("Passed the best quality check\n")
    except ValueError:
        try:
            extractions = [
                (pypdf2_text, evaluate_text_quality(pypdf2_text), len(pypdf2_text.split())),
                (pdftextract_text, evaluate_text_quality(pdftextract_text), len(pdftextract_text.split())),
                (pdfplumber_text, evaluate_text_quality(pdfplumber_text), len(pdfplumber_text.split())),
                (pymupdf_text, evaluate_text_quality(pymupdf_text), len(pymupdf_text.split()))
            ]
            best_text = max((text for text, is_good, word_count in extractions if is_good), key=len)
            print ("Passed the fallback quality check\n")
        except ValueError:
            # If none of the extractions passed the quality check, select the one with the highest word count
            best_text = max(extractions, key=lambda x: x[2])[0]
    
    return best_text
# Extract and select the best text from the PDF using the advanced evaluation function with fallback


# best_text_advanced_with_fallback = extract_and_select_best_advanced_with_fallback("D:\Texas A&M University\Latest_CV\CV\Rohan_Chaudhury__Resume.pdf")
# print(best_text_advanced_with_fallback)  # Displaying first 500 characters for review.
# print (len(best_text_advanced_with_fallback.split()))
# print (len(best_text_advanced_with_fallback))

def get_summarized_pdf(file_path):
    best_text_advanced_with_fallback = extract_and_select_best_advanced_with_fallback(file_path)
    summary = summarize_pdf(best_text_advanced_with_fallback)
    return summary

# best_text_advanced_with_fallback = get_summarized_pdf("D:\Texas A&M University\Latest_CV\CV\Rohan_Chaudhury__Resume.pdf")
# # best_text_advanced_with_fallback = get_summarized_pdf("D:\Texas A&M University\Conversational AI\\asu-resume-template.pdf")
# print(best_text_advanced_with_fallback)  # Displaying first 500 characters for review.
# print (len(best_text_advanced_with_fallback.split()))
# print (len(best_text_advanced_with_fallback))

from . import db
from .models import UserCV

def extract_cv_details_and_store(filename, user_id):
    try:
        cv_details = get_summarized_pdf(filename)
        
        # Delete older entries for this user if they exist
        old_cvs = UserCV.query.filter_by(user_id=user_id).all()
        if old_cvs:
            for cv in old_cvs:
                db.session.delete(cv)
            db.session.commit()

        # Store the new CV details
        user_cv = UserCV(user_id=user_id, details=cv_details)
        db.session.add(user_cv)
        db.session.commit()
        
        return True
    except Exception as e:
        print(f"An error occurred during CV extraction: {e}")
        return False

        
