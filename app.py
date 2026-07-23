import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io

# ---------------------------------------------------------
# Web Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Microstock SEO Metadata Generator",
    page_icon="🎨",
    layout="wide"
)

# Custom Styling (Luxurious & Minimalist Dark Theme)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Enterprise Microstock SEO Generator")
st.caption("Upload images and generate publication-ready CSV metadata for Adobe Stock, Freepik & Shutterstock.")

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configuration")

# API Key input (User can enter their own API key, so your limit isn't exhausted)
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

model_choice = st.sidebar.selectbox(
    "Select AI Model:",
    ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-3.1-pro-extended"]
)

platform = st.sidebar.radio(
    "Target Platform Rules:",
    ["Adobe Stock (Comma ,)", "Freepik (Semicolon ;)"]
)

# ---------------------------------------------------------
# Master Prompt definition
# ---------------------------------------------------------
MASTER_PROMPT_TEMPLATE = """Act as an Elite Adobe Stock Metadata Strategist, Enterprise Microstock SEO Architect, and Commercial Buyer Intent Optimization Expert (July 2026).

Your mission is to produce publication-ready CSV metadata that maximizes discoverability, buyer relevance, commercial search intent, and long-term ranking potential.

=========================================================
STRICT CSV FORMAT
=========================================================
Header MUST be exactly:
Filename,Title,Keywords,Category

Rules:
• Wrap Title inside double quotes
• Wrap Keywords inside double quotes
• Convert every .jpg or .png filename into .eps
• Preserve filename except extension
• Output ONLY a single line of CSV data (no header)

=========================================================
TITLE & KEYWORD OPTIMIZATION
=========================================================
- Title: Target length 60–70 characters. Structure: [Quantity/Type] + [Subject] + [Commercial Use] + [Style] + [Vector Spec].
- Keywords: EXACTLY 49 UNIQUE keywords, ordered by commercial importance. No duplicates.
- Keywords 1-3: Core niche & subject.
- Keywords 4-6: Asset type (vector, icon, etc.).
- Keywords 7-10: Industry & application.
- Keywords 11-40: Commercial terminology, literal objects, concepts.
- Keywords 41-49: Visual style keywords (clean, minimal, modern, professional, etc.).

=========================================================
COMMERCIAL & SAFETY FILTER
=========================================================
No religious, political, trademarked, or offensive terms. Commercially safe only.
Assign the single most relevant Category.

Original filename: {filename}
Output ONLY the CSV row. No markdown, no commentary.
"""

# ---------------------------------------------------------
# File Upload & Processing
# ---------------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload JPG or PNG files:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files and st.button("✨ Generate SEO Metadata"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to proceed!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_choice)
            
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, file in enumerate(uploaded_files):
                status_text.text(f"Processing ({index+1}/{len(uploaded_files)}): {file.name}")
                
                # Image processing
                image = Image.open(file)
                prompt = MASTER_PROMPT_TEMPLATE.format(filename=file.name)
                
                # Gemini Call
                response = model.generate_content([prompt, image])
                raw_out = response.text.strip().replace('```csv', '').replace('```', '').strip()
                
                # Parse output line
                parts = raw_out.split(',', 3)
                if len(parts) >= 3:
                    # Basic cleanup for formatting
                    clean_filename = file.name.rsplit('.', 1)[0] + ".eps"
                    
                    results.append({
                        "Filename": clean_filename,
                        "Title": parts[1].replace('"', '').strip() if len(parts) > 1 else "",
                        "Keywords": parts[2].replace('"', '').strip() if len(parts) > 2 else "",
                        "Category": parts[3].replace('"', '').strip() if len(parts) > 3 else "Vector"
                    })
                
                progress_bar.progress((index + 1) / len(uploaded_files))
                
            status_text.success("✅ All images processed successfully!")
            
            # Display DataFrame on screen
            df = pd.DataFrame(results)
            st.subheader("📋 Generated Metadata Output")
            st.dataframe(df, use_container_width=True)
            
            # Convert to CSV for download
            if platform == "Freepik (Semicolon ;)":
                csv_data = df.to_csv(index=False, sep=';')
            else:
                csv_data = df.to_csv(index=False, sep=',')
                
            st.download_button(
                label="📥 Download CSV File",
                data=csv_data,
                file_name="Microstock_Metadata_SEO.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")