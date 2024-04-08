from brownie import accounts
import brownie


def test_mint(setup_contracts, owner, zero_address):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]
    oracle = accounts[4]

    # Scenario 1: Only a minter can call the mint function.
    with brownie.reverts():
        token.mint(lp, amount, {'from': oracle})

    # Scenario 2: Can't mint to the zero address.
    with brownie.reverts("ERC20: mint to the zero address"):
        token.mint(zero_address, amount, {'from': owner})

    # Scenario 3: Can't mint when the contract is paused.
    token.pause({"from": owner})
    assert token.paused()
    with brownie.reverts("Pausable: paused"):
        token.mint(lp, amount, {'from': owner})

    # Scenario 4: Minting was successful, and the balance has been updated.
    token.unpause({"from": owner})
    assert not token.paused()
    tx = token.mint(lp, amount, {'from': owner})
    assert "Transfer" in tx.events
    assert token.balanceOf(lp) == amount
    assert token.totalSupply() == amount
    assert token.name() == "Bedrock DAO"
    assert token.symbol() == "BRT"
    assert token.decimals() == 18


def test_approve(setup_contracts, approved_account, zero_address):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 1: Can't approve from the zero address.
    with brownie.reverts("ERC20: approve from the zero address"):
        token.approve(lp, amount, {'from': zero_address})

    # Scenario 2: Can't approve to the zero address.
    with brownie.reverts("ERC20: approve to the zero address"):
        token.approve(zero_address, amount, {'from': approved_account})

    # Scenario 3: The approval was successful, and the allowance has been updated.
    tx = token.approve(lp, amount, {'from': approved_account})
    assert "Approval" in tx.events
    assert token.allowance(approved_account, lp) == amount


def test_increaseAllowance(setup_contracts, approved_account, zero_address):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 1: Can't approve from the zero address.
    with brownie.reverts("ERC20: approve from the zero address"):
        token.increaseAllowance(lp, amount, {'from': zero_address})

    # Scenario 2: Can't approve to the zero address.
    with brownie.reverts("ERC20: approve to the zero address"):
        token.increaseAllowance(zero_address, amount, {'from': approved_account})

    # Scenario 3: The approval was successful, and the allowance has been updated.
    tx = token.increaseAllowance(lp, amount, {'from': approved_account})
    assert "Approval" in tx.events
    assert token.allowance(approved_account, lp) == amount


def test_decreaseAllowance(setup_contracts, approved_account):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 1: Can't decrease allowance below zero.
    with brownie.reverts("ERC20: decreased allowance below zero"):
        token.decreaseAllowance(lp, amount, {'from': approved_account})

    # Scenario 2: The approval was successful, and the allowance has been updated.
    tx = token.increaseAllowance(lp, amount, {'from': approved_account})
    assert "Approval" in tx.events
    assert token.allowance(approved_account, lp) == amount

    tx = token.decreaseAllowance(lp, amount, {'from': approved_account})
    assert "Approval" in tx.events
    assert token.allowance(approved_account, lp) == 0


def test_transfer(setup_contracts, owner, zero_address):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 1: Can't approve from the zero address.
    with brownie.reverts("ERC20: transfer from the zero address"):
        token.transfer(lp, amount, {'from': zero_address})

    # Scenario 2: Can't approve to the zero address.
    with brownie.reverts("ERC20: transfer to the zero address"):
        token.transfer(zero_address, amount, {'from': owner})

    # Scenario 3: Cannot transfer an amount exceeding the balance.
    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        token.transfer(lp, amount, {'from': owner})

    # Scenario 4: Can't transfer when the contract is paused.
    token.pause({"from": owner})
    assert token.paused()
    with brownie.reverts("Pausable: paused"):
        token.transfer(lp, amount, {'from': owner})

    # Scenario 5: The approval was successful, and the allowance has been updated.
    token.unpause({"from": owner})
    assert not token.paused()
    token.mint(owner, amount, {'from': owner})

    tx = token.transfer(lp, amount, {'from': owner})
    assert "Transfer" in tx.events
    assert token.balanceOf(owner) == 0
    assert token.balanceOf(lp) == amount
