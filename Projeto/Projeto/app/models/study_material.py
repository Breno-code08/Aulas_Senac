from datetime import datetime, timezone

from app.extensions import db


class StudyMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_space_id = db.Column(
        db.Integer,
        db.ForeignKey("study_space.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject = db.Column(db.String(160), nullable=False)
    content = db.Column(db.Text, nullable=False, default="")
    video_url = db.Column(db.String(2048), nullable=True)
    pdf_filename = db.Column(db.String(255), nullable=True)
    pdf_storage_name = db.Column(db.String(36), nullable=True, unique=True)
    completed = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    study_space = db.relationship(
        "StudySpace",
        back_populates="materials",
    )
    resources = db.relationship(
        "StudyMaterialResource",
        back_populates="material",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StudyMaterialResource.id.asc()",
    )


class StudyMaterialResource(db.Model):
    __tablename__ = "study_material_resource"
    __table_args__ = (
        db.CheckConstraint(
            "kind IN ('content', 'pdf', 'video')",
            name="ck_study_material_resource_kind",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    study_material_id = db.Column(
        db.Integer,
        db.ForeignKey("study_material.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(2048), nullable=True)
    pdf_filename = db.Column(db.String(255), nullable=True)
    pdf_storage_name = db.Column(db.String(36), nullable=True, unique=True)
    material = db.relationship("StudyMaterial", back_populates="resources")
