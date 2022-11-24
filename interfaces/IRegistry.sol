// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

interface IRegistry {
    function latestVault(address token) external view returns (address);

    function endorseVault(address vault) external;

    function newVault(
        address _token,
        address _guardian,
        address _rewards,
        string calldata _name,
        string calldata _symbol,
        uint256 _releaseDelta
    ) external returns (address);
}
