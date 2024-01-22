from brownie import *
from brownie.network import priority_fee
from pathlib import Path

# Commands to run this script:
# holesky:brownie run scripts/testnet/penpie_gauge_deploy.py main holesky-owner holesky-deployer holesky TYPE1 1 --network holesky        
# goerli: brownie run scripts/testnet/penpie_gauge_deploy.py main goerli-owner goerli-deployer goerli TYPE1 1 --network goerli

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

shouldPublishSource = False
priority_fee("80 gwei")
def main(owner="holesky-owner", deployer="holesky-deployer", dep_network="holesky", gType="TYPE1", gTypeWt=1):
    
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
    Testnet Gauge Controller Contract
    """
    gauge_proxy = TransparentUpgradeableProxy.at(
        dep_contracts[dep_network]["gauge"])
    
    transparent_gauge = Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)

    """
    Create dummy Penpie Markets
    """

    penpie_market1 = accounts.add()
    penpie_market2 = accounts.add()
    penpie_market3 = accounts.add()

    """
    Deploy Bribe Manager
    """
    mock_bribe_manager_contract = BribeManager.deploy(
        {'from': deployer}, publish_source=shouldPublishSource)

    mock_bribe_manager_proxy = TransparentUpgradeableProxy.deploy(
        mock_bribe_manager_contract, deployer, b'',
        {'from': deployer}, publish_source=shouldPublishSource)
    
    transparent_mock_bribe_manager = Contract.from_abi("BribeManager", mock_bribe_manager_proxy.address, BribeManager.abi)
    transparent_mock_bribe_manager.initialize({'from': owner})

    """
    Setup Bribe Manager
    """
    
    transparent_mock_bribe_manager.newPool(penpie_market1, chain.id, {'from': owner})
    transparent_mock_bribe_manager.newPool(penpie_market2, chain.id, {'from': owner})
    transparent_mock_bribe_manager.newPool(penpie_market3, chain.id, {'from': owner})
    transparent_mock_bribe_manager.addAllowedTokens(transparent_token.address, {'from': owner})
    
    """
    Deploy staking contract
    """
    
    transparent_penpie_adapter1 = _deploy_gauge(penpie_market1, transparent_token, transparent_mock_bribe_manager,owner, deployer, TransparentUpgradeableProxy)
    
    transparent_penpie_adapter2 = _deploy_gauge(penpie_market2, transparent_token, transparent_mock_bribe_manager,owner, deployer, TransparentUpgradeableProxy)
    
    transparent_penpie_adapter3 = _deploy_gauge(penpie_market3, transparent_token, transparent_mock_bribe_manager,owner, deployer, TransparentUpgradeableProxy)

    print("Gauge 1:", transparent_penpie_adapter1)
    print("Gauge 2:", transparent_penpie_adapter2)
    print("Gauge 3:", transparent_penpie_adapter3)

    """
    Setup Gauges
    """
    transparent_gauge.changeTypeWeight(0, 0, {'from': owner}) # remove old gauges from the calculations
    
    transparent_gauge.addType(gType, gTypeWt, {'from':owner})

    transparent_gauge.addGauge(transparent_penpie_adapter1, 1, 0, {'from':owner})

    transparent_gauge.addGauge(transparent_penpie_adapter2, 1, 0, {'from':owner})

    transparent_gauge.addGauge(transparent_penpie_adapter3, 1, 0, {'from':owner})

def _deploy_gauge(market, reward_token, bribe_manager, owner, deployer, TransparentUpgradeableProxy):
    
    penpie_adapter = PenpieAdapter.deploy(
         {'from': deployer}, publish_source=shouldPublishSource)
    
    penpie_adapter_proxy  =  TransparentUpgradeableProxy.deploy(
        penpie_adapter, deployer, b'',
        {'from': deployer}, publish_source=shouldPublishSource)
    
    transparent_penpie_adapter = Contract.from_abi("PenpieAdapter", penpie_adapter_proxy.address, PenpieAdapter.abi)
    transparent_penpie_adapter.initialize(market, reward_token.address, bribe_manager, {'from': owner})
    
    return transparent_penpie_adapter
    