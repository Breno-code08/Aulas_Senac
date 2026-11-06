from pathlib import Path
from uuid import uuid4

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import StudyMaterial, StudyMaterialResource


def _completion_states(material):
    return [resource.completed for resource in material.resources]


def _sync_material_completion(material):
    states = _completion_states(material)
    material.completed = bool(states) and all(states)


def set_study_material_content_completed(material, content_key, completed):
    if not content_key.startswith("resource-"):
        return False
    try:
        resource_id = int(content_key.removeprefix("resource-"))
    except ValueError:
        return False
    resource = next(
        (item for item in material.resources if item.id == resource_id),
        None,
    )
    if resource is None:
        return False
    resource.completed = completed

    _sync_material_completion(material)
    return True


def set_all_study_material_contents_completed(material, completed):
    for resource in material.resources:
        resource.completed = completed
    _sync_material_completion(material)


def _store_pdf(pdf):
    original_name = secure_filename(pdf.filename)
    stored_name = f"{uuid4().hex}.pdf"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    pdf.save(upload_dir / stored_name)
    return original_name, stored_name


def _add_contents(material, contents, stored_names):
    for content in contents:
        original_name = stored_name = None
        if content["pdf"]:
            original_name, stored_name = _store_pdf(content["pdf"])
            stored_names.append(stored_name)
        material.resources.append(
            StudyMaterialResource(
                kind="content",
                content=content["description"] or None,
                video_url=content["video_url"] or None,
                pdf_filename=original_name,
                pdf_storage_name=stored_name,
            )
        )


def create_study_material(*, study_space, subject, contents=()):
    stored_names = []
    material = StudyMaterial(
        study_space=study_space,
        subject=subject.strip(),
    )
    try:
        _add_contents(material, contents, stored_names)
        db.session.add(material)
        _sync_material_completion(material)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        for stored_name in stored_names:
            (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
        raise
    return material


def update_study_material(*, material, subject, contents=()):
    newly_stored_names = []
    removed_stored_names = []
    current_contents = {content.id: content for content in material.resources}
    retained_ids = set()
    material.subject = subject.strip()

    try:
        for content in contents:
            content_id = content["id"]
            if content_id is None:
                _add_contents(material, [content], newly_stored_names)
                continue

            existing = current_contents[content_id]
            retained_ids.add(content_id)
            changed = (
                existing.content != (content["description"] or None)
                or existing.video_url != (content["video_url"] or None)
            )
            existing.content = content["description"] or None
            existing.video_url = content["video_url"] or None
            if content["pdf"]:
                old_stored_name = existing.pdf_storage_name
                original_name, stored_name = _store_pdf(content["pdf"])
                newly_stored_names.append(stored_name)
                existing.pdf_filename = original_name
                existing.pdf_storage_name = stored_name
                if old_stored_name:
                    removed_stored_names.append(old_stored_name)
                changed = True
            if changed:
                existing.completed = False

        for content_id, content in current_contents.items():
            if content_id not in retained_ids:
                if content.pdf_storage_name:
                    removed_stored_names.append(content.pdf_storage_name)
                material.resources.remove(content)

        _sync_material_completion(material)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        for stored_name in newly_stored_names:
            (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
        raise

    for stored_name in removed_stored_names:
        (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
    return material


def delete_study_material_resource(resource):
    stored_name = resource.pdf_storage_name
    material = resource.material
    material.resources.remove(resource)
    _sync_material_completion(material)
    db.session.commit()
    if stored_name:
        (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)


def delete_study_material(material):
    stored_names = {
        name
        for name in (
            material.pdf_storage_name,
            *(resource.pdf_storage_name for resource in material.resources),
        )
        if name
    }
    db.session.delete(material)
    db.session.commit()
    for stored_name in stored_names:
        (Path(current_app.config["UPLOAD_FOLDER"]) / stored_name).unlink(missing_ok=True)
