from brownie import VeRewards, accounts, project, config
from pathlib import Path
from .contracts import dep_contracts

# Commands to run this script:
# holesky:brownie run scripts/upgrade/upgrade_ve_rewards.py main holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/upgrade/upgrade_ve_rewards.py main goerli-deployer goerli --network goerli

def main(deployer, dep_network):
    
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    deployer = accounts.load(deployer)
    gas_limit = '6721975'

    rewards_proxy = TransparentUpgradeableProxy.at(dep_contracts[dep_network]["rewards"])

    rewards_contract_upgraded = VeRewards.deploy({'from': deployer, 'gas_limit': gas_limit})
    rewards_proxy.upgradeTo(rewards_contract_upgraded, {'from': deployer, 'gas_limit': gas_limit})

    print("Upgraded VeRewards contract at:", rewards_contract_upgraded)


