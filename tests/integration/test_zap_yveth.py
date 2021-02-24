from brownie import Wei


def test_zap_eth(zap_eth, eth_whale, live_weth_vault, weth, interface):

    # Deposit 1 ETH
    amount = 1e18
    assert live_weth_vault.balanceOf(eth_whale) == 0

    zap_eth.depositETH({"from": eth_whale, "value": amount})

    assert live_weth_vault.balanceOf(eth_whale) > 0
    # price per share when vault is empty is 1 to 1
    # assert live_weth_vault.balanceOf(eth_whale) == amount
    print(f"Final Balance '{live_weth_vault.balanceOf(eth_whale)}'")