import json
from github_scanner import scan_github_repo
from dao_scanner import scan_dao_proposals
from market_monitor import check_market_anomalies
from qwen_brain import get_fng_value

def test_system():
    print("=== OMNI-ALPHA DERİN SİSTEM TESTİ ===")
    
    print("\n[1] Fear & Greed Endeksi Testi")
    try:
        fng = get_fng_value()
        print(f"FNG Değeri: {fng}")
    except Exception as e:
        print(f"BAŞARISIZ: {e}")
        
    print("\n[2] GitHub API Testi (Connection Pool / ETag Check)")
    try:
        github_res = scan_github_repo("Uniswap", "v4-core")
        print(f"GitHub Sonuç: Başarılı, Yeni Commitler: {github_res['new_commits'] if github_res else 'Yok'}")
    except Exception as e:
        print(f"BAŞARISIZ: {e}")
        
    print("\n[3] DAO Snapshot GraphQL Testi")
    try:
        dao_res = scan_dao_proposals("uniswap.eth")
        print(f"DAO Sonuç: Başarılı, Teklif: {dao_res['title'] if dao_res else 'Yok'}")
    except Exception as e:
        print(f"BAŞARISIZ: {e}")
        
    print("\n[4] Market Monitor (DefiLlama & Binance) Testi")
    try:
        with open("targets.json", "r") as f:
            targets = json.load(f)
        # Sadece 2 hedef test et
        anomalies = check_market_anomalies(targets[:2])
        print(f"Market Monitor Sonuç: Başarılı, {len(anomalies)} anormallik bulundu.")
    except Exception as e:
        print(f"BAŞARISIZ: {e}")
        
    print("\n=== TEST TAMAMLANDI ===")

if __name__ == "__main__":
    test_system()
