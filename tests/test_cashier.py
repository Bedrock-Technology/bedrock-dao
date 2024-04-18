from brownie import accounts, chain
import brownie


def test_distributeRewards(fn_isolation, setup_contracts, owner, approved_account, floorToWeek, daysInSeconds):
    token, voting_escrow, gauge_controller, penpie_adapter, cashier = (
        setup_contracts[0], setup_contracts[1], setup_contracts[2], setup_contracts[3],
        setup_contracts[7])

    amount = cashier.globalWeekEmission()

    lp = accounts[2]
    oracle = accounts[4]

    week = daysInSeconds(7)

    current_week = gauge_controller.timeTotal()

    scenarios = [
        # Scenario 1: Rewards can't be distributed while the contract is paused.
        {"RevertMsg": "Pausable: paused", "RewardsDistributed": 0, "NextRewardTime": 0},

        # Scenario 2: Rewards will not be distributed if the given gauge's relative weight is zero.
        {"RevertMsg": "", "RewardsDistributed": 0, "NextRewardTime": current_week},

        # Scenario 3: Rewards may not be distributed more than once per week.
        {"RevertMsg": "Invalid reward distribution", "RewardsDistributed": 0, "NextRewardTime": current_week},

        # Scenario 4: Rewards are normally distributed, and the RewardsDistributed events are emitted.
        {"RevertMsg": "", "RewardsDistributed": 2, "NextRewardTime": current_week + week},
    ]

    lock_end = floorToWeek(chain.time()) + 5 * week
    token.mint(lp, amount, {"from": owner})
    token.approve(voting_escrow, amount, {"from": lp})
    voting_escrow.createLock(amount, lock_end, {"from": lp})
    gauge_controller.voteForGaugeWeight(penpie_adapter, gauge_controller.PREC(), {'from': lp})

    for s in scenarios:
        rvt_msg = s['RevertMsg']
        if rvt_msg == "Pausable: paused":
            cashier.pause({"from": owner})
            assert cashier.paused()
            with brownie.reverts(rvt_msg):
                cashier.distributeRewards(penpie_adapter, {'from': oracle})
            cashier.unpause({"from": owner})
            assert not cashier.paused()
        elif rvt_msg == "Invalid reward distribution":
            with brownie.reverts(rvt_msg):
                cashier.distributeRewards(penpie_adapter, {'from': oracle})

            # Fast forward block time by one week
            chain.sleep(week)

            # Mint rewards
            token.mint(approved_account, amount, {"from": owner})
            token.approve(cashier, amount, {"from": approved_account})
        else:
               tx = cashier.distributeRewards(penpie_adapter, {'from': oracle})
               if s['RewardsDistributed'] == 0:
                   assert "RewardsDistributed" not in tx.events
               else:
                assert len(tx.events['RewardsDistributed']) == s['RewardsDistributed']
               assert token.balanceOf(cashier) == 0
        assert cashier.nextRewardTime(penpie_adapter) == s['NextRewardTime']


def test_currentRewards(fn_isolation, setup_contracts, owner, approved_account, floorToWeek, daysInSeconds):
    token, voting_escrow, gauge_controller, penpie_adapter1, penpie_adapter2, cashier = (
        setup_contracts[0], setup_contracts[1], setup_contracts[2], setup_contracts[3], setup_contracts[4],
        setup_contracts[7])

    amount = cashier.globalWeekEmission()

    penpie_adapters = [penpie_adapter1, penpie_adapter2]

    lp = accounts[2]
    oracle = accounts[4]

    week = daysInSeconds(7)

    start_week = get_week(0)

    lock_end = get_week(5)
    token.mint(lp, amount, {"from": owner})
    token.approve(voting_escrow, amount, {"from": lp})
    voting_escrow.createLock(amount, lock_end, {"from": lp})
    gauge_controller.voteForGaugeWeight(penpie_adapter1, gauge_controller.PREC()/2, {'from': lp})
    gauge_controller.voteForGaugeWeight(penpie_adapter2, gauge_controller.PREC()/2, {'from': lp})

    # Scenario 1: No current rewards when no vote weight is in effect.
    for penpie_adapter in penpie_adapters:
        assert gauge_controller.gaugeRelativeWeight(penpie_adapter) == 0
        assert cashier.currentRewards(penpie_adapter) == 0
    chain.sleep(week)

    # Scenario 2: No additional current rewards if they have already been distributed.
    token.mint(approved_account, amount, {"from": owner})
    token.approve(cashier, amount, {"from": approved_account})

    for penpie_adapter in penpie_adapters:
        assert gauge_controller.gaugeRelativeWeight(penpie_adapter) == 5*1e17
        tx = cashier.distributeRewards(penpie_adapter, {'from': oracle})
        assert len(tx.events['RewardsDistributed']) == 2
        assert cashier.currentRewards(penpie_adapter) == 0
        assert cashier.nextRewardTime(penpie_adapter) == start_week + 2 * week
    assert token.balanceOf(approved_account) == 0

    # Scenario 3: Current rewards account only for the relative weight in the current week,
    # despite existing distribution gaps.
    for _ in range(4):
        token.mint(approved_account, amount, {"from": owner})
        token.approve(cashier, amount, {"from": approved_account})
        chain.sleep(week)
    for penpie_adapter in penpie_adapters:
        assert gauge_controller.gaugeRelativeWeight(penpie_adapter) == 5*1e17
        assert cashier.currentRewards(penpie_adapter) == amount/2
        assert cashier.nextRewardTime(penpie_adapter) == start_week + 2 * week

def test_setGlobalEmissionRate(fn_isolation, setup_contracts, owner):
    cashier = setup_contracts[7]

    amount = cashier.globalWeekEmission()

    tx = cashier.setGlobalEmissionRate(amount*2, {"from": owner})
    assert "GlobalEmissionRateSet" in tx.events
    assert cashier.globalWeekEmission() == 2*amount

