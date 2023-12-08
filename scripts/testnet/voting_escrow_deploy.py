from brownie import *
from brownie.convert import EthAddress
from brownie.network import priority_fee
from pathlib import Path


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
    Deploy VotingEscrow contract
    """
    ve_contract = VotingEscrow.deploy(
            {'from': deployer})

    ve_proxy = TransparentUpgradeableProxy.deploy(
            ve_contract, deployer, b'',
            {'from': deployer})

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_ve.initialize( "voting-escrow BRT", "veBRT", transparent_token, {'from': owner})

    """
    Deploy VE Rewards contract
    """
    ve_rewards_contract = VeRewards.deploy(
            {'from': deployer})

    ve_rewards_proxy = TransparentUpgradeableProxy.deploy(
            ve_rewards_contract, deployer, b'',
            {'from': deployer})

    transparent_ve_rewards = Contract.from_abi("VeRewards", ve_rewards_proxy.address, VeRewards.abi)
    transparent_ve_rewards.initialize(transparent_ve, transparent_token, {'from': owner})

    # assign REWARDS_MANAGER_ROLE to rewards contract
    transparent_ve.assignRewardsManager(transparent_ve_rewards, {'from': owner})

    print("TOKEN ADDRESS:", transparent_token)
    print("VE ADDRESS:",transparent_ve) 
    print("VE REWARDS ADDRESS:",transparent_ve) 

