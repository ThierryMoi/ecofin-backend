from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from model.user_model import User
from typing import List
from sqlalchemy import create_engine

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
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def create_user(self, user_data: dict) -> User:
        print(user_data)
        with self.session_scope() as session:
            user = User(**user_data)
            session.add(user)
            return user.dict()

    def get_user_by_id(self, user_id: str) -> User:
        with self.session_scope() as session:
            return session.query(User).filter_by(user_id=user_id).first()

    def update_user(self, user_id: str, new_data: dict) -> User:
        with self.session_scope() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                for key, value in new_data.items():
                    setattr(user, key, value)
                return user

    def delete_user(self, user_id: str) -> None:
        with self.session_scope() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.deleted_at = datetime.now()

    def get_all_users(self) -> List[User]:
        with self.session_scope() as session:
            return session.query(User).filter(User.deleted_at == None).all()
