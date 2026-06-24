import time
import requests
import json
import os
from signal_provider import calculate_rsi

def run_backtest():
    print("🚀 Starting Historical Backtest Engine...")
    symbol = "BTCUSDT"
    interval = "15m"
    limit = 1000 # Max allowed by Binance per request
    
    # 1. Fetch Historical Data
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch historical data: {e}")
        return

    closes = [float(candle[4]) for candle in data]
    timestamps = [int(candle[0]) for candle in data]
    
    # 2. Simulate Trading Engine
    initial_balance = 10000.0
    balance = initial_balance
    position = 0.0
    entry_price = 0.0
    trades = []
    
    # Simple strategy: Buy when RSI < 25, Sell when RSI > 70 or 3% Stop Loss or 5% Take Profit
    for i in range(15, len(closes)):
        current_price = closes[i]
        current_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamps[i]/1000))
        
        # Calculate RSI on a rolling window
        window = closes[i-15:i+1]
        rsi = calculate_rsi(window)
        
        if position == 0.0:
            if rsi < 25.0:
                # Buy
                risk_amount = balance * 0.25 # Risk 25% of portfolio per our logic
                position = risk_amount / current_price
                balance -= risk_amount
                entry_price = current_price
                trades.append({"type": "BUY", "price": current_price, "time": current_time_str, "rsi": rsi})
                
        elif position > 0.0:
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            if rsi > 70.0 or pnl_pct >= 5.0 or pnl_pct <= -3.0:
                # Sell
                revenue = position * current_price
                balance += revenue
                position = 0.0
                trades.append({"type": "SELL", "price": current_price, "time": current_time_str, "pnl": pnl_pct})

    # Close any open positions at the end
    if position > 0.0:
        revenue = position * closes[-1]
        balance += revenue
        position = 0.0
        pnl_pct = ((closes[-1] - entry_price) / entry_price) * 100
        trades.append({"type": "SELL", "price": closes[-1], "time": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamps[-1]/1000)), "pnl": pnl_pct})

    total_profit = balance - initial_balance
    roi = (total_profit / initial_balance) * 100
    win_trades = len([t for t in trades if t["type"] == "SELL" and t.get("pnl", 0) > 0])
    loss_trades = len([t for t in trades if t["type"] == "SELL" and t.get("pnl", 0) <= 0])
    total_completed_trades = win_trades + loss_trades
    win_rate = (win_trades / total_completed_trades * 100) if total_completed_trades > 0 else 0

    print(f"✅ Backtest Complete! ROI: {roi:.2f}% | Win Rate: {win_rate:.2f}%")

    # 3. Generate Report
    os.makedirs("docs", exist_ok=True)
    report_path = "docs/backtest_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Omen Protocol: Historical Strategy Backtest Report\n\n")
        f.write("**Asset:** BTCUSDT\n")
        f.write("**Timeframe:** 15m (Last 1000 Candles)\n")
        f.write("**Strategy:** Extreme Technical Exhaustion (RSI < 25 Buy, RSI > 70 Sell, 3% SL, 5% TP)\n")
        f.write("**Position Sizing:** 25% of Portfolio Risk per Trade\n\n")
        f.write("## Performance Summary\n")
        f.write(f"- **Initial Balance:** ${initial_balance:,.2f}\n")
        f.write(f"- **Final Balance:** ${balance:,.2f}\n")
        f.write(f"- **Total Net Profit:** ${total_profit:,.2f} ({roi:.2f}% ROI)\n")
        f.write(f"- **Total Trades:** {total_completed_trades}\n")
        f.write(f"- **Win Rate:** {win_rate:.2f}%\n")
        f.write(f"- **Profitable Trades:** {win_trades}\n")
        f.write(f"- **Losing Trades:** {loss_trades}\n\n")
        f.write("## Trade Log Snippet\n```text\n")
        for t in trades[:10]: # Show first 10
            if t["type"] == "BUY":
                f.write(f"[{t['time']}] BUY @ {t['price']:.2f} (RSI: {t['rsi']:.2f})\n")
            else:
                f.write(f"[{t['time']}] SELL @ {t['price']:.2f} (PnL: {t['pnl']:.2f}%)\n")
        f.write("...\n```\n")
        f.write("\n*Note: This backtest was generated dynamically using live historical data from Binance API.*")
    
    print(f"📄 Report written to {report_path}")

if __name__ == "__main__":
    run_backtest()
