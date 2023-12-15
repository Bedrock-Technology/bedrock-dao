from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Commands to run this script:
# holesky:brownie run scripts/testnet/dummy_gauge_deploy.py main holesky-owner holesky-deployer holesky --network holesky        
# goerli: brownie run scripts/testnet/dummy_gauge_deploy.py main goerli-owner goerli-deployer goerli --network goerli

dep_contracts = {
    "holesky": {
        "token": "0x91493342f273BCDc28a4f2BE4b0BF7Bd1c334c20",
        "ve":    "0x19A84Cb4f25b95990F0B25b15694349Ee1cCc282",
        "gauge": "0x4A06579Dcb6ec1Db2B09388d1f3418Cd78411c77"
    }, 
    "goerli": {
        "token": "0x07881e8Ac6cAF3C3082227218E94b3D7ffE201fD",
        "ve":    "0x19Cd39eC64d3AbbcF9A448175400cDDbA97B9f56",
        "gauge": "0xa64B2dFfA8818E4A931e7B25ABDDB4CeA12777B4"
    }
}

dummy_token = {
    "holesky": {
        "name": ["Holesky UniETH/rETH LP Token", "Holesky UniETH/wstETH LP Token", "Holesky UniETH/ETH LP Token"],
        "symbol": ["HUNIETH-rETH", "HUNIETH-wstETH", "HUNIETH-ETH"]
    },
    "goerli": {
        "name": ["Goerli UniETH/rETH LP Token", "Goerli UniETH/wstETH LP Token", "Goerli UniETH/ETH LP Token"],
        "symbol": ["GOUNIETH-rETH", "GOUNIETH-wstETH", "GOUNIETH-ETH"]
    }
}

shouldPublishSource = False
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer", dep_network="holesky"):
    
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy
    
    owner = accounts.load(owner)
    deployer = accounts.load(deployer)

    print(f'contract owner account: {owner.address}\n')
    
    """
    Testnet BRT Contract
    """
    token_proxy = TransparentUpgradeableProxy.at(
        dep_contracts[dep_network]["token"])
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    
    """
    Testnet Voting Escrow Contract
    """
    ve_proxy = TransparentUpgradeableProxy.at(
        dep_contracts[dep_network]["ve"])
    
    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    
    """
    Testnet Gauge Controller Contract
    """
    gauge_proxy = TransparentUpgradeableProxy.at(
        dep_contracts[dep_network]["gauge"])
    
    transparent_gauge = Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)

    """
    Deploy dummy LP tokens
    """

    transparent_lp_token1 = deploy_dummy_token(dummy_token[dep_network]["name"], dummy_token[dep_network]["symbol"], owner, deployer, TransparentUpgradeableProxy)
    
    transparent_lp_token2 = deploy_dummy_token(dummy_token[dep_network]["name"], dummy_token[dep_network]["symbol"], owner, deployer, TransparentUpgradeableProxy)
    
    transparent_lp_token3 = deploy_dummy_token(dummy_token[dep_network]["name"], dummy_token[dep_network]["symbol"], owner, deployer, TransparentUpgradeableProxy)
    
    print("LP Token 1:", transparent_lp_token1)
    print("LP Token 2:", transparent_lp_token2)
    print("LP Token 3:", transparent_lp_token3)

    """
    Deploy staking contract
    """
    
    transparent_staking1 = deploy_gauge(transparent_lp_token1, transparent_token, owner, deployer, TransparentUpgradeableProxy)
    
    transparent_staking2 = deploy_gauge(transparent_lp_token2, transparent_token, owner, deployer, TransparentUpgradeableProxy)
    
    transparent_staking3 = deploy_gauge(transparent_lp_token3, transparent_token, owner, deployer, TransparentUpgradeableProxy)

    print("Gauge 1:", transparent_staking1)
    print("Gauge 2:", transparent_staking2)
    print("Gauge 3:", transparent_staking3)

    """
    Setup Gauges
    """
    transparent_gauge.addType("TYPE0", 1, {'from':owner})

    transparent_gauge.addGauge(transparent_staking1, 0, 0, {'from':owner})

    transparent_gauge.addGauge(transparent_staking2, 0, 0, {'from':owner})

    transparent_gauge.addGauge(transparent_staking3, 0, 0, {'from':owner})


def deploy_dummy_token(name, symbol, owner, deployer, TransparentUpgradeableProxy):
    
    token = DummyLPToken.deploy({'from': deployer}, publish_source=shouldPublishSource)

    token_proxy = TransparentUpgradeableProxy.deploy(
        token, deployer, b'',{'from': deployer}, publish_source=shouldPublishSource)

    transparent_token = Contract.from_abi(
        "DummyLPToken", token_proxy.address, DummyLPToken.abi)    
    
    transparent_token.initialize(name, symbol, {'from': owner})    
    return transparent_token


def deploy_gauge(lp_token, reward_token, owner, deployer, TransparentUpgradeableProxy):
    staking_contract = LPStaking.deploy({'from': deployer},  publish_source=shouldPublishSource)

    staking_proxy =  TransparentUpgradeableProxy.deploy(
        staking_contract, deployer, b'',{'from': deployer},  publish_source=shouldPublishSource)
    
    transparent_staking = Contract.from_abi("LPStaking", staking_proxy.address, LPStaking.abi)
    
    transparent_staking.initialize(lp_token, reward_token, {'from': owner})
    return transparent_staking
    