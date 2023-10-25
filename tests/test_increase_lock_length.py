import pytest
import math
from brownie import *

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