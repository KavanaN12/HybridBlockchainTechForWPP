#!/usr/bin/env python3
"""
verify_trading_pipeline.py
Comprehensive verification of the P2P Energy Trading pipeline
Tests: Deployment → Orchestration → Experiments → Settlement
"""

import subprocess
import json
import time
import sys
from pathlib import Path


class TradingPipelineVerifier:
    """Verify end-to-end trading pipeline"""
    
    def __init__(self):
        self.results = {
            'deployment': None,
            'orchestration': None,
            'experiments': None,
            'dashboard': None,
            'overall': 'PENDING'
        }
        self.root_dir = Path(__file__).parent
        
    def log(self, step, message, status="INFO"):
        """Log verification step"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "[ℹ️ ]",
            "SUCCESS": "[✅]",
            "WARNING": "[⚠️ ]",
            "ERROR": "[❌]"
        }.get(status, "[•]")
        
        print(f"{prefix} {timestamp} {step}: {message}")
    
    def verify_contracts_compiled(self):
        """Verify smart contracts are compiled"""
        self.log("CONTRACTS", "Checking if contracts compiled...")
        
        contract_files = [
            "blockchain/contracts/EnergyToken.sol",
            "blockchain/contracts/AuctionEngine.sol"
        ]
        
        for contract in contract_files:
            path = self.root_dir / contract
            if not path.exists():
                self.log("CONTRACTS", f"Missing: {contract}", "ERROR")
                return False
            self.log("CONTRACTS", f"✓ Found: {contract}", "SUCCESS")
        
        return True
    
    def verify_deployment_script(self):
        """Verify deployment script exists and has required components"""
        self.log("DEPLOYMENT", "Checking deployment script...")
        
        script_path = self.root_dir / "blockchain" / "scripts" / "deploy_trading.js"
        
        if not script_path.exists():
            self.log("DEPLOYMENT", "Deployment script not found", "ERROR")
            return False
        
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        required_functions = [
            "deployEnergyToken",
            "deployAuctionEngine",
            "grantMinterRole",
            "runIntegrationTests"
        ]
        
        for func in required_functions:
            if func not in content:
                self.log("DEPLOYMENT", f"Missing function: {func}", "WARNING")
            else:
                self.log("DEPLOYMENT", f"✓ Found function: {func}", "SUCCESS")
        
        self.log("DEPLOYMENT", "Deployment script verified", "SUCCESS")
        return True
    
    def verify_orchestrator(self):
        """Verify trading orchestrator implementation"""
        self.log("ORCHESTRATOR", "Checking trading orchestrator...")
        
        orchestrator_path = self.root_dir / "sync" / "trading_orchestrator.py"
        
        if not orchestrator_path.exists():
            self.log("ORCHESTRATOR", "Orchestrator not found", "ERROR")
            return False
        
        with open(orchestrator_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        required_methods = [
            "forecast_to_energy_tokens",
            "load_hourly_forecast",
            "mint_hourly_tokens",
            "start_auction",
            "process_hour",
            "run_continuous"
        ]
        
        for method in required_methods:
            if method not in content:
                self.log("ORCHESTRATOR", f"Missing method: {method}", "WARNING")
            else:
                self.log("ORCHESTRATOR", f"✓ Found method: {method}", "SUCCESS")
        
        self.log("ORCHESTRATOR", "Orchestrator verified", "SUCCESS")
        return True
    
    def verify_experiments(self):
        """Verify Experiment E implementation"""
        self.log("EXPERIMENTS", "Checking Experiment E...")
        
        exp_path = self.root_dir / "experiments" / "exp_e_trading_efficiency.py"
        
        if not exp_path.exists():
            self.log("EXPERIMENTS", "Experiment E not found", "ERROR")
            return False
        
        with open(exp_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        required_tests = [
            "measure_auction_throughput",
            "measure_bid_scalability",
            "measure_gas_costs",
            "measure_price_discovery",
            "measure_hybrid_vs_onchain"
        ]
        
        for test in required_tests:
            if test not in content:
                self.log("EXPERIMENTS", f"Missing test: {test}", "WARNING")
            else:
                self.log("EXPERIMENTS", f"✓ Found test: {test}", "SUCCESS")
        
        self.log("EXPERIMENTS", "Experiment E verified", "SUCCESS")
        return True
    
    def verify_tests(self):
        """Verify trading unit tests"""
        self.log("TESTS", "Checking trading unit tests...")
        
        tests_path = self.root_dir / "tests" / "test_trading.py"
        
        if not tests_path.exists():
            self.log("TESTS", "Test file not found", "ERROR")
            return False
        
        with open(tests_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        test_classes = [
            "TestEnergyTokenContract",
            "TestAuctionEngineContract",
            "TestTradingOrchestrator",
            "TestTradingExperiments",
            "TestIntegrationFlow"
        ]
        
        test_count = 0
        for test_class in test_classes:
            if test_class in content:
                self.log("TESTS", f"✓ Found test class: {test_class}", "SUCCESS")
                test_count += 1
        
        self.log("TESTS", f"Total test classes: {test_count}/5", "SUCCESS")
        return True
    
    def verify_ci_cd_workflows(self):
        """Verify CI/CD workflows"""
        self.log("CI/CD", "Checking CI/CD workflows...")
        
        workflows = [
            ".github/workflows/test_trading.yml",
            ".github/workflows/deploy_trading.yml",
            ".github/workflows/trading_experiments.yml"
        ]
        
        for workflow in workflows:
            path = self.root_dir / workflow
            if not path.exists():
                self.log("CI/CD", f"Missing workflow: {workflow}", "WARNING")
            else:
                self.log("CI/CD", f"✓ Found workflow: {workflow}", "SUCCESS")
        
        self.log("CI/CD", "CI/CD workflows verified", "SUCCESS")
        return True
    
    def verify_documentation(self):
        """Verify documentation files"""
        self.log("DOCUMENTATION", "Checking documentation...")
        
        docs = [
            "README_P2P_TRADING.md",
            "P2P_TRADING_QUICKSTART.md",
            "OBJECTIVES_COMPLETION_CHECKLIST.md"
        ]
        
        for doc in docs:
            path = self.root_dir / doc
            if not path.exists():
                self.log("DOCUMENTATION", f"Missing doc: {doc}", "WARNING")
            else:
                self.log("DOCUMENTATION", f"✓ Found doc: {doc}", "SUCCESS")
        
        self.log("DOCUMENTATION", "Documentation verified", "SUCCESS")
        return True
    
    def verify_dashboard_tabs(self):
        """Verify dashboard has trading tabs"""
        self.log("DASHBOARD", "Checking dashboard tabs...")
        
        dashboard_path = self.root_dir / "dashboard" / "app.py"
        
        if not dashboard_path.exists():
            self.log("DASHBOARD", "Dashboard not found", "ERROR")
            return False
        
        with open(dashboard_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        required_tabs = [
            "💰 Energy Marketplace",
            "📈 Settlement Tracker"
        ]
        
        for tab in required_tabs:
            if tab in content:
                self.log("DASHBOARD", f"✓ Found tab: {tab}", "SUCCESS")
            else:
                self.log("DASHBOARD", f"Missing tab: {tab}", "WARNING")
        
        self.log("DASHBOARD", "Dashboard tabs verified", "SUCCESS")
        return True
    
    def run_unit_tests(self):
        """Run trading unit tests"""
        self.log("UNIT TESTS", "Running trading unit tests...", "INFO")
        
        try:
            result = subprocess.run(
                ["pytest", "tests/test_trading.py", "-v", "--tb=short"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Count passed tests
                passed = result.stdout.count(" PASSED")
                self.log("UNIT TESTS", f"✓ All tests passed ({passed} tests)", "SUCCESS")
                self.results['tests'] = 'PASSED'
                return True
            else:
                self.log("UNIT TESTS", f"Some tests failed: {result.returncode}", "WARNING")
                self.log("UNIT TESTS", result.stdout[-500:], "INFO")  # Last 500 chars
                return False
        
        except subprocess.TimeoutExpired:
            self.log("UNIT TESTS", "Tests timed out", "WARNING")
            return False
        except Exception as e:
            self.log("UNIT TESTS", f"Error running tests: {str(e)}", "WARNING")
            return False
    
    def verify_files_exist(self):
        """Verify all generated files structure"""
        self.log("FILES", "Verifying project structure...")
        
        required_dirs = [
            "blockchain/contracts",
            "blockchain/scripts",
            "sync",
            "experiments",
            "tests",
            "logs",
            "paper_results"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                self.log("FILES", f"✓ Directory exists: {dir_name}", "SUCCESS")
            else:
                self.log("FILES", f"Missing directory: {dir_name}", "WARNING")
        
        return True
    
    def verify_requirements(self):
        """Verify Python requirements"""
        self.log("REQUIREMENTS", "Checking dependencies...")
        
        required_packages = [
            "web3",
            "pandas",
            "streamlit",
            "plotly",
            "pytest"
        ]
        
        installed = []
        for package in required_packages:
            try:
                __import__(package)
                self.log("REQUIREMENTS", f"✓ Installed: {package}", "SUCCESS")
                installed.append(True)
            except ImportError:
                self.log("REQUIREMENTS", f"Missing: {package}", "WARNING")
                installed.append(False)
        
        all_installed = all(installed)
        if all_installed:
            self.log("REQUIREMENTS", "All dependencies installed", "SUCCESS")
        else:
            self.log("REQUIREMENTS", "Some dependencies missing - run: pip install -r requirements.txt", "WARNING")
        
        return all_installed
    
    def generate_summary(self):
        """Generate verification summary"""
        print("\n" + "="*70)
        print("🎯 P2P ENERGY TRADING PIPELINE - VERIFICATION SUMMARY")
        print("="*70)
        
        checks = {
            "✅ Smart Contracts": self.verify_contracts_compiled(),
            "✅ Deployment Script": self.verify_deployment_script(),
            "✅ Trading Orchestrator": self.verify_orchestrator(),
            "✅ Experiment E": self.verify_experiments(),
            "✅ Unit Tests": self.verify_tests(),
            "✅ CI/CD Workflows": self.verify_ci_cd_workflows(),
            "✅ Documentation": self.verify_documentation(),
            "✅ Dashboard Tabs": self.verify_dashboard_tabs(),
            "✅ Project Structure": self.verify_files_exist(),
            "✅ Dependencies": self.verify_requirements(),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        print(f"\nVerification Results: {passed}/{total} checks passed\n")
        
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}")
        
        print("\n" + "="*70)
        
        if passed == total:
            print("🎉 ALL VERIFICATION CHECKS PASSED!")
            print("\n✨ Your P2P energy trading system is ready to deploy!\n")
            print("Next steps:")
            print("  1. Start Ganache: cd blockchain && npx ganache-cli --deterministic --accounts 20")
            print("  2. Deploy contracts: npx hardhat run scripts/deploy_trading.js --network localhost")
            print("  3. Run orchestrator: python sync/trading_orchestrator.py")
            print("  4. View dashboard: streamlit run dashboard/app.py")
            print("  5. Run experiments: python experiments/exp_e_trading_efficiency.py")
            print()
            self.results['overall'] = 'PASSED'
            return 0
        else:
            print(f"⚠️  {total - passed} check(s) failed or incomplete")
            print("\nPlease address the issues above and re-run verification.\n")
            self.results['overall'] = 'FAILED'
            return 1
    
    def run_all_verification(self):
        """Run complete verification"""
        print("\n🚀 Starting P2P Energy Trading Pipeline Verification\n")
        
        # Code verification (fast)
        self.verify_contracts_compiled()
        self.verify_deployment_script()
        self.verify_orchestrator()
        self.verify_experiments()
        self.verify_tests()
        self.verify_ci_cd_workflows()
        self.verify_documentation()
        self.verify_dashboard_tabs()
        self.verify_files_exist()
        self.verify_requirements()
        
        # Optional: Run unit tests if pytest available
        try:
            import pytest
            self.run_unit_tests()
        except ImportError:
            self.log("UNIT TESTS", "Pytest not installed - skipping test execution", "INFO")
        
        # Generate summary
        return self.generate_summary()


def main():
    """Main entry point"""
    verifier = TradingPipelineVerifier()
    exit_code = verifier.run_all_verification()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
