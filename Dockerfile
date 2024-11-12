FROM python:latest

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apache2-dev \
        build-essential \
        default-libmysqlclient-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instale o mod_wsgi via pip
RUN pip install --no-cache-dir mod_wsgi

# Copie os arquivos de requisitos
COPY ./requirements.txt /app/requirements.txt

# Instale as dependências
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copie o código do projeto
COPY ./django-truco /app

# Defina o diretório de trabalho
WORKDIR /app

# Exponha a porta 8000
EXPOSE 8000

# Defina a variável de ambiente DJANGO_DEBUG
ENV DJANGO_DEBUG=${DJANGO_DEBUG}

# Copiar o script wait-for-it.sh
COPY ./configs/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Comando padrão para alternar entre desenvolvimento e produção
CMD bash -c "\
    if [ \"$DJANGO_DEBUG\" = 'True' ]; then \
        /wait-for-it.sh db:3306 --timeout=60 --strict -- python manage.py runserver 0.0.0.0:8000; \
    else \
        python manage.py collectstatic --noinput && \
        /wait-for-it.sh db:3306 --timeout=60 --strict -- mod_wsgi-express start-server trucosite/wsgi.py --port 8000 --url-alias /static /app/static; \
    fi"