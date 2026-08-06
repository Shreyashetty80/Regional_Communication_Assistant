import os
import shutil
import pickle
import json
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from gtts import gTTS

from context_manager import SessionContextManager

app = FastAPI(title="Context-Aware Smart Communication Assistant")
context_store = SessionContextManager()

os.makedirs("audio_temp", exist_ok=True)

SARVAM_API_KEY = "YOUR_SARVAM_API_KEY_HERE"  # Free API Key from https://dashboard.sarvam.ai/

# Helper: Real Speech-to-Text via Sarvam AI
def transcribe_speech(audio_path: str, lang_code: str = "kn-IN") -> str:
    if SARVAM_API_KEY == "YOUR_SARVAM_API_KEY_HERE":
        return "ನಮಸ್ಕಾರ"  # Fallback preview text if key isn't added yet
    
    url = "https://api.sarvam.ai/speech-to-text"
    headers = {"api-subscription-key": SARVAM_API_KEY}
    
    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {"model": "saaras-v3", "language_code": lang_code}
        response = requests.post(url, headers=headers, files=files, data=data)
        
    if response.status_code == 200:
        return response.json().get("transcript", "")
    return ""

# Helper: Predict Intent from Model
def predict_intent(text: str):
    if not os.path.exists("model.pkl"):
        return "greeting", "ನಮಸ್ಕಾರ! ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
    
    with open("model.pkl", "rb") as f:
        vectorizer, classifier = pickle.load(f)
        
    with open("data/intents.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    X_vec = vectorizer.transform([text])
    predicted_tag = classifier.predict(X_vec)[0]

    for intent in data["intents"]:
        if intent["tag"] == predicted_tag:
            return predicted_tag, intent["responses"][0]

    return "fallback", "I didn't quite understand that query."

@app.get("/")
def read_root():
    return {"status": "Active", "message": "Regional Assistant API Operational"}

@app.post("/process-voice/")
async def process_voice(
    user_id: str = Form(...),
    language: str = Form("kn-IN"),
    file: UploadFile = File(...)
):
    # 1. Save incoming audio
    input_audio_path = f"audio_temp/input_{user_id}.wav"
    with open(input_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Convert Speech to Text (STT)
    transcribed_text = transcribe_speech(input_audio_path, lang_code=language)

    # 3. Predict Intent & Get Response
    current_context = context_store.get_context(user_id)
    predicted_intent, response_text = predict_intent(transcribed_text)

    # 4. Update Context Session
    context_store.update_context(user_id, predicted_intent)

    # 5. Text to Speech (TTS) Output
    output_audio_path = f"audio_temp/output_{user_id}.mp3"
    tts = gTTS(text=response_text, lang="kn")
    tts.save(output_audio_path)

    return {
        "user_id": user_id,
        "user_query_text": transcribed_text,
        "intent": predicted_intent,
        "response_text": response_text,
        "audio_url": f"/get-audio/{user_id}"
    }

@app.get("/get-audio/{user_id}")
def get_audio(user_id: str):
    audio_path = f"audio_temp/output_{user_id}.mp3"
    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/mp3")
    return {"error": "Audio file not found"}