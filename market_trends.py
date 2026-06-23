import urllib.request
import json

def get_trending_coins():
    """
    Fetches the top trending coins from CoinGecko's public API.
    Returns a formatted string for Telegram.
    """
    url = "https://api.coingecko.com/api/v3/search/trending"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        
        trends = []
        for i, coin in enumerate(data.get('coins', [])[:10]):  # Get top 10
            item = coin['item']
            name = item.get('name', 'Unknown')
            symbol = item.get('symbol', 'Unknown')
            rank = item.get('market_cap_rank', 'N/A')
            trends.append(f"{i+1}. *{name}* ({symbol}) - Rank: {rank}")
            
        if trends:
            return "🔥 *PİYASANIN GİZLİ TRENDLERİ (CoinGecko Top 10)* 🔥\n\n" + "\n".join(trends)
        else:
            return "Trend verisi alınamadı."
    except Exception as e:
        return f"Trend analizinde hata oluştu: {e}"

if __name__ == "__main__":
    print(get_trending_coins())
