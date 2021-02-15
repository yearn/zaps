// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/math/Math.sol";
import "../BaseZap.sol";

import {
    SafeERC20,
    SafeMath,
    IERC20,
    Address
} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

import "../../../../interfaces/UniswapInterfaces/IUniswapV2Router02.sol";

contract ZapYDai is BaseZap {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    IUniswapV2Router02 public swapService =
        IUniswapV2Router02(address(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D));

    address weth = address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    constructor() public Ownable() {
        want = IERC20(address(0x6B175474E89094C44Da98b954EedeAC495271d0F));
        yVault = IYVault(address(0xACd43E627e64355f1861cEC6d3a6688B31a6F952));

        want.safeApprove(address(swapService), uint256(-1));
        want.safeApprove(address(yVault), uint256(-1));
    }

    function zapEthIn() external payable override {
        _zapEthIn();
    }

    receive() external payable {
        _zapEthIn();
    }

    function zapEthOut(uint256 lpTokenAmount) external override {
        _zapOut(lpTokenAmount);
    }

    function _zapEthIn() internal {
        uint256 amountIn = address(this).balance;

        address[] memory path = new address[](2);
        path[0] = weth;
        path[1] = address(want);
        uint256 amount =
            swapService.swapExactETHForTokens{value: amountIn}(
                1,
                path,
                address(this),
                now + 1
            )[1];

        yVault.deposit(amount);
        yVault.transfer(msg.sender, yVault.balanceOf(address(this)));
    }

    function _zapOut(uint256 lpTokenAmount) internal {
        require(
            yVault.balanceOf(msg.sender) >= lpTokenAmount,
            "NOT ENOUGH BALANCE"
        );
        yVault.transferFrom(msg.sender, address(this), lpTokenAmount);
        yVault.withdraw(lpTokenAmount);

        uint256 balance = want.balanceOf(address(this));
        address[] memory path = new address[](2);

        require(balance != 0);

        path[0] = address(want);
        path[1] = weth;
        swapService.swapExactTokensForETH(
            balance,
            1,
            path,
            msg.sender,
            now + 1
        );
    }
}
