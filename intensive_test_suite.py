import time
import json
import threading
from signal_provider import TARGET_SYMBOLS, calculate_rsi
from market_monitor import check_market_anomalies
from trade_engine import execute_paper_trade
from http_utils import get_session

def run_intensive_test(duration_minutes=15):
    print(f"[{time.strftime('%X')}] 🚀 STARTING {duration_minutes}-MINUTE INTENSIVE REAL-MARKET TEST...")
    end_time = time.time() + (duration_minutes * 60)
    session = get_session()
    
    with open("targets.json", "r") as f:
        anomaly_targets = json.load(f)
        
    iteration = 1
    while time.time() < end_time:
        print(f"\n--- [ITERATION {iteration}] | Time Remaining: {int(end_time - time.time())}s ---")
        
        # 1. Binance Technical RSI Checks
        print("📊 Scanning Binance Live Klines for Oversold (RSI < 25) Signals...")
        for symbol in TARGET_SYMBOLS:
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=20"
                response = session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    close_prices = [float(candle[4]) for candle in data]
                    if close_prices:
                        current_price = close_prices[-1]
                        rsi = calculate_rsi(close_prices)
                        print(f"   [{symbol}] 15m RSI: {rsi:.2f} | Price: {current_price}")
                        
                        # Real AI threshold
                        if rsi < 25:
                            print(f"   🚨 VALID SIGNAL DETECTED for {symbol} (RSI {rsi:.2f} < 25)!")
                            print("   🤖 Auto-executing PAPER TRADE based on Algorithmic Signal...")
                            res = execute_paper_trade(symbol, usdt_amount=150.0)
                            print(f"   ✅ {res}")
            except Exception as e:
                print(f"   ❌ Error fetching {symbol}: {e}")
                
        # 2. DefiLlama & Binance Volume Anomaly Checks
        print("\n🐋 Scanning On-Chain TVL & Volume Anomalies...")
        try:
            anomalies = check_market_anomalies(anomaly_targets)
            if anomalies:
                for anomaly in anomalies:
                    atype = anomaly.get("type")
                    trade_symbol = anomaly.get("target", {}).get("trade_symbol", "UNKNOWN")
                    if atype == "BANK_RUN":
                        print(f"   🚨 TVL BANK RUN DETECTED on {trade_symbol}! Drop: {anomaly.get('drop_pct')}%")
                        print("   🤖 Executing Defensive SHORT (Paper Trade)...")
                        res = execute_paper_trade(trade_symbol, usdt_amount=100.0)
                        print(f"   ✅ {res}")
                    elif atype == "SMART_MONEY":
                        print(f"   🐋 SMART MONEY SPIKE on {trade_symbol}! Spike: {anomaly.get('spike_pct')}%")
                        print("   🤖 Executing Momentum BUY (Paper Trade)...")
                        res = execute_paper_trade(trade_symbol, usdt_amount=200.0)
                        print(f"   ✅ {res}")
            else:
                print("   ✅ No critical anomalies detected.")
        except Exception as e:
            print(f"   ❌ Error checking anomalies: {e}")
            
        print(f"💤 Sleeping 30 seconds before next scan...")
        iteration += 1
        time.sleep(30)
        
    print(f"\n[{time.strftime('%X')}] 🎉 INTENSIVE TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_intensive_test(15)
