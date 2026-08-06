import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from gtts import gTTS

from context_manager import SessionContextManager

app = FastAPI(title="Context-Aware Smart Communication Assistant")
context_store = SessionContextManager()

# Create folder for temporary audio processing
os.makedirs("audio_temp", exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "Active", "message": "Regional Communication Assistant API Running"}

@app.post("/process-voice/")
async def process_voice(
    user_id: str = Form(...),
    language: str = Form("kn"),  # 'kn' for Kannada, etc.
    file: UploadFile = File(...)
):
    # 1. Save uploaded voice file from Sushmitha's UI
    input_audio_path = f"audio_temp/input_{user_id}.wav"
    with open(input_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Mock STT / Speech-to-Text conversion (Replace with Sarvam AI/Bhashini API call)
    transcribed_text = "ನಮಸ್ಕಾರ" 

    # 3. Fetch context and process intent
    current_context = context_store.get_context(user_id)
    
    # Mock Intent Engine output (Hook up Supreetha's trained classifier here)
    predicted_intent = "greeting"
    response_text = "ನಮಸ್ಕಾರ! ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
    
    # 4. Update session context memory
    context_store.update_context(user_id, predicted_intent)
    
    # 5. Convert response text to voice output (TTS)
    output_audio_path = f"audio_temp/output_{user_id}.mp3"
    tts = gTTS(text=response_text, lang=language if language in ['kn'] else 'kn')
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