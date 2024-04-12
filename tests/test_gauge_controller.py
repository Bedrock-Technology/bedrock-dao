import brownie
from brownie import accounts, chain
import time
import secrets
import os

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


def test_changeTypeWeight(setup_contracts, owner, oracle, daysInSeconds):
    gauge_controller = setup_contracts[2]
    week = daysInSeconds(7)
    start_week = get_week(0)
    next_week = get_week(1)
    gauges = gauge_controller.getGaugeList()
    assert len(gauges) == 2
    assert gauge_controller.getTotalWeight(next_week) == 200 * 1e18
    assert gauge_controller.getLastTotalWtScheduleTime() == next_week
    for i in range(2):
        assert gauge_controller.getLastTypeWtScheduleTime(i) == next_week
        assert gauge_controller.getTypeWeight(i, next_week) == 1
        assert gauge_controller.gaugeRelativeWeight(gauges[i], next_week) == 5 * 1e17

    # Scenario 1: Only an administrator can change type weight.
    with brownie.reverts():
        gauge_controller.changeTypeWeight(0, 0, {'from': oracle})

    # Scenario 2: Can't change type weight for a type that hasn't been registered yet.
    with brownie.reverts("Gauge Type hasn't been registered yet"):
        gauge_controller.changeTypeWeight(2, 0, {'from': owner})

    # Scenario 3: Type weight changed and total weight and gauge relative weight adjusted accordingly over time
    for i in range(5):
        chain.sleep(week)
        tx = gauge_controller.changeTypeWeight(1, 3, {'from': owner})
        assert get_week() == start_week + week * (i+1)
        assert "TypeWeightUpdated" in tx.events
        assert gauge_controller.getTotalWeight(get_week(i+1)) == 400 * 1e18
        assert gauge_controller.getLastTotalWtScheduleTime() == start_week + week * (i+2)
        assert gauge_controller.getTypeWeight(1, get_week(i+1)) == 3
        assert gauge_controller.gaugeRelativeWeight(gauges[0], get_week(i+1)) == 25 * 1e16
        assert gauge_controller.gaugeRelativeWeight(gauges[1], get_week(i+1)) == 75 * 1e16
        assert gauge_controller.getLastTypeWtScheduleTime(1) == start_week + week * (i+2)
    total_wt_schedule_time = gauge_controller.getLastTotalWtScheduleTime()
    type_wt_schedule_time = gauge_controller.getLastTypeWtScheduleTime(1)
    current_week = get_week()
    for i in range(5):
        next_week = current_week + (i+1) * week
        assert gauge_controller.getTotalWeight(next_week) == 400 * 1e18
        assert gauge_controller.getLastTotalWtScheduleTime() == total_wt_schedule_time
        assert gauge_controller.getTypeWeight(1, next_week) == 3
        assert gauge_controller.gaugeRelativeWeight(gauges[0], next_week) == 25 * 1e16
        assert gauge_controller.gaugeRelativeWeight(gauges[1], next_week) == 75 * 1e16
        assert gauge_controller.getLastTypeWtScheduleTime(1) == type_wt_schedule_time


def test_addGauge(setup_contracts, owner, oracle, zero_address, w3):
    gauge_controller = setup_contracts[2]
    fake_gauge = w3.eth.account.create(os.urandom(32)).address
    weight = 200*1e18
    gauges = gauge_controller.getGaugeList()
    n_gauge_types = gauge_controller.nGaugeTypes()
    n_gauges = gauge_controller.nGauges()
    assert len(gauges) == 2

    # Scenario 1: The execution will revert due to invalid inputs.
    scenarios = [
        # Sub-Scenario 1: Only an authorized operator can add gauge.
        {"gAddr": fake_gauge, "gType": 0, "weight": weight, "from": oracle,
         "revert": ""},

        # Sub-Scenario 2: Can't add a gauge with the zero address.
        {"gAddr": zero_address, "gType": 0, "weight": weight, "from": owner,
         "revert": "Invalid address"},

        # Sub-Scenario 3: Can't add a gauge with invalid gauge type.
        {"gAddr": fake_gauge, "gType": n_gauge_types, "weight": weight, "from": owner,
         "revert": "Invalid gauge type"},

        # Sub-Scenario 4: Can't add an already registered gauge
        {"gAddr": gauges[0], "gType": 0, "weight": weight, "from": owner,
         "revert": "Gauge already registered"},

        # Sub-Scenario 5: Can't add more gauges than MAX_NUM_GAUGES (Ignored because it takes too long.)
        # {"gAddr": fake_gauge, "gType": 0, "weight": weight, "from": owner,
        #  "revert": "Can't add more gauges"},
    ]

    for s in scenarios:
        with brownie.reverts(s['revert']):
            gauge_controller.addGauge(s['gAddr'], s['gType'], s['weight'], {'from': s['from']})

    # Scenario 2: Successfully adding the gauge and the relative weight will take effect over time.
    tx = gauge_controller.addGauge(fake_gauge, 0, weight, {'from': owner})
    assert "GaugeAdded" in tx.events

    assert gauge_controller.nGauges() == n_gauges + 1
    assert len(gauge_controller.getGaugeList()) == n_gauges + 1
    assert gauge_controller.gaugeType(fake_gauge) == 0

    assert gauge_controller.gaugeRelativeWeight(fake_gauge) == 0
    assert gauge_controller.gaugeRelativeWeight(fake_gauge, get_week(1)) == 5*1e17
    assert gauge_controller.gaugeRelativeWeight(fake_gauge, get_week(2)) == 5*1e17

    assert gauge_controller.getGaugeWeight(fake_gauge) == 0
    assert gauge_controller.getGaugeWeight(fake_gauge, get_week(1)) == 200*1e18
    assert gauge_controller.getGaugeWeight(fake_gauge, get_week(2)) == 200*1e18

    assert gauge_controller.getGaugeWeight(fake_gauge) == 0
    assert gauge_controller.getGaugeWeight(fake_gauge, get_week(1)) == 200*1e18
    assert gauge_controller.getGaugeWeight(fake_gauge, get_week(2)) == 200*1e18

    assert gauge_controller.getGaugeBaseWeight(fake_gauge) == 0
    assert gauge_controller.getGaugeBaseWeight(fake_gauge, get_week(1)) == 200*1e18
    assert gauge_controller.getGaugeBaseWeight(fake_gauge, get_week(2)) == 200*1e18

    assert gauge_controller.getTotalWeight() == 0
    assert gauge_controller.getTotalWeight(get_week(1)) == 400*1e18
    assert gauge_controller.getTotalWeight(get_week(2)) == 400*1e18

    assert gauge_controller.getWeightsSumPerType(0) == 0
    assert gauge_controller.getWeightsSumPerType(0, get_week(1)) == 300*1e18
    assert gauge_controller.getWeightsSumPerType(0, get_week(2)) == 300*1e18

    assert gauge_controller.getLastGaugeWtScheduleTime(fake_gauge) == get_week(1)
    assert gauge_controller.getLastGaugeBaseWtScheduleTime(fake_gauge) == get_week(1)
    assert gauge_controller.getLastSumWtScheduleTime(1) == get_week(1)
    assert gauge_controller.getLastTotalWtScheduleTime() == get_week(1)


def test_changeGaugeBaseWeight(setup_contracts, owner, oracle, w3):
    gauge_controller = setup_contracts[2]
    fake_gauge = w3.eth.account.create(os.urandom(32)).address
    weight = 300*1e18
    gauges = gauge_controller.getGaugeList()
    assert len(gauges) == 2

    # Scenario 1: The execution will revert due to invalid inputs.
    scenarios = [
        # Sub-Scenario 1: Only the administrator can change gauge base weight.
        {"gAddr": fake_gauge, "newW0": weight, "from": oracle,
         "revert": ""},

        # Sub-Scenario 2: Can't change the base weight of a gauge that hasn't been added.
        {"gAddr": fake_gauge, "newW0": weight, "from": owner,
         "revert": "Gauge not added"},
    ]

    for s in scenarios:
        with brownie.reverts(s['revert']):
            gauge_controller.changeGaugeBaseWeight(s['gAddr'], s['newW0'], {'from': s['from']})

    # Scenario 2: Successfully changing the gauge base weight and the relative weight will take effect over time.
    tx = gauge_controller.changeGaugeBaseWeight(gauges[0], weight, {'from': owner})
    assert "GaugeBaseWeightUpdated" in tx.events

    assert gauge_controller.gaugeRelativeWeight(gauges[0]) == 0
    assert gauge_controller.gaugeRelativeWeight(gauges[0], get_week(1)) == 75*1e16
    assert gauge_controller.gaugeRelativeWeight(gauges[0], get_week(2)) == 75*1e16

    assert gauge_controller.getGaugeWeight(gauges[0]) == 0
    assert gauge_controller.getGaugeWeight(gauges[0], get_week(1)) == 300*1e18
    assert gauge_controller.getGaugeWeight(gauges[0], get_week(2)) == 300*1e18

    assert gauge_controller.getGaugeBaseWeight(gauges[0]) == 0
    assert gauge_controller.getGaugeBaseWeight(gauges[0], get_week(1)) == 300*1e18
    assert gauge_controller.getGaugeBaseWeight(gauges[0], get_week(2)) == 300*1e18

    assert gauge_controller.getTotalWeight() == 0
    assert gauge_controller.getTotalWeight(get_week(1)) == 400*1e18
    assert gauge_controller.getTotalWeight(get_week(2)) == 400*1e18

    assert gauge_controller.getWeightsSumPerType(0) == 0
    assert gauge_controller.getWeightsSumPerType(0, get_week(1)) == 300*1e18
    assert gauge_controller.getWeightsSumPerType(0, get_week(2)) == 300*1e18

    assert gauge_controller.getLastGaugeWtScheduleTime(gauges[0]) == get_week(1)
    assert gauge_controller.getLastGaugeBaseWtScheduleTime(gauges[0]) == get_week(1)
    assert gauge_controller.getLastSumWtScheduleTime(1) == get_week(1)
    assert gauge_controller.getLastTotalWtScheduleTime() == get_week(1)


def test_checkpoint(setup_contracts, owner, daysInSeconds):
    gauge_controller = setup_contracts[2]
    week = daysInSeconds(7)
    week0 = get_week(0)
    week1 = get_week(1)
    gauges = gauge_controller.getGaugeList()

    scenarios = [
        # Scenario 1： Each checkpoint request can fill historical data from the past 100 weeks.
        {"sleepWeeks": 100, "updatedScheduleTime": week0 + 101 * week},

        # Scenario 2： Each checkpoint request cannot fill historical data beyond the past 100 weeks.
        {"sleepWeeks": 200, "updatedScheduleTime": week0 + 201 * week},
    ]

    for s in scenarios:
        chain.sleep(week * s['sleepWeeks'])
        gauge_controller.checkpoint({'from': owner})

        for g in gauges:
            assert gauge_controller.getLastGaugeWtScheduleTime(g) == week1
            assert gauge_controller.getLastGaugeBaseWtScheduleTime(g) == week1
        assert gauge_controller.getLastSumWtScheduleTime(1) == s['updatedScheduleTime']
        assert gauge_controller.getLastTypeWtScheduleTime(1) == s['updatedScheduleTime']
        assert gauge_controller.getLastTotalWtScheduleTime() == s['updatedScheduleTime']

        assert gauge_controller.gaugeRelativeWeight(gauges[0]) == 5*1e17
        assert gauge_controller.gaugeRelativeWeight(gauges[0], get_week(1)) == 5*1e17
        assert gauge_controller.gaugeRelativeWeight(gauges[0], get_week(2)) == 5*1e17

        assert gauge_controller.getGaugeWeight(gauges[0]) == 100*1e18
        assert gauge_controller.getGaugeWeight(gauges[0], get_week(1)) == 100*1e18
        assert gauge_controller.getGaugeWeight(gauges[0], get_week(2)) == 100*1e18

        assert gauge_controller.getGaugeBaseWeight(gauges[0]) == 100*1e18
        assert gauge_controller.getGaugeBaseWeight(gauges[0], get_week(1)) == 100*1e18
        assert gauge_controller.getGaugeBaseWeight(gauges[0], get_week(2)) == 100*1e18

        assert gauge_controller.getTypeWeight(0) == 1
        assert gauge_controller.getTypeWeight(0, get_week(1)) == 1
        assert gauge_controller.getTypeWeight(0, get_week(1)) == 1

        assert gauge_controller.getTotalWeight() == 200*1e18
        assert gauge_controller.getTotalWeight(get_week(1)) == 200*1e18
        assert gauge_controller.getTotalWeight(get_week(2)) == 200*1e18

        assert gauge_controller.getWeightsSumPerType(0) == 100*1e18
        assert gauge_controller.getWeightsSumPerType(0, get_week(1)) == 100*1e18
        assert gauge_controller.getWeightsSumPerType(0, get_week(2)) == 100*1e18


def test_checkpointGauge(setup_contracts, owner, daysInSeconds):
    gauge_controller = setup_contracts[2]
    week = daysInSeconds(7)
    week0 = get_week(0)
    week1 = get_week(1)
    gauges = gauge_controller.getGaugeList()

    scenarios = [
        # Scenario 1： Each gauge checkpoint request can fill historical data from the past 100 weeks.
        {"sleepWeeks": 100, "gaugeWtUpdatedScheduleTime": week0 + 101 * week,
         "totalWtUpdatedScheduleTime": week0 + 101 * week},

        # Scenario 2： Each gauge checkpoint request cannot fill historical data beyond the past 100 weeks.
        {"sleepWeeks": 200, "gaugeWtUpdatedScheduleTime": week0 + 201 * week,
         "totalWtUpdatedScheduleTime": week0 + 301 * week},
    ]

    for s in scenarios:
        # Note: Weekly checkpoints are established to prevent unexpected reversion during the checkpointGauge due to
        # gas limit constraints. Specifically, the checkpointGauge executes _getTotal in conjunction with _getWeight;
        # both functions contain loops that can iterate numerous times, potentially causing calculation costs to exceed
        # the gas limit.
        for _ in range(s['sleepWeeks']):
            chain.sleep(week)
            gauge_controller.checkpoint({'from': owner})
        gauge_controller.checkpointGauge(gauges[0], {'from': owner})

        assert gauge_controller.getLastGaugeWtScheduleTime(gauges[0]) == s['gaugeWtUpdatedScheduleTime']
        assert gauge_controller.getLastGaugeBaseWtScheduleTime(gauges[1]) == week1

        assert gauge_controller.getLastSumWtScheduleTime(1) == s['totalWtUpdatedScheduleTime']
        assert gauge_controller.getLastTypeWtScheduleTime(1) == s['totalWtUpdatedScheduleTime']
        assert gauge_controller.getLastTotalWtScheduleTime() == s['totalWtUpdatedScheduleTime']

        assert gauge_controller.gaugeRelativeWeight(gauges[0]) == 5*1e17
        assert gauge_controller.gaugeRelativeWeight(gauges[0], get_week(1)) == 5*1e17
        assert gauge_controller.gaugeRelativeWeight(gauges[0], get_week(2)) == 5*1e17

        assert gauge_controller.getGaugeWeight(gauges[0]) == 100*1e18
        assert gauge_controller.getGaugeWeight(gauges[0], get_week(1)) == 100*1e18
        assert gauge_controller.getGaugeWeight(gauges[0], get_week(2)) == 100*1e18

        assert gauge_controller.getGaugeBaseWeight(gauges[0]) == 100*1e18
        assert gauge_controller.getGaugeBaseWeight(gauges[0], get_week(1)) == 100*1e18
        assert gauge_controller.getGaugeBaseWeight(gauges[0], get_week(2)) == 100*1e18

        assert gauge_controller.getTypeWeight(0) == 1
        assert gauge_controller.getTypeWeight(0, get_week(1)) == 1
        assert gauge_controller.getTypeWeight(0, get_week(1)) == 1

        assert gauge_controller.getTotalWeight() == 200*1e18
        assert gauge_controller.getTotalWeight(get_week(1)) == 200*1e18
        assert gauge_controller.getTotalWeight(get_week(2)) == 200*1e18

        assert gauge_controller.getWeightsSumPerType(0) == 100*1e18
        assert gauge_controller.getWeightsSumPerType(0, get_week(1)) == 100*1e18
        assert gauge_controller.getWeightsSumPerType(0, get_week(2)) == 100*1e18


def test_checkpointGauge_in_batch(setup_contracts, owner, daysInSeconds):
    gauge_controller = setup_contracts[2]
    week = daysInSeconds(7)
    week0 = get_week(0)
    gauges = gauge_controller.getGaugeList()

    # Scenario 1： Each gauge checkpoint request can fill historical data from the past weeks.
    sleep_weeks = 50
    updated_schedule_time = week0 + (sleep_weeks + 1) * week
    chain.sleep(week*sleep_weeks)
    gauge_controller.checkpointGauge({'from': owner})

    for g in gauges:
        assert gauge_controller.getLastGaugeWtScheduleTime(g) == updated_schedule_time
        assert gauge_controller.getLastGaugeBaseWtScheduleTime(g) == updated_schedule_time

    for i in range(2):
        assert gauge_controller.getLastSumWtScheduleTime(i) == updated_schedule_time
        assert gauge_controller.getLastTypeWtScheduleTime(i) == updated_schedule_time
        assert gauge_controller.getLastTotalWtScheduleTime() == updated_schedule_time

    for g in gauges:
        assert gauge_controller.gaugeRelativeWeight(g) == 5*1e17
        assert gauge_controller.gaugeRelativeWeight(g, get_week(1)) == 5*1e17
        assert gauge_controller.gaugeRelativeWeight(g, get_week(2)) == 5*1e17

    for g in gauges:
        assert gauge_controller.getGaugeWeight(g) == 100*1e18
        assert gauge_controller.getGaugeWeight(g, get_week(1)) == 100*1e18
        assert gauge_controller.getGaugeWeight(g, get_week(2)) == 100*1e18

    for g in gauges:
        assert gauge_controller.getGaugeBaseWeight(g) == 100*1e18
        assert gauge_controller.getGaugeBaseWeight(g, get_week(1)) == 100*1e18
        assert gauge_controller.getGaugeBaseWeight(g, get_week(2)) == 100*1e18

    for i in range(2):
        assert gauge_controller.getTypeWeight(i) == 1
        assert gauge_controller.getTypeWeight(i, get_week(1)) == 1
        assert gauge_controller.getTypeWeight(i, get_week(1)) == 1

    assert gauge_controller.getTotalWeight() == 200*1e18
    assert gauge_controller.getTotalWeight(get_week(1)) == 200*1e18
    assert gauge_controller.getTotalWeight(get_week(2)) == 200*1e18

    for i in range(2):
        assert gauge_controller.getWeightsSumPerType(i) == 100*1e18
        assert gauge_controller.getWeightsSumPerType(i, get_week(1)) == 100*1e18
        assert gauge_controller.getWeightsSumPerType(i, get_week(2)) == 100*1e18

    # Scenario 2： The checkpoint will revert due to the gas limit, usually because there are too many gaps.
    #
    # Note: Specifically, the checkpointGauge executes _getTotal in conjunction with _getWeight;
    # both functions contain loops that can iterate numerous times, potentially causing calculation costs to exceed
    sleep_weeks = 65
    chain.sleep(week*sleep_weeks)
    with brownie.reverts():
        gauge_controller.checkpointGauge({'from': owner})


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