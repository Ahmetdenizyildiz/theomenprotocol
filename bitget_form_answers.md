# Bitget AI Hackathon - Final Submission Form Mapping

*This document contains the exact answers to copy-paste into the Bitget Hackathon Submission Form.*

---

## 📌 Track Selection
**Question:** Track
**Your Answer:** 🟦 Trading Agent

---

## 📌 Project Description

### 1. Idea (Required, Highest Weight)
**Question:** Explain why you built it and the core logic behind it. Why does the strategy work? What signals does it use? How are decisions made? How is risk managed?
**Your Answer:**
**Why we built it:** In the modern crypto market, alpha decays in seconds. Retail traders are physically incapable of monitoring a GitHub repository for a protocol upgrade, checking Etherscan for whale dumps, interpreting the macroeconomic impact of a Federal Reserve announcement, and executing a technical trade based on 15-minute RSI charts simultaneously. We built **Omen Protocol** to democratize this institutional edge as a multi-modal, fully autonomous AI Trading Agent.

**Why the strategy works & Signals Used:** Our strategy hypothesizes that the most profitable trades occur at the intersection of *Sentiment Panic* and *Technical Exhaustion*.
1. **Macro & Sentiment (Qwen AI):** The agent parses global RSS feeds using `news_scanner.py`. The text is passed to Alibaba’s Qwen AI, which acts as the "Brain". (e.g., During our live test of 'Mt. Gox Repayment News', Qwen instantly outputted a "BEARISH" decision with an impact score of 7, correctly diagnosing Extreme Fear liquidity cascades).
2. **On-Chain Signals (TVL Bank Run Detection):** The `market_monitor.py` continuously queries the DefiLlama API. If a protocol's TVL plummets >5% in 10 minutes, it flags a "Bank Run" and emits a SHORT signal.
3. **Technical Indicators:** Relying solely on news is dangerous. `signal_provider.py` pulls 15m Klines from Binance API. If an asset crashes and RSI drops below 25 (Extreme Oversold), it signals a potential technical bounce (successfully validated with real Binance BTCUSDT data during testing).
4. **Developer Activity:** The agent tracks GitHub repositories (`github_scanner.py`) to detect large code commits to core protocols before announcements. (In our live test, it successfully fetched 30 latest commits directly from the Uniswap/v4-core repository).

**Decision Making & Risk Management:**
Signals are routed through `trade_engine.py`. Maximum allocation per trade is strictly capped at 25% of the total portfolio. Position size is dynamically scaled based on Qwen's confidence and impact scores: `Risk = (Confidence / 100) * (Impact Score / 10) * Max_Risk`.

---

### 2. Progress
**Question:** Describe key development challenges and how you solved them. What features are completed, what is still missing, and what are the next steps? List the frameworks, models, and APIs used.
**Your Answer:**
**Development Challenges & Solutions:**
- **Challenge - The Qwen AI Bottleneck:** Hitting the Qwen AI endpoint frequently resulted in severe rate limiting or empty JSON responses during high volatility.
- **Solution - Graceful Fallback System:** We engineered a resilient fallback mechanism. If the AI endpoint fails, `news_scanner.py` gracefully degrades into a "dumb" router. It bypasses sentiment analysis and instantly broadcasts the raw breaking news directly to the Telegram UI, ensuring zero latency.
- **Challenge - NoneType API Errors:** During live testing, external APIs (like DefiLlama) occasionally returned `None` instead of numerical values for TVL, crashing the Bank-Run detector.
- **Solution:** We hardened the API ingress, ensuring strict float casting and defaulting `None` values to zero to prevent thread termination.

**Completed Features:**
- ✅ Autonomous Technical Signal Provider (RSI/Volume via Binance API)
- ✅ Autonomous Macro/News Analyzer (Qwen AI LLM)
- ✅ On-Chain TVL Bank-Run Tracker (DefiLlama API)
- ✅ Paper Trading Engine with Verifiable CSV Logging
- ✅ Comprehensive Test Suite (`system_execution.log`)

**Next Steps:** Move from `PAPER` mode directly to `REAL` mode using Bitget V2 Spot/Futures API keys, and integrate into the Bitget Agent Hub.

**Frameworks, Models, and APIs Used:**
- **AI Model:** Qwen-VL-Plus / Qwen-Max (Alibaba Cloud)
- **APIs:** Binance (Live Price/Klines), DefiLlama (TVL), GitHub REST API.
- **Frameworks:** Python `threading`, `telebot`.

---

### 3. AI Trading Thoughts (Optional)
**Question:** Share your experience using Bitget AI tools, suggestions for improvement, or your views on the future of Agentic Trading.
**Your Answer:**
Building Omen Protocol illuminated a profound shift: the future of Agentic Trading is **Multi-Modal Synthesis**. For years, quantitative trading was restricted to structured numeric data (OHLCV). Now, with tools like Qwen AI, an agent can "read" the market exactly like a human does—interpreting fear in a news headline and correlating it with a sudden drop in RSI. Bitget's extremely fast V2 APIs are vital for validation. Moving forward, the **Bitget Skill Hub** could be a game-changer. Instead of building custom REST wrappers for every on-chain endpoint, having pre-built "Skills" that agents can autonomously invoke would reduce development time by 90% and massively accelerate the adoption of autonomous trading architectures.

---

## 📌 Submission Links

### 【Required】 GitHub repo or MuleRun / GetAgent Studio link
**Your Answer:** 
https://github.com/Ahmetdenizyildiz/theomenprotocol

### 【Required】 Live trading record or paper trading log
**Your Answer:** 
*(Please provide the following two links which contain the required timestamp, pair, side, price, size, balance changes, and English system logs)*
1. **Paper Trading Logs:** https://github.com/Ahmetdenizyildiz/theomenprotocol/blob/main/trading_log.csv
2. **Comprehensive System Execution Logs (AI Reactions):** https://github.com/Ahmetdenizyildiz/theomenprotocol/blob/main/system_execution.log

### 【Optional】 Demo video (≤3 min)
**Your Answer:** 
*(Leave blank unless you recorded a video of the Telegram bot working)*
