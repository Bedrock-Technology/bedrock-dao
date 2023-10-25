import pytest
import math
from brownie import *

"""
Test inrease lock amount
"""
def test_increase_lock_amount__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})
    
    lockEnd = floorToWeek(chain.time() + daysInSeconds(365))

    ve.createLock(amount/2, lockEnd, {"from": account})
    
    assert token.balanceOf(account) == amount/2
    assert ve.locked(account)[0] == amount/2 # locked amount
    assert ve.locked(account)[1] == lockEnd # lock end

    _, _, ts = ve.getLastUserPoint(account)
    assert ve.balanceOf(account) == math.floor((amount/2)/daysInSeconds(365)) * (ve.lockEnd(account) - ts)
     
    chain.sleep(daysInSeconds(60))

    ve.increaseLockAmount(amount/2, {"from": account})

    assert token.balanceOf(account) == 0
    assert ve.locked(account)[0] == amount
    assert ve.locked(account)[1] == lockEnd

    _, _, ts = ve.getLastUserPoint(account)
    assert ve.balanceOf(account) == math.floor((amount)/daysInSeconds(365)) * (ve.lockEnd(account) - ts)