"""lens-ocr — Streamlit web app for Mistral-quality OCR.

Deployed on Streamlit Cloud:
https://lens-ocr.streamlit.app
"""
import os
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image


# Page config
st.set_page_config(
    page_title="lens-ocr — Mistral-quality OCR",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Try to load Gemini key from Streamlit secrets first, then env var
def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")


# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1e40af; }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        background: #10b981;
        color: white;
        border-radius: 12px;
        font-size: 14px;
        font-weight: bold;
        margin-left: 10px;
    }
    .output-card {
        background: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-top: 20px;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🔍 lens-ocr")
    st.markdown("### Mistral-quality OCR — FREE, Open Source")
with col2:
    st.markdown("<br><span class='badge'>MISTRAL-QUALITY</span>", unsafe_allow_html=True)


st.markdown("""
Upload any document image — handwritten or printed — and get clean **Markdown with LaTeX equations**.
Powered by Google Gemini Vision. Built with ❤️ by [@humbleunitydev](https://github.com/humbleunitydev/lens-ocr).
""")


# Sidebar — settings
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    api_key_input = st.text_input(
        "Gemini API Key",
        value="",
        type="password",
        help="Get FREE key at https://aistudio.google.com/apikey",
        placeholder="AQ.Ab8RN6..."
    )

    model = st.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
        index=0,
        help="Flash = fast | Pro = best quality"
    )

    st.markdown("---")
    st.markdown("## 📚 About")
    st.markdown("""
    **lens-ocr** is an open-source OCR tool that rivals paid services like Mistral OCR.

    **Features:**
    - 📐 Handwriting recognition
    - ➗ Equation → LaTeX
    - 📊 Tables → Markdown
    - 📄 Multi-page PDFs
    - 🌍 80+ languages

    [GitHub Repo →](https://github.com/humbleunitydev/lens-ocr)
    """)


# Main area — two columns
col_left, col_right = st.columns([1, 1])


with col_left:
    st.markdown("### 📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg", "webp"],
        help="Supports PNG, JPG, JPEG, WebP"
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption=uploaded_file.name, use_container_width=True)

        if st.button("✨ Extract Content", type="primary", use_container_width=True):
            # Get API key
            key = api_key_input or get_api_key()
            if not key:
                st.error("⚠️ Please provide a Gemini API key in the sidebar!")
                st.info("Get a FREE key at https://aistudio.google.com/apikey")
            else:
                with st.spinner(f"🤖 {model} is reading your document..."):
                    try:
                        # Lazy import to avoid loading at startup
                        from src.lens_ocr.cloud.gemini_vision import GeminiVision

                        # Save uploaded file to temp
                        with tempfile.NamedTemporaryFile(
                            suffix=Path(uploaded_file.name).suffix,
                            delete=False
                        ) as f:
                            f.write(uploaded_file.getvalue())
                            temp_path = f.name

                        # Run Gemini
                        vision = GeminiVision(api_key=key, model=model)
                        markdown = vision.parse(temp_path)

                        # Store in session
                        st.session_state["markdown"] = markdown
                        st.session_state["filename"] = uploaded_file.name

                        # Cleanup
                        try:
                            os.unlink(temp_path)
                        except Exception:
                            pass

                        st.success("✅ Done!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


with col_right:
    st.markdown("### 📄 Extracted Content")

    if "markdown" in st.session_state:
        markdown = st.session_state["markdown"]

        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["🎨 Rendered", "📝 Raw Markdown", "💾 Download"])

        with tab1:
            st.markdown(markdown)

        with tab2:
            st.code(markdown, language="markdown")

        with tab3:
            filename_base = Path(st.session_state.get("filename", "output")).stem
            st.download_button(
                "⬇️ Download as Markdown",
                data=markdown,
                file_name=f"{filename_base}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.download_button(
                "⬇️ Download as Plain Text",
                data=markdown,
                file_name=f"{filename_base}.txt",
                mime="text/plain",
                use_container_width=True,
            )
    else:
        st.info("👈 Upload an image and click Extract to see results here")
        st.markdown("""
        **Sample output for handwritten quadratic formula:**

        $$ax^2 + bx + c = 0$$

        $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
        """)


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6b7280; padding: 20px;'>
    Built with ❤️ by <a href='https://github.com/humbleunitydev'>@humbleunitydev</a> |
    <a href='https://github.com/humbleunitydev/lens-ocr'>⭐ Star on GitHub</a> |
    Powered by Google Gemini
    </div>
    """,
    unsafe_allow_html=True,
)
