from pathlib import Path

from flask import Flask, render_template
from dotenv import load_dotenv

from app.extensions import csrf, db, migrate


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
        app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.models import StudyMaterial, StudySpace
    from app.routes import main_bp, study_spaces_bp, materials_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(study_spaces_bp)
    app.register_blueprint(materials_bp)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.exception("Erro interno ao processar a requisição")
        return render_template("errors/500.html"), 500

    return app
