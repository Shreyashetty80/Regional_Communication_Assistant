class SessionContextManager:

    def __init__(self):
        # Store active conversations
        self.sessions = {}

    def get_context(self, user_id: str) -> dict:

        return self.sessions.get(
            user_id,
            {
                "last_intent": None,
                "slots": {},
                "history": []
            }
        )

    def update_context(
        self,
        user_id: str,
        intent: str,
        slots: dict = None
    ):

        previous_context = self.get_context(user_id)

        history = previous_context.get(
            "history",
            []
        )

        # Keep recent conversation intents
        history.append(intent)

        # Keep only last 5 intents
        history = history[-5:]

        self.sessions[user_id] = {

            "last_intent": intent,

            "slots": slots or {},

            "history": history
        }

    def clear_context(self, user_id: str):

        if user_id in self.sessions:

            del self.sessions[user_id]