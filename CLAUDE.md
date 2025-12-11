# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Task Manager - REST API система управления задачами на Django + DRF с JWT аутентификацией.

## Commands

### Setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

### Development
```bash
python manage.py runserver
```

### Testing
```bash
python manage.py test
python manage.py test tasks.tests.test_api
python manage.py test tasks.tests.test_api.TaskAPITest.test_create_task
```

### Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py shell
```

## Architecture

### Project Structure
- `config/` - Django settings, main URLs
- `tasks/` - Core app with models (Task, Comment), serializers, views, permissions

### Authentication & Permissions
- JWT via `djangorestframework-simplejwt` (default for all endpoints)
- Custom permissions in `tasks/permissions.py`:
  - `IsCreatorOrAdmin` - only task creator or admin can edit/delete
  - `IsCreatorOrAssigneeOrAdmin` - creator, assignee or admin can mark complete
  - `IsAuthorOrAdmin` - only comment author or admin can delete

### API Design Pattern
- ViewSets with DRF Router for automatic URL generation
- Custom actions: `@action(detail=True, methods=['post'])` for `complete` and `assign`
- Nested comments under tasks: `/api/tasks/{id}/comments/`

### Models
**Task**: creator (FK), assignee (nullable FK), is_completed flag
**Comment**: task (FK), author (FK), no edit/update (immutable after creation)

Key relationships:
- creator: CASCADE (delete tasks when user deleted)
- assignee: SET_NULL (keep task when assignee deleted)
- task: CASCADE (delete comments when task deleted)

### Settings Configuration
- `REST_FRAMEWORK` uses JWT auth by default, `IsAuthenticated` permission
- `drf_spectacular` for OpenAPI schema generation
- Access tokens expire in 1 hour, refresh in 7 days

## API Documentation
After server starts, visit:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- Redoc: `http://localhost:8000/api/schema/redoc/`

## Code Style

- No unnecessary comments - code should be self-explanatory
- No emojis in code, comments, or commit messages
- Follow PEP 8 conventions
