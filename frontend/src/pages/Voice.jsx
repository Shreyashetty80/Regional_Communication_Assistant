import { useState } from "react";
import "./Voice.css";

function Voice() {
  const [isListening, setIsListening] = useState(false);
  const [text, setText] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");

  const startVoice = () => {
    setError("");

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError(
        "Speech recognition is not supported. Please use Google Chrome."
      );
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      setError("");
    };

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;

      setText(transcript);

      try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: "voice_user",
            message: transcript,
            language: "en",
          }),
        });

        if (!res.ok) {
          throw new Error("Server error");
        }

        const data = await res.json();

        setResponse(data.response || "No response received.");
      } catch (err) {
        console.error(err);
        setError("Could not connect to the assistant.");
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);

      setIsListening(false);

      if (event.error === "not-allowed") {
        setError(
          "Microphone permission denied. Please allow microphone access."
        );
      } else if (event.error === "no-speech") {
        setError("No speech detected. Please try again.");
      } else if (event.error === "audio-capture") {
        setError("No microphone was detected.");
      } else {
        setError(`Voice error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (err) {
      console.error(err);
      setIsListening(false);
      setError("Could not start voice recognition.");
    }
  };

  return (
    <div className="voice-page">

      {/* HEADER */}
      <header className="voice-header">
        <div className="voice-logo">
          🎙️
        </div>

        <div>
          <h1>Voice Assistant</h1>
          <p>Speak naturally and communicate with your AI assistant</p>
        </div>
      </header>


      {/* MAIN CARD */}
      <main className="voice-card">

        {/* STATUS */}
        <div className="voice-status">
          <span
            className={`status-dot ${
              isListening ? "active" : ""
            }`}
          ></span>

          {isListening ? "Listening..." : "Ready to listen"}
        </div>


        {/* MICROPHONE */}
        <button
          className={`mic-button ${
            isListening ? "mic-active" : ""
          }`}
          onClick={startVoice}
          aria-label="Start voice recognition"
        >
          <span className="mic-symbol">🎙️</span>
        </button>


        <h2>
          {isListening
            ? "Listening to you..."
            : "Tap the microphone"}
        </h2>

        <p className="voice-hint">
          Speak your question clearly. Your speech will be converted
          into text and sent to the AI assistant.
        </p>


        {/* USER MESSAGE */}
        <div className="conversation-box user-box">

          <div className="message-label">
            <span className="label-icon">👤</span>
            You said
          </div>

          <div className="message-content">
            {text || (
              <span className="placeholder">
                Your speech will appear here...
              </span>
            )}
          </div>

        </div>


        {/* ASSISTANT MESSAGE */}
        <div className="conversation-box assistant-box">

          <div className="message-label">
            <span className="label-icon">🤖</span>
            Assistant
          </div>

          <div className="message-content">
            {response || (
              <span className="placeholder">
                Assistant response will appear here...
              </span>
            )}
          </div>

        </div>


        {/* ERROR */}
        {error && (
          <div className="voice-error">
            ⚠️ {error}
          </div>
        )}

      </main>


      {/* FEATURES */}
      <section className="voice-features">

        <div className="feature">
          <div className="feature-icon">🎤</div>

          <div>
            <strong>Speech Recognition</strong>
            <p>Convert your voice into text</p>
          </div>
        </div>


        <div className="feature">
          <div className="feature-icon">🌐</div>

          <div>
            <strong>Multilingual</strong>
            <p>English, Kannada, Tulu & Konkani</p>
          </div>
        </div>


        <div className="feature">
          <div className="feature-icon">🤖</div>

          <div>
            <strong>AI Assistant</strong>
            <p>Get intelligent responses</p>
          </div>
        </div>

      </section>

    </div>
  );
}

export default Voice;