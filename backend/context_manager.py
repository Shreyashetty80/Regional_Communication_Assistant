class SessionContextManager:

    def __init__(self):
        # Store active conversations
        self.sessions = {}

    # ========================================================
    # GET CONTEXT
    # ========================================================

    def get_context(self, user_id: str) -> dict:

        return self.sessions.get(
            user_id,
            {
                "last_intent": None,
                "slots": {},
                "history": []
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
        assistant_response: str = None
    ):

        previous_context = self.get_context(user_id)

        # ----------------------------------------------------
        # Existing intent history
        # ----------------------------------------------------

        intent_history = previous_context.get(
            "history",
            []
        )

        intent_history.append(intent)

        # Keep last 5 intents
        intent_history = intent_history[-5:]

        # ----------------------------------------------------
        # Conversation history
        # ----------------------------------------------------

        conversation_history = previous_context.get(
            "conversation_history",
            []
        )

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

        # Keep last 10 messages
        conversation_history = conversation_history[-10:]

        # ----------------------------------------------------
        # Save context
        # ----------------------------------------------------

        self.sessions[user_id] = {

            "last_intent": intent,

            "slots": slots or {},

            "history": intent_history,

            "conversation_history":
                conversation_history
        }

    # ========================================================
    # CLEAR CONTEXT
    # ========================================================

    def clear_context(self, user_id: str):

        if user_id in self.sessions:

            del self.sessions[user_id]