import pytest
from brownie import config
from brownie import Contract


@pytest.fixture(scope="session")
def deployer(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def user(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def vault():
    yield Contract("0xa258C4606Ca8206D8aA700cE2143D7db854D168c")


@pytest.fixture
def zap(ZapEth, vault, deployer):
    yield deployer.deploy(ZapEth, vault)


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass
