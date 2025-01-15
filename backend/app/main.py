from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
import logging
import os
import sys

# Add parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent))
from Fyers_login import get_historical_data

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


@app.get("/master-data/{exSymbol}")
async def get_master_data_exSymbol(exSymbol: str):
    try:
        csv_path = DATA_DIR / "master_file.csv"
        if not csv_path.exists():
            raise HTTPException(status_code=404, detail="Master file not found")
        df = pd.read_csv(csv_path)
        df = df[df['exSymbol'] == exSymbol]
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        logger.error(f"Error reading master data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_pe_symbol(ce_symbol: str) -> str:
    """Convert CE symbol to PE symbol"""
    if ce_symbol.endswith('CE'):
        return ce_symbol[:-2] + 'PE'
    return ce_symbol

def format_fyers_symbol(symbol: str) -> str:
    """Convert simple symbol to Fyers format"""
    if not symbol.startswith('NSE:'):
        return f"NSE:{symbol}"
    return symbol

@app.get("/historical-straddle/{symbol}")
async def get_historical_straddle(symbol: str, days_back: int = 10):
    try:
        # Format symbol to Fyers format
        formatted_symbol = format_fyers_symbol(symbol)
        logger.info(f"Converting {symbol} to {formatted_symbol}")
        
        # Get CE data
        ce_df = get_historical_data(formatted_symbol, days_back)
        
        # Get PE data
        pe_symbol = get_pe_symbol(formatted_symbol)
        pe_df = get_historical_data(pe_symbol, days_back)
        
        # Handle duplicate timestamps by taking the latest value
        ce_df = ce_df.sort_values('date').groupby('date', as_index=False).last()
        pe_df = pe_df.sort_values('date').groupby('date', as_index=False).last()
        
        # Merge CE and PE data on date
        combined_df = pd.merge(
            ce_df[['date', 'close']].rename(columns={'close': 'ce_price'}),
            pe_df[['date', 'close']].rename(columns={'close': 'pe_price'}),
            on='date',
            how='inner'
        )
        
        # Calculate straddle price
        combined_df['straddle_price'] = combined_df['ce_price'] + combined_df['pe_price']
        
        # Save to CSV using original symbol name
        output_path = DATA_DIR / f"straddle_{symbol}.csv"
        combined_df.to_csv(output_path, index=False)
        logger.info(f"Straddle data saved to {output_path}")
        
        return {
            "original_symbol": symbol,
            "formatted_symbol": formatted_symbol,
            "pe_symbol": pe_symbol,
            "data": combined_df.to_dict(orient="records")
        }
        
    except Exception as e:
        logger.error(f"Error calculating straddle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
