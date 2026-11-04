from datetime import datetime, timezone

from app.extensions import db

SPACE_ICONS = {
    "book": "📚",
    "math": "🧮",
    "science": "🔬",
    "chemistry": "🧪",
    "computer": "💻",
    "globe": "🌍",
    "writing": "✍️",
    "art": "🎨",
    "music": "🎵",
    "brain": "🧠",
    "language": "🗣️",
    "star": "⭐",
}


class StudySpace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False, default="")
    location = db.Column(db.String(160), nullable=False, default="")
    color = db.Column(db.String(20), nullable=False, default="sage", server_default="sage")
    icon = db.Column(db.String(20), nullable=False, default="book", server_default="book")
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    materials = db.relationship(
        "StudyMaterial",
        back_populates="study_space",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StudyMaterial.created_at.desc()",
    )

    def __repr__(self):
        return f"<StudySpace {self.name!r}>"

    @property
    def icon_symbol(self):
        return SPACE_ICONS.get(self.icon, SPACE_ICONS["book"])
