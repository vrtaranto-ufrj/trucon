# trucon
Truco Online

# Para rodar o projeto
1. Crie o arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```env
DJANGO_SECRET_KEY=django-secret-key
DB_PASSWORD=db-password
DB_NAME=db-name
DB_USER=db-user
DB_HOST=db-host
DJANGO_DEBUG=True/False
```

## Dev
1. Coloque como `DJANGO_DEBUG=True` no `.env`

2. Inicie o docker-compose com o perfil de desenvolvimento:
```bash
docker-compose --profile dev up --build
```

## Prod
1. Coloque como `DJANGO_DEBUG=False` no `.env`

2. Inicie o docker-compose com o perfil de produção:
```bash
docker-compose --profile prod up --build
```

### Caso seja a primeira vez rodando, execute as migrações:
```bash
docker-compose exec web python manage.py migrate
```

### A porta padrão do projeto é a 8000, acesse `http://localhost:8000` para ver o projeto rodando.
