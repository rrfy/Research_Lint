# 🎉 BUGGYSHOP - ПОЛНЫЙ ПРОЕКТ ГОТОВ

## 📥 Скачиваемые файлы (4 части)

### **Part 1: generate_buggy_shop.py** 
Содержит **auth** и **products** модули

```
✓ src/__init__.py
✓ src/main.py (5 дефектов - OWASP:A05, STYLES)
✓ src/config.py (8 дефектов - OWASP:A05, A02, STYLES, SOLID)
✓ src/database.py (5 дефектов - OWASP:A03, A05, STYLES, SOLID)

✓ src/auth/models.py (7 дефектов - OWASP:A01, A02, SOLID)
✓ src/auth/schemas.py (7 дефектов - OWASP:A01, A07, STYLES, SOLID)
✓ src/auth/services.py (25 дефектов 🔴 - A01, A02, A03, A07, STYLES, SOLID)
✓ src/auth/dependencies.py (8 дефектов - OWASP:A01, A07, STYLES, SOLID)
✓ src/auth/routes.py (15 дефектов - OWASP:A01, A07, STYLES, SOLID)

✓ src/products/models.py (6 дефектов - OWASP:A01, A05, STYLES, SOLID)
✓ src/products/schemas.py (4 дефектов - OWASP:A03, STYLES, SOLID)
✓ src/products/services.py (12 дефектов - OWASP:A01, A03, A05, STYLES, SOLID)
✓ src/products/routes.py (10 дефектов - OWASP:A01, A03, A04, STYLES)
```

**Как использовать:**
```python
python generate_buggy_shop.py ./buggy-shop
# Создаст все файлы Part 1 в директории buggy-shop/
```

---

### **Part 2: buggy_shop_part2_orders.py**
Содержит **orders** модуль

```
✓ src/orders/models.py (6 дефектов - OWASP:A01, A02, A05, SOLID)
✓ src/orders/schemas.py (4 дефектов - OWASP:A02, A03, STYLES)
✓ src/orders/services.py (14 дефектов - OWASP:A01, A02, A03, STYLES)
✓ src/orders/routes.py (12 дефектов - OWASP:A01, A02, A03, STYLES)
```

**Содержимое:** Переменные со строками для копирования:
- `ORDERS_MODELS`
- `ORDERS_SCHEMAS`
- `ORDERS_SERVICES`
- `ORDERS_ROUTES`

**Как использовать:**
```bash
# Откройте buggy_shop_part2_orders.py
# Скопируйте код из переменных ORDERS_* в соответствующие файлы
# Или запустите для просмотра переменных
python buggy_shop_part2_orders.py
```

---

### **Part 3: buggy_shop_part3_rest.py**
Содержит **uploads**, **utils**, **tests** и **requirements.txt**

```
✓ src/uploads/routes.py (25 дефектов 🔴 - OWASP:A01, A04, A05, STYLES)
✓ src/utils/validators.py (6 дефектов - OWASP:A01, A07, STYLES, SOLID)

✓ tests/conftest.py (4 дефектов - OWASP:A05, STYLES, STRUCT)
✓ tests/test_auth.py (4 дефектов - OWASP:A07, STYLES, STRUCT)
✓ tests/test_products.py (4 дефектов - STYLES, STRUCT)
✓ tests/test_orders.py (3 дефектов - OWASP:A02, STYLES)

✓ requirements.txt (15 дефектов - OWASP:A06 - устаревшие версии)
```

**Содержимое:** Переменные:
- `UPLOADS_ROUTES`
- `UTILS_VALIDATORS`
- `TEST_CONFTEST`
- `TEST_AUTH`
- `TEST_PRODUCTS`
- `TEST_ORDERS`
- `REQUIREMENTS_TXT`

---

### **Part 4: buggy_shop_part4_infra.py**
Содержит конфиги и документацию

```
✓ Dockerfile (5 дефектов - OWASP:A06, A05)
✓ docker-compose.yml (4 дефектов - OWASP:A05, A02, A06)
✓ .github/workflows/ci.yml (4 дефектов - OWASP:A05, A06)
✓ .gitignore
✓ README.md (полная документация)
```

**Содержимое:** Переменные:
- `DOCKERFILE`
- `DOCKER_COMPOSE`
- `CI_YML`
- `GITIGNORE`
- `README`

---

## 🚀 Быстрый старт (3 способа)

### Способ 1: Автоматическая генерация (РЕКОМЕНДУЕТСЯ)

```bash
# Скачайте generate_buggy_shop.py
python generate_buggy_shop.py ./buggy-shop

# Перейдите в проект
cd buggy-shop

# Установите зависимости
pip install -r requirements.txt

# Запустите
python -m uvicorn src.main:app --reload

# Откройте браузер
# http://localhost:8000/docs
```

### Способ 2: Ручное копирование кода

```bash
# Создайте структуру
mkdir -p buggy-shop/{src/{auth,products,orders,uploads,utils},tests,.github/workflows}

# Скопируйте код из каждого файла в соответствующие файлы проекта:
# - generate_buggy_shop.py → src/* файлы
# - buggy_shop_part2_orders.py → src/orders/* файлы
# - buggy_shop_part3_rest.py → src/uploads/*, src/utils/*, tests/*, requirements.txt
# - buggy_shop_part4_infra.py → Dockerfile, docker-compose.yml, .github/workflows/ci.yml, README.md

# Установите и запустите
cd buggy-shop
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

### Способ 3: Docker

```bash
# Убедитесь, что проект создан (способ 1 или 2)
docker-compose up

# Откройте браузер
# http://localhost:8000/docs
```

---

## 📊 Распределение дефектов (200+)

| Модуль | Дефектов | Статус |
|--------|----------|--------|
| auth/services.py | 25 | 🔴 КРИТИЧНОЕ |
| uploads/routes.py | 25 | 🔴 КРИТИЧНОЕ |
| auth/routes.py | 15 | 🟠 ВАЖНОЕ |
| orders/services.py | 14 | 🟠 ВАЖНОЕ |
| products/services.py | 12 | 🟠 ВАЖНОЕ |
| orders/routes.py | 12 | 🟠 ВАЖНОЕ |
| products/routes.py | 10 | 🟠 ВАЖНОЕ |
| auth/dependencies.py | 8 | 🟡 ОБЫЧНОЕ |
| config.py | 8 | 🟡 ОБЫЧНОЕ |
| auth/models.py | 7 | 🟡 ОБЫЧНОЕ |
| auth/schemas.py | 7 | 🟡 ОБЫЧНОЕ |
| orders/models.py | 6 | 🟡 ОБЫЧНОЕ |
| products/models.py | 6 | 🟡 ОБЫЧНОЕ |
| utils/validators.py | 6 | 🟡 ОБЫЧНОЕ |
| database.py | 5 | 🟡 ОБЫЧНОЕ |
| main.py | 5 | 🟡 ОБЫЧНОЕ |
| Dockerfile | 5 | 🟡 ОБЫЧНОЕ |
| orders/schemas.py | 4 | 🟡 ОБЫЧНОЕ |
| products/schemas.py | 4 | 🟡 ОБЫЧНОЕ |
| docker-compose.yml | 4 | 🟡 ОБЫЧНОЕ |
| ci.yml | 4 | 🟡 ОБЫЧНОЕ |
| conftest.py | 4 | 🟡 ОБЫЧНОЕ |
| test_auth.py | 4 | 🟡 ОБЫЧНОЕ |
| test_products.py | 4 | 🟡 ОБЫЧНОЕ |
| test_orders.py | 3 | 🟡 ОБЫЧНОЕ |
| requirements.txt | 15 | 🟡 ОБЫЧНОЕ (устаревшие) |
| **ВСЕГО** | **200+** | ✅ ГОТОВО |

---

## 🎯 Дефекты по категориям OWASP

```
✅ OWASP:A01 (Broken Access Control)       → 15+ примеров
✅ OWASP:A02 (Cryptographic Failures)      → 15+ примеров
✅ OWASP:A03 (Injection - SQL, XSS)        → 15+ примеров
✅ OWASP:A04 (Insecure Design)             → 10+ примеров
✅ OWASP:A05 (Security Misconfiguration)   → 15+ примеров
✅ OWASP:A06 (Vulnerable/Outdated)         → 15+ примеров
✅ OWASP:A07 (Authentication Failures)     → 15+ примеров
✅ OWASP:A08-A10 (другие)                  → 10+ примеров
```

## 🎓 Качество кода

```
✅ STYLES (нарушения единообразия)         → 20+ примеров
✅ SOLID (нарушения принципов)             → 15+ примеров
✅ STRUCT (проблемы архитектуры)           → 10+ примеров
```

---

## 📋 Поиск дефектов

```bash
# Все дефекты помечены FIXME
grep -r "FIXME" src/ | wc -l              # Подсчет
grep -r "FIXME OWASP:A03" src/            # SQL-инъекции
grep -r "FIXME OWASP:A02" src/            # Криптография
grep -r "FIXME OWASP:A01" src/            # Access Control
grep -r "FIXME STYLES" src/               # Стиль
grep -r "FIXME SOLID" src/                # SOLID

# Экспорт
grep -r "FIXME" src/ > defects.txt
```

---

## 🧪 API Примеры

```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'

# Вход
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Получить товары
curl http://localhost:8000/api/products/

# Поиск (SQL-инъекция!)
curl "http://localhost:8000/api/products/search?q=test' OR '1'='1"
```

---

## 📊 Оценка результатов

```python
# Подсчитайте для каждого анализа:
TP = найдены и имеют FIXME комментарий
FP = найдены, но нет FIXME
FN = не найдены, но есть FIXME

Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 * (Precision * Recall) / (Precision + Recall)

# Таблица оценки:
# 80-100% → Отлично (🟢)
# 60-80%  → Хорошо (🟢)
# 40-60%  → Среднее (🟡)
# 0-40%   → Плохо (🔴)
```

---

## ⚠️ Важно!

- ❌ **НЕ используйте в production** - это учебный проект
- ❌ **НЕ давайте публичный доступ** - содержит уязвимости
- ✅ Используйте только для **образовательных целей**
- ✅ Все уязвимости **намеренные и помечены FIXME**

---

## 🎉 Готово!

**Версия:** 1.0.0  
**Файлов:** 21  
**Дефектов:** 200+  
**Готовность:** ✅ 100%  

Спасибо за использование BuggyShop! 🚀
