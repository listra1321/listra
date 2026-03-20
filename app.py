import streamlit as st
from PIL import Image
from orchestrator import AgentOrchestrator
from caption_lookup import CaptionLookup

import os
import streamlit as st

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or st.secrets["OPENROUTER_API_KEY"]
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
st.title("🌿 Agentic Ekowisata Berbasis Data")

text = st.text_area("📝 Masukkan teks wisata")

image_file = st.file_uploader("📷 Upload gambar")

tujuan = st.selectbox(
    "🎯 Tujuan Kebijakan",
    [
        "Optimalisasi Ekonomi Pariwisata",
        "Keberlanjutan Lingkungan",
        "Peningkatan Pengalaman Wisatawan"
    ]
)

orch = AgentOrchestrator()

# =========================
# GENERATE
# =========================
if st.button("🧠 Generate Storytelling & Kebijakan"):

    if text and image_file:

        image = Image.open(image_file)
        st.image(image, caption="Gambar Input", use_column_width=True)

        # =========================
        # CAPTION DARI DATASET
        # =========================
        filename = image_file.name.lower().strip()

        caption = caption_db.get_caption(filename)

        # fallback jika tidak ada
        if not caption:
            caption = f"Gambar berkaitan dengan konteks wisata: {text[:100]}"

        st.subheader("📷 Caption Gambar")
        st.write(caption)

        # =========================
        # MULTI-AGENT PROCESS
        # =========================
        with st.spinner("🤖 Menghasilkan storytelling dan kebijakan..."):
            result = orch.run(text, caption, tujuan)

        # =========================
        # OUTPUT
        # =========================
        st.subheader("📄 Storytelling & Rekomendasi Kebijakan")
        st.write(result)

    else:
        st.warning("⚠️ Mohon lengkapi teks dan gambar.")
