Office Management System
Django REST API система для управления офисом, сотрудниками и рабочими местами с автоматической документацией Swagger.

 Архитектура проекта
text
office_managment/
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile                  # Docker образ приложения
├── requirements.txt            # Зависимости Python
├── start.bat                  # Скрипт запуска для Windows
└── src/                       # Исходный код приложения
    ├── manage.py
    ├── core/                  # Общие модули
    │   ├── database.py
    │   └── dependencies.py
    ├── employee/              # Приложение сотрудников
    │   ├── models.py          # Модели: Employee, Desk, Skill и др.
    │   ├── api_views.py       # DRF ViewSets для API
    │   ├── views.py           # Django Views для HTML
    │   ├── serializers.py     # Сериализаторы DRF
    │   ├── urls.py            # Маршруты приложения
    │   ├── filters.py         # Фильтры для API
    │   ├── permissions.py     # Кастомные permissions
    │   └── migrations/        # Миграции базы данных
    ├── office/                # Настройки проекта
    │   ├── settings.py        # Основные настройки Django
    │   ├── urls.py            # Корневые маршруты
    │   ├── wsgi.py
    │   └── asgi.py
    ├── workplace/             # Приложение рабочих мест
    │   ├── models.py
    │   ├── views.py
    │   └── migrations/
    ├── static/                # Статические файлы
    ├── media/                 # Медиа файлы
    └── templates/             # HTML шаблоны
        ├── base.html
        ├── employees/
        └── includes/
 Функциональность
 Основные возможности
Управление сотрудниками - CRUD операции, навыки, фотографии

Рабочие места - управление столами, бронирование

Навыки сотрудников - система уровней владения навыками

REST API - полный API с документацией Swagger

JWT аутентификация - безопасный доступ к API

Админ-панель - визуальное управление данными

 Бизнес-логика
Валидация расположения сотрудников (разработчики ≠ тестировщики)

Система бронирования рабочих мест

Расчет стажа работы

Управление медиа-контентом

Технологический стек
Backend
Django 4.2 - основной фреймворк

Django REST Framework - REST API

DRF Spectacular - Swagger документация

PostgreSQL - база данных

JWT - аутентификация

Django Filter - фильтрация данных

Инфраструктура
Docker - контейнеризация

Docker Compose - оркестрация

Gunicorn - WSGI сервер (для продакшена)

WhiteNoise - статические файлы

 Быстрый старт
Предварительные требования
Docker

Docker Compose

Запуск в Docker
bash
# Клонирование репозитория
git clone <repository-url>
cd office_managment

# Запуск проекта
docker-compose up --build

# Или используй скрипт для Windows
start.bat
Доступ к приложению
После запуска открой в браузере:

 Главная страница: http://localhost:8000/

 API документация: http://localhost:8000/api/docs/

 Альтернативная документация: http://localhost:8000/api/redoc/

 Админ-панель: http://localhost:8000/admin/

 Сотрудники: http://localhost:8000/employees/

Создание суперпользователя
bash
docker-compose exec web python manage.py createsuperuser
 Модели данных
Основные модели
Employee - сотрудники с должностями, столами, навыками

Desk - рабочие столы с координатами и доступностью

Skill - профессиональные навыки

EmployeeSkill - связь сотрудников с навыками (уровни)

EmployeeImage - фотографии сотрудников

Reservation - бронирование рабочих мест

Примеры API endpoints
text
GET    /employees/api/employees/          # Список сотрудников
POST   /employees/api/employees/          # Создание сотрудника
GET    /employees/api/employees/{id}/     # Детали сотрудника
PUT    /employees/api/employees/{id}/     # Обновление сотрудника
DELETE /employees/api/employees/{id}/     # Удаление сотрудника

GET    /employees/api/desks/              # Список столов
GET    /employees/api/skills/             # Список навыков
POST   /employees/api/reservations/       # Бронирование стола
 Настройки окружения
Создай файл .env в корне проекта:

env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://office_user:office_pass@db:5432/office_db
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_SETTINGS_MODULE=office.settings
 Команды разработки
Работа с миграциями

# Создание миграций
docker-compose exec web python manage.py makemigrations

# Применение миграций
docker-compose exec web python manage.py migrate

# Откат миграций
docker-compose exec web python manage.py migrate app_name zero
Администрирование

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сбор статических файлов
docker-compose exec web python manage.py collectstatic

# Проверка системы
docker-compose exec web python manage.py check
Тестирование
bash
# Запуск тестов
docker-compose exec web python manage.py test

# Остановка контейнеров
docker-compose down

# Запуск контейнеров
docker-compose up -d

# Остановка с удалением volumes
docker-compose down -v

# Перезапуск сервиса
docker-compose restart web

# Выполнение команд в контейнере
docker-compose exec web python manage.py shell

API Документация
Аутентификация
Система использует JWT аутентификацию:


# Получение токена
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
Использование API

# Запрос с токеном
curl -H "Authorization: Bearer your_jwt_token" \
     http://localhost:8000/employees/api/employees/
# Просмотр логов приложения
docker-compose logs web

# Просмотр логов базы данных
docker-compose logs db

# Подробные логи
docker-compose logs --tail=100 -f web



Тестируй API через Swagger
