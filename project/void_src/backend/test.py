import google.generativeai as genai
import os
GEMINI_API=os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "You are VOID, a fun casual friend from Hyderabad. "
        "Reply in Tenglish (Telugu + English mix) like a WhatsApp text. "
        "Short replies only. Never include instructions or meta-commentary in your reply. "
        "Just reply directly as a friend would."
    )
)

questions = [
    "em chestunnav bro?",
    "ela unnav ra?",
    "oka funny joke cheppu",
    "Pokiri movie lo Mahesh Babu dialogue cheppu",
    "nenu sad ga unnanu bro",
    "tomorrow exam undi nervous ga unnanu",
    "best friend ki emi gift istav?",
    "nenu chala bore ga unnanu entertain cheyyi",
]

print("=" * 60)
print("VOID - Gemini Tenglish Test")
print("=" * 60)

for q in questions:
    # Fresh chat each time to avoid context bleed
    chat = model.start_chat(history=[])
    response = chat.send_message(q)
    print(f"\nUser : {q}")
    print(f"VOID : {response.text.strip()}")
    print("-" * 40)