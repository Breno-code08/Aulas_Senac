import json
from pathlib import Path
from sqlalchemy import select, func
from app.extensions import db
from app.models import User, Professional, Category, Service, Favorite, ServiceRequest, Review, Message, AppMeta
from app.services.common import record

SEED_MODELS = {'users': User, 'professionals': Professional, 'categories': Category,
               'services': Service, 'requests': ServiceRequest, 'reviews': Review, 'messages': Message}

def seed_database():
    if db.session.get(AppMeta, 'seed_v1'):
        return
    data = json.loads((Path(__file__).parents[1] / 'seed.json').read_text())
    for table, model in SEED_MODELS.items():
        columns = [c.name for c in model.__table__.columns]
        for values in data[table]:
            if not db.session.get(model, values[0]):
                db.session.add(model(**dict(zip(columns, values))))
        db.session.flush()
    db.session.add(AppMeta(key='seed_v1', value='1'))
    db.session.commit()

def service_dict(service):
    p, u, c = service.professional, service.professional.user, service.category
    rating, count = db.session.execute(select(func.avg(Review.rating), func.count(Review.id)).where(Review.professional_id == p.id)).one()
    return {**record(service), 'category': c.name, 'icon': c.icon, 'user_id': u.id,
            'profession': p.profession, 'bio': p.bio, 'experience': p.experience,
            'name': u.name, 'neighborhood': u.neighborhood,
            'rating': round(rating or 0, 1), 'review_count': count}

def services(active=True, user_id=None):
    query = select(Service).order_by(Service.id)
    if active:
        query = query.where(Service.active == 1)
    if user_id:
        query = query.join(Professional).where(Professional.user_id == user_id)
    return [service_dict(s) for s in db.session.scalars(query)]

def request_dict(r):
    review = db.session.scalar(select(Review).where(Review.request_id == r.id))
    return {**record(r), 'title': r.service.title, 'price': r.service.price,
            'unit': r.service.unit, 'client_name': r.client.name,
            'professional_name': r.professional.user.name,
            'professional_user_id': r.professional.user_id,
            'review_id': review.id if review else None}

def requests_for(user):
    if not user:
        return []
    query = select(ServiceRequest).order_by(ServiceRequest.id.desc())
    if user.role == 'cliente':
        query = query.where(ServiceRequest.client_id == user.id)
    elif user.role == 'profissional':
        query = query.join(Professional).where(Professional.user_id == user.id)
    return [request_dict(r) for r in db.session.scalars(query)]
