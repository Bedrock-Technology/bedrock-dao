import brownie
from tests.utils import get_week


def test_init_status(fn_isolation, setup_contracts, w3, owner, approved_account, global_week_emission, markets):
    # Contracts
    token = setup_contracts[0]
    voting_escrow = setup_contracts[1]
    gauge_controller = setup_contracts[2]
    penpie_adapter1 = setup_contracts[3]
    penpie_adapter2 = setup_contracts[4]
    bribe_manager = setup_contracts[5]
    ve_rewards = setup_contracts[6]
    casher = setup_contracts[7]

    # Roles
    pauser_role = w3.keccak(text='PAUSER_ROLE')
    minter_role = w3.keccak(text='MINTER_ROLE')
    rewards_manager_role = w3.keccak(text='REWARDS_MANAGER_ROLE')
    authorized_operator_role = w3.keccak(text='AUTHORIZED_OPERATOR_ROLE')
    default_admin_role = w3.toBytes(hexstr="0x00")

    # Check roles
    contracts_with_pauser = [token, voting_escrow]
    for c in contracts_with_pauser:
        c.hasRole(pauser_role, owner)
        c.hasRole(default_admin_role, owner)

    token.hasRole(minter_role, owner)
    voting_escrow.hasRole(rewards_manager_role, ve_rewards)
    gauge_controller.hasRole(authorized_operator_role, ve_rewards)

    # Check constant and status variables
    assert casher.WEEK() == 86400*7
    assert casher.MULTIPLIER() == 1e18

    assert casher.rewardToken() == token
    assert casher.gaugeController() == gauge_controller
    assert casher.approvedAccount() == approved_account
    assert casher.globalWeekEmission() == global_week_emission

    assert gauge_controller.MULTIPLIER() == 1e18
    assert gauge_controller.WEEK() == 86400*7
    assert gauge_controller.PREC() == 10000
    assert gauge_controller.WEIGHT_VOTE_DELAY() == 6 * 86400

    assert gauge_controller.timeTotal() == get_week() + 604800

    penpie_adapters = [penpie_adapter1, penpie_adapter2]
    for i, p in enumerate(penpie_adapters):
        assert p.pendleMarket() == markets[i]
        assert p.rewardToken() == token
        assert p.bribeManager() == bribe_manager

    token.name() == "Bedrock DAO"
    token.symbol() == "BRT"
    token.decimals() == 18

    assert ve_rewards.WEEK() == 604800
    assert ve_rewards.MAXWEEKS() == 50

    assert ve_rewards.votingEscrow() == voting_escrow
    assert ve_rewards.rewardToken() == token
    assert ve_rewards.genesisWeek() == get_week()
    assert ve_rewards.lastProfitsUpdate() == get_week()

    assert voting_escrow.WEEK() == 604800
    assert voting_escrow.MAXTIME() == 4*365*24*3600
    assert voting_escrow.MULTIPLIER() == 1e18
