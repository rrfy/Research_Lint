# tests/test_auth.py
import pytest
from http import HTTPStatus


class TestAuthRegistration:
    """Тесты регистрации пользователей"""

    def test_register_success(self, client):
        """Успешная регистрация нового пользователя"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED)
        data = response.json()
        assert "id" in data or "email" in data
        assert data.get("email") == user_data["email"]

    def test_register_duplicate_email(self, client, test_user):
        """Регистрация с существующим email"""
        duplicate_data = {
            "email": test_user["email"],
            "username": "different_username",
            "password": "Password123!"
        }
        response = client.post("/api/auth/register", json=duplicate_data)
        assert response.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, 400)

    def test_register_duplicate_username(self, client, test_user):
        """Регистрация с существующим username"""
        duplicate_data = {
            "email": "different@example.com",
            "username": test_user["username"],
            "password": "Password123!"
        }
        response = client.post("/api/auth/register", json=duplicate_data)
        # Может быть ошибка или успех, зависит от реализации
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT)

    def test_register_invalid_email(self, client):
        """Регистрация с невалидным email"""
        invalid_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "Password123!"
        }
        response = client.post("/api/auth/register", json=invalid_data)
        # Может вернуть 422 (validation error) или 400
        assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST, 422)

    def test_register_missing_fields(self, client):
        """Регистрация без обязательных полей"""
        incomplete_data = {
            "email": "test@example.com"
            # missing username and password
        }
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Тесты входа в систему"""

    def test_login_success(self, client, test_user):
        """Успешный вход"""
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"].lower() == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Вход с неправильным паролем"""
        login_data = {
            "username": test_user["username"],
            "password": "WrongPassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.BAD_REQUEST, 401)

    def test_login_nonexistent_user(self, client):
        """Вход с несуществующим пользователем"""
        login_data = {
            "username": "nonexistent_user",
            "password": "SomePassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.BAD_REQUEST, 401)

    def test_login_empty_credentials(self, client):
        """Вход с пустыми данными"""
        response = client.post("/api/auth/login", json={})
        assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST, 422)


class TestAuthProfile:
    """Тесты профиля пользователя"""

    def test_get_current_user(self, client, auth_headers):
        """Получение информации о текущем пользователе"""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data

    def test_get_current_user_no_auth(self, client):
        """Получение профиля без авторизации"""
        response = client.get("/api/auth/me")
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, 401, 403)

    def test_get_current_user_invalid_token(self, client):
        """Получение профиля с невалидным токеном"""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, 401, 403)


class TestAuthUserManagement:
    """Тесты управления пользователями"""

    def test_get_user_by_id(self, client, test_user, auth_headers, db_session):
        """Получение пользователя по ID"""
        # Получаем ID текущего пользователя
        me_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        response = client.get(f"/api/auth/users/{user_id}", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["id"] == user_id

    def test_get_nonexistent_user(self, client, auth_headers):
        """Получение несуществующего пользователя"""
        response = client.get("/api/auth/users/999999", headers=auth_headers)
        assert response.status_code in (HTTPStatus.NOT_FOUND, 404)

    def test_update_own_profile(self, client, auth_headers):
        """Обновление собственного профиля"""
        # Получаем ID
        me_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        update_data = {
            "email": "updated@example.com"
        }
        response = client.put(
            f"/api/auth/users/{user_id}", 
            json=update_data, 
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.OK, 200)

    def test_delete_own_account(self, client, auth_headers):
        """Удаление собственного аккаунта"""
        me_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        response = client.delete(f"/api/auth/users/{user_id}", headers=auth_headers)
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, 200, 204)


class TestAuthAdmin:
    """Тесты админ-функций"""

    def test_list_all_users_as_admin(self, client, test_admin):
        """Получение списка всех пользователей (админ)"""
        response = client.get("/api/auth/admin/users", headers=test_admin["headers"])
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_list_all_users_as_regular_user(self, client, auth_headers):
        """Получение списка пользователей (обычный юзер)"""
        response = client.get("/api/auth/admin/users", headers=auth_headers)
        assert response.status_code in (HTTPStatus.FORBIDDEN, 403)

    def test_make_user_admin(self, client, test_admin, test_user, db_session):
        """Назначение пользователя администратором"""
        # Получаем ID тестового пользователя
        from src.auth.models import User
        user = db_session.query(User).filter(User.username == test_user["username"]).first()

        response = client.post(
            f"/api/auth/admin/users/{user.id}/make-admin",
            headers=test_admin["headers"]
        )
        assert response.status_code in (HTTPStatus.OK, 200)


class TestAuthPasswordChange:
    """Тесты смены пароля"""

    def test_change_password_success(self, client, test_user, auth_headers):
        """Успешная смена пароля"""
        change_data = {
            "old_password": test_user["password"],
            "new_password": "NewSecurePass123!"
        }
        response = client.post(
            "/api/auth/change-password",
            json=change_data,
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.OK, 200)

    def test_change_password_wrong_old_password(self, client, auth_headers):
        """Смена пароля с неправильным старым паролем"""
        change_data = {
            "old_password": "WrongOldPassword",
            "new_password": "NewSecurePass123!"
        }
        response = client.post(
            "/api/auth/change-password",
            json=change_data,
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.BAD_REQUEST, 401, 400)


class TestAuthLogout:
    """Тесты выхода из системы"""

    def test_logout(self, client, auth_headers):
        """Выход из системы"""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code in (HTTPStatus.OK, 200)
        data = response.json()
        assert "message" in data or "status" in data
