from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create data directory if it doesn't exist
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Trading Data API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Trading Data API is running"}

@app.get("/access-token")
async def get_access_token():
    try:
        token_path = DATA_DIR / "access_token.txt"
        if not token_path.exists():
            raise HTTPException(status_code=404, detail="Access token file not found")
        
        with open(token_path, "r") as f:
            token = f.read().strip()
        return {"access_token": token}
    except Exception as e:
        logger.error(f"Error reading access token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/master-data")
async def get_master_data():
    try:
        csv_path = DATA_DIR / "master_file.csv"
        if not csv_path.exists():
            raise HTTPException(status_code=404, detail="Master file not found")
        
        df = pd.read_csv(csv_path)
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        logger.error(f"Error reading master data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
