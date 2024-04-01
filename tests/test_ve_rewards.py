from brownie import accounts, chain


def test_update_reward(setup_contracts, owner, floorToWeek, daysInSeconds):
    
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

