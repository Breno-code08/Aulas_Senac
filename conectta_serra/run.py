"""Entrada compatível com Flask CLI: python -m flask --app run run."""
from iniciar import create_local_app
app = create_local_app()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
