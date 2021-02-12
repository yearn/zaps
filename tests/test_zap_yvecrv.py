from brownie import Wei, Contract


def test_zap(accounts, ZapYvecrv):
    whale = accounts.at("0xbe0eb53f46cd790cd13851d5eff43d12404d33e8", force=True)
    zap = whale.deploy(ZapYvecrv)
    vault_ecrv_live = Contract(zap.yVault())
    vault_ecrv_live.approve(zap, 2 ** 256 - 1, {"from": whale})

    print("")
    print("Zap In 100 ETH actuals")
    print("----------------------------")

    zap.zapIn(0, {"from": whale, "value": Wei("100 ether")})
    yvTokens = vault_ecrv_live.balanceOf(whale)
    yvTokensPretty = yvTokens / Wei("1 ether")
    print(f"Zap in: {yvTokensPretty} yveCRV")

    startingEthBalance = whale.balance()
    zap.zapOut(yvTokens, 0, {"from": whale})
    zappedOutEth = whale.balance() - startingEthBalance
    zappedOutEthPretty = zappedOutEth / Wei("1 ether")
    print(f"Zap out: {zappedOutEthPretty} ETH")
