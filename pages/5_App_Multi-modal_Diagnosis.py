import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

import google.generativeai as genai
from PIL import Image
import io

# Set up Google Gemini API
try:
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')  # Using vision model for potential frame analysis
except KeyError:
    st.error("Please add your Gemini API key to Streamlit secrets.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while initializing the Gemini API: {e}")
    st.stop()

def generate_diagnosis(prompt, image=None, audio=None, video=None):
    """
    Generates a medical diagnosis based on the provided prompt and optional multimedia.
    """
    content_parts = [prompt]

    if image:
        try:
            img_bytes = image.read()
            img = Image.open(io.BytesIO(img_bytes))
            content_parts.append(img)
        except Exception as e:
            return f"Error reading the uploaded image: {e}"

    if audio:
        audio_bytes = audio.read()
        # Gemini Pro Vision might not directly process audio.
        # You would likely need to transcribe or analyze audio features separately
        # and include the results in the prompt.
        # For this example, we'll just indicate its presence in the prompt.
        prompt += "\nUser has also provided an audio file for analysis."
        # In a real application, you would use a dedicated audio processing model
        # to extract relevant information (e.g., speech patterns, cough sounds)
        # and incorporate that into the prompt.

    if video:
        video_bytes = video.read()
        # Gemini Pro Vision can analyze video frames. You would need to decide
        # how to best represent the video content (e.g., analyze key frames,
        # extract motion patterns).
        # For this example, we'll just indicate its presence in the prompt.
        prompt += "\nUser has also provided a video file for analysis."
        # In a real application, you would use a video processing library
        # to extract relevant frames or features and then potentially pass
        # those frames to Gemini Pro Vision or analyze them separately.

    response = model.generate_content(content_parts)
    return response.text if hasattr(response, 'text') else "No response from the model."

def main():
    st.title("Multi-Modal Medical Diagnosis App")
    st.subheader("Powered by Google Gemini")

    st.sidebar.header("Input Parameters")

    # Text input for symptoms and medical history
    symptoms = st.sidebar.text_area("Describe your symptoms and medical history:", height=200)

    # Multimedia file uploaders
    uploaded_image = st.sidebar.file_uploader("Upload a relevant medical image (optional)", type=["png", "jpg", "jpeg"])
    uploaded_audio = st.sidebar.file_uploader("Upload a relevant audio recording (optional)", type=["wav", "mp3", "ogg"])
    uploaded_video = st.sidebar.file_uploader("Upload a relevant video (optional)", type=["mp4", "avi", "mov"])

    # Construct the prompt
    prompt = f"Based on the following symptoms and medical history: {symptoms}. "
    if uploaded_image is not None:
        prompt += "Analyze the following medical image."
    if uploaded_audio is not None:
        prompt += "Analyze the provided audio recording for any relevant medical information."
    if uploaded_video is not None:
        prompt += "Analyze the provided video for any relevant medical information."
    prompt += " Provide a potential diagnosis and recommendations."

    if st.button("Generate Diagnosis"):
        if not symptoms and uploaded_image is None and uploaded_audio is None and uploaded_video is None:
            st.warning("Please provide at least symptoms/medical history or upload relevant multimedia.")
        else:
            with st.spinner("Generating diagnosis..."):
                diagnosis_result = generate_diagnosis(prompt, uploaded_image, uploaded_audio, uploaded_video)
                st.subheader("Diagnosis and Recommendations:")
                st.write(diagnosis_result)
                st.info("Disclaimer: This is an AI-powered tool for informational purposes only and should not be considered a substitute for professional medical advice. Always consult with a qualified healthcare provider for any health concerns.")

if __name__ == "__main__":
    main()
