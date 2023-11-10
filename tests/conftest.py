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
    Deploy BedrockGovernor
    """
    govern_contract = BedrockGovernor.deploy(
        {'from': deployer})

    govern_proxy = TransparentUpgradeableProxy.deploy(
        govern_contract, deployer, b'',
        {'from': deployer})

    timelock = TimeLock.deploy(
        86400*1,
        [govern_proxy.address],
        ["0x0000000000000000000000000000000000000000"],
        owner,
        {'from': owner})

    transparent_govern = Contract.from_abi("BedrockGovernor", govern_proxy.address, BedrockGovernor.abi)
    transparent_govern.initialize(transparent_ve, timelock, {'from': owner})
    
    return transparent_token, transparent_ve, transparent_gauge, transparent_govern

