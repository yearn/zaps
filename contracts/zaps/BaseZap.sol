// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;

import "@openzeppelin/contracts/access/Ownable.sol";
import {
    SafeERC20,
    IERC20
} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "../../../interfaces/yearn/IYVault.sol";

abstract contract BaseZap is Ownable {
    using SafeERC20 for IERC20;

    IERC20 public want;
    IYVault public yVault;

    function updateVaultAddress(address _vault) external onlyOwner {
        yVault = IYVault(_vault);
        want.safeApprove(_vault, uint256(-1));
    }

    function zapEthIn() external payable virtual {
        require(false, "not impented");
    }

    function zapEthIn(uint256 slippageAllowance) external payable virtual {
        require(false, "not impented");
    }

    function zapEthOut(uint256 lpTokenAmount) external virtual {
        require(false, "not impented");
    }

    function zapEthOut(uint256 lpTokenAmount, uint256 slippageAllowance)
        external
        virtual
    {
        require(false, "not impented");
    }
}
