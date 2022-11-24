import brownie
import pytest
from brownie import chain, web3, Wei, Contract, ZERO_ADDRESS
from eth_account import Account
from eth_account.messages import encode_structured_data


def test_sweep(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    oldest_vault,
):

    ## deposit to the vault after approving
    dai.approve(oldest_vault, 2**256 - 1, {"from": dai_whale})
    oldest_vault.deposit(amount, {"from": dai_whale})

    # oopsie, send some dai to the contract
    dai.transfer(simple_migrator, amount, {"from": dai_whale})

    # whale can't sweep it back out
    with brownie.reverts():
        simple_migrator.sweep(dai.address, {"from": dai_whale})

    # but gov can
    assert dai.balanceOf(simple_migrator) == amount
    before = dai.balanceOf(gov)
    simple_migrator.sweep(dai.address, {"from": gov})
    assert dai.balanceOf(simple_migrator) == 0
    assert dai.balanceOf(gov) - before == amount


def test_migrate_vault(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
):

    ## deposit to the vault after approving
    dai.approve(oldest_vault, 2**256 - 1, {"from": dai_whale})
    oldest_vault.deposit(amount, {"from": dai_whale})
    vault_shares = oldest_vault.balanceOf(dai_whale)

    # check that this works
    from_shares_before = oldest_vault.balanceOf(dai_whale)
    to_shares_before = new_vault_dai.balanceOf(dai_whale)
    oldest_vault.approve(simple_migrator, vault_shares, {"from": dai_whale})
    simple_migrator.migrateAll(oldest_vault, new_vault_dai, {"from": dai_whale})
    from_shares_after = oldest_vault.balanceOf(dai_whale)
    to_shares_after = new_vault_dai.balanceOf(dai_whale)

    # Check that share where taken from user
    assert from_shares_after == from_shares_before - vault_shares
    # Check that token funds where moved correctly
    assert to_shares_after > to_shares_before
    # Check that user can withdraw from new vault
    new_vault_dai.withdraw(
        new_vault_dai.balanceOf(dai_whale), {"from": dai_whale}
    )


def test_migrate_vault_reverts(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
    new_vault_weth,
):

    ## deposit to the vault after approving
    dai.approve(oldest_vault, 2**256 - 1, {"from": dai_whale})
    oldest_vault.deposit(amount, {"from": dai_whale})
    vault_shares = oldest_vault.balanceOf(dai_whale)

    # make our approval
    oldest_vault.approve(simple_migrator, vault_shares, {"from": dai_whale})

    # we can't migrate to a different want or the non-newest version
    with brownie.reverts("Vaults must have the same token"):
        simple_migrator.migrateAll(oldest_vault, new_vault_weth, {"from": dai_whale})

    with brownie.reverts("Target vault should be the latest for token"):
        simple_migrator.migrateAll(oldest_vault, old_vault, {"from": dai_whale})


def generate_permit(vault, owner: Account, spender: Account, value, nonce, deadline):
    name = "Yearn Vault"
    version = vault.apiVersion()
    chain_id = 10  # ganache bug https://github.com/trufflesuite/ganache/issues/1643
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


def test_migrate_vault_permit(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
    accounts,
):

    ## deposit to the vault after approving
    # whale send tester some money
    userForSignature = Account.create()
    user = accounts.at(userForSignature.address, force=True)
    dai.transfer(user, amount, {"from": dai_whale})
    dai.approve(oldest_vault, 2**256 - 1, {"from": user})
    oldest_vault.deposit(amount, {"from": user})
    vault_shares = oldest_vault.balanceOf(user)

    # check that this works
    from_shares_before = oldest_vault.balanceOf(user)
    to_shares_before = new_vault_dai.balanceOf(user)
    
    # migrate with our permit
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        oldest_vault,
        userForSignature,
        simple_migrator,
        vault_shares,
        oldest_vault.nonces(user),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature
    
    simple_migrator.migrateAllWithPermit(
            oldest_vault, new_vault_dai, deadline, signature, {"from": user}
        )
    
    from_shares_after = oldest_vault.balanceOf(user)
    to_shares_after = new_vault_dai.balanceOf(user)

    # Check that share where taken from user
    assert from_shares_after == from_shares_before - vault_shares
    # Check that token funds where moved correctly
    assert to_shares_after > to_shares_before
    # Check that user can withdraw from new vault
    new_vault_dai.withdraw(
        new_vault_dai.balanceOf(user), {"from": user}
    )


def test_migrate_vault_bad_permit(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
    accounts,
):

    ## deposit to the vault after approving
    # whale send tester some money
    userForSignature = Account.create()
    user = accounts.at(userForSignature.address, force=True)
    dai.approve(oldest_vault, 2**256 - 1, {"from": dai_whale})
    oldest_vault.deposit(amount, {"from": dai_whale})
    vault_shares = oldest_vault.balanceOf(dai_whale)

    # check that this works
    from_shares_before = oldest_vault.balanceOf(dai_whale)
    to_shares_before = new_vault_dai.balanceOf(dai_whale)
    
    # migrate with our permit
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        oldest_vault,
        dai_whale,
        simple_migrator,
        vault_shares,
        oldest_vault.nonces(dai_whale),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature
    
    with brownie.reverts():
        simple_migrator.migrateAllWithPermit(
            oldest_vault, new_vault_dai, deadline, signature, {"from": dai_whale}
        )


def test_migrate_vault_permit_too_little(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
    accounts,
):

    ## deposit to the vault after approving
    # whale send tester some money
    userForSignature = Account.create()
    user = accounts.at(userForSignature.address, force=True)
    dai.transfer(user, amount, {"from": dai_whale})
    dai.approve(oldest_vault, 2**256 - 1, {"from": user})
    oldest_vault.deposit(amount, {"from": user})
    vault_shares = oldest_vault.balanceOf(user)

    # check that this works
    from_shares_before = oldest_vault.balanceOf(user)
    to_shares_before = new_vault_dai.balanceOf(user)
    
    # migrate with our permit
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        oldest_vault,
        userForSignature,
        simple_migrator,
        vault_shares - 1,
        oldest_vault.nonces(user),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature
    
    
    with brownie.reverts():
        simple_migrator.migrateAllWithPermit(
            oldest_vault, new_vault_dai, deadline, signature, {"from": user}
        )
    
    from_shares_after = oldest_vault.balanceOf(user)
    to_shares_after = new_vault_dai.balanceOf(user)

    # Check that share where taken from user
    assert from_shares_after == from_shares_before
    # Check that token funds where moved correctly
    assert to_shares_after == to_shares_before


def test_migrate_some(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
):

    ## deposit to the vault after approving
    dai.approve(oldest_vault, 2**256 - 1, {"from": dai_whale})
    oldest_vault.deposit(amount, {"from": dai_whale})
    vault_shares = oldest_vault.balanceOf(dai_whale)

    # check that this works
    from_shares_before = oldest_vault.balanceOf(dai_whale)
    to_shares_before = new_vault_dai.balanceOf(dai_whale)
    oldest_vault.approve(simple_migrator, vault_shares, {"from": dai_whale})
    simple_migrator.migrateShares(oldest_vault, new_vault_dai, vault_shares, {"from": dai_whale})
    from_shares_after = oldest_vault.balanceOf(dai_whale)
    to_shares_after = new_vault_dai.balanceOf(dai_whale)

    # Check that share where taken from user
    assert from_shares_after == from_shares_before - vault_shares
    # Check that token funds where moved correctly
    assert to_shares_after > to_shares_before
    # Check that user can withdraw from new vault
    new_vault_dai.withdraw(
        new_vault_dai.balanceOf(dai_whale), {"from": dai_whale}
    )


def test_migrate_some_permit(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
    accounts,
):

    ## deposit to the vault after approving
    # whale send tester some money
    userForSignature = Account.create()
    user = accounts.at(userForSignature.address, force=True)
    dai.transfer(user, amount, {"from": dai_whale})
    dai.approve(oldest_vault, 2**256 - 1, {"from": user})
    oldest_vault.deposit(amount, {"from": user})
    vault_shares = oldest_vault.balanceOf(user)

    # check that this works
    from_shares_before = oldest_vault.balanceOf(user)
    to_shares_before = new_vault_dai.balanceOf(user)
    
    # migrate with our permit
    deadline = chain[-1].timestamp + 3600
    permit = generate_permit(
        oldest_vault,
        userForSignature,
        simple_migrator,
        vault_shares,
        oldest_vault.nonces(user),
        deadline,
    )
    signature = userForSignature.sign_message(permit).signature
    
    
    simple_migrator.migrateSharesWithPermit(
            oldest_vault, new_vault_dai, vault_shares, deadline, signature, {"from": user}
        )
    
    from_shares_after = oldest_vault.balanceOf(user)
    to_shares_after = new_vault_dai.balanceOf(user)

    # Check that share where taken from user
    assert from_shares_after == from_shares_before - vault_shares
    # Check that token funds where moved correctly
    assert to_shares_after > to_shares_before
    # Check that user can withdraw from new vault
    new_vault_dai.withdraw(
        new_vault_dai.balanceOf(user), {"from": user}
    )


def test_extras(
    gov,
    chain,
    simple_migrator,
    amount,
    dai_whale,
    dai,
    registry,
    oldest_vault,
    old_vault,
    weth,
    new_vault_dai,
    accounts,
):
    # can't migrate to different want
    with brownie.reverts():
        simple_migrator.acceptGovernance({"from": dai_whale})
        
    # can't accept gov that's not pending
    with brownie.reverts():
        simple_migrator.acceptGovernance({"from": dai_whale})
        
    # can't accept gov that's not pending
    with brownie.reverts():
        simple_migrator.acceptGovernance({"from": dai_whale})
        
    # can't set registry if not gov
    with brownie.reverts():
        simple_migrator.setRegistry(registry, {"from": dai_whale})
        
    # can't set registry to zero
    with brownie.reverts():
        simple_migrator.setRegistry(ZERO_ADDRESS, {"from": gov})
        
    # can't set pending gov if not gov
    with brownie.reverts():
        simple_migrator.setPendingGovernance(ZERO_ADDRESS, {"from": dai_whale})
        
    # do things correctly
    simple_migrator.setRegistry(registry, {"from": gov})
    simple_migrator.setPendingGovernance(dai_whale, {"from": gov})
    simple_migrator.acceptGovernance({"from": dai_whale})
    assert simple_migrator.governance() == dai_whale

