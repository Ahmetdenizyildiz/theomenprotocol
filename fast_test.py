import sys
import json
from market_monitor import check_market_anomalies
from onchain_analyzer import check_whale_activity

def print_result(title, result):
    print(f"\n{'='*70}\n{title}\n{'='*70}")
    if isinstance(result, dict) or isinstance(result, list):
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print(result)

print("🚀 OMNI-ALPHA HIZLI SİSTEM (MARKET & ON-CHAIN) TESTLERİ BAŞLIYOR...\n")

# --- 1. MARKET ANOMALY TEST ---
print("[*] TEST 1: MARKET MONITOR (TVL & HACİM ANOMALİSİ) TESTİ BAŞLIYOR...")
targets = [
    {"name": "Aave", "symbol": "AAVE", "trade_symbol": "AAVEUSDT"},
    {"name": "Uniswap", "symbol": "UNI", "trade_symbol": "UNIUSDT"}
]
res_market = check_market_anomalies(targets)
print_result("TEST 1: Market Anomaly (Arka Plan Taraması) Sonucu", res_market)

# --- 2. ONCHAIN WHALE TEST ---
print("\n[*] TEST 2: ETHERSCAN WHALE ACTIVITY TESTİ BAŞLIYOR...")
res_whale = check_whale_activity("AAVEUSDT")
print_result("TEST 2: On-Chain Whale Activity (Balina Takibi) Sonucu", res_whale)

print("\n✅ TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
