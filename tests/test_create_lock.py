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
    assert ve.balanceOf(account) == math.floor(amount/daysInSeconds(365)) * (ve.lockEnd(account) - ts)

"""
Test create lock - revert path
"""
def test_createLock__revert_path(setup_contracts, owner, floorToWeek, daysInSeconds):
    
    token, ve, _ = setup_contracts
    amount = 100e18
    
    account = accounts[2]
    token.mint(account, amount, {"from": owner})
    token.approve(ve, amount, {"from": account})

    lockEnd = floorToWeek(chain.time() + daysInSeconds(365) + daysInSeconds(10)) # 1yr lock
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
