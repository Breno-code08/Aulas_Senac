import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture()
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
            "WTF_CSRF_ENABLED": False,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    client = app.test_client()
    response = client.post(
        "/auth/cadastro",
        data={
            "email": "student@example.com",
            "password": "secure-test-password-123",
            "confirm_password": "secure-test-password-123",
            "submit": "Criar conta",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert db.session.query(User).count() == 1
    return client
