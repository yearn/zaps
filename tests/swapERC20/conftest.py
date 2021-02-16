import pytest
from brownie import config
from brownie import Contract


@pytest.fixture(
    params=[
        (
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "0x2f08119C6f07c006695E079AAFc638b8789FAf18",
        ),  # yusdt
        (
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "0x597aD1e0c13Bfe8025993D9e79C69E1c0233522e",
        ),  # yusdc
        (
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "0xACd43E627e64355f1861cEC6d3a6688B31a6F952",
        ),  # ydai
        (
            "0xe2f2a5C287993345a840Db3B0845fbC70f5935a5",
            "0xE0db48B4F71752C4bEf16De1DBD042B82976b8C7",
        ),  # yvmUSD
        (
            "0x514910771af9ca656af840dff83e8264ecf986ca",
            "0x881b06da56BB5675c54E4Ed311c21E54C5025298",
        ),  # yLINK
        (
            "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
            "0xBA2E7Fed597fd0E3e70f5130BcDbbFE06bB94fe1",
        ),  # yYFI
        (
            "0x0000000000085d4780B73119b644AE5ecd22b376",
            "0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a",
        ),  # yTUSD
        (
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
            "0xcB550A6D4C8e3517A939BC79d0c7093eb7cF56B5",
        ),  # yWBTC
        (
            "0x584bC13c7D411c00c01A62e8019472dE68768430",
            "0xe11ba472F74869176652C35D30dB89854b5ae84D",
        ),  # yvHEGIC
        (
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9",
        ),  # yvUSDC
        (
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "0x19D3364A399d251E894aC732651be8B0E4e85001",
        ),  # yvDAI
    ]
)
def zapper(accounts, ZapSwapERC20, request):
    (want_address, vault_address) = request.param

    zapper = accounts[0].deploy(ZapSwapERC20, want_address, vault_address)
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
