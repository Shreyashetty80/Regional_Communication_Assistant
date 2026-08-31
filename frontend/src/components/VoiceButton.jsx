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
  const recognitionRef = useRef(null);

  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);

  // ============================================================
  // TULU VOICE - BROWSER SPEECH RECOGNITION
  // ============================================================

  const startTuluRecognition = () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        "Tulu voice recognition requires Google Chrome."
      );
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognitionRef.current = recognition;

    recognition.onstart = () => {
      setRecording(true);
      setProcessing(false);
    };

    recognition.onresult = async (event) => {
      const transcript =
        event.results[0][0].transcript;

      console.log("Tulu voice transcript:", transcript);

      if (!transcript.trim()) {
        alert("Could not understand the voice.");
        setRecording(false);
        return;
      }

      setRecording(false);
      setProcessing(true);

      try {
        // Send recognized text to normal chatbot API
        const response = await fetch(
          `${API_URL}/chat`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              user_id: userId,
              message: transcript,
              language: "tcy",
            }),
          }
        );

        if (!response.ok) {
          throw new Error(
            "Chat API request failed"
          );
        }

        const data = await response.json();

        if (!data.success) {
          throw new Error(
            data.message ||
              "Unable to process Tulu voice input"
          );
        }

        // Send result to parent component
        onVoiceResult({
          success: true,
          user_id: userId,
          user_query_text: transcript,
          response_text: data.response,
          intent: data.intent,
          previous_context:
            data.previous_context,
          audio_url: null,
        });

        // Optional browser speech output
        const speech =
          new SpeechSynthesisUtterance(
            data.response
          );

        speech.lang = "en-IN";

        window.speechSynthesis.speak(
          speech
        );
      } catch (error) {
        console.error(
          "Tulu voice processing error:",
          error
        );

        alert(
          "Unable to process Tulu voice input."
        );
      } finally {
        setProcessing(false);
      }
    };

    recognition.onerror = (event) => {
      console.error(
        "Tulu speech recognition error:",
        event.error
      );

      setRecording(false);
      setProcessing(false);

      if (event.error === "not-allowed") {
        alert(
          "Microphone permission was denied."
        );
      } else {
        alert(
          "Could not recognize the voice. Please try again."
        );
      }
    };

    recognition.onend = () => {
      setRecording(false);
    };

    recognition.start();
  };

  // ============================================================
  // SARVAM VOICE - ENGLISH / KANNADA / KONKANI
  // ============================================================

  const startRecording = async () => {
    if (disabled || processing) {
      return;
    }

    // Tulu uses browser speech recognition
    if (language === "tcy") {
      startTuluRecognition();
      return;
    }

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      audioChunksRef.current = [];

      const recorder = new MediaRecorder(
        stream
      );

      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(
            event.data
          );
        }
      };

      recorder.onstop = async () => {
        stream
          .getTracks()
          .forEach((track) => {
            track.stop();
          });

        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: "audio/webm",
          }
        );

        await processVoice(audioBlob);
      };

      recorder.start();

      setRecording(true);
    } catch (error) {
      console.error(
        "Microphone error:",
        error
      );

      alert(
        "Microphone access was denied or is not available."
      );
    }
  };

  // ============================================================
  // STOP RECORDING
  // ============================================================

  const stopRecording = () => {
    // Tulu browser recognition
    if (
      language === "tcy" &&
      recognitionRef.current
    ) {
      recognitionRef.current.stop();
      setRecording(false);
      return;
    }

    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !==
        "inactive"
    ) {
      mediaRecorderRef.current.stop();

      setRecording(false);
      setProcessing(true);
    }
  };

  // ============================================================
  // SEND AUDIO TO FASTAPI / SARVAM
  // ============================================================

  const processVoice = async (audioBlob) => {
    try {
      const formData = new FormData();

      formData.append(
        "user_id",
        userId
      );

      formData.append(
        "language",
        `${language}-IN`
      );

      formData.append(
        "file",
        audioBlob,
        "voice.webm"
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

  // ============================================================
  // BUTTON CLICK
  // ============================================================

  const handleClick = () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={
        disabled || processing
      }
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