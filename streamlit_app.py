"""lens-ocr — Streamlit web app for Mistral-quality OCR.

Live demo: https://lens-ocr-amara.streamlit.app
Repository: https://github.com/Amara-ch/lens-ocr
"""
import os
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image


# Page config
st.set_page_config(
    page_title="lens-ocr | Mistral-quality OCR",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_api_key():
    """Load Gemini key from Streamlit secrets (set in Streamlit Cloud dashboard)."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")


# === STYLING ===
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tighter spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hero section */
    .hero {
        text-align: center;
        padding: 20px 0 30px 0;
    }
    .hero h1 {
        font-size: 56px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero .tagline {
        font-size: 20px;
        color: #6b7280;
        margin-top: 8px;
        font-weight: 500;
    }
    .hero .badges {
        margin-top: 16px;
    }
    .hero .badge {
        display: inline-block;
        padding: 6px 14px;
        margin: 0 4px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-green { background: #d1fae5; color: #065f46; }
    .badge-blue  { background: #dbeafe; color: #1e40af; }
    .badge-purple { background: #ede9fe; color: #5b21b6; }

    /* Section headers */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
        margin: 16px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Button */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 16px;
        width: 100%;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f93 100%);
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* File uploader */
    .stFileUploader {
        background: white;
        border-radius: 12px;
        padding: 4px;
    }

    /* Selectbox */
    .stSelectbox label {
        font-weight: 600;
        color: #374151;
    }

    /* Info / success messages */
    .stAlert {
        border-radius: 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f3f4f6;
        padding: 4px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        color: #9ca3af;
        font-size: 14px;
        padding: 30px 0 10px 0;
        margin-top: 40px;
        border-top: 1px solid #e5e7eb;
    }
    .app-footer a {
        color: #6366f1;
        text-decoration: none;
        font-weight: 600;
    }
    .app-footer a:hover {
        color: #4f46e5;
    }
</style>
""", unsafe_allow_html=True)


# === HERO SECTION ===
st.markdown("""
<div class='hero'>
    <h1>🔍 lens-ocr</h1>
    <div class='tagline'>Mistral-quality OCR — Free & Open Source</div>
    <div class='badges'>
        <span class='badge badge-green'>✓ Handwriting</span>
        <span class='badge badge-blue'>✓ LaTeX equations</span>
        <span class='badge badge-purple'>✓ Tables</span>
        <span class='badge badge-green'>✓ 80+ languages</span>
    </div>
</div>
""", unsafe_allow_html=True)


# === CHECK API KEY (from secrets only — no user input!) ===
api_key = get_api_key()
key_available = bool(api_key)


# === MAIN LAYOUT: 2 columns ===
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="section-title">📤 Upload Document</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop image here or click to browse",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
    )

    # Model selection
    model = st.selectbox(
        "🤖 Choose model",
        ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
        index=0,
        help="Flash = fastest | Pro = highest quality"
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"📄 {uploaded_file.name}", use_container_width=True)

        if not key_available:
            st.error("⚠️ This demo is currently unavailable. Please try again later or [run locally](https://github.com/Amara-ch/lens-ocr).")
        else:
            if st.button("✨ Extract Content", type="primary"):
                with st.spinner(f"🤖 {model} is reading your document..."):
                    try:
                        from src.lens_ocr.cloud.gemini_vision import GeminiVision

                        with tempfile.NamedTemporaryFile(
                            suffix=Path(uploaded_file.name).suffix,
                            delete=False,
                        ) as f:
                            f.write(uploaded_file.getvalue())
                            temp_path = f.name

                        vision = GeminiVision(api_key=api_key, model=model)
                        markdown = vision.parse(temp_path)

                        st.session_state["markdown"] = markdown
                        st.session_state["filename"] = uploaded_file.name

                        try:
                            os.unlink(temp_path)
                        except Exception:
                            pass

                        st.success("✅ Done! See results on the right →")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")


with right:
    st.markdown('<div class="section-title">📄 Extracted Content</div>', unsafe_allow_html=True)

    if "markdown" in st.session_state:
        markdown = st.session_state["markdown"]

        tab1, tab2, tab3 = st.tabs(["🎨 Rendered", "📝 Markdown", "💾 Download"])

        with tab1:
            st.markdown(markdown)

        with tab2:
            st.code(markdown, language="markdown")

        with tab3:
            filename_base = Path(st.session_state.get("filename", "output")).stem
            colA, colB = st.columns(2)
            with colA:
                st.download_button(
                    "⬇️ Markdown",
                    data=markdown,
                    file_name=f"{filename_base}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with colB:
                st.download_button(
                    "⬇️ Plain Text",
                    data=markdown,
                    file_name=f"{filename_base}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
    else:
        st.info("👈 Upload an image and click **Extract Content** to see results here.")
        with st.expander("✨ See sample output"):
            st.markdown("""
            **Handwritten quadratic formula → LaTeX:**

            $$ax^2 + bx + c = 0$$

            $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
            """)


# === FOOTER ===
st.markdown("""
<div class='app-footer'>
    Built with ❤️ by <a href='https://github.com/Amara-ch'>@Amara-ch</a>
    • <a href='https://github.com/Amara-ch/lens-ocr'>⭐ Star on GitHub</a>
    • Powered by Google Gemini Vision
</div>
""", unsafe_allow_html=True)
