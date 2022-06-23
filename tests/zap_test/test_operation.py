def test_deposit(user, zap, vault):
    before = user.balance()
    amount = 10**18
    zap.deposit({"from": user, "value": amount})

    assert vault.balanceOf(user) != 0
    assert before == user.balance() + amount


def test_withdraw(user, zap, vault):
    amount = 10**18
    zap.deposit({"from": user, "value": amount})

    before = user.balance()
    vault.approve(zap, vault.balanceOf(user), {"from": user})

    zap.withdraw(vault.balanceOf(user), {"from": user})
    assert user.balance() > before
