import brownie


def test_addBribeERC20(fn_isolation, setup_contracts, owner):
    penpie_adapter, bribeManager, token = setup_contracts[3], setup_contracts[5], setup_contracts[0]

    # Scenario 1: No status change if the balance is zero
    tx = penpie_adapter.updateReward({"from": owner})
    assert "RewardsDistributed" not in tx.events

    # Scenario 2: The balance will be distributed as a bribe; the allowance will be approved automatically.
    amt = 100e18
    token.mint(penpie_adapter, amt, {"from": owner})
    assert token.balanceOf(penpie_adapter) == amt

    tx = penpie_adapter.updateReward({"from": owner})
    assert "Approval" in tx.events
    assert "RewardsDistributed" in tx.events
    assert token.balanceOf(penpie_adapter) == 0
    assert token.balanceOf(bribeManager) == amt

    epoch = bribeManager.exactCurrentEpoch()
    bribe = bribeManager.getBribesInPool(epoch, 0, {'from': owner})
    assert bribe[0][0] == token.address
    assert bribe[0][1] == amt

    # Scenario 3: updateReward can be called during the contract pause.
    token.mint(penpie_adapter, amt, {"from": owner})
    assert token.balanceOf(penpie_adapter) == amt

    penpie_adapter.pause({"from": owner})
    assert penpie_adapter.paused()

    tx = penpie_adapter.updateReward({"from": owner})
    assert "RewardsDistributed" in tx.events

    penpie_adapter.unpause({"from": owner})
    assert not token.paused()
    