import math
import brownie
from brownie import accounts, chain

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
    assert ve.balanceOf(account) == math.floor((amount)/daysInSeconds(365)) * (ve.lockEnd(account) - ts)
     
    chain.sleep(daysInSeconds(60))

    lockEnd2 = floorToWeek(chain.time() + daysInSeconds(185))
    
    ve.increaseLockLength(lockEnd2, {"from": account})
    
    assert ve.locked(account)[1] == lockEnd2

    _, _, ts = ve.getLastUserPoint(account)
    assert ve.balanceOf(account) == math.floor((amount)/daysInSeconds(365)) * (ve.lockEnd(account) - ts)

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
        ve.increaseLockLength(floorToWeek(chain.time() + daysInSeconds(365 + 7)), {"from": account})
