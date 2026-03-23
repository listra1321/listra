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

        # =========================
        # PROMPT UTAMA (SIMPLE & KUAT)
        # =========================
        prompt = f"""
Anda adalah sistem pendukung keputusan kebijakan ekowisata.

ATURAN:
- Fokus hanya pada destinasi: {destination}
- Gunakan nama {destination} dalam narasi
- Gunakan Bahasa Indonesia formal
- Jangan menyebut destinasi lain
- Jangan membuat format tambahan

DATA:
Teks wisatawan:
Pengalaman wisata di {destination}.
{text}

Deskripsi gambar:
{caption}

TUJUAN KEBIJAKAN:
{tujuan}

TULIS HASIL PERSIS SEPERTI FORMAT INI:

📖 Storytelling:
Saya mengunjungi {destination} dan ...

🏛️ Rekomendasi Kebijakan:
1. ...
2. ...
3. ...
"""

        # =========================
        # SYSTEM PROMPT (PENGUAT)
        # =========================
        system_prompt = f"""
Anda hanya membahas {destination}.

WAJIB:
- Gunakan Bahasa Indonesia
- Gunakan nama {destination}, bukan "Destinasi Wisata"
- Ikuti format output persis seperti diminta
- Jangan menambahkan penjelasan lain
"""

        # =========================
        # CALL LLM
        # =========================
        result = call_llm(system_prompt, prompt)

        # =========================
        # CLEANING OUTPUT (ANTI ERROR)
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

        # hapus pola jawaban model yang sering muncul
        if "Berikut adalah" in result:
            result = result.replace("Berikut adalah tugas yang telah saya lakukan:", "")

        if "Based on the input provided," in result:
            result = result.replace("Based on the input provided,", "")

        # =========================
        # DEBUG (OPSIONAL)
        # =========================
        print("DEBUG RESULT:", result)

        return result
