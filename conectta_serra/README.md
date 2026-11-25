# Conectta Serra — Python + Flask + MySQL

Projeto web regional de serviços para Serra Talhada–PE. Backend em **Python**, com interface em HTML, CSS e JavaScript. Por padrão, os dados ficam no banco **MySQL** do XAMPP.

## Instalar no Windows (incluindo outro computador)

1. Instale **Python 3.12 ou superior** e o **XAMPP**. Na instalação do Python, marque **Add Python to PATH**.
2. Copie a pasta completa do projeto para o computador. Mantenha juntos os arquivos `.bat`, `iniciar.py`, `requirements.txt`, `app/` e `migrations/`.
3. Abra o XAMPP Control Panel e inicie **MySQL**.
4. Dê duplo clique em `preparar_pc.bat` uma única vez. Ele cria o ambiente isolado `.venv` e instala as dependências.
5. Dê duplo clique em `iniciar_site.bat`. Ele verifica o MySQL, abre o navegador e inicia o site.

```bash
http://127.0.0.1:5000/
```

O iniciador cria automaticamente o banco `conectta`, prepara as tabelas e carrega dados de demonstração na primeira execução. Mantenha abertas as janelas do XAMPP/MySQL e do site enquanto estiver usando o sistema; feche a janela do site ou pressione **Ctrl+C** para encerrá-lo.

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
  preparar_pc.bat             # cria ambiente e instala dependências no Windows
  iniciar_site.bat            # verifica MySQL e inicia o site
  exportar_banco.bat          # gera backup SQL para transferência
  importar_banco.bat          # restaura backup SQL
  database_transfer.py        # rotinas de backup MySQL
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

O banco padrão é o MySQL em `127.0.0.1:3306`, esquema `conectta`, usuário `root` e senha vazia. Os cadastros do app ficam na tabela `users`; uma tabela preexistente chamada `usuarios` permanece intacta e não é usada pelo app. Se sua instalação tiver senha ou outros dados de conexão, copie `.env.example` para `.env` e ajuste `DATABASE_URL`, por exemplo `mysql+pymysql://root:SENHA@127.0.0.1:3306/conectta?charset=utf8mb4`. A senha deve ficar somente no `.env`, que não deve ser compartilhado.

### Exportar e importar em outro computador

No computador original, inicie o MySQL do XAMPP e execute `exportar_banco.bat`. Ele gera `conectta-serra-backup.sql`. Copie esse arquivo e a pasta do projeto para o outro computador. Não copie `.venv`, `.env` nem `instance/session.key`; não compartilhe credenciais.

No outro computador:

1. Instale Python e XAMPP e inicie o MySQL.
2. Execute `preparar_pc.bat`.
3. Execute `iniciar_site.bat` uma vez para criar o banco vazio e as tabelas; feche o site depois.
4. Execute `importar_banco.bat` e informe o caminho do arquivo `conectta-serra-backup.sql`. Confirme a substituição das tabelas quando solicitado.
5. Execute `iniciar_site.bat` novamente.

Por padrão, o MySQL local do XAMPP usa `root` sem senha. Se o computador tiver senha ou outra porta, crie `.env` a partir de `.env.example` e ajuste `DATABASE_URL`. O arquivo `.env` é local e não deve ser incluído na cópia. O iniciador cria uma chave de sessão local automaticamente. Os testes usam SQLite em memória.

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
