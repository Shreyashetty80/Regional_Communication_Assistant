
class SessionContextManager:

    def __init__(self):
        # Store separate conversations for each user and language
        self.sessions = {}

    # ========================================================
    # GET CONTEXT
    # ========================================================

    def get_context(self, user_id: str, language: str = "en") -> dict:

        session_key = (user_id, language)

        return self.sessions.get(
            session_key,
            {
                "last_intent": None,
                "slots": {},
                "history": [],
                "conversation_history": []
            }
        )

    # ========================================================
    # UPDATE CONTEXT
    # ========================================================

    def update_context(
        self,
        user_id: str,
        intent: str,
        slots: dict = None,
        user_message: str = None,
        assistant_response: str = None,
        language: str = "en"
    ):

        session_key = (user_id, language)

        previous_context = self.get_context(user_id, language)

        # Keep the last 5 detected intents
        intent_history = previous_context.get("history", []).copy()
        intent_history.append(intent)
        intent_history = intent_history[-5:]

        # Preserve conversation history for this language only
        conversation_history = previous_context.get(
            "conversation_history", []
        ).copy()

        if user_message:
            conversation_history.append({
                "role": "user",
                "content": user_message
            })

        if assistant_response:
            conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

        # Keep the last 10 messages
        conversation_history = conversation_history[-10:]

        self.sessions[session_key] = {
            "last_intent": intent,
            "slots": slots or {},
            "history": intent_history,
            "conversation_history": conversation_history
        }

    # ========================================================
    # CLEAR CONTEXT
    # ========================================================

    def clear_context(
        self,
        user_id: str,
        language: str = None
    ):

        if language is not None:
            # Clear only the selected language
            session_key = (user_id, language)
            self.sessions.pop(session_key, None)
        else:
            # Clear all language contexts for this user
            keys_to_remove = [
                key for key in self.sessions
                if key[0] == user_id
            ]

            for key in keys_to_remove:
                del self.sessions[key]
