import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Rainbow Form 3D", page_icon="🧸", layout="centered")

# Hide Streamlit branding for a professional look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #ffffff;}
    div.stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE API KEY SETUP ---
try:
    # This grabs the key from your Streamlit Secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Server Error: API Key missing. Please go to App Settings > Secrets and add GOOGLE_API_KEY.")
    st.stop()

# --- 3. APP INTERFACE ---
st.title("Turn your drawing into a Toy!")
st.write("Upload a sketch to see the 3D Magic (Powered by Gemini 3.0).")

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the user's sketch
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Sketch", use_column_width=True)

    # The Generate Button
    if st.button("✨ Generate 3D Toy"):
        with st.spinner("Gemini 3.0 (Nano Banana) is sculpting your toy... (Wait ~15s)"):
            try:
                # Configure Google
                genai.configure(api_key=api_key)
                
                # --- MODEL SELECTION ---
                # We use the specific Gemini 3 Pro Image model (Nano Banana)
                # If this fails with 429, ensure you have Pay-As-You-Go billing enabled in Google Cloud.
                model = genai.GenerativeModel('gemini-3-pro-image-preview') 

                # The "Toy Factory" Prompt
                prompt = """
                You are a toy manufacturing expert. Transform this child's sketch into a high-end 3D printed vinyl toy.
                
                CRITICAL RULES:
                1. MATERIAL: Smooth, glossy white plastic.
                2. VOLUME: Turn the flat drawing into a puffy, solid 3D object. The white paper background inside the drawing MUST become the solid white body of the toy.
                3. COLORS: Strictly inherit the marker colors from the drawing.
                4. STYLE: Cute, rounded, safe edges.
                5. OUTPUT: A studio product photo on a white background.
                """

                # --- RUN GENERATION ---
                response = model.generate_content([prompt, image])
                
                # --- SHOW RESULT (THE FIX) ---
                st.success("Here is your toy design!")
                
                # We check if the response contains an image (inline_data)
                # This fixes the "Could not convert to text" error
                if response.parts and response.parts[0].inline_data:
                    # Extract raw image bytes
                    image_data = response.parts[0].inline_data.data
                    st.image(image_data, caption="3D Preview", use_column_width=True)
                    
                    # Optional: Add "Order" button only if generation succeeded
                    st.link_button("🛒 Order This Toy Design ($49)", "https://rainbowform.com/cart")
                else:
                    # Fallback if Google refuses (Safety or Text response)
                    st.warning("Google sent a text response instead of an image:")
                    st.write(response.text)

            except Exception as e:
                # Friendly error handling
                st.error(f"Oops! The AI ran into an issue: {str(e)}")
                if "429" in str(e):
                    st.info("💡 Tip: A 429 error means the Billing Quota was exceeded. Please check your Google Cloud Billing settings.")
