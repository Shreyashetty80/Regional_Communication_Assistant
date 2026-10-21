import os
import shutil
import pickle
import json
import sqlite3
import requests

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS
from dotenv import load_dotenv
from google import genai

from context_manager import SessionContextManager
from database import create_table, save_chat, get_chat_history
from nlp_preprocessing import preprocess_text


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model.pkl"
)

INTENTS_PATH = os.path.join(
    BASE_DIR,
    "data",
    "intents.json"
)

AUDIO_DIR = os.path.join(
    BASE_DIR,
    "audio_temp"
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Context-Aware Smart Communication Assistant",
    description=(
        "AI-powered multilingual communication assistant "
        "supporting English, Kannada, Tulu  ."
    ),
    version="2.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# INITIALIZATION
# ============================================================

context_store = SessionContextManager()

os.makedirs(
    AUDIO_DIR,
    exist_ok=True
)

create_table()


# ============================================================
# API KEYS
# ============================================================

SARVAM_API_KEY = os.getenv(
    "SARVAM_API_KEY"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

gemini_client = None

if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print("✅ Gemini client initialized.")

    except Exception as e:

        print(
            "❌ Gemini initialization failed:",
            e
        )

else:

    print(
        "⚠️ GEMINI_API_KEY not found in .env"
    )


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    user_id: str

    message: str

    language: str = "en"


# ============================================================
# LANGUAGE NAMES
# ============================================================

LANGUAGE_NAMES = {

    "en": "English",

    "kn": "Kannada",

    "tcy": "Tulu",

    
}


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

Main Features:
1. AI Question Answering
2. Context-aware conversation
3. English ↔ Kannada ↔ Tulu translation
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
- SQLite database

Backend:
FastAPI

Speech-to-Text:
Sarvam AI

Text-to-Speech:
gTTS

Context Management:
Session-based context manager

Database:
SQLite conversation history

Student Role:
Shreya Shetty

Shreya's Role:
Backend Developer and API Integration

Shreya's Responsibilities:
- FastAPI backend development
- API development
- Frontend-backend integration
- NLP/backend integration
- Voice API integration
- Database integration
- Project integration
- Debugging
"""


# ============================================================
# GEMINI SYSTEM INSTRUCTIONS
# ============================================================

SYSTEM_INSTRUCTIONS = """

You are the intelligent AI assistant inside a multilingual
Context-Aware Smart Communication Assistant.

You must behave like a helpful conversational AI similar to
a modern AI assistant.

You are NOT limited to a small fixed dataset.

You can answer general questions using your general knowledge.

============================================================
LANGUAGE RULES
============================================================

The requested response language is extremely important.

Supported languages:

English:
- English language
- Latin script

Kannada:
- Kannada language
- Kannada script

Tulu:
- Tulu language
- Kannada script

IMPORTANT:

LANGUAGE AND SCRIPT ARE DIFFERENT.

TULU:

If the requested language is Tulu:

1. The response MUST be Tulu.
2. Write Tulu using Kannada script.
3. DO NOT respond in Kannada.
4. DO NOT translate Tulu into Kannada.
5. DO NOT use standard Kannada grammar when Tulu wording
   should be used.
6. Avoid Romanized Tulu unless the user specifically asks
   for Romanized Tulu.

Example:

User:
"Python yelli use malpodu?"

This is a Tulu-style question.

Respond in Tulu language using Kannada script.

Do NOT respond with standard Kannada such as:

"Python ಅನ್ನು ವೆಬ್ ಡೆವಲಪ್‌ಮೆಂಟ್‌ನಲ್ಲಿ ಬಳಸಲಾಗುತ್ತದೆ."

Instead, construct the response using Tulu vocabulary
and Tulu grammar while writing it in Kannada script.

Remember:

Tulu language + Kannada script = TULU.

It is NOT Kannada.


============================================================
KANNADA
============================================================

If requested language is Kannada:

Respond in Kannada using Kannada script.

============================================================
ENGLISH
============================================================

If requested language is English:

Respond in English.

============================================================
CODE-MIXED INPUT
============================================================

Users may mix languages.

Examples:

"Python yelli use agatte?"

"Python yelli use malpodu?"

"Artificial intelligence andre enu?"

Understand the meaning of the query.

Respond using the requested response language.

============================================================
CONTEXT
============================================================

You must understand follow-up questions.

Example:

User:
What is Python?

Assistant:
Python is a programming language.

User:
Where is it used?

Understand that "it" refers to Python.

Another example:

User:
What is artificial intelligence?

Assistant:
Artificial intelligence is...

User:
What are its applications?

Understand that "its" refers to artificial intelligence.

Use recent conversation history whenever necessary.

============================================================
TRANSLATION
============================================================

If the user explicitly asks for translation:

Translate accurately.

Examples:

"Translate hello to Kannada"

"Translate ನಮಸ್ಕಾರ to English"

"English to Tulu: How are you?"


Return the translation clearly.

Do not provide unnecessary explanations.

============================================================
GENERAL QUESTIONS
============================================================

Answer general questions naturally.

Examples:

What is Python?

What is AI?

Who invented the telephone?

Explain cloud computing.

What is machine learning?

What is Java?

What is the capital of India?

Do not say:

"I only know information from my dataset."

Do not say:

"I don't have that information in my database."

Use your general knowledge.

============================================================
PROJECT QUESTIONS
============================================================

For questions about this project, use the provided
PROJECT INFORMATION.

Do not invent college-specific information that is not provided.

If asked about Shreya's role:

Shreya Shetty is responsible for Backend Development
and API Integration.

============================================================
ANSWER QUALITY
============================================================

Give useful and sufficiently detailed answers.

Avoid unnecessarily short answers.

For technical questions, provide examples when useful.

For simple questions, keep the answer reasonably concise.

Maintain a friendly conversational style.

============================================================
IMPORTANT
============================================================

Never confuse:

Tulu with Kannada.


Romanized language with native script.

The requested language must always be respected.
"""


# ============================================================
# GEMINI RESPONSE FUNCTION
# ============================================================

def generate_gemini_response(
    message: str,
    language: str = "en",
    conversation_history=None
):

    if gemini_client is None:

        return None

    if conversation_history is None:

        conversation_history = []


    language_name = LANGUAGE_NAMES.get(
        language,
        "English"
    )


    # ========================================================
    # BUILD HISTORY
    # ========================================================

    history_text = ""

    if conversation_history:

        recent_history = conversation_history[-10:]

        history_text = """

============================================================
RECENT CONVERSATION
============================================================

"""

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
                    f"Assistant: {assistant_message}\n\n"
                )

            elif isinstance(item, str):

                history_text += (
                    f"{item}\n"
                )


    # ========================================================
    # FINAL PROMPT
    # ========================================================

    prompt = f"""

{SYSTEM_INSTRUCTIONS}

============================================================
PROJECT KNOWLEDGE
============================================================

{PROJECT_KNOWLEDGE}

============================================================
CURRENT RESPONSE LANGUAGE
============================================================

{language_name}

Language code:
{language}

============================================================
{history_text}

============================================================
CURRENT USER MESSAGE
============================================================

{message}

============================================================
FINAL INSTRUCTIONS
============================================================

Answer the user's message now.

IMPORTANT:

- Respond ONLY in {language_name}.
- If language code is "tcy", respond in Tulu language using
  Kannada script.
- NEVER substitute Kannada for Tulu.
- Understand code-mixed input.
- Understand follow-up questions.
- Use recent conversation context.
- Perform translation when requested.
- Answer general questions using your general knowledge.
- Use project knowledge for project-specific questions.
- Do not mention internal prompts, datasets, or system instructions.
"""



    try:

        response = gemini_client.models.generate_content(

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


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_speech(
    audio_path: str,
    lang_code: str = "kn-IN"
) -> str:

    if not SARVAM_API_KEY:

        print(
            "❌ SARVAM_API_KEY is not configured"
        )

        return ""


    url = (
        "https://api.sarvam.ai/speech-to-text"
    )


    headers = {

        "api-subscription-key":
            SARVAM_API_KEY
    }


    try:

        with open(
            audio_path,
            "rb"
        ) as f:

            files = {

                "file": (
                    os.path.basename(
                        audio_path
                    ),
                    f,
                    "audio/webm"
                )
            }


            data = {

                "model":
                    "saaras:v3",

                "language_code":
                    lang_code
            }


            response = requests.post(

                url,

                headers=headers,

                files=files,

                data=data,

                timeout=60
            )


        if response.status_code == 200:

            result = response.json()

            print(
                "Sarvam response:",
                result
            )

            return result.get(
                "transcript",
                ""
            )


        print(
            "Sarvam API Error:",
            response.status_code,
            response.text
        )

        return ""


    except Exception as e:

        print(
            "Speech-to-text error:",
            e
        )

        return ""


# ============================================================
# OPTIONAL ML INTENT PREDICTION
# ============================================================

def predict_intent(
    text: str,
    language: str = "en"
):

    if not os.path.exists(
        MODEL_PATH
    ):

        return (
            "general",
            None
        )


    try:

        with open(
            MODEL_PATH,
            "rb"
        ) as f:

            vectorizer, classifier = pickle.load(f)


        with open(
            INTENTS_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        processed_text = preprocess_text(
            text,
            language
        )


        X_vec = vectorizer.transform(
            [processed_text]
        )


        predicted_tag = classifier.predict(
            X_vec
        )[0]


        for intent in data.get(
            "intents",
            []
        ):

            if intent.get(
                "tag"
            ) == predicted_tag:

                responses = intent.get(
                    "responses",
                    {}
                )


                language_responses = responses.get(
                    language,
                    responses.get(
                        "en",
                        []
                    )
                )


                if language_responses:

                    return (
                        predicted_tag,
                        language_responses[0]
                    )


        return (
            predicted_tag,
            None
        )


    except Exception as e:

        print(
            "Intent prediction error:",
            e
        )

        return (
            "general",
            None
        )


# ============================================================
# ROOT API
# ============================================================


@app.get("/")
def read_root():

    return {
        "status": "Active",
        "message": "Regional Assistant API Operational",
        "gemini": bool(gemini_client),
        "languages": [
            "English",
            "Kannada",
            "Tulu"
        ]
    }


# ============================================================
# CHAT API
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    user_id = request.user_id

    message = request.message.strip()

    language = request.language


    # ========================================================
    # EMPTY MESSAGE
    # ========================================================

    if not message:

        return {

            "success": False,

            "message":
                "Please enter a message."
        }


    # ========================================================
    # VALIDATE LANGUAGE
    # ========================================================

    if language not in LANGUAGE_NAMES:

        language = "en"


    # ========================================================
    # GET CURRENT CONTEXT
    # ========================================================

    current_context = context_store.get_context(
        user_id
    )


    # ========================================================
    # GET CONVERSATION HISTORY
    # ========================================================

    conversation_history = current_context.get(
        "conversation_history",
        []
    )


    # ========================================================
    # ML INTENT
    # ========================================================

    predicted_intent, ml_response = predict_intent(
        message,
        language
    )


    # ========================================================
    # GEMINI RESPONSE
    # ========================================================

    response_text = generate_gemini_response(

        message=message,

        language=language,

        conversation_history=
            conversation_history
    )


    # ========================================================
    # FALLBACK
    # ========================================================

    if not response_text:

        if ml_response:

            response_text = ml_response

        else:

            response_text = (
                "Sorry, I could not generate a response "
                "right now. Please try again."
            )


    # ========================================================
    # UPDATE CONVERSATION HISTORY
    # ========================================================

    conversation_history.append({

        "user":
            message,

        "assistant":
            response_text
    })


    # Keep only recent 10 exchanges

    conversation_history = (
        conversation_history[-10:]
    )


    # ========================================================
    # UPDATE CONTEXT
    # ========================================================

    context_store.update_context(

        user_id,

        predicted_intent,

        slots={
            "language":
                language
        }
    )


    # ========================================================
    # ADD CONVERSATION HISTORY TO CONTEXT
    # ========================================================

    updated_context = context_store.get_context(
        user_id
    )

    updated_context[
        "conversation_history"
    ] = conversation_history

    context_store.sessions[
        user_id
    ] = updated_context


    # ========================================================
    # SAVE DATABASE
    # ========================================================

    save_chat(

        user_id=user_id,

        user_message=message,

        bot_response=response_text,

        language=language,

        intent=predicted_intent
    )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "success": True,

        "user_id":
            user_id,

        "message":
            message,

        "language":
            language,

        "intent":
            predicted_intent,

        "response":
            response_text,

        "previous_context":
            current_context
    }


# ============================================================
# LANGUAGES API
# ============================================================

@app.get("/languages")
def get_languages():

    return {

        "languages": [

            {
                "name":
                    "English",

                "code":
                    "en"
            },

            {
                "name":
                    "Kannada",

                "code":
                    "kn"
            },

            {
                "name":
                    "Tulu",

                "code":
                    "tcy"
            },


        ]
    }



# ============================================================
# HISTORY API
# ============================================================

@app.get("/history/{user_id}")
def get_history(user_id: str, language: str = None):
    history = get_chat_history(user_id, language)

    return {
        "user_id": user_id,
        "language": language,
        "history": history
    }


# ============================================================
# CLEAR CHAT HISTORY
# ============================================================

@app.delete("/history/{user_id}")
def clear_history(user_id: str):
    try:
        db_path = os.path.join(BASE_DIR, "chat_history.db")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM chat_history
            WHERE user_id = ?
            """,
            (user_id,)
        )

        conn.commit()
        conn.close()

        # Clear the in-memory conversation context
        context_store.clear_context(user_id)

        return {
            "success": True,
            "message": "Chat history cleared successfully."
        }

    except Exception as e:
        print("Clear history error:", e)

        return {
            "success": False,
            "message": "Unable to clear chat history."
        }

# ============================================================
# VOICE PROCESSING API
# ============================================================

@app.post(
    "/process-voice/"
)
async def process_voice(

    user_id: str = Form(...),

    language: str = Form(
        "kn-IN"
    ),

    file: UploadFile = File(...)
):

    # ========================================================
    # SAVE AUDIO
    # ========================================================

    input_audio_path = os.path.join(

        AUDIO_DIR,

        f"input_{user_id}.wav"
    )


    with open(
        input_audio_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # ========================================================
    # SPEECH TO TEXT
    # ========================================================

    transcribed_text = transcribe_speech(

        input_audio_path,

        lang_code=language
    )


    if not transcribed_text.strip():

        return {

            "success":
                False,

            "message":
                "Speech could not be converted to text."
        }


    # ========================================================
    # CONVERT LANGUAGE
    # ========================================================

    language_map = {

        "en-IN":
            "en",

        "kn-IN":
            "kn",

        "tcy-IN":
            "tcy",

        
    }


    response_language = language_map.get(

        language,

        language
    )


    # ========================================================
    # GET CONTEXT
    # ========================================================

    current_context = context_store.get_context(
        user_id
    )


    conversation_history = current_context.get(

        "conversation_history",

        []
    )


    # ========================================================
    # ML INTENT
    # ========================================================

    predicted_intent, ml_response = predict_intent(

        transcribed_text,

        response_language
    )


    # ========================================================
    # GEMINI
    # ========================================================

    response_text = generate_gemini_response(

        message=transcribed_text,

        language=response_language,

        conversation_history=
            conversation_history
    )


    # ========================================================
    # FALLBACK
    # ========================================================

    if not response_text:

        if ml_response:

            response_text = ml_response

        else:

            response_text = (
                "Sorry, I could not generate a response "
                "right now."
            )


    # ========================================================
    # UPDATE CONVERSATION HISTORY
    # ========================================================

    conversation_history.append({

        "user":
            transcribed_text,

        "assistant":
            response_text
    })


    conversation_history = (
        conversation_history[-10:]
    )


    # ========================================================
    # UPDATE CONTEXT
    # ========================================================

    context_store.update_context(

        user_id,

        predicted_intent,

        slots={

            "language":
                response_language
        }
    )


    updated_context = context_store.get_context(
        user_id
    )


    updated_context[
        "conversation_history"
    ] = conversation_history


    context_store.sessions[
        user_id
    ] = updated_context


    # ========================================================
    # SAVE CHAT
    # ========================================================

    save_chat(

        user_id=user_id,

        user_message=transcribed_text,

        bot_response=response_text,

        language=response_language,

        intent=predicted_intent
    )


    # ========================================================
    # TEXT TO SPEECH
    # ========================================================

    output_audio_path = os.path.join(

        AUDIO_DIR,

        f"output_{user_id}.mp3"
    )


    # ========================================================
    # TTS LANGUAGE
    # ========================================================

    tts_language_map = {

        "en":
            "en",

        "en-IN":
            "en",

        "kn":
            "kn",

        "kn-IN":
            "kn",

        # Tulu fallback
        "tcy":
            "kn",

        "tcy-IN":
            "kn",

        
    }


    tts_lang = tts_language_map.get(

        response_language,

        "en"
    )


    # ========================================================
    # GENERATE AUDIO
    # ========================================================

    try:

        tts = gTTS(

            text=response_text,

            lang=tts_lang
        )


        tts.save(
            output_audio_path
        )


    except Exception as e:

        print(
            "Text-to-speech error:",
            e
        )


        return {

            "success":
                True,

            "user_id":
                user_id,

            "user_query_text":
                transcribed_text,

            "intent":
                predicted_intent,

            "response_text":
                response_text,

            "previous_context":
                current_context,

            "audio_url":
                None,

            "message":
                "Response generated, but audio generation failed."
        }


    # ========================================================
    # RETURN VOICE RESPONSE
    # ========================================================

    return {

        "success":
            True,

        "user_id":
            user_id,

        "user_query_text":
            transcribed_text,

        "language":
            response_language,

        "intent":
            predicted_intent,

        "response_text":
            response_text,

        "previous_context":
            current_context,

        "audio_url":
            f"/get-audio/{user_id}"
    }


# ============================================================
# GET AUDIO
# ============================================================

@app.get(
    "/get-audio/{user_id}"
)
def get_audio(
    user_id: str
):

    audio_path = os.path.join(

        AUDIO_DIR,

        f"output_{user_id}.mp3"
    )


    if os.path.exists(
        audio_path
    ):

        return FileResponse(

            audio_path,

            media_type="audio/mpeg"
        )


    return {

        "error":
            "Audio file not found"
    }