from typing import List, Optional
from model.user_model import User
class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(self, user_data: dict) -> User:
        
        return self.user_repository.create_user(user_data)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.user_repository.get_user_by_id(user_id)

    def update_user(self, user_id: str, new_data: dict) -> Optional[User]:
        return self.user_repository.update_user(user_id, new_data)

    def delete_user(self, user_id: str) -> None:
        self.user_repository.delete_user(user_id)

    def get_all_users(self) -> List[User]:
        return self.user_repository.get_all_users()
