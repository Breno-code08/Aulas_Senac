from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class StudyMaterialForm(FlaskForm):
    subject = StringField(
        "Assunto",
        validators=[InputRequired(message="Informe o assunto."), Length(max=160)],
    )
    submit = SubmitField("Adicionar material")
