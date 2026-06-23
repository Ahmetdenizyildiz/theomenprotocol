import time
import json
import os
from github_scanner import scan_github_repo
from dao_scanner import scan_dao_proposals
from qwen_brain import analyze_with_qwen
from bitget_shadow import execute_shadow_trade

def load_targets():
    with open("targets.json", "r") as f:
        return json.load(f)

def run_agent():
    targets = load_targets()
    report = f"🚀 *OMNI-ALPHA: MULTI-SCAN BAŞLATILDI* 🚀\n"
    report += f"Hedef Sayısı: {len(targets)} Proje\n\n"
    
    total_trades = 0

    for target in targets:
        name = target["name"]
        github_owner = target["github_owner"]
        github_repo = target["github_repo"]
        dao_space = target["dao_space"]
        trade_symbol = target["trade_symbol"]
        
        print(f"[{name}] Taranıyor...")
        
        github_data = scan_github_repo(github_owner, github_repo)
        dao_data = scan_dao_proposals(dao_space)
        
        if not github_data and not dao_data:
            print(f"[{name}] Yeterli yeni veri yok. Atlanıyor.")
            continue
            
        qwen_result = analyze_with_qwen(github_data or {}, dao_data or {})
        
        if qwen_result:
            decision = qwen_result.get("decision", "NEUTRAL")
            confidence = qwen_result.get("confidence_score", 0)
            impact_score = qwen_result.get("impact_score", 0)
            reason = qwen_result.get("reason", "Belirtilmedi")
            catalyst_type = qwen_result.get("catalyst_type", "Bilinmiyor")
            
            # Sadece kritik güncellemeleri rapora ekle (Impact >= 5 veya BULLISH)
            if decision == "BULLISH" or impact_score >= 5:
                report += f"🔷 *{name} ({trade_symbol})*\n"
                report += f"Türü: {catalyst_type}\n"
                report += f"Karar: *{decision}* (Güven: %{confidence}, Etki: {impact_score}/10)\n"
                report += f"Açıklama: {reason}\n"
                
                # SİSTEM KURALI: Bullish, Güven >= 80 ve Etki >= 7 ise alım yap!
                if decision == "BULLISH" and confidence >= 80 and impact_score >= 7:
                    trade_result = execute_shadow_trade(trade_symbol, decision, confidence)
                    report += f"{trade_result}\n"
                    total_trades += 1
                else:
                    report += "⚠️ Şartlar (Güven>80, Etki>7) sağlanmadı. Pas geçildi.\n"
                
                report += "------------------------\n"
        
        # API limitlerine takılmamak için kısa bir bekleme
        time.sleep(1)

    if total_trades == 0:
        report += "\n🛑 *Sonuç:* Yeterli etkiye sahip (Impact >= 7) yeni bir katalizör bulunamadı. İşlem yapılmadı."
    else:
        report += f"\n✅ *Sonuç:* Toplam {total_trades} adet işlem gerçekleştirildi."
        
    return report

if __name__ == "__main__":
    print("Ajan manuel olarak başlatılıyor...")
    print(run_agent())
