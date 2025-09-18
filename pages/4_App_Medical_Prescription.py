from __future__ import annotations
import base64
import os
from typing import List
from datetime import datetime
from langchain.chains import TransformChain
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

import pandas as pd
import shutil
import google.generativeai as genai

if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

parser = None
st.set_page_config(layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("pages/styles.css")

class MedicationItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str

class PrescriptionInformations(BaseModel):
    patient_name: str = Field(description="Patient's name")
    patient_age: int = Field(description="Patient's age")
    patient_gender: str = Field(description="Patient's gender")
    doctor_name: str = Field(description="Doctor's name")
    doctor_license: str = Field(description="Doctor's license number")
    prescription_date: datetime = Field(description="Date of the prescription")
    medications: List[MedicationItem] = []
    additional_notes: str = Field(description="Additional notes or instructions")

def load_images(inputs: dict) -> dict:
    image_paths = inputs["image_paths"]
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    images_base64 = [encode_image(image_path) for image_path in image_paths]
    return {"images": images_base64}

load_images_chain = TransformChain(
    input_variables=["image_paths"],
    output_variables=["images"],
    transform=load_images
)

def image_model(inputs: dict) -> str:
    model = genai.GenerativeModel('gemini-1.5-flash')

    images_base64 = inputs['images']
    prompt = """
    You are an expert medical transcriptionist specializing in deciphering and accurately transcribing handwritten medical prescriptions.

    Extract and return the following details from the provided prescription:
    1. Patient's full name
    2. Patient's age (handle different formats like "42y", "42yrs", "42", "42 years")
    3. Patient's gender
    4. Doctor's full name
    5. Doctor's license number
    6. Prescription date (in YYYY-MM-DD format)
    7. List of medications including:
       - Medication name
       - Dosage
       - Frequency
       - Duration
    8. Additional notes or instructions (as bullet points, clearly structured)

    Return the response as structured JSON with matching keys.

    Base64-encoded prescription image content:
    """

    image_parts = [
        {"mime_type": "image/png", "data": base64.b64decode(img_b64)}
        for img_b64 in images_base64
    ]

    response = model.generate_content(
        [prompt, *image_parts],
        generation_config={"temperature": 0.4},
    )

    return response.text

def get_prescription_informations(image_paths: List[str]) -> dict:
    parser = JsonOutputParser(pydantic_object=PrescriptionInformations)
    vision_chain = load_images_chain | image_model | parser
    return vision_chain.invoke({'image_paths': image_paths})

def remove_temp_folder(path):
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

def main():
    st.title('Medical Prescription Parsing (Gemini Flash 1.5)')
    global parser
    parser = JsonOutputParser(pydantic_object=PrescriptionInformations)
    uploaded_file = st.file_uploader("Upload a Prescription image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = uploaded_file.name.split('.')[0].replace(' ', '_')
        output_folder = os.path.join(".", f"Check_{filename}_{timestamp}")
        os.makedirs(output_folder, exist_ok=True)

        check_path = os.path.join(output_folder, uploaded_file.name)
        with open(check_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.expander("Prescription Image", expanded=False):
            st.image(uploaded_file, caption='Uploaded Prescription Image.', use_column_width=True)

        with st.spinner('Processing Prescription...'):
            final_result = get_prescription_informations([check_path])
            if 'additional_notes' in final_result:
                additional_notes = final_result['additional_notes']
                if isinstance(additional_notes, list):
                    formatted_notes = "<br> ".join(additional_notes)
                else:
                    formatted_notes = additional_notes.replace("\n", "<br> ")
                final_result['additional_notes'] = f"<ul><li>{formatted_notes}</li></ul>"

            data = [(key, final_result[key]) for key in final_result if key != 'medications']
            df = pd.DataFrame(data, columns=["Field", "Value"])
            st.write(df.to_html(classes='custom-table', index=False, escape=False), unsafe_allow_html=True)

            if 'medications' in final_result and final_result['medications']:
                medications = final_result['medications']
                st.subheader("Medications")

                # Normalize each dict if nested under a single key
                if isinstance(medications[0], dict) and all(len(m) == 1 for m in medications):
                    flat_meds = [list(m.values())[0] for m in medications]
                else:
                    flat_meds = medications

                medications_df = pd.DataFrame(flat_meds)
                st.table(medications_df)


        remove_temp_folder(output_folder)

if __name__ == "__main__":
    main()
