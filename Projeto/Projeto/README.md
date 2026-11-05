# Espaço de Estudos

Aplicação web modular em Flask para organizar individualmente espaços de estudo e seus materiais. Cada espaço pode reunir matérias, arquivos PDF e links para videoaulas, além de uma cor personalizável (sálvia, azul, lavanda, pêssego, rosa ou amarelo) e símbolos relacionados a disciplinas, como livros, matemática, ciências, química, tecnologia, geografia, escrita, arte, música, idiomas e outros. O cadastro inclui nome, descrição e localização/referência opcional; não há controle de capacidade, pois o uso é individual.

## Tecnologias

- Python 3.10+
- Flask, Flask-SQLAlchemy e Flask-Migrate (SQLAlchemy/Alembic)
- Flask-WTF para validação de formulários e proteção CSRF
- MySQL (`breno01`) via PyMySQL; a conexão é configurada por variáveis de ambiente
- Jinja2, CSS e JavaScript

## Estrutura

```text
app/
├── forms/          # Formulários e validações
├── models/         # Entidades SQLAlchemy
├── routes/         # Blueprints HTTP
├── services/       # Operações de persistência
├── static/         # CSS e JavaScript
└── templates/      # Templates Jinja2
migrations/         # Histórico Alembic
tests/              # Testes automatizados
instance/           # Banco local e arquivos não versionados
```

## Pré-requisitos e instalação

É necessário Python 3.10 ou superior e `pip`.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Edite `.env` e substitua `SECRET_KEY` por um segredo aleatório (gere um com `python -c "import secrets; print(secrets.token_hex(32))"`). A factory carrega esse arquivo automaticamente ao iniciar, inclusive quando `run.py` é executado diretamente; variáveis já definidas no ambiente têm precedência. A aplicação não inicia sem uma chave configurada. O `.env.example` contém a configuração MySQL informada: host `127.0.0.1`, porta `3306`, banco `breno01` e usuário `root` sem senha. O servidor MySQL precisa estar ativo e o banco `breno01` já deve existir. Para ambientes permanentes, prefira um usuário MySQL dedicado com permissões somente para esse banco e defina uma senha.

É possível usar uma URL SQLAlchemy completa por `DATABASE_URL`; quando definida, ela tem precedência sobre as variáveis `MYSQL_*`.

## Banco de dados e migrations

Após instalar as dependências e configurar `.env`, inicialize o banco:

```bash
flask --app run.py db upgrade
```

Para criar uma migration após alterar os models:

```bash
flask --app run.py db migrate -m "Descrição da alteração"
flask --app run.py db upgrade
```

## Executar

```bash
flask --app run.py run --debug
```

A aplicação fica disponível em `http://127.0.0.1:5000`. Também é possível iniciar pelo VS Code ou terminal com `python run.py`.
No VS Code, execute `run.py` (ou use o comando Flask acima); não execute `app/__init__.py` diretamente, pois esse arquivo inicializa o pacote e não é um ponto de entrada.

## Testes

```bash
pytest
```

Os testes usam um banco SQLite temporário independente do banco local de desenvolvimento.

## Rotas principais

- `/` — página inicial
- `/suporte` — orientações de uso e dúvidas frequentes
- `/sobre` — informações sobre o projeto
- `/contato` — canal de contato configurável por e-mail
- `/espacos/` — listagem e busca
- `/espacos/novo` — cadastro
- `/espacos/<id>` — detalhes
- `/espacos/<id>/editar` — edição
- `/espacos/<id>/excluir` — exclusão via POST com confirmação
- `/espacos/<id>/materiais` — adicionar assunto com conteúdo escrito obrigatório e PDF/videoaula opcionais
- `/espacos/<id>/materiais/<material_id>/editar` — editar assunto, conteúdo, PDF ou videoaula
- `/espacos/<id>/materiais/<material_id>/status/concluir` — marcar uma matéria como concluída
- `/espacos/<id>/materiais/<material_id>/status/reabrir` — mover uma matéria concluída de volta para pendentes
- `/espacos/<id>/materiais/<material_id>/pdf` — baixar um PDF associado
- `/espacos/<id>/materiais/<material_id>/recursos/<resource_id>/pdf` — baixar PDFs adicionais
- `/espacos/<id>/materiais/<material_id>/recursos/<resource_id>/excluir` — remover conteúdo adicional
- `/espacos/<id>/materiais/<material_id>/excluir` — remover um material

## Contas e privacidade

Crie uma conta em `/auth/cadastro` com e-mail e senha de 12 a 128 caracteres, entre por `/auth/login` e saia por `/auth/logout` (POST). Cada conta só acessa os próprios espaços e materiais.

A migration de autenticação interrompe a atualização caso existam espaços sem proprietário, em vez de atribuí-los automaticamente a uma conta. Resolva os registros antigos antes de atualizar o banco.

Cada matéria exige o nome do assunto e o conteúdo escrito; PDF e link de videoaula são opcionais. Também é possível incluir vários conteúdos escritos, PDFs (16 MB por arquivo) e links adicionais na mesma matéria. Os PDFs são armazenados em `instance/uploads/`, fora da pasta pública de arquivos estáticos, e verificados pelo cabeçalho PDF antes de serem salvos. A migration deve ser aplicada após atualizar o código:

```bash
flask --app run.py db upgrade
```

Para habilitar o link de contato por e-mail, defina `CONTACT_EMAIL` no `.env` local. O formulário de contato usa o aplicativo de e-mail padrão do dispositivo do visitante; o projeto não envia nem armazena mensagens.
