from typing import List, Optional
from model.user_model import User,UserResponse

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(self, user_data: dict) -> Optional[UserResponse]:
        with self.session_scope() as session:
            try:
                user = User(**user_data)
                session.add(user)
                session.flush()
                user_response = UserResponse(
                    user_id=user.user_id,
                    nom_prenom=user.nom_prenom,
                    email=user.email,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    deleted_at=user.deleted_at
                )
                return user_response
            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=400, detail=str(e))
            
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        try:
            return self.user_repository.get_user_by_id(user_id)
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur : {str(e)}")
            return None

    def update_user(self, user_id: str, new_data: dict) -> Optional[User]:
        try:
            return self.user_repository.update_user(user_id, new_data)
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'utilisateur : {str(e)}")
            return None

    def delete_user(self, user_id: str) -> None:
        try:
            self.user_repository.delete_user(user_id)
        except Exception as e:
            print(f"Erreur lors de la suppression de l'utilisateur : {str(e)}")

    def get_all_users(self) -> List[User]:
        try:
            return self.user_repository.get_all_users()
        except Exception as e:
            print(f"Erreur lors de la récupération de tous les utilisateurs : {str(e)}")
            return []
    