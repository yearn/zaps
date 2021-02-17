import pytest
from brownie import config


@pytest.fixture
def subsidizerMock():
    yield

@pytest.fixture
def chiToken(accounts):
    yield accounts[0]

