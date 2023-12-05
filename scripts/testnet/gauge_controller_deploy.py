from brownie import *
from pathlib import Path

def main():
    deps = project.load(  Path.home() / ".brownie" / "packages" / config["dependencies"][0])
    TransparentUpgradeableProxy = deps.TransparentUpgradeableProxy
    
    owner = accounts.load('holesky-owner')
    deployer = accounts.load('holesky-deploy')

    print(f'contract owner account: {owner.address}\n')
    
    """
    Testnet BRT Contract
    """
    token_proxy = TransparentUpgradeableProxy.at(
        "0x91493342f273BCDc28a4f2BE4b0BF7Bd1c334c20")
    
    transparent_token = Contract.from_abi("BedrockDAO", token_proxy.address, BedrockDAO.abi)
    
    """
    Testnet Voting Escrow Contract
    """
    ve_proxy = TransparentUpgradeableProxy.at(
        "0x19A84Cb4f25b95990F0B25b15694349Ee1cCc282")
    
    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)

    """
    Deploy dummy LP tokens
    """

    transparent_lp_token1 = deploy_dummy_token("Holesky UniETH/rETH LP Token", "HUNIETH-rETH", owner, deployer, TransparentUpgradeableProxy)
    
    transparent_lp_token2 = deploy_dummy_token("Holesky UniETH/wstETH LP Token", "HUNIETH-wstETH", owner, deployer, TransparentUpgradeableProxy)
    
    transparent_lp_token3 = deploy_dummy_token("Holesky UniETH/ETH LP Token", "HUNIETH-ETH", owner, deployer, TransparentUpgradeableProxy)
    
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

    gauge_contract = GaugeController.deploy({'from': deployer})

    gauge_proxy = TransparentUpgradeableProxy.deploy(
        gauge_contract, deployer, b'',{'from': deployer})

    transparent_gauge= Contract.from_abi("GaugeController", gauge_proxy.address, GaugeController.abi)
    transparent_gauge.initialize(transparent_ve, {'from': owner})

    print("Gauge Controller:", transparent_gauge)

    """
    Setup Gauges
    """
    transparent_gauge.addType("TYPE0", 1, {'from':owner})

    transparent_gauge.addGauge(transparent_staking1, 0, 0, {'from':owner})

    transparent_gauge.addGauge(transparent_staking2, 0, 0, {'from':owner})

    transparent_gauge.addGauge(transparent_staking3, 0, 0, {'from':owner})


def deploy_dummy_token(name, symbol, owner, deployer, TransparentUpgradeableProxy):
    
    token = DummyLPToken.deploy({'from': deployer})

    token_proxy = TransparentUpgradeableProxy.deploy(
        token, deployer, b'',{'from': deployer})

    transparent_token = Contract.from_abi(
        "DummyLPToken", token_proxy.address, DummyLPToken.abi)    
    
    transparent_token.initialize(name, symbol, {'from': owner})    
    return transparent_token


def deploy_gauge(lp_token, reward_token, owner, deployer, TransparentUpgradeableProxy):
    staking_contract = LPStaking.deploy({'from': deployer})

    staking_proxy =  TransparentUpgradeableProxy.deploy(
        staking_contract, deployer, b'',{'from': deployer})
    
    transparent_staking = Contract.from_abi("LPStaking", staking_proxy.address, LPStaking.abi)
    
    transparent_staking.initialize(lp_token, reward_token, {'from': owner})
    return transparent_staking
    