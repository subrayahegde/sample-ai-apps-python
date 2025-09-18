
import streamlit as st
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
load_dotenv()

def main():
    st.set_page_config(page_title="AI App Gallery", layout="wide")

    # App Gallery
    st.title("App Gallery")
    apps = [
        {"name": "Risk Analysis", "description": "Scans a contract and lists all potential risks, liabilities, or unfavorable terms"},
        {"name": "Document Parser", "description": "Extracts details from a PDF/DOCX/JPEG file and displays the content in textual format"},
        {"name": "Illness Testing", "description": "Identifies any anomalies, diseases or any health issues by scanning the uploaded Image"},
        {"name": "Medical Prescription", "description": "Scans the Handwritten Medical prescrition and shows Medicine/dosage details in a table"},
        {"name": "Multi-modal Diagnosis", "description": "Generates a medical diagnosis based on the provided prompt and optional multimedia"},
        {"name": "Translation Service", "description": "Accepts a file (PDF, Docx or an Image in English), translates the content into Hindi or Kannada"},
        {"name": "Youtube Summarizer", "description": "Lists the essence of a given YouTube video transcript into a concise summary"},
        {"name": "Story Teller", "description": "This app creates a story based on your imagination"}
    ]

    cols = st.columns(4)
    for i, app in enumerate(apps):
        with cols[i % 4]:
            st.subheader(app["name"])
            st.write(app["description"])
            if st.button("Try Now", key=f"app_{i}"):           
                st.switch_page(f"pages/{i+1}_App_{app['name'].replace(' ', '_')}.py")

if __name__ == '__main__':
    main()
