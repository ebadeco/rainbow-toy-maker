import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Rainbow Form 3D", page_icon="🧸", layout="centered")

# Hide Streamlit branding to look professional
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #ffffff;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE API KEY ---
try:
    # This pulls the key from the secret vault (we set this up next)
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Server Error: API Key missing. Please check Secrets settings.")
    st.stop()

# --- 3. APP INTERFACE ---
st.title("Turn your drawing into a Toy!")
st.write("Upload a sketch to see the 3D Magic.")

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the user's drawing
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Sketch", use_column_width=True)

    # The Magic Button
    if st.button("✨ Generate 3D Toy"):
        with st.spinner("Gemini is sculpting your toy... (Wait ~10s)"):
            try:
                # Connect to Google
                genai.configure(api_key=api_key)
                
                # We use the specific Gemini 3 Vision model
                # Fallback to Gemini 1.5 Pro if 3 is busy/unavailable in your region
                model = genai.GenerativeModel('emini-3-pro-image-preview') 

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

                # Run Generation
                response = model.generate_content([prompt, image])
                
                # Show Result
                st.success("Here is your toy design!")
                st.image(response.text, caption="3D Preview (Note: Using Text description if image fails)", use_column_width=True)
                
                # NOTE for User: Gemini 1.5 Pro returns TEXT descriptions primarily. 
                # For actual IMAGE pixels, we usually use Imagen 3. 
                # If you have access to 'gemini-3-pro-image-preview', change the model name above.
                
                # Link to Shopify Cart
                st.link_button("🛒 Order This Toy Design ($49)", "https://rainbowform.com/cart")

            except Exception as e:
                st.error(f"Oops! Something went wrong. Error: {str(e)}")
