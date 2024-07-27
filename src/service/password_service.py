from datetime import datetime, timedelta

import secrets
from configuration.security import  PWD_CONTEXT

class PasswordResetService:
    
    def __init__(self, users_collection, password_resets_collection):
        self.users_collection = users_collection
        self.password_resets_collection = password_resets_collection

    def request_password_reset(self, email):
        user = self.users_collection.find_one({"email": email})
        if user:
            current_month = datetime.utcnow().month
            reset_requests_count = self.password_resets_collection.count_documents({
                "email": email,
                "created_at": {"$gte": datetime(datetime.utcnow().year, current_month, 1)}
            })

            if reset_requests_count >= 5:
                return {"message": "Limite de demandes de réinitialisation de mot de passe atteinte pour ce mois."}

            reset_token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(hours=1)

            self.password_resets_collection.insert_one({
                "email": email,
                "token": reset_token,
                "expires": expires,
                "created_at": datetime.utcnow()
            })

            return {"message": "Demande de réinitialisation du mot de passe envoyée avec succès.","token": reset_token}

        return {"message": "Adresse e-mail non trouvée."}

    def reset_password(self, token, new_password):
        reset_request = self.password_resets_collection.find_one({"token": token})
        if reset_request:
            if reset_request["expires"] > datetime.utcnow():
                email = reset_request["email"]
                user = self.users_collection.find_one({"email": email})
                user["hashed_password"] = PWD_CONTEXT.hash(new_password)
                
                self.password_resets_collection.delete_one({"token": token})
                
                return {"message": "Mot de passe réinitialisé avec succès."}
            else:
                return {"message": "Jeton de réinitialisation du mot de passe expiré."}

        return {"message": "Jeton de réinitialisation du mot de passe invalide."}