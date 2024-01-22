from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Commands to run this script:
# holesky:brownie run scripts/testnet/mock_bribe_manager_deploy.py main holesky-owner holesky-deployer --network holesky        
# goerli: brownie run scripts/testnet/mock_bribe_manager_deploy.py main goerli-owner goerli-deployer --network goerli

shouldPublishSource = False
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer"):
    
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy
    
    owner = accounts.load(owner)
    deployer = accounts.load(deployer)

    print(f'contract owner account: {owner.address}\n')

    """
    Deploy Bribe Manager
    """
    mock_bribe_manager_contract = BribeManager.deploy(
        {'from': deployer}, publish_source=shouldPublishSource)

    mock_bribe_manager_proxy = TransparentUpgradeableProxy.deploy(
        mock_bribe_manager_contract, deployer, b'',
        {'from': deployer}, publish_source=shouldPublishSource)
    
    transparent_mock_bribe_manager = Contract.from_abi("BribeManager", mock_bribe_manager_proxy.address, BribeManager.abi)
    transparent_mock_bribe_manager.initialize({'from': owner})

    print("Mocked Bribe Manager at:", transparent_mock_bribe_manager)