from pathlib import Path

from flask import current_app, flash, redirect, render_template, send_from_directory, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.forms import StudyMaterialForm
from app.models import StudyMaterial
from app.routes import materials_bp
from app.services.study_material_service import create_study_material, delete_study_material
from app.services.study_space_service import get_study_space


@materials_bp.post("/<int:space_id>/materiais")
def create(space_id):
    space = get_study_space(space_id)
    if space is None:
        return render_template("errors/404.html"), 404

    form = StudyMaterialForm()
    if form.validate_on_submit():
        pdf = form.pdf.data
        if pdf and pdf.filename:
            if pdf.stream.read(5) != b"%PDF-":
                form.pdf.errors = (*form.pdf.errors, "O arquivo enviado não parece ser um PDF válido.")
                pdf.stream.seek(0)
                return render_template(
                    "study_spaces/detail.html", space=space, material_form=form
                ), 200
            pdf.stream.seek(0)
        try:
            create_study_material(
                study_space=space,
                subject=form.subject.data,
                content=form.content.data,
                video_url=form.video_url.data,
                pdf=pdf,
            )
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Falha ao salvar material de estudo")
            flash("Não foi possível salvar o material. Tente novamente.", "error")
        else:
            flash("Material adicionado ao espaço.", "success")
            return redirect(url_for("study_spaces.detail", space_id=space.id))

    return render_template(
        "study_spaces/detail.html", space=space, material_form=form
    ), 200


@materials_bp.post("/<int:space_id>/materiais/<int:material_id>/excluir")
def delete(space_id, material_id):
    space = get_study_space(space_id)
    if space is None:
        return render_template("errors/404.html"), 404
    material = db.session.get(StudyMaterial, material_id)
    if material is None or material.study_space_id != space.id:
        return render_template("errors/404.html"), 404

    try:
        delete_study_material(material)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao excluir material de estudo")
        flash("Não foi possível excluir o material. Tente novamente.", "error")
    else:
        flash("Material excluído.", "success")
    return redirect(url_for("study_spaces.detail", space_id=space.id))


@materials_bp.get("/<int:space_id>/materiais/<int:material_id>/pdf")
def download_pdf(space_id, material_id):
    material = db.session.get(StudyMaterial, material_id)
    if (
        material is None
        or material.study_space_id != space_id
        or material.pdf_storage_name is None
    ):
        return render_template("errors/404.html"), 404
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        material.pdf_storage_name,
        as_attachment=True,
        download_name=material.pdf_filename or "material.pdf",
        mimetype="application/pdf",
    )
