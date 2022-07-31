# @version ^0.3.4

@nonpayable
@external
def __init__():
    return

@view
@external
def version() -> uint256:
    return 1

@nonpayable
@external
def test_revert():
    assert False, "Mock1 test revert msg."

@payable
@external
def __default__():
    return
