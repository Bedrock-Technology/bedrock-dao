from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Commands to run this script:
# holesky:brownie run scripts/testnet/voting_escrow_deploy.py main holesky-owner holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/testnet/voting_escrow_deploy.py main goerli-owner goerli-deployer goerli --network goerli

dep_contracts = {
    "holesky": {
        "token": "0x91493342f273BCDc28a4f2BE4b0BF7Bd1c334c20"
    }, 
    "goerli": {
        "token": "0x07881e8Ac6cAF3C3082227218E94b3D7ffE201fD"
    }
}

shouldPublishSource = True
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer", dep_network="holesky"):
    
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    owner = accounts.load(owner)
    deployer = accounts.load(deployer)

    print(f'contract owner account: {owner.address}\n')
    print(f'contract deployer account: {deployer.address}\n')
    
    """
    Testnet BRT Contract
    """
    token_proxy = TransparentUpgradeableProxy.at(dep_contracts[dep_network]["token"])
    
    transparent_token = Contract.from_abi(
        "BedrockDAO", token_proxy.address, BedrockDAO.abi)

    """
    Deploy VotingEscrow contract
    """
    ve_contract = VotingEscrow.deploy(
            {'from': deployer}, publish_source=shouldPublishSource)

    ve_proxy = TransparentUpgradeableProxy.deploy(
            ve_contract, deployer, b'',
            {'from': deployer}, publish_source=shouldPublishSource)

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_ve.initialize( "voting-escrow BRT", "veBRT", transparent_token, {'from': owner})

    """
    Deploy VE Rewards contract
    """
    ve_rewards_contract = VeRewards.deploy(
            {'from': deployer}, publish_source=shouldPublishSource)

    ve_rewards_proxy = TransparentUpgradeableProxy.deploy(
            ve_rewards_contract, deployer, b'',
            {'from': deployer}, publish_source=shouldPublishSource)

    transparent_ve_rewards = Contract.from_abi("VeRewards", ve_rewards_proxy.address, VeRewards.abi)
    transparent_ve_rewards.initialize(transparent_ve, transparent_token, {'from': owner})

    # assign REWARDS_MANAGER_ROLE to rewards contract
    transparent_ve.assignRewardsManager(transparent_ve_rewards, {'from': owner})

    print("TOKEN ADDRESS:", transparent_token)
    print("VE ADDRESS:",transparent_ve) 
    print("VE REWARDS ADDRESS:",transparent_ve_rewards) 

