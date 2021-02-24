import pytest
from brownie import config, Contract


@pytest.fixture
def tokenOwner(accounts):
    yield accounts[0]


@pytest.fixture
def gov(accounts):
    yield accounts[1]


@pytest.fixture
def rewards(gov):
    yield gov


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def user(accounts):
    yield accounts[3]


@pytest.fixture
def Vault(pm):
    Vault = pm(config["dependencies"][0]).Vault
    yield Vault


@pytest.fixture
def tokenFactory(tokenOwner, Token):
    def factory():
        return tokenOwner.deploy(Token)

    yield factory


@pytest.fixture
def controllerFactoryV1(gov, StrategyControllerV2):
    def factory():
        controller = gov.deploy(
            StrategyControllerV2, "0x0000000000000000000000000000000000000000"
        )
        return controller

    yield factory


@pytest.fixture
def vaultFactoryV1(gov, yVault):
    def factory(token, controller):
        vault = gov.deploy(yVault, token, controller)
        return vault

    yield factory


@pytest.fixture
def vaultFactory(pm, gov, rewards, guardian):
    def factory(token):
        Vault = pm(config["dependencies"][0]).Vault
        vault = guardian.deploy(Vault)
        vault.initialize(token, gov, rewards, "", "", {"from": guardian})
        vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
        return vault

    yield factory


@pytest.fixture
def vaultMigrator(guardian, VaultMigratorMock):
    yield guardian.deploy(VaultMigratorMock)


@pytest.fixture
def weth(interface):
    yield interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture
def eth_whale(accounts):
    whale = accounts.at("0x1b3cB81E51011b549d78bf720b0d924ac763A7C2", force=True)
    yield whale


@pytest.fixture
def zap_eth(gov, ZapYvWETH):
    yield gov.deploy(ZapYvWETH)


@pytest.fixture
def live_weth_vault(Vault):
    yield Vault.at("0xa9fE4601811213c340e850ea305481afF02f5b28")
