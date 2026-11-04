from pathlib import Path
from uuid import uuid4

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import StudyMaterial


def create_study_material(*, study_space, subject, content, video_url, pdf):
    stored_name = None
    original_name = None
    if pdf and pdf.filename:
        original_name = secure_filename(pdf.filename)
        stored_name = f"{uuid4().hex}.pdf"
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        pdf.save(upload_dir / stored_name)

    material = StudyMaterial(
        study_space=study_space,
        subject=subject.strip(),
        content=content.strip(),
        video_url=(video_url or "").strip() or None,
        pdf_filename=original_name,
        pdf_storage_name=stored_name,
    )
    try:
        db.session.add(material)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        if stored_name:
            (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
        raise
    return material


def delete_study_material(material):
    stored_name = material.pdf_storage_name
    db.session.delete(material)
    db.session.commit()
    if stored_name:
        (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
