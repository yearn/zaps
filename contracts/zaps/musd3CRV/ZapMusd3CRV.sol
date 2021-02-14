// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../../interfaces/curve/Curve.sol";

import "@openzeppelin/contracts/math/Math.sol";
import "../BaseZap.sol";

import {
    SafeERC20,
    SafeMath,
    IERC20,
    Address
} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

import "../../../../interfaces/yearn/IYVault.sol";
import "../../../../interfaces/UniswapInterfaces/IUniswapV2Router02.sol";
import {UniSwapTools, CurveTools} from "../../libraries/ZapLibrary.sol";

contract ZapMusd3CRV is BaseZap {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    ICurveFi public musd3CurvePool =
        ICurveFi(address(0x8474DdbE98F5aA3179B3B3F5942D724aFcdec9f6));
    ICurveFi public threeCurvePool =
        ICurveFi(address(0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7));

    IERC20[2] public musd3Coins;
    IERC20[3] public threeCurveCoins;

    IUniswapV2Router02 public swapService =
        IUniswapV2Router02(address(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D));

    address weth = address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    constructor() public Ownable() {
        want = IERC20(address(0x1AEf73d49Dedc4b1778d0706583995958Dc862e6));
        yVault = IYVault(address(0x0FCDAeDFb8A7DfDa2e9838564c5A1665d856AFDF));

        want.safeApprove(address(yVault), uint256(-1));
        want.safeApprove(address(musd3CurvePool), uint256(-1));

        musd3Coins[0] = IERC20(
            address(0xe2f2a5C287993345a840Db3B0845fbC70f5935a5)
        ); // musd

        musd3Coins[1] = IERC20(
            address(0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)
        ); // 3curv

        threeCurveCoins[0] = IERC20(
            address(0x6B175474E89094C44Da98b954EedeAC495271d0F)
        ); // dai
        threeCurveCoins[1] = IERC20(
            address(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48)
        ); // usdc
        threeCurveCoins[2] = IERC20(
            address(0xdAC17F958D2ee523a2206206994597C13D831ec7)
        ); // usdt

        for (uint256 i = 0; i < musd3Coins.length; i++) {
            musd3Coins[i].safeApprove(address(musd3CurvePool), uint256(-1));
        }

        musd3Coins[0].safeApprove(address(swapService), uint256(-1));
        for (uint256 i = 0; i < threeCurveCoins.length; i++) {
            threeCurveCoins[i].safeApprove(
                address(threeCurvePool),
                uint256(-1)
            );
            threeCurveCoins[i].safeApprove(address(swapService), uint256(-1));
        }
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

        IERC20[] memory coins = new IERC20[](4);

        coins[0] = threeCurveCoins[0];
        coins[1] = threeCurveCoins[1];
        coins[2] = threeCurveCoins[2];
        coins[3] = musd3Coins[0];
        uint256 best =
            UniSwapTools.findBestCoinToSwapIn(swapService, coins, amountIn);

        address[] memory path = new address[](2);
        path[0] = weth;
        path[1] = address(coins[best]);
        uint256 amount =
            swapService.swapExactETHForTokens{value: amountIn}(
                1,
                path,
                address(this),
                now + 1
            )[1];

        if (best == 3) {
            uint256[2] memory curveAmounts = [amount, 0];
            musd3CurvePool.add_liquidity(curveAmounts, 1);
        } else {
            assert(amount != 0);

            uint256[3] memory threeCurveAmounts =
                CurveTools.prepareCurveAmounts(amount, threeCurveCoins, best);

            threeCurvePool.add_liquidity(threeCurveAmounts, 1);
            uint256 threeCurveBalance = musd3Coins[1].balanceOf(address(this));
            assert(threeCurveBalance != 0);
            uint256[2] memory curveAmounts = [0, threeCurveBalance];

            musd3CurvePool.add_liquidity(curveAmounts, 1);
        }

        uint256 amountToDeposit = want.balanceOf(address(this));
        yVault.depositAll();
        yVault.transfer(msg.sender, yVault.balanceOf(address(this)));
    }

    function _zapOut(uint256 lpTokenAmount) internal {
        require(
            yVault.balanceOf(msg.sender) >= lpTokenAmount,
            "NOT ENOUGH BALANCE"
        );
        yVault.transferFrom(msg.sender, address(this), lpTokenAmount);
        yVault.withdrawAll();

        uint256 balance = want.balanceOf(address(this));
        require(balance > 0, "no balance");

        IERC20[] memory coins = new IERC20[](4);

        coins[0] = threeCurveCoins[0];
        coins[1] = threeCurveCoins[1];
        coins[2] = threeCurveCoins[2];
        coins[3] = musd3Coins[0];
        uint256 best =
            UniSwapTools.findBestCoinToSwapOut(swapService, coins, balance);

        if (best == 3) {
            musd3CurvePool.remove_liquidity_one_coin(balance, 0, 1);
        } else {
            musd3CurvePool.remove_liquidity_one_coin(balance, 1, 1);
            balance = musd3Coins[1].balanceOf(address(this));
            threeCurvePool.remove_liquidity_one_coin(balance, int128(best), 1);
        }

        balance = coins[best].balanceOf(address(this));
        address[] memory path = new address[](2);

        path[0] = address(coins[best]);
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