import os
import streamlit as st
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "meta-llama/llama-3-8b-instruct"


def call_llm_multimodal(content):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        res = response.json()
        print("DEBUG RESPONSE:", res)

        if 'choices' in res:
            return res['choices'][0]['message']['content']
        elif 'error' in res:
            return f"API ERROR: {res['error']['message']}"
        else:
            return f"UNKNOWN RESPONSE: {res}"

    except Exception as e:
        return f"EXCEPTION: {str(e)}"
    
def call_llm(system_prompt, user_prompt):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        res = response.json()
        print("DEBUG TEXT:", res)

        if 'choices' in res:
            return res['choices'][0]['message']['content']
        elif 'error' in res:
            return f"API ERROR: {res['error']['message']}"
        else:
            return str(res)

    except Exception as e:
        return str(e)


# =========================
# STORY AGENT
# =========================

class StoryAgent:

    def __init__(self, memory):
        self.memory = memory

    def run(self, context):

        examples = self.memory.get_examples()
        fewshot = self.memory.format_examples(examples)

        prompt = f"""
Gunakan pola contoh berikut:

{fewshot}

Sekarang buat storytelling + rekomendasi kebijakan:

INPUT BARU:
{context}

OUTPUT:
"""

        return call_llm("Ikuti pola contoh.", prompt)


# =========================
# AGENT
# =========================

class UnifiedAgent:

    def __init__(self, memory):
        self.memory = memory

    def run(self, text, caption, destination, tujuan):

        examples = self.memory.get_examples(2)
        fewshot = self.memory.format_examples(examples)

        prompt = f"""
Anda adalah sistem pendukung kebijakan ekowisata berbasis multimodal.

ATURAN WAJIB:
1. Gabungkan teks input dan deskripsi gambar menjadi narasi yang ALAMI dan IMERSIF.
2. Jangan menghilangkan makna dari teks maupun gambar.
3. Pastikan storytelling kontekstual dengan destinasi: {destination}.
4. Setelah storytelling, buat rekomendasi kebijakan untuk pemerintah daerah.
5. Gunakan Bahasa Indonesia formal.

DATA:
Nama Destinasi: {destination}
Tujuan Kebijakan: {tujuan}

TUGAS:
1. Buat storytelling wisata yang natural, mengalir, dan deskriptif
2. Identifikasi isu
3. Berikan 3 rekomendasi kebijakan konkret berdasarkan hasil storytelling

Teks Input:
{text}

Caption Gambar:
{caption}

Contoh:
{fewshot}

OUTPUT FORMAT:

📖 Storytelling:
(paragraf naratif yang menyatu antara teks dan gambar)

🏛️ Rekomendasi Kebijakan:
1.
2.
3.

JANGAN tampilkan evaluasi.
"""

        return call_llm("Anda adalah sistem pendukung kebijakan ekowisata.", prompt)
