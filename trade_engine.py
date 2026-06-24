import os
import json
import requests
from datetime import datetime
import csv
from dotenv import load_dotenv

load_dotenv(override=True)

TRADING_MODE = os.getenv("TRADING_MODE", "PAPER")

# BITGET_API_KEY = os.getenv("BITGET_API_KEY")
# BITGET_SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
# BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

WALLET_FILE = "wallet.json"

def get_current_price(symbol):
    """
    Fetches the current price of a symbol (e.g. BTCUSDT) from Bitget public v2 API.
    """
    symbol_formatted = symbol.replace("/", "").upper()
    url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol_formatted}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == "00000" and data.get("data"):
            return float(data["data"][0]["lastPr"])
    except Exception as e:
        print(f"[TRADE] Failed to fetch price for ({symbol}): {e}")
    return 0.0

def calculate_position_size(confidence_score, impact_score, portfolio_usdt=1000.0):
    """
    Autonomous risk and money management algorithm similar to Kelly Criterion.
    Maximum risk is capped at 25% of the portfolio.
    """
    if confidence_score < 50 or impact_score < 4:
        return 0, 0.0

    # Risk factor: (Confidence / 100) * (Impact / 10) * Max Risk Cap (0.25)
    risk_percentage = (confidence_score / 100.0) * (impact_score / 10.0) * 0.25
    
    # Round to 1 decimal place
    risk_percentage = round(risk_percentage * 100, 1)
    
    # Investment amount
    position_size = (portfolio_usdt * risk_percentage) / 100.0
    return round(position_size, 2), risk_percentage

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        wallet = {
            "balance_usdt": 10000.0,
            "positions": []
        }
        with open(WALLET_FILE, "w") as f:
            json.dump(wallet, f, indent=4)
        return wallet
    with open(WALLET_FILE, "r") as f:
        return json.load(f)

def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=4)

def execute_trade(symbol, usdt_amount=100.0):
    """Executes trade based on mode (PAPER or REAL)"""
    if TRADING_MODE == "REAL":
        return execute_real_trade(symbol, usdt_amount)
    else:
        return execute_paper_trade(symbol, usdt_amount)

def execute_paper_trade(symbol, usdt_amount):
    """Executes a paper trade using the virtual wallet"""
    wallet = load_wallet()
    
    if wallet["balance_usdt"] < usdt_amount:
        return f"🚨 Insufficient Balance! Remaining: {wallet['balance_usdt']:.2f} USDT"
        
    current_price = get_current_price(symbol)
    if current_price == 0:
        return f"🚨 Could not get current price for {symbol}. Trade cancelled."
        
    coin_amount = usdt_amount / current_price
    
    # Deduct balance
    wallet["balance_usdt"] -= usdt_amount
    
    # Add position
    wallet["positions"].append({
        "symbol": symbol,
        "buy_price": current_price,
        "amount": coin_amount,
        "usdt_invested": usdt_amount,
        "timestamp": datetime.now().isoformat()
    })
    
    save_wallet(wallet)
    
    # Log the trade to CSV for Hackathon "Verifiable Usage Record" requirement
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/trading_log.csv"
    file_exists = os.path.exists(log_file)
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Symbol", "Direction", "Price", "Amount", "Account_Balance_Change", "Remaining_Balance"])
        writer.writerow([
            datetime.now().isoformat(),
            symbol,
            "BUY",
            current_price,
            coin_amount,
            f"-{usdt_amount:.2f}",
            wallet["balance_usdt"]
        ])
    
    return f"🟢 [PAPER TRADE] {symbol} bought!\n💰 Price: {current_price}\n💵 Invested: {usdt_amount} USDT\n💼 Remaining Balance: {wallet['balance_usdt']:.2f} USDT"

def execute_real_trade(symbol, usdt_amount):
    """Sends real order to Bitget API via CCXT"""
    return "🚨 [REAL MODE ACTIVE] Real execution logic via `ccxt` will go here once API keys are active."

def get_portfolio_status():
    """Calculates live PnL"""
    if TRADING_MODE == "REAL":
        return "Please check your Bitget App for real portfolio balance."
        
    wallet = load_wallet()
    total_worth = wallet["balance_usdt"]
    
    report = "📊 *PAPER TRADING PORTFOLIO*\n\n"
    report += f"💵 Cash (USDT): {wallet['balance_usdt']:.2f}\n"
    
    if not wallet["positions"]:
        report += "\nNo open positions yet."
        return report
        
    report += "\n📈 *Open Positions:*\n"
    
    for pos in wallet["positions"]:
        current_price = get_current_price(pos["symbol"])
        if current_price > 0:
            current_value = pos["amount"] * current_price
            pnl_usdt = current_value - pos["usdt_invested"]
            pnl_percent = (pnl_usdt / pos["usdt_invested"]) * 100
            
            icon = "🟢" if pnl_usdt >= 0 else "🔴"
            report += f"{icon} *{pos['symbol']}*\n"
            report += f"Entry: {pos['buy_price']} | Current: {current_price}\n"
            report += f"Invested: {pos['usdt_invested']:.2f} USDT | Value: {current_value:.2f} USDT\n"
            report += f"PnL: {pnl_percent:.2f}% ({pnl_usdt:.2f} USDT)\n\n"
            
            total_worth += current_value
            
    report += f"💎 *Total Net Worth:* {total_worth:.2f} USDT"
    return report
