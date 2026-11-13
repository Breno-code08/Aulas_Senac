from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False, default='')
    role = db.Column(db.String(20), nullable=False)
    neighborhood = db.Column(db.String(60), nullable=False, default='Centro')
    demo = db.Column(db.Integer, nullable=False, default=0)
    __table_args__ = (db.CheckConstraint("role IN ('cliente','profissional','admin')"),)

class Professional(db.Model):
    __tablename__ = 'professionals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), unique=True, nullable=False)
    profession = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Integer, nullable=False, default=1)
    user = db.relationship('User')

class AppMeta(db.Model):
    __tablename__ = 'app_meta'
    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.Text, nullable=False)
