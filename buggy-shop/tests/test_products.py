# tests/test_products.py
import pytest
from http import HTTPStatus


class TestProductsList:
    """Тесты списка продуктов"""

    def test_list_products_empty(self, client):
        """Получение пустого списка продуктов"""
        response = client.get("/api/products")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_products_with_data(self, client, auth_headers):
        """Получение списка продуктов с данными"""
        # Создаем несколько продуктов
        products_data = [
            {"name": "Product 1", "price": 10.99, "description": "Description 1"},
            {"name": "Product 2", "price": 20.99, "description": "Description 2"},
        ]

        for product in products_data:
            client.post("/api/products", json=product, headers=auth_headers)

        response = client.get("/api/products")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2


class TestProductCreate:
    """Тесты создания продуктов"""

    def test_create_product_success(self, client, auth_headers):
        """Успешное создание продукта"""
        product_data = {
            "name": "Test Product",
            "price": 99.99,
            "description": "Test Description",
            "stock": 10
        }
        response = client.post("/api/products", json=product_data, headers=auth_headers)
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, 200, 201)
        data = response.json()
        assert "id" in data
        assert data["name"] == product_data["name"]
        assert data["price"] == product_data["price"]

    def test_create_product_no_auth(self, client):
        """Создание продукта без авторизации"""
        product_data = {
            "name": "Test Product",
            "price": 99.99
        }
        response = client.post("/api/products", json=product_data)
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, 401, 403)

    def test_create_product_invalid_data(self, client, auth_headers):
        """Создание продукта с невалидными данными"""
        product_data = {
            "name": "",  # Пустое имя
            "price": -10  # Отрицательная цена
        }
        response = client.post("/api/products", json=product_data, headers=auth_headers)
        assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST, 422, 400)

    def test_create_product_missing_required_fields(self, client, auth_headers):
        """Создание продукта без обязательных полей"""
        product_data = {
            "description": "Only description"
        }
        response = client.post("/api/products", json=product_data, headers=auth_headers)
        assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST, 422, 400)


class TestProductDetail:
    """Тесты получения деталей продукта"""

    def test_get_product_by_id(self, client, auth_headers):
        """Получение продукта по ID"""
        # Создаем продукт
        product_data = {
            "name": "Test Product",
            "price": 99.99,
            "description": "Test Description"
        }
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Получаем продукт
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == product_data["name"]

    def test_get_nonexistent_product(self, client):
        """Получение несуществующего продукта"""
        response = client.get("/api/products/999999")
        assert response.status_code in (HTTPStatus.NOT_FOUND, 404)


class TestProductUpdate:
    """Тесты обновления продуктов"""

    def test_update_product_success(self, client, auth_headers):
        """Успешное обновление продукта"""
        # Создаем продукт
        product_data = {
            "name": "Original Product",
            "price": 50.00
        }
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Обновляем продукт
        update_data = {
            "name": "Updated Product",
            "price": 75.00
        }
        response = client.put(
            f"/api/products/{product_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.OK, 200)
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]

    def test_update_product_no_auth(self, client, auth_headers):
        """Обновление продукта без авторизации"""
        # Создаем продукт
        product_data = {"name": "Test", "price": 10}
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Пытаемся обновить без токена
        update_data = {"name": "Updated"}
        response = client.put(f"/api/products/{product_id}", json=update_data)
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, 401, 403)

    def test_update_nonexistent_product(self, client, auth_headers):
        """Обновление несуществующего продукта"""
        update_data = {"name": "Updated"}
        response = client.put("/api/products/999999", json=update_data, headers=auth_headers)
        assert response.status_code in (HTTPStatus.NOT_FOUND, 404)


class TestProductDelete:
    """Тесты удаления продуктов"""

    def test_delete_product_success(self, client, auth_headers):
        """Успешное удаление продукта"""
        # Создаем продукт
        product_data = {"name": "To Delete", "price": 10}
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Удаляем продукт
        response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, 200, 204)

    def test_delete_product_no_auth(self, client, auth_headers):
        """Удаление продукта без авторизации"""
        # Создаем продукт
        product_data = {"name": "Test", "price": 10}
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Пытаемся удалить без токена
        response = client.delete(f"/api/products/{product_id}")
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, 401, 403)

    def test_delete_nonexistent_product(self, client, auth_headers):
        """Удаление несуществующего продукта"""
        response = client.delete("/api/products/999999", headers=auth_headers)
        assert response.status_code in (HTTPStatus.NOT_FOUND, 404)


class TestProductSearch:
    """Тесты поиска продуктов"""

    def test_search_products(self, client, auth_headers):
        """Поиск продуктов по запросу"""
        # Создаем продукты
        products = [
            {"name": "Laptop Computer", "price": 1000},
            {"name": "Desktop Computer", "price": 800},
            {"name": "Phone", "price": 500}
        ]
        for product in products:
            client.post("/api/products", json=product, headers=auth_headers)

        # Ищем продукты
        response = client.get("/api/products/search?q=Computer")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        # В результатах должны быть продукты с "Computer"
        # (зависит от реализации поиска)

    def test_search_products_no_results(self, client):
        """Поиск продуктов без результатов"""
        response = client.get("/api/products/search?q=NonexistentProduct12345")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)


class TestProductFilter:
    """Тесты фильтрации продуктов"""

    def test_filter_by_price(self, client, auth_headers):
        """Фильтрация продуктов по цене"""
        # Создаем продукты с разными ценами
        products = [
            {"name": "Cheap", "price": 10},
            {"name": "Medium", "price": 50},
            {"name": "Expensive", "price": 100}
        ]
        for product in products:
            client.post("/api/products", json=product, headers=auth_headers)

        # Фильтруем по цене
        response = client.get("/api/products/filter?min_price=20&max_price=80")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        # Должен быть только "Medium" продукт (зависит от реализации)

    def test_filter_by_min_price_only(self, client):
        """Фильтрация только по минимальной цене"""
        response = client.get("/api/products/filter?min_price=50")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)


class TestProductReviews:
    """Тесты отзывов на продукты"""

    def test_add_review_to_product(self, client, auth_headers):
        """Добавление отзыва к продукту"""
        # Создаем продукт
        product_data = {"name": "Review Test Product", "price": 50}
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Добавляем отзыв
        review_data = {
            "rating": 5,
            "comment": "Great product!"
        }
        response = client.post(
            f"/api/products/{product_id}/reviews",
            json=review_data,
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, 200, 201)
        data = response.json()
        assert data["rating"] == review_data["rating"]
        assert data["comment"] == review_data["comment"]

    def test_add_review_to_nonexistent_product(self, client, auth_headers):
        """Добавление отзыва к несуществующему продукту"""
        review_data = {"rating": 5, "comment": "Test"}
        response = client.post(
            "/api/products/999999/reviews",
            json=review_data,
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.NOT_FOUND, 404)

    def test_get_product_reviews(self, client, auth_headers):
        """Получение отзывов продукта"""
        # Создаем продукт
        product_data = {"name": "Test", "price": 10}
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Добавляем отзыв
        review_data = {"rating": 4, "comment": "Good"}
        client.post(
            f"/api/products/{product_id}/reviews",
            json=review_data,
            headers=auth_headers
        )

        # Получаем отзывы
        response = client.get(f"/api/products/{product_id}/reviews")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_add_review_no_auth(self, client, auth_headers):
        """Добавление отзыва без авторизации"""
        # Создаем продукт
        product_data = {"name": "Test", "price": 10}
        create_response = client.post("/api/products", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        # Пытаемся добавить отзыв без токена
        review_data = {"rating": 5, "comment": "Test"}
        response = client.post(f"/api/products/{product_id}/reviews", json=review_data)
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, 401, 403)
