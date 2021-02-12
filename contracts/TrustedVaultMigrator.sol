// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "./VaultMigrator.sol";
import "./Governable.sol";

import "../interfaces/IRegistry.sol";

/**

Based on https://github.com/emilianobonassi/yearn-vaults-swap

 */

interface ITrustedVaultMigrator is IVaultMigrator {
    function registry() external returns (address);

    function sweep(address _token) external;

    function setRegistry(address _registry) external;
}

contract TrustedVaultMigrator is
    VaultMigrator,
    Governable,
    ITrustedVaultMigrator
{
    address public override registry;

    modifier onlyRegisteredVault(address vault) {
        require(
            IRegistry(registry).latestVault(IVaultAPI(vault).token()) == vault,
            "Target vault should be the latest for token"
        );
        _;
    }

    constructor(address _registry)
        public
        VaultMigrator()
        Governable(address(0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52))
    {
        require(_registry != address(0), "Registry cannot be 0");

        registry = _registry;
    }

    function _migrate(
        address vaultFrom,
        address vaultTo,
        uint256 shares
    ) internal override onlyRegisteredVault(vaultTo) {
        super._migrate(vaultFrom, vaultTo, shares);
    }

    function sweep(address _token) external override onlyGovernance {
        IERC20(_token).safeTransfer(
            governance,
            IERC20(_token).balanceOf(address(this))
        );
    }

    // setters
    function setRegistry(address _registry) external override onlyGovernance {
        require(_registry != address(0), "Registry cannot be 0");
        registry = _registry;
    }
}