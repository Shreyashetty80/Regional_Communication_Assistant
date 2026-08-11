import os
import shutil
import pickle
import json
import requests

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS

from context_manager import SessionContextManager


# ---------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------

app = FastAPI(
    title="Context-Aware Smart Communication Assistant"
)

context_store = SessionContextManager()

os.makedirs("audio_temp", exist_ok=True)


# ---------------------------------------------------
# TEMPORARY CHAT HISTORY
# ---------------------------------------------------

chat_history = {}


# ---------------------------------------------------
# SARVAM API KEY
# ---------------------------------------------------

SARVAM_API_KEY = "YOUR_SARVAM_API_KEY_HERE"


# ---------------------------------------------------
# REQUEST MODEL FOR /chat
# ---------------------------------------------------

class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: str = "en"


# ---------------------------------------------------
# SPEECH TO TEXT
# ---------------------------------------------------

def transcribe_speech(
    audio_path: str,
    lang_code: str = "kn-IN"
) -> str:

    # Preview fallback when API key is not configured
    if SARVAM_API_KEY == "YOUR_SARVAM_API_KEY_HERE":
        return "ನಮಸ್ಕಾರ"

    url = "https://api.sarvam.ai/speech-to-text"

    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }

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
            data=data
        )

    if response.status_code == 200:
        return response.json().get("transcript", "")

    return ""


# ---------------------------------------------------
# INTENT PREDICTION
# ---------------------------------------------------

def predict_intent(text: str, language: str = "en"):

    if not os.path.exists("model.pkl"):
        return (
            "fallback",
            "Sorry, the chatbot model is not available."
        )

    # Load trained model
    with open("model.pkl", "rb") as f:
        vectorizer, classifier = pickle.load(f)

    # Load intents
    with open(
        "data/intents.json",
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    # Convert input into TF-IDF vector
    X_vec = vectorizer.transform([text])

    # Predict intent
    predicted_tag = classifier.predict(X_vec)[0]

    # Find matching response
    for intent in data["intents"]:

        if intent["tag"] == predicted_tag:

            responses = intent.get("responses", {})

            language_responses = responses.get(
                language,
                responses.get("en", [])
            )

            if language_responses:
                return predicted_tag, language_responses[0]

    return (
        "fallback",
        "I didn't quite understand that query."
    )
# ---------------------------------------------------
# ROOT API
# ---------------------------------------------------

@app.get("/")
def read_root():

    return {
        "status": "Active",
        "message": "Regional Assistant API Operational"
    }


# ---------------------------------------------------
# CHAT API
# ---------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    user_id = request.user_id
    message = request.message
    language = request.language

    # Check empty message
    if not message.strip():

        return {
            "success": False,
            "message": "Please enter a message."
        }

    # Get previous context
    current_context = context_store.get_context(user_id)

    # Predict intent
    predicted_intent, response_text = predict_intent(
    message,
    language
    )

    # Update context
    context_store.update_context(
        user_id,
        predicted_intent
    )

    # Create history for user if not available
    if user_id not in chat_history:
        chat_history[user_id] = []

    # Store conversation
    chat_history[user_id].append({

        "user_message": message,

        "bot_response": response_text,

        "language": language,

        "intent": predicted_intent
    })

    # Return response
    return {

        "success": True,

        "user_id": user_id,

        "message": message,

        "language": language,

        "intent": predicted_intent,

        "response": response_text,

        "previous_context": current_context
    }


# ---------------------------------------------------
# LANGUAGES API
# ---------------------------------------------------

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


# ---------------------------------------------------
# HISTORY API
# ---------------------------------------------------

@app.get("/history/{user_id}")
def get_history(user_id: str):

    return {

        "user_id": user_id,

        "history": chat_history.get(
            user_id,
            []
        )
    }


# ---------------------------------------------------
# VOICE PROCESSING API
# ---------------------------------------------------

@app.post("/process-voice/")
async def process_voice(

    user_id: str = Form(...),

    language: str = Form("kn-IN"),

    file: UploadFile = File(...)
):

    # 1. Save incoming audio

    input_audio_path = (
        f"audio_temp/input_{user_id}.wav"
    )

    with open(
        input_audio_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # 2. Speech to Text

    transcribed_text = transcribe_speech(
        input_audio_path,
        lang_code=language
    )

    # 3. Get current context

    current_context = context_store.get_context(
        user_id
    )

    # 4. Predict intent

    predicted_intent, response_text = predict_intent(
        transcribed_text
    )

    # 5. Update context

    context_store.update_context(
        user_id,
        predicted_intent
    )

    # 6. Save conversation

    if user_id not in chat_history:

        chat_history[user_id] = []

    chat_history[user_id].append({

        "user_message": transcribed_text,

        "bot_response": response_text,

        "language": language,

        "intent": predicted_intent
    })

    # 7. Text to Speech

    output_audio_path = (
        f"audio_temp/output_{user_id}.mp3"
    )

    tts = gTTS(
        text=response_text,
        lang="kn"
    )

    tts.save(output_audio_path)

    # 8. Return response

    return {

        "success": True,

        "user_id": user_id,

        "user_query_text": transcribed_text,

        "intent": predicted_intent,

        "response_text": response_text,

        "audio_url": f"/get-audio/{user_id}"

    }


# ---------------------------------------------------
# GET AUDIO
# ---------------------------------------------------

@app.get("/get-audio/{user_id}")
def get_audio(user_id: str):

    audio_path = (
        f"audio_temp/output_{user_id}.mp3"
    )

    if os.path.exists(audio_path):

        return FileResponse(
            audio_path,
            media_type="audio/mp3"
        )

    return {
        "error": "Audio file not found"
    }