import time
import datetime
import json
from market_monitor import check_market_anomalies
from onchain_analyzer import check_whale_activity
from qwen_brain import analyze_news_with_qwen

print("🚀 10 DAKİKALIK KESİNTİSİZ OMNI-ALPHA TESTİ BAŞLIYOR...")
print(f"Başlangıç: {datetime.datetime.now().strftime('%H:%M:%S')}")

# Dummy 20x20 transparent PNG base64 (Bypasses Qwen width/height > 10 constraint)
B64_IMG = "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAKElEQVR42mP8z8Dwn4GKgHHUwFEDRw0cNXDUwFEDRw0cNXDUwFEDAwByxgj/q8lXRAAAAABJRU5ErkJggg=="

report = []

targets = [
    {"name": "Aave", "symbol": "AAVE", "trade_symbol": "AAVEUSDT"},
    {"name": "Uniswap", "symbol": "UNI", "trade_symbol": "UNIUSDT"}
]

for minute in range(1, 11):
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] ⏳ Dakika {minute}/10 taraması başlatılıyor...")
    
    # 1. Market Monitor
    market_res = check_market_anomalies(targets)
    
    # 2. Onchain
    onchain_uni = check_whale_activity("UNIUSDT")
    
    # 3. AI Analysis (Voice/Text)
    news_text = f"Flash news at minute {minute}: Ethereum network upgrade successfully deployed."
    ai_text_res = analyze_news_with_qwen(news_text)
    
    # 4. AI Analysis (Vision) - Run once to avoid heavy rate limits on Qwen
    ai_vision_res = None
    if minute == 1:
        print("[*] Qwen Vision testi çalıştırılıyor...")
        ai_vision_res = analyze_news_with_qwen("What is in this chart?", image_b64=B64_IMG)
        
    iter_data = {
        "minute": minute,
        "market": market_res,
        "onchain_uni": onchain_uni,
        "ai_text_status": "Success" if ai_text_res else "Failed",
        "ai_vision_status": "Success" if ai_vision_res else ("Skipped" if minute != 1 else "Failed")
    }
    report.append(iter_data)
    
    print(f"✅ Dakika {minute} tamamlandı. Bekleniyor (60 sn)...")
    if minute < 10:
        time.sleep(60)

print("\n🎉 10 DAKİKALIK TEST TAMAMLANDI!")
with open("10min_report.json", "w") as f:
    json.dump(report, f, indent=4)
print("Rapor 10min_report.json dosyasına kaydedildi.")
