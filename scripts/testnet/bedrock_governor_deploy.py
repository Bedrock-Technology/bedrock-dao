from brownie import *
from brownie.convert import EthAddress
from brownie.network import priority_fee
from pathlib import Path

shouldPublishSource = False # for holesky
priority_fee("80 gwei")
def main():
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    owner = accounts.load('holesky-owner')
    deployer = accounts.load('holesky-deploy')

    print(f'contract owner account: {owner.address}\n')
    
    """
    Testnet BRT Contract
    """
    token_proxy = TransparentUpgradeableProxy.at(
        "0x91493342f273BCDc28a4f2BE4b0BF7Bd1c334c20")
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    
    """
    Testnet Voting Escrow Contract
    """
    ve_proxy = TransparentUpgradeableProxy.at(
        "0x19A84Cb4f25b95990F0B25b15694349Ee1cCc282")
    
    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)

    """
    Deploy BedrockGovernor contract
    """
    govern_contract = BedrockGovernor.deploy(
            {'from': deployer}, publish_source=shouldPublishSource)

    govern_proxy = TransparentUpgradeableProxy.deploy(
            govern_contract, deployer, b'',
            {'from': deployer}, publish_source=shouldPublishSource)

    timelock = TimeLock.deploy(
            86400*1,
            [govern_proxy.address],
            ["0x0000000000000000000000000000000000000000"],
            owner,
            {'from': owner})

    transparent_govern = Contract.from_abi("BedrockGovernor", govern_proxy.address, BedrockGovernor.abi)
    transparent_govern.initialize(transparent_ve, timelock, {'from': owner})

    print("GOVERN ADDRESS:", transparent_govern)
    print("TIMELOCK ADDRESS:", timelock)
