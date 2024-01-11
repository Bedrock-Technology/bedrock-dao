from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Commands to run this script:
# holesky:brownie run scripts/testnet/cashier_deploy.py main holesky-owner holesky-deployer holesky-approved-account holesky --network holesky        
# goerli: brownie run scripts/testnet/cashier_deploy.py main goerli-owner goerli-deployer goerli-approved-account goerli --network goerli

dep_contracts = {
    "holesky": {
        "token": "0x91493342f273BCDc28a4f2BE4b0BF7Bd1c334c20",
        "gauge": "0x4A06579Dcb6ec1Db2B09388d1f3418Cd78411c77"
    }, 
    "goerli": {
        "token": "0x07881e8Ac6cAF3C3082227218E94b3D7ffE201fD",
        "gauge": "0xa64B2dFfA8818E4A931e7B25ABDDB4CeA12777B4"
    }
}

shouldPublishSource = False
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer", approved_account="holesky-approved-account", dep_network="holesky"):
    
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy
    
    owner = accounts.load(owner)
    deployer = accounts.load(deployer)

    approved_account = accounts.load(approved_account)

    print(f'contract owner account: {owner.address}\n')
    
    """
    Testnet BRT Contract
    """
    token_proxy = TransparentUpgradeableProxy.at(
        dep_contracts[dep_network]["token"])
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    
    """
    Testnet Gauge Controller Contract
    """
    gauge_proxy = TransparentUpgradeableProxy.at(
        dep_contracts[dep_network]["gauge"])
    
    transparent_gauge = Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)

    """
    Deployer Cashier Contract
    """

    cashier_contract = Cashier.deploy(
            {'from': deployer}, publish_source=shouldPublishSource)

    cashier_proxy = TransparentUpgradeableProxy.deploy(
            cashier_contract, deployer, b'',
            {'from': deployer}, publish_source=shouldPublishSource)
    
    transparent_cashier = Contract.from_abi("Cashier", cashier_proxy.address, Cashier.abi)
    transparent_cashier.initialize(transparent_token, 100000 * 1e18, transparent_gauge, approved_account, {'from': owner})

    print("CASHIER ADDRESS:", transparent_cashier)