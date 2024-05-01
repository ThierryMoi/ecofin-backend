from typing import List, Optional
from model.message_model import Message
class MessageService:
    def __init__(self, message_repository):
        self.message_repository = message_repository

    def create_message(self, message_data: dict) -> Message:
        return self.message_repository.create_message(message_data)

    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        return self.message_repository.get_message_by_id(message_id)

    def update_message(self, message_id: str, new_data: dict) -> Optional[Message]:
        return self.message_repository.update_message(message_id, new_data)

    def delete_message(self, message_id: str) -> None:
        self.message_repository.delete_message(message_id)

    def get_all_messages(self) -> List[Message]:
        return self.message_repository.get_all_messages()
