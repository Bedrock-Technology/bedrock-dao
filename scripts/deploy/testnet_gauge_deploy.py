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
    
    ve_proxy = TransparentUpgradeableProxy.at(
        "0x19A84Cb4f25b95990F0B25b15694349Ee1cCc282")
    
    transparent_ve = Contract.from_abi("VotingEscrow", ve_proxy.address, VotingEscrow.abi)

    """
    Deploy dummy LP tokens
    """

    lp_token1 = DummyLPToken.deploy({'from': deployer})

    lp_token2 = DummyLPToken.deploy({'from': deployer})

    lp_token3 = DummyLPToken.deploy({'from': deployer})

    lp_token1_proxy = TransparentUpgradeableProxy.deploy(
        lp_token1, deployer, b'',{'from': deployer})
    
    lp_token2_proxy = TransparentUpgradeableProxy.deploy(
        lp_token2, deployer, b'',{'from': deployer})

    lp_token3_proxy = TransparentUpgradeableProxy.deploy(
        lp_token3, deployer, b'',{'from': deployer})
   
    transparent_lp_token1 = Contract.from_abi(
        "DummyLPToken", lp_token1_proxy.address, DummyLPToken.abi)
    
    transparent_lp_token2 = Contract.from_abi(
        "DummyLPToken", lp_token2_proxy.address, DummyLPToken.abi)
    
    transparent_lp_token3 = Contract.from_abi(
        "DummyLPToken", lp_token3_proxy.address, DummyLPToken.abi)
    
    transparent_lp_token1.initialize(
        "Holesky UniETH/rETH LP Token", "HUNIETH-rETH", {'from': owner})
    
    transparent_lp_token2.initialize(
        "Holesky UniETH/wstETH LP Token", "HUNIETH-wstETH", {'from': owner})
    
    transparent_lp_token3.initialize(
        "Holesky UniETH/ETH LP Token", "HUNIETH-ETH", {'from': owner})

    print("LP Token 1:", transparent_lp_token1)
    print("LP Token 2:", transparent_lp_token2)
    print("LP Token 3:", transparent_lp_token3)

    """
    Deploy staking contract
    """

    staking_contract1 = LPStaking.deploy({'from': deployer})

    staking_contract2 = LPStaking.deploy({'from': deployer})

    staking_contract3 = LPStaking.deploy({'from': deployer})
    
    staking_proxy1 =  TransparentUpgradeableProxy.deploy(
        staking_contract1, deployer, b'',{'from': deployer})
    
    staking_proxy2 =  TransparentUpgradeableProxy.deploy(
        staking_contract2, deployer, b'',{'from': deployer})
    
    staking_proxy3 =  TransparentUpgradeableProxy.deploy(
        staking_contract3, deployer, b'',{'from': deployer})
    
    transparent_staking1 = Contract.from_abi("LPStaking", staking_proxy1.address, LPStaking.abi)
    
    transparent_staking2 = Contract.from_abi("LPStaking", staking_proxy2.address, LPStaking.abi)
    
    transparent_staking3 = Contract.from_abi("LPStaking", staking_proxy3.address, LPStaking.abi)
    
    transparent_staking1.initialize(transparent_lp_token1, transparent_token, {'from': owner})
    
    transparent_staking2.initialize(transparent_lp_token2, transparent_token, {'from': owner})
    
    transparent_staking3.initialize(transparent_lp_token3, transparent_token, {'from': owner})

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
