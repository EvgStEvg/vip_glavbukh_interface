# blueprints/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User  # Добавлен импорт db
from . import auth_bp
from auth import Auth  # Импортируйте ваш класс Auth
import logging
from forms import LoginForm, RegistrationForm  # Импортируйте формы

auth = Auth()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Создаём экземпляр формы
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = auth.authenticate(username, password)
        if user:
            login_user(user)
            logging.info(f"Пользователь {username} успешно вошел в систему.")
            flash("Вы успешно вошли в систему", "success")
            return redirect(url_for('main.dashboard'))
        else:
            logging.warning(f"Неудачная попытка входа для пользователя {username}.")
            flash("Неверные учетные данные", "danger")
            return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)  # Передаём форму в шаблон

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    logging.info("Пользователь вышел из системы.")
    flash("Вы успешно вышли из системы", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Проверьте, существует ли пользователь с таким именем
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Имя пользователя уже существует", "danger")
            return redirect(url_for('auth.register'))
        # Создайте нового пользователя
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Пользователь успешно зарегистрирован", "success")
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)  # Передаём форму в шаблон
