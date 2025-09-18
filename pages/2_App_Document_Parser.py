import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

from llama_parse import LlamaParse
import tempfile

# Set your LlamaParse API key (alternatively use st.secrets)
if os.getenv("LLAMA_CLOUD_API_KEY"):
    os.environ["LLAMA_CLOUD_API_KEY"] = os.getenv("LLAMA_CLOUD_API_KEY")

# Set page config
st.set_page_config(page_title="LlamaParse File Extractor", layout="centered")

st.title("Data Extraction from PDF/DOCX/JPEG using LLama AI Model")
st.markdown("Upload a PDF, DOCX, or JPG/JPEG file to extract and display its content.")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.type
    file_name = uploaded_file.name

    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Initialize LlamaParse
    st.info("Parsing file using LlamaParse. Please wait...")
    parser = LlamaParse(result_type="text", verbose=True)

    try:
        documents = parser.load_data(tmp_path)

        # Display the extracted content
        st.success("✅ File successfully parsed!")
        st.subheader("📃 Extracted Content:")
        for doc in documents:
            st.text_area("Parsed Text", doc.text, height=300)

    except Exception as e:
        st.error(f"❌ Failed to parse file: {e}")

