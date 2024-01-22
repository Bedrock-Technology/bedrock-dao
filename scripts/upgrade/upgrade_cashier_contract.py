from brownie import Cashier, accounts, project, config
from pathlib import Path
from .contracts import dep_contracts

# Commands to run this script:
# holesky:brownie run scripts/upgrade/upgrade_cashier_contract.py main holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/upgrade/upgrade_cashier_contract.py main goerli-deployer goerli --network goerli

def main(deployer, dep_network):
    
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    deployer = accounts.load(deployer)
    gas_limit = '6721975'

    cashier_proxy = TransparentUpgradeableProxy.at(dep_contracts[dep_network]["cashier"])

    cashier_contract_upgraded = Cashier.deploy({'from': deployer, 'gas_limit': gas_limit})
    cashier_proxy.upgradeTo(cashier_contract_upgraded, {'from': deployer, 'gas_limit': gas_limit})

    print("Upgraded Cashier contract at:", cashier_contract_upgraded)