import brownie
import pytest
from brownie import chain, web3, Wei

def test_deploy_chi_token_zero(
    SubsidizerMock,
    accounts
):
    with brownie.reverts("Subsidizer::_setChiToken::zero-address"):
        accounts[0].deploy(
            SubsidizerMock,
            "0x0000000000000000000000000000000000000000"
        )

def test_set_chi_token_zero(
  subsidizerMock,
):
    with brownie.reverts("Subsidizer::_setChiToken::zero-address"):
        subsidizerMock.setChiToken("0x0000000000000000000000000000000000000000")

def test_set_chi_token(
    subsidizerMock
):
    txSetChiToken = subsidizerMock.setChiToken("0x0000000000000000000000000000000000000001")
    assert "ChiTokenSet" in txSetChiToken.events