
from typing import Optional, List

class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def create_user(self, user_data: dict) -> str:
        return self.user_repo.create(user_data)

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        return self.user_repo.find_by_id(user_id)

    def get_all_users(self) -> List[dict]:
        return self.user_repo.find_all()

    def update_user(self, user_id: str, update_data: dict) -> bool:
        return self.user_repo.update(user_id, update_data)

    def delete_user(self, user_id: str) -> bool:
        return self.user_repo.delete(user_id)
