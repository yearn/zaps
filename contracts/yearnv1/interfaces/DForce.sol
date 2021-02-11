// SPDX-License-Identifier: MIT
pragma solidity ^0.6.2;

interface dRewards {
    function withdraw(uint256) external;

    function getReward() external;

    function stake(uint256) external;

    function balanceOf(address) external view returns (uint256);

    function exit() external;
}

interface dERC20 {
    function mint(address, uint256) external;

    function redeem(address, uint256) external;

    function getTokenBalance(address) external view returns (uint256);

    function getExchangeRate() external view returns (uint256);
}
