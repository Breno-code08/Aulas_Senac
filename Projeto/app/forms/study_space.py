from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional

from app.models.study_space import SPACE_ICONS


class StudySpaceForm(FlaskForm):
    name = StringField(
        "Nome",
        validators=[InputRequired(message="Informe o nome."), Length(max=120)],
    )
    description = TextAreaField(
        "Descrição",
        validators=[Optional(), Length(max=2000)],
    )
    location = StringField(
        "Localização",
        validators=[Optional(), Length(max=160)],
    )
    color = RadioField(
        "Cor do espaço",
        choices=[
            ("sage", "Sálvia"),
            ("blue", "Azul"),
            ("lavender", "Lavanda"),
            ("peach", "Pêssego"),
            ("rose", "Rosa"),
            ("gold", "Amarelo"),
        ],
        default="sage",
        validators=[InputRequired(message="Escolha uma cor.")],
    )
    icon = RadioField(
        "Símbolo do espaço",
        choices=[
            ("book", f"{SPACE_ICONS['book']} Livros"),
            ("math", f"{SPACE_ICONS['math']} Matemática"),
            ("science", f"{SPACE_ICONS['science']} Ciências"),
            ("chemistry", f"{SPACE_ICONS['chemistry']} Química"),
            ("computer", f"{SPACE_ICONS['computer']} Tecnologia"),
            ("globe", f"{SPACE_ICONS['globe']} Geografia"),
            ("writing", f"{SPACE_ICONS['writing']} Escrita"),
            ("art", f"{SPACE_ICONS['art']} Arte"),
            ("music", f"{SPACE_ICONS['music']} Música"),
            ("brain", f"{SPACE_ICONS['brain']} Conhecimento"),
            ("language", f"{SPACE_ICONS['language']} Idiomas"),
            ("star", f"{SPACE_ICONS['star']} Geral"),
        ],
        default="book",
        validators=[InputRequired(message="Escolha um símbolo.")],
    )
    submit = SubmitField("Salvar espaço")
