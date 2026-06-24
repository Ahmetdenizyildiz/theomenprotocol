import time
import threading
from http_utils import get_session
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Takip edilecek büyük hacimli koinler
TARGET_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "AVAXUSDT", "DOGEUSDT"]

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50 # Yeterli veri yoksa nötr dön
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
            
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def fetch_klines_and_check_signals(bot, get_chat_ids_func):
    """
    Binance'ten 15 dakikalık mumları çeker. RSI < 25 ise aşırı satım (Oversold) sinyali üretir.
    """
    print("[SIGNAL PROVIDER] Binance Algoritmik Sinyal Motoru başlatıldı...")
    session = get_session()
    
    while True:
        try:
            for symbol in TARGET_SYMBOLS:
                # 15 dakikalık mumlar (son 20 mum yeterli)
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=20"
                response = session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    close_prices = [float(candle[4]) for candle in data]
                    
                    if close_prices:
                        current_price = close_prices[-1]
                        rsi = calculate_rsi(close_prices)
                        
                        # AŞIRI SATIM (DİP) SİNYALİ!
                        if rsi < 25:
                            print(f"[SIGNAL] {symbol} DİP YAKALANDI! RSI: {rsi:.2f}")
                            
                            msg = (
                                f"🚨 *[ALGORİTMİK DİP SİNYALİ]* 🚨\n\n"
                                f"💎 *Varlık:* {symbol}\n"
                                f"📉 *Durum:* Aşırı Satış (Oversold)!\n"
                                f"📊 *15m RSI:* {rsi:.2f} (Kritik Seviye: 25)\n"
                                f"💵 *Anlık Fiyat:* {current_price} USDT\n\n"
                                f"💡 *Açıklama:* Algoritmalarımız bu varlıkta çok ani bir çöküş tespit etti. "
                                f"Geri sekme (tepki yükselişi) ihtimali çok yüksek!"
                            )
                            
                            markup = InlineKeyboardMarkup()
                            markup.add(
                                InlineKeyboardButton("✅ İŞLEM AÇ (BUY)", callback_data=f"buy|{symbol}|200") # Default 200 USDT
                            )
                            
                            current_chat_ids = get_chat_ids_func()
                            for cid in current_chat_ids:
                                try:
                                    bot.send_message(cid, msg, parse_mode="Markdown", reply_markup=markup)
                                except:
                                    pass
                                    
        except Exception as e:
            print(f"[SIGNAL PROVIDER] Hata: {e}")
            
        time.sleep(300) # Her 5 dakikada bir kontrol et

def start_signal_provider_thread(bot, get_chat_ids_func):
    thread = threading.Thread(target=fetch_klines_and_check_signals, args=(bot, get_chat_ids_func), daemon=True)
    thread.start()
    return thread
