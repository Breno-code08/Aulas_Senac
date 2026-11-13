from datetime import datetime, timezone
from flask import session
from app.extensions import db
from app.models import User
import math

class ApiError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status

def fail(message, status=400):
    raise ApiError(message, status)

def now():
    return datetime.now(timezone.utc).isoformat()

def text(value, minimum=2, maximum=200):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        fail(f'Preencha os campos com {minimum} a {maximum} caracteres.')
    return value.strip()

def number(value, minimum=0, maximum=1000000):
    try:
        result = float(value)
    except (ValueError, TypeError):
        fail('Informe um valor numérico válido.')
    if not math.isfinite(result) or not minimum <= result <= maximum:
        fail('Informe um valor numérico válido.')
    return result

def current_user():
    return db.session.get(User, session.get('user_id')) if session.get('user_id') else None

def require(*roles):
    user = current_user()
    if not user:
        fail('Entre em uma conta para continuar.', 401)
    if user.role not in roles:
        fail('Seu perfil não tem acesso a esta ação.', 403)
    return user

def record(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

def get_or_fail(model, record_id):
    obj = db.session.get(model, record_id)
    if obj is None:
        fail('Registro não encontrado.', 404)
    return obj
