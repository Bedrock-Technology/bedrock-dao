from brownie import *
from brownie.convert import EthAddress
from pathlib import Path

import time
import pytest

# this script simulates voters locks to get veToken
def main():
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    owner = accounts[0]
    deployer = accounts[1]

    print(f'contract owner account: {owner.address}\n')

    token_contract = BedrockDAO.deploy(owner, owner, owner, {'from': deployer})

    ve_contract = VotingEscrow.deploy(
            {'from': deployer})

    ve_proxy =  TransparentUpgradeableProxy.deploy(
            ve_contract, deployer, b'',
            {'from': deployer})

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_ve.initialize( "voting-escrow BR", "veBR", token_contract, {'from': owner})

    print("VE ADDRESS:", transparent_ve)

    for i in range(2,4):
        account = accounts[i]
        print("ACCOUNT:", account)
        print("""token_contract.mint(account, 100 * 1e18, {'from':owner})""")
        token_contract.mint(account, 100 * 1e18, {'from':owner})
        print("""token_contract.approve(transparent_ve, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, {'from':account})""")
        token_contract.approve(transparent_ve, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, {'from':account})
        print("""transparent_ve.createLock(100 * 1e18, chain.time() + 86400 * 30, {'from': account})""")
        transparent_ve.createLock(100 * 1e18, chain.time() + 86400 * 30, {'from': account})

        print("lockinfo:", transparent_ve.userPointHistory(account, transparent_ve.userPointEpoch(account)))
        print("balanceOf", account, "is:", transparent_ve.balanceOf(account))
        print("totalSupply is:", transparent_ve.totalSupply())


