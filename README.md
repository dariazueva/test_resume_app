# test_resume_app
Resume App

## Описание

Простое приложение для управления резюме с возможностью улучшения через AI.

## Требования

- Python 3.12
- PostgreSQL
- FastAPI
- SQLAlchemy
- Alembic
- Docker
- uvicorn
- JWT

### Основной функционал
- Регистрация и авторизация
- Аутентификация (JWT)
- CRUD операции с резюме
- Улучшение резюме через AI (заглушка)
- Хранение истории улучшений резюме

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:dariazueva/test_resume_app.git
```
```
cd app
```
Cоздать и активировать виртуальное окружение:
```
python -m venv env
```
* Если у вас Linux/macOS
    ```
    source env/bin/activate
    ```
* Если у вас windows
    ```
    source env/Scripts/activate
    ```
```
python -m pip install --upgrade pip
```
Создайте файл .env и заполните его своими данными по образцу:
```
ENGINE_URL=postgresql+asyncpg://resumeapp_user:mysecretpassword@localhost:5432/resumeapp
SECRET_KEY=your_secret_key
ALGORITHM=HS256
```
#### Запустите через докер:
```bash
docker-compose up -d --build
```
Приложение доступно: http://localhost:8000
#### Выполните миграции:
```bash
docker-compose exec web alembic upgrade head
```
#### API Документация:
Swagger - http://localhost:8000/docs
Redoc - http://localhost:8000/redoc

#### API Endpoints
* POST /auth/register - Регистрация нового пользователя
* POST /auth/token - Получение JWT токенов
* GET /auth/me - Получение данных текущего пользователя
* GET /auth/check_token - Проверка валидности токена
* PATCH /auth/users/{user_id} - Изменение данных пользователя
* GET /auth/users/{user_id} - Получение данных о конкретном пользователе
* DELETE /auth/users/{user_id} - Деактивация пользователя (мягкое удаление)
* GET /auth/users - Получение списка активных пользователей

* GET /resumes/ - Получение списка резюме
* POST /resumes/ - Создание резюме
* GET /resumes/{resume_id} - Получение данных о конкретном резюме
* PUT /resumes/{resume_id} - Обновление конкретного резюме
* DELETE /resumes/{resume_id} - Удаление резюме

* POST /ai/resume/{resume_id}/improve - Улучшение резюме с помощью AI
* GET /ai/resume/{resume_id}/improvements - Получение истории улучшений для резюме


## Автор
Зуева Дарья Дмитриевна
Github https://github.com/dariazueva/