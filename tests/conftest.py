import uuid

import bcrypt
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src import settings
from src.db.base_class import Base
from src.db.session import async_session, engine
from src.models.customer import CustomerSchema
from src.models.schema.in_customer import InSetPasswordSchema


@pytest.fixture
def app() -> FastAPI:
    from src.app import app

    return app


@pytest.fixture
def async_client(app: FastAPI) -> AsyncClient:
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.fixture
async def db_session() -> AsyncSession:
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error during table creation: {e}")
    async with async_session() as session:
        yield session
        await session.flush()
        await session.rollback()


@pytest.fixture(scope="session")
def customer_id() -> uuid.UUID:
    yield uuid.UUID("06c2acac-7810-4dd8-8722-54bdb05fb9e4")


@pytest.fixture(scope="session")
def email() -> str:
    yield "osefhhchnsic@protonmail.com"


@pytest.fixture(scope="session")
def country() -> str:
    yield "DE"


@pytest.fixture(scope="session")
def language() -> str:
    yield "de"


@pytest.fixture(scope="session")
def password() -> str:
    yield "1234"


@pytest.fixture(scope="session")
def confirmed_password(password: str) -> str:
    yield password


@pytest.fixture(scope="session")
def customer_factory(
    customer_id: uuid.UUID, email: str, country: str, language: str, password: str
) -> CustomerSchema:
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    customer = CustomerSchema(
        customer_id=customer_id,
        email=email,
        country=country,
        language=language,
        hashed_password=hashed_password,
    )
    return customer


@pytest.fixture
def set_password_input(
    email: str, password: str, confirmed_password: str
) -> InSetPasswordSchema:
    set_password_input = InSetPasswordSchema(
        email=email,
        password=password,
        confirm_password=confirmed_password,
    )
    yield set_password_input


@pytest.fixture
def generate_jwt_token(customer_id: str) -> str:
    payload = {"customer_id": str(customer_id)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    yield token


@pytest.fixture
def async_client_with_jwt(async_client, generate_jwt_token) -> AsyncClient:
    async_client.headers["Authorization"] = f"Bearer {generate_jwt_token}"
    yield async_client


@pytest.fixture(scope="session")
def client_version() -> str:
    yield "2.1.1"


@pytest.fixture
def async_client_with_jwt_and_client_version(
    async_client_with_jwt, client_version
) -> AsyncClient:
    async_client_with_jwt.headers["client-version"] = client_version
    yield async_client_with_jwt
