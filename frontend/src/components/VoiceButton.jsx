import React, { useRef, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function VoiceButton({
  userId,
  language,
  onVoiceResult,
  disabled = false,
}) {
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);

  const startRecording = async () => {
    if (disabled || processing) {
      return;
    }

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      audioChunksRef.current = [];

      const recorder = new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => {
          track.stop();
        });

        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: "audio/wav",
          }
        );

        await processVoice(audioBlob);
      };

      recorder.start();

      setRecording(true);

    } catch (error) {
      console.error("Microphone error:", error);

      alert(
        "Microphone access was denied or is not available."
      );
    }
  };

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setProcessing(true);
    }
  };

  const processVoice = async (audioBlob) => {
    try {
      const formData = new FormData();

      formData.append("user_id", userId);

      formData.append(
        "language",
        `${language}-IN`
      );

      formData.append(
        "file",
        audioBlob,
        "voice.wav"
      );

      const response = await fetch(
        `${API_URL}/process-voice/`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          "Voice API request failed"
        );
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.message ||
            "Speech processing failed"
        );
      }

      onVoiceResult(data);

      // Play generated response
      if (data.audio_url) {
        const audio = new Audio(
          `${API_URL}${data.audio_url}`
        );

        audio.play().catch((error) => {
          console.error(
            "Audio playback error:",
            error
          );
        });
      }

    } catch (error) {
      console.error(
        "Voice processing error:",
        error
      );

      alert(
        "Unable to process the voice input. Please check the backend and microphone."
      );

    } finally {
      setProcessing(false);
    }
  };

  const handleClick = () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || processing}
      style={{
        padding: "10px 16px",
        marginLeft: "8px",
        cursor:
          disabled || processing
            ? "not-allowed"
            : "pointer",
      }}
    >
      {recording
        ? "⏹ Stop"
        : processing
        ? "⏳ Processing..."
        : "🎤 Voice"}
    </button>
  );
}

export default VoiceButton;