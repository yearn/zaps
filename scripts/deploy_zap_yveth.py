from brownie import ZapYvWETH, accounts, network
from brownie.network.account import PublicKeyAccount
from brownie.network.gas.strategies import GasNowStrategy


import click

# `speed` must be one of: rapid, fast, standard, slow
GAS_PRICE = "standard"


def main():
    print(f"You are using the '{network.show_active()}' network")
    dev = accounts.load("dev")
    print(f"You are using: 'dev' [{dev.address}]")
    print(f"You are using 'gas price' [{GAS_PRICE}]")
    gas_strategy = GasNowStrategy(GAS_PRICE)

    if input("Deploy ZapYvWETH? y/[N]: ").lower() != "y":
        return

    publish_source = click.confirm("Verify source on etherscan?")

    ZapYvWETH.deploy(
        {"from": dev, "gas_price": gas_strategy}, publish_source=publish_source,
    )
