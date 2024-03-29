from brownie import *
from brownie.convert import EthAddress
from pathlib import Path

import time
import pytest

def get_week(n=0):
    WEEK = 604800
    this_week = (chain.time() // WEEK) * WEEK
    return this_week + (n * WEEK)

# this script simulates voters locks to get veToken
# get rewards based on their ve balance
def main():
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    owner = accounts[0]
    deployer = accounts[1]
    voters = [accounts[2],accounts[3]]

    print(f'contract owner account: {owner.address}\n')

    token_contract = BedrockDAO.deploy(owner, owner, owner, {'from': deployer})
    
    ve_contract = VotingEscrow.deploy(
            {'from': deployer})

    ve_proxy =  TransparentUpgradeableProxy.deploy(
            ve_contract, deployer, b'',
            {'from': deployer})

    ve_rewards_contract = VeRewards.deploy(
            {'from': deployer})

    ve_rewards_proxy = TransparentUpgradeableProxy.deploy(
            ve_rewards_contract, deployer, b'',
            {'from': deployer})

    print("BRT ADDRESS:", token_contract)

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_ve.initialize( "voting-escrow BRT", "veBRT", token_contract, {'from': owner})

    print("VE ADDRESS:", transparent_ve)

    transparent_ve_rewards = Contract.from_abi("VeRewards", ve_rewards_proxy.address, VeRewards.abi)
    transparent_ve_rewards.initialize(transparent_ve, token_contract, {'from': owner})

    # assign REWARDS_MANAGER_ROLE to rewards contract
    transparent_ve.assignRewardsManager(transparent_ve_rewards, {'from': owner})

    print("VE REWARDS ADDRESS:", transparent_ve_rewards)

    for voter in voters: 
        print("minting BRT token to: ", voter)
        token_contract.mint(voter, 100 * 1e18, {'from':owner})
        print("Approving BRT token to veBRT")
        token_contract.approve(transparent_ve, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, {'from':voter})
        print("lock 100 * 1e18 value of account", voter, "for 300 days:")
        transparent_ve.createLock(100 * 1e18, chain.time() + 86400 * 300, {'from': voter})

    print("########## MINT REWARDS TO VE_REWARDS #############")
    print('''token_contract.mint(transparent_ve_rewards, 100000 * 1e18, {'from':owner})''')
    token_contract.mint(transparent_ve_rewards, 100000 * 1e18, {'from':owner})
    print('''token_contract.balanceOf(transparent_ve_rewards)''',token_contract.balanceOf(transparent_ve_rewards))
    print('''transparent_ve_rewards.updateReward({'from':owner})''', transparent_ve_rewards.updateReward({'from':owner}))

    print('''#### SLEEP ONE WEEK ####''')
    chain.sleep(86400*7)
    chain.mine(1)

    print("### GET VOTERS REWARDS ###")
    transparent_ve_rewards.updateReward({'from':owner})
    print("transparent_ve.totalSupply(get_week(0))", transparent_ve.totalSupply(get_week(0)))
    for voter in voters: 
        print('''transparent_ve.balanceOf(voter, get_week(0)))''', transparent_ve.balanceOf(voter, get_week(0)))
        print('''transparent_ve_rewards.getPendingReward(voter)''',transparent_ve_rewards.getPendingReward(voter))

    print("### VOTERS CLAIM REWARDS ###")
    for voter in voters: 
        print('''transparent_ve_rewards.claim({'from':voter})''', transparent_ve_rewards.claim({'from':voter})) 
        print('''transparent_ve_rewards.getPendingReward(voter)''',transparent_ve_rewards.getPendingReward(voter))

