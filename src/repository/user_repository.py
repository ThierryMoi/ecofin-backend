from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from model.user_model import User
from typing import List
from sqlalchemy import create_engine
from datetime import datetime  # Ajout de l'import pour datetime

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class UserRepository:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def create_user(self, user_data: dict):
        with self.session_scope() as session:
            try:
                user = User(**user_data)
                session.add(user)
                session.flush()  # Pour déclencher l'erreur de clé unique ici s'il y en a
                return user
            except Exception as e:
                session.rollback()
                raise e

    def get_user_by_id(self, user_id: str) -> User:
        with self.session_scope() as session:
            return session.query(User).filter_by(user_id=user_id).first()

    def update_user(self, user_id: str, new_data: dict) -> User:
        with self.session_scope() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                try:
                    for key, value in new_data.items():
                        setattr(user, key, value)
                    session.flush()  # Pour déclencher l'erreur de clé unique ici s'il y en a
                    return user
                except Exception as e:
                    session.rollback()
                    raise e

    def delete_user(self, user_id: str) -> None:
        with self.session_scope() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                try:
                    user.deleted_at = datetime.now()
                    session.flush()  # Pour déclencher l'erreur de clé unique ici s'il y en a
                except Exception as e:
                    session.rollback()
                    raise e

    def get_all_users(self) -> List[User]:
        with self.session_scope() as session:
            return session.query(User).filter(User.deleted_at == None).all()
