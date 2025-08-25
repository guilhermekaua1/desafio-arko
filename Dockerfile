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

ENV PORT=8000

RUN python manage.py collectstatic --noinput


CMD gunicorn core.wsgi:application --bind 0.0.0.0:$PORT