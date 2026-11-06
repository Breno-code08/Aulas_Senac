from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlsplit

from app.extensions import db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.routes import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().casefold()
        user = db.session.query(User).filter(func.lower(User.email) == email).first()
        if user is None or not user.check_password(form.password.data):
            flash("E-mail ou senha inválidos.", "error")
        else:
            login_user(user)
            next_url = request.args.get("next", "")
            parsed_next = urlsplit(next_url)
            if (
                next_url
                and not parsed_next.scheme
                and not parsed_next.netloc
                and parsed_next.path.startswith("/")
                and not parsed_next.path.startswith("//")
                and "\\" not in next_url
            ):
                return redirect(next_url)
            return redirect(url_for("main.index"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().casefold()
        exists = db.session.query(User.id).filter(func.lower(User.email) == email).first()
        if exists:
            flash("Não foi possível criar a conta com esse e-mail.", "error")
            return render_template("auth/register.html", form=form)

        user = User(email=email)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Falha ao criar conta")
            flash("Não foi possível criar sua conta. Tente novamente.", "error")
            return render_template("auth/register.html", form=form)

        login_user(user)
        flash("Conta criada com sucesso.", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("auth.login"))
