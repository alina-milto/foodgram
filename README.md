# Foodgram — продуктовый помощник

Сайт для публикации рецептов. Пользователи могут создавать рецепты, подписываться на авторов, добавлять рецепты в избранное и формировать список покупок.

## Технологии

- Python 3.10
- Django 5.2
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- GitHub Actions

## Запуск проекта

1. Клонируйте репозиторий:

```bash
git clone https://github.com/azulqilin/foodgram.git
```

2. Создайте файл `.env` в папке `infra/`:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your-secret-key
```

3. Запустите контейнеры:

```bash
cd infra
docker compose up -d
```

4. Создайте суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

5. Загрузите ингредиенты:

```bash
docker compose exec backend python manage.py load_ingredients
```

## Адрес сервера

http://158.160.228.134

## Автор

Alina Milto
