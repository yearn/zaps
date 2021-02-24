// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";

import "../interfaces/IVaultAPI.sol";

interface WETH {
    function deposit() external payable;
}

contract ZapYvWETH {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    address public constant weth =
        address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    address public constant yvWETH =
        address(0xa9fE4601811213c340e850ea305481afF02f5b28);

    constructor() public {
        // Setup approvals
        IERC20(weth).safeApprove(yvWETH, uint256(-1));
    }

    receive() external payable {
        depositETH();
    }

    function depositETH() public payable {
        WETH(weth).deposit{value: msg.value}();
        uint256 _amount = IERC20(weth).balanceOf(address(this));
        IVaultAPI vault = IVaultAPI(yvWETH);

        IVaultAPI(vault).deposit(_amount, msg.sender);
    }
}
