# Foodgram

[![CI](https://github.com/alina-milto/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/alina-milto/foodgram/actions/workflows/main.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-5.2-green)

REST API for a recipe sharing service: users publish recipes, follow
authors, save favorites and download a shopping list with ingredients
summed up across recipes.

I built the backend: API, database, permissions, tests, Docker and CI.
The React frontend was provided by the
[Yandex Practicum](https://practicum.yandex.ru/) course.

**Stack:** Python, Django, Django REST Framework, PostgreSQL, Docker,
Nginx, GitHub Actions, pytest

## Highlights

- Recipe list loads in **6 database queries instead of 44** thanks to
  `prefetch_related` and `Exists` annotations
- **44 API tests** running on PostgreSQL in CI on every pull request
- Input validation and atomic saving of recipes with their ingredients
- Token authentication, author-only editing, filtering and pagination

## Quick start

```bash
git clone https://github.com/alina-milto/foodgram.git
cd foodgram/infra
cp .env.example .env    # set your own SECRET_KEY and POSTGRES_PASSWORD
docker compose up -d --build
docker compose exec backend python manage.py load_ingredients
docker compose exec backend python manage.py createsuperuser
```

Open http://localhost:8000 for the website, `/admin/` for the admin
and `/api/docs/` for the API documentation. Create a few tags in the
admin before adding recipes.

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## Notes

During the course the project ran on a cloud server with HTTPS and
automatic deployment from GitHub Actions. The server is no longer
running, so the repository is set up for local launch. The frontend
and the ingredient list are in Russian, as provided by the course.

## Author

**Alina Milto** — [GitHub](https://github.com/alina-milto)
