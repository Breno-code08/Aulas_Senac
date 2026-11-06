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


def test_site_uses_left_sidebar_navigation_and_dark_blue_theme(app):
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
    home_client = app.test_client()
    home_client.post(
        "/auth/cadastro",
        data={
            "email": "homepage-logo@example.com",
            "password": "secure-homepage-password-123",
            "confirm_password": "secure-homepage-password-123",
            "submit": "Criar conta",
        },
    )
    home_page = home_client.get("/").get_data(as_text=True)
    assert '<span class="home-logo-tile"><img class="home-logo"' in home_page
    assert 'src="/static/images/study-logo.png"' in home_page

    login_submit = page.split('<form method="post" novalidate>', 1)[1].split("</form>", 1)[0]
    assert 'type="submit" value="Entrar"' in login_submit

    stylesheet = app.test_client().get("/static/css/style.css")
    assert stylesheet.status_code == 200
    css = stylesheet.get_data(as_text=True)
    assert "--paper: #080d18" in css
    assert "--green: #4d94ff" in css
    assert ':root[data-theme="light"]' in css
    assert "--paper: #f8fafc" in css
    assert ".home-logo-tile { display: inline-flex; width: 72px; height: 58px" in css
    assert ".home-logo { display: block; width: 100%; height: 100%; filter: brightness(0)" in css
    assert ".site-sidebar .brand { display: flex; width: 58px; height: 58px; min-height: 58px; align-self: center" in css
    assert "border: 1px solid #31558a" in css
    assert ".brand-logo { display: block; width: 48px; height: auto; filter: brightness(0)" in css
    assert ":root[data-theme=\"light\"] .brand-logo" in css
    assert ':root[data-theme="light"] .site-sidebar .brand { border-color: #2563eb; background: #2563eb; }' in css
    assert ':root[data-theme="light"] .home-logo-tile { background: #2563eb; }' in css
    assert ":root[data-theme=\"light\"] .brand-logo," in css
    assert ":root[data-theme=\"light\"] .home-logo { filter: brightness(0) invert(1); }" in css
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
    assert "Adicionar matéria" in page
    assert "Adicionar conteúdo" in page
    assert "Descrição" in page
    assert "PDF" in page
    assert "Link" in page
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
            "content_descriptions": ["Equações e expressões algébricas."],
            "content_video_urls": ["https://example.com/aula"],
            "content_pdfs": [(BytesIO(b"%PDF-1.4\nmaterial"), "algebra.pdf")],
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Material adicionado ao espaço." in response.get_data(as_text=True)
    assert "Álgebra" in response.get_data(as_text=True)
    assert "Equações e expressões algébricas." in response.get_data(as_text=True)
    assert "Baixar algebra.pdf" in response.get_data(as_text=True)
    assert "Abrir link" in response.get_data(as_text=True)


def test_material_moves_between_pending_and_completed(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Lógica")
        material.resources.append(
            StudyMaterialResource(kind="content", content="Algoritmos e variáveis.")
        )
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
    assert "Reabrir conteúdo" in completed_page
    with app.app_context():
        assert db.session.get(StudyMaterial, material_id).completed is True

    reopened = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/status/reabrir",
        follow_redirects=True,
    )
    reopened_page = reopened.get_data(as_text=True)
    assert reopened.status_code == 200
    assert "Matéria movida para pendentes." in reopened_page
    assert "Marcar conteúdo como concluído" in reopened_page
    with app.app_context():
        assert db.session.get(StudyMaterial, material_id).completed is False


def test_material_completes_automatically_when_every_content_is_completed(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Física")
        material.resources.extend(
            [
                StudyMaterialResource(kind="content", content="Aplicações práticas."),
                StudyMaterialResource(
                    kind="content",
                    content="Resumo",
                    pdf_filename="exercicios.pdf",
                    pdf_storage_name="extra.pdf",
                ),
                StudyMaterialResource(
                    kind="content",
                    video_url="https://example.com/exercicios",
                ),
                StudyMaterialResource(
                    kind="content",
                    content="Leis de Newton.",
                    pdf_filename="resumo.pdf",
                    pdf_storage_name="primary.pdf",
                    video_url="https://example.com/newton",
                ),
            ]
        )
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id
        resource_ids = [resource.id for resource in material.resources]

    content_keys = [f"resource-{resource_id}" for resource_id in resource_ids]
    initial_page = client.get(f"/espacos/{space_id}").get_data(as_text=True)
    assert initial_page.count("Marcar conteúdo como concluído") == len(content_keys)
    for content_key in content_keys[:-1]:
        response = client.post(
            f"/espacos/{space_id}/materiais/{material_id}/conteudos/{content_key}/concluir",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Conclua todos os conteúdos para finalizar esta matéria." in response.get_data(
            as_text=True
        )
        with app.app_context():
            assert db.session.get(StudyMaterial, material_id).completed is False

    completed = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/conteudos/{content_keys[-1]}/concluir",
        follow_redirects=True,
    )
    assert completed.status_code == 200
    assert "A matéria foi concluída automaticamente." in completed.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.completed is True
        assert all(resource.completed for resource in material.resources)

    reopened = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/conteudos/{content_keys[0]}/reabrir",
        follow_redirects=True,
    )
    assert reopened.status_code == 200
    assert "Conteúdo movido para pendentes." in reopened.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.completed is False
        assert material.resources[0].completed is False


def test_content_completion_rejects_unknown_content_key(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Lógica")
        material.resources.append(
            StudyMaterialResource(kind="content", content="Algoritmos.")
        )
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    response = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/conteudos/resource-999/concluir"
    )
    assert response.status_code == 404


def test_material_contents_group_description_pdf_and_link(client, app, tmp_path):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Biologia",
            "content_ids": ["", ""],
            "content_descriptions": ["Citologia e organelas.", "Divisão celular."],
            "content_video_urls": [
                "https://example.com/celula",
                "https://example.com/divisao",
            ],
            "content_pdfs": [
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
    assert page.count("Abrir link") == 2
    with app.app_context():
        material = db.session.query(StudyMaterial).one()
        resources = db.session.query(StudyMaterialResource).order_by(StudyMaterialResource.id).all()
        assert len(resources) == 2
        assert all(resource.kind == "content" for resource in resources)
        assert resources[0].video_url == "https://example.com/celula"
        assert resources[1].video_url == "https://example.com/divisao"
        pdf_resource = resources[0]
        pdf_path = tmp_path / "uploads" / pdf_resource.pdf_storage_name
        material_id = material.id
        pdf_resource_id = pdf_resource.id

    edit_page = client.get(f"/espacos/{space_id}/materiais/{material_id}/editar")
    assert "Editar conteúdo" in edit_page.get_data(as_text=True)
    assert edit_page.get_data(as_text=True).count("name=\"content_ids\"") == 3

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
    assert "Conteúdo removido." in edit_after_removal.get_data(as_text=True)
    assert not pdf_path.exists()

    edited = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Biologia",
            "content_ids": [str(resources[1].id), ""],
            "content_descriptions": ["Divisão celular.", "Genética e hereditariedade."],
            "content_video_urls": [
                "https://example.com/divisao",
                "https://example.com/genetica",
            ],
            "content_pdfs": ["", ""],
            "submit": "Salvar alterações",
        },
        follow_redirects=True,
    )
    assert edited.status_code == 200
    assert "Genética e hereditariedade." in edited.get_data(as_text=True)
    assert "Abrir link" in edited.get_data(as_text=True)
    with app.app_context():
        remaining = db.session.query(StudyMaterialResource).order_by(StudyMaterialResource.id).all()
        assert len(remaining) == 2
        assert remaining[0].id == resources[1].id
        assert remaining[0].pdf_filename == "divisao.pdf"
        assert remaining[0].pdf_storage_name is not None
        assert remaining[1].content == "Genética e hereditariedade."


def test_material_rejects_invalid_content_pdf_and_link(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Química",
            "content_ids": [""],
            "content_descriptions": ["Ligações químicas."],
            "content_video_urls": ["javascript:alert(1)"],
            "content_pdfs": [(BytesIO(b"not a PDF"), "anotacoes.pdf")],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert "link HTTP ou HTTPS válido" in response.get_data(as_text=True)
    assert "não parece ser um PDF válido" in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.query(StudyMaterial).count() == 0


def test_material_can_be_created_with_description_pdf_and_link_together(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Física",
            "content_ids": [""],
            "content_descriptions": ["Leis de Newton e movimento."],
            "content_video_urls": ["https://example.com/newton"],
            "content_pdfs": [(BytesIO(b"%PDF-1.4\nnewton"), "newton.pdf")],
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Material adicionado ao espaço." in response.get_data(as_text=True)
    assert "Leis de Newton e movimento." in response.get_data(as_text=True)
    assert "Baixar newton.pdf" in response.get_data(as_text=True)
    assert "Abrir link" in response.get_data(as_text=True)


def test_material_can_be_created_without_content_items(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    response = client.post(
        f"/espacos/{space_id}/materiais",
        data={"subject": "História"},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Material adicionado ao espaço." in response.get_data(as_text=True)
    assert "Nenhum conteúdo adicionado." in response.get_data(as_text=True)


def test_material_rejects_non_pdf_and_non_http_link(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        db.session.add(space)
        db.session.commit()
        space_id = space.id

    invalid_pdf = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Química",
            "content_ids": [""],
            "content_descriptions": ["Ligações químicas."],
            "content_video_urls": [""],
            "content_pdfs": [(BytesIO(b"not a PDF"), "anotacoes.pdf")],
        },
        content_type="multipart/form-data",
    )
    assert invalid_pdf.status_code == 200
    assert "não parece ser um PDF válido" in invalid_pdf.get_data(as_text=True)

    invalid_url = client.post(
        f"/espacos/{space_id}/materiais",
        data={
            "subject": "Química",
            "content_ids": [""],
            "content_descriptions": ["Ligações químicas."],
            "content_video_urls": ["javascript:alert(1)"],
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
            "content_ids": [""],
            "content_descriptions": ["Citologia e estrutura celular."],
            "content_video_urls": [""],
            "content_pdfs": [(BytesIO(b"%PDF-1.4\nconteudo"), "bio.pdf")],
        },
        content_type="multipart/form-data",
    )
    assert added.status_code == 302

    with app.app_context():
        from app.models import StudyMaterial

        material = db.session.query(StudyMaterial).one()
        material_id = material.id
        content = material.resources[0]
        content_id = content.id
        stored_path = tmp_path / "uploads" / content.pdf_storage_name

    downloaded = client.get(
        f"/espacos/{space_id}/materiais/{material_id}/recursos/{content_id}/pdf"
    )
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
        material = StudyMaterial(subject="Matemática")
        material.resources.extend(
            [
                StudyMaterialResource(kind="content", content="Conteúdo original."),
                StudyMaterialResource(
                    kind="content",
                    content="Conteúdo a remover.",
                    pdf_filename="original.pdf",
                    pdf_storage_name="original.pdf",
                    video_url="https://example.com/original",
                ),
            ]
        )
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id
        replace_content_id = material.resources[1].id

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(exist_ok=True)
    old_pdf = upload_dir / "original.pdf"
    old_pdf.write_bytes(b"%PDF-1.4\noriginal")

    edit_page = client.get(f"/espacos/{space_id}/materiais/{material_id}/editar")
    assert edit_page.status_code == 200
    assert "value=\"Matemática\"" in edit_page.get_data(as_text=True)
    assert "Conteúdo original." in edit_page.get_data(as_text=True)
    assert "Conteúdo a remover." in edit_page.get_data(as_text=True)

    response = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Matemática avançada",
            "content_ids": [str(replace_content_id)],
            "content_descriptions": ["Conteúdo atualizado."],
            "content_video_urls": ["https://example.com/atualizado"],
            "content_pdfs": [(BytesIO(b"%PDF-1.7\nnovo arquivo"), "atualizado.pdf")],
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
        assert len(material.resources) == 1
        content = material.resources[0]
        assert content.pdf_filename == "atualizado.pdf"
        assert content.video_url == "https://example.com/atualizado"
        assert (upload_dir / content.pdf_storage_name).read_bytes().startswith(b"%PDF-1.7")


def test_material_edit_rejects_invalid_pdf(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Física")
        material.resources.append(
            StudyMaterialResource(kind="content", content="Conteúdo original.")
        )
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id
        content_id = material.resources[0].id

    response = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Física",
            "content_ids": [str(content_id)],
            "content_descriptions": ["Conteúdo atualizado."],
            "content_video_urls": [""],
            "content_pdfs": [(BytesIO(b"not a PDF"), "invalido.pdf")],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert "não parece ser um PDF válido" in response.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.resources[0].content == "Conteúdo original."


def test_any_content_can_be_removed_in_edit_page_and_all_can_be_removed(client, app):
    with app.app_context():
        space = StudySpace(owner_id=current_test_user_id(), name="Sala de estudo")
        material = StudyMaterial(subject="Física")
        material.resources.extend(
            [
                StudyMaterialResource(kind="content", content="Conteúdo original."),
                StudyMaterialResource(kind="content", content="Outro conteúdo."),
            ]
        )
        space.materials.append(material)
        db.session.add(space)
        db.session.commit()
        space_id = space.id
        material_id = material.id

    edit = client.get(f"/espacos/{space_id}/materiais/{material_id}/editar")
    assert "Editar conteúdo" in edit.get_data(as_text=True)
    with app.app_context():
        ids = [
            str(resource.id)
            for resource in db.session.get(StudyMaterial, material_id).resources
        ]

    removed_one = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={
            "subject": "Física",
            "content_ids": [ids[1]],
            "content_descriptions": ["Outro conteúdo."],
            "content_video_urls": [""],
            "content_pdfs": [""],
            "submit": "Salvar alterações",
        },
        follow_redirects=True,
    )

    assert removed_one.status_code == 200
    assert "Material atualizado." in removed_one.get_data(as_text=True)
    assert "Conteúdo original." not in removed_one.get_data(as_text=True)
    assert "Outro conteúdo." in removed_one.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert len(material.resources) == 1

    removed_all = client.post(
        f"/espacos/{space_id}/materiais/{material_id}/editar",
        data={"subject": "Física", "submit": "Salvar alterações"},
        follow_redirects=True,
    )

    assert removed_all.status_code == 200
    assert "Nenhum conteúdo adicionado." in removed_all.get_data(as_text=True)
    with app.app_context():
        material = db.session.get(StudyMaterial, material_id)
        assert material.resources == []


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
