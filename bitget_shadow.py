import os
import json
import ccxt
from datetime import datetime

WALLET_FILE = "wallet.json"

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        default_wallet = {
            "balance_usdt": 10000.0,
            "positions": []
        }
        save_wallet(default_wallet)
        return default_wallet
    
    with open(WALLET_FILE, "r") as f:
        return json.load(f)

def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=4)

def execute_shadow_trade(symbol, decision, confidence):
    """
    Sanal cüzdan (wallet.json) üzerinden işlem yapar. 
    Gerçek zamanlı fiyatı alır ve Demo Bakiyeden düşer.
    """
    output = f"\n🎯 [BITGET SHADOW MODE]\nİşlem Sinyali: {decision} (Güven: {confidence}%)\n"
    
    if decision != "BULLISH" or confidence < 80:
        output += "⚠️ Karar BULLISH değil veya güven yetersiz. İşlem pas geçildi."
        return output

    try:
        exchange = ccxt.bitget()
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        wallet = load_wallet()
        trade_amount_usdt = 100.0 # Her sinyalde 100 USDT'lik alım yapıyoruz
        
        if wallet["balance_usdt"] < trade_amount_usdt:
            return output + "❌ Yetersiz bakiye! İşlem yapılamadı."
            
        # Bakiyeden düş, coini al
        coin_amount = trade_amount_usdt / current_price
        wallet["balance_usdt"] -= trade_amount_usdt
        
        # Pozisyonu kaydet
        wallet["positions"].append({
            "symbol": symbol,
            "buy_price": current_price,
            "amount": coin_amount,
            "usdt_invested": trade_amount_usdt,
            "timestamp": datetime.now().isoformat()
        })
        
        save_wallet(wallet)
        
        output += f"📊 [{symbol}] Anlık Fiyat: {current_price} USDT\n"
        output += f"🟢 SANAL İŞLEM BAŞARILI: {trade_amount_usdt} USDT tutarında {coin_amount:.4f} {symbol} alındı.\n"
        output += f"💰 Kalan Kasa: {wallet['balance_usdt']:.2f} USDT"
            
        return output
    except Exception as e:
        return output + f"❌ Hata: {e}"

def get_portfolio_status():
    """
    Kullanıcının sanal cüzdanındaki mevcut kâr/zarar durumunu hesaplar.
    """
    wallet = load_wallet()
    positions = wallet.get("positions", [])
    
    output = "💼 *SANAL CÜZDAN DURUMU (Paper Trading)* 💼\n\n"
    output += f"Boştaki Bakiye: *{wallet['balance_usdt']:.2f} USDT*\n\n"
    
    if not positions:
        output += "Henüz açık bir pozisyon bulunmuyor."
        return output
        
    try:
        exchange = ccxt.bitget()
        total_invested = 0
        total_current_value = 0
        
        for idx, pos in enumerate(positions):
            symbol = pos['symbol']
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            buy_price = pos['buy_price']
            amount = pos['amount']
            invested = pos['usdt_invested']
            
            current_value = amount * current_price
            profit_loss = current_value - invested
            profit_loss_percent = (profit_loss / invested) * 100
            
            total_invested += invested
            total_current_value += current_value
            
            icon = "🟢" if profit_loss >= 0 else "🔴"
            output += f"🔹 *{symbol}*\n"
            output += f"   Giriş Fiyatı: {buy_price} USDT\n"
            output += f"   Anlık Fiyat: {current_price} USDT\n"
            output += f"   Yatırım: {invested} USDT\n"
            output += f"   Durum: {icon} {profit_loss:+.2f} USDT ({profit_loss_percent:+.2f}%)\n\n"
            
        total_pl = total_current_value - total_invested
        total_pl_percent = (total_pl / total_invested) * 100 if total_invested > 0 else 0
        
        net_worth = wallet['balance_usdt'] + total_current_value
        
        output += "-----------------------------\n"
        output += f"Toplam Yatırım: *{total_invested:.2f} USDT*\n"
        output += f"Yatırımların Güncel Değeri: *{total_current_value:.2f} USDT*\n"
        output += f"Genel Kâr/Zarar: *{total_pl:+.2f} USDT ({total_pl_percent:+.2f}%)*\n"
        output += f"🏆 Toplam Varlık (Net Worth): *{net_worth:.2f} USDT*"
        
        return output
    except Exception as e:
        return f"❌ Portföy hesaplanırken hata oluştu: {e}"

if __name__ == "__main__":
    # Test
    print(get_portfolio_status())
