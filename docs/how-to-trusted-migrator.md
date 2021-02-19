# Guide to using Trusted Migrator for Yearn Vaults

## Description

[TrustedMigrator](https://etherscan.io/address/0x1824df8D751704FA10FA371d62A37f9B8772ab90) is a useful contract to migrate between legacy v1 Yearn Vaults to v2 Yearn Vaults. It also supports v2 Vaults migration to latest release as long as vaults have the same underlying want token.

Migrator uses registry `v2.registry.ychad.eth` to always migrate to latest release vault in V2

## How does it work for the User

Let's say Alice holds 100 yDAI in v1 (`vaultFrom`) vault and wants to migrate to latest v2 yDAI vault (`vaultTo`).

For this Alice needs to `vaultFrom.approve(migrator.address, 100)`.

Then Alice will call the Migrator Contract e.g `migrator.migrateAll(yvDAIv1.address, yvDAIv2.address)` or `migrateShares(yvDAIv1.address, yvDAIv2.address, 100)`.

Migrator will withdraw the allowed amount of Alice shares on the v1 vault and deposit Alice's converted shares in DAI into the v2 vault.

Alice should have less balance (or zero balance in case of calling migrateAll) of shares in the initial v1 vault and balance available in the v2 Vault under her wallet address.

## ABI to integrate

To generate ABI after cloning the repo and configuring brownie setup following the main [readme file](README.md), you can run:

`brownie compile`

The ABI should be available at `build/contracts/TrustedVaultMigrator.json`
