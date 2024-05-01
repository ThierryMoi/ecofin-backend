from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from model.message_model import Message
from typing import List
from sqlalchemy import create_engine
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class MessageRepository:
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

    def create_message(self, message_data: dict) -> Message:
        print(message_data)
        with self.session_scope() as session:
            message = Message(**message_data)
            session.add(message)
            return message.dict()

    def get_message_by_id(self, message_id: str) -> Message:
        with self.session_scope() as session:
            return session.query(Message).filter_by(message_id=message_id).first()

    def update_message(self, message_id: str, new_data: dict) -> Message:
        with self.session_scope() as session:
            message = session.query(Message).filter_by(message_id=message_id).first()
            if message:
                for key, value in new_data.items():
                    setattr(message, key, value)
                return message

    def delete_message(self, message_id: str) -> None:
        with self.session_scope() as session:
            message = session.query(Message).filter_by(message_id=message_id).first()
            if message:
                message.deleted_at = datetime.now()

    def get_all_messages(self) -> List[Message]:
        with self.session_scope() as session:
            return session.query(Message).filter(Message.deleted_at == None).all()
