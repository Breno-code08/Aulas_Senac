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
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    study_space = db.relationship(
        "StudySpace",
        back_populates="materials",
    )
