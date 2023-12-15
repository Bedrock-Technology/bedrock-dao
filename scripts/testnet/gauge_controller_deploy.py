from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Commands to run this script:
# holesky:brownie run scripts/testnet/gauge_controller_deploy.py main holesky-owner holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/testnet/gauge_controller_deploy.py main goerli-owner goerli-deployer goerli --network goerli

dep_contracts = {
    "holesky": {
        "ve": "0x19A84Cb4f25b95990F0B25b15694349Ee1cCc282"
    }, 
    "goerli": {
        "ve": "0x19Cd39eC64d3AbbcF9A448175400cDDbA97B9f56"
    }
}

shouldPublishSource = False
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer", dep_network="holesky"):
    
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy
    
    owner = accounts.load(owner)
    deployer = accounts.load(deployer)

    print(f'contract owner account: {owner.address}\n')
    print(f'contract deployer account: {deployer.address}\n')
    
    """
    Testnet Voting Escrow Contract
    """
    ve_proxy = TransparentUpgradeableProxy.at(
        dep_contracts[dep_network]["ve"])
    
    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)

    """
    Deploy Gauge Controller
    """

    gauge_contract = GaugeController.deploy({'from': deployer}, publish_source=shouldPublishSource)

    gauge_proxy = TransparentUpgradeableProxy.deploy(
        gauge_contract, deployer, b'',{'from': deployer}, publish_source=shouldPublishSource)

    transparent_gauge= Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)
    transparent_gauge.initialize(transparent_ve, {'from': owner})

    print("Gauge Controller:", transparent_gauge)
