# blueprints/consulting platforms/__init__.py
from flask import Blueprint

consulting_platforms_bp = Blueprint('consulting_platforms', __name__, template_folder='templates')

from . import routes  # Импортируем маршруты
