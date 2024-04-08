from brownie import accounts, chain
import brownie


def test_distributeRewards(setup_contracts, owner, approved_account, floorToWeek, daysInSeconds):
    token, voting_escrow, gauge_controller, penpie_adapter, cashier = (
        setup_contracts[0], setup_contracts[1], setup_contracts[2], setup_contracts[3],
        setup_contracts[6])

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


def test_currentRewards(setup_contracts, owner, approved_account, floorToWeek, daysInSeconds):
    token, voting_escrow, gauge_controller, penpie_adapter, cashier = (
        setup_contracts[0], setup_contracts[1], setup_contracts[2], setup_contracts[3],
        setup_contracts[6])

    amount = cashier.globalWeekEmission()

    lp = accounts[2]
    oracle = accounts[4]

    week = daysInSeconds(7)

    current_week = gauge_controller.timeTotal()

    scenarios = [
        # Scenario 1: No current rewards when no vote weight is in effect.
        {"CurrentRewards": 0, "NextRewardTime": 0, "GaugeRelativeWeight": 0},

        # Scenario 2: No additional current rewards if they have already been distributed.
        {"CurrentRewards": 0, "NextRewardTime": current_week + week, "GaugeRelativeWeight": 1e18},

        # Scenario 3: Current rewards account only for the relative weight in the current week,
        # despite existing distribution gaps.
        {"CurrentRewards": amount, "NextRewardTime": current_week + week, "GaugeRelativeWeight": 1e18},
    ]

    lock_end = floorToWeek(chain.time()) + 5 * week
    token.mint(lp, amount, {"from": owner})
    token.approve(voting_escrow, amount, {"from": lp})
    voting_escrow.createLock(amount, lock_end, {"from": lp})
    gauge_controller.voteForGaugeWeight(penpie_adapter, gauge_controller.PREC(), {'from': lp})

    for i, s in enumerate(scenarios):
        if i == 0:
            chain.sleep(week)
        elif i == 1:
            token.mint(approved_account, amount, {"from": owner})
            token.approve(cashier, amount, {"from": approved_account})
            tx = cashier.distributeRewards(penpie_adapter, {'from': oracle})
            assert len(tx.events['RewardsDistributed']) == 2
            assert token.balanceOf(approved_account) == 0
        else:
            for _ in range(3):
                token.mint(approved_account, amount, {"from": owner})
                token.approve(cashier, amount, {"from": approved_account})
                chain.sleep(week)
                gauge_controller.checkpointGauge(penpie_adapter, {"from": oracle})

        assert cashier.currentRewards(penpie_adapter) == s['CurrentRewards']
        assert cashier.nextRewardTime(penpie_adapter) == s['NextRewardTime']
        assert gauge_controller.gaugeRelativeWeight(penpie_adapter) == s['GaugeRelativeWeight']


def test_setGlobalEmissionRate(setup_contracts, owner):
    cashier = setup_contracts[6]

    amount = cashier.globalWeekEmission()

    tx = cashier.setGlobalEmissionRate(amount*2, {"from": owner})
    assert "GlobalEmissionRateSet" in tx.events
    assert cashier.globalWeekEmission() == 2*amount

