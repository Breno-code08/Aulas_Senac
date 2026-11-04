from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models import StudySpace


def list_study_spaces(search=""):
    query = StudySpace.query
    term = search.strip()
    if term:
        pattern = f"%{term}%"
        query = query.filter(
            db.or_(
                StudySpace.name.ilike(pattern),
                StudySpace.description.ilike(pattern),
                StudySpace.location.ilike(pattern),
            )
        )
    return query.order_by(StudySpace.name.asc()).all()


def get_study_space(space_id):
    return db.session.get(StudySpace, space_id)


def create_study_space(*, name, description="", location="", color="sage", icon="book"):
    space = StudySpace(
        name=name.strip(),
        description=(description or "").strip(),
        location=(location or "").strip(),
        color=color,
        icon=icon,
    )
    db.session.add(space)
    db.session.commit()
    return space


def update_study_space(space, *, name, description="", location="", color="sage", icon="book"):
    space.name = name.strip()
    space.description = (description or "").strip()
    space.location = (location or "").strip()
    space.color = color
    space.icon = icon
    db.session.commit()
    return space


def delete_study_space(space):
    stored_names = [material.pdf_storage_name for material in space.materials if material.pdf_storage_name]
    db.session.delete(space)
    db.session.commit()
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    for stored_name in stored_names:
        (upload_dir / stored_name).unlink(missing_ok=True)
