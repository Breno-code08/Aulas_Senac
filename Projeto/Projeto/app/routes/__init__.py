from flask import Blueprint

main_bp = Blueprint("main", __name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
study_spaces_bp = Blueprint(
    "study_spaces", __name__, url_prefix="/espacos"
)
materials_bp = Blueprint("materials", __name__, url_prefix="/espacos")

from app.routes import auth, main, materials, study_spaces  # noqa: E402,F401
