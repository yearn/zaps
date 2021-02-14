import pytest
from brownie import config
from brownie import Contract


@pytest.fixture
def vault():
    vault = Contract("0x0FCDAeDFb8A7DfDa2e9838564c5A1665d856AFDF")
    yield vault


@pytest.fixture
def gov(accounts, vault):
    gov = vault.governance()
    accounts[0].transfer(gov, 10 * 1e18)
    yield accounts.at(gov, force=True)


@pytest.fixture
def weth():
    yield Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture
def user(accounts):
    yield accounts[1]


@pytest.fixture
def zapper(gov, ZapMusd3CRV):
    zapper = gov.deploy(ZapMusd3CRV)
    yield zapper


@pytest.fixture
def token(interface, zapper):
    yield interface.ERC20(zapper.want())


@pytest.fixture
def usdt(zapper):
    yield Contract(zapper.threeCurveCoins(2))


@pytest.fixture
def musd(zapper):
    yield Contract.from_explorer(
        zapper.musd3Coins(0), as_proxy_for="0xE0d0D052d5B1082E52C6b8422Acd23415c3DF1c4"
    )


@pytest.fixture
def swapService(zapper):
    yield Contract(zapper.swapService())


@pytest.fixture
def whale(accounts, usdt, musd, zapper, swapService):
    whale = accounts[2]
    accounts[5].transfer(whale, 10 * 1e18)

    # get a large amount of usdt
    owner = accounts.at(usdt.getOwner(), force=True)
    amount = 10_000_000 * 10 ** usdt.decimals()
    usdt.issue(amount, {"from": owner})
    usdt.transfer(whale, amount, {"from": owner})

    # approve
    usdt.approve(zapper, 2 ** 256 - 1, {"from": whale})
    usdt.approve(swapService, 2 ** 256 - 1, {"from": whale})
    usdt.approve(musd, 2 ** 256 - 1, {"from": whale})
    # mint musd

    musd.mintTo(usdt, amount / 2, whale, {"from": whale})
    musd.approve(zapper, 2 ** 256 - 1, {"from": whale})
    musd.approve(swapService, 2 ** 256 - 1, {"from": whale})

    yield whale
