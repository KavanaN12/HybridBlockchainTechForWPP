// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * Smart contract for storing data integrity proofs
 * Stores batch hashes from wind turbine SCADA data
 */
contract DataAnchor {
    // Store batch records with hash, energy, and timestamp
    struct BatchRecord {
        bytes32 batchHash;
        uint256 totalEnergy;
        uint256 timestamp;
    }
    
    mapping(uint256 => BatchRecord) public batches;
    uint256 public batchCount = 0;
    
    event BatchStored(uint256 indexed hour, bytes32 batchHash, uint256 totalEnergy);
    
    function storeBatchHash(
        uint256 hour,
        bytes32 batchHash,
        uint256 totalEnergy
    ) public {
        batches[hour] = BatchRecord(batchHash, totalEnergy, block.timestamp);
        batchCount++;
        emit BatchStored(hour, batchHash, totalEnergy);
    }
    
    function verifyIntegrity(uint256 hour, bytes32 expectedHash) public view returns (bool) {
        return batches[hour].batchHash == expectedHash;
    }
    
    function getBatch(uint256 hour) public view returns (BatchRecord memory) {
        return batches[hour];
    }
}
