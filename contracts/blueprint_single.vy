# @version 0.3.4

MAX_BYTES: constant(uint256) = 1
TARGET: immutable(address)
FACTORY_SINGLE: immutable(address)

interface IFactorySingle:
    def impl() -> address: view

@nonpayable
@external
def __init__():
    FACTORY_SINGLE = msg.sender
    TARGET = IFactorySingle(FACTORY_SINGLE).impl()
    return

@payable
@external
def __default__():
    # Simple transfer.
    if len(msg.data) == 0:
        return

    # Delegate call to implementation.
    # NOTE: We need to manually catch a revert here.
    #       revert_on_failure=True does not behave as expected.
    # TODO: Investigate and file an issue with Vyper.
    success: bool = False
    response: Bytes[MAX_BYTES] = b""
    success, response = raw_call(
        TARGET,
        msg.data,
        max_outsize=MAX_BYTES,
        value=msg.value,
        is_delegate_call=True,
        revert_on_failure=False,
    )
    assert success

@nonpayable
@external
def destroy():
    assert msg.sender == FACTORY_SINGLE
    selfdestruct(msg.sender)
