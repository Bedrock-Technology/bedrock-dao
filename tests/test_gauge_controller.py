import brownie
from brownie import accounts, chain
import time
import secrets

from tests.utils import get_week, estimatedVotingPower


def test_addType(setup_contracts, owner):
    gauge_controller = setup_contracts[2]
    wt = 1
    oracle = accounts[4]
    n_gauge_types = gauge_controller.nGaugeTypes()
    next_week = get_week(1)
    scheduled_total_wt = gauge_controller.getTotalWeight(next_week)
    assert gauge_controller.getLastTotalWtScheduleTime() == next_week

    # Scenario 1: Only an administrator can add type.
    with brownie.reverts():
        gauge_controller.addType("TypeX", 0, {'from': oracle})

    # Scenario 2: Can't add type with empty name
    with brownie.reverts("Empty type name"):
        gauge_controller.addType("", 0, {'from': owner})

    # Scenario 3: Type added and weight adjusted accordingly.
    sub_scenarios = [
        # sub-scenario 1: Add type with zero weight.
        {"typeName": "TypeX", "nGaugeTypes": n_gauge_types+1, "typeWeightScheduled": 0, "typeWtScheduleTime": 0,
         "scheduledTotalWt": scheduled_total_wt, "totalWtScheduledTime": next_week},

        # sub-scenario 2: Add type with positive weight
        {"typeName": "TypeY", "nGaugeTypes": n_gauge_types+2, "typeWeightScheduled": wt, "typeWtScheduleTime": next_week,
         "scheduledTotalWt": scheduled_total_wt, "totalWtScheduledTime": next_week},
    ]

    for s in sub_scenarios:
        tx = gauge_controller.addType(s["typeName"], s["typeWeightScheduled"], {'from': owner})
        if s["typeWeightScheduled"] > 0:
            assert "TypeWeightUpdated" in tx.events
        assert "TypeAdded" in tx.events
        assert gauge_controller.nGaugeTypes() == s["nGaugeTypes"]

        assert gauge_controller.getTypeWeight(s["nGaugeTypes"]-1) == 0
        assert gauge_controller.getTypeWeight(s["nGaugeTypes"]-1, next_week) == s["typeWeightScheduled"]
        assert gauge_controller.getLastTypeWtScheduleTime(s["nGaugeTypes"]-1) == s["typeWtScheduleTime"]

        assert gauge_controller.getTotalWeight() == 0
        assert gauge_controller.getLastTotalWtScheduleTime() == s["totalWtScheduledTime"]
        assert gauge_controller.getTotalWeight(next_week) == s["scheduledTotalWt"]

    # Scenario 4: Can't add more types beyond MAX_NUM
    for i in range(int(1e3 - n_gauge_types - 2)):
        tx = gauge_controller.addType(secrets.token_hex(5 // 2), 0, {'from': owner})
        assert "TypeAdded" in tx.events
    with brownie.reverts("Can't add more gauge types"):
        gauge_controller.addType(secrets.token_hex(5 // 2), 0, {'from': owner})

# TODO: To be optimized
# def test_changeGaugeBaseWeight(setup_contracts, owner, zero_address):
#     token, gauge_controller = setup_contracts[0], setup_contracts[2]
#
#     w0 = 100*1e18
#
#     gauges = gauge_controller.getGaugeList()
#     assert gauge_controller.getGaugeWeight(gauges[0]) == 0
#     assert gauge_controller.getGaugeWeight(gauges[0], get_week(1)) == 100*1e18
#     w0_old = gauge_controller.gaugeData(gauges[0])[2]
#     assert w0_old == 100*1e18
#     assert gauge_controller.getTypeWeight(0) == 0
#     assert gauge_controller.getTypeWeight(0, get_week(1)) == 1
#     assert gauge_controller.getWeightsSumPerType(0) == 0
#     assert gauge_controller.getWeightsSumPerType(0, get_week(1)) == 100*1e18
#     assert gauge_controller.getTotalWeight() == 0
#     assert gauge_controller.getTotalWeight(get_week(1)) == 100*1e18
#
#     fake_gauge = accounts[3]
#     oracle = accounts[4]
#
#     # Scenario 1: Only an administrator can change base weight.
#     with brownie.reverts():
#         gauge_controller.changeGaugeBaseWeight(fake_gauge, w0, {'from': oracle})
#
#     # Scenario 2: Can't change the base weight for a gauge that hasn't been added yet.
#     with brownie.reverts("Gauge not added"):
#         gauge_controller.changeGaugeBaseWeight(fake_gauge, w0, {'from': owner})
#
#     # Scenario 3: Base weight will be scheduled for next week.
#     tx = gauge_controller.changeGaugeBaseWeight(gauges[0], w0, {'from': owner})
#     assert "GaugeBaseWeightUpdated" in tx.events
#
#     # Scenario 4: The historical data of base weight, gauge weight, sum weight, type weight, and total weight will be recorded. #  TODO: 100 break


# TODO: To be optimized
# """
# Test vote for gauge weight - happy path
# """
# def test_vote_for_gauge_weight__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve, gauge = setup_contracts[0], setup_contracts[1], setup_contracts[2]
#     amount = 100e18
#
#     voter1 = accounts[2]
#     voter2 = accounts[3]
#     voters = [voter1,voter2]
#
#     lp_gauge1 = accounts[8]
#     lp_gauge2 = accounts[9]
#
#     tx = gauge.addType("TYPE0", 1, {'from':owner})
#     assert "TypeAdded" in tx.events
#
#     tx = gauge.addGauge(lp_gauge1, 0, 0, {'from':owner})
#
#     """
#     test nGauges
#     """
#     assert gauge.nGauges() == 1
#     assert "GaugeAdded" in tx.events
#
#     tx = gauge.addGauge(lp_gauge2, 0, 0, {'from':owner})
#
#     assert gauge.nGauges() == 2
#     assert "GaugeAdded" in tx.events
#
#     """
#     test voteForGaugeWeight
#     """
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(365))
#     for voter in voters:
#         token.mint(voter, amount, {"from": owner})
#         token.approve(ve, amount, {"from": voter})
#         ve.createLock(amount,lockEnd, {"from": voter})
#
#     _, slope, ts = ve.getLastUserPoint(voter1)
#     assert ve.balanceOf(voter1, ts) == estimatedVotingPower(amount, ve.lockEnd(voter1)-ts)
#
#     tx = gauge.voteForGaugeWeight(lp_gauge1, 5000, {'from': voter1})
#     assert "GaugeVoted" in tx.events
#
#     tx = gauge.voteForGaugeWeight(lp_gauge2, 8000, {'from': voter2})
#     assert "GaugeVoted" in tx.events
#
#     """
#     test gaugeRelativeWeight
#     """
#     vp1 = 0.5 * slope * (ve.lockEnd(voter1)-ts)
#     vp2 = 0.8 * slope * (ve.lockEnd(voter2)-ts)
#
#     expectedRelativeWeight = round(vp1/(vp1+vp2), 2)
#     gotRelativeWeight = round(gauge.gaugeRelativeWeight(lp_gauge1, get_week(1))/1e18, 2)
#
#     assert expectedRelativeWeight == gotRelativeWeight
#
#     """
#     test getUserVotesWtForGauge
#     """
#     expectedWt = round(0.5 * slope * (ve.lockEnd(voter1) - get_week(1))/1e18, 2)
#     gotWt = round(gauge.getUserVotesWtForGauge(lp_gauge1, get_week(1))/1e18, 2)
#     assert gotWt == expectedWt
#
#     """
#     test userVoteData
#     """
#
#     voteData = gauge.userVoteData(voter1, lp_gauge1)
#     _, slope, _ = ve.getLastUserPoint(voter1)
#     assert voteData[0] == 0.5 * slope
#     assert voteData[1] == 5000
#     assert voteData[2] == ve.lockEnd(voter1)