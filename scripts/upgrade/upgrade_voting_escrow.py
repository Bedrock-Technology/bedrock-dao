from brownie import VotingEscrow, accounts, project, config
from pathlib import Path
from .contracts import dep_contracts

# Commands to run this script:
# holesky:brownie run scripts/upgrade/upgrade_voting_escrow.py main holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/upgrade/upgrade_voting_escrow.py main goerli-deployer goerli --network goerli

def main(deployer, dep_network):
    
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    deployer = accounts.load(deployer)
    gas_limit = '6721975'

    ve_proxy = TransparentUpgradeableProxy.at(dep_contracts[dep_network]["ve"])

    ve_contract_upgraded = VotingEscrow.deploy({'from': deployer, 'gas_limit': gas_limit})
    ve_proxy.upgradeTo(ve_contract_upgraded, {'from': deployer, 'gas_limit': gas_limit})

    print("Upgraded VotingEscrow contract at:", ve_contract_upgraded)