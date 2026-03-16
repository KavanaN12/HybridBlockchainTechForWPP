// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./EnergyToken.sol";

/**
 * @title AuctionEngine
 * @dev Sealed-bid auction mechanism for peer-to-peer energy trading
 * 
 * Flow:
 * 1. Energy tokens minted hourly (EnergyToken.mintHourlyGeneration)
 * 2. Auction opens → buyers place sealed bids (commitments)
 * 3. Auction closes at hour end
 * 4. Bids revealed and winner determined (highest price)
 * 5. Settlement: tokens → buyer, ETH → turbine owner
 * 6. Tokens burned upon consumption
 * 
 * Design:
 * - Sealed-bid prevents price manipulation (bids not visible until reveal)
 * - Hash commitment: keccak256(price, nonce) prevents bid modification
 * - Single-unit auction: simplifies settlement (1 auction = 1 hour energy)
 * - Scalable: Can run 24 auctions/day (one per hour)
 */
contract AuctionEngine is Ownable {
    
    // Events
    event AuctionStarted(
        uint256 indexed auctionId,
        uint256 indexed hour,
        uint256 energyAvailable,
        uint256 startTime,
        uint256 bidDeadline,
        uint256 revealDeadline
    );
    
    event BidPlaced(
        uint256 indexed auctionId,
        address indexed buyer,
        bytes32 bidCommitment
    );
    
    event BidRevealed(
        uint256 indexed auctionId,
        address indexed buyer,
        uint256 price,
        bool valid
    );
    
    event AuctionSettled(
        uint256 indexed auctionId,
        address indexed winner,
        uint256 pricePerToken,
        uint256 energyTraded,
        uint256 totalValue,
        uint256 timestamp
    );
    
    event AuctionCancelled(uint256 indexed auctionId, string reason);
    
    // Auction struct
    struct Auction {
        uint256 auctionId;
        uint256 hour;  // Hour timestamp (epoch seconds)
        uint256 energyAvailable;  // Tokens available
        uint256 bidDeadline;  // When to stop accepting bids
        uint256 revealDeadline;  // When to stop accepting reveals
        uint256 highestBid;  // Highest price (wei per token)
        address winner;  // Winning bidder
        bool settled;  // Whether settlement completed
        uint256 settlementTime;
        mapping(address => bytes32) bids;  // Sealed bid commitments
        mapping(address => bool) revealed;  // Track who revealed
        address[] bidders;  // List of bidders for iteration
    }
    
    // State variables
    EnergyToken public energyToken;
    address public turbineOwner;  // Receives ETH from sales
    
    mapping(uint256 => Auction) public auctions;  // auctionId → Auction
    mapping(uint256 => uint256) public hourToAuctionId;  // hour → auctionId for quick lookup
    
    uint256 public auctionCounter = 0;
    uint256 public constant BID_DURATION = 30 minutes;  // Time window to place bids
    uint256 public constant REVEAL_DURATION = 10 minutes;  // Time window to reveal
    
    // Constants
    uint256 public constant MIN_ENERGY_FOR_AUCTION = 1;  // 1 Wh minimum
    
    constructor(address _energyToken, address _turbineOwner) Ownable(msg.sender) {
        require(_energyToken != address(0), "Invalid token address");
        require(_turbineOwner != address(0), "Invalid turbine owner");
        
        energyToken = EnergyToken(_energyToken);
        turbineOwner = _turbineOwner;
    }
    
    /**
     * @dev Start new hourly auction
     * Called by trading_orchestrator.py at each hour
     * 
     * @param _hour Hour timestamp (unix seconds)
     * @param _energyWh Energy available for this hour (in Wh)
     */
    function startAuction(uint256 _hour, uint256 _energyWh) external onlyOwner {
        require(_energyWh >= MIN_ENERGY_FOR_AUCTION, "Insufficient energy");
        require(hourToAuctionId[_hour] == 0, "Auction already exists for this hour");
        
        uint256 auctionId = ++auctionCounter;
        Auction storage auction = auctions[auctionId];
        
        auction.auctionId = auctionId;
        auction.hour = _hour;
        auction.energyAvailable = _energyWh;
        auction.bidDeadline = block.timestamp + BID_DURATION;
        auction.revealDeadline = auction.bidDeadline + REVEAL_DURATION;
        auction.settled = false;
        
        hourToAuctionId[_hour] = auctionId;
        
        emit AuctionStarted(
            auctionId,
            _hour,
            _energyWh,
            block.timestamp,
            auction.bidDeadline,
            auction.revealDeadline
        );
    }
    
    /**
     * @dev Place sealed bid (commitment only, price hidden)
     * Buyer sends commitment = keccak256(price, nonce)
     * 
     * @param _auctionId Auction ID
     * @param _commitment keccak256 hash of (price, nonce)
     */
    function placeBid(uint256 _auctionId, bytes32 _commitment) external {
        Auction storage auction = auctions[_auctionId];
        require(block.timestamp <= auction.bidDeadline, "Bidding closed");
        require(_commitment != bytes32(0), "Invalid commitment");
        require(auction.bids[msg.sender] == bytes32(0), "Bid already placed");
        
        auction.bids[msg.sender] = _commitment;
        auction.bidders.push(msg.sender);
        
        emit BidPlaced(_auctionId, msg.sender, _commitment);
    }
    
    /**
     * @dev Reveal sealed bid with actual price
     * Verifies commitment matches keccak256(price, nonce)
     * 
     * @param _auctionId Auction ID
     * @param _price Price per token (wei)
     * @param _nonce Random nonce used to seal bid
     */
    function revealBid(uint256 _auctionId, uint256 _price, uint256 _nonce) external {
        Auction storage auction = auctions[_auctionId];
        require(block.timestamp > auction.bidDeadline, "Bid period not closed");
        require(block.timestamp <= auction.revealDeadline, "Reveal period closed");
        require(!auction.revealed[msg.sender], "Already revealed");
        require(auction.bids[msg.sender] != bytes32(0), "No bid found");
        
        // Verify commitment
        bytes32 computedCommitment = keccak256(abi.encodePacked(_price, _nonce));
        require(computedCommitment == auction.bids[msg.sender], "Invalid reveal");
        
        auction.revealed[msg.sender] = true;
        
        // Track highest bid
        if (_price > auction.highestBid) {
            auction.highestBid = _price;
            auction.winner = msg.sender;
        }
        
        emit BidRevealed(_auctionId, msg.sender, _price, true);
    }
    
    /**
     * @dev Settle auction after reveal period ends
     * Transfer tokens to winner, ETH to turbine owner
     * Burn tokens to mark consumption
     */
    function settleAuction(uint256 _auctionId) external {
        Auction storage auction = auctions[_auctionId];
        require(block.timestamp > auction.revealDeadline, "Reveal period not closed");
        require(!auction.settled, "Already settled");
        require(auction.winner != address(0), "No valid bids");
        
        auction.settled = true;
        auction.settlementTime = block.timestamp;
        
        uint256 totalValue = auction.energyAvailable * auction.highestBid;
        
        // Transfer tokens from AuctionEngine to winner
        require(
            energyToken.transfer(auction.winner, auction.energyAvailable),
            "Token transfer failed"
        );
        
        // Burn tokens to mark consumed
        energyToken.burnOnSettlement(_auctionId, auction.energyAvailable, auction.winner);
        
        // Transfer ETH to turbine owner
        (bool success, ) = turbineOwner.call{value: totalValue}("");
        require(success, "ETH transfer failed");
        
        emit AuctionSettled(
            _auctionId,
            auction.winner,
            auction.highestBid,
            auction.energyAvailable,
            totalValue,
            block.timestamp
        );
    }
    
    /**
     * @dev Cancel auction if no valid bids (emergency)
     */
    function cancelAuction(uint256 _auctionId, string calldata _reason) external onlyOwner {
        Auction storage auction = auctions[_auctionId];
        require(!auction.settled, "Already settled");
        
        auction.settled = true;  // Mark as settled to prevent double-settlement
        
        // Return tokens to owner
        energyToken.transfer(msg.sender, auction.energyAvailable);
        
        emit AuctionCancelled(_auctionId, _reason);
    }
    
    // ============== VIEW FUNCTIONS ==============
    
    /**
     * @dev Get auction details
     */
    function getAuctionDetails(uint256 _auctionId) 
        external view 
        returns (
            uint256 hour,
            uint256 energyAvailable,
            uint256 highestBid,
            address winner,
            bool settled,
            uint256 bidDeadline,
            uint256 revealDeadline
        ) 
    {
        Auction storage auction = auctions[_auctionId];
        return (
            auction.hour,
            auction.energyAvailable,
            auction.highestBid,
            auction.winner,
            auction.settled,
            auction.bidDeadline,
            auction.revealDeadline
        );
    }
    
    /**
     * @dev Get auction for specific hour
     */
    function getAuctionByHour(uint256 _hour) external view returns (uint256) {
        return hourToAuctionId[_hour];
    }
    
    /**
     * @dev Get number of bidders for auction
     */
    function getBidderCount(uint256 _auctionId) external view returns (uint256) {
        return auctions[_auctionId].bidders.length;
    }
    
    /**
     * @dev Check if address has bid in auction
     */
    function hasBid(uint256 _auctionId, address _bidder) external view returns (bool) {
        return auctions[_auctionId].bids[_bidder] != bytes32(0);
    }
    
    /**
     * @dev Get total ETH revenue generated (sum of all settled auctions)
     */
    function getTotalRevenue() external view returns (uint256) {
        return address(this).balance;
    }
    
    // Allow contract to receive ETH
    receive() external payable {}
}
