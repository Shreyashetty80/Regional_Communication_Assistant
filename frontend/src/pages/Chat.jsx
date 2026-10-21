
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import VoiceButton from "../components/VoiceButton";

const API_URL = "http://127.0.0.1:8000";

function Chat() {
  const location = useLocation();
  const navigate = useNavigate();

  const selectedLanguage =
    location.state?.language ||
    localStorage.getItem("selectedLanguage") ||
    "en";

  const languageNames = {
    en: "English",
    kn: "Kannada",
    tcy: "Tulu",
  };

  const languageName =
    languageNames[selectedLanguage] || "English";

  const userId = localStorage.getItem("user_id") || "user_001";

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Load the selected language's conversation history.
  useEffect(() => {
    setMessages([]);
    loadChatHistory();
  }, [userId, selectedLanguage]);

  const loadChatHistory = async () => {
    try {
      setHistoryLoading(true);

      const response = await fetch(
  `${API_URL}/history/${userId}?language=${selectedLanguage}`
);

      if (!response.ok) {
        throw new Error("Failed to load chat history");
      }

      const data = await response.json();
      const allHistory = data.history || [];

      // Display only records matching this language.
      const filteredHistory = allHistory.filter((item) => {
        const itemLanguage =
          item.language || item.language_code;

        return itemLanguage === selectedLanguage;
      });

      const formattedMessages = [];

      filteredHistory.forEach((item) => {
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
      console.error("Chat history error:", error);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Send a message.
  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();

    setMessages((previous) => [
      ...previous,
      { sender: "user", text: userMessage },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          message: userMessage,
          language: selectedLanguage,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat API failed");
      }

      const data = await response.json();

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
      console.error("Chat error:", error);

      setMessages((previous) => [
        ...previous,
        {
          sender: "bot",
          text:
            "Something went wrong. Please check whether the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Handle voice responses.
  const handleVoiceResult = (data) => {
    setMessages((previous) => [
      ...previous,
      {
        sender: "user",
        text: data.user_query_text || "",
      },
      {
        sender: "bot",
        text:
          data.response_text ||
          "Sorry, I could not generate a response.",
      },
    ]);
  };

  // Press Enter to send.
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  // Refresh this lobby's history.
  const refreshHistory = () => {
    loadChatHistory();
  };

  // Clear messages from the screen only.
  const clearChat = () => {
    if (!messages.length) return;

    const confirmed = window.confirm(
      `Clear the ${languageName} conversation from this screen? Saved database history will not be deleted.`
    );

    if (confirmed) {
      setMessages([]);
    }
  };

  // Navigate back to language selection.
  const goBack = () => {
    navigate("/language");
  };

  const buttonStyle = {
    padding: "10px 14px",
    borderRadius: "9px",
    border: "1px solid #414760",
    background: "#20243a",
    color: "#ffffff",
    cursor: "pointer",
    fontWeight: 600,
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "clamp(16px, 4vw, 36px)",
        boxSizing: "border-box",
        fontFamily: "Inter, Arial, sans-serif",
        background:
          "radial-gradient(ellipse at top left, #20183d, #0b0d18 50%, #090b14)",
        color: "#f8fafc",
      }}
    >
      <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
        {/* Header */}
        <header style={{ marginBottom: "26px" }}>
          {/* Back button */}
          <button
            type="button"
            onClick={goBack}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "10px 16px",
              marginBottom: "24px",
              borderRadius: "10px",
              border: "1px solid #414760",
              background: "#20243a",
              color: "#ffffff",
              fontSize: "14px",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            ← Back to Languages
          </button>

          <div>
            <span
              style={{
                display: "inline-block",
                padding: "7px 12px",
                borderRadius: "20px",
                background: "rgba(139,92,246,0.15)",
                border: "1px solid rgba(139,92,246,0.35)",
                color: "#c4b5fd",
                fontSize: "13px",
                marginBottom: "14px",
              }}
            >
              ✦ Smart Communication Assistant
            </span>

            <h1
              style={{
                margin: "0 0 10px",
                fontSize: "clamp(26px, 4vw, 38px)",
                color: "#ffffff",
              }}
            >
              {languageName} Lobby
            </h1>

            <p style={{ color: "#b7bfd3", lineHeight: 1.6 }}>
              Your {languageName} conversations stay in this lobby.
            </p>

            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "10px",
              }}
            >
              <span style={badgeStyle}>User ID: {userId}</span>
              <span style={badgeStyle}>
                Language: {languageName}
              </span>
            </div>
          </div>
        </header>

        {/* Conversation panel */}
        <section
          style={{
            border: "1px solid #292d43",
            borderRadius: "20px",
            background: "#111421",
            overflow: "hidden",
            boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
          }}
        >
          {/* Toolbar */}
          <div
            style={{
              padding: "18px 20px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "12px",
              borderBottom: "1px solid #292d43",
            }}
          >
            <div>
              <h2 style={{ margin: "0 0 5px", color: "#ffffff" }}>
                {languageName} Conversation
              </h2>
              <p
                style={{
                  margin: 0,
                  color: "#aab3c8",
                  fontSize: "13px",
                }}
              >
                {messages.length} messages
              </p>
            </div>

            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              <button
                type="button"
                onClick={refreshHistory}
                disabled={historyLoading}
                style={{
                  ...buttonStyle,
                  opacity: historyLoading ? 0.6 : 1,
                }}
              >
                {historyLoading ? "Refreshing..." : "↻ Refresh"}
              </button>

              <button
                type="button"
                onClick={clearChat}
                disabled={!messages.length || loading}
                style={{
                  ...buttonStyle,
                  opacity: !messages.length || loading ? 0.5 : 1,
                }}
              >
                Clear Chat
              </button>
            </div>
          </div>

          {/* Messages */}
          <div
            style={{
              minHeight: "320px",
              maxHeight: "500px",
              overflowY: "auto",
              padding: "22px",
              background: "#0f1220",
            }}
          >
            {historyLoading && messages.length === 0 ? (
              <p style={{ textAlign: "center", color: "#cbd5e1" }}>
                Loading {languageName} conversations...
              </p>
            ) : messages.length === 0 ? (
              <div
                style={{
                  minHeight: "275px",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    width: "58px",
                    height: "58px",
                    display: "grid",
                    placeItems: "center",
                    borderRadius: "18px",
                    background: "linear-gradient(135deg,#7c3aed,#4f46e5)",
                    fontSize: "26px",
                    marginBottom: "18px",
                  }}
                >
                  ✦
                </div>

                <h3 style={{ color: "#ffffff", margin: "0 0 10px" }}>
                  Welcome to your {languageName} lobby
                </h3>

                <p
                  style={{
                    color: "#aab3c8",
                    maxWidth: "380px",
                    lineHeight: 1.7,
                    fontSize: "14px",
                  }}
                >
                  Start a conversation. Only {languageName} history
                  will be displayed in this lobby.
                </p>
              </div>
            ) : (
              messages.map((message, index) => {
                const isUser = message.sender === "user";

                return (
                  <div
                    key={index}
                    style={{
                      display: "flex",
                      justifyContent: isUser ? "flex-end" : "flex-start",
                      marginBottom: "16px",
                    }}
                  >
                    <div
                      style={{
                        maxWidth: "85%",
                        minWidth: "100px",
                        padding: "13px 16px",
                        borderRadius: isUser
                          ? "16px 16px 4px 16px"
                          : "16px 16px 16px 4px",
                        background: isUser
                          ? "linear-gradient(135deg,#6d4aff,#5540c9)"
                          : "#20243a",
                        border: isUser
                          ? "1px solid #8068ff"
                          : "1px solid #343a53",
                        color: "#ffffff",
                        overflowWrap: "anywhere",
                      }}
                    >
                      <div
                        style={{
                          color: isUser ? "#e9e4ff" : "#c4b5fd",
                          fontSize: "12px",
                          fontWeight: 700,
                          marginBottom: "7px",
                        }}
                      >
                        {isUser ? "You" : "✦ Assistant"}
                      </div>

                      <div
                        style={{
                          color: "#ffffff",
                          fontSize: "15px",
                          lineHeight: 1.7,
                          whiteSpace: "pre-wrap",
                          overflowWrap: "anywhere",
                        }}
                      >
                        {message.text}
                      </div>
                    </div>
                  </div>
                );
              })
            )}

            {loading && (
              <div style={{ color: "#d1d5e5", padding: "12px" }}>
                ✦ Assistant is typing...
              </div>
            )}
          </div>

          {/* Input area */}
          <div
            style={{
              padding: "18px 20px",
              borderTop: "1px solid #292d43",
              background: "#151827",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "stretch",
                flexWrap: "wrap",
                gap: "10px",
              }}
            >
              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`Type your message in ${languageName}...`}
                disabled={loading}
                aria-label="Type your message"
                style={{
                  flex: "1 1 220px",
                  minWidth: 0,
                  boxSizing: "border-box",
                  padding: "13px 15px",
                  borderRadius: "11px",
                  border: "1px solid #3c435c",
                  background: "#0d1020",
                  color: "#ffffff",
                  fontSize: "15px",
                  outline: "none",
                }}
              />

              <button
                type="button"
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                style={{
                  padding: "12px 22px",
                  borderRadius: "11px",
                  border: "none",
                  background: "#6d4aff",
                  color: "#ffffff",
                  fontWeight: 700,
                  cursor:
                    loading || !input.trim() ? "not-allowed" : "pointer",
                  opacity: loading || !input.trim() ? 0.6 : 1,
                }}
              >
                {loading ? "Sending..." : "Send ➤"}
              </button>

              <VoiceButton
                userId={userId}
                language={selectedLanguage}
                onVoiceResult={handleVoiceResult}
                disabled={loading}
              />
            </div>

            <p
              style={{
                color: "#8993ad",
                fontSize: "12px",
                margin: "12px 0 0",
              }}
            >
              Press Enter to send. Selected language: {languageName}.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

const badgeStyle = {
  display: "inline-block",
  padding: "8px 12px",
  borderRadius: "9px",
  background: "#151827",
  border: "1px solid #30364d",
  color: "#d8deed",
  fontSize: "13px",
};

export default Chat;
