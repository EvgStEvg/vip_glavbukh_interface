# blueprints/consultations/__init__.py
from flask import Blueprint

consultations = Blueprint('consultations', __name__)

from . import routes
