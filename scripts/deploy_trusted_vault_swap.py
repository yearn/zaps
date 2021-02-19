from pathlib import Path

from brownie import TrustedVaultMigrator, accounts, config, network, project, web3
from brownie.network.account import PublicKeyAccount
from eth_utils import is_checksum_address


def main():
    print(f"You are using the '{network.show_active()}' network")
    dev = accounts.load("dev")
    print(f"You are using: 'dev' [{dev.address}]")

    if input("Deploy TrustedVaultMigrator? y/[N]: ").lower() != "y":
        return

    TrustedVaultMigrator.deploy(
        PublicKeyAccount("v2.registry.ychad.eth").address,
        "0x0000000000004946c0e9F43F4Dee607b0eF1fA1c",  # Mainnet Chi Token
        {"from": dev},
    )
