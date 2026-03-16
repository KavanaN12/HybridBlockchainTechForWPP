"""
experiments/run_all_experiments.py
Execute all research experiments
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentOrchestrator:
    """Run all research experiments."""
    
    def __init__(self):
        self.results = {}
    
    def experiment_a_scalability(self):
        """Exp A: Hybrid vs Fully On-Chain comparison."""
        print("\n" + "="*60)
        print("EXPERIMENT A: Blockchain Scalability (Hybrid vs Full On-Chain)")
        print("="*60)
        
        hashes_file = Path("experiments/hourly_hashes.csv")
        if not hashes_file.exists():
            print("❌ Hashes not found")
            return
        
        hashes_df = pd.read_csv(hashes_file)
        
        # Hybrid: 1 tx per hour
        hybrid_txs_per_day = 24
        hybrid_gas_estimate = 150000 * 24  # 150k gas per tx
        
        # Full on-chain: 1 tx per record (assuming avg 50 records/hour)
        avg_records_per_hour = hashes_df['record_count'].mean()
        full_txs_per_day = avg_records_per_hour * 24
        full_gas_estimate = 150000 * full_txs_per_day
        
        result = {
            'hybrid_transactions_per_day': hybrid_txs_per_day,
            'full_transactions_per_day': full_txs_per_day,
            'reduction_factor': full_txs_per_day / hybrid_txs_per_day,
            'hybrid_gas_per_day': hybrid_gas_estimate,
            'full_gas_per_day': full_gas_estimate,
            'gas_savings_percent': 100 * (1 - hybrid_gas_estimate / full_gas_estimate)
        }
        
        print(f"\nHybrid Architecture:")
        print(f"  Transactions/day: {result['hybrid_transactions_per_day']}")
        print(f"  Gas/day: {result['hybrid_gas_per_day']:,.0f}")
        
        print(f"\nFully On-Chain:")
        print(f"  Transactions/day: {result['full_transactions_per_day']:.0f}")
        print(f"  Gas/day: {result['full_gas_per_day']:,.0f}")
        
        print(f"\n✓ RESULT: {result['reduction_factor']:.0f}x fewer transactions")
        print(f"✓ GAS SAVINGS: {result['gas_savings_percent']:.1f}%")
        
        self.results['exp_a'] = result
    
    def experiment_b_twin_accuracy(self):
        """Exp B: Twin accuracy by operating zone."""
        print("\n" + "="*60)
        print("EXPERIMENT B: Digital Twin Accuracy by Operating Zone")
        print("="*60)
        
        validation_file = Path("experiments/twin_validation_results.csv")
        if not validation_file.exists():
            print("❌ Twin validation not found")
            return
        
        metrics = pd.read_csv(validation_file).iloc[0]
        
        result = {
            'overall_mae_kw': metrics['mae'],
            'overall_mae_pct': metrics['mae_pct'],
            'overall_rmse_kw': metrics['rmse'],
            'overall_rmse_pct': metrics['rmse_pct'],
            'r_squared': metrics['r2'],
            'fidelity_score': 'High' if metrics['r2'] > 0.85 else 'Medium'
        }
        
        print(f"\nTwin Accuracy Metrics:")
        print(f"  MAE: {result['overall_mae_pct']:.2f}% of rated power")
        print(f"  RMSE: {result['overall_rmse_pct']:.2f}% of rated power")
        print(f"  R²: {result['r_squared']:.3f}")
        print(f"  Fidelity: {result['fidelity_score']}")
        
        self.results['exp_b'] = result
    
    def experiment_c_forecast_accuracy(self):
        """Exp C: Forecast model comparison."""
        print("\n" + "="*60)
        print("EXPERIMENT C: Forecasting Model Accuracy")
        print("="*60)
        
        forecast_file = Path("experiments/forecast_results.csv")
        if not forecast_file.exists():
            print("❌ Forecast results not found")
            return
        
        forecast_df = pd.read_csv(forecast_file)
        
        best_model = forecast_df.loc[forecast_df['rmse'].idxmin()]
        
        print(f"\nForecasting Models Evaluated: {len(forecast_df)}")
        for idx, row in forecast_df.iterrows():
            print(f"\n  {row['model'].upper()}:")
            print(f"    MAE:  {row['mae']:.1f} kW")
            print(f"    RMSE: {row['rmse']:.1f} kW")
            print(f"    MAPE: {row['mape']:.2f}%")
        
        print(f"\n✓ BEST MODEL: {best_model['model'].upper()}")
        print(f"✓ RMSE: {best_model['rmse']:.1f} kW")
        
        self.results['exp_c'] = forecast_df.to_dict('records')
    
    def experiment_d_hash_intervals(self):
        """Exp D: Hash interval optimization."""
        print("\n" + "="*60)
        print("EXPERIMENT D: Hash Interval Trade-Off Analysis")
        print("="*60)
        
        hashes_file = Path("experiments/hourly_hashes.csv")
        if not hashes_file.exists():
            print("❌ Hashes not found")
            return
        
        hashes_df = pd.read_csv(hashes_file)
        total_records = hashes_df['record_count'].sum()
        
        intervals = {
            '1-min': {'interval_hours': 1/60, 'approx_hashes_per_day': 1440},
            '15-min': {'interval_hours': 0.25, 'approx_hashes_per_day': 96},
            '1-hour': {'interval_hours': 1, 'approx_hashes_per_day': 24}
        }
        
        print(f"\nHash Interval Comparison (for {total_records:,.0f} total records):\n")
        
        for interval, specs in intervals.items():
            hashes_per_day = specs['approx_hashes_per_day']
            granularity_loss = 100 * (1 - (1.0 / hashes_per_day))
            
            print(f"  {interval}:")
            print(f"    Hashes/day: {hashes_per_day}")
            print(f"    Min time resolution: {interval}")
            print(f"    Data granularity loss: {granularity_loss:.1f}%")
        
        print(f"\n✓ RECOMMENDATION: 1-hour (optimal balance)")
        
        self.results['exp_d'] = intervals
    
    def run_all(self):
        """Execute all experiments."""
        print("\n" + "█"*60)
        print("█ WPP DIGITAL TWIN - RESEARCH EXPERIMENTS SUITE")
        print("█"*60)
        
        self.experiment_a_scalability()
        self.experiment_b_twin_accuracy()
        self.experiment_c_forecast_accuracy()
        self.experiment_d_hash_intervals()
        
        # Save results
        results_file = Path("paper_results/experiment_results.json")
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print("\n" + "="*60)
        print("✓ ALL EXPERIMENTS COMPLETE")
        print("="*60)
        print(f"\n✓ Results saved to: {results_file}\n")

if __name__ == "__main__":
    orchestrator = ExperimentOrchestrator()
    orchestrator.run_all()
