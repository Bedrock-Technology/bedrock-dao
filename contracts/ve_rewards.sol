// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.9;

import "interfaces/IVotingEscrow.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

 /**
  * @title Rockx Voting-escrow Rewards Contract
  * @author RockX Team
  */
contract VeRewards is Initializable, AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;

    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    uint256 public constant WEEK = 604800;
    uint256 public constant MAXWEEKS = 50; // max number of weeks a user can claim rewards in a single transaction
    mapping(address => uint256) public userLastSettledWeek; // user's last settlement week
    mapping(uint256 => uint256) public weeklyProfits; // week ts -> profits for this week
    uint256 public lastProfitsUpdate; // latest week which has profits updated

    uint256 public accountedBalance; // for tracking of balance change
    address public votingEscrow; // the voting escrow contract
    address public rewardToken; // the reward token to distribute to users as rewards
    uint256 public genesisWeek; // the genesis week the contract has deployed
    uint256 public accountedRewards; // for tracking rewards allocated

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /**
     * @dev This contract will not accept direct ETH transactions.
     */
    receive() external payable {
        revert("Do not send ETH here");
    }

    function initialize(
        address _votingEscrow
    ) initializer public {
        __Pausable_init();
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);

        rewardToken = IVotingEscrow(_votingEscrow).assetToken();
        votingEscrow = _votingEscrow;

        genesisWeek = _floorToWeek(block.timestamp);
        lastProfitsUpdate = genesisWeek;
    }

    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      EXTERNAL FUNCTIONS
    *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */

    /**
     * @dev claim all rewards
     */
    function claim(bool restake) external nonReentrant {
        _updateReward();

        // calc profits and update settled week
        (uint256 profits, uint256 settleToWeek) = _calcProfits(msg.sender);

        userLastSettledWeek[msg.sender] = settleToWeek;
        
        if (profits == 0) return;
        
        if (restake) {
            IERC20(rewardToken).safeApprove(votingEscrow, profits);
            IVotingEscrow(votingEscrow).depositFor(msg.sender, profits);
        } else {
            // transfer profits to user
            IERC20(rewardToken).safeTransfer(msg.sender, profits);
        }

        // track balance decrease
        _balanceDecrease(profits);

        // log
        emit Claimed(msg.sender, restake, profits);
    }

    /**
     * @dev updateReward, make sure this is called once a week if no one claims.
     */
    function updateReward() external { _updateReward(); }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      VIEW FUNCTIONS
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */

    /**
     * @dev return accumulated rewards claimable.
     */
     function getPendingReward(address account) external view returns (uint256, uint256) { return _calcProfits(account); }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      INTERNALS
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */
    /**
     * @dev a formal way to track balance change
     */
    function _balanceDecrease(uint256 amount) internal { accountedBalance -= amount; }

    /**
     * @dev internal calculation of profits for a user
     */
    function _calcProfits(address account) internal view returns (uint256 profits, uint256 settleToWeek) {
        // load user's latest settled week
        settleToWeek = userLastSettledWeek[account];
        if (settleToWeek < genesisWeek) {
            settleToWeek = genesisWeek;
        }

        // lookup user's first ve deposit timestamp
        (,,uint256 ts) = IVotingEscrow(votingEscrow).getFirstUserPoint(account);
        if (settleToWeek < ts) {
            settleToWeek = _floorToWeek(ts);
        }

        // loop throught weeks to accumulate profits
        for (uint i=0; i<MAXWEEKS;i++) {
            uint256 nextWeek = settleToWeek + WEEK;
            if (nextWeek > block.timestamp || nextWeek > lastProfitsUpdate) {
                break;
            }
            settleToWeek = nextWeek;
            uint256 preSettleWeek = settleToWeek - WEEK;

            // get total supply of the week
            uint256 totalSupply = IVotingEscrow(votingEscrow).totalSupply(preSettleWeek);
            if (totalSupply > 0) {  // avert division by zero 
                profits += weeklyProfits[settleToWeek]
                            * IVotingEscrow(votingEscrow).balanceOf(account, preSettleWeek)
                            / totalSupply;
            }
        }

        return (profits, settleToWeek);
    }

    /**
     * @dev compare balance remembered to current balance to find the increased reward.
     */
    function _updateReward() internal {
        uint256 balance = IERC20(rewardToken).balanceOf(address(this));
        if (balance > accountedBalance) {
            // by comparing recorded balance and actual balance,
            // we can find the increment.
            uint256 profits = balance - accountedBalance;
            accountedBalance = balance; // balance sync

            // rewards received this week is scheduled to release in next week.
            uint256 week = _floorToWeek(block.timestamp+WEEK);
            weeklyProfits[week] += profits;
            lastProfitsUpdate = week;

            accountedRewards += profits;
            emit RewardUpdated(profits);
        }
    }

    /**
     *  @notice Floors a timestamp to the nearest weekly increment.
     *  @param _ts arbitrary time stamp.
     *  @return returns the 00:00 am UTC for THU after _ts
     */
    function _floorToWeek(uint256 _ts) private pure returns (uint256) {
        return (_ts / WEEK) * WEEK;
    }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      EVENTS
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */
     event Claimed(address account, bool restake, uint256 amount);
     event RewardUpdated(uint256 amount);
}
