import reflex as rx
from MultimodalChatbot.backend.chat_handler import get_answer


class ChatState(rx.State):
    prompt: str
    chat_history: list[tuple[str, str]]

    def get_answer(self):
        response = get_answer(self.prompt)
        self.chat_history.append((self.prompt, response))
        self.prompt = ''
        yield
