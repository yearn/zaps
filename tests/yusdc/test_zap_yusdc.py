import brownie


def test_swap_using_fallback(zapper, vault, user):
    user.transfer(zapper, 1e18)
    after_transfer = vault.balanceOf(user)
    assert after_transfer != 0


def test_zapIn_ZapOut(zapper, vault, user):
    zapper.zapEthIn({"from": user, "value": 1e18})
    assert vault.balanceOf(user) != 0

    before_zapEthOut = user.balance()
    vault.approve(zapper, 2 ** 256 - 1, {"from": user})
    zapper.zapEthOut(vault.balanceOf(user), {"from": user})
    assert user.balance() > before_zapEthOut
