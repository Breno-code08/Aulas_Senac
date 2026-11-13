from datetime import date
import re
from flask import Blueprint, jsonify, request, session, current_app
from flask_wtf.csrf import generate_csrf
from sqlalchemy import select
from app.extensions import db
from app.models import User, Professional, Category, Service, Favorite, ServiceRequest, Review, Message
from app.services.common import fail, text, number, require, record, get_or_fail, current_user, now
from app.services.catalog import seed_database, services, service_dict, requests_for
from app.services.reports import export_report

api_bp = Blueprint('api', __name__, url_prefix='/api')

def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        fail('Dados inválidos.')
    return data

def done():
    db.session.commit()
    return jsonify(ok=True)

def email(value):
    value = text(value, 5, 120).lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
        fail('Informe um e-mail válido.')
    return value

def owned_request(record_id):
    user = require('cliente', 'profissional', 'admin')
    r = get_or_fail(ServiceRequest, record_id)
    if user.role != 'admin' and user.id not in (r.client_id, r.professional.user_id):
        fail('Acesso não permitido.', 403)
    return r, user

@api_bp.get('/bootstrap')
def bootstrap():
    if current_app.config['DEMO_MODE']:
        seed_database()
    user = current_user()
    favorites = list(db.session.scalars(select(Favorite.professional_id).where(Favorite.user_id == user.id))) if user else []
    return jsonify(user=record(user) if user else None, csrf=generate_csrf(),
                   categories=[record(c) for c in db.session.scalars(select(Category).order_by(Category.id))],
                   services=services(), favorites=favorites, requests=requests_for(user), demo=current_app.config['DEMO_MODE'])

@api_bp.post('/session')
def choose_persona():
    if not current_app.config['DEMO_MODE']:
        fail('A troca de perfis está desativada.', 403)
    user_id = {'cliente': 1, 'profissional': 2, 'admin': 3}.get(body().get('role'))
    if not user_id:
        fail('Perfil inválido.')
    get_or_fail(User, user_id)
    session['user_id'] = user_id
    return jsonify(ok=True)

@api_bp.post('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify(ok=True)

def user_fields(b):
    def required(key, label, minimum, maximum):
        value = b.get(key)
        if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
            fail(f'Informe {label} com {minimum} a {maximum} caracteres.')
        return value.strip()
    phone = str(b.get('phone') or '').strip()
    if len(phone) > 30:
        fail('O telefone deve ter no máximo 30 caracteres.')
    return dict(name=required('name', 'o nome completo', 3, 80),
                email=email(required('email', 'um e-mail', 5, 120)),
                phone=phone, neighborhood=required('neighborhood', 'o bairro', 2, 60))

@api_bp.post('/register')
@api_bp.post('/register/users', defaults={'registration_role':'cliente'})
@api_bp.post('/register/professionals', defaults={'registration_role':'profissional'})
def register(registration_role=None):
    b = body()
    registration_role = registration_role or b.get('role')
    if registration_role not in ('cliente', 'profissional'):
        fail('Perfil inválido.')
    if b.get('role') and b['role'] != registration_role:
        fail('Utilize a área de cadastro correspondente ao seu perfil.')
    fields = user_fields(b)
    if db.session.scalar(select(User.id).where(User.email == fields['email'])):
        fail('Já existe um cadastro com este e-mail.', 409)
    profession = None
    if registration_role == 'profissional':
        profession = b.get('profession')
        if not isinstance(profession, str) or not 3 <= len(profession.strip()) <= 80:
            fail('Informe sua profissão com 3 a 80 caracteres.')
    user = User(**fields, role=registration_role)
    db.session.add(user)
    db.session.flush()
    if profession is not None:
        db.session.add(Professional(user_id=user.id, profession=profession.strip(),
                                    bio='Novo profissional no Conectta Serra.', experience=1))
    db.session.commit()
    session['user_id'] = user.id
    return jsonify(ok=True)

@api_bp.get('/professionals/<int:record_id>')
def professional(record_id):
    p = get_or_fail(Professional, record_id)
    service_rows = db.session.scalars(select(Service).where(Service.professional_id == p.id, Service.active == 1))
    reviews = db.session.scalars(select(Review).where(Review.professional_id == p.id).order_by(Review.id.desc()))
    return jsonify(professional={**record(p), 'name': p.user.name, 'neighborhood': p.user.neighborhood},
                   services=[service_dict(s) for s in service_rows],
                   reviews=[{**record(r), 'name': r.author.name} for r in reviews])

@api_bp.post('/favorites')
def favorite():
    user = require('cliente', 'profissional', 'admin')
    b = body()
    p = get_or_fail(Professional, int(number(b.get('professional_id'), 1)))
    f = db.session.get(Favorite, (user.id, p.id))
    if b.get('saved') and not f:
        db.session.add(Favorite(user_id=user.id, professional_id=p.id))
    elif not b.get('saved') and f:
        db.session.delete(f)
    return done()

@api_bp.post('/requests')
def create_request():
    user = require('cliente')
    b = body()
    s = get_or_fail(Service, int(number(b.get('service_id'), 1)))
    if not s.active:
        fail('Serviço indisponível.')
    try:
        preferred = date.fromisoformat(b.get('preferred_date', ''))
    except (ValueError, TypeError):
        fail('Informe uma data válida.')
    if preferred < date.today():
        fail('Escolha uma data a partir de hoje.')
    db.session.add(ServiceRequest(client_id=user.id, professional_id=s.professional_id, service_id=s.id,
                                  description=text(b.get('description'), 10, 1500),
                                  neighborhood=text(b.get('neighborhood'), 2, 60),
                                  preferred_date=preferred.isoformat(), status='pendente', created_at=now()))
    return done()

@api_bp.patch('/requests/<int:record_id>')
def update_request(record_id):
    r, user = owned_request(record_id)
    status = body().get('status')
    accepted = r.status == 'pendente' and status == 'aceita' and (user.role == 'admin' or user.id == r.professional.user_id)
    cancelled = r.status in ('pendente', 'aceita') and status == 'cancelada' and (user.role == 'admin' or user.id == r.client_id)
    completed = r.status == 'aceita' and status == 'concluida' and (user.role == 'admin' or user.id == r.client_id)
    if not (accepted or cancelled or completed):
        fail('Essa alteração de status não está disponível.', 409)
    r.status = status
    return done()

@api_bp.route('/requests/<int:record_id>/messages', methods=['GET', 'POST'])
def messages(record_id):
    r, user = owned_request(record_id)
    if request.method == 'GET':
        records = db.session.scalars(select(Message).where(Message.request_id == r.id).order_by(Message.id))
        return jsonify([{**record(m), 'sender_name': m.sender.name} for m in records])
    db.session.add(Message(request_id=r.id, sender_id=user.id, body=text(body().get('body'), 1, 2000), created_at=now()))
    return done()

@api_bp.post('/reviews')
def reviews():
    user = require('cliente')
    b = body()
    r, _ = owned_request(int(number(b.get('request_id'), 1)))
    if r.client_id != user.id or r.status != 'concluida':
        fail('Avalie somente um serviço seu concluído.', 403)
    rating = number(b.get('rating'), 1, 5)
    if not rating.is_integer():
        fail('Escolha de 1 a 5 estrelas.')
    db.session.add(Review(request_id=r.id, author_id=user.id, professional_id=r.professional_id,
                          rating=int(rating), comment=text(b.get('comment'), 5, 1000), created_at=now()))
    return done()

@api_bp.get('/manage')
def manage():
    user = require('admin', 'profissional')
    p = db.session.scalar(select(Professional).where(Professional.user_id == user.id))
    return jsonify(users=[record(u) for u in db.session.scalars(select(User).order_by(User.id))] if user.role == 'admin' else [],
                   categories=[record(c) for c in db.session.scalars(select(Category).order_by(Category.id))],
                   services=services(active=False, user_id=user.id if user.role == 'profissional' else None),
                   professional=record(p) if p else None, requests=requests_for(user))

@api_bp.get('/users')
@api_bp.get('/users/<int:record_id>')
def consult_users(record_id=None):
    require('admin')
    if record_id is not None:
        return jsonify(record(get_or_fail(User, record_id)))
    query = select(User).order_by(User.id)
    if request.args.get('role'):
        query = query.where(User.role == request.args['role'])
    result = [record(u) for u in db.session.scalars(query)]
    import unicodedata
    def normalize(value):
        return ''.join(c for c in unicodedata.normalize('NFD', value) if not unicodedata.combining(c)).lower()
    search = normalize(request.args.get('q', '').strip())
    if search:
        result = [u for u in result if search in normalize(u['name']+' '+u['email']+' '+u['neighborhood'])]
    return jsonify(result)

@api_bp.route('/users', methods=['POST'])
@api_bp.route('/users/<int:record_id>', methods=['PUT', 'DELETE'])
def users(record_id=None):
    user = require('admin')
    target = get_or_fail(User, record_id) if record_id else None
    if request.method == 'DELETE':
        if target.id == user.id:
            fail('Você não pode excluir o usuário conectado.')
        if target.demo:
            fail('Os perfis de demonstração são preservados. Crie um usuário para testar a exclusão.')
        db.session.delete(target)
    else:
        b = body()
        if target is None:
            target = User(role='cliente')
            db.session.add(target)
        fields = user_fields(b)
        with db.session.no_autoflush:
            duplicate = db.session.scalar(select(User).where(User.email == fields['email']))
        if duplicate is not None and duplicate.id != target.id:
            fail('Já existe um cadastro com este e-mail.', 409)
        for key, value in fields.items():
            setattr(target, key, value)
    return done()

@api_bp.route('/categories', methods=['POST'])
@api_bp.route('/categories/<int:record_id>', methods=['PUT', 'DELETE'])
def categories(record_id=None):
    require('admin')
    target = get_or_fail(Category, record_id) if record_id else None
    if request.method == 'DELETE':
        db.session.delete(target)
    else:
        if target is None:
            target = Category(icon='tools')
            db.session.add(target)
        target.name = text(body().get('name'), 2, 60)
    return done()

@api_bp.route('/services', methods=['POST'])
@api_bp.route('/services/<int:record_id>', methods=['PUT', 'DELETE'])
def service_crud(record_id=None):
    user = require('admin', 'profissional')
    p = db.session.scalar(select(Professional).where(Professional.user_id == user.id))
    target = get_or_fail(Service, record_id) if record_id else None
    if target and user.role != 'admin' and target.professional_id != p.id:
        fail('Você só pode editar seus serviços.', 403)
    if request.method == 'DELETE':
        db.session.delete(target)
    else:
        b = body()
        if target is None:
            pid = p.id if p else int(number(b.get('professional_id'), 1))
            get_or_fail(Professional, pid)
            target = Service(professional_id=pid)
            db.session.add(target)
        target.title = text(b.get('title'), 3, 100)
        target.description = text(b.get('description'), 10, 1500)
        target.price = number(b.get('price'))
        target.unit = text(b.get('unit'), 1, 30)
        with db.session.no_autoflush:
            target.category_id = get_or_fail(Category, int(number(b.get('category_id'), 1))).id
        target.active = 0 if b.get('active') is False else 1
    return done()

@api_bp.put('/profile')
def profile():
    user = require('profissional')
    p = db.session.scalar(select(Professional).where(Professional.user_id == user.id))
    b = body()
    p.profession = text(b.get('profession'), 3, 80)
    p.bio = text(b.get('bio'), 10, 1500)
    p.experience = int(number(b.get('experience'), 0, 60))
    return done()

@api_bp.get('/reports')
def reports():
    user = require('admin')
    records = requests_for(user)
    filters = request.args
    records = [r for r in records if (not filters.get('status') or r['status'] == filters['status'])
               and (not filters.get('from') or r['created_at'][:10] >= filters['from'])
               and (not filters.get('to') or r['created_at'][:10] <= filters['to'])]
    if filters.get('format') in ('csv', 'pdf'):
        return export_report(records, filters['format'], filters)
    return jsonify(records)
