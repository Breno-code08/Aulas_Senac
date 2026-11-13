from app.extensions import db

class ServiceRequest(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='RESTRICT'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete='RESTRICT'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    neighborhood = db.Column(db.String(60), nullable=False)
    preferred_date = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pendente')
    created_at = db.Column(db.String(30), nullable=False)
    client = db.relationship('User')
    professional = db.relationship('Professional')
    service = db.relationship('Service')
    __table_args__ = (db.CheckConstraint("status IN ('pendente','aceita','concluida','cancelada')"),)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id', ondelete='RESTRICT'), unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='RESTRICT'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(30), nullable=False)
    author = db.relationship('User')
    __table_args__ = (db.CheckConstraint('rating BETWEEN 1 AND 5'),)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id', ondelete='RESTRICT'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(30), nullable=False)
    sender = db.relationship('User')
