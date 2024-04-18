from brownie import accounts
import brownie


def test_mint(fn_isolation, setup_contracts, owner, zero_address):
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


def test_approve(fn_isolation, setup_contracts, approved_account, zero_address):
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


def test_increaseAllowance(fn_isolation, setup_contracts, approved_account, zero_address):
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


def test_decreaseAllowance(fn_isolation, setup_contracts, approved_account):
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


def test_transfer(fn_isolation, setup_contracts, owner, zero_address):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 1: Can't approve from the zero address.
    with brownie.reverts("ERC20: transfer from the zero address"):
        token.transfer(lp, amount, {'from': zero_address})

    # Scenario 2: Can't approve to the zero address.
    with brownie.reverts("ERC20: transfer to the zero address"):
        token.transfer(zero_address, amount, {'from': owner})

    # Scenario 3: Can't transfer an amount exceeding the balance.
    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        token.transfer(lp, amount, {'from': owner})

    # Scenario 4: Can't transfer when the contract is paused.
    token.pause({"from": owner})
    assert token.paused()
    with brownie.reverts("Pausable: paused"):
        token.transfer(lp, amount, {'from': owner})

    # Scenario 5: The transfer was successful, and the allowance has been updated.
    token.unpause({"from": owner})
    assert not token.paused()
    token.mint(owner, amount, {'from': owner})

    tx = token.transfer(lp, amount, {'from': owner})
    assert "Transfer" in tx.events
    assert token.balanceOf(owner) == 0
    assert token.balanceOf(lp) == amount


def test_batchTransfer(fn_isolation, users, setup_contracts, owner, approved_account):
    token = setup_contracts[0]

    amt = 200

    # Scenario 1: At least one recipient is provided.
    with brownie .reverts("BRT: least one recipient address"):
        token.batchTransfer([], [], {'from': owner})

    # Scenario 2: The number of recipients must equal the number of tokens
    with brownie .reverts("BRT: number of recipient addresses does not match the number of tokens"):
        token.batchTransfer([users[0], users[1]], [amt/2], {'from': owner})
    with brownie .reverts("BRT: number of recipient addresses does not match the number of tokens"):
        token.batchTransfer([users[0]], [amt/2, amt/2], {'from': owner})

    # Scenario 3: Transfer successful and balances update accordingly
    token.mint(owner, amt, {'from': owner})
    tx = token.batchTransfer([users[0], users[1]], [amt/2, amt/2], {'from': owner})
    assert 'Transfer' in tx.events
    assert token.totalSupply() == amt
    assert token.balanceOf(owner) == 0
    assert token.balanceOf(users[0]) == amt/2
    assert token.balanceOf(users[1]) == amt/2


def test_transferFrom(fn_isolation, setup_contracts, owner, approved_account):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 0: Can't transfer for insufficient allowance.
    with brownie.reverts("ERC20: insufficient allowance"):
        token.transferFrom(approved_account, owner, amount, {'from': lp})

    # Scenario 3: Can't transfer an amount exceeding the balance.
    token.approve(lp, amount, {'from': approved_account})

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        token.transferFrom(approved_account, owner, amount, {'from': lp})

    # Scenario 4: Can't transfer when the contract is paused.
    token.pause({"from": owner})
    assert token.paused()
    with brownie.reverts("Pausable: paused"):
        token.transferFrom(lp, owner, amount, {'from': lp})

    # Scenario 5: The transfer was successful, and the allowance has been updated.
    token.unpause({"from": owner})
    assert not token.paused()

    token.mint(approved_account, amount, {'from': owner})

    tx = token.transferFrom(approved_account, owner, amount, {'from': lp})
    assert "Transfer" in tx.events
    assert token.balanceOf(approved_account) == 0
    assert token.balanceOf(owner) == amount


def test_burn(fn_isolation, setup_contracts, owner, zero_address):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 1: Can't burn from the zero address.
    with brownie.reverts("ERC20: burn from the zero address"):
        token.burn(amount, {'from': zero_address})

    # Scenario 2: Can't burn an amount exceeding the balance.
    with brownie.reverts("ERC20: burn amount exceeds balance"):
        token.burn(amount, {'from': lp})

    # Scenario 3: Can't burn when the contract is paused.
    token.pause({"from": owner})
    assert token.paused()
    with brownie.reverts("Pausable: paused"):
        token.burn(amount, {'from': lp})

    # Scenario 4: The burn was successful, and the allowance has been updated.
    token.unpause({"from": owner})
    assert not token.paused()
    token.mint(lp, amount, {'from': owner})
    assert token.balanceOf(lp) == amount

    tx = token.burn(amount, {'from': lp})
    assert "Transfer" in tx.events
    assert token.totalSupply() == 0


def test_burnFrom(fn_isolation, setup_contracts, owner, approved_account):
    token = setup_contracts[0]

    amount = 1e18

    lp = accounts[2]

    # Scenario 0: Can't burn for insufficient allowance.
    with brownie.reverts("ERC20: insufficient allowance"):
        token.burnFrom(approved_account, amount, {'from': lp})

    # Scenario 1: Can't burn an amount exceeding the balance.
    token.approve(lp, amount, {'from': approved_account})

    with brownie.reverts("ERC20: burn amount exceeds balance"):
        token.burnFrom(approved_account, amount, {'from': lp})

    # Scenario 2: Can't burn when the contract is paused.
    token.pause({"from": owner})
    assert token.paused()
    with brownie.reverts("Pausable: paused"):
        token.burnFrom(lp, amount, {'from': lp})

    # Scenario 3: The burn was successful, and the allowance has been updated.
    token.unpause({"from": owner})
    assert not token.paused()

    token.mint(approved_account, amount, {'from': owner})

    tx = token.burnFrom(approved_account, amount, {'from': lp})
    assert "Transfer" in tx.events
    assert token.totalSupply() == 0
