import pytest

from pathlib import Path
from brownie import *
import math
import time

deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])

@pytest.fixture
def owner():
    return accounts[0]

@pytest.fixture
def deployer():
    return accounts[1]

@pytest.fixture
def floorToWeek():
    return lambda t : math.floor(t/(86400*7)) * (86400*7)

@pytest.fixture
def daysInSeconds():
    return lambda days: days * 24 * 60 * 60

@pytest.fixture
def setup_contracts(owner, deployer):

    chain.reset()
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy
    print(f'contract owner account: {owner.address}\n')
    
    """
    Deploy BedrockDAO
    """
    token_contract = BedrockDAO.deploy(
        {'from': deployer})

    token_proxy =  TransparentUpgradeableProxy.deploy(
        token_contract, deployer, b'',
        {'from': deployer})
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    transparent_token.initialize({'from': owner})

    """
    Deploy VotingEscrow
    """
    ve_contract = VotingEscrow.deploy(
        {'from': deployer})

    ve_proxy =  TransparentUpgradeableProxy.deploy(
        ve_contract, deployer, b'',
        {'from': deployer})

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_ve.initialize( "voting-escrow BRT", "veBRT", token_proxy.address, {'from': owner})

    """
    Deploy Gauge Controller
    """

    gauge_contract = GaugeController.deploy(
        {'from': deployer})
    
    gauge_proxy = TransparentUpgradeableProxy.deploy(
        gauge_contract, deployer, b'',
        {'from': deployer})
    
    transparent_gauge = Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)
    transparent_gauge.initialize(transparent_ve, {'from': owner})
    
    """
    Deploy Bribe Manager
    """
    mock_bribe_manager_contract = BribeManager.deploy(
        {'from': deployer})

    mock_bribe_manager_proxy = TransparentUpgradeableProxy.deploy(
        mock_bribe_manager_contract, deployer, b'',
        {'from': deployer})
    
    transparent_mock_bribe_manager = Contract.from_abi("BribeManager", mock_bribe_manager_proxy.address, BribeManager.abi)
    transparent_mock_bribe_manager.initialize({'from': owner})

    """
    Setup Bribe Manager
    """
    test_market = accounts[5]
    transparent_mock_bribe_manager.newPool(test_market, chain.id, {'from': owner})
    transparent_mock_bribe_manager.addAllowedTokens(transparent_token.address, {'from': owner})

    print(f'Test Market: {test_market}')    

    """
    Deploy Penpie Adapter
    """
    penpie_adapter = PenpieAdapter.deploy(
        {'from': deployer})
    penpie_adapter_proxy  =  TransparentUpgradeableProxy.deploy(
        penpie_adapter, deployer, b'',
        {'from': deployer})
    
    transparent_penpie_adapter = Contract.from_abi("PenpieAdapter", penpie_adapter_proxy.address, PenpieAdapter.abi)
    transparent_penpie_adapter.initialize(test_market, transparent_token.address, transparent_mock_bribe_manager, {'from': owner})
   
    return transparent_token, transparent_ve, transparent_gauge, transparent_penpie_adapter, transparent_mock_bribe_manager