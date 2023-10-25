import pytest
import math
from brownie import *

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
    assert ve.balanceOf(account) == math.floor(amount/daysInSeconds(365)) * (ve.lockEnd(account) - ts)
    

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
    assert ve.balanceOf(account, ts) == math.floor(amount/daysInSeconds(365)) * (ve.lockEnd(account) - ts)
    

