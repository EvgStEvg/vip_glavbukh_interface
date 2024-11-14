# app.py

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User, History
from auth import Auth
from faq import FAQ
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.consulting_platforms import consulting_platforms_bp
from flask_wtf import CSRFProtect
import logging
from blueprints.consultations import consultations

# Инициализация Flask приложения
app = Flask(__name__)

# Конфигурация приложения
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db.init_app(app)
migrate = Migrate(app, db)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Инициализация CSRFProtect
csrf = CSRFProtect(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Регистрация Blueprint'ов
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(consultations, url_prefix='/consultations')
app.register_blueprint(consulting_platforms_bp, url_prefix='/consulting_platforms')

# Определение загрузчика пользователей для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Загружает пользователя по ID."""
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None

# Основной маршрут (например, главная страница)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)
    return "<br>".join(output)

# Другие маршруты и логика...
@app.context_processor
def utility_processor():
    from blueprints.consulting_platforms.routes import get_system_display_name
    return dict(get_system_display_name=get_system_display_name)

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080)
