API_KEY = "AIzaSyDa8Q7XB6CKnpAGeB6R1OThQOzrgS5FAIo"
from google import genai
from google.genai import types
  # paste your key

client = genai.Client(api_key=API_KEY)

SYSTEM = (
    "You are VOID, a fun casual friend from Hyderabad. "
    "Reply in Tenglish (Telugu + English mix) like a WhatsApp text. "
    "Short replies only. Just reply directly as a friend would."
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

# Try models in order from lightest to heaviest
models_to_try = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-lite-001",
    "gemini-flash-lite-latest",
    "gemini-2.0-flash-001",
    "gemini-2.5-flash",
]

working_model = None
for m in models_to_try:
    try:
        r = client.models.generate_content(
            model=m,
            config=types.GenerateContentConfig(system_instruction=SYSTEM),
            contents="test",
        )
        working_model = m
        print(f"✅ Using model: {m}\n")
        break
    except Exception as e:
        print(f"❌ {m}: {str(e)[:60]}")

if not working_model:
    print("No model worked. Check your API key or quota.")
else:
    print("=" * 60)
    print(f"VOID - Tenglish Test ({working_model})")
    print("=" * 60)

    for q in questions:
        response = client.models.generate_content(
            model=working_model,
            config=types.GenerateContentConfig(system_instruction=SYSTEM),
            contents=q,
        )
        print(f"\nUser : {q}")
        print(f"VOID : {response.text.strip()}")
        print("-" * 40)