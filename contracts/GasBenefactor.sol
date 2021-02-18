// SPDX-License-Identifier: AGPL-3.0
// Copied from https://github.com/b0dhidharma/contract-tools/blob/main/contracts/GasBenefactor.sol

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

import "../interfaces/IChiToken.sol";

interface IGasBenefactor {
    event ChiTokenSet(IChiToken _chiToken);
    event Subsidized(uint256 _amount, address _subsidizor);

    function chiToken() external view returns (IChiToken);

    function setChiToken(IChiToken _chiToken) external;

    function subsidize(uint256 _amount) external;
}

abstract contract GasBenefactor is IGasBenefactor {
    using SafeERC20 for IChiToken;

    IChiToken public override chiToken;

    constructor(IChiToken _chiToken) public {
        _setChiToken(_chiToken);
    }

    modifier subsidizeUserTx {
        uint256 _gasStart = gasleft();
        _;
        // NOTE: Per EIP-2028, gas cost is 16 per (non-empty) byte in calldata
        uint256 _gasSpent =
            21000 + _gasStart - gasleft() + 16 * msg.data.length;
        // NOTE: 41947 is the estimated amount of gas refund realized per CHI redeemed
        // NOTE: 14154 is the estimated cost of the call to `freeFromUpTo`
        chiToken.freeUpTo((_gasSpent + 14154) / 41947);
    }

    modifier discountUserTx {
        uint256 _gasStart = gasleft();
        _;
        // NOTE: Per EIP-2028, gas cost is 16 per (non-empty) byte in calldata
        uint256 _gasSpent =
            21000 + _gasStart - gasleft() + 16 * msg.data.length;
        // NOTE: 41947 is the estimated amount of gas refund realized per CHI redeemed
        // NOTE: 14154 is the estimated cost of the call to `freeFromUpTo`
        chiToken.freeFromUpTo(msg.sender, (_gasSpent + 14154) / 41947);
    }

    function _subsidize(uint256 _amount) internal {
        require(_amount > 0, "GasBenefactor::_subsidize::zero-amount");
        chiToken.safeTransferFrom(msg.sender, address(this), _amount);
        emit Subsidized(_amount, msg.sender);
    }

    function _setChiToken(IChiToken _chiToken) internal {
        require(
            address(_chiToken) != address(0),
            "GasBenefactor::_setChiToken::zero-address"
        );
        chiToken = _chiToken;
        emit ChiTokenSet(_chiToken);
    }
}
