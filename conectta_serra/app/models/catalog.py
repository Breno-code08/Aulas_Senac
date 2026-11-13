from app.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    icon = db.Column(db.String(30), nullable=False, default='tools')

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='RESTRICT'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), nullable=False, default='serviço')
    active = db.Column(db.Integer, nullable=False, default=1)
    professional = db.relationship('Professional')
    category = db.relationship('Category')
    __table_args__ = (db.CheckConstraint('price >= 0'),)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), primary_key=True)
