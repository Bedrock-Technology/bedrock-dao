from brownie import accounts, chain


def test_updateReward(setup_contracts, owner, floorToWeek, daysInSeconds):
    token, voting_escrow, ve_rewards = setup_contracts[0], setup_contracts[1], setup_contracts[5]
    amount = 100e18
    oracle = accounts[4]
    current_week = floorToWeek(chain.time())
    next_week = floorToWeek(chain.time() + daysInSeconds(7))

    scenarios = [
        # Scenario 1: No rewards have been minted yet. Executing updateReward will not change the contract status.
        {"Rewards": 0, "AccountedBalance": 0, "WeeklyProfits": 0, "LastProfitsUpdate": current_week,
         "AccountedRewards": 0, "RewardUpdated": False},

        # Scenario 2: Some rewards have been minted beforehand. Executing updateReward will result in the scheduled
        # release of rewards next week.
        {"Rewards": amount, "AccountedBalance": amount, "WeeklyProfits": amount, "LastProfitsUpdate": next_week,
         "AccountedRewards": amount, "RewardUpdated": True},
    ]

    for s in scenarios:
        token.mint(ve_rewards, s['Rewards'], {"from": owner})
        tx = ve_rewards.updateReward({"from": oracle})
        assert token.balanceOf(ve_rewards) == s['Rewards']
        assert ve_rewards.accountedBalance() == s['AccountedBalance']
        assert ve_rewards.weeklyProfits(next_week) == s['WeeklyProfits']
        assert ve_rewards.lastProfitsUpdate() == s['LastProfitsUpdate']
        assert ve_rewards.accountedRewards() == s['AccountedRewards']
        assert ("RewardUpdated" in tx.events) == s['RewardUpdated']
        if "RewardUpdated" in tx.events:
            assert (tx.events["RewardUpdated"][0]["amount"] == s['AccountedRewards'])


def test_getPendingReward(setup_contracts, owner, floorToWeek, daysInSeconds):
    token, voting_escrow, ve_rewards = setup_contracts[0], setup_contracts[1], setup_contracts[5]
    amount = voting_escrow.MAXTIME()
    lp1 = accounts[2]
    lp2 = accounts[3]
    lps = [lp1, lp2]

    oracle = accounts[4]
    week = daysInSeconds(7)

    max_weeks = ve_rewards.MAXWEEKS()   # 50
    max_pending_profits = (max_weeks-1) * amount

    week0 = ve_rewards.genesisWeek()
    week1 = week0 + week
    week2 = week1 + week
    week3 = week2 + week
    week4 = week3 + week
    week5 = week4 + week
    week51 = week0 + 51 * week
    week62 = week0 + 62 * week

    current_week = week0
    lock_weeks = 60

    scenarios = [
        # Scenario 0 (Week 0): No lock created. Querying getPendingReward results in no profits.
        {"ScheduledWeeklyProfits": 0, "IndividualPendingProfits": 0, "SettleToWeek": week0,
         "LastProfitsUpdate": week0, "TotalMintedRewards": 0, "TotalPendingProfits": 0},

        # Scenario 1 (Week 1): LPs created locks, but VE rewards have not been generated yet. Querying getPendingReward
        # results in no profits.
        {"ScheduledWeeklyProfits": 0, "IndividualPendingProfits": 0, "SettleToWeek": week1,
         "LastProfitsUpdate": week0, "TotalMintedRewards": 0, "TotalPendingProfits": 0},

        # Scenario 2 (Week 2): VE rewards have been generated and updated after locks. Querying getPendingReward results
        # in no profits because Week 2's rewards are scheduled for release in Week 3.
        {"ScheduledWeeklyProfits": 0, "IndividualPendingProfits": 0, "SettleToWeek": week2,
         "LastProfitsUpdate": week3, "TotalMintedRewards": amount, "TotalPendingProfits": 0},

        # Scenario 3 (Week 3): Week 2's rewards are pending for claim, while Week 3's rewards are scheduled for release
        # in Week 4.
        {"ScheduledWeeklyProfits": amount, "IndividualPendingProfits": amount/2, "SettleToWeek": week3,
         "LastProfitsUpdate": week4, "TotalMintedRewards": 2 * amount, "TotalPendingProfits": amount},

        # Scenario 4 (Week 4): Week 2 and Week 3's rewards are pending for claim, while Week 4's has no extra rewards
        # because locks has expired
        {"ScheduledWeeklyProfits": amount, "IndividualPendingProfits": amount, "SettleToWeek": week4,
         "LastProfitsUpdate": week5, "TotalMintedRewards": 2 * amount, "TotalPendingProfits": 2 * amount},

        # Scenario 5 (Week 62): GetPendingReward calculates profits for a maximum of 50 weeks
        # since the last settled week.
        {"ScheduledWeeklyProfits": 0, "IndividualPendingProfits": max_pending_profits/2, "SettleToWeek": week51,
         "LastProfitsUpdate": week62, "TotalMintedRewards": lock_weeks * amount, "TotalPendingProfits": max_pending_profits},
    ]

    next_index = 0
    for s in scenarios:
        # Create locks in week 1
        if next_index == 1:
            lock_end = floorToWeek(chain.time()) + (lock_weeks +1) * week
            for lp in lps:
                token.mint(lp, amount, {"from": owner})
                token.approve(voting_escrow, amount, {"from": lp})
                voting_escrow.createLock(amount, lock_end, {"from": lp})

        # Generate rewards if locks have not yet expired.
        if voting_escrow.totalSupply(current_week) > 0:
            token.mint(ve_rewards, amount, {"from": owner})
            ve_rewards.updateReward({"from": oracle})
        assert ve_rewards.lastProfitsUpdate() == s['LastProfitsUpdate']

        # Check pending rewards
        total_profits = 0
        for lp in lps:
            pending_profits, settle_to_week = ve_rewards.getPendingReward(lp)
            total_profits += pending_profits
            assert pending_profits == s['IndividualPendingProfits']
            assert settle_to_week == s['SettleToWeek']
        # assert token.balanceOf(ve_rewards) == s['TotalMintedRewards']
        assert total_profits == s['TotalPendingProfits']
        assert ve_rewards.weeklyProfits(current_week) == s['ScheduledWeeklyProfits']

        # Fast forward block time by one week
        chain.sleep(week)
        current_week += week
        next_index = next_index + 1
        ve_rewards.updateReward({"from": oracle})

        if next_index == 5:
            for _ in range(lock_weeks-2):
                # Generate rewards if locks have not yet expired.
                if voting_escrow.totalSupply(current_week) > 0:
                    token.mint(ve_rewards, amount, {"from": owner})
                    ve_rewards.updateReward({"from": oracle})

                # Fast forward block time by one week
                chain.sleep(week)
                current_week += week
                next_index = next_index + 1
                ve_rewards.updateReward({"from": oracle})




