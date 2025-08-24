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
# Copie o ficheiro de exemplo para criar o seu ficheiro .env local
cp .env.example .env
```
**Importante:** Abra o ficheiro `.env` e gere uma nova `SECRET_KEY` para o Django. Pode usar o comando abaixo (com Python instalado na sua máquina) para gerar uma:
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
Cole a chave gerada no seu ficheiro `.env`.

### 3. Construir e Iniciar os Contentores
Este comando irá construir a imagem da aplicação Django e iniciar os serviços da web e da base de dados.
```bash
docker-compose up --build -d
```

### 4. Configurar a Base de Dados
Com os contentores em execução, aplique as migrações para criar todas as tabelas na base de dados.
```bash
docker-compose exec web python manage.py migrate
```

### 5. Executar as Rotinas de Importação de Dados
Os dados são importados através de comandos de gestão customizados.

**a. Importar Dados do IBGE (Estados, Municípios, etc.):**
```bash
docker-compose exec web python manage.py importer
```

**b. Importar Dados das Empresas (Receita Federal):**
Este comando irá primeiro descarregar um ficheiro de ~400MB zipado (pode demorar) e depois processar mais de 22 milhões de linhas. **Este processo é longo e pode levar de 10 a 30 minutos.**
```bash
docker-compose exec web python manage.py populate_companies [https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/2025-05/Empresas0.zip](https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/2025-05/Empresas0.zip)
```

### 6. Como Testar o Projeto
O projeto inclui testes unitários para a lógica de importação de empresas. Para os executar:
```bash
docker-compose exec web python manage.py test data_importer
```

### 7. Acessar à Aplicação
Para poder fazer login, crie primeiro um superutilizador:
```bash
docker-compose exec web python manage.py createsuperuser
```
Siga as instruções para definir um nome de utilizador, e-mail e senha.

**a. Acessar às Páginas Web (Tarefa 3):**
* Aceda a **http://localhost:8000/**
* Faça login com as credenciais que acabou de criar.
* Você será redirecionado para a lista de estados e poderá navegar por todas as páginas da aplicação.

**b. Acessar ao Django Admin:**
* Aceda a **http://localhost:8000/admin/**
* Use as mesmas credenciais para ver a área de gestão de dados.