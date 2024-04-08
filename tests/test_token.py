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
