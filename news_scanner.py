import time
import feedparser
import threading
from qwen_brain import analyze_news_with_qwen

RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
]

SEEN_URLS = set()

def scan_rss_feeds(bot, chat_ids):
    """
    Scans RSS feeds for breaking news. If a new item is found, it sends it to Qwen.
    If Qwen determines it's a huge catalyst (impact_score >= 7), it alerts the Telegram chats.
    """
    print("[NEWS SCANNER] Background market scanner started...")
    
    while True:
        try:
            for feed_url in RSS_FEEDS:
                feed = feedparser.parse(feed_url)
                
                # Sadece en güncel 3 habere bakıyoruz
                for entry in feed.entries[:3]:
                    url = entry.link
                    if url not in SEEN_URLS:
                        SEEN_URLS.add(url)
                        
                        title = entry.title
                        summary = entry.get('summary', '')
                        
                        # Haberi analiz et
                        text_to_analyze = f"Title: {title}\nSummary: {summary}\nLink: {url}"
                        print(f"[NEWS SCANNER] Yeni haber tespit edildi: {title}")
                        
                        result = analyze_news_with_qwen(text_to_analyze)
                        
                        if result and not result.get("error"):
                            impact = result.get("impact_score", 0)
                            
                            # EĞER ÇOK BÜYÜK BİR HABER İSE (OTONOM UYARI SİSTEMİ)
                            if impact >= 7:
                                symbol = result.get("affected_symbol", "UNKNOWN")
                                decision = result.get("decision", "NEUTRAL")
                                reason = result.get("reason", "")
                                
                                alert_msg = (
                                    f"🚨 *[OTOMATİK PİYASA UYARISI]* 🚨\n\n"
                                    f"Yüksek etkili yeni bir haber tespit edildi!\n"
                                    f"📰 *Haber:* {title}\n"
                                    f"🎯 *Etkilenen Varlık:* {symbol} ({decision})\n"
                                    f"🔥 *Etki Puanı:* {impact}/10\n\n"
                                    f"💡 *Gerekçe:* {reason}\n\n"
                                    f"🔗 [Kaynağa Git]({url})"
                                )
                                for cid in chat_ids:
                                    try:
                                        bot.send_message(cid, alert_msg, parse_mode="Markdown")
                                    except:
                                        pass
                                
        except Exception as e:
            print(f"[NEWS SCANNER] Hata: {e}")
            
        time.sleep(60) # Her 60 saniyede bir tarama yap

def start_news_scanner_thread(bot, chat_ids):
    thread = threading.Thread(target=scan_rss_feeds, args=(bot, chat_ids), daemon=True)
    thread.start()
    return thread
