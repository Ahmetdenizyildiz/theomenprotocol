import sys
import json
import warnings
warnings.filterwarnings("ignore")

from qwen_brain import analyze_news_with_qwen
from market_monitor import check_market_anomalies
from onchain_analyzer import check_whale_activity

def print_result(title, result):
    print(f"\n{'='*70}\n{title}\n{'='*70}")
    if isinstance(result, dict) or isinstance(result, list):
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print(result)

print("🚀 OMNI-ALPHA KAPSAMLI (SES, MARKET, ON-CHAIN) TESTLERİ BAŞLIYOR...\n")

# --- 1. VOICE SNIPER TEST ---
print("[*] TEST 1: SES (VOICE TRANSCRIPTION) TESTİ BAŞLIYOR...")
voice_transcription = "[VOICE TRANSCRIPTION]: The US government just announced they are selling 50,000 Bitcoins from the Silk Road seizure tomorrow morning."
res_voice = analyze_news_with_qwen(voice_transcription)
print_result("TEST 1: Ses (Voice) Analizi Sonucu", res_voice)

# --- 2. MARKET ANOMALY TEST ---
print("\n[*] TEST 2: MARKET MONITOR (TVL & HACİM ANOMALİSİ) TESTİ BAŞLIYOR...")
targets = [
    {"name": "Aave", "symbol": "AAVE", "trade_symbol": "AAVEUSDT"},
    {"name": "Uniswap", "symbol": "UNI", "trade_symbol": "UNIUSDT"}
]
res_market = check_market_anomalies(targets)
print_result("TEST 2: Market Anomaly (Arka Plan Taraması) Sonucu", res_market)

# --- 3. ONCHAIN WHALE TEST ---
print("\n[*] TEST 3: ETHERSCAN WHALE ACTIVITY TESTİ BAŞLIYOR...")
res_whale = check_whale_activity("AAVEUSDT")
print_result("TEST 3: On-Chain Whale Activity (Balina Takibi) Sonucu", res_whale)

print("\n✅ TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
