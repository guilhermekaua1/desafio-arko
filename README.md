# Desafio Técnico Arko - Plataforma de Análise de Dados

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-20.10-2496ED?style=for-the-badge&logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-2.0-130654?style=for-the-badge&logo=pandas)

## 📖 Descrição do Projeto

Esta é uma aplicação web completa desenvolvida com Django, criada como solução para o Desafio Técnico da Arko. A aplicação consome e processa dados de duas fontes distintas: uma API REST (IBGE) e um ficheiro CSV de grande volume (Receita Federal). Os dados são armazenados numa base de dados PostgreSQL e apresentados numa interface web com funcionalidades de listagem, filtragem e paginação.

O projeto foi totalmente containerizado com Docker para garantir um ambiente de desenvolvimento e execução 100% reprodutível.

### ✨ Nota de Intenção e Arquitetura

A arquitetura do projeto foi uma decisão deliberada para alinhar a solução diretamente com os requisitos. Optei por usar o padrão **MTV (Model-Template-View)** nativo do Django, pois o desafio pedia a criação de "páginas web" renderizadas no servidor. A utilização do Django Rest Framework (DRF) foi considerada, mas descartada para evitar "over-engineering", uma vez que uma API não era um requisito. A ênfase foi colocada na robustez do backend, na performance do processamento de dados e na qualidade do código através de testes unitários.

## 🚀 Funcionalidades

* **Importação de Dados do IBGE:** Um comando otimizado (`importer`) que consome o endpoint de Distritos da API do IBGE para popular de forma eficiente as tabelas de Regiões, Estados, Municípios e Distritos, fazendo apenas uma chamada de rede.
* **Importação de Dados da Receita Federal:** Um comando robusto e autossuficiente (`populate_companies`) que **descarrega automaticamente** o ficheiro ZIP da Receita Federal, processa o CSV de grande volume (+1.7 GB) em `chunks` para eficiência de memória e utiliza `bulk operations` do Django para uma inserção performática, atualizando registos existentes sem duplicar.
* **Interface Web Segura:** Páginas para listar todas as entidades (Estados, Municípios, Distritos e Empresas), com funcionalidades completas de **filtragem por campo** e **paginação**.
* **Autenticação:** O acesso a todas as páginas de dados é protegido e requer login de utilizador.
* **Testes Automatizados:** O projeto inclui testes unitários para a lógica de negócio mais crítica (o processamento de "chunks" de empresas), garantindo a qualidade e a confiabilidade do código.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.11, Django
* **Base de Dados:** PostgreSQL
* **Containerização:** Docker, Docker Compose
* **Bibliotecas Principais:**
    * `pandas`: Para processamento de alta performance do ficheiro CSV.
    * `django-filter`: Para a criação de filtros dinâmicos nas páginas web.
    * `pydantic`: Para a validação robusta dos dados da API.
    * `psycopg2-binary`: Driver de conexão com o PostgreSQL.
    * `django-environ`: Para a gestão segura de variáveis de ambiente.
    * `tqdm`: Para exibir uma barra de progresso durante o download de ficheiros.

## ⚙️ Pré-requisitos

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/) (geralmente já vem com o Docker Desktop)

## 🚀 Como Executar o Projeto

Siga estes passos para configurar e executar a aplicação localmente.

### 1. Clonar o Repositório
```bash
git clone https://github.com/guilhermekaua1/desafio-arko
cd desafio-arko
```

### 2. Configuração de Variáveis de Ambiente
O projeto utiliza um ficheiro `.env` para gerir as configurações.

```bash
cp .env.example .env
```
**Importante:** Abra o ficheiro `.env` e gere uma nova `SECRET_KEY` para o Django. Pode usar o comando abaixo (com Python instalado na sua máquina) para gerar uma:
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
Cole a chave gerada no seu ficheiro `.env`.

### 3. Construir e Iniciar os Containers
Este comando irá construir a imagem da aplicação Django e iniciar os serviços da web e da base de dados.
```bash
docker-compose up --build -d
```

### 4. Configurar a Base de Dados
Com os contentores em execução, aplique as migrações para criar todas as tabelas na base de dados.
```bash
docker-compose exec web python manage.py migrate
```

### 5. Acessar à Aplicação
Para poder fazer login, crie primeiro um superutilizador:
```bash
docker-compose exec web python manage.py createsuperuser
```
Siga as instruções para definir um nome de utilizador, e-mail e senha.

### 6. Executar as Rotinas de Importação de Dados

Para uma base de dados completa, recomenda-se executar os três comandos abaixo.

**a. Importador Otimizado do IBGE (Rápido):**
Este comando utiliza uma estratégia otimizada, fazendo uma única chamada ao endpoint de `distritos` da API do IBGE para popular a maioria das entidades.

```bash
docker-compose exec web python manage.py importer
```

**b. Importador Completo do IBGE (Garantia de Integridade):**
Este comando busca os dados de cada entidade (Estados, Municípios) em endpoints separados. É mais lento, mas serve como rotina complementar para garantir que mesmo os municípios que não tenham distritos registados na API sejam importados.
```bash
docker-compose exec web python manage.py populate_ibge
```

**c. Importador de Empresas (Receita Federal via S3):**
Este comando descarrega e processa o ficheiro de dados de empresas.
*Nota: Para garantir uma importação rápida e estável para a avaliação, o ficheiro ZIP original da Receita Federal (~400MB) foi previamente alojado num bucket Amazon S3 de alta velocidade. O comando abaixo utiliza esta fonte otimizada.*
**O download deverá ser quase instantâneo, mas o processamento das mais de 22 milhões de linhas ainda pode levar de 10 a 30 minutos.**
```bash
docker-compose exec web python manage.py populate_companies [https://desafio-arko-empresas-final.s3.us-east-1.amazonaws.com/Empresas0.zip](https://desafio-arko-empresas-final.s3.us-east-1.amazonaws.com/Empresas0.zip)
```

### 6. Como Testar o Projeto
O projeto inclui testes unitários para a lógica de importação de empresas. Para os executar:
```bash
docker-compose exec web python manage.py test data_importer
```

## ⚡ Execução Alternativa (sem Docker)

Para executar o projeto localmente sem Docker, será necessário ter o Python 3.11+ e o PostgreSQL instalados na sua máquina.

1.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv .venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate      # Windows
    ```
2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure as variáveis de ambiente:** Crie um ficheiro `.env` (a partir do `.env.example`) e ajuste as variáveis da base de dados (`DB_HOST`, `DB_PORT`, etc.) para corresponderem à sua instalação local do PostgreSQL.
4.  **Execute as migrações e os comandos de importação:**
    ```bash
    python manage.py migrate
    python manage.py importer
    python manage.py populate_companies https://desafio-arko-empresas-final.s3.us-east-1.amazonaws.com/Empresas0.zip
    ```
5.  **Inicie o servidor:**
    ```bash
    python manage.py runserver
    ```

### 7. Acessar à Aplicação

**a. Acessar às Páginas Web (Tarefa 3):**
* Aceda a **http://localhost:8000/**
* Faça login com as credenciais que acabou de criar.
* Você será redirecionado para a lista de estados e poderá navegar por todas as páginas da aplicação.

**b. Acessar ao Django Admin:**
* Aceda a **http://localhost:8000/admin/**
* Use as mesmas credenciais para ver a área de gestão de dados.

## 🔌 Acessar à Base de Dados Diretamente

A base de dados do PostgreSQL dentro do contentor está exposta na porta `5432` da sua máquina local (`localhost`). Pode usar uma ferramenta como DBeaver, Postico ou pgAdmin para se conectar a ela com as seguintes credenciais (do ficheiro `.env`):
* **Host:** `localhost`
* **Porta:** `5432`
* **Utilizador:** `arko_user` (ou o que estiver no seu `.env`)
* **Senha:** `supersecretpassword` (ou o que estiver no seu `.env`)
* **Base de Dados:** `arko_db` (ou o que estiver no seu `.env`)