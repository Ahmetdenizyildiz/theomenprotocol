import os
import time
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from github_scanner import scan_github_repo
from dao_scanner import scan_dao_proposals
from trade_engine import execute_trade, get_portfolio_status, get_current_price, calculate_position_size
from qwen_brain import analyze_with_qwen, analyze_news_with_qwen, analyze_document_with_qwen, get_fng_value
from onchain_analyzer import check_whale_activity
from market_monitor import check_market_anomalies
import json
import base64
import speech_recognition as sr
from pydub import AudioSegment
import re
from io import BytesIO
from http_utils import fetch_url_text
from market_trends import get_trending_coins
from news_scanner import start_news_scanner_thread
from signal_provider import start_signal_provider_thread
def process_text_for_urls(text):
    if not text: return text
    url_pattern = re.compile(r'https?://\S+')
    urls = url_pattern.findall(text)
    if not urls: return text
    
    extracted_texts = []
    for url in urls:
        fetched = fetch_url_text(url)
        if fetched:
            extracted_texts.append(f"--- CONTENT FROM {url} ---\n{fetched}\n------------------------")
    
    if extracted_texts:
        return text + "\n\n" + "\n".join(extracted_texts)
    return text
def escape_markdown(text):
    if not text:
        return "-"
    # Escape markdown characters that might cause parse errors
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

load_dotenv(override=True)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

CHAT_ID_FILE = "chat_ids.txt"

def get_chat_ids():
    if not os.path.exists(CHAT_ID_FILE): return set()
    with open(CHAT_ID_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def add_chat_id(chat_id):
    chat_ids = get_chat_ids()
    if str(chat_id) not in chat_ids:
        chat_ids.add(str(chat_id))
        with open(CHAT_ID_FILE, "w") as f:
            for cid in chat_ids:
                f.write(cid + "\n")

PROCESSED_EVENTS_FILE = "processed_events.json"

def get_processed_events():
    if not os.path.exists(PROCESSED_EVENTS_FILE): return {}
    with open(PROCESSED_EVENTS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

load_processed_events = get_processed_events

def save_processed_events(events):
    with open(PROCESSED_EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=4)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_chat_id(message.chat.id)
    msg = (
        "🚀 *Omni-Alpha Agent Active!*\n\n"
        "Your account is registered. I will now run in the background and scan "
        "20 major DeFi projects' GitHub and DAO data every 10 minutes.\n\n"
        "If Qwen finds a major update (Impact Score >= 7), "
        "I will send you an instant message to confirm the trade.\n\n"
        "Commands:\n"
        "/portfolio - Shows your Paper Trading PnL.\n"
        "/force\\_scan - Triggers an instant scan to test the bot."
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['force_scan'])
def handle_force_scan(message):
    add_chat_id(message.chat.id)
    bot.reply_to(message, "🛠️ *Test Mode:* System scan triggered. Scanning the first 3 projects as a test, please wait...", parse_mode="Markdown")
    
    try:
        with open("targets.json", "r") as f:
            targets = json.load(f)[:3] # Test with only first 3
            
        report = "📊 *SAMPLE SCAN RESULTS*\n\n"
        for target in targets:
            name = target["name"]
            github_data = scan_github_repo(target["github_owner"], target["github_repo"])
            dao_data = scan_dao_proposals(target["dao_space"])
            
            if github_data or dao_data:
                qwen = analyze_with_qwen(github_data or {}, dao_data or {})
                if qwen:
                    report += f"🔹 *{name}*: {qwen.get('decision', 'NEUTRAL')} (Impact: {qwen.get('impact_score', 0)}/10)\n"
                    report += f"📝 {qwen.get('reason', '')}\n\n"
            else:
                report += f"🔹 *{name}*: No new data found.\n\n"
                
        bot.send_message(message.chat.id, report, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error during test scan: {e}")

@bot.message_handler(commands=['portfolio'])
def send_portfolio(message):
    add_chat_id(message.chat.id)
    bot.reply_to(message, get_portfolio_status(), parse_mode="Markdown")

@bot.message_handler(content_types=['document'])
def handle_document_sniper(message):
    add_chat_id(message.chat.id)
    bot.send_message(message.chat.id, "📄 Document received! Analyzing deeply via Document Sniper (PDF/TXT)...")
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        doc_text = ""
        file_name = message.document.file_name.lower()
        
        if file_name.endswith(".pdf"):
            pdf_reader = PdfReader(BytesIO(downloaded_file))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    doc_text += extracted + "\n"
        elif file_name.endswith(".txt"):
            doc_text = downloaded_file.decode('utf-8')
        else:
            bot.send_message(message.chat.id, "❌ Please send only .pdf or .txt files.")
            return
            
        if not doc_text.strip():
            bot.send_message(message.chat.id, "❌ Could not extract text from document (is it a scanned image?).")
            return
            
        result = analyze_document_with_qwen(doc_text)
        process_sniper_result(message, result)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Document analysis failed: {e}")
@bot.message_handler(commands=['github'])
def handle_github(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Lütfen bir repo girin. Örnek: `/github uniswap/v4-core`", parse_mode="Markdown")
            return
            
        repo_target = parts[1].strip()
        if "/" not in repo_target:
            bot.reply_to(message, "⚠️ Lütfen geçerli bir Github Owner/Repo formatı girin. Örnek: `uniswap/v4-core`")
            return
            
        owner, repo = repo_target.split("/", 1)
        
        bot.reply_to(message, f"🔍 *{owner}/{repo}* deposundaki son 24 saatlik gelişmeler ve yazılımcı aktiviteleri çekiliyor...", parse_mode="Markdown")
        
        github_data = scan_github_repo(owner, repo)
        
        if not github_data:
            bot.reply_to(message, "❌ Bu repoda son 24 saatte kayda değer bir güncelleme (commit) bulunamadı veya repo geçersiz.")
            return
            
        bot.reply_to(message, f"✅ *{github_data['new_commits']} yeni commit bulundu!* Qwen AI tarafından önem derecesi analiz ediliyor...", parse_mode="Markdown")
        
        # Analyze using existing function
        qwen = analyze_with_qwen(github_data, {})
        
        if qwen:
            decision = qwen.get("decision", "NEUTRAL")
            confidence = qwen.get("confidence_score", 0)
            impact = qwen.get("impact_score", 0)
            reason = qwen.get("reason", "")
            
            msg = f"📊 *GITHUB OTONOM ANALİZ RAPORU*\n\n"
            msg += f"📦 *Repo:* {owner}/{repo}\n"
            msg += f"👨‍💻 *Yeni Commitler:* {github_data['new_commits']}\n"
            msg += f"🔮 *Karar:* {decision} (Güven: {confidence}%, Etki: {impact}/10)\n\n"
            msg += f"📝 *Özet:* {reason}\n"
            
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Qwen analizi sırasında bir hata oluştu.")
            
    except Exception as e:
        bot.reply_to(message, f"Hata: {e}")

@bot.message_handler(commands=['trends'])
def handle_trends(message):
    bot.reply_to(message, "🔍 CoinGecko üzerinden piyasanın gizli trendlerini kopyalıyorum...", parse_mode="Markdown")
    trends_text = get_trending_coins()
    bot.reply_to(message, trends_text, parse_mode="Markdown")

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice_sniper(message):
    bot.reply_to(message, "🎙️ *Voice Assistant Active!* Transcribing and analyzing your voice...", parse_mode="Markdown")
    try:
        file_info = bot.get_file(message.voice.file_id if message.content_type == 'voice' else message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        ogg_path = "temp_voice.ogg"
        wav_path = "temp_voice.wav"
        with open(ogg_path, "wb") as new_file:
            new_file.write(downloaded_file)
            
        AudioSegment.from_ogg(ogg_path).export(wav_path, format="wav")
        
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="en-US")
            
        bot.reply_to(message, f"🗣️ *Transcript:* {text}", parse_mode="Markdown")
        
        result = analyze_news_with_qwen(text)
        process_sniper_result(message, result)
        
        os.remove(ogg_path)
        os.remove(wav_path)
    except Exception as e:
        bot.reply_to(message, f"Voice analysis error: {e}")

@bot.message_handler(func=lambda message: True)
def handle_sniper_news(message):
    # If not a command, treat as News/Text, send to Qwen Sniper
    if message.text.startswith('/'): return
    bot.reply_to(message, "🎯 *Sniper Mode Active!* Reading links and sending to Qwen for analysis...", parse_mode="Markdown")
    
    try:
        enriched_text = process_text_for_urls(message.text)
        result = analyze_news_with_qwen(enriched_text)
        process_sniper_result(message, result)
    except Exception as e:
        bot.send_message(message.chat.id, f"Sniper error: {e}")

def process_sniper_result(message, result):
    if not result:
        bot.send_message(message.chat.id, "🤷 ❌ [HATA MOTORU] Qwen'den hiçbir yanıt alınamadı (Boş).")
        return
        
    if "error" in result:
        error_msg = f"🚨 [SİSTEM HATA MOTORU]\n\nHata Türü: {result['error']}\nDetay: {result['details']}"
        if "raw" in result:
            error_msg += f"\n\nQwen Ham Yanıtı (JSON Bozuk):\n{result['raw'][:500]}"
        bot.send_message(message.chat.id, error_msg) # parse_mode yok, format çökmesin
        return

    if not result.get("affected_symbol"):
        bot.send_message(message.chat.id, "🤷 Qwen metni okudu ancak belirgin bir coin (affected_symbol) çıkaramadı.")
        return
        
    symbol = result["affected_symbol"]
    decision = result.get("decision", "NEUTRAL")
    confidence = result.get("confidence_score", 0)
    impact = result.get("impact_score", 0)
    reason = escape_markdown(result.get("reason", ""))
    macro_analysis = escape_markdown(result.get("macro_analysis", ""))
    project_name = escape_markdown(result.get("project_name", symbol))
    
    short_t = escape_markdown(result.get("short_term", "-"))
    med_t = escape_markdown(result.get("medium_term", "-"))
    long_t = escape_markdown(result.get("long_term", "-"))
    
    playbook = result.get("playbook_strategy", {})
    pb_market = escape_markdown(playbook.get("market_condition", "-"))
    pb_trigger = escape_markdown(playbook.get("trigger", "-"))
    pb_risk = escape_markdown(playbook.get("risk_management", "-"))
    pb_exit = escape_markdown(playbook.get("exit_conditions", "-"))
    
    current_price = get_current_price(symbol)
    price_text = escape_markdown(f"{current_price} USDT") if current_price > 0 else "Unknown"
    
    # Portfolio is always paper trade here for now, assume 1000 for sizing
    rec_size, rec_pct = calculate_position_size(confidence, impact, portfolio_usdt=1000.0)
    
    msg = f"🎯 *SNIPER ANALYSIS: {project_name} ({symbol})*\n\n"
    msg += f"💵 *Current Price:* {price_text}\n"
    msg += f"📊 *Decision:* {decision} (Confidence: {confidence}%, Impact: {impact}/10)\n\n"
    if macro_analysis and macro_analysis != "-":
        msg += f"🌍 *Macro Analysis:* {macro_analysis}\n\n"
    msg += f"📝 *Summary:* {reason}\n\n"
    if playbook:
        msg += f"📘 *BITGET PLAYBOOK STRATEGY*\n"
        msg += f"• *Market Condition:* {pb_market}\n"
        msg += f"• *Trigger:* {pb_trigger}\n"
        msg += f"• *Risk Management:* {pb_risk}\n"
        msg += f"• *Exit & Stop-Loss:* {pb_exit}\n\n"
    else:
        msg += f"⏳ *Short Term:* {short_t}\n"
        msg += f"📅 *Medium Term:* {med_t}\n"
        msg += f"📈 *Long Term:* {long_t}\n\n"
    
    if impact >= 7 and decision == "BULLISH":
        msg += f"✅ *System Recommendation:* High potential! Suggested to enter with {rec_pct}% of portfolio ({rec_size} USDT)."
        btn_text = f"✅ OPEN {rec_size} USDT TRADE" if rec_size > 0 else "✅ OPEN TRADE"
    else:
        msg += "⚠️ *System Recommendation:* NOT RECOMMENDED due to low impact/confidence."
        btn_text = "✅ OPEN TRADE ANYWAY"
        
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(btn_text, callback_data=f"buy|{symbol}|{rec_size}"),
        InlineKeyboardButton("❌ PASS", callback_data=f"pass|{symbol}")
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    parts = call.data.split("|")
    action = parts[0]
    symbol = parts[1]
    amount_to_trade = None
    if len(parts) > 2 and parts[2] != "0":
        try:
            amount_to_trade = float(parts[2])
        except ValueError:
            pass

    if action == "buy":
        bot.answer_callback_query(call.id, "Executing trade...")
        amount_text = f"with {amount_to_trade} USDT " if amount_to_trade else "with Default (100) USDT "
        
        result = execute_trade(symbol, usdt_amount=amount_to_trade if amount_to_trade else 100)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ APPROVED {amount_text}!\n\n{result}")
    elif action == "pass":
        bot.answer_callback_query(call.id, "Opportunity passed.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❌ Opportunity Passed.")

def background_scan_loop():
    processed_events = load_processed_events()
    shield_activated = False
    
    with open('targets.json', 'r') as f:
        targets = json.load(f)
        
    while True:
        chat_ids = get_chat_ids()
        if not chat_ids:
            time.sleep(60)
            continue
            
        # Smart Shield (Auto-Hedge) Check
        fng_val = get_fng_value()
        if fng_val < 25 and not shield_activated:
            shield_activated = True
            shield_msg = (
                "🛡️ *SMART SHIELD ACTIVATED (AUTO-HEDGE)* 🛡️\n\n"
                f"Fear & Greed Index dropped to *{fng_val}* (Extreme Fear)! "
                "There is a risk of panic selling in the markets.\n\n"
                "💡 *Recommendation:* To protect your portfolio, consider buying Gold (PAXGUSDT) or "
                "opening a Short position on Bitcoin (BTCUSDT) to hedge your risk."
            )
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(
                InlineKeyboardButton("🛡️ BUY PAXG (GOLD)", callback_data="buy|PAXGUSDT|200"),
                InlineKeyboardButton("🛡️ SHORT BTC", callback_data="buy|BTCUSDT|200"),
                InlineKeyboardButton("❌ ACCEPT RISK", callback_data="pass|HEDGE")
            )
            for chat_id in chat_ids:
                try:
                    bot.send_message(chat_id, shield_msg, parse_mode="Markdown", reply_markup=markup)
                except Exception as e:
                    pass
        elif fng_val >= 25:
            shield_activated = False
            
        # Market Monitor (TVL Bank Run & Volume Anomalies)
        try:
            anomalies = check_market_anomalies(targets)
            for anomaly in anomalies:
                atype = anomaly.get("type")
                target_obj = anomaly.get("target", {})
                trade_symbol = target_obj.get("trade_symbol", "UNKNOWN")
                name = target_obj.get("name", "Unknown")
                
                if atype == "BANK_RUN":
                    drop_pct = anomaly.get("drop_pct", 0)
                    msg = (
                        f"🚨 *TVL COLLAPSE ALERT: {name} ({trade_symbol})* 🚨\n\n"
                        f"⚠️ DefiLlama data shows a massive *{drop_pct}%* drop in Total Value Locked (TVL) for {name} in the last 10 minutes!\n"
                        "This could indicate a HACK or whales withdrawing funds (Bank Run)."
                    )
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("🔻 EMERGENCY SHORT", callback_data=f"buy|{trade_symbol}|200"))
                elif atype == "SMART_MONEY":
                    spike_pct = anomaly.get("spike_pct", 0)
                    msg = (
                        f"🐋 *VOLUME ANOMALY: {name} ({trade_symbol})* 🐋\n\n"
                        f"📊 Binance USDT Volume shows an unusual *{spike_pct}%* spike in the last 10 minutes.\n"
                        "Smart Money might be accumulating before a price surge. BULLISH opportunity!"
                    )
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("🚀 ENTER TRADE", callback_data=f"buy|{trade_symbol}|200"))
                
                for chat_id in chat_ids:
                    try:
                        bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=markup)
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"Market Monitor Error: {e}")
            
        for target in targets:
            name = target["name"]
            github_owner = target["github_owner"]
            github_repo = target["github_repo"]
            dao_space = target["dao_space"]
            trade_symbol = target["trade_symbol"]
            
            print(f"Scanning [{name}]...")
            github_data = scan_github_repo(github_owner, github_repo)
            dao_data = scan_dao_proposals(dao_space)
            
            is_new_data = False
            
            if github_data:
                latest_sha = github_data.get("latest_sha")
                if latest_sha and processed_events.get(f"{name}_github") != latest_sha:
                    is_new_data = True
                    processed_events[f"{name}_github"] = latest_sha
            
            if dao_data:
                latest_id = dao_data.get("id")
                if latest_id and processed_events.get(f"{name}_dao") != latest_id:
                    is_new_data = True
                    processed_events[f"{name}_dao"] = latest_id
            
            if is_new_data:
                # Step 3: Cross-Analysis with On-Chain Whale Tracking
                whale_status = check_whale_activity(trade_symbol)
                
                qwen = analyze_with_qwen(github_data or {}, dao_data or {})
                if qwen:
                    decision = qwen.get("decision", "NEUTRAL")
                    confidence = qwen.get("confidence_score", 0)
                    impact = qwen.get("impact_score", 0)
                    reason = escape_markdown(qwen.get("reason", ""))
                    macro_analysis = escape_markdown(qwen.get("macro_analysis", ""))
                    short_t = escape_markdown(qwen.get("short_term", "-"))
                    med_t = escape_markdown(qwen.get("medium_term", "-"))
                    long_t = escape_markdown(qwen.get("long_term", "-"))
                    
                    playbook = qwen.get("playbook_strategy", {})
                    pb_market = escape_markdown(playbook.get("market_condition", "-"))
                    pb_trigger = escape_markdown(playbook.get("trigger", "-"))
                    pb_risk = escape_markdown(playbook.get("risk_management", "-"))
                    pb_exit = escape_markdown(playbook.get("exit_conditions", "-"))
                    
                    current_price = get_current_price(trade_symbol)
                    price_text = escape_markdown(f"{current_price} USDT") if current_price > 0 else "Unknown"
                    
                    rec_size, rec_pct = calculate_position_size(confidence, impact, portfolio_usdt=1000.0)
                    
                    msg = f"🔍 *NEW DEVELOPMENT DETECTED*\n\n"
                    msg += f"💎 *Project:* {escape_markdown(name)} ({trade_symbol})\n"
                    msg += f"💵 *Current Price:* {price_text}\n"
                    
                    # Add Whale Alert
                    if whale_status == "WHALE DUMP":
                        msg += f"🚨 *ON-CHAIN ALERT: Massive SELLING detected in Whale wallets simultaneously with this news\! This could be Insider trading dump\!*\n\n"
                    elif whale_status == "WHALE PUMP":
                        msg += f"🐋 *ON-CHAIN ALERT: Whales are currently accumulating massive amounts of {trade_symbol} from exchanges\!*\n\n"

                    msg += f"📊 *Decision:* {decision} (Confidence: {confidence}%, Impact: {impact}/10)\n\n"
                    if macro_analysis and macro_analysis != "-":
                        msg += f"🌍 *Macro Analysis:* {macro_analysis}\n\n"
                    msg += f"📝 *Summary:* {reason}\n\n"
                    if playbook:
                        msg += f"📘 *BITGET PLAYBOOK STRATEGY*\n"
                        msg += f"• *Market Condition:* {pb_market}\n"
                        msg += f"• *Trigger:* {pb_trigger}\n"
                        msg += f"• *Risk Management:* {pb_risk}\n"
                        msg += f"• *Exit & Stop-Loss:* {pb_exit}\n\n"
                    else:
                        msg += f"⏳ *Short Term:* {short_t}\n"
                        msg += f"📅 *Medium Term:* {med_t}\n"
                        msg += f"📈 *Long Term:* {long_t}\n\n"
                    
                    if decision == "BULLISH" and impact >= 7:
                        msg += f"✅ *System Recommendation:* High potential! Suggested to enter with {rec_pct}% of portfolio ({rec_size} USDT)."
                        btn_text = f"✅ OPEN {rec_size} USDT TRADE" if rec_size > 0 else "✅ OPEN TRADE"
                    else:
                        msg += "⚠️ *System Recommendation:* NOT RECOMMENDED due to low impact/confidence."
                        btn_text = "✅ OPEN TRADE ANYWAY"
                        
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 2
                    markup.add(
                        InlineKeyboardButton(btn_text, callback_data=f"buy|{trade_symbol}|{rec_size}"),
                        InlineKeyboardButton("❌ PASS", callback_data=f"pass|{trade_symbol}")
                    )
                    
                    for chat_id in chat_ids:
                        try:
                            # Use MarkdownV2 for strict escaping
                            bot.send_message(chat_id, msg, parse_mode="MarkdownV2", reply_markup=markup)
                        except Exception as e:
                            print(f"Failed to send message: {e}")
                                
        save_processed_events(processed_events)
            
        print("All projects scanned. Sleeping for 10 minutes...")
        time.sleep(600) # Sleep for 10 mins

if __name__ == "__main__":
    # Render Free Web Service Bypass (Dummy HTTP Server)
    import http.server
    import socketserver
    def start_dummy_server():
        port = int(os.environ.get("PORT", 8080))
        Handler = http.server.SimpleHTTPRequestHandler
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"Dummy Web Server running on port {port}")
                httpd.serve_forever()
        except Exception as e:
            print("HTTP Server error:", e)

    threading.Thread(target=start_dummy_server, daemon=True).start()

    # Start background loop as thread
    t = threading.Thread(target=background_scan_loop, daemon=True)
    t.start()
    
    # Start automated news scanner thread for registered chats
    start_news_scanner_thread(bot, get_chat_ids)
    
    # Start algorithmic signal provider (Binance RSI)
    start_signal_provider_thread(bot, get_chat_ids)
    
    # Process commands and messages
    bot.infinity_polling()
