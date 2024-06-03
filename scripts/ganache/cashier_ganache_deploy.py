from brownie import *
from brownie.convert import EthAddress
from pathlib import Path

import time
import pytest

def get_week(n=0):
    WEEK = 604800
    this_week = (chain.time() // WEEK) * WEEK
    return this_week + (n * WEEK)

# this script simulates voters locks to get veToken, and votes on different gauges,
# cashier distribute rewards to gauges based on their weights
def main():
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    owner = accounts[0]
    deployer = accounts[1]
    voters = [accounts[2],accounts[3]]
    lp_gauge1 = accounts[8]
    lp_gauge2 = accounts[9]
    approved_account = accounts[4]

    print(f'contract owner account: {owner.address}\n')

    token_contract = BedrockDAO.deploy(owner, owner, owner, {'from': deployer})

    ve_contract = VotingEscrow.deploy(
            {'from': deployer})

    ve_proxy =  TransparentUpgradeableProxy.deploy(
            ve_contract, deployer, b'',
            {'from': deployer})

    gauge_contract = GaugeController.deploy(
            {'from': deployer})

    gauge_proxy = TransparentUpgradeableProxy.deploy(
            gauge_contract, deployer, b'',
            {'from': deployer})

    cashier_contract = Cashier.deploy(
            {'from': deployer})

    cashier_proxy = TransparentUpgradeableProxy.deploy(
            cashier_contract, deployer, b'',
            {'from': deployer})

    print("BR ADDRESS:", token_contract)

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_ve.initialize( "voting-escrow BR", "veBR", token_contract, {'from': owner})

    print("VE ADDRESS:", transparent_ve)

    transparent_gauge= Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)
    transparent_gauge.initialize(transparent_ve, {'from': owner})

    print("GAUGE ADDRESS:", transparent_gauge)

    transparent_cashier = Contract.from_abi("Cashier", cashier_proxy.address, Cashier.abi)
    transparent_cashier.initialize(token_contract, 100000 * 1e18, transparent_gauge, approved_account, {'from': owner})

    print("CASHIER ADDRESS:", transparent_cashier)

    print("########## GAUGE CONTROLLER INIT #############")
    print(r'''addType("LP-TYPE0", 1, {'from':owner})''')
    transparent_gauge.addType("TYPE0", 1, {'from':owner})

    print(r'''addGauge(lp_gauge1, 0, 0, {'from':owner})''', lp_gauge1)
    transparent_gauge.addGauge(lp_gauge1, 0, 0, {'from':owner})
    print(r'''addGauge(lp_gauge2, 0, 0, {'from':owner})''', lp_gauge2)
    transparent_gauge.addGauge(lp_gauge2, 0, 0, {'from':owner})

    for voter in voters: 
        print("minting BR token to: ", voter)
        token_contract.mint(voter, 100 * 1e18, {'from':owner})
        print("Approving BR token to veBR")
        token_contract.approve(transparent_ve, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, {'from':voter})
        print("lock 100 * 1e18 value of account", voter, "for 300 days:")
        transparent_ve.createLock(100 * 1e18, chain.time() + 86400 * 300, {'from': voter})

        print(r'''voteForGaugeWeight(lp_gauge1, 5000, {'from': voter})''')
        transparent_gauge.voteForGaugeWeight(lp_gauge1, 3000, {'from': voter})
        print(r'''voteForGaugeWeight(lp_gauge2, 8000, {'from': voter})''')
        transparent_gauge.voteForGaugeWeight(lp_gauge2, 7000, {'from': voter})

        print(r'''transparent_gauge.gaugeRelativeWeight(lp_gauge1, get_week(1))''', transparent_gauge.gaugeRelativeWeight(lp_gauge1, get_week(1)))
        print(r'''transparent_gauge.gaugeRelativeWeight(lp_gauge2, get_week(1))''', transparent_gauge.gaugeRelativeWeight(lp_gauge2, get_week(1)))

    print("########## CASHIER INIT #############")
    token_contract.mint(approved_account, 100000 * 1e18, {'from':owner})
    print('''token_contract.balanceOf(approved_account)''',token_contract.balanceOf(approved_account))
    token_contract.approve(transparent_cashier, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, {'from':approved_account})
    print('''transparent_cashier.setGlobalEmissionRate(100 * 1e18, {'from':owner}''')
    transparent_cashier.setGlobalEmissionRate(100 * 1e18, {'from':owner}) 

    chain.sleep(86400*7)
    chain.mine(1)
    print("distributeRewards to gauge 1 & 2")
    transparent_cashier.distributeRewards(lp_gauge1, {'from':owner})
    transparent_cashier.distributeRewards(lp_gauge2, {'from':owner})
    print('''token_contract.balanceOf(lp_gauge1)''',token_contract.balanceOf(lp_gauge1))
    print('''token_contract.balanceOf(lp_gauge2)''',token_contract.balanceOf(lp_gauge2))

