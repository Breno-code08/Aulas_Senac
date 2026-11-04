from flask import render_template

from app.routes import main_bp
from app.services.study_space_service import list_study_spaces


@main_bp.get("/")
def index():
    spaces = list_study_spaces()[:3]
    return render_template("index.html", spaces=spaces)
