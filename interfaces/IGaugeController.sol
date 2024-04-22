// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.9;

interface IGaugeController {
    struct VoteData {
        uint256 slope;
        uint256 power;
        uint256 end;
        uint256 voteTime;
    }

    /// @notice Checkpoint to fill data common for all gauges
    function checkpoint() external;

    /// @notice Checkpoints for the given gauge for missing weeks
    function checkpointGauge(address _gAddr) external;

    /// @notice Checkpoints for all registered gauges for missing weeks
    function checkpointGauge() external;

    ///  @notice Allocate voting power for changing pool weights
    ///  @param _gAddr Gauge which `msg.sender` votes for
    ///  @param _userWeight Weight for a gauge in bps (units of 0.01%). Minimal is 0.01%. Ignored if 0
    function voteForGaugeWeight(address _gAddr, uint256 _userWeight) external;

    /// @notice gets the number of gauge registered with the controller.
    function nGauges() external view returns (uint256);

    /// @notice Get gauge type for address
    /// @param _gAddr Gauge address
    /// @return Gauge type id
    function gaugeType(address _gAddr) external view returns (uint128);

    ///  @notice Get gauge relative weight (not more than 1.0), normalized to 1e18
    ///         (e.g. 1.0 == 1e18). Inflation which will be received by it is
    ///         inflation_rate * relative_weight / 1e18
    ///  @param _gAddr Gauge address
    ///  @param _time Timestamp
    ///  @return Gauge relative weight, normalized to 1e18
    function gaugeRelativeWeight(address _gAddr, uint256 _time)
        external
        view
        returns (uint256);

    ///  @notice Get current gauge relative weight (not more than 1.0), normalized to 1e18
    ///         (e.g. 1.0 == 1e18). Inflation which will be received by it is
    ///         inflation_rate * relative_weight / 1e18
    ///  @param _gAddr Gauge address
    ///  @return Gauge relative weight, normalized to 1e18
    function gaugeRelativeWeight(address _gAddr)
        external
        view
        returns (uint256);

    ///  @notice Get current gauge weight
    ///  @param _gAddr Gauge address
    ///  @return Gauge weight
    function getGaugeWeight(address _gAddr) external view returns (uint256);

    ///  @notice Get gauge weight
    ///  @param _gAddr Gauge address
    ///  @param _time Timestamp
    ///  @return Gauge weight
    function getGaugeWeight(address _gAddr, uint256 _time)
        external
        view
        returns (uint256);

    ///  @notice Get current gaugeWeight - w0 (base weight)
    ///  @param _gAddr Gauge address
    ///  @return Vote weight for the gauge.
    function getUserVotesWtForGauge(address _gAddr)
        external
        view
        returns (uint256);

    ///  @notice Get gaugeWeight - w0 (base weight)
    ///  @param _gAddr Gauge address
    ///  @return Vote weight for the gauge.
    function getUserVotesWtForGauge(address _gAddr, uint256 _time)
    external
    view
    returns (uint256);

    /// @notice Get the user's vote data for a gauge.
    /// @param _user Address of the user
    /// @param _gAddr Address of the gauge.
    /// @return Returns VoteData struct.
    function userVoteData(address _user, address _gAddr)
        external
        view
        returns (VoteData memory);

    ///  @notice Get current gauge base weight
    ///  @param _gAddr Gauge address
    ///  @return Gauge base weight
    function getGaugeBaseWeight(address _gAddr)
        external
        view
        returns (uint256);

    ///  @notice Get gauge base weight
    ///  @param _gAddr Gauge address
    ///  @param _time Timestamp
    ///  @return Gauge base weight
    function getGaugeBaseWeight(address _gAddr, uint256 _time)
        external
        view
        returns (uint256);

    /// @notice Get current type weight
    ///  @param _gType Type id
    ///  @return Type weight
    function getTypeWeight(uint128 _gType)
        external
        view
        returns (uint256);

    ///  @notice Get type weight
    ///  @param _gType Type id
    ///  @param _time Timestamp
    ///  @return Type weight
    function getTypeWeight(uint128 _gType, uint256 _time)
        external
        view
        returns (uint256);

    ///  @notice Get current total (type-weighted) weight
    ///  @return Total weight
    function getTotalWeight()
        external
        view
        returns (uint256);

    ///  @notice Get total (type-weighted) weight
    ///  @param _time Timestamp
    ///  @return Total weight
    function getTotalWeight(uint256 _time)
        external
        view
        returns (uint256);

    ///  @notice Get current sum of gauge weights per type
    ///  @param _gType Type id
    ///  @return Sum of gauge weights
    function getWeightsSumPerType(uint128 _gType)
        external
        view
        returns (uint256);

    ///  @notice Get sum of gauge weights per type
    ///  @param _gType Type id
    ///  @param _time Timestamp
    ///  @return Sum of gauge weights
    function getWeightsSumPerType(uint128 _gType, uint256 _time)
        external
        view
        returns (uint256);

    ///  @notice Returns address of all registered gauges.
    function getGaugeList()
        external
        view
        returns (address[] memory);

    ///  @notice Get last gauge weight schedule time
    ///  @param _gAddr Gauge address
    ///  @return Last schedule time
    function getLastGaugeWtScheduleTime(address _gAddr)
        external
        view
        returns (uint256);

    ///  @notice Get last gauge base weight schedule time
    ///  @param _gAddr Gauge address
    ///  @return Last schedule time
    function getLastGaugeBaseWtScheduleTime(address _gAddr)
        external
        view
        returns (uint256);

    ///  @notice Get last type weight schedule time
    ///  @param _gType Gauge type
    ///  @return Last schedule time
    function getLastTypeWtScheduleTime(uint128 _gType)
        external
        view
        returns (uint256);

    ///  @notice Get last sum weight schedule time for a gauge type
    ///  @param _gType Gauge type
    ///  @return Last schedule time
    function getLastSumWtScheduleTime(uint128 _gType)
        external
        view
        returns (uint256);

    ///  @notice Get last total weight schedule time
    ///  @return Last schedule time
    function getLastTotalWtScheduleTime()
        external
        view
        returns (uint256);
}
