import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import VoiceButton from "../components/VoiceButton";

const API_URL = "http://127.0.0.1:8000";

function Chat() {
  const location = useLocation();

  // ---------------------------------------------------
  // SELECTED LANGUAGE
  // ---------------------------------------------------

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

  // ---------------------------------------------------
  // USER ID
  // ---------------------------------------------------

  const userId =
    localStorage.getItem("user_id") || "user_001";

  // ---------------------------------------------------
  // STATES
  // ---------------------------------------------------

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  // ---------------------------------------------------
  // LOAD CHAT HISTORY
  // ---------------------------------------------------

  useEffect(() => {
    loadChatHistory();
  }, [userId]);

  const loadChatHistory = async () => {
    try {
      setHistoryLoading(true);

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
    } finally {
      setHistoryLoading(false);
    }
  };

  // ---------------------------------------------------
  // SEND TEXT MESSAGE
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

  // ---------------------------------------------------
  // VOICE RESULT
  // ---------------------------------------------------

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
  // REFRESH CHAT HISTORY
  // ---------------------------------------------------

  const refreshHistory = () => {
    loadChatHistory();
  };

  // ---------------------------------------------------
  // CLEAR CHAT
  // ---------------------------------------------------
  // This only clears the current screen.
  // Database history is NOT deleted.
  // ---------------------------------------------------

  const clearChat = () => {
    if (messages.length === 0) {
      return;
    }

    const confirmClear = window.confirm(
      "Are you sure you want to clear the chat from the screen?"
    );

    if (confirmClear) {
      setMessages([]);
    }
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

      {/* ------------------------------------------------
          HEADER
      ------------------------------------------------ */}

      <h1>
        {languageName} Chat Assistant
      </h1>

      <p>
        <strong>User ID:</strong> {userId}
      </p>

      <p>
        <strong>Language:</strong> {languageName}
      </p>

      <hr />

      {/* ------------------------------------------------
          CHAT HISTORY HEADER
      ------------------------------------------------ */}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "10px",
        }}
      >
        <h2>
          Conversation
        </h2>

        <div
          style={{
            display: "flex",
            gap: "8px",
          }}
        >

          {/* REFRESH */}

          <button
            onClick={refreshHistory}
            disabled={historyLoading}
          >
            {historyLoading
              ? "Refreshing..."
              : "🔄 Refresh"}
          </button>

          {/* CLEAR */}

          <button
            onClick={clearChat}
            disabled={
              messages.length === 0 ||
              loading
            }
          >
            🗑️ Clear Chat
          </button>

        </div>
      </div>

      {/* ------------------------------------------------
          CHAT AREA
      ------------------------------------------------ */}

      <div
        style={{
          minHeight: "300px",
          maxHeight: "500px",
          overflowY: "auto",
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "15px",
          backgroundColor: "#fafafa",
        }}
      >

        {messages.length === 0 ? (

          <p
            style={{
              textAlign: "center",
              color: "#777",
            }}
          >
            No conversation to display.
          </p>

        ) : (

          messages.map(
            (message, index) => (

              <div
                key={index}
                style={{
                  marginBottom: "15px",
                  padding: "10px",
                  borderRadius: "8px",
                  backgroundColor:
                    message.sender === "user"
                      ? "#e8f0fe"
                      : "#f1f1f1",
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

            )
          )

        )}

        {/* LOADING */}

        {loading && (

          <div
            style={{
              marginBottom: "15px",
              padding: "10px",
              borderRadius: "8px",
              backgroundColor: "#f1f1f1",
            }}
          >
            <strong>
              Assistant:
            </strong>

            <span
              style={{
                marginLeft: "8px",
              }}
            >
              Typing...
            </span>
          </div>

        )}

      </div>

      <hr />

      {/* ------------------------------------------------
          INPUT AREA
      ------------------------------------------------ */}

      <div
        style={{
          display: "flex",
          gap: "8px",
          marginTop: "15px",
        }}
      >

        {/* TEXT INPUT */}

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
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        />

        {/* SEND BUTTON */}

        <button
          onClick={sendMessage}
          disabled={
            loading ||
            !input.trim()
          }
        >
          {loading
            ? "Sending..."
            : "Send"}
        </button>

        {/* VOICE BUTTON */}

        <VoiceButton
          userId={userId}
          language={selectedLanguage}
          onVoiceResult={handleVoiceResult}
          disabled={loading}
        />

      </div>

    </div>
  );
}

export default Chat;