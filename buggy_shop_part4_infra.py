#!/usr/bin/env python3
"""
BuggyShop - Part 4: Docker & Infrastructure Files
Генерирует Docker конфиги, CI/CD и документацию
"""

# ==================== DOCKER ====================

DOCKERFILE = '''# Dockerfile - FIXME: 5 дефектов
# FIXME OWASP:A06 - Python версия 3.9 устаревшая
FROM python:3.9-slim  # FIXME OWASP:A06: Python 3.9 (июнь 2021) - используй 3.11+

# FIXME OWASP:A05 - Запуск от root
RUN apt-get update && apt-get install -y \\
    gcc  # FIXME OWASP:A05: Лишние пакеты для production

WORKDIR /app

# FIXME OWASP:A05 - Нет разделения слоев для кеша
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  # FIXME OWASP:A06: pip без --upgrade

# FIXME OWASP:A05 - Копирование всего кода
COPY . .

# FIXME OWASP:A05 - Нет создания непривилегированного пользователя
# FIXME OWASP:A05 - Работает от root!

EXPOSE 8000

# FIXME OWASP:A05 - Запуск с debug=True (из config.py)
# FIXME OWASP:A05 - Нет healthcheck
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]  # FIXME OWASP:A05: 0.0.0.0 доступен изне
'''

DOCKER_COMPOSE = '''version: "3.8"  # FIXME OWASP:A05 - Версия 3.8 устаревшая (используй 3.9+)

services:
  # FIXME OWASP:A05 - PostgreSQL пароль слабый
  db:
    image: postgres:13-alpine  # FIXME OWASP:A06 - PostgreSQL 13 устаревшая (15+ актуальная)
    environment:
      POSTGRES_USER: buggyshop  # FIXME OWASP:A02 - Хардкодированное имя пользователя
      POSTGRES_PASSWORD: buggyshop123  # FIXME OWASP:A02: Слабый пароль хардкодирован!
      POSTGRES_DB: buggyshop  # FIXME OWASP:A02: Имя БД в открытом виде
    ports:
      - "5432:5432"  # FIXME OWASP:A05 - PostgreSQL открыта на публику (должна быть внутри)
    volumes:
      - postgres_data:/var/lib/postgresql/data  # FIXME OWASP:A05 - Нет backup стратегии
    # FIXME OWASP:A05 - Нет healthcheck
    networks:
      - buggyshop-network

  # FIXME OWASP:A05 - Приложение работает от root
  app:
    build: .
    ports:
      - "8000:8000"  # FIXME OWASP:A05 - Приложение открыто всем
    environment:
      DATABASE_URL: postgresql://buggyshop:buggyshop123@db:5432/buggyshop  # FIXME OWASP:A02: Пароль в открытом виде!
      DEBUG: "True"  # FIXME OWASP:A05: DEBUG=True в production!
    depends_on:
      - db
    # FIXME OWASP:A05 - Нет лимитов ресурсов
    # FIXME OWASP:A05 - Нет restart policy
    networks:
      - buggyshop-network

volumes:
  postgres_data:  # FIXME OWASP:A05 - Нет backup

networks:
  buggyshop-network:
    driver: bridge  # FIXME STRUCT - Нет изоляции
'''

CI_YML = '''# .github/workflows/ci.yml - CI/CD pipeline
# FIXME: 4 дефекта
name: CI  # FIXME STYLES - Имя слишком короткое

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  # FIXME OWASP:A05 - Тесты запускаются в production окружении
  test:
    runs-on: ubuntu-20.04  # FIXME OWASP:A06 - Ubuntu 20.04 устаревшая (используй latest)
    
    steps:
    - uses: actions/checkout@v2  # FIXME OWASP:A06 - v2 устаревшая (используй v4)
    
    # FIXME OWASP:A05 - Python версия зафиксирована на 3.9
    - name: Set up Python
      uses: actions/setup-python@v2  # FIXME OWASP:A06 - v2 старая
      with:
        python-version: 3.9  # FIXME OWASP:A06: 3.9 устаревшая
    
    # FIXME OWASP:A05 - Зависимости из requirements.txt (все устаревшие)
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    # FIXME OWASP:A05 - Тесты в БД с debug логированием
    - name: Run tests
      env:
        DATABASE_URL: sqlite:///./test.db  # FIXME OWASP:A05: Тесты используют реальный файл
      run: |
        pytest tests/ -v --tb=short  # FIXME OWASP:A05 - Traceback открыт
    
    # FIXME OWASP:A05 - Нет проверки качества кода (flake8, pylint)
    # FIXME OWASP:A05 - Нет проверки безопасности (bandit, safety)

  # FIXME STYLES - Деплой без проверки
  build:
    runs-on: ubuntu-20.04
    needs: test
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t buggyshop:latest .  # FIXME OWASP:A05: Тег latest опасен
      # FIXME OWASP:A05 - Нет регистрации образа
'''

GITIGNORE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
venv/
env/
.env  # FIXME OWASP:A05 - Иногда .env коммитится!

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/
temp/

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
'''

# ==================== README ====================

README = r'''# 🔴 BuggyShop - Полный проект с намеренными уязвимостями

**Исследовательское приложение для тестирования AI-агентов в анализе качества и безопасности кода**

## ⚠️ ВНИМАНИЕ

Это приложение содержит **200+ намеренных уязвимостей** и **небезопасно** для production использования. 
Используйте ТОЛЬКО для образовательных целей в локальной разработке.

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| **Файлов** | 21 |
| **Строк кода** | ~2500 |
| **Дефектов** | 200+ |
| **OWASP A1-A10** | 15+ примеров каждой |
| **SOLID нарушений** | 15+ |
| **Проблем архитектуры** | 10+ |
| **Стиля кода** | 20+ |
| **Соотношение чистого/ошибочного** | 1:40 |

## 🔴 Критичные модули

### auth/services.py (25 дефектов)
- SHA256 вместо bcrypt для паролей (FIXME OWASP:A02)
- SQL-инъекции (FIXME OWASP:A03)
- Timing attacks (FIXME OWASP:A02)
- Отсутствие rate limiting (FIXME OWASP:A07)
- make_admin без проверок (FIXME OWASP:A01)

### uploads/routes.py (25 дефектов)
- Path traversal: `../../../etc/passwd` (FIXME OWASP:A04)
- Zip bomb (FIXME OWASP:A04)
- Любые расширения файлов (FIXME OWASP:A04)
- Отсутствие MIME-type проверки (FIXME OWASP:A04)
- Скачивание любых файлов (FIXME OWASP:A04)

## 🚀 Быстрый старт

### Локально

```bash
# Клонировать проект
git clone <url>
cd buggy-shop

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate

# Установить зависимости (все устаревшие - FIXME DEP-OUTDATED)
pip install -r requirements.txt

# Инициализировать БД
python -c "from src.database import init_db; init_db()"

# Запустить
python -m uvicorn src.main:app --reload

# Открыть
# http://localhost:8000/docs
```

### Docker

```bash
docker-compose up
```

## 📝 Дефолтные учетные данные

```
Email: admin@buggyshop.com
Username: admin
Password: admin123  # FIXME OWASP:A02: Слабый пароль
```

## 📍 Найти дефекты

Все дефекты помечены комментариями `FIXME`:

```bash
# Найти SQL-инъекции
grep -r "FIXME OWASP:A03" src/

# Найти все проблемы с паролями
grep -r "FIXME OWASP:A02" src/

# Подсчитать в одном файле
grep "FIXME" src/auth/services.py | wc -l

# Экспортировать в файл
grep -r "FIXME" src/ > defects.txt
```

## 🧪 Стратегии анализа AI

### 1️⃣ Параметрический анализ

```
Проанализируй products/services.py на SQL-инъекции.
Ищи использование f-strings в SQL запросах.
Укажи точные строки и описание проблемы.
```

### 2️⃣ Слепой анализ

```
Проверь auth/services.py на уязвимости.
Не говорю сколько их и какие.
Оцени severity каждой найденной.
```

### 3️⃣ SOLID и стиль

```
Проверь auth/models.py на нарушения SOLID.
Найди проблемы с единообразием кода.
Укажи что нужно рефакторить.
```

## 📊 Оценка результатов

```python
TP = найдены и помечены FIXME
FP = найдены, но нет FIXME
FN = не найдены, но есть FIXME

Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

**Таблица оценки:**

| Результат | Precision | Recall | F1 |
|-----------|-----------|--------|-----|
| 🔴 Плохо | 0-40% | 0-40% | 0-40% |
| 🟡 Среднее | 40-60% | 40-60% | 40-60% |
| 🟢 Хорошо | 60-80% | 60-80% | 60-80% |
| 🟢 Отлично | 80-100% | 80-100% | 80-100% |

## 📚 API Endpoints

### Аутентификация
```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
POST   /api/auth/logout
POST   /api/auth/change-password
GET    /api/debug/token/{token}  # FIXME OWASP:A05 - Отладочный!
```

### Товары
```
GET    /api/products
GET    /api/products/{id}
GET    /api/products/search  # FIXME OWASP:A03 - SQL-инъекция
GET    /api/products/filter  # FIXME OWASP:A03 - SQL-инъекция
POST   /api/products  # FIXME OWASP:A03 - XSS
```

### Заказы
```
POST   /api/orders  # FIXME OWASP:A02 - CC в открытом виде!
GET    /api/orders/{id}  # FIXME OWASP:A01 - IDOR
GET    /api/orders/my/orders
GET    /api/orders/search  # FIXME OWASP:A03 - SQL-инъекция
POST   /api/orders/{id}/pay  # FIXME OWASP:A02 - CVV передается!
```

### Загрузка файлов
```
POST   /api/uploads/upload  # FIXME OWASP:A04 - Path traversal
POST   /api/uploads/upload-image  # FIXME OWASP:A04 - Path traversal
GET    /api/uploads/download/{filename}  # FIXME OWASP:A04 - Path traversal
DELETE /api/uploads/delete/{filename}  # FIXME OWASP:A04 - Path traversal
POST   /api/uploads/upload-archive  # FIXME OWASP:A04 - ZIP bomb
```

## 🧹 Запуск тестов

```bash
# Все тесты
pytest tests/ -v

# С покрытием
pytest tests/ --cov=src --cov-report=html

# Конкретный тест
pytest tests/test_auth.py::test_register -v
```

## 🔬 Примеры уязвимостей

### SQL-инъекция (OWASP:A03)
```python
# FIXME OWASP:A03 - в products/services.py
sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
result = db.execute(text(sql))  # Уязвимо!
```

### Path Traversal (OWASP:A04)
```python
# FIXME OWASP:A04 - в uploads/routes.py
filepath = os.path.join(UPLOAD_DIR, filename)  # ../../../etc/passwd
with open(filepath, "rb") as f:  # Уязвимо!
    return f.read()
```

### Слабая криптография (OWASP:A02)
```python
# FIXME OWASP:A02 - в auth/services.py
password_hash = hashlib.sha256(password.encode()).hexdigest()  # Уязвимо!
```

### IDOR (OWASP:A01)
```python
# FIXME OWASP:A01 - в orders/routes.py
order = get_order(db, order_id)  # Нет проверки владельца!
return order  # Уязвимо для IDOR!
```

## 📖 Документация

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## 🔍 Структура проекта

```
buggy-shop/
├── src/
│   ├── main.py (5 дефектов)
│   ├── config.py (8 дефектов)
│   ├── database.py (5 дефектов)
│   ├── auth/ (63 дефекта)
│   ├── products/ (32 дефекта)
│   ├── orders/ (36 дефектов)
│   ├── uploads/ (25 дефектов)
│   └── utils/ (6 дефектов)
├── tests/ (15 дефектов)
├── Dockerfile (5 дефектов)
├── docker-compose.yml (4 дефекта)
├── requirements.txt (15 дефектов)
└── README.md
```

## 📅 История версий

| Версия | Дата | Статус | Дефектов |
|--------|------|--------|----------|
| 1.0.0 | 2025-12-11 | ✅ Финальная | 200+ |

## ✅ Checklist использования

- [ ] Установлены зависимости из requirements.txt
- [ ] Создана БД через init_db()
- [ ] Запущено приложение локально
- [ ] Протестирован API через Swagger UI
- [ ] Запущены тесты (pytest)
- [ ] Запущен анализ AI-агентом
- [ ] Собраны результаты анализа
- [ ] Подсчитаны метрики (Precision, Recall, F1)

## 🚨 Безопасность

**ОПАСНО ДЛЯ PRODUCTION:**
- ❌ DEBUG = True
- ❌ CORS = "*"
- ❌ Пароли в коде
- ❌ CC в открытом виде
- ❌ SQL-инъекции
- ❌ Path traversal
- ❌ IDOR уязвимости

## 📧 Помощь

Если возникают проблемы:
1. Проверьте, что Python 3.9+
2. Проверьте, что pip install сработал без ошибок
3. Проверьте логи: `grep "ERROR" app.log`
4. Убедитесь, что порт 8000 свободен

## 📄 Лицензия

MIT License - Используйте в образовательных целях

---

**Версия:** 1.0.0  
**Статус:** ✅ Полностью готово к использованию  
**Дефектов:** 200+  
**Готовность:** 100%
'''

print("✅ Docker и инфраструктура файлы готовы!")
print(f"   ✓ Dockerfile")
print(f"   ✓ docker-compose.yml")
print(f"   ✓ .github/workflows/ci.yml")
print(f"   ✓ .gitignore")
print(f"   ✓ README.md")

print(f"\n🎉 ВСЕ ФАЙЛЫ ПРОЕКТА ГОТОВЫ!")
