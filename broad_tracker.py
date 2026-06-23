import time
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Popüler ERC-20 Token Kontratları
TOKENS = {
    "UNI": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "PEPE": "0x6982508145454Ce325dDbE47a25d4ec3d2311933"
}

def get_etherscan_latest_tx(contract, decimals=18):
    if not ETHERSCAN_API_KEY: return "NO API KEY"
    url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&contractaddress={contract}&page=1&offset=1&sort=desc&apikey={ETHERSCAN_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data["status"] == "1" and data["result"]:
            tx = data["result"][0]
            # Etherscan explorer linki ile verelim ki tıklandığında anında teyit edilebilsin
            tx_hash = tx['hash']
            value = float(tx['value']) / (10**int(tx['tokenDecimal']))
            return f"{value:,.2f} adet -> https://etherscan.io/tx/{tx_hash}"
    except Exception as e:
        return f"Error: {e}"
    return "No TX"

print("🌍 GENİŞ ÇAPLI (MULTI-COIN) CANLI ZİNCİR TAKİBİ BAŞLIYOR...\n")
print("Sistemin ağa olan bağını kanıtlamak için UNI, AAVE, LINK ve PEPE'nin Ethereum üzerindeki son işlemlerini canlı çekiyorum.\nSize verilen Etherscan linklerine tıklayıp işlemlerin 'Seconds ago' (Birkaç saniye önce) yapıldığını kendi gözlerinizle görebilirsiniz.\n")

for i in range(1, 5):
    print(f"⏱️ ZAMAN DİLİMİ {i} (Her coin için anlık Etherscan sorgusu):")
    
    for symbol, contract in TOKENS.items():
        tx_info = get_etherscan_latest_tx(contract)
        print(f"   🔹 {symbol:4s} Son İşlem : {tx_info}")
        time.sleep(0.5) # API rate limit (5 calls/sec limit) için ufak bekleme
        
    print("-" * 75)
    
    if i < 4:
        print("   [⏳ Zincire yeni blokların eklenmesi bekleniyor (15 sn)...]")
        time.sleep(15)

print("\n✅ Geniş çaplı veri testi tamamlandı!")
