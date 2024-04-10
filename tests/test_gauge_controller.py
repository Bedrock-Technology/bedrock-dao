import brownie
from brownie import accounts, chain
import time

from tests.utils import get_week, estimatedVotingPower


# TODO: To be optimized
def test_changeGaugeBaseWeight(setup_contracts, owner, zero_address):
    token, gauge_controller = setup_contracts[0], setup_contracts[2]

    w0 = 100*1e18

    gauges = gauge_controller.getGaugeList()
    assert gauge_controller.getGaugeWeight(gauges[0]) == 0
    assert gauge_controller.getGaugeWeight(gauges[0], get_week(1)) == 100*1e18
    w0_old = gauge_controller.gaugeData(gauges[0])[2]
    assert w0_old == 100*1e18
    assert gauge_controller.getTypeWeight(0) == 0
    assert gauge_controller.getTypeWeight(0, get_week(1)) == 1
    assert gauge_controller.getWeightsSumPerType(0) == 0
    assert gauge_controller.getWeightsSumPerType(0, get_week(1)) == 100*1e18
    assert gauge_controller.getTotalWeight() == 0
    assert gauge_controller.getTotalWeight(get_week(1)) == 100*1e18
    assert gauge_controller.zero() == 1*1e18

    fake_gauge = accounts[3]
    oracle = accounts[4]

    # Scenario 1: Only an administrator can change base weight.
    with brownie.reverts():
        gauge_controller.changeGaugeBaseWeight(fake_gauge, w0, {'from': oracle})

    # Scenario 2: Can't change the base weight for a gauge that hasn't been added yet.
    with brownie.reverts("Gauge not added"):
        gauge_controller.changeGaugeBaseWeight(fake_gauge, w0, {'from': owner})

    # Scenario 3: Base weight will be scheduled for next week.
    tx = gauge_controller.changeGaugeBaseWeight(gauges[0], w0, {'from': owner})
    assert "GaugeBaseWeightUpdated" in tx.events

    # Scenario 4: The historical data of base weight, gauge weight, sum weight, type weight, and total weight will be recorded. #  TODO: 100 break


"""
Test vote for gauge weight - happy path
"""
def test_vote_for_gauge_weight__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):

    token, ve, gauge = setup_contracts[0], setup_contracts[1], setup_contracts[2]
    amount = 100e18

    voter1 = accounts[2]
    voter2 = accounts[3]
    voters = [voter1,voter2]

    lp_gauge1 = accounts[8]
    lp_gauge2 = accounts[9]

    tx = gauge.addType("TYPE0", 1, {'from':owner})
    assert "TypeAdded" in tx.events

    tx = gauge.addGauge(lp_gauge1, 0, 0, {'from':owner})

    """
    test nGauges
    """
    assert gauge.nGauges() == 1
    assert "GaugeAdded" in tx.events

    tx = gauge.addGauge(lp_gauge2, 0, 0, {'from':owner})

    assert gauge.nGauges() == 2
    assert "GaugeAdded" in tx.events

    """
    test voteForGaugeWeight
    """

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365))
    for voter in voters:
        token.mint(voter, amount, {"from": owner})
        token.approve(ve, amount, {"from": voter})
        ve.createLock(amount,lockEnd, {"from": voter})

    _, slope, ts = ve.getLastUserPoint(voter1)
    assert ve.balanceOf(voter1, ts) == estimatedVotingPower(amount, ve.lockEnd(voter1)-ts)

    tx = gauge.voteForGaugeWeight(lp_gauge1, 5000, {'from': voter1})
    assert "GaugeVoted" in tx.events

    tx = gauge.voteForGaugeWeight(lp_gauge2, 8000, {'from': voter2})
    assert "GaugeVoted" in tx.events

    """
    test gaugeRelativeWeight
    """
    vp1 = 0.5 * slope * (ve.lockEnd(voter1)-ts)
    vp2 = 0.8 * slope * (ve.lockEnd(voter2)-ts)

    expectedRelativeWeight = round(vp1/(vp1+vp2), 2)
    gotRelativeWeight = round(gauge.gaugeRelativeWeight(lp_gauge1, get_week(1))/1e18, 2)

    assert expectedRelativeWeight == gotRelativeWeight

    """
    test getUserVotesWtForGauge
    """
    expectedWt = round(0.5 * slope * (ve.lockEnd(voter1) - get_week(1))/1e18, 2)
    gotWt = round(gauge.getUserVotesWtForGauge(lp_gauge1, get_week(1))/1e18, 2)
    assert gotWt == expectedWt

    """
    test userVoteData
    """

    voteData = gauge.userVoteData(voter1, lp_gauge1)
    _, slope, _ = ve.getLastUserPoint(voter1)
    assert voteData[0] == 0.5 * slope
    assert voteData[1] == 5000
    assert voteData[2] == ve.lockEnd(voter1)