"""
sync/trading_orchestrator.py

P2P Energy Trading Orchestrator

Connects forecasting predictions to blockchain trading:
1. Load hourly energy forecast from forecasting/models.py
2. Mint ENERGY tokens on EnergyToken contract
3. Start auctions on AuctionEngine contract
4. Track settlement and revenue

This runs on hourly schedule (production) or manually for testing.

Usage:
    python sync/trading_orchestrator.py [--hour TIMESTAMP]
"""

import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

import pandas as pd
import numpy as np
from web3 import Web3
from dotenv import load_dotenv

# Configure logging
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            msg = self.format(record)
            msg = msg.encode('ascii', 'replace').decode('ascii')
            self.stream.write(msg + self.terminator)
            self.flush()

formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
file_handler = logging.FileHandler('logs/trading_orchestrator.log', encoding='utf-8')
file_handler.setFormatter(formatter)
stream_handler = SafeStreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Load environment
load_dotenv()

# ============== CONFIGURATION ==============

class TradingConfig:
    """Trading system configuration"""
    
    # Blockchain
    GANACHE_RPC = "http://localhost:8545"
    WEB3_TIMEOUT = 20
    
    # Contract addresses (from .env after deploy_trading.js)
    ENERGY_TOKEN_ADDRESS = os.environ.get("ENERGY_TOKEN_ADDRESS", "")
    AUCTION_ENGINE_ADDRESS = os.environ.get("AUCTION_ENGINE_ADDRESS", "")
    
    # Parameters
    MIN_AUCTION_ENERGY = 1  # Wh
    
    # ABIs
    ERC20_ABI = [
        {
            "name": "mintHourlyGeneration",
            "type": "function",
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_hour", "type": "uint256"},
                {"name": "_energyWh", "type": "uint256"}
            ],
            "outputs": []
        }
    ]
    
    AUCTION_ABI = [
        {
            "name": "startAuction",
            "type": "function",
            "inputs": [
                {"name": "_hour", "type": "uint256"},
                {"name": "_energyWh", "type": "uint256"}
            ],
            "outputs": []
        },
        {
            "name": "getAuctionDetails",
            "type": "function",
            "inputs": [{"name": "_auctionId", "type": "uint256"}],
            "outputs": [
                {"name": "hour", "type": "uint256"},
                {"name": "energyAvailable", "type": "uint256"},
                {"name": "highestBid", "type": "uint256"},
                {"name": "winner", "type": "address"},
                {"name": "settled", "type": "bool"},
                {"name": "bidDeadline", "type": "uint256"},
                {"name": "revealDeadline", "type": "uint256"}
            ]
        }
    ]


class TradingOrchestrator:
    """Manages P2P energy trading lifecycle"""
    
    def __init__(self, config: TradingConfig = None):
        """Initialize orchestrator with blockchain connection"""
        self.config = config or TradingConfig()
        self.w3 = Web3(Web3.HTTPProvider(self.config.GANACHE_RPC, request_kwargs={'timeout': self.config.WEB3_TIMEOUT}))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to Ganache at {self.config.GANACHE_RPC}")
        
        logger.info(f"✓ Connected to Ganache (chain ID: {self.w3.eth.chain_id})")
        
        # Initialize contracts
        self._init_contracts()
        
        # Trading state
        self.auction_count = 0
        self.total_energy_traded = 0  # Wh
        self.total_revenue = 0  # Wei
    
    def _init_contracts(self):
        """Initialize contract instances"""
        if not Web3.is_address(self.config.ENERGY_TOKEN_ADDRESS):
            raise ValueError(f"Invalid EnergyToken address: {self.config.ENERGY_TOKEN_ADDRESS}")
        
        if not Web3.is_address(self.config.AUCTION_ENGINE_ADDRESS):
            raise ValueError(f"Invalid AuctionEngine address: {self.config.AUCTION_ENGINE_ADDRESS}")
        
        self.energy_token = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.config.ENERGY_TOKEN_ADDRESS),
            abi=self.config.ERC20_ABI
        )
        
        self.auction_engine = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.config.AUCTION_ENGINE_ADDRESS),
            abi=self.config.AUCTION_ABI
        )
        
        logger.info(f"✓ Contracts initialized")
    
    def forecast_to_energy_tokens(self, forecast_kwh: float) -> int:
        """
        Convert forecast (kWh) to energy tokens (Wh)
        
        Args:
            forecast_kwh: Energy forecast in kWh
        
        Returns:
            Energy in Wh (1 token = 1 Wh)
        """
        energy_wh = int(forecast_kwh * 1000)  # kWh → Wh
        return max(energy_wh, self.config.MIN_AUCTION_ENERGY)
    
    def load_hourly_forecast(self, hour: Optional[int] = None) -> float:
        """
        Load energy forecast for hour from forecasting/models.py
        
        Args:
            hour: Unix timestamp of hour (default: current hour)
        
        Returns:
            Energy forecast in kWh
        """
        if hour is None:
            hour = int(datetime.now().timestamp())
        
        # Align to hour boundary
        hour = hour - (hour % 3600)
        
        # Try to load from forecast results
        forecast_file = Path("experiments/forecast_results.csv")
        if not forecast_file.exists():
            logger.warning(f"Forecast file not found: {forecast_file}")
            logger.info("Using synthetic forecast for testing (random 0.5-5 MWh)")
            return float(np.random.uniform(0.5, 5.0))  # Synthetic: 0.5-5 MWh
        
        try:
            df = pd.read_csv(forecast_file)
            # Assume forecast_results has columns: timestamp, forecast_power (kW)
            # And we need hourly sum
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            hourly = df.resample('H').agg({'forecast_power': 'mean'})
            
            # Return forecast for this hour (in kWh)
            forecast_kwh = float(hourly.loc[hourly.index == pd.Timestamp(hour, unit='s'), 'forecast_power'].iloc[0])
            return forecast_kwh / 1000 * 60  # Convert kW to kWh (per hour, so divide by 60 for per-minute)
        
        except Exception as e:
            logger.warning(f"Error loading forecast: {e}")
            return float(np.random.uniform(0.5, 5.0))
    
    def mint_hourly_tokens(self, hour: int, energy_forecast_kwh: float) -> Tuple[bool, str]:
        """
        Mint energy tokens for hourly forecast
        
        Args:
            hour: Unix timestamp of hour
            energy_forecast_kwh: Energy forecast in kWh
        
        Returns:
            (success: bool, tx_hash: str)
        """
        try:
            energy_wh = self.forecast_to_energy_tokens(energy_forecast_kwh)
            
            # Get default account (deployer)
            accounts = self.w3.eth.accounts
            if not accounts:
                raise ValueError("No accounts available")
            
            account = accounts[0]
            
            # Build transaction
            tx = self.energy_token.functions.mintHourlyGeneration(
                Web3.to_checksum_address(self.config.AUCTION_ENGINE_ADDRESS),
                hour,
                energy_wh
            ).build_transaction({
                'from': account,
                'nonce': self.w3.eth.get_transaction_count(account),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Send transaction
            tx_hash = self.w3.eth.send_transaction(tx)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✓ Minted {energy_wh} ENERGY tokens for hour {hour} (tx: {tx_hash.hex()[:8]}...)")
            
            return True, tx_hash.hex()
        
        except Exception as e:
            logger.error(f"✗ Token minting failed: {e}")
            return False, ""
    
    def start_auction(self, hour: int, energy_wh: int) -> Tuple[bool, Optional[int]]:
        """
        Start energy auction for hour
        
        Args:
            hour: Unix timestamp of hour
            energy_wh: Energy available in Wh
        
        Returns:
            (success: bool, auction_id: Optional[int])
        """
        try:
            accounts = self.w3.eth.accounts
            account = accounts[0]
            
            # Build transaction
            tx = self.auction_engine.functions.startAuction(hour, energy_wh).build_transaction({
                'from': account,
                'nonce': self.w3.eth.get_transaction_count(account),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Send transaction
            tx_hash = self.w3.eth.send_transaction(tx)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            auction_id = self.auction_count + 1
            self.auction_count += 1
            
            logger.info(f"✓ Started auction #{auction_id} for {energy_wh} Wh (tx: {tx_hash.hex()[:8]}...)")
            
            return True, auction_id
        
        except Exception as e:
            logger.error(f"✗ Auction start failed: {e}")
            return False, None
    
    def process_hour(self, hour: Optional[int] = None) -> Dict:
        """
        Process complete hourly trading cycle:
        1. Load forecast
        2. Mint tokens
        3. Start auction
        4. Log state
        
        Args:
            hour: Unix timestamp of hour (default: current hour)
        
        Returns:
            Trading event summary dict
        """
        if hour is None:
            hour = int(datetime.now().timestamp())
        
        hour = hour - (hour % 3600)  # Align to hour boundary
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing hour: {datetime.fromtimestamp(hour).isoformat()}")
        logger.info(f"{'='*60}")
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'hour': hour,
            'forecast_kwh': 0,
            'tokens_minted': 0,
            'auction_id': None,
            'auction_started': False,
            'errors': []
        }
        
        # Step 1: Load forecast
        try:
            forecast_kwh = self.load_hourly_forecast(hour)
            event['forecast_kwh'] = forecast_kwh
            tokens = self.forecast_to_energy_tokens(forecast_kwh)
            logger.info(f"→ Forecast: {forecast_kwh:.2f} kWh = {tokens} tokens")
        except Exception as e:
            logger.error(f"✗ Forecast loading failed: {e}")
            event['errors'].append(f"Forecast load error: {str(e)}")
            return event
        
        # Step 2: Mint tokens
        try:
            success, tx_hash = self.mint_hourly_tokens(hour, forecast_kwh)
            if success:
                event['tokens_minted'] = tokens
            else:
                raise Exception("Token minting failed")
        except Exception as e:
            logger.error(f"✗ Token minting failed: {e}")
            event['errors'].append(f"Minting error: {str(e)}")
            return event
        
        # Step 3: Start auction
        try:
            success, auction_id = self.start_auction(hour, tokens)
            if success:
                event['auction_id'] = auction_id
                event['auction_started'] = True
            else:
                raise Exception("Auction start failed")
        except Exception as e:
            logger.error(f"✗ Auction start failed: {e}")
            event['errors'].append(f"Auction error: {str(e)}")
            return event
        
        # Step 4: Log state
        self.total_energy_traded += tokens
        logger.info(f"✓ Hour processed successfully")
        logger.info(f"  Total energy in auctions: {self.total_energy_traded} Wh\n")
        
        return event
    
    def run_continuous(self, interval_minutes: int = 60):
        """
        Run trading orchestrator in continuous mode (production)
        Creates new auction every `interval_minutes`
        
        Args:
            interval_minutes: Minutes between auctions (default: 60 = hourly)
        """
        logger.info(f"Starting continuous trading (interval: {interval_minutes} min)")
        
        while True:
            try:
                # Process current hour
                current_hour = int(datetime.now().timestamp())
                event = self.process_hour(current_hour)
                
                # Save log (JSONL format: one JSON per line)
                log_path = Path("logs/trading_log.json")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, 'a') as f:
                    f.write(json.dumps(event) + '\n')
                
                # Wait for next interval
                logger.info(f"Waiting {interval_minutes} minutes for next auction...")
                import time
                time.sleep(interval_minutes * 60)
            
            except KeyboardInterrupt:
                logger.info("Stopping trading orchestrator")
                break
            except Exception as e:
                logger.error(f"Unexpected error in continuous mode: {e}")
                import time
                time.sleep(60)  # Retry after 1 minute


def main():
    """Main entry point"""
    import os
    
    # Create logs directory
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Initialize orchestrator
    try:
        orchestrator = TradingOrchestrator()
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        sys.exit(1)
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--hour" and len(sys.argv) > 2:
            # Process specific hour
            try:
                hour = int(sys.argv[2])
                logger.info(f"Processing hour: {hour}")
                event = orchestrator.process_hour(hour)
                
                # Save to file (JSONL format: one JSON per line)
                log_path = Path("logs/trading_log.json")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(log_path, 'a') as f:
                    f.write(json.dumps(event) + '\n')
                
                print(json.dumps(event, indent=2))
                logger.info(f"Trading log saved to: {log_path}")
            except ValueError:
                logger.error(f"Invalid hour timestamp: {sys.argv[2]}")
                sys.exit(1)
        elif sys.argv[1] == "--continuous":
            # Run in continuous mode
            orchestrator.run_continuous()
        else:
            logger.error(f"Unknown argument: {sys.argv[1]}")
            sys.exit(1)
    else:
        # Default: process current hour once
        event = orchestrator.process_hour()
        
        # Save to file (JSONL format: one JSON per line)
        log_path = Path("logs/trading_log.json")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logger.info(f"Trading log saved to: {log_path}")


if __name__ == "__main__":
    main()
