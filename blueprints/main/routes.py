# blueprints/main/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from models import db, History, User
from . import main_bp
import logging
import requests
import os  # Добавлен импорт os
from datetime import datetime, timedelta
from collections import defaultdict
from forms import ConsultantPlusForm, SettingsForm  # Импортируйте формы
from faq import FAQ  # Импортируйте класс FAQ

faq = FAQ()  # Инициализируйте FAQ

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Отображает панель управления после успешного входа."""
    username = current_user.username  # Получаем имя пользователя
    
    # Получение всех запросов текущего пользователя
    user_histories = History.query.filter_by(user_id=current_user.id).all()
    
    # Подготовка данных для графика: количество запросов за последние 7 дней
    today = datetime.utcnow().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]  # Последние 7 дней
    date_labels = [date.strftime('%d.%m') for date in dates]
    
    # Инициализация словаря для подсчета запросов по датам
    query_counts = defaultdict(int)
    for history in user_histories:
        history_date = history.timestamp.date()
        if history_date in dates:
            query_counts[history_date] += 1
    
    # Подготовка данных в нужном порядке
    data_counts = [query_counts[date] for date in dates]
    
    return render_template('dashboard.html', username=username, date_labels=date_labels, data_counts=data_counts)

@main_bp.route('/history')
@login_required
def history():
    history_items = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()
    return render_template('history.html', history=history_items)

@main_bp.route('/history/delete/<int:history_id>', methods=['POST'])
@login_required
def delete_history_item(history_id):
    try:
        history_item = History.query.get_or_404(history_id)
        
        # Проверяем, принадлежит ли запись текущему пользователю
        if history_item.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Доступ запрещен'}), 403
            
        db.session.delete(history_item)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/faq', methods=['GET'])
def faq_route():
    """Возвращает список FAQ как HTML."""
    try:
        faq_items = faq.load_faq()
        return render_template('faq.html', faq_items=faq_items), 200
    except Exception as e:
        logging.error("Ошибка при загрузке FAQ", exc_info=True)
        flash("Ошибка при загрузке FAQ", "danger")
        return redirect(url_for('main.dashboard')), 500

@main_bp.route('/', methods=['GET'])
def index():
    """Перенаправляет на панель управления или страницу входа в зависимости от статуса пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('auth.login'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Отображает страницу настроек."""
    form = SettingsForm()
    if form.validate_on_submit():
        new_username = form.username.data
        new_password = form.password.data

        if new_username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user and existing_user.id != current_user.id:
                flash("Им�� пользователя уже занято", "danger")
                return redirect(url_for('main.settings'))
            current_user.username = new_username
        if new_password:
            current_user.set_password(new_password)
        db.session.commit()
        flash("Настройки обновлены", "success")
        return redirect(url_for('main.settings'))

    return render_template('settings.html', form=form)


@main_bp.route('/consultant_plus', methods=['GET', 'POST'])
@login_required
def consultant_plus():
    """Отображает страницу модуля ConsultantPlus."""
    form = ConsultantPlusForm()
    if form.validate_on_submit():
        user_query = form.query.data
        if not user_query:
            flash("Запрос не может быть пустым", "warning")
            return redirect(url_for('main.consultant_plus'))

        try:
            # Отправка запроса в n8n
            n8n_response = send_to_n8n({'query': user_query, 'user': current_user.username})

            if n8n_response.get('status') == 'success':
                response = n8n_response.get('data')
                # Сохранение в историю
                history = History(search_query=user_query, response=response, user_id=current_user.id)
                db.session.add(history)
                db.session.commit()
                flash("Запрос выполнен успешно", "success")
                return render_template('consultant_plus.html', form=form, response=response)
            else:
                flash("Не удалось обработать запрос", "danger")
                return render_template('consultant_plus.html', form=form)
        except Exception as e:
            logging.error("Ошибка при обработке запроса", exc_info=True)
            flash("Произошла ошибка при обработке запроса", "danger")
            return render_template('consultant_plus.html', form=form)
    
    return render_template('consultant_plus.html', form=form)

@main_bp.route('/query', methods=['POST'])
@login_required
def query_route_api():
    """Обрабатывает запросы пользователей и взаимодействует с n8n и MetaGPT."""
    try:
        user_query = request.json.get('query')
        if not user_query:
            return jsonify({"error": "Запрос отсутствует"}), 400

        # Отправка запроса в n8n
        n8n_response = send_to_n8n({'query': user_query, 'user': current_user.username})

        if n8n_response.get('status') == 'success':
            response = n8n_response.get('data')
            # Сохранение в историю
            history = History(search_query=user_query, response=response, user_id=current_user.id)
            db.session.add(history)
            db.session.commit()
            return jsonify({"response": response}), 200
        else:
            return jsonify({"error": "Не удалось обработать запрос"}), 500
    except Exception as e:
        logging.error("Ошибка при обработке запроса", exc_info=True)
        return jsonify({"error": "Произошла ошибка"}), 500

def send_to_n8n(data):
    """Отправляет данные на вебхук n8n и возвращает ответ."""
    webhook_url = os.getenv('N8N_WEBHOOK_URL')
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"n8n ответил статусом {response.status_code}")
            return {"status": "error"}
    except Exception as e:
        logging.error("Ошибка при отправке данных в n8n", exc_info=True)
        return {"status": "error"}
