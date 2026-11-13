# Conectta Serra — Python + Flask + SQLite

Projeto web regional de serviços para Serra Talhada–PE. Backend em **Python**, com interface em HTML, CSS e JavaScript. Os dados ficam no banco **SQLite**, e não no armazenamento do navegador.

## Começar no VS Code

1. Extraia o ZIP inteiro. Mantenha `iniciar.py`, `requirements.txt`, `app/` e `migrations/` juntos.
2. No VS Code, use **Arquivo → Abrir Pasta** e abra a pasta `conectta_serra`.
3. Abra **Terminal → Novo Terminal**.
4. Com Python 3.12 ou superior instalado, execute:

```bash
python -m pip install -r requirements.txt
python iniciar.py
```

5. Abra **http://127.0.0.1:5000/** no navegador. Mantenha o terminal aberto enquanto usa o site.
6. Para encerrar, pressione **Ctrl+C** no terminal.

No Windows, se `python` não for reconhecido e o comando `py` estiver disponível, use `py -m pip install -r requirements.txt` e `py iniciar.py`.

`iniciar.py` prepara o banco pelas migrations, gera uma chave de sessão local e carrega os perfis fictícios na primeira execução. Nas próximas execuções, preserva os dados cadastrados. Não é necessário instalar um servidor de banco de dados.

## Ambiente virtual (opcional, recomendado)

Windows / PowerShell, sem precisar ativar scripts:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe iniciar.py
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python iniciar.py
```

O projeto inclui `.vscode/launch.json`. Com o suporte a Python configurado no VS Code e o interpretador escolhido, você também pode usar a configuração **Conectta Serra (Python/Flask)** para iniciar a depuração.

## Cadastros separados

- **Usuário/cliente:** página `#cadastro-usuario` e endpoint Python `POST /api/register/users`.
- **Profissional:** página `#cadastro-profissional` e endpoint `POST /api/register/professionals`, com profissão obrigatória e criação de perfil vinculado.
- Também há atalhos `/cadastro/usuario` e `/cadastro/profissional`.
- As páginas têm formulários próprios, campos obrigatórios, verificação de e-mail e prevenção de e-mails duplicados.

## Funcionalidades

- Cadastro, consulta, listagem com busca/filtros, edição e exclusão de usuários.
- Cadastro e manutenção de serviços pelo profissional; categorias e gestão pelo administrador.
- Catálogo de serviços, perfis profissionais e favoritos.
- Solicitações de orçamento, mensagens por pedido, aceite, cancelamento e conclusão.
- Avaliação única por solicitação concluída.
- Relatórios filtrados por status e data de cadastro, com exportação em PDF e CSV.
- Validação no servidor, autorização por perfil, CSRF e chaves estrangeiras para preservar o histórico.

Os perfis fictícios de demonstração são preservados na exclusão. Para testar o CRUD completo de usuários, entre como administrador e crie um novo usuário. Registros com histórico relacionado não podem ser excluídos; serviços com histórico podem ser pausados.

## Perfis e apresentação

Em **Experimentar os perfis**, escolha **Sou cliente**, **Sou profissional** ou **Sou administrador**. São papéis acadêmicos, sem senha própria. O cadastro cria uma sessão para o novo registro. A troca entre contas usa os três perfis de exemplo; não existe recuperação de senha nem login comercial neste MVP.

Roteiro sugerido:

1. Mostre a página inicial e faça uma busca por elétrica.
2. Demonstre as páginas de cadastro de cliente e profissional separadas.
3. Entre no cliente de exemplo, abra Rafael Lima e solicite um serviço para uma data futura.
4. Abra a conversa do pedido e envie uma mensagem.
5. Troque para profissional, aceite o pedido e responda.
6. Volte ao cliente, conclua e avalie.
7. Como administrador, teste o cadastro, consulta, edição e exclusão de um novo usuário.
8. Exporte um relatório PDF e um CSV com os filtros escolhidos.

## Organização do código

```text
conectta_serra/
  iniciar.py                  # prepara o banco e inicia o site
  run.py                      # entrada alternativa para Flask CLI
  requirements.txt
  .env.example
  app/
    __init__.py               # Application Factory
    config.py
    extensions.py             # SQLAlchemy, Migrate e CSRF
    models/                   # tabelas e relacionamentos
    routes/                   # Blueprints da interface e da API
    services/                 # validações, consultas e relatórios
    templates/index.html      # interface Jinja2
    static/css/style.css
    static/js/app.js
    seed.json                 # exemplos fictícios
  migrations/                 # histórico do esquema
  tests/test_flask.py
```

A interface usa navegação por fragmentos e conversa com a API Flask. HTML, CSS e JavaScript permanecem separados. As operações de dados são feitas por Python com SQLAlchemy.

## Banco e configurações

O banco padrão fica em `instance/conectta.db`. A chave local fica em `instance/session.key`. A pasta `instance/`, `.env` e ambientes virtuais não fazem parte da distribuição. Faça cópia do arquivo do banco com o servidor parado caso queira guardar sua demonstração.

Um arquivo `.env` é opcional. Para personalizar, copie `.env.example` e configure `SECRET_KEY`, `DATABASE_URL` e `DEMO_MODE`. Se `SECRET_KEY` não for informada, o iniciador gera uma chave local persistente. O esquema e os testes usam SQLite. Outro banco exige driver e validação próprios.

Para futuras mudanças nos models:

```bash
python -m flask --app run db migrate -m "descricao da alteracao"
python -m flask --app run db upgrade
```

Revise as migrations antes de aplicá-las. Não altere migrations já aplicadas. A primeira inicialização executa somente as migrations incluídas.

## Testes

```bash
python -m pytest -q
```

Cobrem CSRF, autorização, cadastro de clientes e profissionais, campos obrigatórios, e-mails duplicados, vínculo do profissional, CRUD, integridade, fluxo de solicitações/mensagens/avaliações e exportações PDF/CSV.

Este pacote é uma demonstração acadêmica local. Ele inicia em `127.0.0.1`, sem depuração e sem alterar a hospedagem privada existente. Não há pagamentos, notificações automáticas, upload de portfólio ou autenticação comercial.
