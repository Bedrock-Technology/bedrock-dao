import math
import brownie
from brownie import accounts, chain

"""
Test create lock - happy path
"""
def test_createLock__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
    tx = ve.createLock(amount, lockEnd, {"from": account})
    
    assert "Locked" in tx.events
    assert token.balanceOf(account) == 0
    assert ve.locked(account)[0] == amount # locked amount
    assert ve.locked(account)[1] == floorToWeek(lockEnd) # lock end

    _, _, ts = ve.getLastUserPoint(account)
    slope = math.floor(amount/(4*daysInSeconds(365)))
    assert ve.balanceOf(account) ==slope * (ve.lockEnd(account) - ts)

"""
Test create lock - revert path
"""
def test_createLock__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    lockEnd = floorToWeek(chain.time() + 4*daysInSeconds(365) + daysInSeconds(10)) # 4yr lock
    with brownie.reverts():
        ve.createLock(amount, lockEnd, {"from": account}) # lock end is past maxtime
    
    lockEnd = floorToWeek(chain.time() - daysInSeconds(10)) 
    with brownie.reverts():
        ve.createLock(amount, lockEnd, {"from": account}) # lock end is in past

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
    with brownie.reverts():
        ve.createLock(0, lockEnd, {"from": account}) # lock amount is 0
    
    ve.createLock(amount, lockEnd, {"from": account}) # lock amount
    with brownie.reverts():
        ve.createLock(amount, lockEnd, {"from": account}) # lock again without withdrawing old tokens first

"""
Test inrease lock amount - happy path
"""
def test_increase_lock_amount__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})
    
    lockEnd = floorToWeek(chain.time() + daysInSeconds(365))

    tx = ve.createLock(amount/2, lockEnd, {"from": account})
    
    assert "Locked" in tx.events
    assert token.balanceOf(account) == amount/2
    assert ve.locked(account)[0] == amount/2 # locked amount
    assert ve.locked(account)[1] == lockEnd # lock end

    _, _, ts = ve.getLastUserPoint(account)
    slope = math.floor((amount/2)/(4*daysInSeconds(365)))
    assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)
     
    chain.sleep(daysInSeconds(60))

    ve.increaseLockAmount(amount/2, {"from": account})

    assert "Locked" in tx.events
    assert token.balanceOf(account) == 0
    assert ve.locked(account)[0] == amount
    assert ve.locked(account)[1] == lockEnd

    _, _, ts = ve.getLastUserPoint(account)
    slope = math.floor(amount/(4*daysInSeconds(365)))
    assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)

"""
Test inrease lock amount - revert path
"""
def test_increase_lock_amount__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    with brownie.reverts("Must stake non zero amount"):
        ve.increaseLockAmount(0, {"from": account}) # value cannot be zero

    with brownie.reverts("No existing lock found"):
        ve.increaseLockAmount(amount, {"from": account}) # no existing lock

    tx = ve.createLock(amount, floorToWeek(chain.time() + daysInSeconds(365)), {"from": account})
    assert "Locked" in tx.events

    chain.sleep(daysInSeconds(365))

    with brownie.reverts("Cannot add to expired lock. Withdraw"):
        ve.increaseLockAmount(amount, {"from": account}) # lock end has passed

"""
Test increase lock length
"""
def test_increase_lock_length__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})
    
    lockEnd = floorToWeek(chain.time() + daysInSeconds(180))

    ve.createLock(amount, lockEnd, {"from": account})
    
    assert token.balanceOf(account) == 0
    assert ve.locked(account)[0] == amount # locked amount
    assert ve.locked(account)[1] == lockEnd # lock end

    _, _, ts = ve.getLastUserPoint(account)
    slope = math.floor((amount)/(4*daysInSeconds(365)))
    assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)
     
    chain.sleep(daysInSeconds(60))

    lockEnd2 = floorToWeek(chain.time() + daysInSeconds(185))
    
    ve.increaseLockLength(lockEnd2, {"from": account})
    
    assert ve.locked(account)[1] == lockEnd2

    _, _, ts = ve.getLastUserPoint(account)
    slope = math.floor((amount)/(4*daysInSeconds(365)))
    assert ve.balanceOf(account) == slope * (ve.lockEnd(account) - ts)

"""
Test inrease lock length - revert path
"""
def test_increase_lock_length__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    with brownie.reverts("Nothing is locked"):
        ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(1)), {"from": account})
    
    tx = ve.createLock(amount, floorToWeek(chain.time() + daysInSeconds(7)), {"from": account})
    assert "Locked" in tx.events

    chain.sleep(daysInSeconds(8))

    with brownie.reverts("Lock expired"):
        ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(1)), {"from": account})

    tx = ve.withdraw({'from': account})
    assert "Unlocked" in tx.events

    token.approve(ve, amount, {"from": account})
    tx = ve.createLock(amount, floorToWeek(chain.time() + daysInSeconds(14)), {"from": account})
    assert "Locked" in tx.events
    
    with brownie.reverts("Can only increase lock WEEK"):
        ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(1)), {"from": account})
    
    with brownie.reverts("Exceeds maxtime"):
        ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(4*365 + 7)), {"from": account})

"""
Test withdraw - happy path
"""
def test_withdraw__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})
    
    lockEnd = floorToWeek(chain.time() + daysInSeconds(365))

    tx = ve.createLock(amount, lockEnd, {"from": account})
    assert "Locked" in tx.events

    chain.sleep(daysInSeconds(365))

    tx = ve.withdraw({"from": account})
    assert "Unlocked" in tx.events

    assert token.balanceOf(account) == amount
    assert ve.locked(account)[0] == 0
    assert ve.locked(account)[1] == 0
    assert ve.balanceOf(account) == 0

"""
Test withdraw - revert path
"""
def test_withdraw__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})
    
    lockEnd = floorToWeek(chain.time() + daysInSeconds(365))

    tx = ve.createLock(amount, lockEnd, {"from": account})
    assert "Locked" in tx.events

    chain.sleep(daysInSeconds(7))

    with brownie.reverts("The lock didn't expire"):
        ve.withdraw({"from": account})
    
    chain.sleep(daysInSeconds(365))

    tx = ve.withdraw({"from": account})
    assert "Unlocked" in tx.events

    with brownie.reverts("Must have something to withdraw"):
        ve.withdraw({"from": account})
    
"""
Test balanceOf (current)
"""
def test_balance_of__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
    ve.createLock(amount, lockEnd, {"from": account})

    _, _, ts = ve.getLastUserPoint(account)
    assert ve.balanceOf(account) == math.floor(amount/daysInSeconds(4*365)) * (ve.lockEnd(account) - ts)
    

"""
Test balanceOf (at timestamp)
"""
def test_balance_of_with_timestamp__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
    ve.createLock(amount, lockEnd, {"from": account})

    _, _, ts = ve.getLastUserPoint(account)
    assert ve.balanceOf(account, ts) == math.floor(amount/daysInSeconds(4*365)) * (ve.lockEnd(account) - ts)
    
