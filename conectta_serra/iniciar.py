"""Inicia o Conectta Serra em Python/Flask no computador local.

No terminal do VS Code:
    python -m pip install -r requirements.txt
    python iniciar.py

Abra http://127.0.0.1:5000/ no navegador.
"""
from pathlib import Path
import os
import secrets
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

def local_secret():
    """Gera uma chave local uma única vez e a reutiliza ao reiniciar."""
    instance = ROOT / 'instance'
    instance.mkdir(exist_ok=True)
    key_path = instance / 'session.key'
    if not key_path.exists():
        try:
            fd = os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, 'w', encoding='utf-8') as key_file:
                key_file.write(secrets.token_hex(32))
    return key_path.read_text(encoding='utf-8').strip()

def create_local_app():
    os.environ.setdefault('SECRET_KEY', local_secret())
    from app import create_app
    from flask_migrate import upgrade
    from app.services.catalog import seed_database
    application = create_app()
    with application.app_context():
        upgrade(directory=str(ROOT / 'migrations'))
        if application.config['DEMO_MODE']:
            seed_database()
    return application

if __name__ == '__main__':
    application = create_local_app()
    print('\nConectta Serra: abra http://127.0.0.1:5000/ no navegador.\n')
    application.run(host='127.0.0.1', port=5000, debug=False)
