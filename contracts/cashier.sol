// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.9;

import "interfaces/IGaugeController.sol";
import "interfaces/IRewardReceiver.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

/**
 *  @title Cashier
 *  @notice This contract manages the reward distribution to different LP's based on gauges weight, weekly.
 *  @author RockX Team(AGPL)
 */
contract Cashier is Initializable, PausableUpgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;
    using Address for address;

    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant PROTOCOL_MANAGER_ROLE = keccak256("PROTOCOL_MANAGER_ROLE");

    uint256 public constant WEEK = 86400*7;
    uint256 public constant MULTIPLIER = 1e18;

    address public rewardToken; // the token as the rewards
    address public gaugeController; // gauge controller to determine how much to transfer
    address public approvedAccount; // the account who owns the to-be distributed rewards
                                    // a multi-sig wallet is recommended.
    uint256 public globalWeekEmission; // Reward Token Emissions per week.

    mapping(address => uint256) public nextRewardTime; // Tracks the next reward time for a gauge.

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address _rewardToken,
        uint256 _globalWeekEmission,
        address _gaugeController,
        address _approvedAccount
    ) initializer public {
        __Pausable_init();
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(PROTOCOL_MANAGER_ROLE, msg.sender);

        rewardToken = _rewardToken;
        gaugeController = _gaugeController;
        globalWeekEmission = _globalWeekEmission;
        approvedAccount = _approvedAccount;
    }

    /** 
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     * 
     *      CONTRACT EXTERNAL CONTROL
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */
    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @notice Function set the global emission rate per week
     * @param _newWeekEmission New weekly emission rate
     */
    function setGlobalEmissionRate(uint256 _newWeekEmission) external onlyRole(PROTOCOL_MANAGER_ROLE)  {
        globalWeekEmission = _newWeekEmission;
        emit GlobalEmissionRateSet(_newWeekEmission);
    }

    /**
     * @notice Function to send rewards and update the reward rates for a gauge.
     * @param _gAddr Address of the gauge
     */
    function distributeRewards(address _gAddr) external nonReentrant {
        _distributeRewards(_gAddr);
    }

    /** 
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     * 
     *      EXTERNAL VIEW
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */

    /**
     * @notice Function gets the rewards for gauge, for current cycle.
     * @param _gAddr Address of the gauge.
     * @return Returns the pending amount to be distributed.
     */
    function currentRewards(address _gAddr) external view returns (uint256) {
        if (block.timestamp < nextRewardTime[_gAddr]) {
            return 0;
        }

        uint256 gaugeRelativeWt = IGaugeController(gaugeController)
            .gaugeRelativeWeight(_gAddr);
        uint256 rewards = (globalWeekEmission * gaugeRelativeWt) / (MULTIPLIER);
        return rewards;
    }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     * 
     *      INTERNAL HELPER 
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */
    /**
     * @notice Function to send rewards to a gauge for the cycle.
     * @param _gAddr Address of the gauge.
     * @dev if there is a gap in reward distribution, for multiple cycles,
     *      only the latest cycle is considered for rewards.
     */
    function _distributeRewards(address _gAddr) private {
        uint256 nextRwdTime = nextRewardTime[_gAddr];
        require(
            nextRwdTime == 0 || (block.timestamp > nextRwdTime),
            "Invalid reward distribution"
        );

        // schedule next week's transfer
        nextRewardTime[_gAddr] = _floorToWeek(block.timestamp + WEEK);

        // Relative weights are always calculated based on the current cycle.
        uint256 gaugeRelativeWt = IGaugeController(gaugeController)
            .gaugeRelativeWeight(_gAddr);

        if (gaugeRelativeWt == 0) return;
         
        uint256 rewards = (globalWeekEmission * gaugeRelativeWt) / MULTIPLIER;

        // transfer ERC20 reward token to farm.
        IERC20(rewardToken).safeTransferFrom(approvedAccount, _gAddr, rewards);

        // notify staking with updateReward() if it's a contract
        if (_gAddr.isContract()) {
            IRewardReceiver(_gAddr).updateReward();
        }

        emit RewardsDistributed(_gAddr, rewards);
    }

    /**
     * @notice Floors a timestamp to the nearest weekly increment.
     * @param _ts arbitrary time stamp.
     * @return returns the 00:00 am UTC for THU after _ts
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
    event GlobalEmissionRateSet(uint256 rate);
    event RewardsDistributed(address indexed gAddr, uint256 amount);
}
