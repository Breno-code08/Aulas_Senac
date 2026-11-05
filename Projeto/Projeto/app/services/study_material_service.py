from pathlib import Path
from uuid import uuid4

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import StudyMaterial, StudyMaterialResource


def _store_pdf(pdf):
    original_name = secure_filename(pdf.filename)
    stored_name = f"{uuid4().hex}.pdf"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    pdf.save(upload_dir / stored_name)
    return original_name, stored_name


def _add_resources(material, resources, stored_names):
    for resource in resources:
        if resource["kind"] == "content":
            material.resources.append(
                StudyMaterialResource(kind="content", content=resource["content"])
            )
        elif resource["kind"] == "video":
            material.resources.append(
                StudyMaterialResource(kind="video", video_url=resource["video_url"])
            )
        else:
            original_name, stored_name = _store_pdf(resource["pdf"])
            stored_names.append(stored_name)
            material.resources.append(
                StudyMaterialResource(
                    kind="pdf",
                    pdf_filename=original_name,
                    pdf_storage_name=stored_name,
                )
            )


def create_study_material(*, study_space, subject, content, video_url, pdf, resources=()):
    stored_names = []
    original_name = stored_name = None
    if pdf and pdf.filename:
        original_name, stored_name = _store_pdf(pdf)
        stored_names.append(stored_name)

    material = StudyMaterial(
        study_space=study_space,
        subject=subject.strip(),
        content=content.strip(),
        video_url=(video_url or "").strip() or None,
        pdf_filename=original_name,
        pdf_storage_name=stored_name,
    )
    try:
        _add_resources(material, resources, stored_names)
        db.session.add(material)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        for stored_name in stored_names:
            (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
        raise
    return material


def update_study_material(*, material, subject, content, video_url, pdf, resources=()):
    old_stored_name = material.pdf_storage_name
    newly_stored_names = []
    replaced_primary_pdf = False

    if pdf and pdf.filename:
        original_name, new_stored_name = _store_pdf(pdf)
        newly_stored_names.append(new_stored_name)
        material.pdf_filename = original_name
        material.pdf_storage_name = new_stored_name
        replaced_primary_pdf = True

    material.subject = subject.strip()
    material.content = content.strip()
    material.video_url = (video_url or "").strip() or None

    try:
        _add_resources(material, resources, newly_stored_names)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        for stored_name in newly_stored_names:
            (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
        raise

    if replaced_primary_pdf and old_stored_name:
        (Path(current_app.config["UPLOAD_FOLDER"]) / old_stored_name).unlink(missing_ok=True)
    return material


def delete_study_material_resource(resource):
    stored_name = resource.pdf_storage_name
    db.session.delete(resource)
    db.session.commit()
    if stored_name:
        (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)


def delete_study_material(material):
    stored_names = [
        name
        for name in (
            material.pdf_storage_name,
            *(resource.pdf_storage_name for resource in material.resources),
        )
        if name
    ]
    db.session.delete(material)
    db.session.commit()
    for stored_name in stored_names:
        (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
