from itertools import count
from brownie import Wei, reverts
import eth_abi
from brownie.convert import to_bytes
import random
import brownie
from datetime import datetime


def test_swap_using_fallback(zapper, vault, user):
    user.transfer(zapper, 1e18)
    after_transfer = vault.balanceOf(user)
    assert after_transfer != 0


def test_zapIn_using_musd(weth, zapper, vault, swapService, user, whale, musd):
    # Make musd less valuable
    now = datetime.now()
    timestamp = datetime.timestamp(now) + 10
    swapService.swapExactTokensForETH(
        100_000 * 10 ** musd.decimals(),
        1,
        [musd, weth],
        whale,
        timestamp,
        {"from": whale},
    )
    zapper.zapEthIn({"from": user, "value": 1e18})

    assert vault.balanceOf(user) != 0


def test_zapIn_using_3crv(weth, zapper, vault, swapService, user, whale, musd):
    # Make more valuable
    now = datetime.now()
    timestamp = datetime.timestamp(now) + 10
    swapService.swapExactETHForTokens(
        1, [weth, musd], whale, timestamp, {"from": whale, "amount": "15 ether"}
    )

    zapper.zapEthIn({"from": user, "value": 1e18})

    assert vault.balanceOf(user) != 0


def test_zapOut_using_musd(weth, zapper, vault, swapService, gov, user, whale, musd):
    user.transfer(zapper, 1e18)
    vault.earn({"from": gov})
    vault.approve(zapper, 2 ** 256 - 1, {"from": user})

    # Make musd more valuable
    now = datetime.now()
    timestamp = datetime.timestamp(now) + 10
    swapService.swapExactETHForTokens(
        1, [weth, musd], whale, timestamp, {"from": whale, "amount": "15 ether"}
    )

    before_zapEthOut = user.balance()
    zapper.zapEthOut(vault.balanceOf(user), {"from": user})
    assert user.balance() > before_zapEthOut


def test_zapOut_using_curv3(weth, zapper, vault, swapService, gov, user, whale, musd):
    user.transfer(zapper, 1e18)
    vault.earn({"from": gov})
    vault.approve(zapper, 2 ** 256 - 1, {"from": user})

    # Make musd less valuable
    now = datetime.now()
    timestamp = datetime.timestamp(now) + 10
    swapService.swapExactTokensForETH(
        20_000 * 10 ** musd.decimals(),
        1,
        [musd, weth],
        whale,
        timestamp,
        {"from": whale},
    )

    before_zapEthOut = user.balance()
    zapper.zapEthOut(vault.balanceOf(user), {"from": user})
    assert user.balance() > before_zapEthOut
