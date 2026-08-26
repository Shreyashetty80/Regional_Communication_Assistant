import { useState } from "react";

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
      console.log("🎙️ Voice recognition started");
      setIsListening(true);
      setError("");
    };

   recognition.onresult = (event) => {
  console.log("NUMBER OF RESULTS:", event.results.length);

  for (let i = 0; i < event.results.length; i++) {
    console.log(
      "RESULT",
      i,
      ":",
      event.results[i][0].transcript
    );
  }

  const transcript = event.results[0][0].transcript;

  alert("Chrome heard: " + transcript);

  setText(transcript);
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
      console.log("🎙️ Voice recognition ended");
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (error) {
      console.error("Could not start recognition:", error);
      setIsListening(false);
      setError("Could not start voice recognition.");
    }
  };

  return (
    <div className="voice-page">
      <h1>Voice Assistant</h1>

      <p>
        {isListening
          ? "🎙️ Listening... Speak now"
          : "Tap the microphone"}
      </p>

      <div
        className={`voice-circle ${isListening ? "listening" : ""}`}
        onClick={startVoice}
      >
        🎙️
      </div>

      <div className="voice-text">
        <strong>You:</strong>
        <br />
        {text || "Your speech will appear here..."}
      </div>

      <div className="assistant-response">
        <strong>Assistant:</strong>
        <br />
        {response || "Assistant response will appear here..."}
      </div>

      {error && (
        <p style={{ color: "red", marginTop: "15px" }}>
          {error}
        </p>
      )}
    </div>
  );
}

export default Voice;