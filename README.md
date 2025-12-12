# Task Manager API

REST API система управления задачами на Django REST Framework с JWT аутентификацией.

## Возможности

- CRUD операции для задач
- Назначение задач пользователям
- Отметка задач как выполненных
- Комментирование задач
- JWT аутентификация
- Swagger/Redoc документация

## Технологии

- Python 3.13
- Django 5.2
- Django REST Framework
- djangorestframework-simplejwt
- drf-spectacular
- SQLite

## Быстрый старт

### С Docker

```bash
docker compose up --build
```

Создание суперпользователя (когда контейнер запущен, в другом терминале):
```bash
docker compose exec web python manage.py createsuperuser
```

### Без Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API

Сервер: `http://localhost:8000`

### Основные endpoints

- `POST /api/auth/register/` - регистрация
- `POST /api/auth/token/` - получить JWT токен
- `GET /api/tasks/` - список задач
- `POST /api/tasks/` - создать задачу
- `PATCH /api/tasks/{id}/` - обновить задачу
- `POST /api/tasks/{id}/complete/` - отметить выполненной
- `POST /api/tasks/{id}/assign/` - назначить исполнителя
- `POST /api/comments/` - создать комментарий
- `GET /api/comments/?task={id}` - комментарии к задаче

### Документация

- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- Redoc: http://localhost:8000/api/schema/redoc/
- Admin: http://localhost:8000/admin/

## Тестирование

```bash
python manage.py test
```

Всего тестов: 41

## Права доступа

**Задачи:**
- Редактировать/удалить: только создатель или admin
- Отметить выполненной: создатель, исполнитель или admin
- Назначить исполнителя: создатель или admin

**Комментарии:**
- Удалить: только автор или admin
