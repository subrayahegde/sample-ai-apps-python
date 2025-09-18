import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

import tempfile
from PIL import Image
import pytesseract
import docx
import PyPDF2
from pdf2image import convert_from_path
import google.generativeai as genai

# Set up Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error('GEMINI_API_KEY environment variable not set.')
    st.stop()
genai.configure(api_key=API_KEY)

st.title('Contract Risk Analyzer (Gemini AI)')

uploaded_file = st.file_uploader('Upload a legal document (PDF, DOCX, or image)', type=['pdf', 'docx', 'png', 'jpg', 'jpeg'])


def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    text = ''
    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ''
    except Exception:
        # fallback to OCR
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            tmp_pdf.write(file.read())
            tmp_pdf.flush()
            images = convert_from_path(tmp_pdf.name)
            for image in images:
                text += pytesseract.image_to_string(image)
        file.seek(0)
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)


def extract_text(file, filetype):
    if filetype == 'pdf':
        return extract_text_from_pdf(file)
    elif filetype == 'docx':
        return extract_text_from_docx(file)
    elif filetype in ['png', 'jpg', 'jpeg']:
        return extract_text_from_image(file)
    else:
        return ''


def analyze_risks_with_gemini(text):
    prompt = (
        "You are a legal expert. Read the following contract and list all potential risks, liabilities, or unfavorable terms for the party receiving the contract. "
        "Present the risks as a numbered list with a brief explanation for each.\n\nContract Text:\n" + text
    )
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

if uploaded_file:
    filetype = uploaded_file.name.split('.')[-1].lower()
    with st.spinner('Extracting text from document...'):
        text = extract_text(uploaded_file, filetype)
    if not text.strip():
        st.error('No text could be extracted from the document.')
    else:
        st.subheader('Extracted Text (preview)')
        st.text_area('Text', text[:2000] + ('...' if len(text) > 2000 else ''), height=200)
        if st.button('Analyze Risks with Gemini AI'):
            with st.spinner('Analyzing risks with Gemini AI...'):
                try:
                    risks = analyze_risks_with_gemini(text)
                    st.subheader('Identified Risks')
                    st.markdown(risks)
                except Exception as e:
                    st.error(f'Error analyzing risks: {e}') 
