// SPDX-License-Identifier: MIT
pragma solidity ^0.6.2;

interface MStable {
    function mint(address, uint256) external;

    function redeem(address, uint256) external;
}

interface mSavings {
    function depositSavings(uint256) external;

    function creditBalances(address) external view returns (uint256);

    function redeem(uint256) external;

    function exchangeRate() external view returns (uint256);
}
