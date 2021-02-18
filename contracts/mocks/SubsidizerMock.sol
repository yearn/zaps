// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "../Subsidizer.sol";

contract SubsidizerMock is Subsidizer {
    constructor(IChiToken _chiToken) public Subsidizer(_chiToken) {}

    function trySubsidizeTx() public subsidizeUserTx {}

    function tryDiscountTx() public discountUserTx {}

    function setChiToken(IChiToken _chiToken) public override {
        _setChiToken(_chiToken);
    }
}
