import pytest
from brownie import config
from brownie import Contract


@pytest.fixture
def zapper(accounts, ZapYDai):
    zapper = accounts[0].deploy(ZapYDai)
    yield zapper


@pytest.fixture
def vault(zapper):
    vault = Contract(zapper.yVault())
    yield vault


@pytest.fixture
def gov(accounts, vault):
    gov = vault.governance()
    accounts[0].transfer(gov, 10 * 1e18)
    yield accounts.at(gov, force=True)


@pytest.fixture
def user(accounts):
    yield accounts[1]


@pytest.fixture
def token(interface, zapper):
    yield interface.ERC20(zapper.want())
