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
from services.bidding_service import store_bid, get_all_bids, get_winning_bid, clear_bids
from services.settlement_service import settle_auction, get_settlement_history
from services.hash_service import generate_hash, verify_hash_integrity
from blockchain.web3_client import store_settlement_on_chain

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
        
        st.subheader("🔐 MongoDB Data Integrity")
        
        bids = get_all_bids()
        if bids:
            st.write(f"**Current Bids in MongoDB:** {len(bids)}")
            
            # Generate hash of current bids
            current_hash = generate_hash(bids)
            st.write(f"**Hash of Bids:** `{current_hash[:32]}...`")
            
            # Verify integrity
            is_valid = verify_hash_integrity(bids, current_hash)
            if is_valid:
                st.success("✅ MongoDB Bids Data: Integrity Verified")
            else:
                st.error("❌ MongoDB Bids Data: Integrity Check Failed")
            
            # Show bids
            st.dataframe(pd.DataFrame(bids), use_container_width=True)
        else:
            st.info("ℹ️ No bids in MongoDB yet")
        
        st.divider()
        
        # Blockchain Hash Verification
        st.subheader("⛓️ Settlement Hash Verification")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔗 Verify Latest Settlement"):
                from blockchain.web3_client import get_batch_from_chain
                
                settlements = get_settlement_history(limit=1)
                if settlements:
                    settlement = settlements[0]
                    mongo_hash = settlement.get("data_hash")
                    auction_id = settlement.get("auction_id", 1)
                    settlement_bids = settlement.get("all_bids", [])
                    
                    st.info(f"📦 Settlement ID: {auction_id}")
                    st.write(f"**Bids in Settlement:** {len(settlement_bids)}")
                    st.write(f"**MongoDB Hash:** `{mongo_hash[:32]}...`")
                    
                    # ✅ VERIFY HASH USING STORED BIDS (not current bids)
                    if settlement_bids:
                        recomputed_hash = generate_hash(settlement_bids)
                        
                        if recomputed_hash == mongo_hash:
                            st.success("✅ Settlement Hash is Valid")
                        else:
                            st.error("❌ Settlement Hash Mismatch!")
                            st.write(f"Stored Hash:      {mongo_hash}")
                            st.write(f"Recomputed Hash:  {recomputed_hash}")
                    
                    # Try to retrieve from blockchain
                    blockchain_data = get_batch_from_chain(auction_id)
                    
                    if blockchain_data:
                        bc_hash = blockchain_data.get("hash")
                        if bc_hash:
                            st.write(f"\n**Blockchain Hash:** `{bc_hash[:32]}...`")
                            
                            if mongo_hash == bc_hash or mongo_hash.lower() == bc_hash.lower():
                                st.success("✅ BLOCKCHAIN MATCH - Data integrity confirmed across off-chain and on-chain!")
                            else:
                                st.error("❌ BLOCKCHAIN MISMATCH - Hash doesn't match on-chain storage!")
                                st.write(f"Full MongoDB Hash:     {mongo_hash}")
                                st.write(f"Full Blockchain Hash:  {bc_hash}")
                        else:
                            st.warning("⚠️ No hash data from blockchain")
                    else:
                        st.warning("⚠️ Settlement not found on blockchain yet. Store settlement first.")
                else:
                    st.info("ℹ️ No settlements in MongoDB yet. Run settlement first.")
        
        st.divider()
        
        # Original file-based integrity check
        if st.button("🔐 Run Tamper Detection (File-based)"):
            st.info("Running deterministic integrity check on historical files...")
            
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
                results = []
                for idx, row in hashes_df.iterrows():
                    hour = row['hour']
                    stored_hash = row['batch_hash']
                    batch_data = hourly_batches.get(hour, [])
                    passed = hasher.verify_hash(hour, batch_data, stored_hash)
                    status = "✓ VALID" if passed else "✗ TAMPERED"
                    if not passed:
                        all_valid = False
                    results.append({"Hour": hour, "Hash": stored_hash[:20] + "...", "Status": status})
                
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)

                if all_valid:
                    st.success("✓ All historical hashes verified! Data integrity confirmed.")
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

        col1, col2 = st.columns(2)
        
        with col1:
            col1, col2 = st.columns(2)

            with col1:
                amount = st.number_input("Enter energy (Wh)", min_value=0.0, step=1.0)

            with col2:
                price_input = st.number_input("Enter price ($/Wh)", min_value=0.0, step=0.00001)
        
        with col2:
            user_id = st.text_input("User ID (Optional)", value="consumer_1")

        if trading_log_file.exists() and logs:
            forecast = logs[-1].get("forecast_kwh", 1)
            # simple dynamic pricing
            price_per_wh = price_input if price_input > 0 else 0.000045
            if price_per_wh is None or price_per_wh == 0:
                price_per_wh = 0.000045
        else:
            price_per_wh = 0.000045
        
        cost = amount * price_per_wh
        st.write(f"**Estimated Cost:** ${cost:.6f}")
        st.write(f"**Price per Wh:** ${price_per_wh:.8f}")

        if st.button("Place Bid", type="primary"):
            if amount == 0:
                st.warning("⚠️ Please enter an amount greater than 0")
            else:
                bid_id = store_bid(user=user_id, energy=amount, price=price_per_wh)
                if bid_id:
                    st.success("✅ Bid stored successfully in MongoDB")
                    st.write(f"Bid ID: {bid_id}")
                else:
                    st.error("❌ Failed to store bid. Check MongoDB connection.")

        st.subheader("📜 All Bids (MongoDB)")
        
        bids = get_all_bids()
        if bids:
            bids_df = pd.DataFrame(bids)
            st.dataframe(bids_df, use_container_width=True)
            
            # Show winning bid
            winning = get_winning_bid()
            if winning:
                st.info(f"🏆 Current Highest Bid: **${winning['price_per_wh']:.8f}/Wh** by {winning['user']}")
        else:
            st.info("No bids placed yet.")

    # ========== TAB 7: Settlement Tracker ==========
    with tab7:
        st.header("📈 Settlement Tracker - Trade History")
        
        # Settlement functionality
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔨 Run Settlement", type="primary"):
                st.info("⏳ Running auction settlement...")
                settlement = settle_auction()
                if settlement:
                    st.success("✅ Settlement created!")
                    st.json({
                        "_id": settlement.get("_id"),
                        "auction_id": settlement.get("auction_id"),
                        "winner": settlement.get("winner", {}).get("user"),
                        "winner_price": settlement.get("winner", {}).get("price_per_wh"),
                        "total_bids": settlement.get("all_bids_count"),
                        "data_hash": settlement.get("data_hash")[:16] + "..."
                    })
                else:
                    st.error("❌ Settlement failed. Ensure bids exist in MongoDB.")
        
        with col2:
            if st.button("🔗 Store on Blockchain"):
                st.info("⏳ Attempting blockchain storage...")
                settlements = get_settlement_history(limit=1)
                if settlements:
                    settlement = settlements[0]
                    winner = settlement.get("winner", {})
                    tx_hash = store_settlement_on_chain(
                        auction_id=settlement.get("auction_id", 1),
                        winner=winner.get("user", "0x0"),
                        energy=winner.get("energy", 0),
                        price=winner.get("price_per_wh", 0),
                        data_hash=settlement.get("data_hash", "")
                    )
                    if tx_hash:
                        st.success(f"✅ Stored on blockchain!\nTX: {tx_hash}")
                    else:
                        st.warning("⚠️ Blockchain connection issue. Check Web3 configuration.")
                else:
                    st.warning("⚠️ No settlement found. Run settlement first.")
        
        with col3:
            if st.button("🗑️ Clear All Bids"):
                if clear_bids():
                    st.success("✅ Bids cleared")
                else:
                    st.error("❌ Failed to clear bids")
        
        # Recent settlements from MongoDB
        st.subheader("📋 Recent Settlements (MongoDB)")
        
        settlements = get_settlement_history(limit=10)
        if settlements:
            settlement_data = []
            for s in settlements:
                winner = s.get("winner", {})
                settlement_data.append({
                    "ID": s.get("_id", "")[:8] + "...",
                    "Auction": s.get("auction_id"),
                    "Winner": winner.get("user", "N/A"),
                    "Energy (Wh)": winner.get("energy", 0),
                    "Price ($/Wh)": f"${winner.get('price_per_wh', 0):.8f}",
                    "Total Bids": s.get("all_bids_count"),
                    "Status": s.get("status", "unknown"),
                    "TX Hash": s.get("tx_hash", "Pending")[:8] + "..." if s.get("tx_hash") else "Pending"
                })
            
            settlement_df = pd.DataFrame(settlement_data)
            st.dataframe(settlement_df, use_container_width=True, height=300)
            
            # Statistics
            st.subheader("📊 Settlement Analytics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Settlements", len(settlements))
            
            with col2:
                confirmed = len([s for s in settlements if s.get("status") == "confirmed_blockchain"])
                st.metric("Confirmed on Chain", confirmed)
            
            with col3:
                total_energy = sum([s.get("winner", {}).get("energy", 0) for s in settlements])
                st.metric("Total Energy (Wh)", f"{total_energy:,.0f}")
            
            with col4:
                avg_price = np.mean([s.get("winner", {}).get("price_per_wh", 0) for s in settlements]) if settlements else 0
                st.metric("Avg Price ($/Wh)", f"${avg_price:.8f}")
        else:
            st.info("ℹ️ No settlements yet. Place bids and run settlement.")
        
        # Data integrity verification
        st.subheader("🔐 Data Integrity Verification")
        
        if st.button("Verify Latest Settlement Hash"):
            settlements = get_settlement_history(limit=1)
            if settlements:
                settlement = settlements[0]
                stored_hash = settlement.get("data_hash")
                settlement_bids = settlement.get("all_bids", [])
                
                # ✅ FIXED: Use stored bids (not reconstructed data)
                if settlement_bids:
                    recomputed_hash = generate_hash(settlement_bids)
                    is_valid = verify_hash_integrity(settlement_bids, stored_hash)
                    
                    if is_valid:
                        st.success("✅ Hash verification PASSED - Data integrity confirmed!")
                        st.write(f"**Bids in Settlement:** {len(settlement_bids)}")
                        st.write(f"**Stored Hash:** `{stored_hash[:32]}...`")
                        st.write(f"**Computed Hash:** `{recomputed_hash[:32]}...`")
                    else:
                        st.error("❌ Hash verification FAILED - Possible data tampering!")
                        st.write(f"**Stored Hash:** {stored_hash}")
                        st.write(f"**Computed Hash:** {recomputed_hash}")
                else:
                    st.warning("⚠️ Settlement has no stored bids for verification")
            else:
                st.warning("⚠️ No settlement found to verify")
        
        # Old trading data visualization (if exists)
        settlement_file = Path("paper_results/exp_e_trading_efficiency.json")
        trading_log_file = Path("logs/trading_log.json")

        if trading_log_file.exists():
            try:
                import json
                with open(trading_log_file, 'r') as f:
                    logs = [json.loads(line) for line in f if line.strip()]
                
                if logs:
                    st.subheader("📈 Historical Trading Data (JSON Logs)")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Historical Auctions", len(logs))
                    with col2:
                        total_historical_energy = sum([log.get('tokens_minted', 0) for log in logs])
                        st.metric("Energy Traded (Wh)", f"{total_historical_energy:,.0f}")
                    with col3:
                        avg_forecast = np.mean([log.get('forecast_kwh', 0) for log in logs])
                        st.metric("Avg Forecast (kWh)", f"{avg_forecast:.2f}")
            except Exception as e:
                st.warning(f"⚠️ Could not load trading data: {str(e)}")


st.sidebar.success(f"Logged in as: {role}")
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))

st.markdown("---")
st.markdown("**WPP Digital Twin** | Research-Grade Prototype | Hybrid On-Chain + Off-Chain Architecture")