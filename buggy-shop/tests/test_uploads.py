# tests/test_uploads.py
import pytest
from http import HTTPStatus
from io import BytesIO


class TestFileUpload:
    """Тесты загрузки файлов"""

    def test_upload_file_success(self, client, auth_headers):
        """Успешная загрузка файла"""
        # Создаем тестовый файл
        file_content = b"Test file content"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }

        response = client.post(
            "/api/uploads/upload",
            files=files,
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, 200, 201)
        data = response.json()
        assert "filename" in data
        assert data["filename"] == "test.txt"
        assert "size" in data
        assert data["size"] == len(file_content)

    def test_upload_file_no_auth(self, client):
        """Загрузка файла без авторизации"""
        file_content = b"Test"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }

        response = client.post("/api/uploads/upload", files=files)
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, 401, 403)

    def test_upload_multiple_files(self, client, auth_headers):
        """Загрузка нескольких файлов"""
        files_to_upload = [
            ("file1.txt", b"Content 1"),
            ("file2.txt", b"Content 2"),
            ("file3.txt", b"Content 3")
        ]

        for filename, content in files_to_upload:
            files = {
                "file": (filename, BytesIO(content), "text/plain")
            }
            response = client.post(
                "/api/uploads/upload",
                files=files,
                headers=auth_headers
            )
            assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, 200, 201)

    def test_upload_large_file(self, client, auth_headers):
        """Загрузка большого файла"""
        # Создаем файл размером 1MB
        large_content = b"X" * (1024 * 1024)
        files = {
            "file": ("large.bin", BytesIO(large_content), "application/octet-stream")
        }

        response = client.post(
            "/api/uploads/upload",
            files=files,
            headers=auth_headers
        )
        # Может успешно загрузиться или вернуть ошибку, зависит от лимитов
        assert response.status_code in (
            HTTPStatus.OK, HTTPStatus.CREATED, 
            HTTPStatus.BAD_REQUEST, HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            200, 201, 400, 413
        )

    def test_upload_file_with_special_characters(self, client, auth_headers):
        """Загрузка файла с специальными символами в имени"""
        file_content = b"Test"
        files = {
            "file": ("test file!@#.txt", BytesIO(file_content), "text/plain")
        }

        response = client.post(
            "/api/uploads/upload",
            files=files,
            headers=auth_headers
        )
        # Может быть успех или ошибка, зависит от валидации имени файла
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.BAD_REQUEST, 200, 201, 400)

    def test_upload_image_file(self, client, auth_headers):
        """Загрузка изображения"""
        # Простейший PNG (1x1 pixel)
        png_content = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        )
        files = {
            "file": ("test.png", BytesIO(png_content), "image/png")
        }

        response = client.post(
            "/api/uploads/upload",
            files=files,
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, 200, 201)


class TestFileDownload:
    """Тесты скачивания файлов"""

    def test_download_existing_file(self, client, auth_headers):
        """Скачивание существующего файла"""
        # Сначала загружаем файл
        file_content = b"Download test content"
        files = {
            "file": ("download_test.txt", BytesIO(file_content), "text/plain")
        }
        upload_response = client.post(
            "/api/uploads/upload",
            files=files,
            headers=auth_headers
        )
        assert upload_response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, 200, 201)
        filename = upload_response.json()["filename"]

        # Теперь скачиваем
        response = client.get(f"/api/uploads/download/{filename}")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "message" in data or "filename" in data

    def test_download_nonexistent_file(self, client):
        """Скачивание несуществующего файла"""
        response = client.get("/api/uploads/download/nonexistent_file.txt")
        assert response.status_code in (HTTPStatus.NOT_FOUND, 404)

    def test_download_file_with_path_traversal(self, client):
        """Попытка скачать файл с path traversal"""
        response = client.get("/api/uploads/download/../../../etc/passwd")
        # Должен вернуть ошибку или не найти файл
        assert response.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST, 404, 400)


class TestFileUploadEdgeCases:
    """Тесты граничных случаев загрузки"""

    def test_upload_empty_file(self, client, auth_headers):
        """Загрузка пустого файла"""
        files = {
            "file": ("empty.txt", BytesIO(b""), "text/plain")
        }

        response = client.post(
            "/api/uploads/upload",
            files=files,
            headers=auth_headers
        )
        # Может быть успех или ошибка
        assert response.status_code in (
            HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.BAD_REQUEST,
            200, 201, 400
        )

    def test_upload_without_file(self, client, auth_headers):
        """Попытка загрузки без файла"""
        response = client.post(
            "/api/uploads/upload",
            headers=auth_headers
        )
        assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST, 422, 400)

    def test_upload_file_same_name_twice(self, client, auth_headers):
        """Загрузка двух файлов с одинаковым именем"""
        file_content1 = b"First content"
        file_content2 = b"Second content"

        files1 = {
            "file": ("duplicate.txt", BytesIO(file_content1), "text/plain")
        }
        response1 = client.post(
            "/api/uploads/upload",
            files=files1,
            headers=auth_headers
        )
        assert response1.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, 200, 201)

        files2 = {
            "file": ("duplicate.txt", BytesIO(file_content2), "text/plain")
        }
        response2 = client.post(
            "/api/uploads/upload",
            files=files2,
            headers=auth_headers
        )
        # Может перезаписать или вернуть ошибку
        assert response2.status_code in (
            HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.CONFLICT,
            200, 201, 409
        )
