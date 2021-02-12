from pathlib import Path

from brownie import VaultMigrator, accounts, config, network, project, web3
from eth_utils import is_checksum_address


def main():
    print(f"You are using the '{network.show_active()}' network")
    dev = accounts.load("dev")
    print(f"You are using: 'dev' [{dev.address}]")

    if input("Deploy VaultMigrator? y/[N]: ").lower() != "y":
        return

    VaultMigrator.deploy({"from": dev})
