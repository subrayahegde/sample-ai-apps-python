import streamlit as st
from dotenv import load_dotenv
import os
import requests
load_dotenv()

# === CONFIG ===
API_KEY = os.getenv("MISTRAL_API_KEY")  # Replace with your real Mistral API key
API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-small"  # Or mistral-medium / mistral-tiny

# === Streamlit UI Setup ===
st.set_page_config(page_title="Mistral Storyteller", layout="centered")
st.markdown("<h1 style='text-align:center;'>📖 Mistral Storyteller</h1>", unsafe_allow_html=True)
st.caption("Let Mistral spin a short story from your imagination.")

# === User Prompt Input ===
user_prompt = st.text_input("Enter a theme, setting, or character (optional):", placeholder="e.g. A girl who talks to animals")

if st.button("Generate Story ✨"):
    with st.spinner("Mistral is writing your story..."):
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            messages = [
                {
                    "role": "system",
                    "content": "You are a creative and imaginative storyteller. Write vivid and short stories."
                },
                {
                    "role": "user",
                    "content": f"Write a short story under 300 words{' about ' + user_prompt if user_prompt else ''}."
                }
            ]

            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.9,
                "max_tokens": 600,
                "stream": False
            }

            response = requests.post(API_URL, headers=headers, json=payload)
            result = response.json()

            story = result["choices"][0]["message"]["content"].strip()
            st.markdown("### 📝 Your Story")
            st.write(story)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.info("Enter an idea or theme and click the button to generate your story.")

