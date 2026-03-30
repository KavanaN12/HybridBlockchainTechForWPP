from sync.trading_orchestrator import TradingOrchestrator

# Initialize and start the trading orchestrator
if __name__ == "__main__":
    orchestrator = TradingOrchestrator()
    orchestrator.run_continuous(interval_minutes=60)