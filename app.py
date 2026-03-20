import streamlit as st
from PIL import Image
from orchestrator import AgentOrchestrator
from caption_lookup import CaptionLookup
import os

# =========================
# API KEY (Streamlit Cloud)
# =========================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or st.secrets["OPENROUTER_API_KEY"]

st.set_page_config(
    page_title="Agentic DSS Ekowisata | Listra Horhoruw",
    layout="wide"
)

from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

@st.cache_resource
def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

def generate_caption_blip(image):
    processor, model = load_blip()

    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)

    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

# =========================
# LOAD CAPTION DATASET
# =========================
caption_db = CaptionLookup("data_caption.csv")

# =========================
# HELPER
# =========================
def detect_destination(text):
    text_lower = text.lower()

    if "toba" in text_lower:
        return "Danau Toba"
    elif "borobudur" in text_lower:
        return "Candi Borobudur"
    else:
        return "Destinasi Wisata"

# =========================
# UI
# =========================
st.title("🌿 Agentic Decision Support System (DSS) Ekowisata")

text = st.text_area("📝 Masukkan teks wisata")

image_file = st.file_uploader("📷 Upload gambar")

tujuan = st.selectbox(
    "🎯 Tujuan Kebijakan",
    [
        "Konservasi Lingkungan",
        "Pemberdayaan Masyarakat Lokal",
        "Optimalisasi Ekonomi Pariwisata",
        "Keseimbangan Ekowisata Berkelanjutan"
    ]
)

orch = AgentOrchestrator()

# =========================
# GENERATE
# =========================
if st.button("🧠 Generate Storytelling & Kebijakan"):

    if text and image_file:

        # tampilkan gambar (TETAP ADA)
        image = Image.open(image_file)
        st.image(image, width=240)

        # =========================
        # CAPTION (HANYA BACKEND)
        # =========================
        filename = image_file.name.lower().strip()
        caption = generate_caption_blip(image)

        # fallback kalau tidak ada
        if not caption:
            caption = f"Gambar berkaitan dengan konteks wisata: {text[:100]}"

        # =========================
        # MULTI-AGENT PROCESS
        # =========================
        with st.spinner("🤖 Menghasilkan storytelling dan kebijakan..."):
            result = orch.run(text, caption, tujuan)

        # =========================
        # OUTPUT BERSIH (NO CAPTION)
        # =========================
        st.divider()

        # split hasil jadi 2 bagian
        if "REKOMENDASI:" in result:
            story, rekom = result.split("REKOMENDASI:", 1)
        else:
            story = result
            rekom = ""

        # =========================
        # STORYTELLING
        # =========================
        st.subheader("📄 Storytelling Wisata")
        st.write(story.strip())


    else:
        st.warning("⚠️ Mohon lengkapi teks dan gambar.")

# ======================================================
# Footer
# ======================================================
st.markdown("---")
st.caption(
    "Catatan: Sistem ini merupakan prototipe DSS berbasis agentic control "
    "dan tidak menggantikan kewenangan pengambil kebijakan."
)
