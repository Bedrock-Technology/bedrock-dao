import pytest
from web3 import Web3
from pathlib import Path
from brownie import *
import math


@pytest.fixture(scope="session", autouse=True)
def w3():
    return Web3(Web3.HTTPProvider('http://localhost:8545'))

@pytest.fixture(scope="session", autouse=True)
def owner():
    return accounts[0]

@pytest.fixture(scope="session", autouse=True)
def deployer():
    return accounts[1]

@pytest.fixture(scope="session", autouse=True)
def approved_account():
    return accounts[2]

@pytest.fixture(scope="session", autouse=True)
def markets():
    return accounts[3], accounts[4]

@pytest.fixture(scope="session", autouse=True)
def users():
    return accounts[5], accounts[6]

@pytest.fixture(scope="session", autouse=True)
def init_type_names():
    return "TYPE0", "TYPE1"

@pytest.fixture(scope="session", autouse=True)
def init_type_weights():
    return 1, 1

@pytest.fixture(scope="session", autouse=True)
def init_gauge_base_weights():
    return 100*1e18, 100*1e18

@pytest.fixture(scope="session", autouse=True)
def oracle():
    return accounts[7]

@pytest.fixture(scope="session", autouse=True)
def zero_address():
    return accounts.at("0x0000000000000000000000000000000000000000", True)

@pytest.fixture(scope="session", autouse=True)
def global_week_emission():
    return 100 * 1e18

@pytest.fixture(scope="session", autouse=True)
def floorToWeek():
    return lambda t : math.floor(t/(86400*7)) * (86400*7)

@pytest.fixture(scope="session", autouse=True)
def daysInSeconds():
    return lambda days: days * 24 * 60 * 60

@pytest.fixture(scope="session", autouse=True)
def proxy():
    # Reference: https://docs.openzeppelin.com/contracts/4.x/api/proxy#TransparentUpgradeableProxy
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    return deps.TransparentUpgradeableProxy

@pytest.fixture()
def setup_contracts(proxy, owner, deployer, approved_account, global_week_emission, markets, init_type_names, init_type_weights, init_gauge_base_weights):
    # ----------Implementation Contract Deployment----------
    mock_bribe_manager_contract = BribeManager.deploy({'from': deployer})
    penpie_adapter1 = PenpieAdapter.deploy({'from': deployer})
    penpie_adapter2 = PenpieAdapter.deploy({'from': deployer})

    token_contract = BedrockDAO.deploy(owner, owner, owner, {'from': deployer})
    ve_contract = VotingEscrow.deploy({'from': deployer})
    gauge_contract = GaugeController.deploy({'from': deployer})
    ve_rewards = VeRewards.deploy({'from': deployer})
    cashier = Cashier.deploy({'from': deployer})

    # ----------Proxy Contract Deployment----------
    mock_bribe_manager_proxy = proxy.deploy(mock_bribe_manager_contract, deployer, b'', {'from': deployer})
    penpie_adapter_proxy1 = proxy.deploy(penpie_adapter1, deployer, b'', {'from': deployer})
    penpie_adapter_proxy2 = proxy.deploy(penpie_adapter2, deployer, b'', {'from': deployer})

    ve_proxy = proxy.deploy(ve_contract, deployer, b'', {'from': deployer})
    gauge_proxy = proxy.deploy(gauge_contract, deployer, b'', {'from': deployer})
    ve_rewards_proxy = proxy.deploy(ve_rewards, deployer, b'', {'from': deployer})
    cashier_proxy = proxy.deploy(cashier, deployer, b'', {'from': deployer})

    # ----------Transparent Contract Creating----------
    transparent_mock_bribe_manager = Contract.from_abi("BribeManager", mock_bribe_manager_proxy.address, BribeManager.abi)
    transparent_penpie_adapter1 = Contract.from_abi("PenpieAdapter", penpie_adapter_proxy1.address, PenpieAdapter.abi)
    transparent_penpie_adapter2 = Contract.from_abi("PenpieAdapter", penpie_adapter_proxy2.address, PenpieAdapter.abi)

    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)
    transparent_gauge = Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)
    transparent_ve_rewards = Contract.from_abi("VeRewards", ve_rewards_proxy.address, VeRewards.abi)
    transparent_cashier = Contract.from_abi("Cashier", cashier_proxy.address, Cashier.abi)

    # ----------Contract Initializing----------
    transparent_mock_bribe_manager.initialize({'from': owner})
    transparent_penpie_adapter1.initialize(markets[0], token_contract.address, transparent_mock_bribe_manager, {'from': owner})
    transparent_penpie_adapter2.initialize(markets[1], token_contract.address, transparent_mock_bribe_manager, {'from': owner})

    transparent_ve.initialize( "voting-escrow BR", "veBR", token_contract.address, {'from': owner})
    transparent_gauge.initialize(transparent_ve, {'from': owner})
    transparent_ve_rewards.initialize(transparent_ve, {'from': owner})
    transparent_cashier.initialize(token_contract, global_week_emission, transparent_gauge, approved_account, {'from': owner})

    # ----------Contract Configuring----------
    # Register markets
    transparent_mock_bribe_manager.newPool(markets[0], chain.id, {'from': owner})
    transparent_mock_bribe_manager.newPool(markets[1], chain.id, {'from': owner})
    transparent_mock_bribe_manager.addAllowedTokens(token_contract.address, {'from': owner})

    # Register gauge types and gauges
    transparent_gauge.addType(init_type_names[0], init_type_weights[0], {'from': owner})
    transparent_gauge.addType(init_type_names[1], init_type_weights[1], {'from': owner})
    assert transparent_gauge.nGaugeTypes() == 2

    transparent_gauge.addGauge(transparent_penpie_adapter1, 0, init_gauge_base_weights[0], {'from': owner})
    transparent_gauge.addGauge(transparent_penpie_adapter2, 1, init_gauge_base_weights[1], {'from': owner})
   
    return (token_contract, transparent_ve, transparent_gauge, transparent_penpie_adapter1, transparent_penpie_adapter2,
            transparent_mock_bribe_manager, transparent_ve_rewards, transparent_cashier)
