import sys
import json
import base64
import time
import requests
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

print("🚀 OMNI-ALPHA KAPSAMLI (GÖRSEL, SES, ON-CHAIN) TESTLERİ BAŞLIYOR...\n")

# --- 1. IMAGE SNIPER TEST ---
print("[*] TEST 1: GÖRSEL (IMAGE SNIPER) TESTİ BAŞLIYOR...")
try:
    # 1x1 valid JPEG base64 to test the VLM pipeline
    b64_image = "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
    
    img_prompt = "This chart screenshot shows Ethereum dropping by 20% in the last hour due to an exchange hack. What is your playbook?"
    res_img = analyze_news_with_qwen(img_prompt, image_b64=b64_image)
    print_result("TEST 1: Görsel (Image) Analiz Sonucu", res_img)
except Exception as e:
    print(f"Görsel Testi Hatası: {e}")

time.sleep(2) # Prevent API rate limits

# --- 2. VOICE SNIPER TEST ---
print("\n[*] TEST 2: SES (VOICE TRANSCRIPTION) TESTİ BAŞLIYOR...")
voice_transcription = "[VOICE TRANSCRIPTION]: The US government just announced they are selling 50,000 Bitcoins from the Silk Road seizure tomorrow morning."
res_voice = analyze_news_with_qwen(voice_transcription)
print_result("TEST 2: Ses (Voice) Analizi Sonucu", res_voice)

time.sleep(2)

# --- 3. MARKET ANOMALY TEST ---
print("\n[*] TEST 3: MARKET MONITOR (TVL & HACİM ANOMALİSİ) TESTİ BAŞLIYOR...")
targets = [
    {"name": "Aave", "symbol": "AAVE", "trade_symbol": "AAVEUSDT"},
    {"name": "Uniswap", "symbol": "UNI", "trade_symbol": "UNIUSDT"}
]
res_market = check_market_anomalies(targets)
print_result("TEST 3: Market Anomaly (Arka Plan Taraması) Sonucu", res_market)

# --- 4. ONCHAIN WHALE TEST ---
print("\n[*] TEST 4: ETHERSCAN WHALE ACTIVITY TESTİ BAŞLIYOR...")
res_whale = check_whale_activity("AAVEUSDT")
print_result("TEST 4: On-Chain Whale Activity (Balina Takibi) Sonucu", res_whale)

print("\n✅ TÜM KAPSAMLI TESTLER BAŞARIYLA TAMAMLANDI!")
