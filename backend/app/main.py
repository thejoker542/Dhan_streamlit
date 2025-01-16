from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
import logging
import os
import sys
import redis
from fastapi_socketio import SocketManager
import json
import time

# Add parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent))
from Fyers_login import get_access_token
from fyers_ws import FyersWebsocketClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create data directory if it doesn't exist
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

app = FastAPI(title="Trading Data API")
socket_manager = SocketManager(app=app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global WebSocket client instance
ws_client = None

def broadcast_market_update(data):
    """Broadcast market data to all connected clients"""
    try:
        if not data or not isinstance(data, dict):
            logger.error({"error": "Invalid market data format", "data": str(data)[:200]})
            return
            
        symbol = str(data.get('symbol', ''))
        if not symbol:
            logger.error({"error": "No symbol in market data", "data": str(data)[:200]})
            return
            
        try:
            # Store in Redis using standard key pattern
            redis_key = f"market_update:{symbol}"
            redis_client.set(redis_key, json.dumps(data))
            redis_client.expire(redis_key, 86400)  # 24 hour TTL
            
            logger.info({
                "message": "Market data stored in Redis",
                "symbol": symbol,
                "key": redis_key,
                "ltp": data.get('ltp')
            })
            
            # Broadcast to all clients
            socket_manager.emit('market_update', data)
            
            logger.info({
                "message": "Market data broadcasted to clients",
                "symbol": symbol,
                "event": "market_update",
                "ltp": data.get('ltp')
            })
            
        except Exception as e:
            logger.error({
                "error": f"Error storing/broadcasting market data: {str(e)}",
                "symbol": symbol,
                "data": str(data)[:200],
                "traceback": str(e.__traceback__)
            })
            
    except Exception as e:
        logger.error({
            "error": f"Error processing market data: {str(e)}", 
            "data": str(data)[:200],
            "traceback": str(e.__traceback__)
        })
        socket_manager.emit('error', {'message': f"Market data error: {str(e)}"})

def initialize_websockets():
    """Initialize websocket connections"""
    try:
        # Get fresh token
        access_token = get_access_token()
        if not access_token:
            raise ValueError("No access token available")
            
        # Initialize websocket client
        global ws_client
        ws_client = FyersWebsocketClient(
            access_token=access_token,
            redis_client=redis_client,
            socketio=socket_manager
        )
        
        # Set callbacks
        ws_client.set_callbacks(
            market_update_cb=broadcast_market_update
        )
        
        # Try to connect multiple times
        for attempt in range(3):
            logger.info({"message": f"Attempting websocket connection - attempt {attempt + 1}/3"})
            
            if ws_client.connect():
                logger.info({"message": "Websocket connection established and subscribed"})
                return ws_client
                    
            time.sleep(2)  # Wait before retry
            
        raise Exception("Failed to establish stable websocket connection after 3 attempts")
            
    except Exception as e:
        logger.error({"error": f"Websocket initialization failed: {str(e)}"})
        return None

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

@app.post("/subscribe")
async def subscribe_symbols(symbols: list[str]):
    """Subscribe to market data for specified symbols"""
    try:
        if not ws_client or not ws_client.is_connected:
            # Try to initialize WebSocket if not connected
            if not initialize_websockets():
                raise HTTPException(status_code=500, detail="WebSocket connection failed")
        
        # Format symbols if needed (add NSE: prefix if not present)
        formatted_symbols = [
            f"NSE:{symbol}" if not symbol.startswith("NSE:") else symbol 
            for symbol in symbols
        ]
        
        # Subscribe to symbols
        ws_client.subscribe(formatted_symbols)
        
        return {
            "message": "Successfully subscribed to symbols",
            "symbols": formatted_symbols
        }
        
    except Exception as e:
        logger.error({"error": f"Symbol subscription failed: {str(e)}"})
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unsubscribe")
async def unsubscribe_symbols(symbols: list[str]):
    """Unsubscribe from market data for specified symbols"""
    try:
        if not ws_client or not ws_client.is_connected:
            raise HTTPException(status_code=400, detail="WebSocket not connected")
        
        # Format symbols if needed
        formatted_symbols = [
            f"NSE:{symbol}" if not symbol.startswith("NSE:") else symbol 
            for symbol in symbols
        ]
        
        # Unsubscribe from symbols
        ws_client.unsubscribe(formatted_symbols)
        
        return {
            "message": "Successfully unsubscribed from symbols",
            "symbols": formatted_symbols
        }
        
    except Exception as e:
        logger.error({"error": f"Symbol unsubscription failed: {str(e)}"})
        raise HTTPException(status_code=500, detail=str(e))

# Initialize WebSocket connection on startup
@app.on_event("startup")
async def startup_event():
    initialize_websockets()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
