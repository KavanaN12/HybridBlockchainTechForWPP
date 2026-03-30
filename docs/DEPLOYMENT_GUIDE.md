## Deployment Plan

### Local Deployment
1. Clone the repository.
2. Set up the Python virtual environment:
   ```
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```
   uvicorn forecasting.models:app --host 0.0.0.0 --port 8000
   ```
4. Run the blockchain services:
   ```
   ./blockchain/start-ganache.sh
   ```

### Production Deployment
1. Use Docker for containerization:
   ```
   docker-compose up --build
   ```
2. Deploy to cloud platforms (e.g., AWS, Azure, Fly.io) using the provided deployment scripts.
3. Ensure MongoDB and blockchain nodes are configured for high availability.

### Notes
- Use `.env` files to manage environment-specific configurations.
- Refer to `CLOUD_DEPLOYMENT_GUIDE.md` for detailed cloud deployment steps.