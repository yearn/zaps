import pytest


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
