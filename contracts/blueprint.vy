# @version 0.3.4

MAX_BYTES: constant(uint256) = 1
TARGET: immutable(address)
FACTORY: immutable(address)

interface IFactory:
    def impl_map(_id: uint256) -> address: view

@nonpayable
@external
def __init__(_id: uint256):
    FACTORY = msg.sender
    TARGET = IFactory(FACTORY).impl_map(_id)

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
        value=msg.value,
        max_outsize = MAX_BYTES,
        is_delegate_call=True,
        revert_on_failure=False,
    )
    assert success

@nonpayable
@external
def destroy():
    assert msg.sender == FACTORY
    selfdestruct(msg.sender)
