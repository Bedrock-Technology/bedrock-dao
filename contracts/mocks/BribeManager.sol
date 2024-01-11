// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract BribeManager is Initializable, PausableUpgradeable, OwnableUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;
    using Address for address;

    struct Pool {
        address _market;
        bool _active;
        uint256 _chainId;
    }
    
    struct Bribe {
        address _token;
        uint256 _amount;
    }

    struct PoolVotes {
        address _bribe;
        uint256 _votes;
    }
    
    address constant NATIVE = address(1);
    uint256 constant DENOMINATOR = 10000;

    uint256 public epochPeriod;
    uint256 public epochStartTime;
    uint256 private currentEpoch;
    
    Pool[] public pools;
    mapping(address => uint256) public marketToPid;
    mapping(address => uint256) public unCollectedFee;


    address[] public allowedTokens;
    mapping(address => bool) public allowedToken;
    mapping(bytes32 => Bribe) public bribes;  // The index is hashed based on the epoch, pid and token address
    mapping(bytes32 => bytes32[]) public bribesInPool;  // Mapping pool => bribes. The index is hashed based on the epoch, pid

    address payable public distributor;
    address payable private feeCollector;
    uint256 public feeRatio;
    uint256 public maxBribingBatch;

    error InvalidBatch();
    error InvalidPool();
    error InvalidBribeToken();
    error ZeroAddress();
    error MarketExists();

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
    
    function initialize() initializer public {
        __Pausable_init();
        __Ownable_init();
        __ReentrancyGuard_init();

        epochPeriod = 1;
        currentEpoch = 0;
        
        maxBribingBatch = 8;
        feeRatio = 0;
    }

    function exactCurrentEpoch() public view returns (uint256) {
        if (epochStartTime == 0) return 0;

        uint256 epochEndTime = epochStartTime + epochPeriod;
        if (block.timestamp > epochEndTime)
            return currentEpoch + 1;
        else
            return currentEpoch;
    }

    function getCurrentEpochEndTime() public view returns(uint256 endTime) {
        endTime = epochStartTime + epochPeriod;
    }

    function getApprovedTokens() public view returns(address[] memory) {
        return allowedTokens;
    }

    function getPoolLength() public view returns(uint256) {
        return pools.length;
    }

    
    function addBribeERC20(uint256 _batch, uint256 _pid, address _token, uint256 _amount) external nonReentrant whenNotPaused {
        _addBribeERC20(_batch, _pid, _token, _amount);
    }

    function _addBribeERC20(uint256 _batch, uint256 _pid, address _token, uint256 _amount /*, bool forVePendle */) internal {
        if (_batch == 0 || _batch > maxBribingBatch) revert InvalidBatch();
        if (_pid >= pools.length || !pools[_pid]._active) revert InvalidPool();
        if (!allowedToken[_token] && _token != NATIVE) revert InvalidBribeToken();

        uint256 startFromEpoch = exactCurrentEpoch();
        uint256 totalFee = 0;
        uint256 totalBribing = 0;
        uint256 totalBribingForVePendle = 0;

        uint256 bribePerEpoch = _amount / _batch;
        uint256 bribePerEpochForVlPNP = bribePerEpoch;
        uint256 bribePerEpochForVePendle = 0;
        
        // if (forVePendle) {
        //     bribePerEpochForVlPNP = bribePerEpoch * pnpBribingRatio / DENOMINATOR;
        //     bribePerEpochForVePendle = bribePerEpoch - bribePerEpochForVlPNP;
        // }

        for (uint256 epoch = startFromEpoch; epoch < startFromEpoch + _batch; epoch++) {
            // if (forVePendle && bribePerEpochForVePendle > 0) {
            //     (uint256 feeForVePendle, uint256 afterFeeForVePendle) = _addBribeForVePendle(epoch, _pid, _token, bribePerEpochForVePendle);
            //     totalFee += feeForVePendle;
            //     totalBribingForVePendle += afterFeeForVePendle;
            // }

            (uint256 fee, uint256 afterFee) = _addBribe(epoch, _pid, _token, bribePerEpochForVlPNP);
            totalFee += fee;
            totalBribing += afterFee;
        }

        // transfer the token to the target directly in one time to save the gas fee
        if (totalFee > 0) {
            if (feeCollector == address(0)) {
                unCollectedFee[_token] += totalFee;
                IERC20(_token).safeTransferFrom(msg.sender, address(this), totalFee);
            } else {
                IERC20(_token).safeTransferFrom(msg.sender, feeCollector, totalFee);
            }
        }
        
        IERC20(_token).safeTransferFrom(msg.sender, address(this) /* distributer */, totalBribing);
        // if (forVePendle && totalBribingForVePendle > 0) {
        //     IERC20(_token).safeTransferFrom(msg.sender, distributorForVePendle, totalBribingForVePendle);
        // }
    }

    function _addBribe(uint256 _epoch, uint256 _pid, address _token, uint256 _amount) internal returns (uint256 fee, uint256 afterFee) {
        fee = _amount * feeRatio / DENOMINATOR;
        afterFee = _amount - fee;

        // We will generate a unique index for each pool and reward based on the epoch
        bytes32 poolIdentifier = _getPoolIdentifier(_epoch, _pid);
        bytes32 rewardIdentifier = _getTokenIdentifier(_epoch, _pid, _token);

        Bribe storage bribe = bribes[rewardIdentifier];
        bribe._amount += afterFee;
        if(bribe._token == address(0)) {
            bribe._token = _token;
            bribesInPool[poolIdentifier].push(rewardIdentifier);
        }

        emit NewBribe(msg.sender, _epoch, _pid, _token, afterFee);
    }

    function newPool(address _market, uint16 _chainId) external onlyOwner {
        if (_market == address(0)) revert ZeroAddress();

        for (uint256 i = 0; i < pools.length; i++) {
            if (pools[i]._market == _market) {
                revert MarketExists();
            }
        }

        Pool memory pool = Pool(_market, true, _chainId);
        pools.push(pool);

        marketToPid[_market] = pools.length - 1;
        emit NewPool(_market, _chainId);
    }

    function addAllowedTokens(address _token) external onlyOwner {
        if (allowedToken[_token]) revert InvalidBribeToken();

        allowedTokens.push(_token);

        allowedToken[_token] = true;
    }

    function _getPoolIdentifier(uint256 _epoch, uint256 _pid) internal pure returns (bytes32) {
        return
            keccak256(
                abi.encodePacked(_epoch, _pid)
            );
    }

    function _getTokenIdentifier(uint256 _epoch, uint256 _pid, address _token) internal pure returns (bytes32) {
        return
            keccak256(
                abi.encodePacked(_epoch, _pid, _token)
            );
    }
    
    function getBribesInPool(uint256 _epoch, uint256 _pid) public view returns (Bribe[] memory) {
        if (_pid >= getPoolLength()) revert InvalidPool();
        
        bytes32 poolIdentifier = _getPoolIdentifier(_epoch, _pid);

        bytes32[] memory poolBribes = bribesInPool[poolIdentifier];
        Bribe[] memory rewards = new Bribe[](poolBribes.length);

        for (uint256 i = 0; i < poolBribes.length; i++) {
            rewards[i] = bribes[poolBribes[i]];
        }

        return rewards;
    }

    event NewBribe(address indexed _user, uint256 indexed _epoch, uint256 _pid, address _bribeToken, uint256 _amount);
    event NewPool(address indexed _market, uint256 _chainId);
}