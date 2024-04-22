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

def test_resetAllowance(fn_isolation, users, setup_contracts, owner):
    penpie_adapter, bribeManager, token = setup_contracts[3], setup_contracts[5], setup_contracts[0]

    # Scenario 1: Only the owner are allowed to reset allowance
    with brownie.reverts():
        penpie_adapter.resetAllowance({"from": users[0]})

    # Scenario 2: Scenario 1: No effects will take place if the current allowance is zero.
    tx = penpie_adapter.resetAllowance({"from": owner})
    assert "ResetAllowanceForBribeManager" not in tx.events

    # Scenario 3: Scenario 1: If the current allowance is greater than zero, it will be reset to zero.
    amt = 100e18
    token.approve(bribeManager, amt, {"from": penpie_adapter})
    assert token.allowance(penpie_adapter, bribeManager) > 0

    tx = penpie_adapter.resetAllowance({"from": owner})
    assert "ResetAllowanceForBribeManager" in tx.events
    assert token.allowance(penpie_adapter, bribeManager) == 0



