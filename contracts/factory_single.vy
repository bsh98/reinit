# @version ^0.3.4

salt: public(bytes32)
impl: public(address)
proxy: public(address)

BLUEPRINT_SINGLE: immutable(address)
OWNER: immutable(address)

interface IProxy:
    def destroy(): nonpayable

@nonpayable
@external
def __init__(_blueprint_single: address):
    BLUEPRINT_SINGLE = _blueprint_single
    OWNER = msg.sender

@payable
@external
def __default__():
    return

@nonpayable
@external
def set_salt(_salt: bytes32):
    assert msg.sender == OWNER, "unauthorized"
    self.salt = _salt

@nonpayable
@external
def set_impl(_impl: address):
    assert msg.sender == OWNER, "unauthorized"
    self.impl = _impl

@nonpayable
@external
def deploy_proxy() -> address:
    assert msg.sender == OWNER, "unauthorized"
    proxy: address = create_from_blueprint(BLUEPRINT_SINGLE, code_offset=0, salt=self.salt)
    self.proxy = proxy
    return proxy

@nonpayable
@external
def destroy_proxy():
    assert msg.sender == OWNER, "unauthorized"
    IProxy(self.proxy).destroy()
