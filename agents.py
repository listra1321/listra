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

=========================
ATURAN WAJIB (STRICT MODE)
=========================

1. WAJIB menyebut nama destinasi ini di kalimat pertama:
   "{destination}"

2. DILARANG menggunakan istilah:
   - "Destinasi Wisata"
   - "tempat ini"
   - "lokasi ini"

3. DILARANG menyebut:
   - kota/negara lain
   - destinasi lain selain "{destination}"

4. DILARANG mengarang fakta (contoh: suhu, negara, sejarah fiktif)

5. Jika informasi tidak tersedia:
   → gunakan deskripsi umum yang realistis
   → JANGAN berhalusinasi

6. Storytelling HARUS konsisten dengan:
   - teks input
   - caption gambar
   - destinasi "{destination}"

=========================
DATA
=========================

Destinasi: {destination}
Tujuan Kebijakan: {tujuan}

=========================
INPUT
=========================

Teks:
Pengalaman wisata di {destination}.
{text}

Deskripsi Gambar:
{caption}

=========================
CONTOH
=========================

{fewshot}

=========================
TUGAS
=========================

1. Buat storytelling naratif (1–2 paragraf)
2. Sebut {destination} di kalimat pertama
3. Integrasikan teks + gambar
4. Identifikasi isu secara implisit dalam cerita
5. Buat 3 rekomendasi kebijakan:
   - spesifik
   - realistis
   - berbasis cerita

=========================
FORMAT OUTPUT (WAJIB)
=========================

📖 Storytelling:
(TULIS DI SINI)

🏛️ Rekomendasi Kebijakan:
1. ...
2. ...
3. ...

=========================
LARANGAN TAMBAHAN
=========================

- Jangan menyebut tempat lain
- Jangan menambahkan data palsu
- Jangan keluar dari konteks {destination}
"""

        result = call_llm(
            "Anda adalah sistem DSS ekowisata yang ketat dan tidak boleh berhalusinasi.",
            prompt
        )

        # =========================
        # POST-PROCESSING GUARD
        # =========================

        if "Destinasi Wisata" in result:
            result = result.replace("Destinasi Wisata", destination)

        return result
