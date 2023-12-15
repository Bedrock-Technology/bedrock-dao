from brownie import BedrockDAO, accounts, project, config
from pathlib import Path
from .contracts import dep_contracts

# Commands to run this script:
# holesky:brownie run scripts/upgrade/upgrade_token.py main holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/upgrade/upgrade_token.py main goerli-deployer goerli --network goerli

def main(deployer, dep_network):
    
    deps = project.load(Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    deployer = accounts.load(deployer)
    gas_limit = '6721975'

    token_proxy = TransparentUpgradeableProxy.at(dep_contracts[dep_network]["token"])

    token_contract_upgraded = BedrockDAO.deploy({'from': deployer, 'gas_limit': gas_limit})
    token_proxy.upgradeTo(token_contract_upgraded, {'from': deployer, 'gas_limit': gas_limit})

    print("Upgraded BedrockDao token contract at:", token_contract_upgraded)