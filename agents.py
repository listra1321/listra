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
        # PROMPT UTAMA (MULTIMODAL STRONG)
        # =========================
        prompt = f"""
Anda adalah sistem pendukung keputusan kebijakan ekowisata berbasis multimodal.

ATURAN:
- Fokus hanya pada destinasi: {destination}
- Gunakan Bahasa Indonesia formal
- WAJIB menggabungkan informasi dari teks DAN deskripsi gambar
- WAJIB menyebut elemen visual dari gambar (objek, suasana, aktivitas)
- DILARANG menambahkan detail visual yang tidak ada di caption
- Dilarang membuat cerita umum yang tidak sesuai dengan gambar
- Jika caption terbatas, gunakan deskripsi umum tanpa mengarang
- Jangan menyebut destinasi lain

DATA:
Teks wisatawan:
Pengalaman wisata di {destination}.
{text}

Deskripsi gambar:
{caption}

TUJUAN KEBIJAKAN:
{tujuan}

TUGAS:
1. Buat storytelling yang menggabungkan teks dan gambar secara nyata
2. Sebut detail visual dari gambar dalam narasi
3. Identifikasi isu berdasarkan kondisi yang terlihat
4. Berikan 3 rekomendasi kebijakan yang relevan

FORMAT OUTPUT (WAJIB):

📖 Storytelling:
Saya mengunjungi {destination} dan melihat ...

🏛️ Rekomendasi Kebijakan:
1. ...
2. ...
3. ...
"""

        # =========================
        # SYSTEM PROMPT (PENGUAT PERILAKU)
        # =========================
        system_prompt = f"""
Anda hanya membahas {destination}.

WAJIB:
- Gunakan Bahasa Indonesia
- Gunakan informasi dari teks dan deskripsi gambar
- Jika gambar menunjukkan objek tertentu, sebutkan dalam cerita
- Jangan membuat narasi umum
- Ikuti format output dengan tepat
- Jangan menambahkan interpretasi visual yang tidak ada
- Jangan mengarang objek seperti "reruntuhan kota" jika tidak disebut
"""

        # =========================
        # CALL LLM
        # =========================
        result = call_llm(system_prompt, prompt)

        # =========================
        # CLEANING OUTPUT (BACKUP)
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
        # DEBUG (SANGAT DISARANKAN)
        # =========================
        print("DEBUG DESTINATION:", destination)
        print("DEBUG CAPTION:", caption)
        print("DEBUG RESULT:", result)

        return result
