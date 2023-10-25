from brownie import *
from brownie.convert import EthAddress
from brownie.network import priority_fee
from pathlib import Path

import time
import pytest

shouldPublishSource = True
priority_fee("80 gwei")

def main():
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    owner = accounts.load('holesky-owner')
    deployer = accounts.load('holesky-deployer')

    print(f'contract owner account: {owner.address}\n')

    """
    Deploy BedrockDAO contract
    """
    token_contract = BedrockDAO.deploy(
            {'from': deployer})

    token_proxy =  TransparentUpgradeableProxy.deploy(
            token_contract, deployer, b'',
            {'from': deployer})
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    transparent_token.initialize(owner, {'from': owner})


    """
    Deploy VotingEscrow contract
    """
    ve_contract = VotingEscrow.deploy(
            {'from': deployer}, publish_source=shouldPublishSource)

    ve_proxy =  TransparentUpgradeableProxy.deploy(
            ve_contract, deployer, b'',
            {'from': deployer}, publish_source=shouldPublishSource)

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_ve.initialize( "voting-escrow BRT", "veBRT", transparent_token, {'from': owner})

#     """
#     Deploy BedrockGovernor contract
#     """
#     govern_contract = BedrockGovernor.deploy(
#             {'from': deployer}, publish_source=shouldPublishSource)

#     govern_proxy = TransparentUpgradeableProxy.deploy(
#             govern_contract, deployer, b'',
#             {'from': deployer}, publish_source=shouldPublishSource)

#     timelock = TimeLock.deploy(
#             86400*1,
#             [govern_proxy.address],
#             ["0x0000000000000000000000000000000000000000"],
#             owner,
#             {'from': owner})

#     transparent_govern = Contract.from_abi("BedrockGovernor", govern_proxy.address, BedrockGovernor.abi)
#     transparent_govern.initialize(transparent_ve, timelock, {'from': owner})

    print("TOKEN ADDRESS:", transparent_token)
    print("VE ADDRESS:",transparent_ve) 
#     print("GOVERN ADDRESS:", transparent_govern)
#     print("TIMELOCK ADDRESS:", timelock)
