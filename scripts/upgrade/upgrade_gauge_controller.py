from brownie import GaugeController, accounts, project, config
from pathlib import Path
from .contracts import dep_contracts

# Commands to run this script:
# holesky:brownie run scripts/upgrade/upgrade_gauge_controller.py main holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/upgrade/upgrade_gauge_controller.py main goerli-deployer goerli --network goerli

def main(deployer, dep_network):
    
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    deployer = accounts.load(deployer)
    gas_limit = '6721975'

    gauge_proxy = TransparentUpgradeableProxy.at(dep_contracts[dep_network]["gauge"])

    gauge_contract_upgraded = GaugeController.deploy({'from': deployer, 'gas_limit': gas_limit})
    gauge_proxy.upgradeTo(gauge_contract_upgraded, {'from': deployer, 'gas_limit': gas_limit})

    print("Upgraded GaugeController contract at:", gauge_contract_upgraded)