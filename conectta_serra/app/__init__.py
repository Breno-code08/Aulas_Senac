from flask import Flask, jsonify
from flask_wtf.csrf import CSRFError
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlite3 import Connection
from app.config import Config
from app.extensions import db, migrate, csrf

@event.listens_for(Engine, 'connect')
def foreign_keys(connection, _):
    if isinstance(connection, Connection):
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Defina SECRET_KEY no arquivo .env antes de iniciar.')
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    from app import models
    from app.routes.api import api_bp
    from app.routes.pages import pages_bp
    from app.services.common import ApiError
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)

    @app.errorhandler(ApiError)
    def api_error(error):
        db.session.rollback()
        return jsonify(error=error.message), error.status

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify(error='Sessão expirada. Recarregue a página.'), 403

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        db.session.rollback()
        message = 'Este registro possui vínculos ou já existe. Confira os dados.'
        return jsonify(error=message), 409

    @app.errorhandler(OperationalError)
    def database_error(error):
        db.session.rollback()
        app.logger.exception('Falha no banco de dados')
        return jsonify(error='Banco indisponível. Confira as migrations e tente novamente.'), 503

    @app.errorhandler(404)
    def missing(error):
        return jsonify(error='Página não encontrada.'), 404

    @app.errorhandler(500)
    def internal(error):
        db.session.rollback()
        return jsonify(error='Não foi possível concluir. Tente novamente.'), 500

    @app.cli.command('seed')
    def seed_command():
        from app.services.catalog import seed_database
        seed_database()
        print('Dados fictícios de demonstração criados.')

    @app.after_request
    def security(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        if response.content_type.startswith('application/json'):
            response.headers['Cache-Control'] = 'no-store'
        return response
    return app
