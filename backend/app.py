import os
import shutil
import pickle
import json
import requests

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS

from backend.context_manager import SessionContextManager
from backend.database import create_table, save_chat, get_chat_history
from backend.nlp_preprocessing import preprocess_text


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
INTENTS_PATH = os.path.join(BASE_DIR, "data", "intents.json")
AUDIO_DIR = os.path.join(BASE_DIR, "audio_temp")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Context-Aware Smart Communication Assistant",
    description="Context-aware multilingual communication assistant for regional languages.",
    version="1.0.0"
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

os.makedirs(AUDIO_DIR, exist_ok=True)

create_table()


# ============================================================
# SARVAM API KEY
# ============================================================

SARVAM_API_KEY = "YOUR_SARVAM_API_KEY_HERE"


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: str = "en"


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_speech(
    audio_path: str,
    lang_code: str = "kn-IN"
) -> str:

    # Preview fallback when Sarvam API key is not configured
    if SARVAM_API_KEY == "YOUR_SARVAM_API_KEY_HERE":
        return "ನಮಸ್ಕಾರ"

    url = "https://api.sarvam.ai/speech-to-text"

    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }

    try:

        with open(audio_path, "rb") as f:

            files = {
                "file": f
            }

            data = {
                "model": "saaras-v3",
                "language_code": lang_code
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

            return result.get("transcript", "")

        print(
            "Sarvam API Error:",
            response.status_code,
            response.text
        )

        return ""

    except Exception as e:

        print("Speech-to-text error:", e)

        return ""


# ============================================================
# INTENT PREDICTION
# ============================================================

def predict_intent(
    text: str,
    language: str = "en"
):

    if not os.path.exists(MODEL_PATH):

        return (
            "fallback",
            "Sorry, the chatbot model is not available."
        )

    try:

        # ----------------------------------------------------
        # Load trained model
        # ----------------------------------------------------

        with open(MODEL_PATH, "rb") as f:

            vectorizer, classifier = pickle.load(f)

        # ----------------------------------------------------
        # Load intents
        # ----------------------------------------------------

        with open(
            INTENTS_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        # ----------------------------------------------------
        # Same preprocessing used during training
        # ----------------------------------------------------

        processed_text = preprocess_text(
            text,
            language
        )

        # ----------------------------------------------------
        # TF-IDF vector
        # ----------------------------------------------------

        X_vec = vectorizer.transform(
            [processed_text]
        )

        # ----------------------------------------------------
        # Predict intent
        # ----------------------------------------------------

        predicted_tag = classifier.predict(
            X_vec
        )[0]

        # ----------------------------------------------------
        # Find matching response
        # ----------------------------------------------------

        for intent in data["intents"]:

            if intent["tag"] == predicted_tag:

                responses = intent.get(
                    "responses",
                    {}
                )

                language_responses = responses.get(
                    language,
                    responses.get("en", [])
                )

                if language_responses:

                    return (
                        predicted_tag,
                        language_responses[0]
                    )

        return (
            predicted_tag,
            "I understood your query, but I do not have a suitable response yet."
        )

    except Exception as e:

        print("Intent prediction error:", e)

        return (
            "fallback",
            "Sorry, I was unable to process your query."
        )


# ============================================================
# ROOT API
# ============================================================

@app.get("/")
def read_root():

    return {
        "status": "Active",
        "message": "Regional Assistant API Operational"
    }


# ============================================================
# CONTEXT-AWARE FOLLOW-UP DETECTION
# ============================================================

def is_follow_up_question(message: str) -> bool:

    message_lower = message.lower().strip()

    english_phrases = [

        # ----------------------------------------------------
        # English pronouns
        # ----------------------------------------------------

        "it",
        "its",
        "it's",
        "this",
        "that",
        "these",
        "those",

        # ----------------------------------------------------
        # English - more information
        # ----------------------------------------------------

        "tell me more",
        "tell me more about it",
        "tell me more about this",
        "more about it",
        "more about this",
        "explain more",
        "explain it",
        "explain this",
        "what about it",
        "what about this",

        # ----------------------------------------------------
        # English - applications
        # ----------------------------------------------------

        "application",
        "applications",
        "what are its applications",
        "what is its application",
        "what are the applications",
        "what are its uses",
        "what is it used for",
        "what is this used for",

        # ----------------------------------------------------
        # English - usage
        # ----------------------------------------------------

        "where is it used",
        "where is this used",
        "where is that used",
        "how is it used",
        "how is this used",
        "where can it be used",
        "which field",
        "which fields",
        "which field is it used",
        "which fields use it",
        "where python is used",
        "where is python used"
    ]
        # ----------------------------------------------------
        # Kannada - applications / usage
        # ----------------------------------------------------

    kannada_phrases =[
        "ಇದರ ಉಪಯೋಗಗಳು ಯಾವುವು",
        "ಇದರ ಉಪಯೋಗವೇನು",
        "ಇದರ ಬಳಕೆ ಏನು",
        "ಇದನ್ನು ಎಲ್ಲಿ ಬಳಸುತ್ತಾರೆ",
        "ಇದನ್ನು ಎಲ್ಲಿ ಬಳಸಲಾಗುತ್ತದೆ",
        "ಇದು ಎಲ್ಲಿ ಉಪಯೋಗವಾಗುತ್ತದೆ",
        "ಇದರ ಅಪ್ಲಿಕೇಶನ್‌ಗಳು ಯಾವುವು",
        "ಇದರ ಅಪ್ಲಿಕೇಶನ್ ಯಾವುದು",
        "ಇದರ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ಹೇಳಿ",
        "ಇದರ ಬಗ್ಗೆ ಹೇಳಿ",
        "ಇದರ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು",
        "ಇದರ ಬಳಕೆಗಳು ಯಾವುವು",
        "ಯಾವ ಕ್ಷೇತ್ರಗಳಲ್ಲಿ ಬಳಸುತ್ತಾರೆ",
        "ಯಾವ ಕ್ಷೇತ್ರಗಳಲ್ಲಿ ಬಳಸಲಾಗುತ್ತದೆ",
        "ಇದನ್ನು ಯಾವ ಕ್ಷೇತ್ರಗಳಲ್ಲಿ ಬಳಸುತ್ತಾರೆ"
    ]

        # ----------------------------------------------------
        # Tulu - common follow-up words / phrases
        # ----------------------------------------------------

    tulu_phrases = [
        "Idu yava upayogolu",
        "Idu yava upayogolu?",
        "Idu yava fieldd use malpodu",
        "Idu yava fieldd use malpodu?",
        "Idu yava fieldd use malpuver",
        "Idu yava fieldd use malpuver?",
        "Idu yelli use malpodu",
        "Idu yelli use malpodu?",
        "Idu yava kshetrad use malpodu",
        "Idu yava kshetrad use malpodu?",
        "Idu yava reeti use malpodu",
        "Idu yava reeti use malpodu?",
        "Idu yenk use malpodu",
        "Idu yenk use malpodu?",
        "Idu yava upayog",
        "Idu yava upayoga",
        "Idu yava prayojana",
        "Idu yava field",
        "Yava fieldd use malpodu",
        "Yava fieldd use malpuver",
        "Yelli use malpodu",
        "Idu bagge matte pand",
        "Idu bagge pand",
        "Idu bagge innashtu pand",
        "Matte pand",
        "Innashtu pand"
    ]
        # ----------------------------------------------------
        # Konkani - common follow-up words / phrases
        # ----------------------------------------------------

    konkani_phrases = [
        "kitem upyog",
        "kitem use",
        "kashi vaportat",
        "khoim vaportat",
        "khoim use kortat",
        "kitem applications",
        "applications"
    ]

    # --------------------------------------------------------
    # Exact / phrase matching
    # --------------------------------------------------------

    all_phrases = (
        english_phrases
        + kannada_phrases
        + tulu_phrases
        + konkani_phrases
    )

    for phrase in all_phrases:

        if phrase in message_lower:
            return True

    return False


# ============================================================
# CONTEXT-AWARE RESPONSE
# ============================================================

def get_contextual_response(
    message: str,
    previous_context: dict,
    predicted_intent: str,
    language: str
):

    last_intent = previous_context.get(
        "last_intent"
    )

    message_lower = message.lower().strip()

    # ========================================================
    # TECHNOLOGY CONTEXT
    # ========================================================

    if (
        last_intent == "technology"
        and is_follow_up_question(message)
    ):

        responses = {

            # =================================================
            # ENGLISH
            # =================================================

            "en": {

                "applications":
                    "Python is widely used in web development, data analysis, artificial intelligence, machine learning, automation, and scientific computing.",

                "fields":
                    "Python is commonly used in data science, artificial intelligence, machine learning, web development, automation, and scientific research.",

                "default":
                    "Python is widely used in areas such as data science, artificial intelligence, machine learning, web development, and automation."
            },

            # =================================================
            # KANNADA
            # =================================================

            "kn": {

                "applications":
                    "Python ಅನ್ನು ವೆಬ್ ಡೆವಲಪ್‌ಮೆಂಟ್, ಡೇಟಾ ಅನಾಲಿಸಿಸ್, ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ, ಮೆಷಿನ್ ಲರ್ನಿಂಗ್, ಆಟೊಮೇಷನ್ ಮತ್ತು ವೈಜ್ಞಾನಿಕ ಗಣಕಯಂತ್ರಗಳಲ್ಲಿ ಬಳಸಲಾಗುತ್ತದೆ.",

                "fields":
                    "Python ಅನ್ನು ಡೇಟಾ ಸೈನ್ಸ್, ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ, ಮೆಷಿನ್ ಲರ್ನಿಂಗ್, ವೆಬ್ ಡೆವಲಪ್‌ಮೆಂಟ್, ಆಟೊಮೇಷನ್ ಮತ್ತು ವೈಜ್ಞಾನಿಕ ಸಂಶೋಧನೆಗಳಲ್ಲಿ ಬಳಸಲಾಗುತ್ತದೆ.",

                "default":
                    "Python ಅನ್ನು ಡೇಟಾ ಸೈನ್ಸ್, ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ, ಮೆಷಿನ್ ಲರ್ನಿಂಗ್, ವೆಬ್ ಡೆವಲಪ್‌ಮೆಂಟ್ ಮತ್ತು ಆಟೊಮೇಷನ್ ಕ್ಷೇತ್ರಗಳಲ್ಲಿ ವ್ಯಾಪಕವಾಗಿ ಬಳಸಲಾಗುತ್ತದೆ."
            },

            # =================================================
            # TULU
            # =================================================

            "tcy": {

                "applications":
                    "Python web development, data analysis, artificial intelligence, machine learning, automation mattu scientific computingd use malpodu.",

                "fields":
                    "Python data science, artificial intelligence, machine learning, web development, automation mattu scientific researchd use malpodu.",

                "default":
                    "Python data science, AI, machine learning, web development mattu automation fieldsd use malpodu."
            },

            # =================================================
            # KONKANI
            # =================================================

            "kok": {

                "applications":
                    "Python web development, data analysis, artificial intelligence, machine learning, automation ani scientific computingant vaportat.",

                "fields":
                    "Python data science, artificial intelligence, machine learning, web development, automation ani scientific researchant vaportat.",

                "default":
                    "Python data science, artificial intelligence, machine learning, web development ani automationant vaportat."
            }
        }

        # ----------------------------------------------------
        # Select language
        # ----------------------------------------------------

        language_data = responses.get(
            language,
            responses["en"]
        )

        # ====================================================
        # APPLICATIONS / USE
        # ====================================================

        if (
            "application" in message_lower
            or "applications" in message_lower
            or "ಉಪಯೋಗ" in message_lower
            or "ಬಳಕೆ" in message_lower
            or "ಅಪ್ಲಿಕೇಶನ್" in message_lower
            or "use" in message_lower
            or "uses" in message_lower
            or "upyog" in message_lower
            or "upayoga" in message_lower
            or "vaportug" in message_lower
            or "use malpodu" in message_lower
            or "prayojana" in message_lower
        ):

            return language_data["applications"]

        # ====================================================
        # FIELDS / WHERE USED
        # ====================================================

        if (
            "which field" in message_lower
            or "which fields" in message_lower
            or "where is it used" in message_lower
            or "where is python used" in message_lower
            or "which fields use it" in message_lower
            or "where can it be used" in message_lower
            or "ಯಾವ ಕ್ಷೇತ್ರ" in message_lower
            or "ಎಲ್ಲಿ ಬಳಸ" in message_lower
            or "khoim" in message_lower
            or "ell use" in message_lower
            or "ov field" in message_lower
            or "ov kshetrad" in message_lower
        ):

            return language_data["fields"]

        # ====================================================
        # GENERAL FOLLOW-UP
        # ====================================================

        return language_data["default"]

    return None


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
            "message": "Please enter a message."
        }

    # ========================================================
    # GET PREVIOUS CONTEXT
    # ========================================================

    current_context = context_store.get_context(
        user_id
    )

    # ========================================================
    # PREDICT INTENT
    # ========================================================

    predicted_intent, response_text = predict_intent(
        message,
        language
    )

    # ========================================================
    # CONTEXT-AWARE RESPONSE
    #
    # IMPORTANT:
    # Previous context is checked BEFORE updating it.
    # ========================================================

    contextual_response = get_contextual_response(
        message=message,
        previous_context=current_context,
        predicted_intent=predicted_intent,
        language=language
    )

    if contextual_response is not None:

        response_text = contextual_response

        # ----------------------------------------------------
        # IMPORTANT:
        # Keep the previous subject intent.
        #
        # Example:
        #
        # Python ಎಂದರೇನು?        -> technology
        # ಇದರ ಉಪಯೋಗಗಳು ಯಾವುವು?  -> technology
        #
        # This prevents the ML model from changing the
        # context to farewell/general intent.
        # ----------------------------------------------------

        if current_context.get("last_intent"):

            predicted_intent = current_context.get(
                "last_intent"
            )

    # ========================================================
    # UPDATE CONTEXT
    # ========================================================

    context_store.update_context(
        user_id,
        predicted_intent
    )

    # ========================================================
    # SAVE CHAT
    # ========================================================

    save_chat(
        user_id=user_id,
        user_message=message,
        bot_response=response_text,
        language=language,
        intent=predicted_intent
    )

    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return {

        "success": True,

        "user_id": user_id,

        "message": message,

        "language": language,

        "intent": predicted_intent,

        "response": response_text,

        "previous_context": current_context
    }


# ============================================================
# LANGUAGES API
# ============================================================

@app.get("/languages")
def get_languages():

    return {

        "languages": [

            {
                "name": "English",
                "code": "en"
            },

            {
                "name": "Kannada",
                "code": "kn"
            },

            {
                "name": "Tulu",
                "code": "tcy"
            },

            {
                "name": "Konkani",
                "code": "kok"
            }

        ]
    }


# ============================================================
# HISTORY API
# ============================================================

@app.get("/history/{user_id}")
def get_history(user_id: str):

    history = get_chat_history(
        user_id
    )

    return {

        "user_id": user_id,

        "history": history
    }


# ============================================================
# VOICE PROCESSING API
# ============================================================

@app.post("/process-voice/")
async def process_voice(

    user_id: str = Form(...),

    language: str = Form("kn-IN"),

    file: UploadFile = File(...)
):

    # ========================================================
    # 1. SAVE INCOMING AUDIO
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
    # 2. SPEECH TO TEXT
    # ========================================================

    transcribed_text = transcribe_speech(
        input_audio_path,
        lang_code=language
    )

    # ========================================================
    # CHECK TRANSCRIPTION
    # ========================================================

    if not transcribed_text.strip():

        return {

            "success": False,

            "message":
                "Speech could not be converted to text."
        }

    # ========================================================
    # 3. GET PREVIOUS CONTEXT
    # ========================================================

    current_context = context_store.get_context(
        user_id
    )

    # ========================================================
    # 4. CONVERT LANGUAGE CODE
    # ========================================================

    language_map = {

        "kn-IN": "kn",

        "tcy-IN": "tcy",

        "kok-IN": "kok",

        "en-IN": "en"
    }

    response_language = language_map.get(
        language,
        language
    )

    # ========================================================
    # 5. PREDICT INTENT
    # ========================================================

    predicted_intent, response_text = predict_intent(
        transcribed_text,
        language=response_language
    )

    # ========================================================
    # 6. CONTEXT-AWARE RESPONSE
    # ========================================================

    contextual_response = get_contextual_response(
        message=transcribed_text,
        previous_context=current_context,
        predicted_intent=predicted_intent,
        language=response_language
    )

    if contextual_response is not None:

        response_text = contextual_response

        # Keep previous context intent

        if current_context.get("last_intent"):

            predicted_intent = current_context.get(
                "last_intent"
            )

    # ========================================================
    # 7. UPDATE CONTEXT
    # ========================================================

    context_store.update_context(
        user_id,
        predicted_intent
    )

    # ========================================================
    # 8. SAVE VOICE CONVERSATION
    # ========================================================

    save_chat(
        user_id=user_id,
        user_message=transcribed_text,
        bot_response=response_text,
        language=response_language,
        intent=predicted_intent
    )

    # ========================================================
    # 9. TEXT TO SPEECH
    # ========================================================

    output_audio_path = os.path.join(
        AUDIO_DIR,
        f"output_{user_id}.mp3"
    )

    # ========================================================
    # gTTS LANGUAGE SUPPORT
    # ========================================================

    tts_language_map = {

        "en": "en",

        "en-IN": "en",

        "kn": "kn",

        "kn-IN": "kn",

        # gTTS does not directly support Tulu
        "tcy": "en",

        "tcy-IN": "en",

        # gTTS does not directly support Konkani
        "kok": "en",

        "kok-IN": "en"
    }

    tts_lang = tts_language_map.get(
        language,
        "en"
    )

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

            "success": True,

            "user_id": user_id,

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
    # 10. RETURN RESPONSE
    # ========================================================

    return {

        "success": True,

        "user_id": user_id,

        "user_query_text":
            transcribed_text,

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

@app.get("/get-audio/{user_id}")
def get_audio(user_id: str):

    audio_path = os.path.join(
        AUDIO_DIR,
        f"output_{user_id}.mp3"
    )

    if os.path.exists(audio_path):

        return FileResponse(
            audio_path,
            media_type="audio/mpeg"
        )

    return {

        "error":
            "Audio file not found"
    }