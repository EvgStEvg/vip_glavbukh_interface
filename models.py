# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
import os

db = SQLAlchemy()

# Загрузка ключа из переменных окружения
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not set in environment variables")
fernet = Fernet(ENCRYPTION_KEY.encode())

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    histories = relationship("History", back_populates="user")
    credentials = relationship("UserCredentials", back_populates="user")
    
    @property
    def password(self):
        raise AttributeError('Пароль не может быть прочитан напрямую.')

    @password.setter
    def password(self, plaintext_password):
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self.password_hash, plaintext_password)

class History(db.Model):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    role = Column(String(20), default='user')

    user = relationship("User", back_populates="histories")

    @staticmethod
    def clear_user_history(user_id):
        try:
            History.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing history: {e}")
            return False

    def __repr__(self):
        return f'<History {self.id}>'

class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'
    id = Column(Integer, primary_key=True)
    system_name = Column(String(100), nullable=False)
    system_username = Column(String(150), nullable=False)
    _system_password = Column("system_password", String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    user = relationship("User", back_populates="credentials")

    @property
    def system_password(self):
        # Дешифрование пароля с обработкой ошибки
        try:
            return fernet.decrypt(self._system_password.encode()).decode()
        except InvalidToken:
            return None

    @system_password.setter
    def system_password(self, plaintext_password):
        # Шифрование пароля
        self._system_password = fernet.encrypt(plaintext_password.encode()).decode()
