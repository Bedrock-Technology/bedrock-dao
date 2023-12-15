from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Command to run this script: 
# holesky: brownie run scripts/testnet/bedrock_token_deploy.py main holesky-owner holesky-deployer --network holesky 
# goerli: brownie run scripts/testnet/bedrock_token_deploy.py main goerli-owner goerli-deployer --network goerli 

shouldPublishSource = True
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer"):
    
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    owner = accounts.load(owner)
    deployer = accounts.load(deployer)

    print(f'contract deployer account: {deployer.address}\n')
    print(f'contract owner account: {owner.address}\n')

    """
    Deploy BedrockDAO contract
    """
    token_contract = BedrockDAO.deploy(
            {'from': deployer}, publish_source=shouldPublishSource)

    token_proxy = TransparentUpgradeableProxy.deploy(
            token_contract, deployer, b'',
            {'from': deployer}, publish_source=shouldPublishSource)
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    transparent_token.initialize({'from': owner})

    print("BRT TOKEN ADDRESS:", transparent_token)
