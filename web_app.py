import streamlit as st
from orchestrator import UnifiedMemoryEngine, SmartAIRouter
from config.settings import Config

# Setup Halaman Streamlit
st.set_page_config(page_title="Multi-AI Super App", page_icon="🤖", layout="centered")
st.title("🤖 Multi-AI Orchestrator")
st.caption("Sistem Otomatisasi Konten & Naskah dengan Smart Fallback")

# Inisialisasi Memory Engine & Router ke dalam Session State Streamlit
if "memory" not in st.session_state:
    st.session_state.memory = UnifiedMemoryEngine(
        system_instruction="Kamu adalah asisten pengonsep proyek otomatisasi video."
    )
if "router" not in st.session_state:
    st.session_state.router = SmartAIRouter()

# Tampilkan Riwayat Obrolan di Layar Web
for msg in st.session_state.memory.history:
    if msg["role"] == "system":
        continue
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(msg["content"])

# Form Input Prompt Pengguna
if user_input := st.chat_input("Ketik instruksi naskah/ide di sini..."):
    # Tampilkan pesan pengguna di antarmuka
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Jalankan Orchestrator dan tampilkan respon AI
    with st.chat_message("assistant"):
        with st.spinner("Mengolah dengan Smart Fallback Router..."):
            response = st.session_state.router.execute_prompt(st.session_state.memory, user_input)
            st.markdown(response)