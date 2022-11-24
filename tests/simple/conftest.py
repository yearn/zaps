import pytest
from brownie import config, Wei, Contract, chain, ZERO_ADDRESS, interface
import requests

# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture
def gov(accounts):
    yield accounts.at("0xF5d9D6133b698cE29567a90Ab35CfB874204B3A7", force=True) # optimism 0xF5d9D6133b698cE29567a90Ab35CfB874204B3A7


@pytest.fixture
def registry():
    yield interface.IRegistry("0x79286Dd38C9017E5423073bAc11F53357Fc5C128")  # optimism: 0x79286Dd38C9017E5423073bAc11F53357Fc5C128, mainnet v2: 0x50c1a2eA0a861A967D9d0FFE2AE4012c2E053804


@pytest.fixture
def simple_migrator(gov, SimpleVaultMigrator, registry):
    simple_migrator = gov.deploy(SimpleVaultMigrator, gov, registry)
    yield simple_migrator


# this is the amount of funds we have our whale deposit. adjust this as needed based on their wallet balance
@pytest.fixture
def amount():
    amount = 5_000e18
    yield amount


@pytest.fixture
def dai_whale(accounts):
    # Totally in it for the tech
    dai_whale = accounts.at("0xc66825C5c04b3c2CcD536d626934E16248A63f68", force=True)
    yield dai_whale


@pytest.fixture
def dai(interface):
    return interface.ERC20("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1")


@pytest.fixture
def oldest_vault(interface):
    yield interface.VaultToken("0xa318373f0424ef0257b5b75460548D6d34947D97")


@pytest.fixture
def old_vault():
    yield interface.VaultToken("0xfbef713696465DDab297164c3b6A0122D92A3bAc")


@pytest.fixture
def new_vault_dai():
    yield interface.VaultToken("0x65343F414FFD6c97b0f6add33d16F6845Ac22BAc")


@pytest.fixture
def new_vault_weth():
    yield interface.VaultToken("0x5B977577Eb8a480f63e11FC615D6753adB8652Ae")


@pytest.fixture
def weth(interface):
    yield interface.ERC20(
        "0x4200000000000000000000000000000000000006"
    )  # op: 0x4200000000000000000000000000000000000006, mainnet: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
