import brownie
import pytest
from brownie import chain, web3, Wei


def test_sweep(
    interface, Token, user, TrustedVaultMigrator, gov, accounts,
):
    # Registry
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    ychad = accounts.at(web3.ens.resolve("ychad.eth"), force=True)

    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

    vaultMigrator = gov.deploy(TrustedVaultMigrator, registry)
    # Give user some funds
    tokenAmount = Wei("10 ether")
    token.transfer(vaultMigrator, tokenAmount, {"from": tokenOwner})

    assert token.balanceOf(vaultMigrator) == tokenAmount
    balanceBefore = token.balanceOf(ychad)

    vaultMigrator.sweep(token.address, {"from": ychad})

    assert token.balanceOf(vaultMigrator) == 0
    assert token.balanceOf(ychad) - balanceBefore == tokenAmount


def test_sweep_from_rando(
    interface, Token, user, TrustedVaultMigrator, gov, accounts,
):
    # Registry v2
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

    vaultMigrator = gov.deploy(TrustedVaultMigrator, registry)
    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(vaultMigrator, tokenAmount, {"from": tokenOwner})

    with brownie.reverts("governable::only-governance"):
        vaultMigrator.sweep(token.address, {"from": tokenOwner})
