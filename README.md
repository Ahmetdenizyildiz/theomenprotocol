# Omni-Alpha Trading Agent 🚀 
[![Bitget AI Hackathon](https://img.shields.io/badge/Bitget_AI-Hackathon-blue.svg)](https://bitget-ai.gitbook.io/hackathon)

*An autonomous AI Trading Agent that reads the market like a whale and acts like a sniper.*

## 1. Project Thesis
Omni-Alpha is an autonomous Trading Agent built for the **Bitget AI Agent Hackathon (Track 1: Trading Agent)**. 
Unlike traditional quantitative bots that rely on static technical indicators, Omni-Alpha leverages Large Language Models (Alibaba Qwen) to truly "understand" market sentiment, global macroeconomic events, on-chain whale activity, and GitHub/DAO developments. 
It processes multimodal inputs (News, Voice, Images, PDFs) and generates actionable **Playbook Strategies** consisting of market conditions, entry triggers, and strict risk management.

## 2. Completeness (Architecture)
The bot operates 24/7 in a complete autonomous loop without human intervention.
- **Perception Layer:**
  - `market_monitor.py`: Scans for DeFi Bank Runs & Smart Money Anomalies.
  - `onchain_analyzer.py`: Monitors real-time whale transactions via Etherscan API.
  - `github_scanner.py` & `dao_scanner.py`: Tracks protocol updates and governance.
- **Brain Layer (`qwen_brain.py`):**
  - Consumes the data alongside the real-time Fear & Greed Index.
  - Generates a "Playbook Strategy" JSON (Market Condition, Trigger, Risk, Stop Loss).
- **Execution Layer (`trade_engine.py`):**
  - Evaluates Qwen's `confidence_score` and `impact_score`.
  - Determines position size algorithmically (Kelly-criterion style).
  - Executes the paper trade and logs it to `trading_log.csv` for verifiable usage records.

## 3. Runnability (How to Install & Run)
You can run this project locally or deploy it on a free VPS (like Oracle Cloud).

### Prerequisites
- Python 3.10+
- `ffmpeg` (for voice processing)
- Telegram Bot Token
- Alibaba Qwen API Key (via Bitget Hackathon proxy)
- Etherscan API Key (Optional, for real-time whale tracking)

### Installation
```bash
git clone https://github.com/yourusername/omni-alpha-agent.git
cd omni-alpha-agent
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
QWEN_API_KEY="your_qwen_api_key_here"
ETHERSCAN_API_KEY="your_etherscan_key_here"
TRADING_MODE="PAPER"
```

### Run the Agent
```bash
python telegram_bot.py
```
> **Tip for 24/7 Execution:** Use `nohup python telegram_bot.py &` or `tmux` to keep the bot running in the background even after you close your terminal. Oracle Cloud's "Always Free" tier is highly recommended for hosting.

## 4. Novelty & Potential
Omni-Alpha goes beyond simple trading:
- **Auto-Hedge Shield:** It automatically suggests opening short positions or buying Gold (PAXG) when the Fear & Greed Index drops to extreme levels (< 25).
- **Document Sniper:** You can send it SEC lawsuit PDFs or 50-page Whitepapers, and it will instantly extract the tokenomics red flags or legal risks.
- **Multimodal News Processing:** Send a screenshot of a breaking news tweet or a voice note, and Qwen Vision/Audio will instantly formulate a trade.

## Verifiable Usage Record
The agent includes a built-in `trade_engine.py` that logs all autonomous paper trades into a `trading_log.csv` file, proving end-to-end execution capability to the Hackathon Judges.
