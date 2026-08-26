const API_URL = "http://127.0.0.1:8000";

export async function sendChatMessage(userId, message, language) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      message: message,
      language: language,
    }),
  });

  if (!response.ok) {
    throw new Error("Backend request failed");
  }

  return await response.json();
}