import os
import json
import requests
from google import genai
from config.settings import Config

class SmartAIRouter:
    def __init__(self, gemini_key=None, openrouter_key=None):
        # Mengambil kunci otomatis dari Config jika tidak diisi manual
        self.gemini_key = gemini_key or Config.GEMINI_API_KEY
        self.openrouter_key = openrouter_key or Config.OPENROUTER_API_KEY
        
class UnifiedMemoryEngine:
    """Mengelola memori percakapan tunggal agar tidak hilang saat berganti AI."""
    def __init__(self, system_instruction="Kamu adalah asisten pengonsep proyek otomatisasi video."):
        self.history = [
            {"role": "system", "content": system_instruction}
        ]

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_full_history(self):
        return self.history


class SmartAIRouter:
    """Routing otomatis berhirarki 5 AI dengan penyampaian konteks penuh."""
    def __init__(self, gemini_key=None, openrouter_key=None):
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        self.openrouter_key = openrouter_key or os.getenv("OPENROUTER_API_KEY")

    def execute_prompt(self, memory_engine: UnifiedMemoryEngine, user_prompt: str) -> str:
        memory_engine.add_message("user", user_prompt)
        history = memory_engine.get_full_history()

        # Daftar urutan prioritas 5 AI yang akan dicoba satu per satu
        providers = [
            ("1. Google Gemini", self._call_gemini),
            ("2. ChatGPT (OpenAI)", lambda h: self._call_openrouter_model(h, "openai/gpt-4o-mini")),
            ("3. Anthropic Claude", lambda h: self._call_openrouter_model(h, "anthropic/claude-3.5-sonnet")),
            ("4. Perplexity AI", lambda h: self._call_openrouter_model(h, "perplexity/sonar")),
            ("5. Copilot / GPT-4o", lambda h: self._call_openrouter_model(h, "openai/gpt-4o"))
        ]

        response_text = None

        for name, provider_func in providers:
            try:
                print(f"\n[Router] Mencoba menghubungkan ke {name}...")
                response_text = provider_func(history)
                print(f"[Router] Berhasil direspon oleh {name}!")
                break # Keluar dari loop jika AI berhasil menjawab
            except Exception as e:
                print(f"[Warning] {name} gagal / token habis: {e}")
                print("[Router] Dialihkan ke AI berikutnya...")

        # Fallback terakhir jika semua 5 AI di atas gagal/habis token
        if not response_text:
            print("[Router] Semua API habis. Mengalihkan ke Offline Fallback...")
            last_msg = [m['content'] for m in history if m['role'] == 'user'][-1]
            response_text = f"[Mode Offline] Semua limit API habis. Konteks tetap aman untuk: '{last_msg}'."

        memory_engine.add_message("assistant", response_text)
        return response_text

    def _call_gemini(self, history):
        # Jika Gemini Key lokal bermasalah, dipanggil via OpenRouter (Tetap Gratis)
        if self.openrouter_key:
            return self._call_openrouter_model(history, "google/gemini-2.5-flash:free")
        
        # Fallback biasa jika menggunakan SDK Google
        client = genai.Client(api_key=self.gemini_key)
        formatted_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_prompt
        )
        return response.text

    def _call_openrouter_model(self, history, model_name):
        if not self.openrouter_key:
            raise ValueError("API Key OpenRouter belum dipasang.")

        payload_messages = []
        for msg in history:
            role = msg["role"] if msg["role"] in ["system", "user", "assistant"] else "user"
            payload_messages.append({"role": role, "content": msg["content"]})

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model_name,
                "messages": payload_messages
            }),
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            raise RuntimeError(f"HTTP Error {response.status_code}: {response.text}")


# --- MODES INTERAKTIF TERMINAL ---
if __name__ == "__main__":
    memory = UnifiedMemoryEngine(system_instruction="Kamu adalah asisten multi-AI terintegrasi.")
    router = SmartAIRouter()

    print("=== SEAMLESS 5-AI INTEGRATED CONSOLE ===")
    
    while True:
        user_input = input("\nKamu: ")
        if user_input.lower() in ["exit", "keluar"]:
            print("Sampai jumpa!")
            break
            
        if not user_input.strip():
            continue
            
        response = router.execute_prompt(memory, user_input)
        print(f"\nAI Output:\n{response}")