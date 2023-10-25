import pytest
import math
from brownie import *

"""
Test withdraw
"""
def test_increase_lock_length__happy_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})
    
    lockEnd = floorToWeek(chain.time() + daysInSeconds(365))

    ve.createLock(amount, lockEnd, {"from": account})

    chain.sleep(daysInSeconds(365))

    ve.withdraw({"from": account})

    assert token.balanceOf(account) == amount
    assert ve.locked(account)[0] == 0
    assert ve.locked(account)[1] == 0
    assert ve.balanceOf(account) == 0