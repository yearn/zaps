// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "../VaultMigrator.sol";

contract VaultMigratorMock is VaultMigrator {
    constructor() public {}

    function internalPermit(
        address vault,
        uint256 value,
        uint256 deadline,
        bytes calldata signature
    ) internal {
        _permit(vault, value, deadline, signature);
    }

    function internalMigrate(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) external {
        _migrate(vaultFrom, vaultTo, shares);
    }
}
