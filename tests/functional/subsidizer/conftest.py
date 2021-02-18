import pytest
from brownie import config

@pytest.fixture
def chiToken(ChiToken, accounts):
    chiToken = accounts[0].deploy(ChiToken)
    yield chiToken

@pytest.fixture
def subsidizerMock(SubsidizerMock, chiToken, accounts):
    subsidizerMock = accounts[0].deploy(
        SubsidizerMock,
        chiToken
    )
    yield subsidizerMock

