import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Default Token Contract Addresses
TOKEN_CONTRACTS = {
    "UNIUSDT": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "AAVEUSDT": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "LDOUSDT": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
    "LINKUSDT": "0x514910771af9ca656af840dff83e8264ecf986ca",
}

# Massive Exchange Wallets (Binance etc.) - Token inflow means DUMP, outflow means PUMP
EXCHANGE_WALLETS = [
    "0x28C6c06298d514Db089934071355E5743bf21d60", # Binance 14
    "0xF977814e90dA44bFA03b6295A0616a897441aceC", # Binance 8
]

def check_whale_activity(symbol):
    """
    STRICTLY REAL TIME WHALE TRACKING.
    No simulated data. If the API key is missing or the token contract is not listed,
    it strictly returns 'NORMAL'.
    """
    if not ETHERSCAN_API_KEY:
        print("[ONCHAIN] Missing ETHERSCAN_API_KEY in .env. Skipping whale tracking.")
        return "NORMAL"
        
    contract = TOKEN_CONTRACTS.get(symbol)
    if not contract:
        print(f"[ONCHAIN] No predefined contract for {symbol}. Skipping whale tracking.")
        return "NORMAL"
        
    url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&contractaddress={contract}&page=1&offset=50&sort=desc&apikey={ETHERSCAN_API_KEY}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data["status"] == "1" and data["message"] == "OK":
            txs = data["result"]
            
            pump_score = 0
            dump_score = 0
            
            for tx in txs:
                value = int(tx["value"]) / (10 ** int(tx["tokenDecimal"]))
                # Count only massive transfers (e.g., > 100,000 tokens)
                if value > 100000:
                    _from = tx["from"].lower()
                    _to = tx["to"].lower()
                    
                    # If it went TO an exchange = DUMP
                    if _to in [w.lower() for w in EXCHANGE_WALLETS]:
                        dump_score += 1
                    # If it came FROM an exchange = PUMP
                    elif _from in [w.lower() for w in EXCHANGE_WALLETS]:
                        pump_score += 1
                        
            if dump_score > pump_score and dump_score >= 1:
                return "WHALE DUMP"
            elif pump_score > dump_score and pump_score >= 1:
                return "WHALE PUMP"
    except Exception as e:
        print(f"[ONCHAIN] Etherscan API Error: {e}")
        
    return "NORMAL"
