from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models import StudySpace


def list_study_spaces(*, user_id, search=""):
    query = StudySpace.query.filter_by(owner_id=user_id)
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


def get_study_space(space_id, *, user_id):
    return StudySpace.query.filter_by(id=space_id, owner_id=user_id).first()


def create_study_space(*, owner_id, name, description="", location="", color="sage", icon="book"):
    space = StudySpace(
        owner_id=owner_id,
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
    stored_names = [
        stored_name
        for material in space.materials
        for stored_name in (
            material.pdf_storage_name,
            *(resource.pdf_storage_name for resource in material.resources),
        )
        if stored_name
    ]
    db.session.delete(space)
    db.session.commit()
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    for stored_name in stored_names:
        (upload_dir / stored_name).unlink(missing_ok=True)
