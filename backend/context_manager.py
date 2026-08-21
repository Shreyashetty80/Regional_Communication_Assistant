class SessionContextManager:
    def __init__(self):
        # In-memory storage for active user conversations
        self.sessions = {}

    def get_context(self, user_id: str) -> dict:
        return self.sessions.get(user_id, {"last_intent": None, "slots": {}})

    def update_context(self, user_id: str, intent: str, slots: dict = None):
        self.sessions[user_id] = {
            "last_intent": intent,
            "slots": slots or {}
        }

    def clear_context(self, user_id: str):
        if user_id in self.sessions:
            del self.sessions[user_id]