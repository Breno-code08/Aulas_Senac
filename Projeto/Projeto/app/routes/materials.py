from pathlib import Path
from urllib.parse import urlsplit

from flask import current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import DataRequired

from app.extensions import db
from app.forms import StudyMaterialForm
from app.models import StudyMaterial, StudyMaterialResource
from app.routes import materials_bp
from app.services.study_material_service import (
    create_study_material,
    delete_study_material,
    delete_study_material_resource,
    update_study_material,
)
from app.services.study_space_service import get_study_space

MAX_PDF_SIZE = 16 * 1024 * 1024


def _collect_additional_resources():
    resources = []
    errors = []

    for content in request.form.getlist("additional_contents"):
        content = content.strip()
        if not content:
            continue
        if len(content) > 10000:
            errors.append("Cada conteúdo adicional deve ter no máximo 10.000 caracteres.")
        else:
            resources.append({"kind": "content", "content": content})

    for video_url in request.form.getlist("additional_video_urls"):
        video_url = video_url.strip()
        if not video_url:
            continue
        try:
            parsed_url = urlsplit(video_url)
            valid_url = (
                parsed_url.scheme in {"http", "https"}
                and parsed_url.hostname is not None
                and parsed_url.port != 0
                and len(video_url) <= 2048
            )
        except ValueError:
            valid_url = False
        if not valid_url:
            errors.append("Cada videoaula adicional precisa de um link HTTP ou HTTPS válido.")
        else:
            resources.append({"kind": "video", "video_url": video_url})

    for pdf in request.files.getlist("additional_pdfs"):
        if not pdf or not pdf.filename:
            continue
        if Path(pdf.filename).suffix.lower() != ".pdf":
            errors.append("Todos os arquivos adicionais precisam estar no formato PDF.")
            continue
        if pdf.stream.read(5) != b"%PDF-":
            errors.append("Um dos arquivos enviados não parece ser um PDF válido.")
            pdf.stream.seek(0)
            continue
        pdf.stream.seek(0, 2)
        size = pdf.stream.tell()
        pdf.stream.seek(0)
        if size > MAX_PDF_SIZE:
            errors.append("Cada PDF pode ter no máximo 16 MB.")
            continue
        resources.append({"kind": "pdf", "pdf": pdf})

    return resources, errors


def _validate_pdf_file(pdf):
    if not pdf or not pdf.filename:
        return None
    if Path(pdf.filename).suffix.lower() != ".pdf":
        return "Envie um arquivo PDF."
    if pdf.stream.read(5) != b"%PDF-":
        pdf.stream.seek(0)
        return "O arquivo enviado não parece ser um PDF válido."
    pdf.stream.seek(0, 2)
    size = pdf.stream.tell()
    pdf.stream.seek(0)
    if size > MAX_PDF_SIZE:
        return "Cada PDF pode ter no máximo 16 MB."
    return None


def _additional_form_context(errors):
    return {
        "additional_contents": request.form.getlist("additional_contents"),
        "additional_video_urls": request.form.getlist("additional_video_urls"),
        "additional_errors": errors,
    }


@materials_bp.post("/<int:space_id>/materiais")
def create(space_id):
    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404

    form = StudyMaterialForm()
    is_valid = form.validate_on_submit()
    resources, additional_errors = _collect_additional_resources()
    if is_valid and not additional_errors:
        pdf = form.pdf.data
        pdf_error = _validate_pdf_file(pdf)
        if pdf_error:
            form.pdf.errors = (*form.pdf.errors, pdf_error)
            return render_template(
                "study_spaces/detail.html",
                space=space,
                material_form=form,
                **_additional_form_context(additional_errors),
            ), 200
        try:
            create_study_material(
                study_space=space,
                subject=form.subject.data,
                content=form.content.data,
                video_url=form.video_url.data,
                pdf=pdf,
                resources=resources,
            )
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Falha ao salvar material de estudo")
            flash("Não foi possível salvar o material. Tente novamente.", "error")
        else:
            flash("Material adicionado ao espaço.", "success")
            return redirect(url_for("study_spaces.detail", space_id=space.id))

    return render_template(
        "study_spaces/detail.html",
        space=space,
        material_form=form,
        **_additional_form_context(additional_errors),
    ), 200


@materials_bp.route("/<int:space_id>/materiais/<int:material_id>/editar", methods=["GET", "POST"])
def edit(space_id, material_id):
    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    material = StudyMaterial.query.filter_by(
        id=material_id,
        study_space_id=space.id,
    ).first()
    if material is None:
        return render_template("errors/404.html"), 404

    form = StudyMaterialForm(obj=material)
    form.submit.label.text = "Salvar alterações"
    remove_primary_content = request.form.get("remove_primary_content") == "1"
    if remove_primary_content:
        form.content.validators = [
            validator
            for validator in form.content.validators
            if not isinstance(validator, DataRequired)
        ]
    is_valid = form.validate_on_submit()
    resources, additional_errors = _collect_additional_resources()
    has_written_content = bool((form.content.data or "").strip()) or any(
        resource.kind == "content" for resource in material.resources
    ) or any(resource["kind"] == "content" for resource in resources)
    if is_valid and remove_primary_content and not has_written_content:
        form.content.errors = (
            *form.content.errors,
            "Mantenha pelo menos um conteúdo escrito nesta matéria.",
        )
        is_valid = False
    if is_valid and not additional_errors:
        pdf = form.pdf.data
        pdf_error = _validate_pdf_file(pdf)
        if pdf_error:
            form.pdf.errors = (*form.pdf.errors, pdf_error)
            return render_template(
                "materials/edit.html",
                space=space,
                material=material,
                form=form,
                **_additional_form_context(additional_errors),
            ), 200
        try:
            update_study_material(
                material=material,
                subject=form.subject.data,
                content=form.content.data,
                video_url=form.video_url.data,
                pdf=pdf,
                resources=resources,
            )
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Falha ao atualizar material de estudo")
            flash("Não foi possível atualizar o material. Tente novamente.", "error")
        else:
            flash("Material atualizado.", "success")
            return redirect(url_for("study_spaces.detail", space_id=space.id))

    return render_template(
        "materials/edit.html",
        space=space,
        material=material,
        form=form,
        **_additional_form_context(additional_errors),
    ), 200


@materials_bp.post("/<int:space_id>/materiais/<int:material_id>/recursos/<int:resource_id>/excluir")
def delete_resource(space_id, material_id, resource_id):
    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    material = StudyMaterial.query.filter_by(
        id=material_id,
        study_space_id=space.id,
    ).first()
    if material is None:
        return render_template("errors/404.html"), 404
    resource = next((item for item in material.resources if item.id == resource_id), None)
    if resource is None:
        return render_template("errors/404.html"), 404

    try:
        delete_study_material_resource(resource)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao excluir recurso de estudo")
        flash("Não foi possível excluir o recurso. Tente novamente.", "error")
    else:
        flash("Recurso excluído.", "success")
    return redirect(
        url_for("materials.edit", space_id=space.id, material_id=material.id)
    )


@materials_bp.post("/<int:space_id>/materiais/<int:material_id>/status/<status>")
def set_status(space_id, material_id, status):
    if status not in {"concluir", "reabrir"}:
        return render_template("errors/404.html"), 404

    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    material = StudyMaterial.query.filter_by(
        id=material_id,
        study_space_id=space.id,
    ).first()
    if material is None:
        return render_template("errors/404.html"), 404

    material.completed = status == "concluir"
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao atualizar o status da matéria")
        flash("Não foi possível atualizar o status. Tente novamente.", "error")
    else:
        message = "Matéria marcada como concluída." if material.completed else "Matéria movida para pendentes."
        flash(message, "success")
    return redirect(url_for("study_spaces.detail", space_id=space.id))


@materials_bp.post("/<int:space_id>/materiais/<int:material_id>/excluir")
def delete(space_id, material_id):
    space = get_study_space(space_id, user_id=current_user.id)
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
    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    material = StudyMaterial.query.filter_by(
        id=material_id,
        study_space_id=space.id,
    ).first()
    if material is None or material.pdf_storage_name is None:
        return render_template("errors/404.html"), 404
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        material.pdf_storage_name,
        as_attachment=True,
        download_name=material.pdf_filename or "material.pdf",
        mimetype="application/pdf",
    )


@materials_bp.get(
    "/<int:space_id>/materiais/<int:material_id>/recursos/<int:resource_id>/pdf"
)
def download_resource_pdf(space_id, material_id, resource_id):
    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    resource = (
        StudyMaterialResource.query.join(StudyMaterial)
        .filter(
            StudyMaterial.id == material_id,
            StudyMaterial.study_space_id == space.id,
            StudyMaterialResource.id == resource_id,
            StudyMaterialResource.kind == "pdf",
        )
        .first()
    )
    if resource is None or resource.pdf_storage_name is None:
        return render_template("errors/404.html"), 404
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        resource.pdf_storage_name,
        as_attachment=True,
        download_name=resource.pdf_filename or "material.pdf",
        mimetype="application/pdf",
    )
