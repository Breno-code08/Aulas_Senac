from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Optional, URL


class StudyMaterialForm(FlaskForm):
    subject = StringField(
        "Assunto",
        validators=[InputRequired(message="Informe o assunto."), Length(max=160)],
    )
    content = TextAreaField(
        "Conteúdo do assunto",
        validators=[
            DataRequired(message="Escreva o conteúdo do assunto."),
            Length(max=10000, message="O conteúdo deve ter no máximo 10.000 caracteres."),
        ],
    )
    pdf = FileField("Material em PDF", validators=[FileAllowed(["pdf"], "Envie um arquivo PDF.")])
    video_url = StringField(
        "Link da videoaula",
        validators=[
            Optional(),
            URL(
                require_tld=False,
                schemes=["http", "https"],
                message="Informe um link HTTP ou HTTPS válido.",
            ),
            Length(max=2048),
        ],
    )
    submit = SubmitField("Adicionar material")
