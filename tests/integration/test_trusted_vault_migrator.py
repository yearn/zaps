import brownie
import pytest
from brownie import chain, web3, Wei


def test_sweep_from_governance(
    interface, Token, user, TrustedVaultMigrator, gov, accounts,
):
    # Registry
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    chiToken = "0x0000000000004946c0e9F43F4Dee607b0eF1fA1c"
    ychad = accounts.at(web3.ens.resolve("ychad.eth"), force=True)

    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

    vaultMigrator = gov.deploy(TrustedVaultMigrator, registry, chiToken)
    # Give user some funds
    tokenAmount = Wei("10 ether")
    token.transfer(vaultMigrator, tokenAmount, {"from": tokenOwner})

    assert token.balanceOf(vaultMigrator) == tokenAmount
    balanceBefore = token.balanceOf(ychad)

    vaultMigrator.sweep(token.address, {"from": ychad})

    assert token.balanceOf(vaultMigrator) == 0
    assert token.balanceOf(ychad) - balanceBefore == tokenAmount


def test_sweep_not_from_governance(
    interface, Token, user, TrustedVaultMigrator, gov, accounts,
):
    # Registry v2
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    chiToken = "0x0000000000004946c0e9F43F4Dee607b0eF1fA1c"
    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

    vaultMigrator = gov.deploy(TrustedVaultMigrator, registry, chiToken)
    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(vaultMigrator, tokenAmount, {"from": tokenOwner})

    with brownie.reverts("governable::only-governance"):
        vaultMigrator.sweep(token.address, {"from": tokenOwner})


def test_migrate_vault_not_latest(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    TrustedVaultMigratorMock,
    gov,
    accounts,
):
    # Registry
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    chiToken = "0x0000000000004946c0e9F43F4Dee607b0eF1fA1c"
    vaultMigrator = gov.deploy(TrustedVaultMigratorMock, registry, chiToken)

    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

    # Create a V1 Vault
    controller = controllerFactoryV1()
    strategy = gov.deploy(StrategyDForceDAI, controller)
    vaultA = vaultFactoryV1(token, controller)
    controller.setStrategy(token, strategy, {"from": gov})

    # Create target V2 vault
    vaultB = vaultFactory(token)

    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit(tokenAmount, {"from": user})

    # Migrate in vaultB
    balanceVaultA = vaultA.balanceOf(user)

    vaultA.approve(vaultMigrator, balanceVaultA, {"from": user})

    with brownie.reverts("Target vault should be the latest for token"):
        vaultMigrator.internalMigrate(vaultA, vaultB, balanceVaultA, {"from": user})


def checkMigrationWasSuccesful(
    vaultMigrator, tokenOwner, sharesAmount, token, fromVault, toVault
):
    ownerSharesOfFromBefore = fromVault.balanceOf(tokenOwner)
    toVaultBalanceOfTokenBefore = token.balanceOf(toVault)
    fromVault.approve(vaultMigrator, sharesAmount, {"from": tokenOwner})
    vaultMigrator.internalMigrate(
        fromVault, toVault, sharesAmount, {"from": tokenOwner}
    )
    ownerSharesOfFromAfter = fromVault.balanceOf(tokenOwner)
    toVaultBalanceOfTokenAfter = token.balanceOf(toVault)
    # Check that share where taken from user
    assert ownerSharesOfFromAfter == ownerSharesOfFromBefore - sharesAmount
    # Check that token funds where moved correctly
    assert toVaultBalanceOfTokenAfter > toVaultBalanceOfTokenBefore
    # Check that user can withdraw from new vault
    toVault.withdraw(toVault.balanceOf(tokenOwner), {"from": tokenOwner})


# Also endorsed to endorsed test
def test_e2e_migrate_v1_dai_migration(
    interface, Token, TrustedVaultMigratorMock, gov, accounts, yVault
):
    # Registry
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    chiToken = "0x0000000000004946c0e9F43F4Dee607b0eF1fA1c"
    vaultMigrator = gov.deploy(TrustedVaultMigratorMock, registry, chiToken)

    DAI = Token.at("0x6b175474e89094c44da98b954eedeac495271d0f")  # DAI
    yDAIWhale = accounts.at(
        "0x3b9af7e7b54578eb9ec9da63af396b11c4f01aef", force=True
    )  # whale for yDAI

    yDAI = yVault.at("0xACd43E627e64355f1861cEC6d3a6688B31a6F952")

    # Create target V2 vault
    latestDAIVault = interface.IVaultAPI(interface.IRegistry(registry).latestVault(DAI))

    checkMigrationWasSuccesful(
        vaultMigrator, yDAIWhale, yDAI.balanceOf(yDAIWhale), DAI, yDAI, latestDAIVault
    )


# Also endorsed to endorsed
def test_e2e_migrate_v1_usdc_migration(
    interface, Token, TrustedVaultMigratorMock, gov, accounts, yVault
):
    # Registry
    registry = "0xe15461b18ee31b7379019dc523231c57d1cbc18c"
    chiToken = "0x0000000000004946c0e9F43F4Dee607b0eF1fA1c"
    vaultMigrator = gov.deploy(TrustedVaultMigratorMock, registry, chiToken)

    USDC = Token.at("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")  # USDC
    yUSDCWhale = accounts.at(
        "0xdb91f52eefe537e5256b8043e5f7c7f44d81f5aa", force=True
    )  # whale for yUSDC

    yUSDC = yVault.at("0x597ad1e0c13bfe8025993d9e79c69e1c0233522e")

    # Create target V2 vault
    latestUSDCVault = interface.IVaultAPI(
        interface.IRegistry(registry).latestVault(USDC)
    )

    checkMigrationWasSuccesful(
        vaultMigrator,
        yUSDCWhale,
        yUSDC.balanceOf(yUSDCWhale),
        USDC,
        yUSDC,
        latestUSDCVault,
    )


# Also endorsed to experimental
def test_e2e_migrate_eth_migration(
    interface, Token, VaultMigratorMock, gov, accounts, yVault
):
    # We can't use trustedVaultMigrator since
    # we want to test the yvWETH experimental vault

    vaultMigrator = gov.deploy(VaultMigratorMock)

    WETH = Token.at("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")  # WETH
    yWETHWhale = accounts.at(
        "0x6bb8bc41e668b7c8ef3850486c9455b5c86830b3", force=True
    )  # whale for yWETH

    yWETH = yVault.at("0xe1237aa7f535b0cc33fd973d66cbf830354d16c7")

    # Create target V2 vault (also experimental)
    latestWETHVault = interface.IVaultAPI("0x6392e8fa0588CB2DCb7aF557FdC9D10FDe48A325")

    checkMigrationWasSuccesful(
        vaultMigrator,
        yWETHWhale,
        yWETH.balanceOf(yWETHWhale),
        WETH,
        yWETH,
        latestWETHVault,
    )
