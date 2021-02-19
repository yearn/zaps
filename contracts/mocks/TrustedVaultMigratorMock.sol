// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "../TrustedVaultMigrator.sol";

contract TrustedVaultMigratorMock is TrustedVaultMigrator {
    constructor(address _registry, IChiToken _chiToken)
        public
        TrustedVaultMigrator(_registry, _chiToken)
    {}

    function internalMigrate(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) external {
        _migrate(vaultFrom, vaultTo, shares);
    }
}
