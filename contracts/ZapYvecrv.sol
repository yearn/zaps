// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import {Math} from "@openzeppelin/contracts/math/Math.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {
    SafeERC20,
    SafeMath,
    IERC20,
    Address
} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

interface IYVault is IERC20 {
    function deposit(uint256 amount, address recipient) external;

    function withdraw() external;

    function pricePerShare() external view returns (uint256);
}

interface ICurveFi {
    function add_liquidity(uint256[2] calldata amounts, uint256 min_mint_amount)
        external
        payable;

    function remove_liquidity_one_coin(
        uint256 _token_amount,
        int128 i,
        uint256 min_amount
    ) external;
}

contract ZapYvecrv is Ownable {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    IYVault public yVault =
        IYVault(address(0x0e880118C29F095143dDA28e64d95333A9e75A47));
    ICurveFi public CurveStableSwap =
        ICurveFi(address(0xc5424B857f758E906013F3555Dad202e4bdB4567)); // Curve ETH/sETH StableSwap pool contract

    IERC20 public want =
        IERC20(address(0xA3D87FffcE63B53E0d54fAa1cc983B7eB0b74A9c)); // Curve.fi ETH/sETH (eCRV)

    uint256 public constant DEFAULT_SLIPPAGE = 200; // slippage allowance out of 10000: 2%
    bool private _noReentry = false;

    constructor() public Ownable() {
        want.safeApprove(address(yVault), uint256(-1));
        want.safeApprove(address(CurveStableSwap), uint256(-1));
    }

    // Accept ETH and zap in with no token swap
    receive() external payable {
        if (_noReentry) {
            return;
        }
        _zapIn(0);
    }

    //
    // Zap In
    //

    function zapIn(uint256 slippageAllowance) external payable {
        if (_noReentry) {
            return;
        }
        if (slippageAllowance == 0) {
            slippageAllowance = DEFAULT_SLIPPAGE;
        }
        _zapIn(slippageAllowance);
    }

    function _zapIn(uint256 slippageAllowance) internal {
        uint256 ethDeposit = address(this).balance;
        require(ethDeposit > 1, "INSUFFICIENT ETH DEPOSIT");

        CurveStableSwap.add_liquidity{value: ethDeposit}([ethDeposit, 0], 0);

        uint256 outAmount = want.balanceOf(address(this));
        require(
            outAmount.mul(slippageAllowance.add(10000)).div(10000) >=
                ethDeposit,
            "TOO MUCH SLIPPAGE"
        );

        yVault.deposit(outAmount, msg.sender);
    }

    //
    // Zap Out
    //

    function zapOut(uint256 yvTokenAmount, uint256 slippageAllowance) external {
        uint256 yvTokenWithdrawl =
            Math.min(yvTokenAmount, yVault.balanceOf(msg.sender));
        require(yvTokenWithdrawl > 0, "INSUFFICIENT FUNDS");

        yVault.transferFrom(msg.sender, address(this), yvTokenWithdrawl);
        yVault.withdraw();
        uint256 wantBalance = want.balanceOf(address(this));

        _noReentry = true;
        CurveStableSwap.remove_liquidity_one_coin(wantBalance, 0, 0);
        _noReentry = false;

        uint256 ethBalance = address(this).balance;
        msg.sender.transfer(ethBalance);

        require(
            ethBalance.mul(slippageAllowance.add(10000)).div(10000) >=
                wantBalance,
            "TOO MUCH SLIPPAGE"
        );

        uint256 leftover = yVault.balanceOf(address(this));
        if (leftover > 0) {
            yVault.transfer(msg.sender, leftover);
        }
    }

    //
    // Misc external functions
    //

    //There should never be any tokens in this contract
    function rescueTokens(address token, uint256 amount) external onlyOwner {
        if (token == address(0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE)) {
            amount = Math.min(address(this).balance, amount);
            msg.sender.transfer(amount);
        } else {
            IERC20 want = IERC20(token);
            amount = Math.min(want.balanceOf(address(this)), amount);
            want.safeTransfer(msg.sender, amount);
        }
    }

    function updateVaultAddress(address _vault) external onlyOwner {
        yVault = IYVault(_vault);
        want.safeApprove(_vault, uint256(-1));
    }
}
