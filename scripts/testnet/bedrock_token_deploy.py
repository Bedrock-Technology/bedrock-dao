from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Command to run this script: 
# holesky: brownie run scripts/testnet/bedrock_token_deploy.py main holesky-owner holesky-deployer --network holesky 
# goerli: brownie run scripts/testnet/bedrock_token_deploy.py main goerli-owner goerli-deployer --network goerli 

shouldPublishSource = True
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer"):
    
    owner = accounts.load(owner)
    deployer = accounts.load(deployer)

    print(f'contract deployer account: {deployer.address}\n')
    print(f'contract owner account: {owner.address}\n')

    """
    Deploy BedrockDAO contract
    """
    token_contract = BedrockDAO.deploy(owner, owner, owner, {'from': deployer}, publish_source=shouldPublishSource)

    print("BR TOKEN ADDRESS:", token_contract.address)
