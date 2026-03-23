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
        "temperature": 0.3
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

        prompt = f"""
Anda adalah sistem pendukung keputusan kebijakan ekowisata.

ATURAN:
- Fokus hanya pada destinasi: {destination}
- Dilarang menyebut destinasi lain
- Gunakan Bahasa Indonesia formal

DATA:
Teks wisatawan:
{text}

Deskripsi gambar:
{caption}

TUJUAN KEBIJAKAN:
{tujuan}

TUGAS:
1. Buat storytelling wisata untuk {destination}
2. Identifikasi isu dari cerita
3. Berikan 3 rekomendasi kebijakan konkret

Gunakan bahasa formal, jelas, dan berbasis konteks input.
"""

        result = call_llm(
            f"Anda hanya boleh membahas {destination}. Gunakan Bahasa Indonesia.",
            prompt
        )

        # =========================
        # CLEANING MINIMAL (AMAN)
        # =========================
        bad_words = [
            "Destinasi Wisata",
            "destinasi wisata",
            "Tempat ini",
            "tempat ini",
            "Lokasi ini",
            "lokasi ini"
        ]

        for w in bad_words:
            result = result.replace(w, destination)

        result = result.replace("Based on the input provided,", "")

        print("DEBUG RESULT:", result)

        return result
