import { useEffect, useState } from "react";

function Chat() {
  const [language, setLanguage] = useState("");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const selectedLanguage = localStorage.getItem("selectedLanguage");
    setLanguage(selectedLanguage || "English");
  }, []);

  const sendMessage = () => {
    if (message.trim() === "") {
      return;
    }

    const newMessage = {
      text: message,
      sender: "user",
    };

    setMessages((previousMessages) => [
      ...previousMessages,
      newMessage,
    ]);

    setMessage("");
  };

  return (
    <div className="chat-page">
      <div className="chat-container">

        <h1>{language} Chat Assistant</h1>

        <div className="chat-history">
          {messages.length === 0 ? (
            <p className="welcome-message">
              Start a conversation in {language}.
            </p>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className="message user-message"
              >
                {msg.text}
              </div>
            ))
          )}
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder={`Type your message in ${language}...`}
          />

          <button onClick={sendMessage}>
            Send
          </button>
        </div>

      </div>
    </div>
  );
}

export default Chat;