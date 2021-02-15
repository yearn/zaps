// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

interface IYVault is IERC20 {
    function deposit(uint256 amount, address recipient) external;

    function deposit(uint256 amount) external;

    function depositAll() external;

    function withdraw(uint256 amount) external;

    function withdraw() external;

    function withdrawAll() external;
}
