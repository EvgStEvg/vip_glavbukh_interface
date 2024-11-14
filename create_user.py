# create_user.py
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_user(username, password, role):
    app = create_app()
    with app.app_context():
        # Проверка, существует ли уже пользователь с таким именем
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Пользователь с именем '{username}' уже существует.")
            return

        # Создание нового пользователя
        new_user = User(
            username=username,
            role=role
        )
        new_user.set_password(password)  # Установка пароля

        db.session.add(new_user)
        try:
            db.session.commit()
            print(f"Пользователь '{username}' создан успешно.")
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при создании пользователя: {e}")

if __name__ == '__main__':
    # Замените 'admin', 'your_secure_password', 'admin' на нужные значения
    create_user('admin', 'admin123', 'admin')

