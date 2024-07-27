
from typing import Optional, List

class DiscussionService:
    def __init__(self, discussion_repo):
        self.discussion_repo = discussion_repo

    def create_discussion(self, discussion_data: dict) -> str:
        return self.discussion_repo.create(discussion_data)

    def get_discussion_by_id(self, discussion_id: str) -> Optional[dict]:
        return self.discussion_repo.find_by_id(discussion_id)

    def get_all_discussions(self,page,page_size) -> dict:
        dc={}
        lst , nb = self.discussion_repo.find_all(page,page_size)
        dc["discussions"]=lst
        dc["page_size"]=page_size
        dc["page"]=page
        dc["nb_pages"]=nb
        return dc
    
    def get_all_discussions_by_user(self,user_id ,page,page_size) -> dict:
        dc={}
        lst , nb = self.discussion_repo.find_all_by_user(user_id, page,page_size)
        dc["discussions"]=lst
        dc["page_size"]=page_size
        dc["page"]=page
        dc["nb_pages"]=nb
        return dc
        
 

    def get_all_discussions_by_user_id(self,user_id) -> List[dict]:
        return self.discussion_repo.find_by_user_id(user_id)

    def update_discussion(self, discussion_id: str, update_data: dict) -> bool:
        return self.discussion_repo.update(discussion_id, update_data)

    def delete_discussion(self, discussion_id: str) -> bool:
        return self.discussion_repo.delete(discussion_id)
