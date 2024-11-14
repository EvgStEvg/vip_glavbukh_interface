# blueprints/consultations/routes.py

import os
from typing import List, Dict, Optional
from datetime import datetime
from functools import lru_cache
import logging
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai import OpenAIError, RateLimitError, AuthenticationError, BadRequestError
from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for, session
from flask_login import login_required, current_user
from langchain_google_community import GoogleSearchAPIWrapper
from bs4 import BeautifulSoup
import requests
import re
from models import db, History
from forms import ConsultationForm
from . import consultations  # Импортируем существующий Blueprint
from markupsafe import Markup  # Добавляем этот импорт

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """Вы - опытный консультант по налоговому и бухгалтерскому учету с 15-летним стажем работы в крупных консалтинговых компаниях.

Ваша задача - давать четкие, структурированные ответы на вопросы пользователей, основываясь на актуальном законодательстве и предоставленном контексте.

При ответе придерживайтесь следующей структуры:
1. Краткий прямой ответ на вопрос
2. Подробное объяснение со ссылками на нормативные документы
3. Важные примечания или предупреждения (если применимо)

Всегда указывайте источники информации и актуальные нормы законодательства."""

TRUSTED_DOMAINS = [
    "consultant.ru",
    "garant.ru",
    "minfin.gov.ru",
    "nalog.gov.ru",
    "publication.pravo.gov.ru",
    "buh.ru",
    "glavbukh.ru"
]

class SearchError(Exception):
    """Пользовательское исключение для ошибок поиска"""
    pass

@lru_cache(maxsize=100)
def cache_search_results(query: str) -> List[Dict]:
    """Кэширование результатов поиска для оптимизации производительности"""
    return search_accounting_info(query)

def search_accounting_info(query: str) -> List[Dict]:
    """Поиск актуальной информации на профессиональных ресурсах"""
    try:
        search = GoogleSearchAPIWrapper(
            google_api_key=GOOGLE_API_KEY,
            google_cse_id=GOOGLE_CSE_ID
        )
        
        # Расширяем поиск, добавляя специфические запросы
        search_queries = [
            f"{query} site:nalog.gov.ru",  # Сайт ФНС
            f"{query} site:consultant.ru судебная практика",  # Судебная практика
            f"{query} site:garant.ru НК РФ статья",  # Статьи НК РФ
            f"{query} site:minfin.gov.ru письмо",  # Письма Минфина
            f"{query} site:kad.arbitr.ru"  # Картотека арбитражных дел
        ]
        
        results_text = []
        for search_query in search_queries:
            try:
                search_results = search.results(search_query, num_results=2)
                
                for result in search_results:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    }
                    
                    response = requests.get(
                        result["link"], 
                        timeout=10,
                        headers=headers,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Ищем основной контент
                    content_div = (
                        soup.find('div', class_='content') or
                        soup.find('div', class_='document-content') or
                        soup.find('div', class_='legal-text') or
                        soup.find('main') or
                        soup
                    )
                    
                    text = content_div.get_text()
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        domain = "Неизвестный источник"
                        if 'nalog.gov.ru' in result["link"]:
                            domain = "ФНС России"
                        elif 'consultant.ru' in result["link"]:
                            domain = "КонсультантПлюс"
                        elif 'garant.ru' in result["link"]:
                            domain = "Гарант"
                        elif 'minfin.gov.ru' in result["link"]:
                            domain = "Минфин России"
                        elif 'kad.arbitr.ru' in result["link"]:
                            domain = "Картотека арбитражных де"
                        
                        results_text.append({
                            "source": result["link"],
                            "content": text[:5000],  # Увеличваем размер контекста
                            "title": result.get("title", "Без названия"),
                            "domain": domain
                        })
                        logger.info(f"Successfully processed result from {result['link']}")
                        
            except Exception as e:
                logger.error(f"Error processing search result: {e}")
                continue
                
        return results_text
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

def process_consultation(question: str) -> tuple[str, List[Dict]]:
    """Обработка консультационного запроса"""
    try:
        # Поиск релевантной информации
        search_results = search_accounting_info(question)
        
        # Подготовка контекста с более детальной информацией
        context_parts = []
        for i, result in enumerate(search_results):
            source_type = "неизвестный источник"
            if 'nalog.gov.ru' in result['source']:
                source_type = "официальная позиция ФНС России"
            elif 'kad.arbitr.ru' in result['source']:
                source_type = "судебная практика"
            elif 'minfin.gov.ru' in result['source']:
                source_type = "разъяснения Минфина России"
            elif 'consultant.ru' in result['source'] or 'garant.ru' in result['source']:
                source_type = "нормативно-правовая база"
            
            context_parts.append(f"""
Источник {i+1} ({source_type}):
URL: {result['source']}
Заголовок: {result['title']}
Содержание: {result['content']}
            """)
        
        context = "\n\n".join(context_parts)
        
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""
            Вопрос пользователя: {question}
            
            Дата запроса: {current_date}
            
            Найденная информация:
            {context}
            
            Пожалуйста, проанализируйте предоставленную информацию и дайте профессиональный ответ, учитывая все требования к структуре и содержанию.
            """}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            response_format={ "type": "text" }
        )
        
        return response.choices[0].message.content, search_results
    except Exception as e:
        logger.error(f"Error processing consultation: {e}")
        raise

def get_user_history(user_id: int, limit: int = 10) -> List[History]:
    """Получение истории сообщений пользователя"""
    return History.query.filter_by(user_id=user_id).order_by(History.timestamp.desc()).limit(limit).all()

def save_messages(user_id: int, user_query: str, assistant_response: str, sources: List[Dict]) -> None:
    """Сохранение сообщений в базу данных"""
    try:
        user_message = History(
            user_id=user_id,
            message=user_query,
            role='user'
        )
        
        # Добавляем источники к ответу ассистента
        response_with_sources = assistant_response + "\n\nИсточники:\n"
        for source in sources:
            response_with_sources += f"- {source['title']}: {source['source']}\n"
        
        assistant_message = History(
            user_id=user_id,
            message=response_with_sources,
            role='assistant'
        )
        
        db.session.add_all([user_message, assistant_message])
        db.session.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.session.rollback()
        raise

def nl2br(value):
    """Конвертирует переносы строк в HTML-теги <br>"""
    if not value:
        return ""
    return Markup(value.replace('\n', '<br>\n'))

@consultations.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = ConsultationForm()
    # Получаем текущую сесию диалога из сессии Flask
    current_session = session.get('current_consultation', [])
    return render_template('consultations/index.html', 
                         form=form, 
                         current_session=current_session)

@consultations.route('/send', methods=['POST'])
@login_required
def send():
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({'success': False, 'message': 'Сообщение не может быть пустым'})
        
        try:
            # Получаем результаты поиска
            search_results = search_accounting_info(message)
            
            # Формируем контекст из результатов поиска
            context_parts = []
            for result in search_results:
                context_parts.append(f"""
                Источник: {result['domain']}
                Заголовок: {result['title']}
                Содержание: {result['content']}
                """)
            
            context = "\n\n".join(context_parts)
            
            # Формируем сообщения для GPT
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
                Вопрос пользователя: {message}
                
                Контекст из нормативных документов:
                {context}
                """}
            ]
            
            # Отправляем запрос к OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Получаем ответ ассистента
            assistant_response = response.choices[0].message.content
            
            # Сохраняем сообщения в базу данных
            save_messages(current_user.id, message, assistant_response, search_results)
            
            # Возвращаем успешный ответ с текстом ответа ассистента
            return jsonify({
                'success': True,
                'response': assistant_response
            })
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return jsonify({
                'success': False,
                'message': 'Ошибка при обработке сообщения'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Ошибка при отправке сообщения: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Произошла ошибка при отправке сообщения'
        }), 500

@consultations.route('/end_session', methods=['POST'])
@login_required
def end_session():
    try:
        # Получаем текущую сессию
        current_session = session.get('current_consultation', [])
        
        # Сохраняем всю сессию в историю
        for message in current_session:
            history_item = History(
                user_id=current_user.id,
                message=message['message'],
                role=message['role'],
                timestamp=message['timestamp']
            )
            db.session.add(history_item)
        
        db.session.commit()
        
        # Очищаем текущую сессию
        session.pop('current_consultation', None)
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@consultations.route('/clear_history', methods=['POST'])
@login_required
def clear_history():
    try:
        # Удаляем всю историю пользователя
        History.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'История успешно очищена'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка при очистке истории: {str(e)}'}), 500

@consultations.route('/history/delete/<int:history_id>', methods=['POST'])
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

@consultations.route('/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    try:
        message = History.query.get_or_404(message_id)
        
        # Проверяем, принадлежит ли сообщение текущему пользователю
        if message.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Доступ запрещен'}), 403
            
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500