# app/history/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import History
import logging

history_bp = Blueprint('history', __name__)

logger = logging.getLogger(__name__)

@history_bp.route('/history', methods=['GET'])
@login_required
def history():
    """Отображает страницу истории."""
    try:
        user_histories = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()
        return render_template('history.html', histories=user_histories)
    except Exception as e:
        logger.error("Ошибка при загрузке истории", exc_info=True)
        flash("Произошла ошибка при загрузке истории", "danger")
        return redirect(url_for('dashboard.dashboard')), 500
