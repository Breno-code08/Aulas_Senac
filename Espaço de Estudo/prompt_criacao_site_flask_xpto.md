# Prompt para criação de um site XPTO com Flask

> **Instrução de uso:** substitua os valores `XPTO` pelos nomes e
> detalhes reais do projeto quando necessário. Mantenha `XPTO` como
> placeholder enquanto os requisitos ainda não estiverem definidos.

## 1. Objetivo

Atue como um(a) engenheiro(a) de software sênior, com experiência em
Python, Flask, arquitetura modular, bancos de dados relacionais e
desenvolvimento web.

Crie um site chamado **Espaço de Estudos**, utilizando **Python com Flask**, com
arquitetura modular, persistência de dados em um banco de dados **breno01**
e funcionalidades completas de CRUD (Create, Read, Update e Delete).

O projeto deve ser organizado, escalável, de fácil manutenção e seguir
boas práticas de desenvolvimento. Não concentre toda a aplicação em um
único arquivo.

## 2. Tecnologias e requisitos

Utilize as seguintes tecnologias:

-   **Backend:** Python 3 e Flask.
-   **Arquitetura:** aplicação Flask modular, preferencialmente com
    Application Factory e Blueprints.
-   **ORM:** Flask-SQLAlchemy / SQLAlchemy para definição e manipulação
    dos models.
-   **Banco de dados:** Usuarios, com conexão configurada por variáveis de
    ambiente.
-   **Frontend:** HTML5, CSS3 e JavaScript.
-   **Templates:** Jinja2, utilizando o mecanismo de templates do Flask.
-   **Configuração:** arquivo `.env` para configurações locais e
    segredos; disponibilize também um `.env.example` sem credenciais
    reais.
-   **Dependências:** arquivo `requirements.txt` com todas as
    bibliotecas necessárias e versões compatíveis.

Caso o banco breno01 exija um driver específico, inclua-o no
`requirements.txt` e implemente a conexão de acordo com a tecnologia
escolhida.

## 3. Funcionalidades obrigatórias

Implemente um CRUD completo para a entidade principal **Espaço de Estudos**.

### Create --- Criar

-   Disponibilizar uma página/formulário para cadastrar um novo
    registro.
-   Validar os campos obrigatórios no backend.
-   Exibir mensagens claras de sucesso ou erro.
-   Persistir os dados no banco de dados.

### Read --- Consultar

-   Disponibilizar uma página de listagem dos registros.
-   Exibir os dados de forma organizada em tabela ou cards.
-   Implementar visualização detalhada de um registro.
-   Incluir busca ou filtro quando fizer sentido para os campos da
    entidade.
-   Tratar corretamente listas vazias e falhas de consulta.

### Update --- Atualizar

-   Permitir a edição de registros existentes.
-   Carregar os dados atuais no formulário.
-   Validar os dados antes de salvar.
-   Exibir mensagens de sucesso ou erro.

### Delete --- Excluir

-   Permitir a exclusão de registros.
-   Solicitar confirmação antes da exclusão.
-   Tratar registros inexistentes e erros de integridade referencial.
-   Utilizar método HTTP apropriado e proteção contra CSRF nos
    formulários.

## 4. Models e banco de dados

-   Crie os models utilizando SQLAlchemy.
-   Cada entidade deve possuir seu próprio model, em arquivo ou módulo
    organizado de acordo com o tamanho do projeto.
-   Defina corretamente os tipos de dados, chaves primárias, chaves
    estrangeiras, restrições e relacionamentos necessários.
-   Utilize migrations (Flask-Migrate/Alembic) para versionar alterações
    no schema.
-   Não espalhe comandos SQL ou regras de persistência pelas rotas.
    Centralize o acesso aos dados nos models e/ou em uma camada de
    serviços/repositórios.
-   Configure a conexão por variável de ambiente, por exemplo
    `DATABASE_URL`.
-   Não deixe credenciais, senhas ou tokens diretamente no código-fonte.
-   Inclua tratamento de erros de conexão e instruções para inicializar
    o banco.

Os campos específicos da entidade, seus relacionamentos e regras de
negócio devem ser definidos conforme os requisitos do **breno01**. Não
invente regras de negócio que não tenham sido especificadas; sinalize os
pontos que precisam de definição.

## 5. Arquitetura e estrutura de pastas

Organize o projeto de forma modular. Utilize a estrutura abaixo como
referência e adapte-a apenas quando houver justificativa técnica:

``` text
blog/
│
├── app/
│   ├── __init__.py             
│   ├── extensions.py            
│   ├── config.py                
│   │
│   ├── models/
|   |   ├── user.py
│   │   ├── post.py
│   │   └── comment.py              
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── xpto_routes.py       # Rotas relacionadas ao CRUD de XPTO
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── xpto_service.py      # Regras de negócio e operações da entidade
│   │
│   ├── forms/
│   │   ├── __init__.py
│   │   └── xpto_forms.py        # Formulários e validações, se aplicável
│   │
│   ├── templates/
│   │   ├── base.html            # Layout base compartilhado
│   │   ├── index.html           # Página inicial
│   │   └── xpto/
│   │       ├── list.html        # Listagem
│   │       ├── detail.html      # Detalhes
│   │       ├── create.html      # Cadastro
│   │       └── edit.html        # Edição
│   │
│   └── static/
│       ├── css/
│       │   ├── style.css        # Estilos globais
│       │   └── xpto.css         # Estilos específicos da área XPTO
│       │
│       ├── js/
│       │   ├── main.js          # Scripts globais
│       │   └── xpto.js          # Scripts específicos da área XPTO
│       │
│       └── images/
│
├── migrations/                  # Histórico das migrations
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_xpto.py             # Testes do CRUD
│
├── .env.example                 # Exemplo de variáveis de ambiente
├── .gitignore
├── config.py                    # Opcional: ponto de configuração externo, se necessário
├── requirements.txt             # Dependências Python
├── run.py                       # Ponto de entrada da aplicação
└── README.md                    # Documentação e instruções
```

### Separação obrigatória do frontend

A separação entre HTML, CSS e JavaScript deve ser respeitada:

-   **HTML:** mantenha os arquivos `.html` dentro de `app/templates/`.
-   **CSS:** mantenha os arquivos `.css` dentro de `app/static/css/`.
-   **JavaScript:** mantenha os arquivos `.js` dentro de
    `app/static/js/`.
-   **Imagens e outros arquivos estáticos:** mantenha-os em diretórios
    apropriados dentro de `app/static/`.

Cada página deve ter seu próprio template quando possuir conteúdo ou
estrutura específicos. Utilize `base.html` para elementos
compartilhados, como cabeçalho, menu, rodapé e inclusão de arquivos
CSS/JS. Evite duplicar marcação e não coloque CSS ou JavaScript extensos
diretamente nos arquivos HTML.

Organize os arquivos estáticos por funcionalidade quando o projeto
crescer. Carregue scripts específicos apenas nas páginas que precisam
deles.

## 6. Boas práticas de implementação

-   Utilize Application Factory (`create_app`) para inicializar a
    aplicação.
-   Separe as rotas por domínio ou funcionalidade usando Blueprints.
-   Mantenha regras de negócio na camada `services`, evitando rotas
    extensas.
-   Utilize models para representar as entidades do banco.
-   Utilize consultas parametrizadas/ORM; nunca concatene dados do
    usuário em SQL.
-   Valide dados tanto no frontend quanto no backend. A validação do
    backend é obrigatória.
-   Utilize tratamento de exceções e páginas de erro adequadas (404 e
    500).
-   Utilize mensagens flash para feedback das operações.
-   Implemente proteção CSRF em formulários.
-   Proteja configurações sensíveis por variáveis de ambiente.
-   Evite duplicação de código e mantenha nomes claros e consistentes.
-   Não utilize dados fictícios como se fossem dados reais do sistema.
-   Não implemente funcionalidades fora do escopo sem documentá-las.

## 7. Interface e experiência do usuário

Crie uma interface moderna, limpa, responsiva e intuitiva.

A interface deve incluir:

-   Menu de navegação.
-   Página inicial ou dashboard simples.
-   Listagem dos registros.
-   Formulários de cadastro e edição.
-   Ações visíveis para visualizar, editar e excluir.
-   Confirmação de exclusão.
-   Mensagens de feedback para sucesso, validação e falhas.
-   Estados vazios (quando não houver registros).
-   Layout adaptável para desktop, tablet e celular.

Mantenha a identidade visual do projeto como ****, sem assumir
cores, logotipo ou referências visuais que não tenham sido informadas.
Se esses detalhes não forem fornecidos, utilize um tema neutro e fácil
de personalizar.

## 8. Arquivo requirements.txt

Crie obrigatoriamente o arquivo `requirements.txt` na raiz do projeto.

Ele deve listar todas as dependências Python realmente utilizadas pela
aplicação, incluindo, conforme necessário:

-   Flask
-   Flask-SQLAlchemy
-   Flask-Migrate
-   Flask-WTF
-   python-dotenv
-   Driver do banco de dados XPTO
-   Bibliotecas adicionais utilizadas no projeto

Utilize versões compatíveis e, preferencialmente, fixe versões para
tornar a instalação reproduzível. Não inclua bibliotecas que não sejam
utilizadas.

O nome correto do arquivo é `requirements.txt`.

## 9. Documentação e execução

Crie um `README.md` contendo:

1.  Descrição do projeto.
2.  Tecnologias utilizadas.
3.  Estrutura de diretórios.
4.  Pré-requisitos.
5.  Instruções para criar e ativar um ambiente virtual.
6.  Instalação das dependências com `pip install -r requirements.txt`.
7.  Configuração das variáveis de ambiente.
8.  Configuração e inicialização do banco de dados.
9.  Execução das migrations.
10. Como iniciar a aplicação.
11. Como executar os testes.

Inclua os comandos necessários para Windows e Linux/macOS quando houver
diferenças.

## 10. Entregáveis

Ao concluir, forneça o projeto com:

-   Todos os arquivos Python necessários.
-   Models SQLAlchemy.
-   Rotas organizadas em Blueprints.
-   Camada de serviços, quando aplicável.
-   Templates HTML separados por página.
-   Arquivos CSS separados dos templates.
-   Arquivos JavaScript separados dos templates.
-   Conexão funcional com o banco XPTO por configuração externa.
-   CRUD completo da entidade XPTO.
-   Arquivo `requirements.txt`.
-   Arquivo `.env.example`.
-   Arquivo `.gitignore`.
-   Migrations.
-   Testes automatizados.
-   README.md com instruções completas.

Não entregue apenas trechos de código ou exemplos isolados. Gere todos
os arquivos necessários, respeitando a estrutura de diretórios definida.

## 11. Critérios de aceitação

Considere o projeto concluído somente quando:

-   A aplicação iniciar corretamente seguindo o README.
-   A conexão com o banco XPTO funcionar com as configurações
    fornecidas.
-   Os models estiverem mapeados corretamente.
-   Todas as operações do CRUD funcionarem.
-   Os templates, CSS e JavaScript estiverem separados e organizados.
-   O arquivo `requirements.txt` permitir instalar as dependências.
-   Não houver credenciais sensíveis versionadas.
-   Os testes automatizados forem executáveis e passarem no ambiente
    configurado.
-   O código estiver modular, legível e sem dependências desnecessárias.

## 12. Orientação final para a IA

Antes de começar a implementação:

1.  Analise os requisitos disponíveis.
2.  Identifique quais informações sobre a entidade XPTO e o banco XPTO
    ainda não foram especificadas.
3.  Não invente campos, relacionamentos ou regras de negócio. Quando
    forem indispensáveis, registre-os como placeholders ou solicite
    esclarecimentos.
4.  Apresente brevemente a arquitetura e a estrutura de pastas
    planejadas.
5.  Em seguida, implemente o projeto completo.

Durante a implementação, priorize código funcional, segurança, clareza e
facilidade de manutenção. Ao final, apresente um resumo do que foi
criado, os comandos para executar a aplicação e quaisquer configurações
que ainda precisem ser preenchidas.
