// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "../interfaces/IChiToken.sol";

interface ISubsidizer {
    event ChiTokenSet(IChiToken _chiToken);

    function chiToken() external view returns (IChiToken);

    function setChiToken() external;
}

abstract contract Subsidizer is ISubsidizer {
    IChiToken public override chiToken;

    constructor(IChiToken _chiToken) public {
        _setChiToken(_chiToken);
    }

    modifier subsidizeTx {
        uint256 _gasStart = gasleft();
        _;
        // NOTE: Per EIP-2028, gas cost is 16 per (non-empty) byte in calldata
        uint256 _gasSpent =
            21000 + _gasStart - gasleft() + 16 * msg.data.length;
        // NOTE: 41947 is the estimated amount of gas refund realized per CHI redeemed
        // NOTE: 14154 is the estimated cost of the call to `freeFromUpTo`
        chiToken.freeFromUpTo(address(this), (_gasSpent + 14154) / 41947);
    }

    modifier discountTx {
        uint256 _gasStart = gasleft();
        _;
        // NOTE: Per EIP-2028, gas cost is 16 per (non-empty) byte in calldata
        uint256 _gasSpent =
            21000 + _gasStart - gasleft() + 16 * msg.data.length;
        // NOTE: 41947 is the estimated amount of gas refund realized per CHI redeemed
        // NOTE: 14154 is the estimated cost of the call to `freeFromUpTo`
        chiToken.freeFromUpTo(msg.sender, (_gasSpent + 14154) / 41947);
    }

    function _setChiToken(IChiToken _chiToken) internal {
        require(
            address(_chiToken) != address(0),
            "Subsidizer::_setChiToken::zero-address"
        );
        chiToken = _chiToken;
        emit ChiTokenSet(_chiToken);
    }
}
