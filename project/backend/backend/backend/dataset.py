"""
Run this on your PC to generate a large synthetic Tenglish dataset using Gemini.
pip install google-genai
"""
from google import genai
import json
import time

API_KEY = "AIzaSyDa8Q7XB6CKnpAGeB6R1OThQOzrgS5FAIo"
client = genai.Client(api_key=API_KEY)

TOPICS = [
    # Daily life
    "casual greeting between friends",
    "morning routine conversation",
    "late night conversation between friends",
    "weekend plans discussion",
    "bored at home conversation",
    "waking up late and rushing",
    "power cut situation",
    "rain and weather talk",
    "auto and cab problems",
    "stuck in traffic conversation",

    # Food
    "talking about biryani and food",
    "ordering food online zomato swiggy",
    "eating at dhaba or hotel",
    "cooking disaster at home",
    "craving midnight snacks",
    "discussing favourite street food",
    "tea vs coffee debate",
    "trying new restaurant",

    # College and studies
    "sharing exam stress",
    "asking for help with studies",
    "bunking college together",
    "assignment deadline pressure",
    "results day tension",
    "group study gone wrong",
    "asking notes from friend",
    "professor is strict conversation",
    "placement and campus interview",
    "semester exam preparation",

    # Movies and entertainment
    "discussing Pokiri Mahesh Babu dialogues",
    "talking about Pushpa movie",
    "RRR movie discussion",
    "KGF movie dialogues",
    "discussing favorite hero",
    "going to theatre together",
    "Netflix and OTT discussion",
    "discussing a funny YouTube video",
    "talking about web series",
    "debating best Telugu movie ever",
    "discussing item songs",
    "talking about Allu Arjun",
    "discussing Prabhas movies",
    "talking about Vijay Deverakonda",

    # Cricket and sports
    "India won cricket match celebration",
    "India lost match disappointment",
    "IPL match discussion",
    "favorite cricket player debate",
    "playing cricket in street",
    "fantasy cricket team discussion",
    "kabaddi or other sports",

    # Relationships and love
    "discussing girlfriend or boyfriend",
    "crush proposal advice",
    "breakup support conversation",
    "relationship advice from friend",
    "talking about arranged marriage",
    "proposing to someone",
    "jealousy in relationship",
    "long distance relationship problems",
    "Valentine's day plans",
    "fighting with girlfriend or boyfriend",

    # Friends and friendship
    "planning to hangout together",
    "roasting each other jokes",
    "missing old school friends",
    "planning a trip together",
    "friend doing something stupid",
    "best friend birthday surprise",
    "friend borrowing money",
    "old memories nostalgia",
    "introducing new friend to group",
    "friend group drama",

    # Emotions and mental health
    "motivating a sad friend",
    "sharing good news excitement",
    "venting about bad day",
    "anxiety before important event",
    "feeling lonely conversation",
    "celebrating achievement together",
    "dealing with failure",
    "overthinking at night",
    "feeling ignored by friends",
    "stress relief conversation",

    # Work and career
    "talking about salary and job",
    "office politics discussion",
    "boss is annoying conversation",
    "job interview preparation",
    "salary hike negotiation",
    "work from home problems",
    "startup idea discussion",
    "freelancing conversation",
    "career confusion advice",
    "switching jobs discussion",

    # Family
    "talking about family pressure",
    "parents asking about marriage",
    "mother scolding situation",
    "family function drama",
    "sibling fight",
    "dad not understanding technology",
    "relatives visit tension",
    "asking parents for money",

    # Technology and social media
    "discussing new phone",
    "phone battery dying",
    "slow internet frustration",
    "Instagram reels addiction",
    "gaming discussion PUBG FreeFire",
    "WhatsApp status discussion",
    "meme sharing conversation",
    "YouTube shorts addiction",
    "online shopping discussion",
    "UPI payment problem",

    # Funny and jokes
    "sharing a funny joke",
    "roasting friend's fashion",
    "embarrassing moment story",
    "funny autocorrect message",
    "drunk texting situation",
    "sending message to wrong person",
    "friend doing cringe thing",
    "funny college memory",

    # Money and finance
    "asking friend to return money",
    "splitting bill after outing",
    "discussing crypto investment",
    "saving money tips",
    "month end broke situation",
    "getting first salary celebration",

    # Health
    "sick and asking for help",
    "gym motivation conversation",
    "dieting gone wrong",
    "hangover recovery chat",
    "doctor visit fear",

    # Miscellaneous
    "asking for life advice",
    "discussing astrology and horoscope",
    "talking about dreams last night",
    "philosophical late night talk",
    "discussing God and religion casually",
    "election and politics casual talk",
    "complaining about electricity bill",
    "house hunting problems",
    "discussing tattoo or piercing",
    "talking about pet dog or cat",
]

PROMPT_TEMPLATE = """Generate 10 Tenglish (Telugu + English code-switching) conversation pairs about: {topic}

Tenglish style examples:
- "em chestunnav bro?" → "nenu fine ga unnanu ra, nuvvu cheppu?"
- "ela unnav ra?" → "baagunnanu bro! chala days aindi kada, em vishayam?"
- "tomorrow exam undi nervous ga unnanu" → "chill bro nuvvu set chesestaav! 💪"
- "yaar movie chala baagundi ra" → "ayyo nenu chudaledu yet! spoiler ivvaku 😭"
- "nenu sad ga unnanu bro" → "ayyooo enduku ra? cheppu enti problem?"

Rules:
1. Mix Telugu words in English script naturally with English
2. Use casual words freely: bro, ra, rey, le, kada, ga, ani, undi, unnav, cheppu, nenu, ela, em, ayyo, arre, chala, baaga, super, ante, okka, mana, nuvvu, meeru, istav, ledhu, ayindi, chesav, vachav, padda, thappa, kooda, kuda, inka, ippudu, appudu, enduku, ekkada, evadu, evari
3. Short messages like real WhatsApp texts
4. Add emojis naturally 😂 😅 🔥 ❤️ 😭 🤣 😊 👍 💪
5. Include slang: da, di, maccha, Anna, akka, sir, boss, yaar
6. Sometimes use ALL CAPS for emphasis like CHALA, SUPER, AYYO
7. No formal Telugu script, no full English sentences only

Return ONLY a JSON array, no other text:
[
  {{"instruction": "message here", "output": "reply here"}},
  {{"instruction": "message here", "output": "reply here"}}
]"""

all_pairs = []
failed = []

print(f"Generating Tenglish dataset for {len(TOPICS)} topics...")
print(f"Expected: ~{len(TOPICS) * 10} pairs total")
print("=" * 60)

for i, topic in enumerate(TOPICS):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=PROMPT_TEMPLATE.format(topic=topic),
        )

        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        pairs = json.loads(text)
        # Filter quality
        pairs = [p for p in pairs if len(p.get('instruction','')) > 5 and len(p.get('output','')) > 5]
        all_pairs.extend(pairs)
        print(f"✅ {i+1}/{len(TOPICS)} '{topic}': {len(pairs)} pairs (total: {len(all_pairs)})")

        # Save progress every 10 topics
        if (i + 1) % 10 == 0:
            with open("tenglish_synthetic.json", "w", encoding="utf-8") as f:
                json.dump(all_pairs, f, ensure_ascii=False, indent=2)
            print(f"  💾 Progress saved: {len(all_pairs)} pairs")

        time.sleep(2)

    except Exception as e:
        print(f"❌ '{topic}': {str(e)[:80]}")
        failed.append(topic)
        time.sleep(5)

# Final save
with open("tenglish_synthetic.json", "w", encoding="utf-8") as f:
    json.dump(all_pairs, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print(f"✅ DONE! Total pairs: {len(all_pairs)}")
print(f"❌ Failed topics: {len(failed)}")
print(f"📁 Saved to: tenglish_synthetic.json")
print("\nSample pairs:")
for p in all_pairs[:5]:
    print(f"  Q: {p['instruction']}")
    print(f"  A: {p['output']}")
    print()