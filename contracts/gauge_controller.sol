// SPDX-License-Identifier: AGPL-3.0-or-later
// ⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀
// ⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀
// ⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢠⣤⣤⣤⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀
// ⠉⠻⣿⡟⠛⠛⠻⣿⣄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⡀⡀⡀⡀⡀⡀⡀⠙⢿⣿⡟⠁⡀⡀⠙⣿⠟⠁
// ⡀⡀⣿⡇⡀⡀⡀⢸⣿⡆⡀⡀⡀⡀⡀⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⣀⣀⣀⡀⡀⡀⡀⣿⣿⡀⡀⡀⡀⡀⡀⡀⡀⡀⢿⣿⡄⡀⡀⣾⠃⡀⡀
// ⡀⡀⣿⡇⡀⡀⡀⢸⣿⠃⡀⡀⡀⣾⡿⠉⠉⠙⣿⣄⡀⡀⡀⣴⣿⠋⠉⠻⣿⡄⡀⡀⣿⣿⡀⡀⠙⣿⠿⠉⡀⡀⡀⡀⢻⣿⣄⣿⠁⡀⡀⡀
// ⡀⡀⣿⣇⣀⣀⣤⡿⠋⡀⡀⡀⣼⣿⡀⡀⡀⡀⢸⣿⡀⡀⢠⣿⠃⡀⡀⡀⠛⡀⡀⡀⣿⣿⡀⢀⡿⠁⡀⡀⡀⡀⡀⡀⡀⢻⣿⡄⡀⡀⡀⡀
// ⡀⡀⣿⡏⠉⠻⣿⣄⡀⡀⡀⡀⣿⣿⡀⡀⡀⡀⠘⣿⡇⡀⢸⣿⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⣴⣿⣦⡀⡀⡀⡀⡀⡀⡀⢠⡿⢻⣿⡄⡀⡀⡀
// ⡀⡀⣿⡇⡀⡀⠻⣿⣆⡀⡀⡀⢿⣿⡀⡀⡀⡀⢸⣿⠁⡀⢸⣿⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⡀⠘⣿⣧⡀⡀⡀⡀⡀⣰⡟⡀⡀⢻⣿⡄⡀⡀
// ⡀⢀⣿⣧⡀⡀⡀⠻⣿⣦⡀⡀⠈⣿⣄⡀⡀⡀⣾⡿⡀⡀⡀⢿⣷⡀⡀⡀⣀⡄⡀⡀⣿⣿⡀⡀⠈⣿⣷⡀⡀⡀⣴⣿⡀⡀⡀⡀⢻⣿⣄⡀
// ⠛⠛⠛⠛⠛⡀⡀⡀⠈⠛⠛⡀⡀⡀⠛⠿⠿⠟⠋⡀⡀⡀⡀⡀⠙⠿⠿⠿⠛⡀⠘⠛⠛⠛⠛⡀⡀⡀⠙⠛⠛⠛⠛⠛⠛⡀⡀⠛⠛⠛⠛⠛
// ⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀
// ⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀

pragma solidity ^0.8.9;
import "interfaces/IVotingEscrow.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts/utils/math/SafeCast.sol";

/**
 *  @title GaugeController
 *  @notice This contract is the solidity version of curves GaugeController.
 *  @author Curve Finance (MIT) - original concept and implementation in Vyper 
 *              (see: https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/GaugeController.vy)
 *          Sperax Team (MIT) - solidity interpretation of gauge controller.
 *              (see: https://arbiscan.io/address/0xdce2810fc24d8ec8a6d2d749e1248e3f0ba97257#code)
 *          RockX Team - this version, structure and code optimized, role-based access-control
 */
contract GaugeController is AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    bytes32 public constant AUTHORIZED_OPERATOR = keccak256("AUTHORIZED_OPERATOR_ROLE");

    struct Point {
        uint256 bias;
        uint256 slope;
    }

    struct VoteData {
        uint256 slope;
        uint256 power;
        uint256 end;
        uint256 voteTime;
    }

    struct GaugeData {
        uint128 gType; // Gauge type
        uint256 wtUpdateTime; // latest weight schedule time
        uint256 w0; // base weight for the gauge.
    }

    uint256 public constant MULTIPLIER = 1e18;
    uint256 public constant WEEK = 604800;
    uint256 public constant PREC = 10000;

    uint256 constant MAX_NUM = 1e3;
    uint256 constant MAX_NUM_GAUGES = 1e4;

    // # Cannot change weight votes more often than once in 6 days
    uint256 public constant WEIGHT_VOTE_DELAY = 6 * 86400;
    address public votingEscrow;
    uint128 public nGaugeTypes;
    uint128 public nGauges;
    // last scheduled time;
    uint256 public timeTotal;

    address[] public gauges;
    // type_id -> last scheduled time
    uint256[MAX_NUM] public timeSum;
    // type_id -> time
    uint256[MAX_NUM] public lastTypeWtTime;

    // time -> total weight
    mapping(uint256 => uint256) public totalWtAtTime;

    // user -> gauge_addr -> VoteData
    mapping(address => mapping(address => VoteData)) public userVoteData;
    // Total vote power used by user
    mapping(address => uint256) public userVotePower;

    // gauge_addr => type_id
    mapping(address => GaugeData) public gaugeData;
    // gauge_addr -> time -> Point
    mapping(address => mapping(uint256 => Point)) public gaugePoints;
    // gauge_addr -> time -> slope
    mapping(address => mapping(uint256 => uint256)) public gaugeSlopeChanges;

    // gauge_addr -> last scheduled time for base weight
    mapping(address => uint256) public timeGaugeBaseWt;
    // gauge_addr -> time -> base weight
    mapping(address => mapping(uint256 => uint256)) public gaugeBaseWtAtTime;


    // Track gauge name
    mapping(uint128 => string) public typeNames;
    // type_id -> time -> Point
    mapping(uint128 => mapping(uint256 => Point)) public typePoints;
    // type_id -> time -> slope
    mapping(uint128 => mapping(uint256 => uint256)) public typeSlopeChanges;
    // type_id -> time -> type weight
    mapping(uint128 => mapping(uint256 => uint256)) public typeWtAtTime;

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      CONTRACT & META MANAGEMENT
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address _votingEscrow) initializer public {
        __AccessControl_init();
        __ReentrancyGuard_init();

        votingEscrow = _votingEscrow;
        timeTotal = block.timestamp / WEEK * WEEK;

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(AUTHORIZED_OPERATOR, msg.sender);
    }

    /**
     * @notice Add gauge type with name `_name` and weight `weight`
     * @param _typeName Name of gauge type
     * @param _weight Weight of gauge type
     */
    function addType(string memory _typeName, uint256 _weight)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        require(nGaugeTypes < MAX_NUM, "Can't add more gauge types");

        bytes memory typeNameBytes = bytes(_typeName);
        require(typeNameBytes.length > 0, "Empty type name");

        uint128 gType = nGaugeTypes;
        typeNames[gType] = _typeName;
        nGaugeTypes = gType + 1;
        if (_weight != 0) {
            _changeTypeWeight(gType, _weight);
        }
        emit TypeAdded(_typeName, gType);
    }

    /*
     * @notice Change gauge type `_gType` weight to `_weight
     * @param _gType Gauge type id
     * @param _weight New Gauge weight
    */
    function changeTypeWeight(uint128 _gType, uint256 _weight)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        _changeTypeWeight(_gType, _weight);
    }

    /*
     *  @notice Change the base weight of a gauge
     *  @param _gAddr Gauge address
     *  @param _newW0 New base weight for the gauge
     */
    function changeGaugeBaseWeight(address _gAddr, uint256 _newW0)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        _changeGaugeBaseWeight(_gAddr, _newW0);
    }

    /**
     *  @notice Add gauge `gAddr` of type `gauge_type` with weight `weight`
     *  @param _gAddr Gauge address
     *  @param _gType Gauge type
     *  @param _weight Gauge weight
     */
    function addGauge(
        address _gAddr,
        uint128 _gType,
        uint256 _weight
    ) external onlyRole(AUTHORIZED_OPERATOR)
    {
        require(_gAddr != address(0), "Invalid address");
        require(_gType < nGaugeTypes, "Invalid gauge type");
        require(gaugeData[_gAddr].gType == 0, "Gauge already registered");  ///  @dev can't add the same gauge twice
        require(nGauges < MAX_NUM_GAUGES, "Can't add more gauges");
        gauges.push(_gAddr);
        nGauges += 1;

        uint256 nextTime = _getWeek(block.timestamp + WEEK);

        if (_weight > 0) {
            uint256 typeWeight = _getTypeWeight(_gType);
            uint256 oldSum = _getSum(_gType);
            uint256 oldTotal = _getTotal();

            typePoints[_gType][nextTime].bias = _weight + oldSum;
            timeSum[_gType] = nextTime;
            totalWtAtTime[nextTime] = oldTotal + typeWeight * _weight;
            timeTotal = nextTime;

            gaugePoints[_gAddr][nextTime].bias = _weight;
        }

        if (timeSum[_gType] == 0) {
            timeSum[_gType] = nextTime;
        }
        gaugeData[_gAddr] = GaugeData({
            gType: _gType + 1,
            wtUpdateTime: nextTime,
            w0: _weight
        });

        emit GaugeAdded(_gAddr, _gType, _weight);
    }

    /**
     *  @notice Checkpoint to fill data common for all gauges
     */
    function checkpoint() external {
        _getTotal();
    }

    /**
     *  @notice checkpoints gauge weight for missing weeks
     */
    function checkpointGauge(address _gAddr) external {
        _getWeight(_gAddr);
        _getTotal();
    }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      EXTERNAL FUNCTIONS FOR GAUGE VOTING
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */

    /**
     *  @notice Allocate voting power for changing pool weights
     *  @param _gAddr Gauge which `msg.sender` votes for
     *  @param _userWeight Weight for a gauge in bps (units of 0.01%). Minimal is 0.01%. Ignored if 0
     */
    function voteForGaugeWeight(address _gAddr, uint256 _userWeight)
        external
        nonReentrant
    {
        require(
            _userWeight >= 0 && _userWeight <= PREC,
            "Invalid voting power provided"
        );

        // Get user's latest veToken stats
        (, int128 slope,) = IVotingEscrow(votingEscrow).getLastUserPoint(msg.sender);

        require(slope > 0, "no voting power available");

        uint256 lockEnd = IVotingEscrow(votingEscrow).lockEnd(msg.sender);

        uint256 nextTime = _getWeek(block.timestamp + WEEK);

        require(lockEnd > nextTime, "Lock expires before next cycle");

        // Prepare slopes and biases in memory
        VoteData memory oldVoteData = userVoteData[msg.sender][_gAddr];
        require(
            block.timestamp >= oldVoteData.voteTime + WEIGHT_VOTE_DELAY,
            "Can't vote so often"
        );

        VoteData memory newVoteData = VoteData({
            slope: (SafeCast.toUint256(slope) * _userWeight) / PREC,
            end: lockEnd,
            power: _userWeight,
            voteTime: block.timestamp
        });
        // Check and update powers (weights) used
        _updateUserPower(oldVoteData.power, newVoteData.power);

        _updateScheduledChanges(
            oldVoteData,
            newVoteData,
            nextTime,
            lockEnd,
            _gAddr
        );

        _getTotal();
        userVoteData[msg.sender][_gAddr] = newVoteData;
        uint256 voteUsed = newVoteData.slope * (newVoteData.end - newVoteData.voteTime);

        emit GaugeVoted(block.timestamp, msg.sender, _gAddr, _userWeight, voteUsed);
    }


    /**
     *  @notice Get gauge weight normalized to 1e18 and also fill all the unfilled
     *         values for type and gauge records
     *  @dev Any address can call, however nothing is recorded if the values are filled already
     *  @param _gAddr Gauge address
     *  @param _time Relative weight at the specified timestamp in the past or present
     *  @return Value of relative weight normalized to 1e18
     */
    function gaugeRelativeWeightWrite(address _gAddr, uint256 _time)
        external
        returns (uint256)
    {
        _getWeight(_gAddr);
        _getTotal();
        return _gaugeRelativeWeight(_gAddr, _time);
    }

    function gaugeRelativeWeightWrite(address _gAddr)
        external
        returns (uint256)
    {
        _getWeight(_gAddr);
        _getTotal();
        return _gaugeRelativeWeight(_gAddr, block.timestamp);
    }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      EXTERNAL VIEW FUNCTIONS
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */

    /*
     * @notice Get gauge type for address
     * @param _gAddr Gauge address
     * @return Gauge type id
     */
    function gaugeType(address _gAddr) external view returns (uint128) {
        return _getGaugeType(_gAddr);
    }

    /**
     *  @notice Get gauge relative weight (not more than 1.0), normalized to 1e18
     *         (e.g. 1.0 == 1e18). Inflation which will be received by it is
     *         inflation_rate * relative_weight / 1e18
     *  @param _gAddr Gauge address
     *  @param _time Timestamp
     *  @return Gauge relative weight, normalized to 1e18
     */
    function gaugeRelativeWeight(address _gAddr, uint256 _time) external view returns (uint256) {
        return _gaugeRelativeWeight(_gAddr, _time);
    }

    /**
     *  @notice Get current gauge relative weight (not more than 1.0), normalized to 1e18
     *         (e.g. 1.0 == 1e18). Inflation which will be received by it is
     *         inflation_rate * relative_weight / 1e18
     *  @param _gAddr Gauge address
     *  @return Gauge relative weight, normalized to 1e18
     */
    function gaugeRelativeWeight(address _gAddr) external view returns (uint256) {
        return _gaugeRelativeWeight(_gAddr, block.timestamp);
    }

    /**
     *  @notice Get current gauge weight
     *  @param _gAddr Gauge address
     *  @return Gauge weight
     */
    function getGaugeWeight(address _gAddr) external view returns (uint256) {
        return _getGaugeWeightReadOnly(_gAddr, block.timestamp);
    }

    /**
     *  @notice Get gauge weight
     *  @param _gAddr Gauge address
     *  @param _time Timestamp
     *  @return Gauge weight
     */
    function getGaugeWeight(address _gAddr, uint256 _time) external view returns (uint256) {
        return _getGaugeWeightReadOnly(_gAddr, _time);
    }

    /**
     *  @notice Get current gaugeWeight - w0 (base weight).
     *  @param _gAddr Gauge address
     *  @return Vote weight for the gauge.
     */
    function getUserVotesWtForGauge(address _gAddr) external view returns (uint256) {
        uint256 wt = _getGaugeWeightReadOnly(_gAddr, block.timestamp);
        uint256 w0 = _getGaugeBaseWeightReadOnly(_gAddr, block.timestamp);
        return wt - w0;
    }

    /**
     *  @notice Get gaugeWeight - w0 (base weight)
     *  @param _gAddr Gauge address
     *  @param _time Timestamp
     *  @return Vote weight for the gauge.
     */
    function getUserVotesWtForGauge(address _gAddr, uint256 _time) external view returns (uint256) {
        uint256 wt = _getGaugeWeightReadOnly(_gAddr, _time);
        uint256 w0 = _getGaugeBaseWeightReadOnly(_gAddr, _time);
        return wt - w0;
    }

    /**
     *  @notice Get current gauge base weight
     *  @param _gAddr Gauge address
     *  @return Gauge base weight
     */
    function getGaugeBaseWeight(address _gAddr)  external  view returns (uint256) {
        return _getGaugeBaseWeightReadOnly(_gAddr, block.timestamp);
    }

    /**
     *  @notice Get gauge base weight
     *  @param _gAddr Gauge address
     *  @param _time Timestamp
     *  @return Gauge base weight
     */
    function getGaugeBaseWeight(address _gAddr, uint256 _time)  external  view returns (uint256) {
        return _getGaugeBaseWeightReadOnly(_gAddr, _time);
    }

    /**
     *  @notice Get current type weight
     *  @param _gType Type id
     *  @return Type weight
     */
    function getTypeWeight(uint128 _gType) external view returns (uint256) {
        return _getTypeWeightReadOnly(_gType, block.timestamp);
    }

    /**
     *  @notice Get type weight
     *  @param _gType Type id
     *  @param _time Timestamp
     *  @return Type weight
     */
    function getTypeWeight(uint128 _gType, uint256 _time) external view returns (uint256) {
        return _getTypeWeightReadOnly(_gType, _time);
    }

    /**
     *  @notice Get current total (type-weighted) weight
     *  @return Total weight
     */
    function getTotalWeight() external view returns (uint256) {
        return _getTotalWeightReadOnly(block.timestamp);
    }

    /**
     *  @notice Get total (type-weighted) weight
     *  @param _time Timestamp
     *  @return Total weight
     */
    function getTotalWeight(uint256 _time) external view returns (uint256) {
        return _getTotalWeightReadOnly(_time);
    }

    /**
     *  @notice Get current sum of gauge weights per type
     *  @param _gType Type id
     *  @return Sum of gauge weights
     */
    function getWeightsSumPerType(uint128 _gType) external view returns (uint256) {
        return _getSumWeightReadOnly(_gType, block.timestamp);
    }

    /**
     *  @notice Get sum of gauge weights per type
     *  @param _gType Type id
     *  @param _time Timestamp
     *  @return Sum of gauge weights
     */
    function getWeightsSumPerType(uint128 _gType, uint256 _time) external view returns (uint256) {
        return _getSumWeightReadOnly(_gType, _time);
    }

    /**
     *  @notice Returns address of all registered gauges.
     */
    function getGaugeList() external view returns (address[] memory) {
        return gauges;
    }

    /**
     *  @notice Get last gauge weight schedule time
     *  @param _gAddr Gauge address
     *  @return Last schedule time
     */
    function getLastGaugeWtScheduleTime(address _gAddr) external view returns (uint256) {
        return gaugeData[_gAddr].wtUpdateTime;
    }

    /**
     *  @notice Get last gauge base weight schedule time
     *  @param _gAddr Gauge address
     *  @return Last schedule time
     */
    function getLastGaugeBaseWtScheduleTime(address _gAddr) external view returns (uint256) {
        return timeGaugeBaseWt[_gAddr];
    }

    /**
     *  @notice Get last type weight schedule time
     *  @param _gType Gauge type
     *  @return Last schedule time
     */
    function getLastTypeWtScheduleTime(uint128 _gType) external view returns (uint256) {
        if (_gType >= MAX_NUM) return 0;
        return lastTypeWtTime[_gType];
    }

    /**
     *  @notice Get last sum weight schedule time for a gauge type
     *  @param _gType Gauge type
     *  @return Last schedule time
     */
    function getLastSumWtScheduleTime(uint128 _gType) external view returns (uint256) {
        if (_gType >= MAX_NUM) return 0;
        return timeSum[_gType];
    }

    /**
     *  @notice Get last total weight schedule time
     *  @return Last schedule time
     */
    function getLastTotalWtScheduleTime() external view returns (uint256) {
        return timeTotal;
    }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      INTERNAL HELPER FUNCTIONS
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */

    /**
     *  @notice Fill historic gauge base weight week-over-week for missed check-points
     *          and return the gauge base weight for the future week
     *  @param _gAddr Address of the gauge.
     *  @return Gauge base weight
     */
    function _getGaugeBaseWeight(address _gAddr) private returns (uint256) {
        uint256 t = timeGaugeBaseWt[_gAddr];
        if (t > 0) {
            uint256 w = gaugeBaseWtAtTime[_gAddr][t];
            for (uint8 i = 0; i < 100; i++) {
                if (t > block.timestamp) {
                    break;
                }
                t += WEEK;
                gaugeBaseWtAtTime[_gAddr][t] = w;
            }
            timeGaugeBaseWt[_gAddr] = t;
            return w;
        }
        return 0;
    }

    /**
     *  @notice Fill historic type weights week-over-week for missed check-points
     *          and return the type weight for the future week
     *  @param _gType Gauge type id
     *  @return Type weight
     */
    function _getTypeWeight(uint128 _gType) private returns (uint256) {
        uint256 t = lastTypeWtTime[_gType];
        if (t > 0) {
            uint256 w = typeWtAtTime[_gType][t];
            for (uint8 i = 0; i < 100; i++) {
                if (t > block.timestamp) {
                    break;
                }
                t += WEEK;
                typeWtAtTime[_gType][t] = w;
            }
            lastTypeWtTime[_gType] = t;
            return w;
        }
        return 0;
    }

    /**
     *  @notice Fill sum of gauge weights for the same type week-over-week for
     *         missed checkpoints and return the sum for the future week
     *  @param _gType Gauge type id
     *  @return Sum of weights
     */
    function _getSum(uint128 _gType) private returns (uint256) {
        uint256 t = timeSum[_gType];
        if (t > 0) {
            uint256 sumW0 = _getBaseWeight(_gType);
            Point memory pt = typePoints[_gType][t];
            for (uint8 i = 0; i < 100; i++) {
                if (t > block.timestamp) {
                    break;
                }
                t += WEEK;
                uint256 dBias = pt.slope * WEEK;
                if (pt.bias > sumW0 + dBias) {
                    pt.bias -= dBias;
                    pt.slope -= typeSlopeChanges[_gType][t];
                } else {
                    pt.bias = sumW0;
                    pt.slope = 0;
                }
                typePoints[_gType][t] = pt;
            }
            timeSum[_gType] = t;
            return pt.bias;
        }
        return 0;
    }

    /**
     *  @notice Calculate the total gauge base weight of the given gauge type
     *  @param _gType Gauge type id
     *  @return Total gauge base weight of the given gauge type
     */
    function _getBaseWeight(uint128 _gType) private view returns (uint256) {
        uint256 sumW0 = 0;
        address[] memory gaugeList = gauges;
        for (uint16 i = 0; i < gaugeList.length; i++) {
            address gAddr = gaugeList[i];
            if (_getGaugeType(gAddr) == _gType) {
                sumW0 += gaugeData[gAddr].w0;
            }
        }
        return sumW0;
    }

    /**
     *  @notice Fill historic total weights week-over-week for missed checkins
     *         and return the total for the future week
     *  @return Total weight
     */
    function _getTotal() private returns (uint256) {
        uint256 t = timeTotal;
        uint128 numTypes = nGaugeTypes;
        if (t > block.timestamp) {
            t -= WEEK;
        }

        // Updating type related data
        for (uint16 i = 0; i < numTypes; i++) {
            _getSum(i);
            _getTypeWeight(i);
        }

        uint256 pt = totalWtAtTime[t];

        for (uint256 i = 0; i < 100; i++) {
            if (t > block.timestamp) {
                break;
            }
            t += WEEK;
            pt = 0;

            for (uint128 gType = 0; gType < numTypes; gType++) {
                uint256 typeSum = typePoints[gType][t].bias;
                uint256 typeWeight = typeWtAtTime[gType][t];
                pt += typeSum * typeWeight;
            }
            totalWtAtTime[t] = pt;
        }
        timeTotal = t;
        return pt;
    }

    /**
     *  @notice Fill historic gauge weights week-over-week for missed checkins
     *         and return the total for the future week
     *  @param _gAddr Address of the gauge
     *  @return Gauge weight
     */
    function _getWeight(address _gAddr) private returns (uint256) {
        _getGaugeBaseWeight(_gAddr);

        uint256 t = gaugeData[_gAddr].wtUpdateTime;
        if (t > 0) {
            uint256 w0 = gaugeData[_gAddr].w0;
            Point memory pt = gaugePoints[_gAddr][t];
            for (uint8 i = 0; i < 100; i++) {
                if (t > block.timestamp) {
                    break;
                }
                t += WEEK;
                uint256 dBias = pt.slope * WEEK;
                if (pt.bias > w0 + dBias) {
                    pt.bias -= dBias;
                    pt.slope -= gaugeSlopeChanges[_gAddr][t];
                } else {
                    pt.bias = w0;
                    pt.slope = 0;
                }
                gaugePoints[_gAddr][t] = pt;
            }
            gaugeData[_gAddr].wtUpdateTime = t;
            return pt.bias;
        }
        return 0;
    }

    /**
     *  @notice Change type weight
     *  @param _gType Type id
     *  @param _weight New type weight
     */
    function _changeTypeWeight(uint128 _gType, uint256 _weight) private {
        require(nGaugeTypes > 0 && _gType < nGaugeTypes, "Gauge Type hasn't been registered yet");
        
        uint256 oldWeight = _getTypeWeight(_gType);
        uint256 oldSum = _getSum(_gType);
        uint256 totalWeight = _getTotal();
        uint256 nextTime = _getWeek(block.timestamp + WEEK);

        totalWeight = totalWeight + (oldSum * _weight) - (oldSum * oldWeight);
        totalWtAtTime[nextTime] = totalWeight;
        typeWtAtTime[_gType][nextTime] = _weight;
        timeTotal = nextTime;
        lastTypeWtTime[_gType] = nextTime;

        emit TypeWeightUpdated(_gType, nextTime, _weight, totalWeight);
    }

    /**
     *  @notice Change the base weight of a gauge
     *  @param _gAddr Gauge Address
     *  @param _newW0 New base weight for the gauge
     */
    function _changeGaugeBaseWeight(address _gAddr, uint256 _newW0) private {
        uint128 gType = _getGaugeType(_gAddr);
        uint256 oldGaugeWeight = _getWeight(_gAddr);
        uint256 oldW0 = gaugeData[_gAddr].w0;
        uint256 typeWeight = _getTypeWeight(gType);
        uint256 oldSum = _getSum(gType);
        uint256 totalWeight = _getTotal();
        uint256 nextTime = _getWeek(block.timestamp + WEEK);

        timeGaugeBaseWt[_gAddr] = nextTime;
        gaugeBaseWtAtTime[_gAddr][nextTime] = _newW0;

        uint256 newGaugeWeight = oldGaugeWeight + _newW0 - oldW0;
        gaugePoints[_gAddr][nextTime].bias = newGaugeWeight;
        gaugeData[_gAddr].wtUpdateTime = nextTime;
        gaugeData[_gAddr].w0 = _newW0;

        uint256 newSum = oldSum + _newW0 - oldW0;
        typePoints[gType][nextTime].bias = newSum;
        timeSum[gType] = nextTime;

        totalWeight += (newSum - oldSum) * typeWeight;
        totalWtAtTime[nextTime] = totalWeight;
        timeTotal = nextTime;
        emit GaugeBaseWeightUpdated(_gAddr, block.timestamp, _newW0, newGaugeWeight, totalWeight);
    }

    /**
     *  @notice Update user power.
     *  @param _oldPow current power used.
     *  @param _newPow updated power.
     */
    function _updateUserPower(uint256 _oldPow, uint256 _newPow) private {
        // Check and update powers (weights) used
        uint256 powerUsed = userVotePower[msg.sender];
        powerUsed = powerUsed + _newPow - _oldPow;
        userVotePower[msg.sender] = powerUsed;
        require(powerUsed >= 0 && powerUsed <= PREC, "Power beyond boundaries");
    }

    /**
     *  @notice Update the vote data and scheduled slope changes.
     *  @param _oldVoteData user's old vote data.
     *  @param _newVoteData user's new vote data.
     *  @param _nextTime timestamp for next cycle.
     *  @param _lockEnd the expiry ts for user's veToken position.
     *  @param _gAddr address of the gauge.
     */
    function _updateScheduledChanges(
        VoteData memory _oldVoteData,
        VoteData memory _newVoteData,
        uint256 _nextTime,
        uint256 _lockEnd,
        address _gAddr
    ) private {
        uint128 gType = _getGaugeType(_gAddr);

        // Calculate the current bias based on the oldVoteData.
        uint256 old_dt = 0;
        if (_oldVoteData.end > _nextTime) {
            old_dt = _oldVoteData.end - _nextTime;
        }
        uint256 oldBias = _oldVoteData.slope * old_dt;

        // Calculate the new bias.
        uint256 new_dt = _lockEnd - _nextTime;
        uint256 newBias = _newVoteData.slope * new_dt;

        {
            // restrict scope of below variables (resolves, stack too deep)
            uint256 oldWtBias = _getWeight(_gAddr);
            uint256 oldSumBias = _getSum(gType);
            // Remove old and schedule new slope changes
            // Remove slope changes for old slopes
            // Schedule recording of initial slope for _nextTime.
            gaugePoints[_gAddr][_nextTime].bias =
                _max(oldWtBias + newBias, oldBias) -
                oldBias;
            typePoints[gType][_nextTime].bias =
                _max(oldSumBias + newBias, oldBias) -
                oldBias;
        }

        uint256 oldGaugeSlope = gaugePoints[_gAddr][_nextTime].slope;
        uint256 oldTypeSlope = typePoints[gType][_nextTime].slope;

        if (_oldVoteData.end > _nextTime) {
            gaugePoints[_gAddr][_nextTime].slope =
                _max(oldGaugeSlope + _newVoteData.slope, _oldVoteData.slope) -
                _oldVoteData.slope;
            typePoints[gType][_nextTime].slope =
                _max(oldTypeSlope + _newVoteData.slope, _oldVoteData.slope) -
                _oldVoteData.slope;
        } else {
            gaugePoints[_gAddr][_nextTime].slope += _newVoteData.slope;
            typePoints[gType][_nextTime].slope += _newVoteData.slope;
        }

        if (_oldVoteData.end > block.timestamp) {
            // Cancel old slope changes if they still didn't happen
            gaugeSlopeChanges[_gAddr][_oldVoteData.end] -= _oldVoteData.slope;
            typeSlopeChanges[gType][_oldVoteData.end] -= _oldVoteData.slope;
        }

        // Add slope changes for new slopes
        gaugeSlopeChanges[_gAddr][_newVoteData.end] += _newVoteData.slope;
        typeSlopeChanges[gType][_newVoteData.end] += _newVoteData.slope;
    }

    /**
     *  @notice Returns the gauge weight based on the last check-pointed data.
     *  @param _gAddr Address of the gauge.
     *  @param _time Timestamp.
     *  @return Gauge weight based on the Week start of the provided time.
     */
    function _getGaugeWeightReadOnly(address _gAddr, uint256 _time)
        private
        view
        returns (uint256)
    {
        // No gauge wt has been scheduled yet
        uint256 t = gaugeData[_gAddr].wtUpdateTime;
        if (t == 0) return 0;

        // Gauge wt is check-pointed for the timestamp
        _time = _getWeek(_time);
        if (_time <= t) {
            return gaugePoints[_gAddr][_time].bias;
        }

        // Gauge wt check-pointed gaps exist.
        uint256 gaps = (_time - t) / WEEK;

        Point memory pt = gaugePoints[_gAddr][t];

        uint256 w0 = gaugeData[_gAddr].w0;

        for (uint256 i = 0; i < gaps; i++) {
            t += WEEK;
            uint256 dBias = pt.slope * WEEK;
            if (pt.bias <= dBias + w0) {
                pt.bias = w0;
                break;
            }
            pt.bias -= dBias;
            pt.slope -= gaugeSlopeChanges[_gAddr][t];
        }

        return pt.bias;
    }

    /**
     *  @notice Returns the gauge base weight based on the last check-pointed data.
     *  @param _gAddr Address of the gauge.
     *  @param _time Timestamp.
     *  @return Gauge base weight based on the Week start of the provided time.
     */
    function _getGaugeBaseWeightReadOnly(address _gAddr, uint256 _time)
    private
    view
    returns (uint256)
    {
        uint256 t = timeGaugeBaseWt[_gAddr];
        _time = _getWeek(_time);

        // Gauge base wt is check-pointed for the timestamp
        if (_time <= t) {
            return gaugeBaseWtAtTime[_gAddr][_time];
        }

        // Gauge base wt check-pointed gaps exist.
        return gaugeBaseWtAtTime[_gAddr][t];
    }

    /**
     *  @notice Returns the type weight based on the last check-pointed data.
     *  @param _gType Type id.
     *  @param _time Timestamp.
     *  @return Type weight based on the Week start of the provided time.
     */
    function _getTypeWeightReadOnly(uint128 _gType, uint256 _time)
    private
    view
    returns (uint256)
    {
        // No type wt has been scheduled yet
        if (_gType >= MAX_NUM) return 0;
        uint256 t = lastTypeWtTime[_gType];
        if (t == 0) return 0;

        // Type wt is check-pointed for the timestamp
        _time = _getWeek(_time);
        if (_time <= t) {
            return typeWtAtTime[_gType][_time];
        }

        // Type wt check-pointed gaps exist.
        return typeWtAtTime[_gType][t];
    }

    /**
     *  @notice Returns the sum of gauge weights for the same type
     *  @param _gType Type id.
     *  @param _time Timestamp.
     *  @return Sum of weights
     */
    function _getSumWeightReadOnly(uint128 _gType, uint256 _time)
    private
    view
    returns (uint256)
    {
        uint256 sumWt = 0;
        address[] memory gaugeList = gauges;
        for (uint16 i = 0; i < gaugeList.length; i++) {
            address gAddr = gaugeList[i];
            if (_getGaugeType(gAddr) == _gType) {
                sumWt += _getGaugeWeightReadOnly(gAddr, _time);
            }
        }
        return sumWt;
    }

    /**
     *  @notice Returns the total weight based on the last check-pointed data.
     *  @param _time Timestamp.
     *  @return Total weight based on the Week start of the provided time.
     */
    function _getTotalWeightReadOnly(uint256 _time)
    private
    view
    returns (uint256)
    {
        uint256 totalWt = 0;
        address[] memory gaugeList = gauges;
        for (uint16 i = 0; i < gaugeList.length; i++) {
            address gAddr = gaugeList[i];
            uint128 gType = _getGaugeType(gAddr);
            uint256 gaugeWt = _getGaugeWeightReadOnly(gAddr, _time);
            uint256 typeWt = _getTypeWeightReadOnly(gType, _time);
            totalWt += gaugeWt * typeWt;
        }
        return totalWt;
    }

    /**
     *  @notice Get Gauge relative weight (not more than 1.0) normalized to 1e18
     *         (e.g. 1.0 == 1e18). Inflation which will be received by it is
     *         inflation_rate * relative_weight / 1e18
     *  @param _gAddr Gauge address
     *  @param _time Timestamp
     *  @return Value of relative weight normalized to 1e18
     */
    function _gaugeRelativeWeight(address _gAddr, uint256 _time)
        private
        view
        returns (uint256)
    {
        uint256 totalWeight = _getTotalWeightReadOnly(_time);
        if (totalWeight > 0) {
            uint128 gType = _getGaugeType(_gAddr);
            uint256 typeWeight = _getTypeWeightReadOnly(gType, _time);
            uint256 gaugeWeight = _getGaugeWeightReadOnly(_gAddr, _time);
            return (MULTIPLIER * typeWeight * gaugeWeight) / totalWeight;
        }
        return 0;
    }

    /**
     *  @notice Gets the gauge type.
     *  @param _gAddr Gauge address.
     *  @return Returns gauge type.
     */
    function _getGaugeType(address _gAddr) private view returns (uint128) {
        uint128 gType = gaugeData[_gAddr].gType;
        require(gType > 0, "Gauge not added");
        return gType - 1;
    }

    /**
     *  @notice Get the based on the ts.
     *  @param _ts arbitrary time stamp.
     *  @return returns the 00:00 am UTC for THU after _ts
     */
    function _getWeek(uint256 _ts) private pure returns (uint256) {
        return (_ts / WEEK) * WEEK;
    }

    function _max(uint256 _a, uint256 _b) private pure returns (uint256) {
        if (_a > _b) return _a;
        return _b;
    }

    /**
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *
     *      EVENTS
     *
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     */
    event TypeAdded(string name, uint128 typeId);
    event TypeWeightUpdated(
        uint128 typeId,
        uint256 time,
        uint256 weight,
        uint256 totalWeight
    );
    event GaugeBaseWeightUpdated(
        address indexed gAddr,
        uint256 time,
        uint256 baseWeight,
        uint256 gaugeWeight,
        uint256 totalWeight
    );
    event GaugeVoted(
        uint256 time,
        address indexed user,
        address indexed gAddr,
        uint256 weight,
        uint256 voteUsed
    );
    event GaugeAdded(address indexed addr, uint128 gType, uint256 weight);
}
