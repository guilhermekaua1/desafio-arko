# Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Definir variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo de dependências e instalá-las
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar todo o código do projeto para o diretório de trabalho
COPY . .