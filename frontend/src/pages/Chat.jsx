import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import VoiceButton from "../components/VoiceButton";

const API_URL = "http://127.0.0.1:8000";

function Chat() {
  const location = useLocation();

  // Get selected language
  const selectedLanguage =
    location.state?.language ||
    localStorage.getItem("selectedLanguage") ||
    "en";

  const languageNames = {
    en: "English",
    kn: "Kannada",
    tcy: "Tulu",
    kok: "Konkani",
  };

  const languageName =
    languageNames[selectedLanguage] || "English";

  // Temporary user ID
  const userId =
    localStorage.getItem("user_id") || "user_001";

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // ---------------------------------------------------
  // LOAD CHAT HISTORY FROM DATABASE
  // ---------------------------------------------------

  useEffect(() => {
    loadChatHistory();
  }, [userId]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(
        `${API_URL}/history/${userId}`
      );

      if (!response.ok) {
        throw new Error("Failed to load history");
      }

      const data = await response.json();

      const history = data.history || [];

      const formattedMessages = [];

      history.forEach((item) => {
        formattedMessages.push({
          sender: "user",
          text: item.user_message,
        });

        formattedMessages.push({
          sender: "bot",
          text: item.bot_response,
        });
      });

      setMessages(formattedMessages);

    } catch (error) {
      console.error(
        "Chat history error:",
        error
      );
    }
  };

  // ---------------------------------------------------
  // SEND MESSAGE
  // ---------------------------------------------------

  const sendMessage = async () => {
    if (!input.trim() || loading) {
      return;
    }

    const userMessage = input.trim();

    // Show user message immediately
    setMessages((previous) => [
      ...previous,
      {
        sender: "user",
        text: userMessage,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            user_id: userId,
            message: userMessage,
            language: selectedLanguage,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Chat API failed");
      }

      const data = await response.json();

      // Show bot response
      setMessages((previous) => [
        ...previous,
        {
          sender: "bot",
          text:
            data.response ||
            "Sorry, I could not generate a response.",
        },
      ]);

    } catch (error) {
      console.error(
        "Chat error:",
        error
      );

      setMessages((previous) => [
        ...previous,
        {
          sender: "bot",
          text:
            "Sorry, something went wrong. Please check whether the backend server is running.",
        },
      ]);

    } finally {
      setLoading(false);
    }
  };

  const handleVoiceResult = (data) => {
    const userText =
      data.user_query_text || "";

    const botText =
      data.response_text ||
      "Sorry, I could not generate a response.";

    setMessages((previous) => [
      ...previous,
      {
        sender: "user",
        text: userText,
      },
      {
        sender: "bot",
        text: botText,
      },
    ]);
  };

  // ---------------------------------------------------
  // ENTER KEY
  // ---------------------------------------------------

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  // ---------------------------------------------------
  // CLEAR LOCAL CHAT VIEW
  // ---------------------------------------------------

  const refreshHistory = () => {
    loadChatHistory();
  };

  // ---------------------------------------------------
  // UI
  // ---------------------------------------------------

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "30px",
        boxSizing: "border-box",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>
        {languageName} Chat Assistant
      </h1>

      <p>
        User ID: {userId}
      </p>

      <p>
        Language: {languageName}
      </p>

      <hr />

      {/* CHAT HISTORY */}

      <div
        style={{
          minHeight: "300px",
          maxHeight: "500px",
          overflowY: "auto",
          padding: "10px 0",
        }}
      >
        {messages.length === 0 ? (
          <p>
            No previous conversation found.
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              style={{
                marginBottom: "12px",
              }}
            >
              <strong>
                {message.sender === "user"
                  ? "You"
                  : "Assistant"}
                :
              </strong>

              <span
                style={{
                  marginLeft: "8px",
                }}
              >
                {message.text}
              </span>
            </div>
          ))
        )}

        {loading && (
          <p>
            <strong>Assistant:</strong> Typing...
          </p>
        )}
      </div>

      <hr />

      {/* INPUT */}

      <div
        style={{
          display: "flex",
          gap: "8px",
          marginTop: "15px",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          onKeyDown={handleKeyDown}
          placeholder={
            `Type your message in ${languageName}`
          }
          style={{
            flex: 1,
            padding: "10px",
          }}
        />

        <button
          onClick={sendMessage}
          disabled={loading}
        >
          {loading ? "Sending..." : "Send"}
        </button>

        <VoiceButton
          userId={userId}
          language={selectedLanguage}
          onVoiceResult={handleVoiceResult}
          disabled={loading}
        />

      </div>

      <button
        onClick={refreshHistory}
        style={{
          marginTop: "12px",
        }}
      >
        Refresh Chat History
      </button>
    </div>
  );
}

export default Chat;