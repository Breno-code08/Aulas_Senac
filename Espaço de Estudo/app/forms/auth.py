from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = EmailField(
        "E-mail",
        validators=[DataRequired(message="Informe seu e-mail."), Email()],
    )
    password = PasswordField(
        "Senha",
        validators=[DataRequired(message="Informe sua senha."), Length(max=128)],
    )
    submit = SubmitField("Entrar")


class RegistrationForm(FlaskForm):
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired(message="Informe seu e-mail."),
            Email(),
            Length(max=254),
        ],
    )
    password = PasswordField(
        "Senha",
        validators=[
            DataRequired(message="Crie uma senha."),
            Length(min=12, max=128, message="A senha deve ter entre 12 e 128 caracteres."),
        ],
    )
    confirm_password = PasswordField(
        "Confirme a senha",
        validators=[
            DataRequired(message="Confirme sua senha."),
            EqualTo("password", message="As senhas não conferem."),
        ],
    )
    submit = SubmitField("Criar conta")
