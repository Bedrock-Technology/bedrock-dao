from brownie import BribeManager, Cashier, GaugeController, PenpieAdapter, BedrockDAO, VeRewards, VotingEscrow, accounts, Contract, project, config, chain
from pathlib import Path

# This script file is designed to run in a local network environment using the following commands.
# On Ganache local network: `brownie run scripts/local/deployment.py`
# On forked local network: `brownie run scripts/local/deployment.py --network=YOU_LOCAL_NETWORK_ID`


def main():
    print("Local Environment Reset ......")
    chain.reset()

    print("Proxy Code Loading ......")
    # Reference: https://docs.openzeppelin.com/contracts/4.x/api/proxy#TransparentUpgradeableProxy
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy

    print("Params Specification ......")
    global_week_emission = 100 * 1e18

    print("Accounts Loading ......")
    owner = accounts[0]
    deployer = accounts[1]

    approved_account = accounts[2]
    penpie_market_1 = accounts[3]
    penpie_market_2 = accounts[4]
    penpie_market_3 = accounts[5]

    print("Contract Deployment ......")

    bribe_manager = BribeManager.deploy({'from': deployer})
    bedrock_dao = BedrockDAO.deploy(owner, owner, owner, {'from': deployer})
    voting_escrow = VotingEscrow.deploy({'from': deployer})
    gauge_controller = GaugeController.deploy({'from': deployer})
    ve_rewards = VeRewards.deploy({'from': deployer})
    cashier = Cashier.deploy({'from': deployer})
    penpie_adapter_1 = PenpieAdapter.deploy({'from': deployer})
    penpie_adapter_2 = PenpieAdapter.deploy({'from': deployer})
    penpie_adapter_3 = PenpieAdapter.deploy({'from': deployer})

    bribe_manager_proxy = TransparentUpgradeableProxy.deploy(bribe_manager, deployer, b'', {'from': deployer})
    voting_escrow_proxy = TransparentUpgradeableProxy.deploy(voting_escrow, deployer, b'', {'from': deployer})
    gauge_controller_proxy = TransparentUpgradeableProxy.deploy(gauge_controller, deployer, b'', {'from': deployer})
    ve_rewards_proxy = TransparentUpgradeableProxy.deploy(ve_rewards, deployer, b'', {'from': deployer})
    cashier_proxy = TransparentUpgradeableProxy.deploy(cashier, deployer, b'', {'from': deployer})
    penpie_adapter_1_proxy = TransparentUpgradeableProxy.deploy(penpie_adapter_1, deployer, b'', {'from': deployer})
    penpie_adapter_2_proxy = TransparentUpgradeableProxy.deploy(penpie_adapter_2, deployer, b'', {'from': deployer})
    penpie_adapter_3_proxy = TransparentUpgradeableProxy.deploy(penpie_adapter_3, deployer, b'', {'from': deployer})

    print("Deployed BribeManager address:", bribe_manager)
    print("Deployed BedrockDAO address:", bedrock_dao)
    print("Deployed VotingEscrow address:", voting_escrow)
    print("Deployed GaugeController address:", gauge_controller)
    print("Deployed VeRewards address:", ve_rewards)
    print("Deployed Cashier address:", cashier)
    print("Deployed PenpieAdapter-1 address:", penpie_adapter_1)
    print("Deployed PenpieAdapter-2 address:", penpie_adapter_2)
    print("Deployed PenpieAdapter-3 address:", penpie_adapter_3)

    print(" ")

    print("Deployed BribeManager Proxy address:", bribe_manager_proxy)
    print("Deployed VotingEscrow Proxy address:", voting_escrow_proxy)
    print("Deployed GaugeController Proxy address:", gauge_controller_proxy)
    print("Deployed VeRewards Proxy address:", ve_rewards_proxy)
    print("Deployed Cashier Proxy address:", cashier_proxy)
    print("Deployed PenpieAdapter-1 Proxy address:", penpie_adapter_1_proxy)
    print("Deployed PenpieAdapter-2 Proxy address:", penpie_adapter_2_proxy)
    print("Deployed PenpieAdapter-3 Proxy address:", penpie_adapter_3_proxy)

    print(" ")
    print("Contract Initialization ......")

    bribe_manager_transparent = Contract.from_abi("BribeManager", bribe_manager_proxy.address, BribeManager.abi)
    voting_escrow_transparent = Contract.from_abi("VotingEscrow", voting_escrow_proxy.address, VotingEscrow.abi)
    gauge_controller_transparent = Contract.from_abi("GaugeController", gauge_controller_proxy.address, GaugeController.abi)
    ve_rewards_transparent = Contract.from_abi("VeRewards", ve_rewards_proxy.address, VeRewards.abi)
    cashier_transparent = Contract.from_abi("Cashier", cashier_proxy.address, Cashier.abi)
    penpie_adapter_1_transparent = Contract.from_abi("PenpieAdapter", penpie_adapter_1_proxy.address, PenpieAdapter.abi)
    penpie_adapter_2_transparent = Contract.from_abi("PenpieAdapter", penpie_adapter_2_proxy.address, PenpieAdapter.abi)
    penpie_adapter_3_transparent = Contract.from_abi("PenpieAdapter", penpie_adapter_3_proxy.address, PenpieAdapter.abi)

    bribe_manager_transparent.initialize({'from': owner})
    voting_escrow_transparent.initialize(
        bedrock_dao.name(),
        bedrock_dao.symbol(),
        bedrock_dao.address,
        {'from': owner})
    gauge_controller_transparent.initialize(voting_escrow_transparent.address, {'from': owner})
    ve_rewards_transparent.initialize(voting_escrow_transparent.address, bedrock_dao.address, {'from': owner})
    cashier_transparent.initialize(
        bedrock_dao.address,
        global_week_emission,
        gauge_controller_transparent,
        approved_account,
        {'from': owner})
    penpie_adapter_1_transparent.initialize(
        penpie_market_1,
        bedrock_dao.address,
        bribe_manager_transparent.address,
        {'from': owner})
    penpie_adapter_2_transparent.initialize(
        penpie_market_2,
        bedrock_dao.address,
        bribe_manager_transparent.address,
        {'from': owner})
    penpie_adapter_3_transparent.initialize(
        penpie_market_3,
        bedrock_dao.address,
        bribe_manager_transparent.address,
        {'from': owner})

    print("Initial Contract Status Check ......")   # TODO: Checking more status

    assert bedrock_dao.name() == "Bedrock DAO"
    assert bedrock_dao.symbol() == "BRT"

    assert voting_escrow_transparent.name() == bedrock_dao.name()
    assert voting_escrow_transparent.symbol() == bedrock_dao.symbol()
    assert voting_escrow_transparent.assetToken() == bedrock_dao.address

    assert gauge_controller_transparent.votingEscrow() == voting_escrow_transparent.address

    assert ve_rewards_transparent.votingEscrow() == voting_escrow_transparent.address
    assert ve_rewards_transparent.rewardToken() == bedrock_dao.address

    assert cashier_transparent.rewardToken() == bedrock_dao.address
    assert cashier_transparent.globalWeekEmission() == global_week_emission
    assert cashier_transparent.gaugeController() == gauge_controller_transparent.address
    assert cashier_transparent.gaugeController() == gauge_controller_transparent.address
    assert cashier_transparent.approvedAccount() == approved_account

    assert penpie_adapter_1_transparent.pendleMarket() == penpie_market_1
    assert penpie_adapter_1_transparent.rewardToken() == bedrock_dao.address
    assert penpie_adapter_1_transparent.bribeManager() == bribe_manager_transparent.address

    assert penpie_adapter_2_transparent.pendleMarket() == penpie_market_2
    assert penpie_adapter_2_transparent.rewardToken() == bedrock_dao.address
    assert penpie_adapter_2_transparent.bribeManager() == bribe_manager_transparent.address

    assert penpie_adapter_3_transparent.pendleMarket() == penpie_market_3
    assert penpie_adapter_3_transparent.rewardToken() == bedrock_dao.address
    assert penpie_adapter_3_transparent.bribeManager() == bribe_manager_transparent.address








