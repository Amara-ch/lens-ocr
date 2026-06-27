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


# === STYLING — Clean white + dark maroon theme ===
st.markdown("""
<style>
    /* Force light theme everywhere */
    .stApp {
        background: #fafaf7 !important;
        color: #1f2937 !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hero section */
    .hero {
        text-align: center;
        padding: 30px 0 40px 0;
    }
    .hero h1 {
        font-size: 60px;
        font-weight: 800;
        margin: 0;
        color: #7f1d1d;
        letter-spacing: -1.5px;
    }
    .hero .tagline {
        font-size: 20px;
        color: #6b7280;
        margin-top: 10px;
        font-weight: 500;
    }
    .hero .badges {
        margin-top: 20px;
    }
    .hero .badge {
        display: inline-block;
        padding: 7px 16px;
        margin: 3px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        background: #ffffff;
        color: #7f1d1d;
        border: 1.5px solid #fecaca;
    }

    /* Section titles */
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        margin: 10px 0 14px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* All text on light bg */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
    .stText, label, .stTextInput label, .stSelectbox label,
    .stFileUploader label {
        color: #1f2937 !important;
    }

    /* Selectbox - force light theme */
    .stSelectbox > div > div {
        background: #ffffff !important;
        color: #1f2937 !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    .stSelectbox label {
        color: #374151 !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #1f2937 !important;
    }
    div[data-baseweb="popover"] {
        background: #ffffff !important;
    }
    li[role="option"] {
        background: #ffffff !important;
        color: #1f2937 !important;
    }
    li[role="option"]:hover {
        background: #fef2f2 !important;
        color: #7f1d1d !important;
    }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        background: #ffffff !important;
        border: 2px dashed #fecaca !important;
        border-radius: 12px !important;
        padding: 24px !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #7f1d1d !important;
        background: #fef2f2 !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #6b7280 !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: #7f1d1d !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
    }

    /* Primary button */
    .stButton button {
        background: #7f1d1d !important;
        color: white !important;
        border: none !important;
        padding: 14px 28px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    .stButton button:hover {
        background: #991b1b !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(127, 29, 29, 0.3) !important;
    }
    .stButton button:active {
        transform: translateY(0) !important;
    }

    /* Download button */
    .stDownloadButton button {
        background: #ffffff !important;
        color: #7f1d1d !important;
        border: 2px solid #7f1d1d !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton button:hover {
        background: #7f1d1d !important;
        color: white !important;
    }

    /* Info / success / error messages */
    .stAlert {
        border-radius: 10px !important;
        border-left: 4px solid #7f1d1d !important;
    }
    [data-baseweb="notification"] {
        background: #fef2f2 !important;
        color: #1f2937 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f3f4f6;
        padding: 4px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #6b7280 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #ffffff !important;
        color: #7f1d1d !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Tab content */
    .stTabs [data-baseweb="tab-panel"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        margin-top: 12px;
        border: 1px solid #e5e7eb;
    }

    /* Rendered markdown inside tabs - readable! */
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] li,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] div {
        color: #1f2937 !important;
    }

    /* Code blocks */
    .stCodeBlock, code {
        background: #fef2f2 !important;
        color: #7f1d1d !important;
        border-radius: 8px !important;
    }
    pre {
        background: #1f2937 !important;
        color: #f9fafb !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
    pre code {
        background: transparent !important;
        color: #f9fafb !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        color: #1f2937 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 1px solid #e5e7eb !important;
    }

    /* Caption */
    [data-testid="stCaptionContainer"] {
        color: #6b7280 !important;
    }

    /* Image caption */
    .stImage [data-testid="stImageCaption"] {
        color: #6b7280 !important;
        font-style: italic;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #7f1d1d !important;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        color: #6b7280;
        font-size: 14px;
        padding: 30px 0 10px 0;
        margin-top: 50px;
        border-top: 1px solid #e5e7eb;
    }
    .app-footer a {
        color: #7f1d1d;
        text-decoration: none;
        font-weight: 600;
    }
    .app-footer a:hover {
        color: #991b1b;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)


# === HERO SECTION ===
st.markdown("""
<div class='hero'>
    <h1>🔍 lens-ocr</h1>
    <div class='tagline'>Mistral-quality OCR — Free & Open Source</div>
    <div class='badges'>
        <span class='badge'>✓ Handwriting</span>
        <span class='badge'>✓ LaTeX equations</span>
        <span class='badge'>✓ Tables</span>
        <span class='badge'>✓ 80+ languages</span>
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
