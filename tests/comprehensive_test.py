import time
import json
import logging
from qwen_brain import analyze_news_with_qwen
from github_scanner import scan_github_repo
from dao_scanner import scan_dao_proposals
from signal_provider import calculate_rsi, TARGET_SYMBOLS
from market_monitor import check_market_anomalies
from http_utils import get_session

# Set up English logging to system_execution.log
logging.basicConfig(
    filename='system_execution.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

def print_and_log(msg):
    logging.info(msg)

def format_telegram_alert(title, result, url):
    impact = result.get("impact_score", 0)
    symbol = result.get("affected_symbol", "UNKNOWN")
    decision = result.get("decision", "NEUTRAL")
    reason = result.get("reason", "")
    
    alert_msg = (
        f"🚨 *[OTOMATİK PİYASA UYARISI]* 🚨\n\n"
        f"Yüksek etkili yeni bir haber tespit edildi!\n"
        f"📰 *Haber:* {title}\n"
        f"🎯 *Etkilenen Varlık:* {symbol} ({decision})\n"
        f"🔥 *Etki Puanı:* {impact}/10\n\n"
        f"💡 *Gerekçe:* {reason}\n\n"
        f"🔗 [Kaynağa Git]({url})"
    )
    return alert_msg

def run_comprehensive_tests():
    print_and_log("==================================================")
    print_and_log("🚀 OMEN PROTOCOL: COMPREHENSIVE SYSTEM TEST SUITE")
    print_and_log("==================================================")
    
    # ---------------------------------------------------------
    # TEST 1: NEWS SENTIMENT & AI REACTION
    # ---------------------------------------------------------
    print_and_log("\n[TEST 1] AI News Sentiment Engine")
    print_and_log("PURPOSE: To verify if the Qwen AI LLM can ingest breaking macroeconomic/crypto news, accurately assess its market impact, and generate a structured trade signal without crashing.")
    
    test_news_title = "Mt. Gox to Start Bitcoin Repayments in July, Triggering Market Panic"
    test_news_summary = "The defunct Mt. Gox exchange will begin distributing billions of dollars in Bitcoin and Bitcoin Cash to creditors starting the first week of July, potentially introducing massive sell pressure to the market."
    test_news_url = "https://www.coindesk.com/mt-gox-repayments"
    
    text_to_analyze = f"Title: {test_news_title}\nSummary: {test_news_summary}\nLink: {test_news_url}"
    print_and_log(f"-> Injecting test news: '{test_news_title}'")
    
    ai_result = analyze_news_with_qwen(text_to_analyze)
    if ai_result and not ai_result.get("error"):
        print_and_log(f"-> AI Processing Successful. Extracted JSON: {json.dumps(ai_result, indent=2)}")
        if ai_result.get("impact_score", 0) >= 7:
            telegram_output = format_telegram_alert(test_news_title, ai_result, test_news_url)
            print_and_log(f"-> TELEGRAM BOT OUTPUT (Simulated):\n{telegram_output}")
        else:
            print_and_log("-> AI determined impact score < 7. No automated alert triggered.")
    else:
        print_and_log(f"-> AI Processing FAILED or returned empty. Fallback would activate. Error: {ai_result}")

    # ---------------------------------------------------------
    # TEST 2: GITHUB DEVELOPER ACTIVITY TRACKER
    # ---------------------------------------------------------
    print_and_log("\n[TEST 2] GitHub Developer Activity Scanner")
    print_and_log("PURPOSE: To verify the agent's ability to fetch the latest commits from a DeFi protocol's repository, providing early 'insider' alpha before major news breaks.")
    
    print_and_log("-> Fetching latest commits for Uniswap/v4-core...")
    github_result = scan_github_repo("Uniswap", "v4-core")
    if github_result:
        print_and_log(f"-> GitHub Fetch Successful. Latest commit SHA: {github_result['latest_sha']}")
        print_and_log(f"-> Commit Message: {github_result['commit_message']}")
        print_and_log("-> TELEGRAM BOT OUTPUT (Simulated):")
        print_and_log(f"💻 *GITHUB UPDATE: Uniswap/v4-core*\n**Yazar:** {github_result['author']}\n**Commit:** {github_result['commit_message']}")
    else:
        print_and_log("-> GitHub Fetch FAILED or Repo Not Found.")

    # ---------------------------------------------------------
    # TEST 3: ON-CHAIN DAO PROPOSAL TRACKER
    # ---------------------------------------------------------
    print_and_log("\n[TEST 3] Snapshot DAO Proposal Scanner")
    print_and_log("PURPOSE: To verify if the agent can track decentralized governance proposals, allowing traders to front-run protocol changes (like fee switches or treasury unlocks).")
    
    print_and_log("-> Fetching latest DAO proposals for 'uniswap.eth'...")
    dao_result = scan_dao_proposals("uniswap.eth")
    if dao_result:
        print_and_log(f"-> DAO Fetch Successful. Proposal: {dao_result['title']}")
        print_and_log(f"-> Status: {dao_result['state']} | Voting Ends: {dao_result['end']}")
    else:
        print_and_log("-> DAO Fetch FAILED or Space Not Found.")

    # ---------------------------------------------------------
    # TEST 4: BINANCE RSI (TECHNICAL INDICATOR) SIGNAL
    # ---------------------------------------------------------
    print_and_log("\n[TEST 4] Binance Technical Indicator (15m RSI) Scanner")
    print_and_log("PURPOSE: To verify the Signal Provider calculates RSI accurately using Live Binance Klines to detect 'Oversold' dip-buying opportunities.")
    
    session = get_session()
    test_symbol = "BTCUSDT"
    print_and_log(f"-> Fetching 15m Klines for {test_symbol}...")
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={test_symbol}&interval=15m&limit=20"
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            close_prices = [float(candle[4]) for candle in data]
            if close_prices:
                current_price = close_prices[-1]
                rsi = calculate_rsi(close_prices)
                print_and_log(f"-> RSI Calculation Successful. Current Price: {current_price}, 15m RSI: {rsi:.2f}")
                if rsi < 25:
                    print_and_log(f"-> 🚨 ALGORITHMIC SIGNAL MET (RSI {rsi:.2f} < 25). Paper trade would execute.")
                else:
                    print_and_log(f"-> No oversold condition met (RSI {rsi:.2f} >= 25).")
    except Exception as e:
        print_and_log(f"-> Binance Fetch FAILED: {e}")

    # ---------------------------------------------------------
    # TEST 5: DEFILLAMA TVL ANOMALY DETECTOR
    # ---------------------------------------------------------
    print_and_log("\n[TEST 5] DefiLlama TVL Bank Run Detector")
    print_and_log("PURPOSE: To verify the agent can track Total Value Locked across DeFi protocols to detect sudden liquidity drains or 'Bank Runs'.")
    
    targets = [{"name": "Aave", "symbol": "AAVE", "trade_symbol": "AAVEUSDT", "defillama_slug": "aave"}]
    print_and_log(f"-> Checking TVL & Volume Anomalies for target: {targets[0]['name']}...")
    try:
        anomalies = check_market_anomalies(targets)
        print_and_log(f"-> Anomaly Check Successful. Anomalies detected: {len(anomalies)}")
        for anomaly in anomalies:
            print_and_log(f"   * Type: {anomaly.get('type')}, Target: {anomaly.get('target', {}).get('trade_symbol')}")
    except Exception as e:
        print_and_log(f"-> TVL Anomaly Check FAILED: {e}")

    print_and_log("\n==================================================")
    print_and_log("✅ COMPREHENSIVE SYSTEM TEST SUITE COMPLETED")
    print_and_log("==================================================")

if __name__ == "__main__":
    run_comprehensive_tests()
