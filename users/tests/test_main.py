import os
from dotenv import find_dotenv, load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import create_database, database_exists

from .mocks.mocks import create_user, create_user_duplicated, create_user_with_not_properties, update_user_success, update_user_not_properties, generate_token, generate_token_no_properties, generate_token_invalid_password, generate_token_no_user

from ..src import main
from ..src.database import database

env_file = find_dotenv('.env')
loaded = load_dotenv(env_file)

print('********************************************************************************************************')
print('DB_USER->', os.environ.get("DB_USER"),
      'DB_PASSWORD->', os.environ.get("DB_PASSWORD"),
      'DB_HOST->', os.environ.get("DB_HOST"),
      'DB_NAME->', os.environ.get("DB_NAME"),
      'DB_PORT->', os.environ.get("DB_PORT"))
print('********************************************************************************************************')

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    username=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    database="user_test_db",
    port=os.environ.get("DB_PORT")
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
)
if not database_exists(engine.url):
    create_database(engine.url)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    database.Base.metadata.create_all(bind=engine)
    yield
    database.Base.metadata.drop_all(bind=engine)


main.app.dependency_overrides[main.database.get_db] = override_get_db

client = TestClient(main.app)


def test_root(test_db):
    response = client.get("/")
    assert response.status_code == 200


def test_create_users_success(test_db):
    response = client.post("/users", json=create_user)
    assert response.status_code == 201


def test_create_users_already_exist(test_db):
    response1 = client.post("/users", json=create_user_duplicated)
    assert response1.status_code == 201
    response2 = client.post("/users", json=create_user_duplicated)
    assert response2.status_code == 412


def test_create_users_with_not_properties(test_db):
    response = client.post("/users", json=create_user_with_not_properties)
    assert response.status_code == 400


def test_update_user(test_db):
    responseCreate = client.post("/users", json=create_user)
    userId = responseCreate.json()['id']
    responseUpdate = client.patch(
        "/users/"+userId, json=update_user_success)
    assert responseUpdate.status_code == 200
    assert responseUpdate.json() == {"msg": "el usuario ha sido actualizado"}


def test_update_user_not_found(test_db):
    responseUpdate = client.patch(
        "/users/bf8792d2-3097-11ee-be56-0242ac120002", json=update_user_success)
    assert responseUpdate.status_code == 404
    assert responseUpdate.json() == {"detail": "El usuario con este ID no existe"
                                     }


def test_update_user_not_properties(test_db):
    responseCreate = client.post("/users", json=create_user)
    userId = responseCreate.json()['id']
    responseUpdate = client.patch(
        "/users/"+userId, json=update_user_not_properties)
    assert responseUpdate.status_code == 400
    assert responseUpdate.json() == {"detail": "Al menos un campo debe ser pasado en el cuerpo de la petición"
                                     }


def test_generate_token_success(test_db):
    client.post("/users", json=create_user)
    response = client.post("/users/auth", json=generate_token)
    assert response.status_code == 200


def test_generate_token_no_properties(test_db):
    client.post("/users", json=create_user)
    response = client.post("/users/auth", json=generate_token_no_properties)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "username y password son campos obligatorios"}


def test_generate_token_invalid_password(test_db):
    client.post("/users", json=create_user)
    response = client.post("/users/auth", json=generate_token_invalid_password)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Password incorrecto"}


def test_generate_token_no_user(test_db):
    client.post("/users", json=create_user)
    response = client.post("/users/auth", json=generate_token_no_user)
    assert response.status_code == 404
    assert response.json() == {
        "detail": "username con este password no existe"}


def test_check_me_success(test_db):
    client.post("/users", json=create_user)
    responseToken = client.post("/users/auth", json=generate_token)
    token = responseToken.json()['token']

    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_check_me_no_token(test_db):
    response = client.get(
        "/users/me")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "el token no fue suministrado en el header"}


def test_check_me_invalid_token(test_db):
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer fake_token"})
    assert response.status_code == 401
    assert response.json() == {
        "detail": "el token es invalido o ya expiro"}


def test_verify_health(test_db):
    response = client.get("/users/ping")
    assert response.status_code == 200
    assert response.json() == 'pong'


def test_reset(test_db):
    response = client.post("/users/reset")
    assert response.status_code == 200
    assert response.json() == {"msg": "Todos los datos fueron eliminados"}
