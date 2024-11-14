# auth.py
from typing import Optional
from models import User, db
from werkzeug.security import check_password_hash

class Auth:
    """Класс для обработки процессов аутентификации пользователей."""

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Аутентифицирует пользователя по имени пользователя и паролю.

        Args:
            username (str): Имя пользователя.
            password (str): Пароль пользователя.

        Returns:
            Optional[User]: Объект User при успешной аутентификации, иначе None.
        """
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    def logout(self) -> None:
        """Выходит из текущего пользователя."""
        pass  # Логика выхода может быть добавлена при необходимости

    def is_authenticated(self, user) -> bool:
        """
        Проверяет, аутентифицирован ли пользователь.

        Args:
            user (User): Объект пользователя.

        Returns:
            bool: True, если аутентифицирован, иначе False.
        """
        return user.is_authenticated
