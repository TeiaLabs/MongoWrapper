import os

import pytest
import dotenv

import mongow


@pytest.fixture
def mongodb_uri() -> str:
    dotenv.load_dotenv()
    return os.environ["MONGODB_URI"]


@pytest.fixture(autouse=True)
def db(mongodb_uri: str):
    return mongow.init_database(mongodb_uri).database
