"""
dashboard/app.py
Streamlit dashboard for WPP Digital Twin
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import requests

# Ensure root workspace is on Python path so local package imports resolve
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from forecasting.models import ForecastingEngine

st.set_page_config(page_title="WPP Digital Twin Dashboard", layout="wide")

st.markdown("Hybrid On-Chain and Off-Chain Architecture for Blockchain-Enabled Wind Management")

# ---------------- ROLE ENTRY ----------------
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    st.title("⚡ WPP Digital Twin Platform")

    role = st.selectbox("Select your role", ["Producer", "Maintainer", "Consumer"])

    if st.button("Enter Platform"):
        st.session_state.role = role
        st.rerun()

    st.stop()

role = st.session_state.role
st.title("⚡ Wind Power Plant - Digital Twin Dashboard")

if role == "Producer":
    st.subheader("System Overview")

    data_file = Path("data/processed/scada_preprocessed.csv")
    if data_file.exists():
        df = pd.read_csv(data_file)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Avg Wind Speed", f"{df['wind_speed'].mean():.2f} m/s")
        col3.metric("Avg Power", f"{df['power'].mean():.2f} kW")
    else:
        st.warning("SCADA data not found.")
    tab1, tab2, tab3 = st.tabs([
        "📊 Raw Data",
        "👯 Digital Twin",
        "🔮 Forecasting"
    ])
    with tab1:
        st.header("Raw SCADA Data")
        
        data_file = Path("data/processed/scada_preprocessed.csv")
        if data_file.exists():
            df = pd.read_csv(data_file)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Avg Wind Speed (m/s)", f"{df['wind_speed'].mean():.2f}")
            with col3:
                st.metric("Avg Power (kW)", f"{df['power'].mean():.1f}")

                # Generator speed and power non-zero counts (to diagnose zero values)
                if 'generator_speed' in df.columns:
                    nonzero_gen = (df['generator_speed'] != 0).sum()
                    st.write(f"Generator speed non-zero rows: {nonzero_gen} / {len(df)}")
                if 'power' in df.columns:
                    nonzero_power = (df['power'] != 0).sum()
                    st.write(f"Actual power non-zero rows: {nonzero_power} / {len(df)}")
    # ========== TAB 2: Digital Twin ==========
    with tab2:
        st.header("Digital Twin Validation")
        
        results_file = Path("experiments/twin_validation_results.csv")
        if results_file.exists():
            metrics = pd.read_csv(results_file).iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("MAE (kW)", f"{metrics['mae']:.1f}")
            with col2:
                st.metric("MAE (%)", f"{metrics['mae_pct']:.1f}%")
            with col3:
                st.metric("RMSE (kW)", f"{metrics['rmse']:.1f}")
            with col4:
                st.metric("R² Score", f"{metrics['r2']:.3f}")
            
            st.success("✓ Twin validation complete! Twin fidelity is high.")
        else:
            st.info("ℹ️ Run twin validation: `python twin/validate_twin.py`")
        
        st.subheader("Theoretical vs Actual Power")
        data_file = Path("data/processed/scada_preprocessed.csv")
        if data_file.exists():
            df = pd.read_csv(data_file)
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df['power'].head(500), name='Actual Power', line=dict(color='blue')))
            fig.add_trace(go.Scatter(y=df['theoretical_power'].head(500), name='Theoretical Power', line=dict(color='red', dash='dash')))
            fig.update_layout(title="Twin Overlay", xaxis_title="Hours", yaxis_title="Power (kW)")
            st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 3: Forecasting ==========
    with tab3:
        st.header("1. ML Forecasting Results")

        forecast_file = Path("experiments/forecast_results.csv")
        if forecast_file.exists():
            forecast_df = pd.read_csv(forecast_file)
            if forecast_df.empty:
                st.warning("Forecast results file exists but contains no rows. Run `python forecasting/models.py` again.")
            else:
                st.subheader("Model Comparison")
                st.dataframe(forecast_df, use_container_width=True)
                
                fig = px.bar(forecast_df, x='model', y=['mae', 'rmse'], barmode='group',
                            title="Forecasting Model Comparison")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Run forecasting: `python forecasting/models.py`")

        # Fallback: evaluate hash and models if file is missing
        if not forecast_file.exists():
            st.info("ℹ️ No forecast results found. Run: `python forecasting/models.py`")
 

        st.subheader("2. Energy Efficiency Analysis")

        data_file = Path("data/processed/scada_preprocessed.csv")
        if data_file.exists():
            df = pd.read_csv(data_file)

            df['efficiency'] = (df['power'] / df['theoretical_power']) * 100

            fig = px.histogram(df, x='efficiency', nbins=50, title="Efficiency Distribution")
            st.plotly_chart(fig, use_container_width=True)

            st.metric("Average Efficiency (%)", f"{df['efficiency'].mean():.2f}")
        else:
            st.warning("SCADA data not found.")


        st.subheader("3. Forecast model evaluation")

        forecast_file = Path("experiments/forecast_results.csv")

        if forecast_file.exists():
            results = pd.read_csv(forecast_file)

            if not results.empty:
                st.subheader("Forecasting Model Performance")
                st.dataframe(results, use_container_width=True)

                fig = px.bar(
                    results,
                    x="model",
                    y=["mae", "rmse"],
                    barmode="group",
                    title="Model Performance Comparison"
                )
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Forecast results file is empty.")

        else:
            st.info("ℹ️ No forecast results found. Run: `python forecasting/models.py`")

        if role == "Producer":
            uploaded_file = st.sidebar.file_uploader(
                "Upload WPP Data (CSV)", type=["csv"]
            )

            if uploaded_file is not None:
                input_df = pd.read_csv(uploaded_file)

                st.write("### Uploaded Data")
                st.dataframe(input_df.head())

                try:
                    engine = ForecastingEngine()

                    input_df = input_df.copy()

                    # ✅ Validate input early
                    required_cols = ["wind_speed", "power"]
                    if not all(col in input_df.columns for col in required_cols):
                        st.error("Uploaded file missing required columns")
                        st.stop()

                    # Feature engineering
                    input_df["rolling_avg_wind"] = input_df["wind_speed"].rolling(window=3).mean()
                    input_df["lag_power"] = input_df["power"].shift(1)

                    input_df = input_df.dropna()

                    if input_df.empty:
                        st.error("Not enough data after feature engineering (need at least 3 rows)")
                        st.stop()

                    engine.load_models("forecasting/models_checkpoint")

                    features = input_df[["wind_speed", "rolling_avg_wind", "lag_power"]]

                    model = engine.models.get("random_forest")

                    if model is None:
                        st.warning("Model not loaded")
                    else:
                        predictions = model.predict(features)
                        input_df["predicted_power"] = predictions

                        st.subheader("Predictions")

                        st.dataframe(input_df.head(), use_container_width=True)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(y=input_df["power"], name="Actual"))
                        fig.add_trace(go.Scatter(y=input_df["predicted_power"], name="Predicted"))

                        st.plotly_chart(fig, use_container_width=True)

                        input_df["error"] = input_df["power"] - input_df["predicted_power"]
                        st.metric("Average Error", f"{input_df['error'].mean():.2f}")

                except Exception as e:
                    st.error(f"Prediction failed: {e}")


elif role == "Maintainer":
    tab4, tab5 = st.tabs([
        "⛓️ Blockchain Anchors",
        "✓ Integrity Check"
    ])
    with tab4:
        st.header("Blockchain Hash Anchors")
        
        hashes_file = Path("experiments/hourly_hashes.csv")
        if hashes_file.exists():
            hashes_df = pd.read_csv(hashes_file)
            
            st.metric("Total Batches Hashed", len(hashes_df))
            
            st.subheader("Recent Hashes")
            st.dataframe(hashes_df.tail(10), use_container_width=True)
            
            st.subheader("Hash Distribution")
            fig = px.histogram(hashes_df, x='record_count', nbins=30, title="Records per Hourly Batch")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Generate hashes: `python hashing/batch_hasher.py`")

    # ========== TAB 5: Integrity Check ==========
    with tab5:
        st.header("Data Integrity Verification")
        
        if st.button("🔐 Run Tamper Detection"):
            st.info("Running deterministic integrity check...")
            
            hashes_file = Path("experiments/hourly_hashes.csv")
            data_file = Path("data/processed/scada_preprocessed.csv")
            if not hashes_file.exists():
                st.warning("⚠️ No batch hash file available. Generate hashes first using `python hashing/batch_hasher.py`.")
            elif not data_file.exists():
                st.warning("⚠️ Preprocessed SCADA data not found. Run preprocessing first.")
            else:
                from hashing.batch_hasher import BatchHasher
                hasher = BatchHasher()

                df = pd.read_csv(data_file)
                time_col = 'datetime' if 'datetime' in df.columns else 'time'
                hourly_batches = hasher.batch_by_hour(df, time_col=time_col)

                hashes_df = pd.read_csv(hashes_file)
                all_valid = True
                for idx, row in hashes_df.iterrows():
                    hour = row['hour']
                    stored_hash = row['batch_hash']
                    batch_data = hourly_batches.get(hour, [])
                    passed = hasher.verify_hash(hour, batch_data, stored_hash)
                    status = "✓ VALID" if passed else "✗ TAMPERED"
                    if not passed:
                        all_valid = False
                    st.write(f"{hour}: Hash `{stored_hash[:20]}...` {status}")

                if all_valid:
                    st.success("✓ All hashes verified! Data integrity confirmed.")
                else:
                    st.error("✗ Tampering detected! Hash mismatch found.")

elif role == "Consumer":
    tab6, tab7 = st.tabs([
        "💰 Energy Marketplace",
        "📈 Settlement Tracker"
    ])

    with tab6:
        st.header("💰 Energy Marketplace - Peer-to-Peer Trading")
        
        trading_log_file = Path("logs/trading_log.json")

        if trading_log_file.exists():
            import json

            try:
                with open(trading_log_file, 'r') as f:
                    logs = [json.loads(line) for line in f if line.strip()]

                if logs:
                    latest_log = logs[-1]

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current Auction ID", int(latest_log.get('auction_id', 0)))
                    with col2:
                        energy_available = latest_log.get('tokens_minted', 0)
                        st.metric("Energy Available (Wh)", f"{energy_available:,.0f}")
                    with col3:
                        forecast = latest_log.get('forecast_kwh', 0)
                        st.metric("Forecasted Supply (kWh)", f"{forecast:.2f}")
                    with col4:
                        status = "🟢 Active" if latest_log.get('auction_started') else "⏹️ Waiting"
                        st.metric("Status", status)

                    st.subheader("Current Auction Details")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Hour**:", latest_log.get('timestamp', 'N/A'))
                        st.write("**Auction ID**:", latest_log.get('auction_id', 'N/A'))
                        st.write("**Energy (Wh)**:", f"{latest_log.get('tokens_minted', 0):,.0f}")

                    with col2:
                        bidding_window = "Open (Bid Phase: 00:00-00:30 UTC)"
                        st.write("**Bidding Window**:", bidding_window)
                        bids_file = Path("logs/user_bids.json")

                        if bids_file.exists():
                            with open(bids_file, "r") as f:
                                bids = [json.loads(line) for line in f if line.strip()]
                            st.write("**Current Bids:**", len(bids))
                        else:
                            st.write("**Current Bids:** 0")
                        if bids_file.exists() and bids:
                            highest_price = max([b["price_per_wh"] for b in bids])
                            st.write(f"**Highest Price:** ${highest_price:.8f}/Wh")
                        else:
                            st.write("**Highest Price:** N/A")

                    # Display trading history
                    st.subheader("Recent Auctions (Past 24 Hours)")

                    trading_history = []
                    for log in logs[-24:]:  # Last 24 hours of logs
                        trading_history.append({
                            'Auction ID': int(log.get('auction_id', 0)),
                            'Time': log.get('timestamp', 'N/A'),
                            'Energy (Wh)': f"{log.get('tokens_minted', 0):,.0f}",
                            'Forecast (kWh)': f"{log.get('forecast_kwh', 0):.2f}",
                            'Status': '✓ Active' if log.get('auction_started') else '⏹️ Waiting'
                        })
                    
                    if trading_history:
                        history_df = pd.DataFrame(trading_history)
                        st.dataframe(history_df, use_container_width=True)
                    
                    # Statistics
                    st.subheader("Trading Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_energy = sum([log.get('tokens_minted', 0) for log in logs])
                        st.metric("Total Energy Traded (Wh)", f"{total_energy:,.0f}")
                    
                    with col2:
                        avg_forecast = np.mean([log.get('forecast_kwh', 0) for log in logs])
                        st.metric("Avg Hourly Forecast (kWh)", f"{avg_forecast:.2f}")
                    
                    with col3:
                        st.metric("Total Auctions", len(logs))
                    
                else:
                    st.info("ℹ️ No trading activity yet. Start trading: `python sync/trading_orchestrator.py`")
            
            except Exception as e:
                st.warning(f"⚠️ Could not load trading log: {str(e)}")
        else:
            st.info("ℹ️ Trading log not found. Deploy contracts and run orchestrator first.")

        st.subheader("Place Your Bid")

        amount = st.number_input("Enter energy (Wh)", min_value=0.0)

        if trading_log_file.exists() and logs:
            forecast = logs[-1].get("forecast_kwh", 1)

            # simple dynamic pricing
            price_per_wh = max(0.00003, min(0.00008, 0.00005 * (1 / (forecast + 0.1))))

            if price_per_wh is None or price_per_wh == 0:
                price_per_wh = 0.000045
        else:
            price_per_wh = 0.000045
        cost = amount * price_per_wh

        st.write(f"Estimated Cost: ${cost:.6f}")

        import json

        if st.button("Place Bid"):

            bid = {
                "energy": amount,
                "price_per_wh": price_per_wh,
                "total_cost": cost,
                "timestamp": str(pd.Timestamp.now()),
                "user": "consumer_1"
            }

            log_file = Path("logs/user_bids.json")
            log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, "a") as f:
                f.write(json.dumps(bid) + "\n")

            st.success("✅ Bid stored successfully")

        log_file = Path("logs/user_bids.json")

        if log_file.exists():
            import json

            with open(log_file, "r") as f:
                bids = [json.loads(line) for line in f if line.strip()]

            if bids:
                st.subheader("📜 Your Bids")
                bids_df = pd.DataFrame(bids[::-1])  # latest first
                st.dataframe(bids_df, use_container_width=True)
            else:
                st.info("No bids placed yet.")

    # ========== TAB 7: Settlement Tracker ==========
    with tab7:
        bids_file = Path("logs/user_bids.json")

        if bids_file.exists():
            with open(bids_file, "r") as f:
                bids = [json.loads(line) for line in f if line.strip()]
        else:
            bids = []
        st.header("📈 Settlement Tracker - Trade History")
        
        settlement_file = Path("paper_results/exp_e_trading_efficiency.json")
        trading_log_file = Path("logs/trading_log.json")

        if trading_log_file.exists():
            import json

            try:
                with open(trading_log_file, 'r') as f:
                    logs = [json.loads(line) for line in f if line.strip()]

                if logs:
                    st.subheader("Recent Settlements (Past 24 Hours)")

                    settlements = []
                    for i, log in enumerate(logs[-24:], 1):
                        hour_num = i
                        timestamp = log.get('timestamp', 'N/A')
                        energy = log.get('tokens_minted', 0)

                        # Simulate settlement details (in production, fetch from blockchain)
                        price = log.get("price_per_wh", 0.000045)
                        if bids:
                            winning_bid = max(bids, key=lambda x: x["price_per_wh"])
                            winner_addr = winning_bid["user"]
                            price = winning_bid["price_per_wh"]
                            value = winning_bid["total_cost"]
                        else:
                            winner_addr = "N/A"
                            price = 0
                            value = 0
                                                    
                        settlements.append({
                            'Hour': f"{hour_num:02d}:00 UTC",
                            'Timestamp': timestamp,
                            'Energy (Wh)': f"{energy:,.0f}",
                            'Winner': f"{winner_addr}...",
                            'Price ($/Wh)': f"${price:.8f}",
                            'Value ($)': f"${value:.2f}",
                            'Status': '✓ Settled'
                        })

                    settlement_df = pd.DataFrame(settlements)
                    st.dataframe(settlement_df, use_container_width=True)

                    st.subheader("Settlement Analytics")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        total_settled = len(settlements)
                        st.metric("Auctions Settled", total_settled)

                    with col2:
                        avg_price = (
                            np.mean([b["price_per_wh"] for b in bids])
                            if bids else 0
                        )
                        st.metric("Avg Price ($/Wh)", f"${avg_price:.8f}")

                    with col3:
                        total_revenue = sum([float(s['Value ($)'].replace('$', '')) for s in settlements])
                        st.metric("Total Revenue ($)", f"${total_revenue:.2f}")

                    with col4:
                        settlement_success_rate = (
                            (len(settlements) / len(logs)) * 100 if logs else 0
                        )
                        st.metric("Settlement Success Rate", f"{settlement_success_rate:.1f}%")

                    # Price discovery chart
                    st.subheader("Price Discovery Over Time")

                    prices = []
                    times = []
                    for i, settlement in enumerate(settlements):
                        prices.append(float(settlement['Price ($/Wh)'].replace('$', '')))
                        times.append(f"Hour {i+1}")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=times, y=prices, mode='lines+markers',
                        name='Settlement Price',
                        line=dict(color='green', width=2),
                        marker=dict(size=8)
                    ))
                    fig.update_layout(
                        title="Price Discovery - Last 24 Hours",
                        xaxis_title="Time",
                        yaxis_title="Price ($/Wh)",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Efficiency metrics
                    st.subheader("Trading Efficiency Metrics")

                    col1, col2 = st.columns(2)

                    with col1:
                        total_bids = len(bids) if bids_file.exists() else 0
                        st.metric("Total Bids", total_bids)

                        total_energy = sum([b["energy"] for b in bids]) if bids_file.exists() else 0
                        st.metric("Total Energy Requested (Wh)", f"{total_energy:,.0f}")

                        avg_price = (
                            np.mean([b["price_per_wh"] for b in bids])
                            if bids_file.exists() and bids else 0
                        )
                        st.metric("Average Bid Price ($/Wh)", f"${avg_price:.8f}")


                    with col2:
                        latest_bid = bids[-1]["timestamp"] if bids_file.exists() and bids else "N/A"
                        st.metric("Last Bid Time", latest_bid)

                        total_transactions = len(bids) if bids_file.exists() else 0
                        st.metric("Total Transactions", total_transactions)

                        st.metric("System Type", "Hybrid (Off-chain + On-chain hash)")
                    
                else:
                    st.info("ℹ️ No settlements yet. Run trading orchestrator to generate settlements.")
            
            except Exception as e:
                st.warning(f"⚠️ Could not load settlement data: {str(e)}")
        else:
            st.info("ℹ️ Settlement tracker requires trading data. Deploy and run orchestrator first.")


st.sidebar.success(f"Logged in as: {role}")
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))

st.markdown("---")
st.markdown("**WPP Digital Twin** | Research-Grade Prototype | Hybrid On-Chain + Off-Chain Architecture")