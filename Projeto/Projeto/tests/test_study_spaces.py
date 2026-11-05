from io import BytesIO

import pytest

from app import create_app
from app.extensions import db
from app.models import StudyMaterial, StudyMaterialResource, StudySpace, User


def current_test_user_id():
    return db.session.query(User.id).filter_by(email="student@example.com").scalar()


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


def test_login_logout_and_private_routes(client, app):
    anonymous_client = app.test_client()
    response = anonymous_client.get("/espacos/")
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login")

    login_response = client.post(
        "/auth/login",
        data={
            "email": "STUDENT@example.com",
            "password": "secure-test-password-123",
            "submit": "Entrar",
        },
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert "Organize seus materiais de estudo." in login_response.get_data(as_text=True)

    logout_response = client.post("/auth/logout", follow_redirects=True)
    assert logout_response.status_code == 200
    assert "Entrar" in logout_response.get_data(as_text=True)


def test_site_uses_left_sidebar_navigation_and_dark_green_theme(app):
    response = app.test_client().get("/auth/login")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert '<aside class="site-sidebar">' in page
    assert 'class="brand-logo"' in page
    assert 'src="/static/images/study-logo.png"' in page
    assert "brand-label" not in page
    assert "Navegação principal" in page
    assert "site-header" not in page
    assert "data-theme-toggle" in page
    assert "js/theme.js" in page

    login_submit = page.split('<form method="post" novalidate>', 1)[1].split("</form>", 1)[0]
    assert 'type="submit" value="Entrar"' in login_submit

    stylesheet = app.test_client().get("/static/css/style.css")
    assert stylesheet.status_code == 200
    css = stylesheet.get_data(as_text=True)
    assert "--paper: #090d0a" in css
    assert "--green: #31c76a" in css
    assert ':root[data-theme="light"]' in css
    assert "--paper: #fbfcfa" in css
    assert ".home-logo { display: block; width: 56px; height: auto" in css
    assert ".site-sidebar .brand { display: flex; width: 58px; height: 58px; min-height: 58px; align-self: center" in css
    assert "border: 1px solid #31563c" in css
    assert ".app-main { display: flex" in css
    assert '.form-card .action-row input[type="submit"].button { width: auto' in css
    assert "@media (max-width: 760px)" in css

    theme_script = app.test_client().get("/static/js/theme.js")
    assert theme_script.status_code == 200
    script = theme_script.get_data(as_text=True)
    assert "localStorage.getItem(storageKey)" in script
    assert 'localStorage.setItem(storageKey, nextTheme)' in script


def test_registration_hashes_password_and_validates_password_length(app):
    client = app.test_client()
    response = client.post(
        "/auth/cadastro",
        data={
            "email": "new@example.com",
            "password": "short",
            "confirm_password": "short",
            "submit": "Criar conta",
        },
    )
    assert response.status_code == 200
    assert "12 e 128 caracteres" in response.get_data(as_text=True)

    response = client.post(
        "/auth/cadastro",
        data={
            "email": "NEW@example.com",
            "password": "a-strong-password-123",
            "confirm_password": "a-strong-password-123",
            "submit": "Criar conta",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        user = db.session.query(User).filter_by(email="new@example.com").one()
        assert user.password_hash != "a-strong-password-123"
        assert user.check_password("a-strong-password-123")


def test_users_cannot_access_each_others_spaces(client, app):
    with app.app_context():
        space = StudySpace(
            owner_id=current_test_user_id(),
            name="Espaço privado",
        )
        material = StudyMaterial(
            subject="Anotações privadas",
            content="Conteúdo disponível apenas para o proprietário.",
        )
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    other_client = app.test_client()
    response = other_client.post(
        "/auth/cadastro",
        data={
            "email": "other@example.com",
            "password": "another-secure-password-456",
            "confirm_password": "another-secure-password-456",
            "submit": "Criar conta",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Espaço privado" not in other_client.get("/espacos/").get_data(as_text=True)
    assert other_client.get(f"/espacos/{space_id}").status_code == 404
    assert other_client.get(
        f"/espacos/{space_id}/materiais/{material_id}/editar"
    ).status_code == 404
    assert other_client.get(
        f"/espacos/{space_id}/materiais/{material_id}/pdf"
    ).status_code == 404
    assert other_client.post(
        f"/espacos/{space_id}/materiais/{material_id}/excluir"
    ).status_code == 404
    assert other_client.post(
        f"/espacos/{space_id}/materiais/{material_id}/status/concluir"
    ).status_code == 404


def test_homepage_has_open_space_action(client, app):
    with app.app_context():
        space = StudySpace(
            owner_id=current_test_user_id(),
            name="Caderno de matemática",
            icon="math",
            color="blue",
        )
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.get("/")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Caderno de matemática" in page
    assert 'class="home-logo"' in page
    assert 'src="/static/images/study-logo.png"' in page
    assert "Abrir espaço" in page
    assert f'href="/espacos/{space_id}"' in page


def test_support_and_about_pages_are_available(client):
    support_response = client.get("/suporte")
    about_response = client.get("/sobre")

    assert support_response.status_code == 200
    assert "Central de ajuda" in support_response.get_data(as_text=True)
    assert "Como criar um espaço de estudo?" in support_response.get_data(as_text=True)
    assert about_response.status_code == 200
    assert "Sobre o projeto" in about_response.get_data(as_text=True)


def test_contact_page_uses_configured_email(client):
    response = client.get("/contato")

    assert response.status_code == 200
    assert "endereço de contato ainda não foi configurado" in response.get_data(as_text=True)


def test_contact_page_shows_configured_email(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'contact.db'}",
            "CONTACT_EMAIL": "suporte@example.test",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with app.app_context():
        db.create_all()
    client = app.test_client()
    client.post(
        "/auth/cadastro",
        data={
            "email": "contact@example.com",
            "password": "secure-contact-password-123",
            "confirm_password": "secure-contact-password-123",
            "submit": "Criar conta",
        },
    )
    response = client.get("/contato")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "suporte@example.test" in page
    assert "mailto:suporte@example.test" in page


def test_search_filters_by_location(client, app):
    with app.app_context():
        db.session.add_all(
            [
                StudySpace(owner_id=current_test_user_id(), name="Sala Norte", location="Bloco A"),
                StudySpace(owner_id=current_test_user_id(), name="Sala Sul", location="Bloco B"),
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
        space = StudySpace(owner_id=current_test_user_id(), name="Sala antiga")
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
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
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
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
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


def test_material_moves_between_pending_and_completed(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Lógica", content="Algoritmos e variáveis.")
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    pending_page = client.get(f"/espacos/{space_id}").get_data(as_text=True)
    assert "Pendentes" in pending_page
    assert "Concluídas" in pending_page
    assert "Lógica" in pending_page
    assert "Nenhuma matéria concluída." in pending_page

    completed = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/status/concluir",
        follow_redirects=True,
    )
    completed_page = completed.get_data(as_text=True)
    assert completed.status_code == 200
    assert "Matéria marcada como concluída." in completed_page
    assert "Nenhuma matéria pendente." in completed_page
    assert "Mover para pendentes" in completed_page
    with app.app_context():
        assert db.session.get(StudyMaterial, material_id).completed is True

    reopened = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/status/reabrir",
        follow_redirects=True,
    )
    reopened_page = reopened.get_data(as_text=True)
    assert reopened.status_code == 200
    assert "Matéria movida para pendentes." in reopened_page
    assert "Marcar como concluída" in reopened_page
    with app.app_context():
        assert db.session.get(StudyMaterial, material_id).completed is False


def test_material_accepts_multiple_extra_contents_pdfs_and_links(client, app, tmp_path):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Biologia",
            "content": "Conteúdo principal.",
            "additional_contents": ["Citologia e organelas.", "Divisão celular."],
            "additional_video_urls": [
                "https://example.com/celula",
                "https://example.com/divisao",
            ],
            "additional_pdfs": [
                (BytesIO(b"%PDF-1.4\ncitologia"), "citologia.pdf"),
                (BytesIO(b"%PDF-1.7\ndivisao"), "divisao.pdf"),
            ],
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Citologia e organelas." in page
    assert "Divisão celular." in page
    assert "Baixar citologia.pdf" in page
    assert "Baixar divisao.pdf" in page
    assert page.count("Assistir videoaula adicional") == 2
    assert "Excluir este conteúdo adicional?" not in page
    with app.app_context():
        material = db.session.query(StudyMaterial).one()
        resources = db.session.query(StudyMaterialResource).order_by(StudyMaterialResource.id).all()
        assert len(resources) == 6
        pdf_resource = next(resource for resource in resources if resource.kind == "pdf")
        pdf_path = tmp_path / "uploads" / pdf_resource.pdf_storage_name
        material_id = material.id
        pdf_resource_id = pdf_resource.id

    edit_page = client.get(f"/espacos/{space_id}/materiais/{material_id}/editar")
    assert edit_page.get_data(as_text=True).count(
        "Excluir este conteúdo adicional?"
    ) == 6

    downloaded = client.get(
        f"/espacos/{space_id}/materiais/{material_id}/recursos/{pdf_resource_id}/pdf"
    )
    assert downloaded.status_code == 200
    assert downloaded.data.startswith(b"%PDF-1.4")
    downloaded.close()
    assert pdf_path.exists()

    removed = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/recursos/{pdf_resource_id}/excluir",
    )
    assert removed.status_code == 302
    assert removed.headers["Location"].endswith(
        f"/espacos/{space_id}/materiais/{material_id}/editar"
    )
    edit_after_removal = client.get(removed.headers["Location"])
    assert edit_after_removal.status_code == 200
    assert "Recurso excluído." in edit_after_removal.get_data(as_text=True)
    assert not pdf_path.exists()

    edited = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Biologia",
            "content": "Conteúdo principal.",
            "additional_contents": ["Genética e hereditariedade."],
            "additional_video_urls": ["https://example.com/genetica"],
            "submit": "Salvar alterações",
        },
        follow_redirects=True,
    )
    assert edited.status_code == 200
    assert "Genética e hereditariedade." in edited.get_data(as_text=True)
    assert "Assistir videoaula adicional" in edited.get_data(as_text=True)
    with app.app_context():
        assert db.session.query(StudyMaterialResource).count() == 7


def test_material_rejects_invalid_additional_resources(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Química",
            "content": "Ligações químicas.",
            "additional_video_urls": ["javascript:alert(1)"],
            "additional_pdfs": [(BytesIO(b"not a PDF"), "anotacoes.pdf")],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert "link HTTP ou HTTPS válido" in response.get_data(as_text=True)
    assert "não parece ser um PDF válido" in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.query(StudyMaterial).count() == 0


def test_material_can_be_created_with_content_only(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
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
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
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
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
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
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
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
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
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


def test_material_can_be_edited_and_pdf_replaced(client, app, tmp_path):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(
            subject="Matemática",
            content="Conteúdo original.",
            pdf_filename="original.pdf",
            pdf_storage_name="original.pdf",
            video_url="https://example.com/original",
        )
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(exist_ok=True)
    old_pdf = upload_dir / "original.pdf"
    old_pdf.write_bytes(b"%PDF-1.4\noriginal")

    edit_page = client.get(f"/espacos/{space_id}/materiais/{material_id}/editar")
    assert edit_page.status_code == 200
    assert "value=\"Matemática\"" in edit_page.get_data(as_text=True)
    assert "Conteúdo original." in edit_page.get_data(as_text=True)

    response = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Matemática avançada",
            "content": "Conteúdo atualizado.",
            "video_url": "https://example.com/atualizado",
            "pdf": (BytesIO(b"%PDF-1.7\nnovo arquivo"), "atualizado.pdf"),
            "submit": "Salvar alterações",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Material atualizado." in response.get_data(as_text=True)
    assert "Matemática avançada" in response.get_data(as_text=True)
    assert "Conteúdo atualizado." in response.get_data(as_text=True)
    assert not old_pdf.exists()
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.pdf_filename == "atualizado.pdf"
        assert material.video_url == "https://example.com/atualizado"
        assert (upload_dir / material.pdf_storage_name).read_bytes().startswith(b"%PDF-1.7")


def test_material_edit_rejects_invalid_pdf(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Física", content="Conteúdo original.")
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    response = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Física",
            "content": "Conteúdo atualizado.",
            "pdf": (BytesIO(b"not a PDF"), "invalido.pdf"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert "não parece ser um PDF válido" in response.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.content == "Conteúdo original."


def test_primary_content_can_only_be_removed_from_edit_page(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Física", content="Conteúdo original.")
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    detail = client.get(f"/espacos/{space_id}")
    assert "Remover conteúdo principal" not in detail.get_data(as_text=True)
    edit = client.get(f"/espacos/{space_id}/materiais/{material_id}/editar")
    assert "Remover conteúdo principal" in edit.get_data(as_text=True)

    removed = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Física",
            "content": "",
            "remove_primary_content": "1",
            "additional_contents": ["Conteúdo substituto."],
            "submit": "Salvar alterações",
        },
        follow_redirects=True,
    )

    assert removed.status_code == 200
    assert "Material atualizado." in removed.get_data(as_text=True)
    assert "Conteúdo original." not in removed.get_data(as_text=True)
    assert "Conteúdo substituto." in removed.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.content == ""


def test_primary_content_cannot_be_removed_without_another_written_content(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Física", content="Conteúdo original.")
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    response = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Física",
            "content": "",
            "remove_primary_content": "1",
            "submit": "Salvar alterações",
        },
    )

    assert response.status_code == 200
    assert "Mantenha pelo menos um conteúdo escrito nesta matéria." in response.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.content == "Conteúdo original."


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
