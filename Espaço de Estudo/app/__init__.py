from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
from flask_login import current_user

from app.extensions import csrf, db, login_manager, migrate


def create_app(test_config=None):
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    from app.config import Config

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Configure a SECRET_KEY segura no ambiente antes de iniciar a aplicação.")

    app.config.setdefault("UPLOAD_FOLDER", str(Path(app.instance_path) / "uploads"))
    if app.config.get("MAX_CONTENT_LENGTH") is None:
        app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Entre na sua conta para continuar."
    login_manager.login_message_category = "error"

    from app.models import StudyMaterial, StudySpace, User
    from app.routes import auth_bp, main_bp, study_spaces_bp, materials_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(study_spaces_bp)
    app.register_blueprint(materials_bp)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    @app.before_request
    def require_login():
        public_endpoints = {
            "auth.login",
            "auth.register",
            "static",
        }
        if request.endpoint not in public_endpoints and not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.full_path))

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.exception("Erro interno ao processar a requisição")
        return render_template("errors/500.html"), 500

    return app
