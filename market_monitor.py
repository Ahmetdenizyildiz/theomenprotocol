from http_utils import get_session
import json
import os

CACHE_FILE = "market_cache.json"

def check_market_anomalies(targets):
    """
    targets: [{"name": "Aave", "symbol": "AAVE", "trade_symbol": "AAVEUSDT", "defillama_slug": "aave"}, ...]
    Returns a list of anomalies: [{"type": "BANK_RUN", "target": target_dict, "details": "..."}, ...]
    """
    anomalies = []
    current_data = {}
    session = get_session()
    
    # --- 1. DefiLlama TVL Fetch ---
    try:
        r_llama = session.get("https://api.llama.fi/protocols", timeout=10)
        llama_data = r_llama.json()
        llama_map = {p["slug"].lower(): p.get("tvl", 0) for p in llama_data if "slug" in p}
    except Exception as e:
        print(f"DefiLlama API Error: {e}")
        llama_map = {}

    # --- 2. Binance Volume Fetch ---
    try:
        r_binance = session.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        binance_data = r_binance.json()
        binance_map = {t["symbol"]: float(t.get("quoteVolume", 0)) for t in binance_data if "symbol" in t}
    except Exception as e:
        print(f"Binance API Error: {e}")
        binance_map = {}

    # --- 3. Load Cache ---
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                old_cache = json.load(f)
        except:
            old_cache = {}
    else:
        old_cache = {}

    # --- 4. Process Targets and Check Anomalies ---
    for target in targets:
        symbol = target.get("symbol", "")
        trade_symbol = target.get("trade_symbol", "")
        name = target.get("name", "")
        
        # Simplified mapping from name to defillama slug if not explicitly set
        slug = name.lower().replace(" ", "-")
        
        current_tvl = llama_map.get(slug, 0)
        current_vol = binance_map.get(trade_symbol, 0)
        
        current_data[trade_symbol] = {
            "tvl": current_tvl,
            "volume": current_vol
        }
        
        if old_cache and trade_symbol in old_cache:
            old_tvl = old_cache[trade_symbol].get("tvl", 0)
            old_vol = old_cache[trade_symbol].get("volume", 0)
            
            # Check Bank Run (TVL Drop > 5%)
            if old_tvl > 0 and current_tvl > 0:
                tvl_drop_pct = ((old_tvl - current_tvl) / old_tvl) * 100
                if tvl_drop_pct >= 5.0:
                    anomalies.append({
                        "type": "BANK_RUN",
                        "target": target,
                        "drop_pct": round(tvl_drop_pct, 2)
                    })
            
            # Check Smart Money (Volume Spike > 50%)
            if old_vol > 0 and current_vol > 0:
                vol_spike_pct = ((current_vol - old_vol) / old_vol) * 100
                if vol_spike_pct >= 50.0:
                    anomalies.append({
                        "type": "SMART_MONEY",
                        "target": target,
                        "spike_pct": round(vol_spike_pct, 2)
                    })

    # --- 5. Save new cache ---
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(current_data, f)
    except Exception as e:
        print(f"Cache Save Error: {e}")

    return anomalies

if __name__ == "__main__":
    # Test script
    import json
    with open("targets.json", "r") as f:
        t = json.load(f)
    print(check_market_anomalies(t))
