import brownie
from brownie import accounts, chain

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
    