import brownie
from brownie import accounts, chain

from tests.utils import get_week


def test_depositFor(fn_isolation, setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    weeks_in_lock = 2

    token.mint(users[0], amt/2, {"from": owner})
    token.approve(ve, amt/2, {"from": users[0]})
    token.mint(owner, amt/2, {"from": owner})
    token.approve(ve, amt/2, {"from": owner})
    lock_end = get_week(weeks_in_lock+1)

    # Scenario 1: Only a rewards manager can deposit for a user
    with brownie.reverts(""):
        ve.depositFor(users[0], 0, {"from": users[1]})

    # Scenario 2: Cannot lock while the contract is paused.
    ve.pause({"from": owner})
    assert ve.paused()

    with brownie.reverts("Pausable: paused"):
        ve.depositFor(users[0], 0, {"from": owner})

    ve.unpause({"from": owner})
    assert not ve.paused()

    # Scenario 3: Cannot lock zero value
    with brownie.reverts("Must stake non zero amount"):
        ve.depositFor(users[0], 0, {"from": owner})

    # Scenario 4: Cannot increase amount if there is no existing lock
    with brownie.reverts("No existing lock found"):
        ve.depositFor(users[0], amt, {"from": owner})

    # Scenario 5: Cannot increase amount if the lock has expired
    tx = ve.createLock(amt/2, lock_end, {"from": users[0]})
    assert "Locked" in tx.events

    chain.sleep(weeks_in_lock*week+week)
    with brownie.reverts("Cannot add to expired lock. Withdraw"):
        ve.depositFor(users[0], amt, {"from": owner})

    tx = ve.withdraw({"from": users[0]})
    assert "Unlocked" in tx.events

    # Scenario 6: After amount increase, the balance will change accordingly,
    # and the historical data point should be updated.
    lock_end = get_week(weeks_in_lock+1)
    token.approve(ve, amt, {"from": users[0]})
    ve.createLock(amt/2, lock_end, {"from": users[0]})
    tx = ve.depositFor(users[0], amt/2, {"from": owner})
    assert "Locked" in tx.events

    assert ve.userPointEpoch(users[0]) == 4
    assert ve.globalEpoch() == 7

    assert ve.totalLocked() == amt

    assert ve.locked(users[0])[0] == amt
    assert ve.locked(users[0])[1] == lock_end
    assert ve.lockEnd(users[0]) == lock_end

    bias, slope, ts = ve.getLastUserPoint(users[0])
    assert bias == (lock_end - ts) * slope
    assert slope == slope
    assert abs(ts - chain.time()) <= 10

    user_point_blk = ve.userPointHistory(users[0], ve.userPointEpoch(users[0]))[3]
    assert user_point_blk == chain.height

    global_point = ve.pointHistory(ve.globalEpoch())
    assert global_point[0] == (lock_end - ts) * slope
    assert global_point[1] == slope
    assert global_point[2] == ts
    assert global_point[3] == chain.height

    assert abs(ve.balanceOf(users[0]) - (lock_end-chain.time()) * slope) <= slope
    assert ve.balanceOf(users[0], get_week()) == 0
    assert ve.balanceOf(users[0], get_week(1)) == 2*week*slope
    assert ve.balanceOf(users[0], get_week(2)) == week*slope
    assert ve.balanceOf(users[0], get_week(3)) == 0
    assert abs(ve.balanceOfAt(users[0], chain.height) - (lock_end-chain.time()) * slope) <= slope

    assert abs(ve.totalSupply() - (lock_end-chain.time()) * slope) <= slope
    assert ve.totalSupply(get_week()) == 0
    assert ve.totalSupply(get_week(1)) == 2*week*slope
    assert ve.totalSupply(get_week(2)) == week*slope
    assert ve.totalSupply(get_week(3)) == 0
    assert abs(ve.totalSupplyAt(chain.height) - (lock_end-chain.time()) * slope) <= slope


def test_createLock(fn_isolation, setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    weeks_in_lock = 2

    token.mint(users[0], amt, {"from": owner})
    token.approve(ve, amt, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)

    # Scenario 1: Cannot lock while the contract is paused.
    ve.pause({"from": owner})
    assert ve.paused()

    with brownie.reverts("Pausable: paused"):
        ve.createLock(amt, lock_end, {"from": users[0]})

    ve.unpause({"from": owner})
    assert not ve.paused()

    # Scenario 2: Cannot lock zero value
    with brownie.reverts("Must stake non zero amount"):
        ve.createLock(0, lock_end, {"from": users[0]})

    # Scenario 3: Cannot create a new lock if a locked amount already exists.
    tx = ve.createLock(amt, lock_end, {"from": users[0]})
    assert "Locked" in tx.events

    bias, slope, ts = ve.getFirstUserPoint(users[0])
    assert bias == (lock_end - ts) * slope
    assert slope == slope
    assert abs(ts - chain.time()) <= 10

    for i in range(2):
        with brownie.reverts("Withdraw old tokens first"):
            ve.createLock(amt, lock_end, {"from": users[0]})
        chain.sleep(weeks_in_lock*week + week)

    tx = ve.withdraw({"from": users[0]})
    assert "Unlocked" in tx.events

    # Scenario 4: Cannot lock if the specified end time has already passed.
    with brownie.reverts("Can only lock until time in the future"):
        ve.createLock(amt, get_week(), {"from": users[0]})

    # Scenario 5: Cannot lock if the specified end time exceeds the maximum time limit.
    with brownie.reverts("Exceeds maxtime"):
        ve.createLock(amt, get_week(2) + ve.MAXTIME(), {"from": users[0]})

    # Scenario 6: After lock, the balance will change accordingly,
    # and the historical data point should be updated.
    lock_end = get_week(weeks_in_lock+1)
    token.approve(ve, amt, {"from": users[0]})
    tx = ve.createLock(amt, lock_end, {"from": users[0]})
    assert "Locked" in tx.events

    assert ve.userPointEpoch(users[0]) == 3
    assert ve.globalEpoch() == 9

    assert ve.totalLocked() == amt

    assert ve.locked(users[0])[0] == amt
    assert ve.locked(users[0])[1] == lock_end
    assert ve.lockEnd(users[0]) == lock_end

    bias, slope, ts = ve.getLastUserPoint(users[0])
    assert bias == (lock_end - ts) * slope
    assert slope == slope
    assert abs(ts - chain.time()) <= 10

    user_point_blk = ve.userPointHistory(users[0], ve.userPointEpoch(users[0]))[3]
    assert user_point_blk == chain.height

    global_point = ve.pointHistory(ve.globalEpoch())
    assert global_point[0] == (lock_end - ts) * slope
    assert global_point[1] == slope
    assert global_point[2] == ts
    assert global_point[3] == chain.height

    assert abs(ve.balanceOf(users[0]) - (lock_end-chain.time()) * slope) <= slope
    assert ve.balanceOf(users[0], get_week()) == 0
    assert ve.balanceOf(users[0], get_week(1)) == 2*week*slope
    assert ve.balanceOf(users[0], get_week(2)) == week*slope
    assert ve.balanceOf(users[0], get_week(3)) == 0
    assert abs(ve.balanceOfAt(users[0], chain.height) - (lock_end-chain.time()) * slope) <= slope

    assert abs(ve.totalSupply() - (lock_end-chain.time()) * slope) <= slope
    assert ve.totalSupply(get_week()) == 0
    assert ve.totalSupply(get_week(1)) == 2*week*slope
    assert ve.totalSupply(get_week(2)) == week*slope
    assert ve.totalSupply(get_week(3)) == 0
    assert abs(ve.totalSupplyAt(chain.height) - (lock_end-chain.time()) * slope) <= slope


def test_increaseLockAmount(fn_isolation, setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    weeks_in_lock = 2

    token.mint(users[0], amt, {"from": owner})
    token.approve(ve, amt, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)

    # Scenario 1: Cannot lock while the contract is paused.
    ve.pause({"from": owner})
    assert ve.paused()

    with brownie.reverts("Pausable: paused"):
        ve.increaseLockAmount(amt, {"from": users[0]})

    ve.unpause({"from": owner})
    assert not ve.paused()

    # Scenario 2: Cannot lock zero value
    with brownie.reverts("Must stake non zero amount"):
        ve.increaseLockAmount(0, {"from": users[0]})

    # Scenario 3: Cannot increase amount if there is no existing lock
    with brownie.reverts("No existing lock found"):
        ve.increaseLockAmount(amt, {"from": users[0]})

    # Scenario 4: Cannot increase amount if the lock has expired
    tx = ve.createLock(amt, lock_end, {"from": users[0]})
    assert "Locked" in tx.events

    chain.sleep(weeks_in_lock*week+week)
    with brownie.reverts("Cannot add to expired lock. Withdraw"):
        ve.increaseLockAmount(amt, {"from": users[0]})

    tx = ve.withdraw({"from": users[0]})
    assert "Unlocked" in tx.events

    # Scenario 5: After amount increase, the balance will change accordingly,
    # and the historical data point should be updated.
    lock_end = get_week(weeks_in_lock+1)
    token.approve(ve, amt, {"from": users[0]})
    ve.createLock(amt/2, lock_end, {"from": users[0]})
    tx = ve.increaseLockAmount(amt/2, {"from": users[0]})
    assert "Locked" in tx.events

    assert ve.userPointEpoch(users[0]) == 4
    assert ve.globalEpoch() == 7

    assert ve.totalLocked() == amt

    assert ve.locked(users[0])[0] == amt
    assert ve.locked(users[0])[1] == lock_end
    assert ve.lockEnd(users[0]) == lock_end

    bias, slope, ts = ve.getLastUserPoint(users[0])
    assert bias == (lock_end - ts) * slope
    assert slope == slope
    assert abs(ts - chain.time()) <= 10

    user_point_blk = ve.userPointHistory(users[0], ve.userPointEpoch(users[0]))[3]
    assert user_point_blk == chain.height

    global_point = ve.pointHistory(ve.globalEpoch())
    assert global_point[0] == (lock_end - ts) * slope
    assert global_point[1] == slope
    assert global_point[2] == ts
    assert global_point[3] == chain.height

    assert abs(ve.balanceOf(users[0]) - (lock_end-chain.time()) * slope) <= slope
    assert ve.balanceOf(users[0], get_week()) == 0
    assert ve.balanceOf(users[0], get_week(1)) == 2*week*slope
    assert ve.balanceOf(users[0], get_week(2)) == week*slope
    assert ve.balanceOf(users[0], get_week(3)) == 0
    assert abs(ve.balanceOfAt(users[0], chain.height) - (lock_end-chain.time()) * slope) <= slope

    assert abs(ve.totalSupply() - (lock_end-chain.time()) * slope) <= slope
    assert ve.totalSupply(get_week()) == 0
    assert ve.totalSupply(get_week(1)) == 2*week*slope
    assert ve.totalSupply(get_week(2)) == week*slope
    assert ve.totalSupply(get_week(3)) == 0
    assert abs(ve.totalSupplyAt(chain.height) - (lock_end-chain.time()) * slope) <= slope


def test_increaseLockLength(fn_isolation, setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    weeks_in_lock = 2

    token.mint(users[0], amt, {"from": owner})
    token.approve(ve, amt, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)

    # Scenario 1: Cannot increase lock length while the contract is paused.
    ve.pause({"from": owner})
    assert ve.paused()

    with brownie.reverts("Pausable: paused"):
        ve.increaseLockLength(lock_end, {"from": users[0]})

    ve.unpause({"from": owner})
    assert not ve.paused()

    # Scenario 2: Cannot increase lock length if nothing is locked
    with brownie.reverts("Nothing is locked"):
        ve.increaseLockLength(lock_end, {"from": users[0]})

    # Scenario 3: Cannot shorten the lock
    tx = ve.createLock(amt, lock_end-week, {"from": users[0]})
    assert "Locked" in tx.events

    with brownie.reverts("Can only increase lock WEEK"):
        ve.increaseLockLength(get_week(), {"from": users[0]})

    # Scenario 4: Cannot increase the lock length if the specified end time exceeds the maximum time limit.
    with brownie.reverts("Exceeds maxtime"):
        ve.increaseLockLength(get_week(2) + ve.MAXTIME(), {"from": users[0]})

    # Scenario 5: Cannot increase lock length if the lock has expired
    chain.sleep(weeks_in_lock*week + week)
    with brownie.reverts("Lock expired"):
        ve.increaseLockLength(lock_end, {"from": users[0]})

    tx = ve.withdraw({"from": users[0]})
    assert "Unlocked" in tx.events

    # Scenario 6: After increase the lock length, the balance will change accordingly,
    # and the historical data point should be updated.
    lock_end = get_week(weeks_in_lock+1)
    token.approve(ve, amt, {"from": users[0]})
    ve.createLock(amt, lock_end-week, {"from": users[0]})
    tx = ve.increaseLockLength(lock_end, {"from": users[0]})
    assert "Locked" in tx.events

    assert ve.userPointEpoch(users[0]) == 4
    assert ve.globalEpoch() == 7

    assert ve.totalLocked() == amt

    assert ve.locked(users[0])[0] == amt
    assert ve.locked(users[0])[1] == lock_end
    assert ve.lockEnd(users[0]) == lock_end

    bias, slope, ts = ve.getLastUserPoint(users[0])
    assert bias == (lock_end - ts) * slope
    assert slope == slope
    assert abs(ts - chain.time()) <= 10

    user_point_blk = ve.userPointHistory(users[0], ve.userPointEpoch(users[0]))[3]
    assert user_point_blk == chain.height

    global_point = ve.pointHistory(ve.globalEpoch())
    assert global_point[0] == (lock_end - ts) * slope
    assert global_point[1] == slope
    assert global_point[2] == ts
    assert global_point[3] == chain.height

    assert abs(ve.balanceOf(users[0]) - (lock_end-chain.time()) * slope) <= slope
    assert ve.balanceOf(users[0], get_week()) == 0
    assert ve.balanceOf(users[0], get_week(1)) == 2*week*slope
    assert ve.balanceOf(users[0], get_week(2)) == week*slope
    assert ve.balanceOf(users[0], get_week(3)) == 0
    assert abs(ve.balanceOfAt(users[0], chain.height) - (lock_end-chain.time()) * slope) <= slope

    assert abs(ve.totalSupply() - (lock_end-chain.time()) * slope) <= slope
    assert ve.totalSupply(get_week()) == 0
    assert ve.totalSupply(get_week(1)) == 2*week*slope
    assert ve.totalSupply(get_week(2)) == week*slope
    assert ve.totalSupply(get_week(3)) == 0
    assert abs(ve.totalSupplyAt(chain.height) - (lock_end-chain.time()) * slope) <= slope


def test_withdraw(fn_isolation, setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    amount = 100e18
    week = daysInSeconds(7)
    weeks_in_lock = 2

    token.mint(users[0], amount, {"from": owner})
    token.approve(ve, amount, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)

    tx = ve.createLock(amount, lock_end, {"from": users[0]})
    assert "Locked" in tx.events
    assert token.balanceOf(users[0]) == 0

    # Scenario 1: Cannot withdraw when the locked amount is zero
    with brownie.reverts("Must have something to withdraw"):
        ve.withdraw({"from": users[1]})

    # Scenario 2: Cannot withdraw before lock expiration
    with brownie.reverts("The lock didn't expire"):
        ve.withdraw({"from": users[0]})

    # Scenario 3: After withdrawal, the balance will change accordingly,
    # and the historical data point should be updated.    
    chain.sleep(weeks_in_lock*week + week)
    tx = ve.withdraw({"from": users[0]})
    assert "Unlocked" in tx.events
    assert token.balanceOf(users[0]) == amount

    assert ve.userPointEpoch(users[0]) == 2
    assert ve.globalEpoch() == 5

    assert ve.totalLocked() == 0

    assert ve.locked(users[0])[0] == 0
    assert ve.locked(users[0])[1] == 0
    assert ve.lockEnd(users[0]) == 0

    bias, slope, ts = ve.getLastUserPoint(users[0])
    assert bias == 0
    assert slope == 0
    assert abs(ts - chain.time()) <= 10

    user_point_blk = ve.userPointHistory(users[0], ve.userPointEpoch(users[0]))[3]
    assert user_point_blk == chain.height

    global_point = ve.pointHistory(ve.globalEpoch())
    assert global_point[0] == 0
    assert global_point[1] == 0
    assert global_point[2] == ts
    assert global_point[3] == chain.height

    assert ve.balanceOf(users[0]) == 0
    assert ve.balanceOf(users[0], get_week()) == 0
    assert ve.balanceOfAt(users[0], chain.height) == 0

    assert ve.totalSupply() == 0
    assert ve.totalSupply(get_week()) == 0
    assert ve.totalSupply(chain.height) == 0

    # # Scenario 2: Can withdraw even when contract is paused and lock is expired
    token.approve(ve, amount, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)
    
    ve.createLock(amount, lock_end, {"from": users[0]})
    
    ve.pause({"from": owner})
    assert ve.paused()

    chain.sleep(weeks_in_lock*week + week)
    tx = ve.withdraw({"from": users[0]})
    assert "Unlocked" in tx.events
    assert token.balanceOf(users[0]) == amount

    ve.unpause({"from": owner})
    assert not ve.paused()

def test_balanceOf(fn_isolation, setup_contracts, owner, users, daysInSeconds):
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
                assert ve.balanceOf(users[i]) - int(slope * (lock_end - ts)) <= 10*slope
            else:
                assert ve.balanceOf(users[i]) == 0

        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})


def test_balanceOf_with_timestamp(fn_isolation, setup_contracts, owner, users, daysInSeconds):
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
                assert ve.balanceOf(users[i], get_week(1)) - int(slope * (lock_end - get_week(1))) <= 10*slope
            else:
                assert ve.balanceOf(users[i], get_week()) == 0

        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})


def test_balanceOfAt(fn_isolation, setup_contracts, owner, users, daysInSeconds, floorToWeek):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    week1 = get_week(1)
    amt = ve.MAXTIME()*100e18
    slope = amt/ve.MAXTIME()
    weeks_in_lock = 2

    token.mint(users[0], amt, {"from": owner})
    token.approve(ve, amt, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)

    tx = ve.createLock(amt, lock_end, {"from": users[0]})
    assert "Locked" in tx.events
    assert ve.globalEpoch() == 1

    powers = [slope * 2 * week, slope * 1 * week, 0]
    for i in range(weeks_in_lock + 1):
        assert ve.balanceOf(users[0], week1 + i * week) == powers[i]

    bias, slope, ts = ve.getFirstUserPoint(users[0])
    point0 = ve.pointHistory(1)
    point0_ts = point0[2]
    point0_blk = point0[3]

    height0 = chain.height

    # Scenario 1: Can provide only past block number
    with brownie.reverts("Only past block number"):
        ve.balanceOfAt(users[0], height0 + 1)

    # Scenario 2: Zero balance before lock
    assert ve.balanceOfAt(users[0], height0 - 1) == 0

    # Scenario 3: Balance at lock time
    assert ve.balanceOfAt(users[0], height0) == (lock_end - ts) * slope

    # Scenario 4: The checkpoint has not been updated for some time
    sleep_weeks = weeks_in_lock+1
    for i in range(sleep_weeks):
        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})
        assert chain.height == height0 + (i + 1)

    dTime = chain.time() - point0_ts
    dBlock = chain.height - point0_blk

    for i in range(weeks_in_lock + 2):
        block_number = height0 + i
        block_time = point0_ts + (block_number-point0_blk) * dTime/dBlock

        dBias = slope * (block_time - ts)

        if bias > dBias:
            assert ve.balanceOfAt(users[0], block_number) == bias - dBias
        else:
            assert ve.balanceOfAt(users[0], block_number) == 0

    for i in range(weeks_in_lock + 1):
        block_number = height0 + i + 1
        assert abs(ve.balanceOfAt(users[0], block_number) - powers[i]) <= slope * week

    # Scenario 5: Checkpoint has been updated
    ve.checkpoint({"from": owner})
    epochs = 1 + sleep_weeks + 1
    assert ve.globalEpoch() == epochs

    initial_last_pt = ve.pointHistory(1)
    initial_last_pt_ts = initial_last_pt[2]
    assert initial_last_pt[3] == height0

    block_slope = int(1e18 * (chain.height - height0) / (chain.time() - initial_last_pt_ts))

    height2_pt = ve.pointHistory(3)
    height2_pt_ts = height2_pt[2]
    height2_pt_blk = height2_pt[3]
    assert height2_pt_ts == floorToWeek(initial_last_pt_ts) + week*2
    assert height2_pt_blk == height0 + int((height2_pt_ts - initial_last_pt_ts) * block_slope / 1e18)
    assert height2_pt_blk == height0 + 2

    height3_pt = ve.pointHistory(4)
    height3_pt_ts = height3_pt[2]
    height3_pt_blk = height3_pt[3]
    assert height3_pt_ts == floorToWeek(initial_last_pt_ts) + week*3
    assert height3_pt_blk == height0 + int((height3_pt_ts - initial_last_pt_ts) * block_slope / 1e18)
    assert height3_pt_blk == height0 + 3

    for i in range(weeks_in_lock+1):
        block_number = height0 + i + 1
        assert ve.balanceOfAt(users[0], block_number) == powers[i]


def test_totalSupply(fn_isolation, setup_contracts, owner, users, daysInSeconds):
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
            assert ve.totalSupply() - 2 * int(slope * (lock_end - ts)) <= 2*10*slope
        else:
            assert ve.totalSupply() == 0

        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})


def test_totalSupply_with_timestamp(fn_isolation, setup_contracts, owner, users, daysInSeconds):
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

    for i in range(2):
        assert ve.totalSupply(get_week()) == 0
        assert ve.totalSupply(get_week(1)) == 2*slope*2*week
        assert ve.totalSupply(get_week(2)) == 2*slope*1*week
        assert ve.totalSupply(get_week(3)) == 0

    for i in range(10):
        ts = chain.time()
        if ts <= lock_end:
            assert ve.totalSupply(get_week(1)) - 2 * int(slope * (lock_end - get_week(1))) <= 2*10*slope
        else:
            assert ve.totalSupply() == 0

        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})


def test_totalSupplyAt(fn_isolation, setup_contracts, owner, users, daysInSeconds, floorToWeek):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    week1 = get_week(1)
    amt = ve.MAXTIME()*100e18
    slope = amt/ve.MAXTIME()
    weeks_in_lock = 2

    token.mint(users[0], amt, {"from": owner})
    token.approve(ve, amt, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)

    tx = ve.createLock(amt, lock_end, {"from": users[0]})
    assert "Locked" in tx.events
    assert ve.globalEpoch() == 1

    powers = [slope * 2 * week, slope * 1 * week, 0]
    for i in range(weeks_in_lock + 1):
        assert ve.balanceOf(users[0], week1 + i * week) == powers[i]

    bias, slope, ts = ve.getFirstUserPoint(users[0])
    point0 = ve.pointHistory(1)
    point0_ts = point0[2]
    point0_blk = point0[3]

    height0 = chain.height

    # Scenario 1: Can provide only past block number
    with brownie.reverts("Only past block number"):
        ve.totalSupplyAt(height0 + 1)

    # Scenario 2: Zero balance before lock
    assert ve.totalSupplyAt(height0 - 1) == 0

    # Scenario 3: Balance at lock time
    assert ve.totalSupplyAt(height0) == (lock_end - ts) * slope

    # Scenario 4: The checkpoint has not been updated for some time
    sleep_weeks = weeks_in_lock+1
    for i in range(sleep_weeks):
        chain.sleep(week)
        token.mint(users[0], amt, {"from": owner})
        assert chain.height == height0 + (i + 1)

    dTime = chain.time() - point0_ts
    dBlock = chain.height - point0_blk

    for i in range(weeks_in_lock + 2):
        block_number = height0 + i
        block_time = point0_ts + (block_number-point0_blk) * dTime/dBlock

        dBias = slope * (block_time - ts)

        if bias > dBias:
            assert ve.totalSupplyAt(block_number) == bias - dBias
        else:
            assert ve.totalSupplyAt(block_number) == 0

    for i in range(weeks_in_lock + 1):
        block_number = height0 + i + 1
        assert abs(ve.totalSupplyAt(block_number) - powers[i]) <= slope * week

    # Scenario 5: Checkpoint has been updated
    ve.checkpoint({"from": owner})
    epochs = 1 + sleep_weeks + 1
    assert ve.globalEpoch() == epochs

    initial_last_pt = ve.pointHistory(1)
    initial_last_pt_ts = initial_last_pt[2]
    assert initial_last_pt[3] == height0

    block_slope = int(1e18 * (chain.height - height0) / (chain.time() - initial_last_pt_ts))

    height2_pt = ve.pointHistory(3)
    height2_pt_ts = height2_pt[2]
    height2_pt_blk = height2_pt[3]
    assert height2_pt_ts == floorToWeek(initial_last_pt_ts) + week*2
    assert height2_pt_blk == height0 + int((height2_pt_ts - initial_last_pt_ts) * block_slope / 1e18)
    assert height2_pt_blk == height0 + 2

    height3_pt = ve.pointHistory(4)
    height3_pt_ts = height3_pt[2]
    height3_pt_blk = height3_pt[3]
    assert height3_pt_ts == floorToWeek(initial_last_pt_ts) + week*3
    assert height3_pt_blk == height0 + int((height3_pt_ts - initial_last_pt_ts) * block_slope / 1e18)
    assert height3_pt_blk == height0 + 3

    for i in range(weeks_in_lock + 1):
        block_number = height0 + i + 1
        assert ve.totalSupplyAt(block_number) == powers[i]


def test_checkpoint(fn_isolation, setup_contracts, owner, users, daysInSeconds):
    token, ve = setup_contracts[0], setup_contracts[1]

    week = daysInSeconds(7)
    amt = ve.MAXTIME()*100e18
    slope = amt/ve.MAXTIME()
    weeks_in_lock = 2

    token.mint(users[0], amt, {"from": owner})
    token.approve(ve, amt, {"from": users[0]})
    lock_end = get_week(weeks_in_lock+1)

    tx = ve.createLock(amt, lock_end, {"from": users[0]})
    assert "Locked" in tx.events

    for i in range(5):
        ve.checkpoint({"from": owner})

        assert ve.userPointEpoch(users[0]) == 1
        assert ve.globalEpoch() == 2 + i

        assert ve.slopeChanges(lock_end) == -slope

        global_point = ve.pointHistory(ve.globalEpoch())
        assert abs(global_point[0] - (lock_end - chain.time()) * slope)/1e18 <= slope
        assert global_point[1] == slope
        assert abs(global_point[2] - chain.time()) <= 10
        assert global_point[3] == chain.height

        assert abs(ve.totalSupply() - (lock_end-chain.time()) * slope) <= slope
        assert ve.totalSupply(get_week()) == 0
        assert ve.totalSupply(get_week(1)) == 2*week*slope
        assert ve.totalSupply(get_week(2)) == week*slope
        assert ve.totalSupply(get_week(3)) == 0
        assert abs(ve.totalSupplyAt(chain.height) - (lock_end-chain.time()) * slope) <= slope


