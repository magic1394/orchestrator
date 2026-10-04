import os
import streamlit as st
from dotenv import load_dotenv

# Muat file .env jika running di lokal
load_dotenv()

class Config:
    # Cek dari Streamlit Secrets dulu, jika tidak ada baru ambil dari .env/os.environ
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY and not cls.OPENROUTER_API_KEY:
            print("[Warning] Kunci API tidak ditemukan!")
            return False
        return True