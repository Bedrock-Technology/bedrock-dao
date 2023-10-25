import pytest
import math
from brownie import *

"""
Test create lock
"""
def test_createLock__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365)) # 1yr lock
    ve.createLock(amount, lockEnd, {"from": account})
    
    assert token.balanceOf(account) == 0
    assert ve.locked(account)[0] == amount # locked amount
    assert ve.locked(account)[1] == floorToWeek(lockEnd) # lock end

    _, _, ts = ve.getLastUserPoint(account)
    assert ve.balanceOf(account) == math.floor(amount/daysInSeconds(365)) * (ve.lockEnd(account) - ts)
    

