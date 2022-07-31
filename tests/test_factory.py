import pytest
import scripts.blueprint_helper
import brownie
from brownie import (
    factory as Factory, 
    factory_single as FactorySingle, 
    mock1 as Mock1,
    mock2 as Mock2,
    accounts,
    chain,
    Contract,
)

@pytest.fixture
def mock1():
    m1 = Mock1.deploy({"from": accounts[0]})
    return m1

@pytest.fixture
def mock2():
    m2 = Mock2.deploy({"from": accounts[0]})
    return m2

@pytest.fixture
def blueprint():
    init_bc = scripts.blueprint_helper.get_blueprint_init()
    bp_addr = accounts[2].get_deployment_address()
    _ = accounts[2].transfer(data=init_bc)
    bp = Contract.from_abi("blueprint", bp_addr, Mock1.abi)
    return bp

@pytest.fixture
def blueprint_single():
    init_bc = scripts.blueprint_helper.get_blueprint_single_init()
    bp_addr = accounts[2].get_deployment_address()
    _ = accounts[2].transfer(data=init_bc)
    bp = Contract.from_abi("blueprint", bp_addr, Mock1.abi)
    return bp

def test_factory_single(blueprint_single, mock1, mock2):
    # Deploy factory.
    factory_single = FactorySingle.deploy(blueprint_single.address, {"from": accounts[0]})

    # Set salt.
    salt = "0x69"
    factory_single.set_salt(salt)

    # Set implementatin address.
    factory_single.set_impl(mock1.address, {"from": accounts[0]})

    # Deploy proxy.
    tx = factory_single.deploy_proxy({"from": accounts[0]})
    proxy_address = tx.return_value
    mock1_proxy = Contract.from_abi("Mock 1 Proxy", proxy_address, Mock1.abi)

    mock1_proxy_bytecode = mock1_proxy.bytecode

    # Test create2 collision
    with brownie.reverts():
        factory_single.set_impl(mock2.address)
        factory_single.deploy_proxy()

    # Destroy proxy before we can re-deplpy.
    original_bytecode = mock1_proxy.bytecode
    factory_single.destroy_proxy({"from": accounts[0]})

    # Re-initialize.
    factory_single.set_impl(mock2.address, {"from": accounts[0]})
    tx = factory_single.deploy_proxy()
    proxy_address_2 = tx.return_value
    mock2_proxy = Contract.from_abi("Mock 2 Proxy", proxy_address_2, Mock2.abi)

    # Confirm same address.
    assert mock1_proxy.address == mock2_proxy.address

    # Confirm the runtime bytecode at the proxy address is different.
    mock2_proxy_bytecode = mock2_proxy.bytecode
    assert mock1_proxy_bytecode != mock2_proxy_bytecode

    # Reset the chain for later tests.
    chain.reset()

def test_factory(blueprint, mock1, mock2):
    # Deploy factory.
    factory = Factory.deploy(blueprint.address, {"from": accounts[0]})

    # Set salts.
    salt_1 = "0x69"
    salt_2 = "0x1337"
    id_1 = 0
    id_2 = 1
    factory.set_salt(id_1, salt_1)
    factory.set_salt(id_2, salt_2)

    # Set implementatin addresses.
    factory.set_impl(id_1, mock1.address, {"from": accounts[0]})
    factory.set_impl(id_2, mock2.address, {"from": accounts[0]})

    # Deploy proxy id_1.
    tx = factory.deploy_proxy(id_1, {"from": accounts[0]})
    proxy_address = tx.return_value
    mock1_proxy = Contract.from_abi("Mock 1 Proxy", proxy_address, Mock1.abi)
    mock1_proxy_bytecode = mock1_proxy.bytecode

    # Deploy proxy id_2.
    tx = factory.deploy_proxy(id_2, {"from": accounts[0]})
    proxy_address = tx.return_value
    mock2_proxy = Contract.from_abi("Mock 2 Proxy", proxy_address, Mock2.abi)
    mock2_proxy_bytecode = mock2_proxy.bytecode

    # Destroy proxy before we can re-deplpy.
    factory.destroy_proxy(id_1, {"from": accounts[0]})

    # Re-initialize.  Test by deploying Mock2 proxy at id=0.
    factory.set_impl(id_1, mock2.address, {"from": accounts[0]})
    tx = factory.deploy_proxy(id_1)
    proxy_address_2 = tx.return_value
    mock2_proxy_2 = Contract.from_abi("Mock 2 Proxy 2", proxy_address_2, Mock2.abi)

    # Confirm same address and different runtime bytecode.
    assert mock1_proxy.address == mock2_proxy_2.address
    assert mock1_proxy.bytecode != mock2_proxy_2.bytecode

    # Confirm both mock2 proxies have the same runtime bytecode.
    assert mock2_proxy.address != mock2_proxy_2.address
    assert mock2_proxy.bytecode == mock2_proxy_2.bytecode

    # Test create2 collision
    with brownie.reverts():
        factory.set_impl(id_2, mock1.address)
        factory.deploy_proxy(id_2)

    # Reset the chain for later tests.
    chain.reset()

def test_proxy_revert(blueprint, mock1):
    # Deploy factory.
    factory = Factory.deploy(blueprint.address, {"from": accounts[0]})

    # Set salt.
    salt_1 = "0x69"
    id_1 = 0
    factory.set_salt(id_1, salt_1)

    # Set implementatin address.
    factory.set_impl(id_1, mock1.address, {"from": accounts[0]})

    # Deploy proxy id_1.
    tx = factory.deploy_proxy(id_1, {"from": accounts[0]})
    proxy_address = tx.return_value
    mock1_proxy = Contract.from_abi("Mock 1 Proxy", proxy_address, Mock1.abi)

    # Test revert in implementation
    #with brownie.reverts("Mock 1 test revert msg."):
    with brownie.reverts():
        mock1_proxy.test_revert({"from": accounts[0]})

    # Reset the chain for later tests.
    chain.reset()
