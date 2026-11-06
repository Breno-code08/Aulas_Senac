from pathlib import Path
from urllib.parse import urlsplit

from flask import current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.forms import StudyMaterialForm
from app.models import StudyMaterial, StudyMaterialResource
from app.routes import materials_bp
from app.services.study_material_service import (
    create_study_material,
    delete_study_material,
    delete_study_material_resource,
    set_all_study_material_contents_completed,
    set_study_material_content_completed,
    update_study_material,
)
from app.services.study_space_service import get_study_space

MAX_PDF_SIZE = 16 * 1024 * 1024


def _validate_pdf(pdf):
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


def _validate_video_url(video_url):
    if not video_url:
        return None
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
    return None if valid_url else "Informe um link HTTP ou HTTPS válido."


def _collect_contents(existing_contents=()):
    contents = []
    errors = []
    known_contents = {content.id: content for content in existing_contents}
    seen_ids = set()
    ids = request.form.getlist("content_ids")
    descriptions = request.form.getlist("content_descriptions")
    video_urls = request.form.getlist("content_video_urls")
    pdfs = request.files.getlist("content_pdfs")

    entry_count = max([len(ids), len(descriptions), len(video_urls), len(pdfs)], default=0)
    for index in range(entry_count):
        raw_id = ids[index].strip() if index < len(ids) else ""
        content_id = None
        if raw_id:
            try:
                content_id = int(raw_id)
            except ValueError:
                errors.append("Um dos conteúdos enviados não é válido.")
                continue
            if content_id not in known_contents:
                errors.append("Um dos conteúdos enviados não pertence a esta matéria.")
                continue
            if content_id in seen_ids:
                errors.append("Um conteúdo não pode ser enviado mais de uma vez.")
                continue
            seen_ids.add(content_id)

        description = descriptions[index].strip() if index < len(descriptions) else ""
        video_url = video_urls[index].strip() if index < len(video_urls) else ""
        pdf = pdfs[index] if index < len(pdfs) and pdfs[index].filename else None
        if len(description) > 10000:
            errors.append("Cada descrição deve ter no máximo 10.000 caracteres.")
        video_error = _validate_video_url(video_url)
        if video_error:
            errors.append(video_error)
        pdf_error = _validate_pdf(pdf)
        if pdf_error:
            errors.append(pdf_error)

        existing = known_contents.get(content_id)
        keeps_existing_pdf = bool(existing and existing.pdf_storage_name and pdf is None)
        if not description and not video_url and pdf is None and not keeps_existing_pdf:
            continue
        contents.append(
            {
                "id": content_id,
                "description": description,
                "video_url": video_url,
                "pdf": pdf,
            }
        )
    return contents, errors


def _content_form_context(errors, contents=(), material=None):
    if request.method == "POST":
        ids = request.form.getlist("content_ids")
        descriptions = request.form.getlist("content_descriptions")
        video_urls = request.form.getlist("content_video_urls")
        existing_by_id = {content.id: content for content in material.resources} if material else {}
        entry_count = max([len(ids), len(descriptions), len(video_urls), 1])
        entries = []
        for index in range(entry_count):
            raw_id = ids[index] if index < len(ids) else ""
            try:
                existing = existing_by_id.get(int(raw_id)) if raw_id else None
            except ValueError:
                existing = None
            entries.append(
                {
                    "id": raw_id,
                    "description": descriptions[index] if index < len(descriptions) else "",
                    "video_url": video_urls[index] if index < len(video_urls) else "",
                    "pdf_filename": existing.pdf_filename if existing else None,
                }
            )
    else:
        entries = [
            {
                "id": content.id,
                "description": content.content or "",
                "video_url": content.video_url or "",
                "pdf_filename": content.pdf_filename,
            }
            for content in contents
        ]
        if not entries:
            entries = [{"id": "", "description": "", "video_url": "", "pdf_filename": None}]
    return {"content_entries": entries, "content_errors": errors}


@materials_bp.post("/<int:space_id>/materiais")
def create(space_id):
    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404

    form = StudyMaterialForm()
    is_valid = form.validate_on_submit()
    contents, content_errors = _collect_contents()
    if is_valid and not content_errors:
        try:
            create_study_material(
                study_space=space,
                subject=form.subject.data,
                contents=contents,
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
        **_content_form_context(content_errors, contents),
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
    is_valid = form.validate_on_submit()
    if request.method == "POST":
        contents, content_errors = _collect_contents(material.resources)
    else:
        contents, content_errors = material.resources, []
    if is_valid and not content_errors:
        try:
            update_study_material(
                material=material,
                subject=form.subject.data,
                contents=contents,
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
        **_content_form_context(content_errors, contents, material),
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
        flash("Não foi possível remover o conteúdo. Tente novamente.", "error")
    else:
        flash("Conteúdo removido.", "success")
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

    set_all_study_material_contents_completed(material, status == "concluir")
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


@materials_bp.post(
    "/<int:space_id>/materiais/<int:material_id>/conteudos/<content_key>/<status>"
)
def set_content_status(space_id, material_id, content_key, status):
    if status not in {"concluir", "reabrir"}:
        return render_template("errors/404.html"), 404

    space = get_study_space(space_id, user_id=current_user.id)
    if space is None:
        return render_template("errors/404.html"), 404
    material = StudyMaterial.query.filter_by(
        id=material_id,
        study_space_id=space.id,
    ).first()
    if material is None or not set_study_material_content_completed(
        material, content_key, status == "concluir"
    ):
        return render_template("errors/404.html"), 404

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Falha ao atualizar o status do conteúdo")
        flash("Não foi possível atualizar o conteúdo. Tente novamente.", "error")
    else:
        if material.completed:
            flash("Conteúdo concluído. A matéria foi concluída automaticamente.", "success")
        elif status == "concluir":
            flash("Conteúdo marcado como concluído.", "success")
        else:
            flash("Conteúdo movido para pendentes.", "success")
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
