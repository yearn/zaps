# @version ^0.3.3

interface Vault():
    def deposit(amount: uint256, recipient: address) -> uint256: nonpayable
    def withdraw(maxShares: uint256) -> uint256: nonpayable
    def transferFrom(_from : address, _to : address, _value : uint256) -> bool: nonpayable
    def token() -> address: nonpayable

interface WEth(ERC20):
    def deposit(): payable
    def approve(_spender : address, _value : uint256) -> bool: nonpayable
    def withdraw(amount: uint256): nonpayable

VAULT: immutable(Vault)
WETH: immutable(WEth)

@external
def __init__(vault: address):
    weth: address = Vault(vault).token()
    VAULT = Vault(vault)
    WETH = WEth(weth)
    WEth(weth).approve(vault, MAX_UINT256)

@external
@payable
def deposit():
    assert  msg.value != 0 #dev: "!value"
    WETH.deposit(value= msg.value)
    VAULT.deposit( msg.value, msg.sender)

@external
@nonpayable
def withdraw(amount: uint256):
    VAULT.transferFrom(msg.sender, self, amount)
    weth_amount: uint256 = VAULT.withdraw(amount)
    assert amount != 0 #dev: "!amount"
    WETH.withdraw(weth_amount)
    send(msg.sender, weth_amount)

@external
@payable
def __default__():
    return