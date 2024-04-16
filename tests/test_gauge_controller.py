import brownie
from brownie import accounts, chain
import math
import time
import secrets
import os

from tests.utils import get_week, estimatedLockAmt, estimatedVotingPower


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


def test_weight_decrease_overtime(setup_contracts, owner, users, daysInSeconds):
    token, voting_escrow, gauge_controller = (
        setup_contracts[0], setup_contracts[1], setup_contracts[2])

    four_years = daysInSeconds(4*365)
    week = daysInSeconds(7)
    week1 = get_week(1)
    week2 = get_week(2)
    week3 = get_week(3)
    week6 = get_week(6)

    gauges = gauge_controller.getGaugeList()

    prec = gauge_controller.PREC()

    # sleep_weeks = 50
    # updated_schedule_time = week0 + (sleep_weeks + 1) * week
    # chain.sleep(week*sleep_weeks)

    weeks_in_lock = 4
    voting_power = 700e18
    lock_end = get_week(weeks_in_lock + 1)
    amt_in_lock = estimatedLockAmt(voting_power, weeks_in_lock)
    assert amt_in_lock == 36500e18
    slope = amt_in_lock/four_years

    token.mint(users[0], amt_in_lock, {"from": owner})
    token.approve(voting_escrow, amt_in_lock, {"from": users[0]})

    voting_escrow.createLock(amt_in_lock, lock_end, {"from": users[0]})
    assert voting_escrow.locked(users[0])[0] == amt_in_lock  # amount
    assert voting_escrow.locked(users[0])[1] == lock_end  # end
    assert voting_escrow.lockEnd(users[0]) == lock_end  # end

    gauge_controller.voteForGaugeWeight(gauges[0], prec, {'from': users[0]})
    assert gauge_controller.userVoteData(users[0], gauges[0])[0] == slope   # slope
    assert gauge_controller.userVoteData(users[0], gauges[0])[1] == prec   # power
    assert gauge_controller.userVoteData(users[0], gauges[0])[2] == lock_end   # end
    # assert gauge_controller.userVoteData(users[0], gauges[0])[3] == chain.time()   # voteTime

    gauge_controller.changeGaugeBaseWeight(gauges[0], 0, {'from': owner})

    # Scenario 1： Weights are scheduled to take effect from next week.
    for i in range(2):
        assert gauge_controller.getLastGaugeWtScheduleTime(gauges[i]) == week1
        assert gauge_controller.getLastGaugeBaseWtScheduleTime(gauges[i]) == week1
        assert gauge_controller.getLastTypeWtScheduleTime(i) == week1
        assert gauge_controller.getLastSumWtScheduleTime(i) == week1
    assert gauge_controller.getLastTotalWtScheduleTime() == week1

    assert math.ceil(gauge_controller.gaugeRelativeWeight(gauges[0])/1e15) == 0
    assert math.ceil(gauge_controller.gaugeRelativeWeight(gauges[1])/1e15) == 0
    relative_weight0 = gauge_controller.gaugeRelativeWeight(gauges[0], week1)
    relative_weight1 = gauge_controller.gaugeRelativeWeight(gauges[1], week1)
    assert math.ceil(relative_weight0/1e15) == 875
    assert math.floor(relative_weight1/1e15) == 125
    assert math.ceil((relative_weight0 + relative_weight1)/1e18) == 1

    gauge_weights = [
        {"week0": 0, "week1": 700},
        {"week0": 0, "week1": 100},
    ]
    for i in range(2):
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i])) == gauge_weights[i]['week0']
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i], week1)/1e18) == gauge_weights[i]['week1']

    gauge_base_weights = [
        {"week0": 0, "week1": 0},
        {"week0": 0, "week1": 100e18},
    ]
    for i in range(2):
        assert gauge_controller.getGaugeBaseWeight(gauges[i]) == gauge_base_weights[i]['week0']
        assert gauge_controller.getGaugeBaseWeight(gauges[i], week1) == gauge_base_weights[i]['week1']

    assert gauge_controller.getUserVotesWtForGauge(gauges[0]) == 0
    assert math.ceil(gauge_controller.getUserVotesWtForGauge(gauges[0], week1)/1e18) == voting_power/1e18
    assert gauge_controller.getUserVotesWtForGauge(gauges[1]) == 0
    assert gauge_controller.getUserVotesWtForGauge(gauges[1], week1) == 0

    for i in range(2):
        assert gauge_controller.getTypeWeight(i) == 0
        assert gauge_controller.getTypeWeight(i, week1) == 1

    assert gauge_controller.getTotalWeight() == 0
    assert math.ceil(gauge_controller.getTotalWeight(week1)/1e18) == 800

    assert gauge_controller.getWeightsSumPerType(0) == 0
    assert math.ceil(gauge_controller.getWeightsSumPerType(0, week1)/1e18) == voting_power/1e18
    assert gauge_controller.getWeightsSumPerType(1) == 0
    assert gauge_controller.getWeightsSumPerType(1, week1) == 100e18

    # Scenario 2: Before the lock expires, type weights and base weights will remain constant,
    # while user vote weight decreases over time.
    #
    # Note: All view functions should return consistent weights that will decrease over time even no checkpoints occur
    chain.sleep(week*2)
    token.mint(users[0], amt_in_lock, {"from": owner})

    for i in range(2):
        assert gauge_controller.getLastGaugeWtScheduleTime(gauges[i]) == week1
        assert gauge_controller.getLastGaugeBaseWtScheduleTime(gauges[i]) == week1
        assert gauge_controller.getLastTypeWtScheduleTime(i) == week1
        assert gauge_controller.getLastSumWtScheduleTime(i) == week1
    assert gauge_controller.getLastTotalWtScheduleTime() == week1

    relative_weight0 = math.ceil(gauge_controller.gaugeRelativeWeight(gauges[0])/1e15)
    relative_weight1 = math.floor(gauge_controller.gaugeRelativeWeight(gauges[1])/1e15)
    assert relative_weight0 == math.ceil(1e18 * slope*week*3 / (slope*week*3 + 100e18)/1e15)
    assert relative_weight1 == math.floor(1e18 * 100e18 / (slope*week*3 + 100e18)/1e15)
    assert relative_weight0 + relative_weight1 == 1000

    gauge_weights = [
        {"week2": math.ceil(slope*week*3/1e18), "week3": math.ceil(slope*week*2/1e18)},
        {"week2": 100, "week3": 100},
    ]
    for i in range(2):
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i])/1e18) == gauge_weights[i]['week2']
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i], get_week(1))/1e18) == gauge_weights[i]['week3']

    gauge_base_weights = [
        {"week2": 0, "week3": 0},
        {"week2": 100e18, "week3": 100e18},
    ]
    for i in range(2):
        assert gauge_controller.getGaugeBaseWeight(gauges[i]) == gauge_base_weights[i]['week2']
        assert gauge_controller.getGaugeBaseWeight(gauges[i], get_week(1)) == gauge_base_weights[i]['week3']

    assert math.ceil(gauge_controller.getUserVotesWtForGauge(gauges[0])/1e18) == math.ceil((slope*week*3)/1e18)
    assert math.ceil(gauge_controller.getUserVotesWtForGauge(gauges[0], get_week(1))/1e18) == math.ceil((slope*week*2)/1e18)
    assert gauge_controller.getUserVotesWtForGauge(gauges[1]) == 0
    assert gauge_controller.getUserVotesWtForGauge(gauges[1], get_week(1)) == 0

    for i in range(2):
        assert gauge_controller.getTypeWeight(i) == 1
        assert gauge_controller.getTypeWeight(i, get_week(1)) == 1

    assert math.ceil(gauge_controller.getTotalWeight()/1e18) == math.ceil((slope*week*3)/1e18) + 100
    assert math.ceil(gauge_controller.getTotalWeight(get_week(1))/1e18) == math.ceil((slope*week*2)/1e18) + 100

    assert math.ceil(gauge_controller.getWeightsSumPerType(0)/1e18) == math.ceil((slope*week*3)/1e18)
    assert math.ceil(gauge_controller.getWeightsSumPerType(0, get_week(1))/1e18) == math.ceil((slope*week*2)/1e18)
    assert gauge_controller.getWeightsSumPerType(1) == 100e18
    assert gauge_controller.getWeightsSumPerType(1, get_week(1)) == 100e18

    # Scenario 3: After the lock has expired, type weights and base weights will still remain constant,
    # while user vote weight becomes zero.
    #
    # Note: All view functions should return consistent weights that will decrease over time even no checkpoints occur
    chain.sleep(week*3)
    token.mint(users[0], amt_in_lock, {"from": owner})

    for i in range(2):
        assert gauge_controller.getLastGaugeWtScheduleTime(gauges[i]) == week1
        assert gauge_controller.getLastGaugeBaseWtScheduleTime(gauges[i]) == week1
        assert gauge_controller.getLastTypeWtScheduleTime(i) == week1
        assert gauge_controller.getLastSumWtScheduleTime(i) == week1
    assert gauge_controller.getLastTotalWtScheduleTime() == week1

    relative_weight0 = gauge_controller.gaugeRelativeWeight(gauges[0])
    relative_weight1 = gauge_controller.gaugeRelativeWeight(gauges[1])
    assert relative_weight0 == 0
    assert relative_weight1 == 1e18
    assert relative_weight0 + relative_weight1 == 1e18

    gauge_weights = [
        {"week2": 0, "week3": 0},
        {"week2": 100, "week3": 100},
    ]
    for i in range(2):
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i])/1e18) == gauge_weights[i]['week2']
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i], get_week(1))/1e18) == gauge_weights[i]['week3']

    gauge_base_weights = [
        {"week2": 0, "week3": 0},
        {"week2": 100e18, "week3": 100e18},
    ]
    for i in range(2):
        assert gauge_controller.getGaugeBaseWeight(gauges[i]) == gauge_base_weights[i]['week2']
        assert gauge_controller.getGaugeBaseWeight(gauges[i], get_week(1)) == gauge_base_weights[i]['week3']

    assert gauge_controller.getUserVotesWtForGauge(gauges[0]) == 0
    assert gauge_controller.getUserVotesWtForGauge(gauges[0], get_week(1)) == 0
    assert gauge_controller.getUserVotesWtForGauge(gauges[1]) == 0
    assert gauge_controller.getUserVotesWtForGauge(gauges[1], get_week(1)) == 0

    for i in range(2):
        assert gauge_controller.getTypeWeight(i) == 1
        assert gauge_controller.getTypeWeight(i, get_week(1)) == 1

    assert gauge_controller.getTotalWeight() == 100e18
    assert gauge_controller.getTotalWeight(get_week(1)) == 100e18

    assert math.ceil(gauge_controller.getWeightsSumPerType(0)/1e18) == 0
    assert math.ceil(gauge_controller.getWeightsSumPerType(0, get_week(1))/1e18) == 0
    assert gauge_controller.getWeightsSumPerType(1) == 100e18
    assert gauge_controller.getWeightsSumPerType(1, get_week(1)) == 100e18

    # Scenario 4: After checkpoints, the weights in the contract status will be updated to ensure they are consistent
    # with what we have queried previously using view functions.
    gauge_controller.checkpointGauge({'from': owner})

    for i in range(2):
        assert gauge_controller.getLastGaugeWtScheduleTime(gauges[i]) == week6
        assert gauge_controller.getLastGaugeBaseWtScheduleTime(gauges[i]) == week6
        assert gauge_controller.getLastTypeWtScheduleTime(i) == week6
        assert gauge_controller.getLastSumWtScheduleTime(i) == week6
    assert gauge_controller.getLastTotalWtScheduleTime() == week6

    relative_weight0 = math.ceil(gauge_controller.gaugeRelativeWeight(gauges[0], week2)/1e15)
    relative_weight1 = math.floor(gauge_controller.gaugeRelativeWeight(gauges[1], week2)/1e15)
    assert relative_weight0 == math.ceil(1e18 * slope*week*3 / (slope*week*3 + 100e18)/1e15)
    assert relative_weight1 == math.floor(1e18 * 100e18 / (slope*week*3 + 100e18)/1e15)
    assert relative_weight0 + relative_weight1 == 1000

    gauge_weights = [
        {"week2": math.ceil(slope*week*3/1e18), "week3": math.ceil(slope*week*2/1e18)},
        {"week2": 100, "week3": 100},
    ]
    for i in range(2):
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i], week2)/1e18) == gauge_weights[i]['week2']
        assert math.ceil(gauge_controller.getGaugeWeight(gauges[i], week3)/1e18) == gauge_weights[i]['week3']

    gauge_base_weights = [
        {"week2": 0, "week3": 0},
        {"week2": 100e18, "week3": 100e18},
    ]
    for i in range(2):
        assert gauge_controller.getGaugeBaseWeight(gauges[i], week2) == gauge_base_weights[i]['week2']
        assert gauge_controller.getGaugeBaseWeight(gauges[i], week3) == gauge_base_weights[i]['week3']

    assert math.ceil(gauge_controller.getUserVotesWtForGauge(gauges[0], week2)/1e18) == math.ceil((slope*week*3)/1e18)
    assert math.ceil(gauge_controller.getUserVotesWtForGauge(gauges[0], week3)/1e18) == math.ceil((slope*week*2)/1e18)
    assert gauge_controller.getUserVotesWtForGauge(gauges[1], week2) == 0
    assert gauge_controller.getUserVotesWtForGauge(gauges[1], week3) == 0

    for i in range(2):
        assert gauge_controller.getTypeWeight(i, week2) == 1
        assert gauge_controller.getTypeWeight(i, week3) == 1

    assert math.ceil(gauge_controller.getTotalWeight(week2)/1e18) == math.ceil((slope*week*3)/1e18) + 100
    assert math.ceil(gauge_controller.getTotalWeight(week3)/1e18) == math.ceil((slope*week*2)/1e18) + 100

    assert math.ceil(gauge_controller.getWeightsSumPerType(0, week2)/1e18) == math.ceil((slope*week*3)/1e18)
    assert math.ceil(gauge_controller.getWeightsSumPerType(0, week3)/1e18) == math.ceil((slope*week*2)/1e18)
    assert gauge_controller.getWeightsSumPerType(1, week2) == 100e18
    assert gauge_controller.getWeightsSumPerType(1, week3) == 100e18


def test_voteForGaugeWeight(setup_contracts, owner, users, daysInSeconds):
    token, voting_escrow, gauge_controller = (
        setup_contracts[0], setup_contracts[1], setup_contracts[2])

    week = daysInSeconds(7)
    gauges = gauge_controller.getGaugeList()
    prec = gauge_controller.PREC()

    weeks_in_lock = 4
    voting_power = 700e18
    amt = estimatedLockAmt(voting_power, weeks_in_lock)

    token.mint(users[0], amt, {"from": owner})
    token.approve(voting_escrow, amt, {"from": users[0]})

    # Scenario 1: Users can't provide invalid voting power
    with brownie.reverts("Invalid voting power provided"):
        gauge_controller.voteForGaugeWeight(gauges[0], prec+1, {'from': users[0]})

    # Scenario 2: Users without available voting power can't vote
    with brownie.reverts("no voting power available"):
        gauge_controller.voteForGaugeWeight(gauges[0], prec, {'from': users[1]})

    # Scenario 3: Users can't vote if the lock expires before next week
    tx = voting_escrow.createLock(1e18, get_week(1), {"from": users[0]})
    assert "Locked" in tx.events

    with brownie.reverts("Lock expires before next cycle"):
        gauge_controller.voteForGaugeWeight(gauges[0], prec, {'from': users[0]})

    # Scenario 4: Users can't vote too frequently for the same gauge
    voting_escrow.increaseLockLength(get_week(10), {"from": users[0]})    # TODO
    assert "Locked" in tx.events

    tx = gauge_controller.voteForGaugeWeight(gauges[0], prec, {'from': users[0]})
    assert "GaugeVoted" in tx.events
    with brownie.reverts("Can't vote so often"):
        gauge_controller.voteForGaugeWeight(gauges[0], prec, {'from': users[0]})

    # Scenario 5: Users can't vote with power beyond the boundary limit
    chain.sleep(int(gauge_controller.WEIGHT_VOTE_DELAY()/week) + week)
    with brownie.reverts("Power beyond boundaries"):
        gauge_controller.voteForGaugeWeight(gauges[1], 1, {'from': users[0]})

    # Scenario 6: Users cannot vote with positive power for a gauge that has a weight of zero;
    # however, they can allocate zero power to it.
    tx = gauge_controller.changeTypeWeight(0, 0, {'from': owner})
    assert "TypeWeightUpdated" in tx.events

    with brownie.reverts("Votes for a gauge with zero type weight"):
        gauge_controller.voteForGaugeWeight(gauges[0], prec, {'from': users[0]})

    tx = gauge_controller.voteForGaugeWeight(gauges[0], 0, {'from': users[0]})
    assert "GaugeVoted" in tx.events

    # Scenario 8: Users can vote positively for a gauge with a positive type weight;
    # the power is scheduled to take effect the following week.
    tx = gauge_controller.changeTypeWeight(0, 1, {'from': owner})
    assert "TypeWeightUpdated" in tx.events

    chain.sleep(10 * week)
    amt = voting_escrow.MAXTIME()*100e18
    tx = voting_escrow.withdraw({"from": users[0]})
    assert "Unlocked" in tx.events

    slope = amt / voting_escrow.MAXTIME()
    lock_end = get_week(3)

    for i in range(2):
        token.mint(users[i], amt, {"from": owner})
        token.approve(voting_escrow, amt, {"from": users[i]})
        tx = voting_escrow.createLock(amt, lock_end, {"from": users[i]})
        assert "Locked" in tx.events

        tx = gauge_controller.voteForGaugeWeight(gauges[i], prec, {'from': users[i]})
        assert "GaugeVoted" in tx.events

        assert gauge_controller.userVotePower(users[i]) == prec

        assert gauge_controller.userVoteData(users[i], gauges[i])[0] == slope
        assert gauge_controller.userVoteData(users[i], gauges[i])[1] == prec
        assert gauge_controller.userVoteData(users[i], gauges[i])[2] == lock_end
        # assert gauge_controller.userVoteData(users[i], gauges[0])[3] == chain.time()   # voteTime

    for i in range(2):
        assert gauge_controller.getLastGaugeWtScheduleTime(gauges[i]) == get_week(1)
        assert gauge_controller.getLastGaugeBaseWtScheduleTime(gauges[i]) == get_week(1)
        assert gauge_controller.getLastTypeWtScheduleTime(i) == get_week(1)
        assert gauge_controller.getLastSumWtScheduleTime(i) == get_week(1)
        assert gauge_controller.getLastTotalWtScheduleTime() == get_week(1)

        assert gauge_controller.getGaugeBaseWeight(gauges[i]) == 100e18
        assert gauge_controller.getGaugeBaseWeight(gauges[i], get_week(1)) == 100e18
        assert gauge_controller.getGaugeBaseWeight(gauges[i], get_week(2)) == 100e18
        assert gauge_controller.getGaugeBaseWeight(gauges[i], get_week(3)) == 100e18

        assert gauge_controller.getGaugeWeight(gauges[i]) == 100e18
        assert gauge_controller.getGaugeWeight(gauges[i], get_week(1))/1e18 == 100 + 100*2*week
        assert gauge_controller.getGaugeWeight(gauges[i], get_week(2))/1e18 == 100 + 100*1*week
        assert gauge_controller.getGaugeWeight(gauges[i], get_week(3)) == 100e18

        assert gauge_controller.gaugePoints(gauges[i], get_week())[0] == 100e18
        assert gauge_controller.gaugePoints(gauges[i], get_week(1))[0]/1e18 == 100 + 100*2*week
        assert gauge_controller.gaugePoints(gauges[i], get_week(2))[0] == 0
        assert gauge_controller.gaugePoints(gauges[i], get_week(3))[0] == 0

        assert gauge_controller.gaugePoints(gauges[i], get_week())[1] == 0
        assert gauge_controller.gaugePoints(gauges[i], get_week(1))[1] == 100*1e18
        assert gauge_controller.gaugePoints(gauges[i], get_week(2))[1] == 0
        assert gauge_controller.gaugePoints(gauges[i], get_week(3))[1] == 0

        assert gauge_controller.gaugeSlopeChanges(gauges[i], get_week()) == 0
        assert gauge_controller.gaugeSlopeChanges(gauges[i], get_week(1)) == 0
        assert gauge_controller.gaugeSlopeChanges(gauges[i], get_week(2)) == 0
        assert gauge_controller.gaugeSlopeChanges(gauges[i], get_week(3)) == 100*1e18

        assert gauge_controller.gaugeBaseWtAtTime(gauges[i], get_week()) == 100*1e18
        assert gauge_controller.gaugeBaseWtAtTime(gauges[i], get_week(1)) == 100*1e18
        assert gauge_controller.gaugeBaseWtAtTime(gauges[i], get_week(2)) == 0
        assert gauge_controller.gaugeBaseWtAtTime(gauges[i], get_week(3)) == 0

        assert gauge_controller.getUserVotesWtForGauge(gauges[i]) == 0
        assert gauge_controller.getUserVotesWtForGauge(gauges[i], get_week(1)) == 100e18*2*week
        assert gauge_controller.getUserVotesWtForGauge(gauges[i], get_week(2)) == 100e18*1*week
        assert gauge_controller.getUserVotesWtForGauge(gauges[i], get_week(3)) == 0

        assert gauge_controller.getTypeWeight(i) == 1
        assert gauge_controller.getTypeWeight(i, get_week(1)) == 1
        assert gauge_controller.getTypeWeight(i, get_week(2)) == 1
        assert gauge_controller.getTypeWeight(i, get_week(3)) == 1

        assert gauge_controller.getWeightsSumPerType(i) == 100e18
        assert gauge_controller.getWeightsSumPerType(i, get_week(1))/1e18 == 100 + 100*2*week
        assert gauge_controller.getWeightsSumPerType(i, get_week(2))/1e18 == 100 + 100*1*week
        assert gauge_controller.getWeightsSumPerType(i, get_week(3)) == 100e18

        assert gauge_controller.typePoints(i, get_week())[0] == 100e18
        assert gauge_controller.typePoints(i, get_week(1))[0]/1e18 == 100 + 100*2*week
        assert gauge_controller.typePoints(i, get_week(2))[0] == 0
        assert gauge_controller.typePoints(i, get_week(3))[0] == 0

        assert gauge_controller.typePoints(i, get_week())[1] == 0
        assert gauge_controller.typePoints(i, get_week(1))[1] == 100*1e18
        assert gauge_controller.typePoints(i, get_week(2))[1] == 0
        assert gauge_controller.typePoints(i, get_week(3))[1] == 0

        assert gauge_controller.typeSlopeChanges(i, get_week()) == 0
        assert gauge_controller.typeSlopeChanges(i, get_week(1)) == 0
        assert gauge_controller.typeSlopeChanges(i, get_week(2)) == 0
        assert gauge_controller.typeSlopeChanges(i, get_week(3)) == 100*1e18

        assert gauge_controller.getTotalWeight() == 2*100e18
        assert gauge_controller.getTotalWeight(get_week(1))/1e18 == 2*(100 + 100*2*week)
        assert gauge_controller.getTotalWeight(get_week(2))/1e18 == 2*(100 + 100*1*week)
        assert gauge_controller.getTotalWeight(get_week(3)) == 2*100e18

        assert gauge_controller.gaugeRelativeWeight(gauges[i]) == 50/100 * 1e18
        assert gauge_controller.gaugeRelativeWeight(gauges[i], get_week(1)) == 50/100 * 1e18
        assert gauge_controller.gaugeRelativeWeight(gauges[i], get_week(2)) == 50/100 * 1e18
        assert gauge_controller.gaugeRelativeWeight(gauges[i], get_week(3)) == 50/100 * 1e18

