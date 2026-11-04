from io import BytesIO

import pytest

from app import create_app
from app.extensions import db
from app.models import StudySpace


def test_create_and_list_study_space(client):
    response = client.post(
        "/espacos/novo",
        data={
            "name": "Biblioteca",
            "description": "Sala silenciosa",
            "location": "Bloco A",
            "color": "blue",
            "icon": "math",
            "submit": "Salvar espaço",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Espaço cadastrado com sucesso." in response.get_data(as_text=True)
    assert "Biblioteca" in response.get_data(as_text=True)
    assert "🧮" in response.get_data(as_text=True)
    assert "space-color-blue" in response.get_data(as_text=True)


def test_create_requires_name(client):
    response = client.post("/espacos/novo", data={"name": "", "submit": "Salvar espaço"})

    assert response.status_code == 200
    assert "Informe o nome." in response.get_data(as_text=True)


def test_homepage_has_open_space_action(client, app):
    with app.app_context():
        space = StudySpace(name="Caderno de matemática", icon="math", color="blue")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.get("/")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Caderno de matemática" in page
    assert "Abrir espaço" in page
    assert f'href="/espacos/{space_id}"' in page


def test_search_filters_by_location(client, app):
    with app.app_context():
        db.session.add_all(
            [
                StudySpace(name="Sala Norte", location="Bloco A"),
                StudySpace(name="Sala Sul", location="Bloco B"),
            ]
        )
        db.session.commit()

    response = client.get("/espacos/?q=Bloco+A")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Sala Norte" in page
    assert "Sala Sul" not in page


def test_update_and_delete_study_space(client, app):
    with app.app_context():
        space = StudySpace(name="Sala antiga")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    updated = client.post(
        f"/espacos/{space_id}/editar",
        data={
            "name": "Sala renovada",
            "color": "lavender",
            "icon": "science",
            "submit": "Salvar espaço",
        },
        follow_redirects=True,
    )
    assert updated.status_code == 200
    assert "Sala renovada" in updated.get_data(as_text=True)
    assert "🔬" in updated.get_data(as_text=True)
    assert "space-color-lavender" in updated.get_data(as_text=True)

    deleted = client.post(f"/espacos/{space_id}/excluir", follow_redirects=True)
    assert deleted.status_code == 200
    assert "Espaço excluído com sucesso." in deleted.get_data(as_text=True)
    assert "Sala renovada" not in deleted.get_data(as_text=True)


def test_study_space_rejects_unknown_appearance_choices(client):
    response = client.post(
        "/espacos/novo",
        data={
            "name": "Espaço inválido",
            "color": "background:url(javascript:alert(1))",
            "icon": "<script>alert(1)</script>",
            "submit": "Salvar espaço",
        },
    )

    assert response.status_code == 200
    assert "Espaço cadastrado com sucesso." not in response.get_data(as_text=True)


def test_missing_space_returns_404(client):
    response = client.get("/espacos/999")

    assert response.status_code == 404
    assert "Não encontramos esta página." in response.get_data(as_text=True)


def test_study_space_detail_shows_material_form(client, app):
    with app.app_context():
        space = StudySpace(name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.get(f"/espacos/{space_id}")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Adicionar matéria ou material" in page
    assert "Conteúdo do assunto" in page
    assert "PDF</label> <span class=\"field-hint\">(opcional)</span>" in page
    assert "videoaula</label> <span class=\"field-hint\">(opcional)</span>" in page
    assert "Capacidade" not in page


def test_add_pdf_and_video_material(client, app):
    with app.app_context():
        space = StudySpace(name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Álgebra",
            "content": "Equações e expressões algébricas.",
            "video_url": "https://example.com/aula",
            "pdf": (BytesIO(b"%PDF-1.4\nmaterial"), "algebra.pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Material adicionado ao espaço." in response.get_data(as_text=True)
    assert "Álgebra" in response.get_data(as_text=True)
    assert "Equações e expressões algébricas." in response.get_data(as_text=True)
    assert "Baixar algebra.pdf" in response.get_data(as_text=True)
    assert "Assistir videoaula" in response.get_data(as_text=True)


def test_material_can_be_created_with_content_only(client, app):
    with app.app_context():
        space = StudySpace(name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={"subject": "Física", "content": "Leis de Newton e movimento."},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Material adicionado ao espaço." in response.get_data(as_text=True)
    assert "Leis de Newton e movimento." in response.get_data(as_text=True)


def test_material_can_be_created_with_video_link_only(client, app):
    with app.app_context():
        space = StudySpace(name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "História",
            "content": "Brasil Colônia.",
            "video_url": "https://example.com/historia",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Material adicionado ao espaço." in response.get_data(as_text=True)
    assert "Assistir videoaula" in response.get_data(as_text=True)


def test_material_requires_written_content(client, app):
    with app.app_context():
        space = StudySpace(name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Física",
            "content": "   ",
            "video_url": "https://example.com/fisica",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert "Escreva o conteúdo do assunto." in response.get_data(as_text=True)


def test_material_rejects_non_pdf_and_non_http_video(client, app):
    with app.app_context():
        space = StudySpace(name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    invalid_pdf = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Química",
            "content": "Ligações químicas.",
            "pdf": (BytesIO(b"not a PDF"), "anotacoes.pdf"),
        },
        content_type="multipart/form-data",
    )
    assert invalid_pdf.status_code == 200
    assert "não parece ser um PDF válido" in invalid_pdf.get_data(as_text=True)

    invalid_url = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Química",
            "content": "Ligações químicas.",
            "video_url": "javascript:alert(1)",
        },
        content_type="multipart/form-data",
    )
    assert invalid_url.status_code == 200
    assert "link HTTP ou HTTPS válido" in invalid_url.get_data(as_text=True)


def test_material_pdf_download_and_delete(client, app, tmp_path):
    with app.app_context():
        space = StudySpace(name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    added = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Biologia",
            "content": "Citologia e estrutura celular.",
            "pdf": (BytesIO(b"%PDF-1.4\nconteudo"), "bio.pdf"),
        },
        content_type="multipart/form-data",
    )
    assert added.status_code == 302

    with app.app_context():
        from app.models import StudyMaterial

        material = db.session.query(StudyMaterial).one()
        material_id = material.id
        stored_path = tmp_path / "uploads" / material.pdf_storage_name

    downloaded = client.get(f"/espacos/{space_id}/materiais/{material_id}/pdf")
    assert downloaded.status_code == 200
    assert downloaded.data.startswith(b"%PDF-")
    assert downloaded.headers["Content-Disposition"].endswith('filename=bio.pdf')
    downloaded.close()
    assert stored_path.exists()

    deleted = client.post(f"/espacos/{space_id}/materiais/{material_id}/excluir")
    assert deleted.status_code == 302
    assert not stored_path.exists()


def test_forms_require_csrf_token(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'csrf.db'}",
        }
    )
    response = app.test_client().post(
        "/espacos/novo", data={"name": "Sala", "submit": "Salvar espaço"}
    )

    assert response.status_code == 400


def test_app_requires_secret_key():
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"TESTING": True, "SECRET_KEY": None})
