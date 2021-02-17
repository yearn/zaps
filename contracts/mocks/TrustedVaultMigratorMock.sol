// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "../TrustedVaultMigrator.sol";

contract TrustedVaultMigratorMock is TrustedVaultMigrator {
    constructor(address _registry) public TrustedVaultMigrator(_registry) {}

    function internalMigrate(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) external {
        _migrate(vaultFrom, vaultTo, shares);
    }
}
