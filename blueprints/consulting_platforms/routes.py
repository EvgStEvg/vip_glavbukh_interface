# blueprints/consulting_platforms/routes.py

import os
import openai
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, History, User, UserCredentials
from forms import ConsultationForm, CredentialsForm

from . import consulting_platforms_bp  # Импортируем Blueprint

def get_system_display_name(system_key):
    """Возвращает читаемое название системы по ключу."""
    systems = {
        'glavbukh': 'Главбух',
        'consultant_plus': 'Консультант Плюс'
    }
    return systems.get(system_key, system_key)

@consulting_platforms_bp.route('/', methods=['GET', 'POST'])
@login_required
def consulting_platforms():
    form = ConsultationForm()
    if form.validate_on_submit():
        search_query = form.search_query.data
        # Здесь добавьте логику отправки запросов во все системы и получение ответов
        # Пример:
        responses = [
            {
                'system_name': 'n8n',
                'response': 'Ответ от n8n',
                'direct_link': 'http://n8n-system-link.com'
            },
            {
                'system_name': 'MetaGPT',
                'response': 'Ответ от MetaGPT',
                'direct_link': 'http://metagpt-system-link.com'
            }
        ]

        # Сохранение в историю
        history_entry = History(
            search_query=search_query,
            response='; '.join([resp['response'] for resp in responses]),
            timestamp=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(history_entry)
        db.session.commit()

        # Проверка, является ли запрос AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Возвращение JSON-ответа
            return jsonify({
                'success': True,
                'responses': responses,
                'histories': [
                    {
                        'search_query': history_entry.search_query,
                        'response': history_entry.response,
                        'timestamp': history_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
                ]
            })
        else:
            flash('Запрос отправлен успешно!', 'success')
            return redirect(url_for('consulting_platforms.consulting_platforms'))

    # Обработка GET-запросов
    responses = []  # Здесь можно загрузить последние ответы, если необходимо
    histories = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()
    return render_template('consulting_platforms.html', form=form, responses=responses, histories=histories)

@consulting_platforms_bp.route('/manage_credentials', methods=['GET', 'POST'])
@login_required
def manage_credentials():
    form = CredentialsForm()
    if form.validate_on_submit():
        system_name = form.system_name.data
        system_username = form.system_username.data
        system_password = form.system_password.data

        # Проверяем, существует ли уже запись для данной системы
        existing_credentials = UserCredentials.query.filter_by(user_id=current_user.id, system_name=system_name).first()
        if existing_credentials:
            flash(f"Учетные данные для системы '{system_name}' уже существуют.", "warning")
            return redirect(url_for('consulting_platforms.manage_credentials'))

        # Создаём новую запись
        new_credentials = UserCredentials(
            system_name=system_name,
            system_username=system_username,
            user_id=current_user.id
        )
        new_credentials.system_password = system_password  # Используем свойство для шифрования

        db.session.add(new_credentials)
        db.session.commit()
        flash(f"Учетные данные для системы '{system_name}' успешно сохранены.", "success")
        return redirect(url_for('consulting_platforms.manage_credentials'))

    # Получаем все учетные данные пользователя
    user_credentials = UserCredentials.query.filter_by(user_id=current_user.id).all()
    return render_template('manage_credentials.html', form=form, credentials=user_credentials)

@consulting_platforms_bp.route('/delete_credentials/<int:credential_id>', methods=['POST'])
@login_required
def delete_credentials(credential_id):
    credential = UserCredentials.query.get_or_404(credential_id)
    if credential.user_id != current_user.id:
        flash("У вас нет прав для удаления этих учетных данных.", "danger")
        return redirect(url_for('consulting_platforms.manage_credentials'))

    db.session.delete(credential)
    db.session.commit()
    flash(f"Учетные данные для системы '{credential.system_name}' успешно удалены.", "success")
    return redirect(url_for('consulting_platforms.manage_credentials'))
