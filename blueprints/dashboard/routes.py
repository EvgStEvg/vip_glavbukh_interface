# app/dashboard/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import History
from collections import defaultdict
from datetime import datetime, timedelta
import logging

dashboard_bp = Blueprint('dashboard', __name__)

logger = logging.getLogger(__name__)

@dashboard_bp.route('/dashboard')
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
