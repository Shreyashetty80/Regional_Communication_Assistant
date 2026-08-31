import os
from dotenv import load_dotenv
from google import genai

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if GEMINI_API_KEY:

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print("✅ Gemini client initialized.")

    except Exception as e:

        print("❌ Gemini client initialization failed:")
        print(e)

else:

    print("⚠️ GEMINI_API_KEY not found in .env")


# ============================================================
# PROJECT KNOWLEDGE
# ============================================================

PROJECT_KNOWLEDGE = """
PROJECT INFORMATION

Project Name:
Context-Aware Smart Communication Assistant for Regional Languages

College:
Canara Engineering College, Mangaluru, India

Department:
Information Science and Engineering

Project Type:
AI / NLP / Conversational AI / Voice-Enabled Assistant

Supported Languages:
1. English
2. Kannada
3. Tulu
4. Konkani

Main Features:
1. AI Question Answering
2. Context-aware conversation
3. English ↔ Kannada ↔ Tulu ↔ Konkani translation
4. Speech-to-text
5. Text-to-speech
6. Multilingual chat
7. Code-mixed language support
8. Project and college-specific knowledge
9. Conversation history

Technology:
- Python
- FastAPI
- React.js
- Natural Language Processing
- TF-IDF
- Multinomial Naive Bayes
- Speech-to-Text
- Text-to-Speech
- Gemini API
- SQLite/database-based conversation history

Backend:
FastAPI

Speech-to-Text:
Sarvam AI

Text-to-Speech:
gTTS

Context Management:
A session-based context manager maintains recent conversation information
and helps the assistant understand follow-up questions.

Database:
Conversation history is stored so previous conversations can be retrieved.

Student Role:
Shreya Shetty is responsible for Backend Development and API Integration.

Backend Responsibilities:
- FastAPI backend development
- API development
- Frontend-backend integration
- NLP/backend integration
- Voice API integration
- Database integration
- Project integration and debugging
"""


# ============================================================
# SYSTEM INSTRUCTIONS
# ============================================================

SYSTEM_INSTRUCTIONS = """
You are the AI assistant inside a Context-Aware Smart Communication
Assistant for Regional Languages.

Your job is to behave like a helpful conversational AI assistant,
not like a simple fixed-response chatbot.

IMPORTANT RULES:

1. Answer general questions naturally and helpfully.

2. Understand follow-up questions using the conversation context.

Example:

User:
What is Python?

Assistant:
Python is a programming language...

User:
Where is it used?

The assistant must understand that "it" means Python.

3. Support:
English
Kannada
Tulu
Konkani

4. LANGUAGE RULE:

Always answer in the language requested by the user.

If the user asks in Kannada, answer in Kannada.

If the user asks in English, answer in English.

If the user asks in Tulu, answer in Tulu.

If the user asks in Konkani, answer in Konkani.

5. NATIVE SCRIPT:

For Kannada, use Kannada script.

For Tulu, prefer Tulu written in Kannada script when appropriate,
instead of unnecessary English/Roman transliteration.

For Konkani, prefer native Devanagari script when appropriate,
instead of unnecessary Roman transliteration.

Do NOT automatically convert regional-language responses into English.

6. CODE-MIXED INPUT:

Users may mix English with Kannada, Tulu, or Konkani.

Understand the meaning and respond naturally in the requested language.

Example:
"Python yelli use agatte?"

Understand it as:
"Where is Python used?"

7. TRANSLATION:

If the user explicitly asks to translate something, translate the
meaning accurately.

Examples:

"Translate hello to Kannada"

"Translate ನಮಸ್ಕಾರ to English"

"English to Tulu: How are you?"

"Konkani to Kannada: ..."

Return the translation clearly.

Do not add unnecessary explanation unless requested.

8. PROJECT KNOWLEDGE:

Use the provided project information when the user asks about:
- the project
- college
- department
- technologies
- architecture
- features
- team roles
- backend
- APIs
- NLP
- speech processing
- context management
- database
- your role

9. IMPORTANT:

Do NOT say:
"I only know information from my dataset."

For normal/general questions, answer using your general knowledge.

For project-specific questions, use the project information provided
to you.

10. If a question is ambiguous, ask a short clarification question.

11. Give useful answers rather than extremely short answers.

12. Do not invent specific college facts that are not provided.

13. Maintain a friendly, natural conversational style.

14. When the user asks technical questions, explain clearly with examples
when useful.

15. If the user asks "what can you do?", explain the major capabilities
of this assistant.
"""


# ============================================================
# GEMINI RESPONSE FUNCTION
# ============================================================

def generate_gemini_response(
    message: str,
    language: str = "en",
    conversation_history=None
):

    if client is None:

        return None

    if conversation_history is None:

        conversation_history = []

    # ========================================================
    # LANGUAGE NAMES
    # ========================================================

    language_names = {

        "en": "English",

        "kn": "Kannada",

        "tcy": "Tulu",

        "kok": "Konkani"
    }

    language_name = language_names.get(
        language,
        language
    )

    # ========================================================
    # BUILD CONVERSATION CONTEXT
    # ========================================================

    history_text = ""

    if conversation_history:

        recent_history = conversation_history[-10:]

        history_text = "\n\nRECENT CONVERSATION:\n"

        for item in recent_history:

            if isinstance(item, dict):

                user_message = item.get(
                    "user",
                    ""
                )

                assistant_message = item.get(
                    "assistant",
                    ""
                )

                history_text += (
                    f"User: {user_message}\n"
                    f"Assistant: {assistant_message}\n"
                )

            elif isinstance(item, str):

                history_text += (
                    f"{item}\n"
                )

    # ========================================================
    # COMPLETE PROMPT
    # ========================================================

    prompt = f"""
{SYSTEM_INSTRUCTIONS}

{PROJECT_KNOWLEDGE}

CURRENT RESPONSE LANGUAGE:
{language_name}

{history_text}

CURRENT USER MESSAGE:
{message}

Answer the user's message now.

Remember:
- Use the requested language.
- Preserve native script for regional languages.
- Use conversation context when relevant.
- If this is a translation request, perform translation.
- If this is a general question, answer naturally.
- If this is about the project, use the project information above.
"""

    try:

        response = client.models.generate_content(

            model="gemini-3.5-flash-lite",

            contents=prompt
        )

        if response and response.text:

            return response.text.strip()

        return None

    except Exception as e:

        print(
            "❌ Gemini response error:",
            type(e).__name__,
            e
        )

        return None