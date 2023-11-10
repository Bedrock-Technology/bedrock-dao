import brownie
from brownie import accounts, chain

from tests.utils import get_week, estimatedVotingPower

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

    assert gauge.nGauges() == 1
    assert "GaugeAdded" in tx.events

    tx = gauge.addGauge(lp_gauge2, 0, 0, {'from':owner})

    assert gauge.nGauges() == 2
    assert "GaugeAdded" in tx.events

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365))
    for voter in voters:
        token.mint(voter, amount, {"from": owner})
        token.approve(ve, amount, {"from": voter})
        ve.createLock(amount,lockEnd, {"from": voter})
    
    _, _, ts = ve.getLastUserPoint(voter1)
    assert ve.balanceOf(voter1) == estimatedVotingPower(amount, ve.lockEnd(voter1)-ts)
    
    tx = gauge.voteForGaugeWeight(lp_gauge1, 5000, {'from': voter1})
    assert "GaugeVoted" in tx.events

    tx = gauge.voteForGaugeWeight(lp_gauge2, 8000, {'from': voter2})
    assert "GaugeVoted" in tx.events

    vp1 = 0.5 * estimatedVotingPower(amount, ve.lockEnd(voter1)-ts)
    vp2 = 0.8 * estimatedVotingPower(amount, ve.lockEnd(voter2)-ts)

    expectedRelativeWeight = round(vp1/(vp1+vp2), 2)
    gotRelativeWeight = round(gauge.gaugeRelativeWeight(lp_gauge1, get_week(1))/1e18, 2)

    assert expectedRelativeWeight == gotRelativeWeight