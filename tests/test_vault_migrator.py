import brownie
import pytest
from brownie import Wei, chain
from eth_account import Account
from eth_account.messages import encode_structured_data


def generate_permit(vault, owner: Account, spender: Account, value, nonce, deadline):
    name = "Yearn Vault"
    version = vault.apiVersion()
    chain_id = 1  # ganache bug https://github.com/trufflesuite/ganache/issues/1643
    contract = str(vault)
    data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Permit": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint256"},
            ],
        },
        "domain": {
            "name": name,
            "version": version,
            "chainId": chain_id,
            "verifyingContract": contract,
        },
        "primaryType": "Permit",
        "message": {
            "owner": owner.address,
            "spender": spender.address,
            "value": value,
            "nonce": nonce,
            "deadline": deadline,
        },
    }
    return encode_structured_data(data)


def beforeTestMigrateAll(
    user,
    gov,
    accounts,
    Token,
    controllerFactoryV1,
    vaultFactory,
    vaultFactoryV1,
    StrategyDForceDAI,
):
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
    tokenAmount = Wei("10 ether")
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit(tokenAmount, {"from": user})

    yield token
    yield tokenOwner
    yield tokenAmount
    yield vaultA
    yield vaultB


def beforeTestMigrateWithPermit(accounts, tokenOwner, tokenFactory, vaultFactory):
    userForSignature = Account.create()
    user = accounts.at(userForSignature.address, force=True)

    token = tokenFactory()
    vaultA = vaultFactory(token)
    vaultB = vaultFactory(token)

    # Give user some funds
    tokenAmount = Wei("10 ether")
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit({"from": user})

    yield user
    yield userForSignature
    yield token
    yield tokenAmount
    yield vaultA
    yield vaultB


def checkSuccesfullMigrateShares(user, sharesAmount, vaultMigrator, vaultA, vaultB):
    preMigrationVaultABalance = vaultA.balanceOf(user)
    assert preMigrationVaultABalance >= sharesAmount
    vaultMigrator.migrateShares(vaultA, vaultB, sharesAmount, {"from": user})
    postMigrationVaultBBalance = vaultB.balanceOf(user)
    assert vaultA.balanceOf(user) == preMigrationVaultABalance - sharesAmount
    assert postMigrationVaultBBalance == sharesAmount


def checkSuccesfullMigration(tx, user, sharesAmount, vaultMigrator, vaultA, vaultB):
    preMigrationVaultABalance = vaultA.balanceOf(user)
    assert preMigrationVaultABalance >= sharesAmount
    tx()
    postMigrationVaultBBalance = vaultB.balanceOf(user)
    assert vaultA.balanceOf(user) == preMigrationVaultABalance - sharesAmount
    assert postMigrationVaultBBalance == sharesAmount
    vaultB.withdraw(sharesAmount, {"from": user})


def test_migrate_all_not_approved(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
    token, tokenOwner, tokenAmount, vaultA, vaultB = beforeTestMigrateAll(
        user,
        gov,
        accounts,
        Token,
        controllerFactoryV1,
        vaultFactory,
        vaultFactoryV1,
        StrategyDForceDAI,
    )

    with brownie.reverts("ERC20: transfer amount exceeds allowance"):
        vaultMigrator.migrateAll(vaultA, vaultB, {"from": user})


def test_migrate_all_less_approved(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
    token, tokenOwner, tokenAmount, vaultA, vaultB = beforeTestMigrateAll(
        user,
        gov,
        accounts,
        Token,
        controllerFactoryV1,
        vaultFactory,
        vaultFactoryV1,
        StrategyDForceDAI,
    )

    vaultA.approve(vaultMigrator, tokenAmount - Wei("1 ether"), {"from": user})

    with brownie.reverts("ERC20: transfer amount exceeds allowance"):
        vaultMigrator.migrateAll(vaultA, vaultB, {"from": user})


def test_migrate_all_approved(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
    token, tokenOwner, tokenAmount, vaultA, vaultB = beforeTestMigrateAll(
        user,
        gov,
        accounts,
        Token,
        controllerFactoryV1,
        vaultFactory,
        vaultFactoryV1,
        StrategyDForceDAI,
    )

    vaultA.approve(vaultMigrator, tokenAmount, {"from": user})

    def migrateTx():
        vaultMigrator.migrateAll(vaultA, vaultB, {"from": user})

    checkSuccesfullMigration(
        migrateTx, user, tokenAmount, vaultMigrator, vaultA, vaultB
    )


def test_migrate_all_with_lower_permit(
    vaultFactory, tokenFactory, tokenOwner, vaultMigrator, chain, accounts
):

    (
        user,
        userForSignature,
        token,
        tokenAmount,
        vaultA,
        vaultB,
    ) = beforeTestMigrateWithPermit(accounts, tokenOwner, tokenFactory, vaultFactory)

    # Migrate in vaultB
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        vaultA,
        userForSignature,
        vaultMigrator,
        tokenAmount - 1,
        vaultA.nonces(user),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature

    with brownie.reverts():
        vaultMigrator.migrateAllWithPermit(
            vaultA, vaultB, deadline, signature, {"from": user}
        )


def test_migrate_all_with_permit(
    vaultFactory, tokenFactory, tokenOwner, vaultMigrator, chain, accounts
):
    (
        user,
        userForSignature,
        token,
        tokenAmount,
        vaultA,
        vaultB,
    ) = beforeTestMigrateWithPermit(accounts, tokenOwner, tokenFactory, vaultFactory)

    # Migrate in vaultB
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        vaultA,
        userForSignature,
        vaultMigrator,
        tokenAmount,
        vaultA.nonces(user),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature

    def migrateTx():
        vaultMigrator.migrateAllWithPermit(
            vaultA, vaultB, deadline, signature, {"from": user}
        )

    checkSuccesfullMigration(
        migrateTx, user, tokenAmount, vaultMigrator, vaultA, vaultB
    )


def test_migrate_shares_no_approve(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
    token, tokenOwner, tokenAmount, vaultA, vaultB = beforeTestMigrateAll(
        user,
        gov,
        accounts,
        Token,
        controllerFactoryV1,
        vaultFactory,
        vaultFactoryV1,
        StrategyDForceDAI,
    )
    with brownie.reverts("ERC20: transfer amount exceeds allowance"):
        vaultMigrator.migrateShares(vaultA, vaultB, tokenAmount, {"from": user})


def test_migrate_shares_less_approved(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
    token, tokenOwner, tokenAmount, vaultA, vaultB = beforeTestMigrateAll(
        user,
        gov,
        accounts,
        Token,
        controllerFactoryV1,
        vaultFactory,
        vaultFactoryV1,
        StrategyDForceDAI,
    )

    vaultA.approve(vaultMigrator, tokenAmount - Wei("1 ether"), {"from": user})

    with brownie.reverts("ERC20: transfer amount exceeds allowance"):
        vaultMigrator.migrateShares(vaultA, vaultB, tokenAmount, {"from": user})


def test_migrate_shares_all_approved(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
    token, tokenOwner, tokenAmount, vaultA, vaultB = beforeTestMigrateAll(
        user,
        gov,
        accounts,
        Token,
        controllerFactoryV1,
        vaultFactory,
        vaultFactoryV1,
        StrategyDForceDAI,
    )

    amountToMigrate = tokenAmount - Wei("1 ether")

    vaultA.approve(vaultMigrator, amountToMigrate, {"from": user})

    def migrateTx():
        vaultMigrator.migrateShares(vaultA, vaultB, amountToMigrate, {"from": user})

    checkSuccesfullMigration(
        migrateTx, user, amountToMigrate, vaultMigrator, vaultA, vaultB
    )


def test_migrate_shares_with_lower_permit(
    vaultFactory, tokenFactory, tokenOwner, vaultMigrator, chain, accounts
):
    (
        user,
        userForSignature,
        token,
        tokenAmount,
        vaultA,
        vaultB,
    ) = beforeTestMigrateWithPermit(accounts, tokenOwner, tokenFactory, vaultFactory)

    # Migrate in vaultB
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        vaultA,
        userForSignature,
        vaultMigrator,
        tokenAmount - Wei("1 ether"),
        vaultA.nonces(user),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature

    with brownie.reverts():
        vaultMigrator.migrateSharesWithPermit(
            vaultA, vaultB, tokenAmount, deadline, signature, {"from": user}
        )


def test_migrate_shares_with_permit(
    vaultFactory, tokenFactory, tokenOwner, vaultMigrator, chain, accounts
):
    (
        user,
        userForSignature,
        token,
        tokenAmount,
        vaultA,
        vaultB,
    ) = beforeTestMigrateWithPermit(accounts, tokenOwner, tokenFactory, vaultFactory)

    amountToMigrate = tokenAmount - Wei("1 ether")

    # Migrate in vaultB
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        vaultA,
        userForSignature,
        vaultMigrator,
        amountToMigrate,
        vaultA.nonces(user),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature

    def migrateTx():
        vaultMigrator.migrateSharesWithPermit(
            vaultA, vaultB, amountToMigrate, deadline, signature, {"from": user}
        )

    checkSuccesfullMigration(
        migrateTx, user, amountToMigrate, vaultMigrator, vaultA, vaultB
    )


def test_migrate_from_v1_to_v1_different_token(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
    tokenFactory,
):
    token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
    tokenOwner = accounts.at(
        "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
    )  # whale for DAI

    # Create a V1 Vault
    controller = controllerFactoryV1()
    strategy = gov.deploy(StrategyDForceDAI, controller)
    vaultA = vaultFactoryV1(token, controller)
    controller.setStrategy(token, strategy, {"from": gov})

    # Create another V1 Vault
    tokenVaultB = tokenFactory()
    vaultB = vaultFactoryV1(tokenVaultB, controller)
    controller.setStrategy(tokenVaultB, strategy, {"from": gov})

    # Give user some funds
    tokenAmount = Wei("10 ether")
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit(tokenAmount, {"from": user})

    vaultA.approve(vaultMigrator, tokenAmount, {"from": user})

    with brownie.reverts("Vaults must have the same token"):
        vaultMigrator.internalMigrate(vaultA, vaultB, tokenAmount, {"from": user})


# TODO: FIx
# def test_migrate_from_v1_to_v1_same_token(
#     vaultFactory,
#     vaultFactoryV1,
#     controllerFactoryV1,
#     Token,
#     StrategyDForceDAI,
#     user,
#     vaultMigrator,
#     gov,
#     accounts,
#     tokenFactory
# ):
#     token = Token.at("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
#     tokenOwner = accounts.at(
#         "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", force=True
#     )  # whale for DAI

#     # Create a V1 Vault
#     controller = controllerFactoryV1()
#     strategy = gov.deploy(StrategyDForceDAI, controller)
#     vaultA = vaultFactoryV1(token, controller)
#     controller.setStrategy(token, strategy, {"from": gov})

#     # Create another V1 Vault
#     controllerB = controllerFactoryV1()
#     strategyB = gov.deploy(StrategyDForceDAI, controllerB)
#     vaultB = vaultFactoryV1(token, controllerB)
#     controllerB.setStrategy(token, strategyB, {"from": gov})

#     # Give user some funds
#     tokenAmount = Wei("10 ether")
#     token.transfer(user, tokenAmount, {"from": tokenOwner})

#     # Deposit in vaultA
#     token.approve(vaultA, tokenAmount, {"from": user})
#     vaultA.deposit(tokenAmount, {"from": user})

#     vaultA.approve(vaultMigrator, tokenAmount, {"from": user})

#     vaultMigrator.internalMigrate(vaultA, vaultB, tokenAmount, {"from": user})


def test_migrate_from_v1_to_v2_different_token(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
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
    tokenAmount = Wei("10 ether")
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit(tokenAmount, {"from": user})

    vaultA.approve(vaultMigrator, tokenAmount, {"from": user})

    def migrateTx():
        vaultMigrator.internalMigrate(vaultA, vaultB, tokenAmount, {"from": user})

    checkSuccesfullMigration(
        migrateTx, user, tokenAmount, vaultMigrator, vaultA, vaultB
    )


def test_migrate_from_v1_to_v2_same_token(
    vaultFactory,
    vaultFactoryV1,
    controllerFactoryV1,
    Token,
    StrategyDForceDAI,
    user,
    vaultMigrator,
    gov,
    accounts,
):
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
    tokenAmount = Wei("10 ether")
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit(tokenAmount, {"from": user})

    vaultA.approve(vaultMigrator, tokenAmount, {"from": user})

    def migrateTx():
        vaultMigrator.internalMigrate(vaultA, vaultB, tokenAmount, {"from": user})

    checkSuccesfullMigration(
        migrateTx, user, tokenAmount, vaultMigrator, vaultA, vaultB
    )


def test_migrate_from_v2_to_v2_different_token(
    vaultFactory, tokenFactory, tokenOwner, user, vaultMigrator
):
    tokenA = tokenFactory()
    tokenB = tokenFactory()
    vaultA = vaultFactory(tokenA)
    vaultB = vaultFactory(tokenB)

    # Give user some funds
    tokenAmount = "10 ether"
    tokenA.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    tokenA.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit({"from": user})

    # Migrate in vaultB
    vaultA.approve(vaultMigrator, tokenAmount, {"from": user})

    with brownie.reverts("Vaults must have the same token"):
        vaultMigrator.internalMigrate(vaultA, vaultB, tokenAmount, {"from": user})


def test_migrate_from_v2_to_v2_same_token(
    vaultFactory, tokenFactory, tokenOwner, user, vaultMigrator
):
    token = tokenFactory()
    vaultA = vaultFactory(token)
    vaultB = vaultFactory(token)

    # Give user some funds
    tokenAmount = "10 ether"
    token.transfer(user, tokenAmount, {"from": tokenOwner})

    # Deposit in vaultA
    token.approve(vaultA, tokenAmount, {"from": user})
    vaultA.deposit({"from": user})

    # Migrate in vaultB
    vaultA.approve(vaultMigrator, tokenAmount, {"from": user})

    def migrateTx():
        vaultMigrator.internalMigrate(vaultA, vaultB, tokenAmount, {"from": user})

    checkSuccesfullMigration(
        migrateTx, user, tokenAmount, vaultMigrator, vaultA, vaultB
    )
