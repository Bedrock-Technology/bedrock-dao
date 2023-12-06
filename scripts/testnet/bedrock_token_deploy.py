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
    Deploy BedrockDAO contract
    """
    token_contract = BedrockDAO.deploy(
            {'from': deployer})

    token_proxy = TransparentUpgradeableProxy.deploy(
            token_contract, deployer, b'',
            {'from': deployer})
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    transparent_token.initialize({'from': owner})

    print("TOKEN ADDRESS:", transparent_token)
