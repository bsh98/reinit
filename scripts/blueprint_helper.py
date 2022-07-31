from brownie import (
    blueprint as Blueprint, 
    blueprint_single as BlueprintSingle, 
)

def _get_init(_raw_bytecode: str):
    """
    @source https://github.com/vyperlang/vyper/blob/2adc34ffd3bee8b6dee90f552bbd9bb844509e19/tests/base_conftest.py#L130-L160
    """
    bytecode = _raw_bytecode
    bytecode_len = (len(bytecode) - 2) // 2
    bytecode_len_hex = hex(bytecode_len)[2:].rjust(4, "0")
    # prepend a quick deploy preamble
    deploy_preamble = "61" + bytecode_len_hex + "3d81600a3d39f3"
    deploy_bytecode = "0x" + deploy_preamble + bytecode[2:]
    return deploy_bytecode

def get_blueprint_single_init():
    raw_bytecode = BlueprintSingle.bytecode
    bytecode = _get_init(raw_bytecode)
    print(bytecode)
    return bytecode

def get_blueprint_init():
    raw_bytecode = Blueprint.bytecode
    bytecode = _get_init(raw_bytecode)
    print(bytecode)
    return bytecode
