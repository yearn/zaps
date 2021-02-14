pragma solidity ^0.6.12;

import "../../../../interfaces/UniswapInterfaces/IUniswapV2Router02.sol";

import {
    SafeERC20,
    SafeMath,
    IERC20,
    Address
} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

library UniSwapTools {
    using SafeERC20 for IERC20;
    address constant weth = address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    function findBestCoinToSwapIn(
        IUniswapV2Router02 swapService,
        IERC20[] memory coins,
        uint256 amountIn
    ) internal view returns (uint256) {
        uint256 bestOut = 0;
        uint256 bestCoin;
        for (uint256 i = 0; i < coins.length; i++) {
            ERC20 coin = ERC20(address(coins[i]));
            uint256 coinDecimals = coin.decimals();

            address[] memory path = new address[](2);
            path[0] = weth;
            path[1] = address(coin);

            uint256 totalOut =
                swapService.getAmountsOut(amountIn, path)[1] /
                    (10**coinDecimals);
            if (totalOut > bestOut) {
                bestOut = totalOut;
                bestCoin = i;
            }
        }
        return bestCoin;
    }

    function findBestCoinToSwapOut(
        IUniswapV2Router02 swapService,
        IERC20[] memory coins,
        uint256 amountIn
    ) internal view returns (uint256) {
        uint256 bestOut = 0;
        uint256 bestCoin;
        for (uint256 i = 0; i < coins.length; i++) {
            ERC20 coin = ERC20(address(coins[i]));
            uint256 coinDecimals = coin.decimals();

            uint256 amount = amountIn / (10**(18 - coinDecimals));
            address[] memory path = new address[](2);
            path[0] = address(coin);
            path[1] = weth;
            uint256 totalOut = swapService.getAmountsOut(amount, path)[1];
            if (totalOut > bestOut) {
                bestOut = totalOut;
                bestCoin = i;
            }
        }
        return bestCoin;
    }
}

library CurveTools {
    using SafeERC20 for IERC20;

    function prepareCurveAmounts(
        uint256 amount,
        IERC20[2] memory coins,
        uint256 best
    ) internal pure returns (uint256[2] memory) {
        uint256[2] memory amounts;
        for (uint256 i = 0; i < coins.length; i++) {
            amounts[i] = 0;
            if (i == best) {
                amounts[i] = amount;
            }
        }
        return amounts;
    }

    function prepareCurveAmounts(
        uint256 amount,
        IERC20[3] memory coins,
        uint256 best
    ) internal pure returns (uint256[3] memory) {
        uint256[3] memory amounts;
        for (uint256 i = 0; i < coins.length; i++) {
            amounts[i] = 0;
            if (i == best) {
                amounts[i] = amount;
            }
        }
        return amounts;
    }
}
