import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key found:", bool(api_key))

if not api_key:
    print("❌ GEMINI_API_KEY is missing from .env")
    exit()

try:
    client = genai.Client(api_key=api_key)

    print("Connecting to Gemini...")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Say hello and explain what artificial intelligence is in one sentence."
    )

    print("\n✅ Gemini response:")
    print(response.text)

except Exception as e:
    print("\n❌ Gemini error:")
    print(type(e).__name__)
    print(e)