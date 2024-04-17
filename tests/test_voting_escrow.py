import math
import brownie
from brownie import accounts, chain

from tests.utils import get_week, estimatedVotingPower


# # TODO: To be optimized
# """
# Test create lock - happy path
# """
# def test_createLock__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
#     tx = ve.createLock(amount, lockEnd, {"from": account})
#
#     assert "Locked" in tx.events
#     assert token.balanceOf(account) == 0
#     assert ve.locked(account)[0] == amount # locked amount
#     assert ve.locked(account)[1] == floorToWeek(lockEnd) # lock end
#
#     _, _, ts = ve.getLastUserPoint(account)
#     assert ve.balanceOf(account) == estimatedVotingPower(amount, ve.lockEnd(account) - ts)
#
# # TODO: To be optimized
# """
# Test create lock - revert path
# """
# def test_createLock__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     lockEnd = floorToWeek(chain.time() + 4*daysInSeconds(365) + daysInSeconds(10)) # 4yr lock
#     with brownie.reverts():
#         ve.createLock(amount, lockEnd, {"from": account}) # lock end is past maxtime
#
#     lockEnd = floorToWeek(chain.time() - daysInSeconds(10))
#     with brownie.reverts():
#         ve.createLock(amount, lockEnd, {"from": account}) # lock end is in past
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
#     with brownie.reverts():
#         ve.createLock(0, lockEnd, {"from": account}) # lock amount is 0
#
#     ve.createLock(amount, lockEnd, {"from": account}) # lock amount
#     with brownie.reverts():
#         ve.createLock(amount, lockEnd, {"from": account}) # lock again without withdrawing old tokens first
#
# # TODO: To be optimized
# """
# Test inrease lock amount - happy path
# """
# def test_increase_lock_amount__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(365))
#
#     tx = ve.createLock(amount/2, lockEnd, {"from": account})
#
#     assert "Locked" in tx.events
#     assert token.balanceOf(account) == amount/2
#     assert ve.locked(account)[0] == amount/2 # locked amount
#     assert ve.locked(account)[1] == lockEnd # lock end
#
#     _, _, ts = ve.getLastUserPoint(account)
#     slope = math.floor((amount/2)/(4*daysInSeconds(365)))
#     assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)
#
#     chain.sleep(daysInSeconds(60))
#
#     ve.increaseLockAmount(amount/2, {"from": account})
#
#     assert "Locked" in tx.events
#     assert token.balanceOf(account) == 0
#     assert ve.locked(account)[0] == amount
#     assert ve.locked(account)[1] == lockEnd
#
#     _, _, ts = ve.getLastUserPoint(account)
#     slope = math.floor(amount/(4*daysInSeconds(365)))
#     assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)
#
# # TODO: To be optimized
# """
# Test inrease lock amount - revert path
# """
# def test_increase_lock_amount__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     with brownie.reverts("Must stake non zero amount"):
#         ve.increaseLockAmount(0, {"from": account}) # value cannot be zero
#
#     with brownie.reverts("No existing lock found"):
#         ve.increaseLockAmount(amount, {"from": account}) # no existing lock
#
#     tx = ve.createLock(amount, floorToWeek(chain.time() + daysInSeconds(365)), {"from": account})
#     assert "Locked" in tx.events
#
#     chain.sleep(daysInSeconds(365))
#
#     with brownie.reverts("Cannot add to expired lock. Withdraw"):
#         ve.increaseLockAmount(amount, {"from": account}) # lock end has passed
#
# # TODO: To be optimized
# """
# Test increase lock length
# """
# def test_increase_lock_length__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(180))
#
#     ve.createLock(amount, lockEnd, {"from": account})
#
#     assert token.balanceOf(account) == 0
#     assert ve.locked(account)[0] == amount # locked amount
#     assert ve.locked(account)[1] == lockEnd # lock end
#
#     _, _, ts = ve.getLastUserPoint(account)
#     slope = math.floor((amount)/(4*daysInSeconds(365)))
#     assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)
#
#     chain.sleep(daysInSeconds(60))
#
#     lockEnd2 = floorToWeek(chain.time() + daysInSeconds(185))
#
#     ve.increaseLockLength(lockEnd2, {"from": account})
#
#     assert ve.locked(account)[1] == lockEnd2
#
#     _, _, ts = ve.getLastUserPoint(account)
#     slope = math.floor((amount)/(4*daysInSeconds(365)))
#     assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)
#
# # TODO: To be optimized
# """
# Test inrease lock length - revert path
# """
# def test_increase_lock_length__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     with brownie.reverts("Nothing is locked"):
#         ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(1)), {"from": account})
#
#     tx = ve.createLock(amount, floorToWeek(chain.time() + daysInSeconds(7)), {"from": account})
#     assert "Locked" in tx.events
#
#     chain.sleep(daysInSeconds(8))
#
#     with brownie.reverts("Lock expired"):
#         ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(1)), {"from": account})
#
#     tx = ve.withdraw({'from': account})
#     assert "Unlocked" in tx.events
#
#     token.approve(ve, amount, {"from": account})
#     tx = ve.createLock(amount, floorToWeek(chain.time() + daysInSeconds(14)), {"from": account})
#     assert "Locked" in tx.events
#
#     with brownie.reverts("Can only increase lock WEEK"):
#         ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(1)), {"from": account})
#
#     with brownie.reverts("Exceeds maxtime"):
#         ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(4*365 + 7)), {"from": account})
#
# # TODO: To be optimized
# """
# Test withdraw - happy path
# """
# def test_withdraw__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(365))
#
#     tx = ve.createLock(amount, lockEnd, {"from": account})
#     assert "Locked" in tx.events
#
#     chain.sleep(daysInSeconds(365))
#
#     tx = ve.withdraw({"from": account})
#     assert "Unlocked" in tx.events
#
#     assert token.balanceOf(account) == amount
#     assert ve.locked(account)[0] == 0
#     assert ve.locked(account)[1] == 0
#     assert ve.balanceOf(account) == 0
#
# # TODO: To be optimized
# """
# Test withdraw - revert path
# """
# def test_withdraw__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(365))
#
#     tx = ve.createLock(amount, lockEnd, {"from": account})
#     assert "Locked" in tx.events
#
#     chain.sleep(daysInSeconds(7))
#
#     with brownie.reverts("The lock didn't expire"):
#         ve.withdraw({"from": account})
#
#     chain.sleep(daysInSeconds(365))
#
#     tx = ve.withdraw({"from": account})
#     assert "Unlocked" in tx.events
#
#     with brownie.reverts("Must have something to withdraw"):
#         ve.withdraw({"from": account})
#
# # TODO: To be optimized
# """
# Test balanceOf (at timestamp)
# """
# def test_balance_of_with_timestamp__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
#
#     token, ve = setup_contracts[0], setup_contracts[1]
#     amount = 100e18
#
#     account = accounts[2]
#     token.mint(account, amount, {"from": owner})
#     token.approve(ve, amount, {"from": account})
#
#     lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
#     ve.createLock(amount, lockEnd, {"from": account})
#
#     _, _, ts = ve.getLastUserPoint(account)
#     assert ve.balanceOf(account, ts) == math.floor(amount/daysInSeconds(4*365)) * (ve.lockEnd(account) - ts)


def test_balanceOf(setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    slope = amt / ve.MAXTIME()
    lock_end = get_week(3)

    # Scenario 1: The user's voting power is zero if they have not locked.
    for i in range(2):
        assert ve.balanceOf(users[i]) == 0

    # Scenario 2: The user's voting power will decrease linearly over time until it reaches zero.
    for i in range(2):
        token.mint(users[i], amt, {"from": owner})
        token.approve(ve, amt, {"from": users[i]})
        ve.createLock(amt, lock_end, {"from": users[i]})

    for i in range(10):
        ts = chain.time()
        for i in range(2):
            if ts <= lock_end:
                assert ve.balanceOf(users[i])/1e19 == int(slope * (lock_end - ts))/1e19
            else:
                assert ve.balanceOf(users[i]) == 0

        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})


def test_balanceOf_with_timestamp(setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    slope = amt / ve.MAXTIME()
    lock_end = get_week(3)

    # Scenario 1: The user's voting power is zero if they have not locked.
    for i in range(2):
        assert ve.balanceOf(users[0], get_week()) == 0

    # Scenario 2: The user's voting power will decrease linearly over time until it reaches zero.
    for i in range(2):
        token.mint(users[i], amt, {"from": owner})
        token.approve(ve, amt, {"from": users[i]})
        ve.createLock(amt, lock_end, {"from": users[i]})

    for i in range(2):
        assert ve.balanceOf(users[i], get_week()) == 0
        assert ve.balanceOf(users[i], get_week(1)) == slope*2*week
        assert ve.balanceOf(users[i], get_week(2)) == slope*1*week
        assert ve.balanceOf(users[i], get_week(3)) == 0

    for i in range(1):
        ts = chain.time()
        for i in range(1):
            if ts <= lock_end:
                assert ve.balanceOf(users[i], get_week(1))/1e19 == int(slope * (lock_end - get_week(1)))/1e19
            else:
                assert ve.balanceOf(users[i], get_week()) == 0

        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})


def test_totalSupply(setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    slope = amt / ve.MAXTIME()
    lock_end = get_week(3)

    # Scenario 1: The total voting power is zero if users have not locked.
    assert ve.totalSupply() == 0

    # Scenario 2: The total voting power will decrease linearly over time until it reaches zero.
    for i in range(2):
        token.mint(users[i], amt, {"from": owner})
        token.approve(ve, amt, {"from": users[i]})
        ve.createLock(amt, lock_end, {"from": users[i]})

    for i in range(10):
        ts = chain.time()
        if ts <= lock_end:
            assert ve.totalSupply()/1e19 == 2 * int(slope * (lock_end - ts))/1e19
        else:
            assert ve.totalSupply() == 0

        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})


