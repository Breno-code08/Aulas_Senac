from flask import current_app, render_template
from flask_login import current_user

from app.routes import main_bp
from app.services.study_space_service import list_study_spaces


@main_bp.get("/")
def index():
    spaces = list_study_spaces(user_id=current_user.id)[:3]
    return render_template("index.html", spaces=spaces)


@main_bp.get("/suporte")
def support():
    return render_template("support.html")


@main_bp.get("/sobre")
def about():
    return render_template("about.html")


@main_bp.get("/contato")
def contact():
    return render_template(
        "contact.html",
        contact_email=current_app.config["CONTACT_EMAIL"],
    )
