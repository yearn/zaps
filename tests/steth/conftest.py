import pytest
from brownie import config
from brownie import Contract


@pytest.fixture
def vault(pm):
    Vault = pm(config["dependencies"][0]).Vault
    vault = Vault.at("0xdCD90C7f6324cfa40d7169ef80b12031770B4325")
    yield vault


@pytest.fixture
def strategy():
    strategy = Contract("0x997a498E72d4225F0D78540B6ffAbb6cA869edc9")

    yield strategy


@pytest.fixture
def gov(accounts, vault):
    gov = vault.governance()
    accounts[0].transfer(gov, 10 * 1e18)
    yield accounts.at(gov, force=True)


@pytest.fixture
def user(accounts):
    yield accounts[1]


@pytest.fixture
def ldo(interface):
    # this one is curvesteth
    yield interface.ERC20("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32")


@pytest.fixture
def token(interface):
    yield interface.ERC20("0x06325440D014e39736583c165C2963BA99fAf14E")


@pytest.fixture
def whale(accounts, web3, token, chain, ldo):
    # big binance7 wallet
    # acc = accounts.at('0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8', force=True)

    ldo_acc = accounts.at("0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c", force=True)

    # big binance8 wallet
    acc = accounts.at("0x97960149fc611508748dE01202974d372a677632", force=True)

    ldo.transfer(acc, 5000000 * 1e20, {"from": ldo_acc})

    assert token.balanceOf(acc) > 0

    yield acc


@pytest.fixture
def zapper(gov, ZapSteth):
    zapper = gov.deploy(ZapSteth)
    yield zapper


@pytest.fixture
def nocoiner(accounts):
    # Has no tokens (DeFi is a ponzi scheme!)
    yield accounts[5]
