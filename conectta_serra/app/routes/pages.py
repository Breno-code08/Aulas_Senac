from flask import Blueprint, render_template, redirect, url_for
pages_bp = Blueprint('pages', __name__)

@pages_bp.get('/')
def index():
    return render_template('index.html')

@pages_bp.get('/cadastro/usuario')
def user_registration():
    return redirect(url_for('pages.index') + '#cadastro-usuario')

@pages_bp.get('/cadastro/profissional')
def professional_registration():
    return redirect(url_for('pages.index') + '#cadastro-profissional')
