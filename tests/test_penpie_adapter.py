"""
Test vote for gauge weight - happy path
"""
def test_addBribeERC20(fn_isolation, setup_contracts, owner):
    penpie_adapter, bribeManager, transparent_token = setup_contracts[3], setup_contracts[5], setup_contracts[0]

    transparent_token.mint(penpie_adapter, 100e18, {"from": owner})
    assert transparent_token.balanceOf(penpie_adapter) == 100e18

    epoch = bribeManager.exactCurrentEpoch()

    tx = penpie_adapter.updateReward({"from": owner})
    assert "RewardsDistributed" in tx.events

    bribe = bribeManager.getBribesInPool(epoch, 0, {'from': owner})
    assert bribe[0][0] == transparent_token.address
    assert bribe[0][1] == 100e18
    