# @version ^0.3.4

salt_map: public(HashMap[uint256, bytes32])
impl_map: public(HashMap[uint256, address])
proxy_map: public(HashMap[uint256, address])

BLUEPRINT: immutable(address)
OWNER: immutable(address)

interface IProxy:
    def destroy(): nonpayable

@nonpayable
@external
def __init__(_blueprint: address):
    BLUEPRINT = _blueprint
    OWNER = msg.sender

@payable
@external
def __default__():
    return

@nonpayable
@external
def set_salt(_id: uint256, _salt: bytes32):
    assert msg.sender == OWNER, "unauthorized"
    self.salt_map[_id] = _salt

@nonpayable
@external
def set_impl(_id: uint256, _impl: address):
    assert msg.sender == OWNER, "unauthorized"
    self.impl_map[_id] = _impl

@nonpayable
@external
def deploy_proxy(_id: uint256) -> address:
    assert msg.sender == OWNER, "unauthorized"
    salt: bytes32 = self.salt_map[_id]
    proxy: address = create_from_blueprint(BLUEPRINT, _id, code_offset=0, salt=salt)
    self.proxy_map[_id] = proxy
    return proxy

@nonpayable
@external
def destroy_proxy(_id: uint256):
    assert msg.sender == OWNER, "unauthorized"
    paddr: address = self.proxy_map[_id]
    IProxy(paddr).destroy()
