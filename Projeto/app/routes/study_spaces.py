from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.forms import StudyMaterialForm, StudySpaceForm
from app.routes import study_spaces_bp
from app.services import study_space_service


@study_spaces_bp.get("/")
def list_spaces():
    search = request.args.get("q", "")
    try:
        spaces = study_space_service.list_study_spaces(
            user_id=current_user.id,
            search=search,
        )
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao consultar espaços de estudo")
        flash("Não foi possível carregar os espaços. Tente novamente.", "error")
        spaces = []
    return render_template("study_spaces/list.html", spaces=spaces, search=search)


@study_spaces_bp.route("/novo", methods=["GET", "POST"])
def create():
    form = StudySpaceForm()
    if form.validate_on_submit():
        try:
            space = study_space_service.create_study_space(
                owner_id=current_user.id,
                name=form.name.data,
                description=form.description.data,
                location=form.location.data,
                color=form.color.data,
                icon=form.icon.data,
            )
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Falha ao criar espaço de estudo")
            flash("Não foi possível salvar o espaço. Tente novamente.", "error")
        else:
            flash("Espaço cadastrado com sucesso.", "success")
            return redirect(url_for("study_spaces.detail", space_id=space.id))
    return render_template("study_spaces/create.html", form=form)


@study_spaces_bp.get("/<int:space_id>")
def detail(space_id):
    space = study_space_service.get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    return render_template(
        "study_spaces/detail.html",
        space=space,
        material_form=StudyMaterialForm(),
    )


@study_spaces_bp.route("/<int:space_id>/editar", methods=["GET", "POST"])
def edit(space_id):
    space = study_space_service.get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    form = StudySpaceForm(obj=space)
    if form.validate_on_submit():
        try:
            study_space_service.update_study_space(
                space,
                name=form.name.data,
                description=form.description.data,
                location=form.location.data,
                color=form.color.data,
                icon=form.icon.data,
            )
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Falha ao editar espaço de estudo")
            flash("Não foi possível atualizar o espaço. Tente novamente.", "error")
        else:
            flash("Espaço atualizado com sucesso.", "success")
            return redirect(url_for("study_spaces.detail", space_id=space.id))
    return render_template("study_spaces/edit.html", form=form, space=space)


@study_spaces_bp.post("/<int:space_id>/excluir")
def delete(space_id):
    space = study_space_service.get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    try:
        study_space_service.delete_study_space(space)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao excluir espaço de estudo")
        flash("Não foi possível excluir o espaço. Tente novamente.", "error")
        return redirect(url_for("study_spaces.detail", space_id=space_id))
    flash("Espaço excluído com sucesso.", "success")
    return redirect(url_for("study_spaces.list_spaces"))
