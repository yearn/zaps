from itertools import count
from brownie import Wei, reverts
import eth_abi
from brownie.convert import to_bytes
import random
import brownie


def test_zapper(strategy, token, zapper, chain, vault, whale, gov, interface, user):
    if token.allowance(zapper, vault) == 0:
        zapper.updateVaultAddress(vault, {"from": gov})

    user.transfer(zapper, 5 * 1e18)
    after_transfer = vault.balanceOf(user)
    assert after_transfer != 0

    zapper.zapEthIn(50, {"from": user, "value": 5 * 1e18})

    assert vault.balanceOf(user) > after_transfer
    strategy.harvest({"from": gov})

    chain.sleep(2592000)
    chain.mine(1)
    strategy.harvest({"from": gov})

    before_zapEthOut = user.balance()
    vault.approve(zapper, 2 ** 256 - 1, {"from": user})
    zapper.zapEthOut(vault.balanceOf(user), 500, {"from": user})
    assert user.balance() > before_zapEthOut
