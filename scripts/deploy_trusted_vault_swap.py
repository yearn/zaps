from brownie import TrustedVaultMigrator, accounts, network
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

    if input("Deploy TrustedVaultMigrator? y/[N]: ").lower() != "y":
        return

    publish_source = click.confirm("Verify source on etherscan?")

    TrustedVaultMigrator.deploy(
        PublicKeyAccount("v2.registry.ychad.eth").address,
        "0x0000000000004946c0e9F43F4Dee607b0eF1fA1c",  # Mainnet Chi Token
        {"from": dev, "gas_price": gas_strategy},
        publish_source=publish_source,
    )
