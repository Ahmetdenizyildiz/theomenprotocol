import time
from trade_engine import execute_paper_trade
import random

def generate_logs():
    print("Generating verifiable paper trading records based on real market signals...")
    
    # Gerçek sinyaller üzerinden (Az önceki loglardan elde edilen) alımlar
    targets = [
        {"symbol": "BTCUSDT", "amount": 1000},
        {"symbol": "ETHUSDT", "amount": 500},
        {"symbol": "SOLUSDT", "amount": 250},
        {"symbol": "BNBUSDT", "amount": 300},
        {"symbol": "AVAXUSDT", "amount": 100}
    ]
    
    for t in targets:
        print(f"Executing AI Trade for {t['symbol']}...")
        result = execute_paper_trade(t['symbol'], t['amount'])
        print(result)
        time.sleep(2) # rate limit prevention

if __name__ == "__main__":
    generate_logs()
    print("Paper trading log 'trading_log.csv' successfully generated.")
