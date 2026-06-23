import os
import json
from http_utils import get_session
from openai import OpenAI
from dotenv import load_dotenv

def get_fear_and_greed():
    try:
        session = get_session()
        r = session.get("https://api.alternative.me/fng/", timeout=5)
        data = r.json()
        val = data["data"][0]["value"]
        cls = data["data"][0]["value_classification"]
        return f"{val} ({cls})"
    except:
        return "Unknown"

def get_fng_value():
    try:
        session = get_session()
        r = session.get("https://api.alternative.me/fng/", timeout=5)
        data = r.json()
        return int(data["data"][0]["value"])
    except:
        return 50 # Default neutral


load_dotenv(override=True)

QWEN_API_KEY = os.getenv("QWEN_API_KEY")

def analyze_with_qwen(github_data, dao_data):
    """
    Sends the gathered GitHub and DAO data to Qwen AI and
    returns a BULLISH or BEARISH decision along with a confidence score.
    """
    print("[QWEN] Analyzing data...")
    
    if not QWEN_API_KEY:
        print("[ERROR] QWEN_API_KEY not found.")
        return None

    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url="https://hackathon.bitgetops.com/v1",
    )
    
    fng = get_fear_and_greed()
    
    system_prompt = (
        "You are a Senior Blockchain Developer and an expert Crypto Economist. "
        "You will be given the latest GitHub code updates of a project and the latest DAO voting proposal on Snapshot. "
        f"The current Global Crypto Market Sentiment (Fear & Greed Index) is: {fng}. Please consider this general market perception in your analysis.\n\n"
        "Your task is to review these two pieces of data and predict their impact on the project's token price. "
        "You must also evaluate how critical this development is with an Impact Score (impact_score) between 1 and 10.\n"
        "IMPORTANT - IMPACT SCORE RULES (Be Very Strict):\n"
        "- 1-3: Minor changes, ordinary code updates, simple DAO votes, routine analysis.\n"
        "- 4-6: Medium level news (e.g., minor exchange listings, testnet updates, medium scale votes).\n"
        "- 7-8: Very Big news (Mainnet launch, top 5 exchange listing, massive partnerships, decisions affecting millions in volume).\n"
        "- 9-10: Industry-shaking news (e.g., SEC ETF approval, $100M+ hack, arrest of a key leader).\n"
        "BITGET PLAYBOOK RULES: Do not just give a DIRECTION, you must provide a complete strategy (Execution Script) inside the 'playbook_strategy' object.\n"
        "Please reply ONLY in the following JSON format: "
        '{"decision": "BULLISH" | "BEARISH" | "NEUTRAL", "impact_score": 1-10, "confidence_score": 0-100, "reason": "A short English explanation", "catalyst_type": "Type of catalyst", "short_term": "Short-term impact (1-7 days) analysis", "medium_term": "Medium-term (1-3 months) analysis", "long_term": "Long-term (1 year+) analysis", "playbook_strategy": {"market_condition": "Trend / Ranging etc.", "trigger": "Entry Trigger", "risk_management": "Risk management rule", "exit_conditions": "Exit and Stop-Loss rule"}}'
    )
    
    user_content = f"""
    [GITHUB DATA]
    Repo: {github_data.get('repo')}
    Commits in Last 24 Hours: {github_data.get('new_commits')}
    Commit Messages:
    {github_data.get('commit_messages')}
    
    [DAO VOTING DATA]
    Project: {dao_data.get('space')}
    Proposal Title: {dao_data.get('title')}
    Current State: {dao_data.get('state')}
    Leading Choice (Expected to Win): {dao_data.get('winning_choice')}
    Proposal Summary: {dao_data.get('body')}
    """

    try:
        completion = client.chat.completions.create(
            model="qwen3.6-plus",
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
            ],
            response_format={"type": "json_object"}
        )
        
        result_json = completion.choices[0].message.content
        return json.loads(result_json)
        
    except Exception as e:
        print(f"[QWEN] Error occurred: {e}")
        return None

def analyze_news_with_qwen(news_text, image_b64=None):
    """
    Analyzes the Telegram news or image forwarded by the user, determines if it 
    affects any project globally, and finds the direction of the impact.
    If there is an image, it uses Qwen Vision (Multimodal).
    """
    print("[QWEN] Performing Universal News Analysis (Unlimited Sniper Mode)...")
    
    if not QWEN_API_KEY:
        print("[ERROR] QWEN_API_KEY not found.")
        return None

    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url="https://hackathon.bitgetops.com/v1",
    )
    
    fng = get_fear_and_greed()
    
    system_prompt = (
        "You are a Master Crypto Sniper and a Top Tier Global Macroeconomist. "
        "The user will send you breaking market news, war news, central bank (FED) decisions, global financial events, OR crypto charts/images. "
        "Your task: Analyze how this news or image will affect the crypto market. "
        "If the news is a macroeconomic or geopolitical event, predict where the capital will flow and determine the most logical crypto asset accordingly. "
        "MULTIMODAL RULES: If the user provides an image, look for coin tickers (e.g., BTC, ETH) inside the image. "
        "If they provide text along with the image, use the text as context/instructions to interpret the image. NEVER say 'coin not found' if you can read it from the chart! "
        "While doing this, specify very clearly which coin to choose and which direction (BULLISH/BEARISH).\n\n"
        f"The current Global Crypto Market Sentiment (Fear & Greed Index) is: {fng}. You must consider this general state of fear or greed in your analysis.\n\n"
        "IMPORTANT - IMPACT SCORE RULES (Be Extremely Ruthless and Realistic):\n"
        "When determining the Impact Score (1-10) of the given news on the chosen token's price, avoid exaggeration:\n"
        "- 1-3 Score: Ordinary political statements, insignificant economic data, journalist comments (CRITICAL: Analyzes by journalists/analysts like Wu Blockchain or ordinary news sharing NEVER shake the market, you MUST give them a max of 2 or 3 points!).\n"
        "- 4-6 Score: Medium level impacts (Regional crises, expected interest rate decisions, regulation rumors).\n"
        "- 7-8 Score: Giant Catalysts (Outbreak of a major war, surprise FED rate decision, global stock market crashes).\n"
        "- 9-10 Score: Historical Events (World war, Dollar losing its reserve currency status).\n\n"
        "BITGET PLAYBOOK RULES: State your decision as a strategy (Execution Script) in the 'playbook_strategy' object.\n"
        "Please write your macroeconomic interpretation in the 'macro_analysis' field and reply ONLY in the following JSON format: "
        '{"affected_symbol": "Most logical trade symbol (e.g., PAXGUSDT, BTCUSDT etc.)", "project_name": "Project or Coin Name", "decision": "BULLISH" | "BEARISH" | "NEUTRAL", "impact_score": 1-10, "confidence_score": 0-100, "macro_analysis": "Deep macroeconomic interpretation about the impact of global events on crypto and markets", "reason": "Clear reason for trade recommendation", "short_term": "Short-term expectation", "medium_term": "Medium-term expectation", "long_term": "Long-term expectation", "playbook_strategy": {"market_condition": "Compatible market scenario", "trigger": "Trade Entry trigger", "risk_management": "Capital/Risk management", "exit_conditions": "Stop-Loss and Take-Profit targets"}}'
    )
    
    if image_b64:
        text_prompt = f"Context/Instruction from user:\n{news_text}\n\nPlease analyze this image." if news_text else "Please analyze this crypto chart or image, identify the coin, and provide a trading playbook."
        user_content = [
            {"type": "text", "text": text_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    else:
        user_content = f"BREAKING NEWS:\n{news_text}"

    try:
        model_name = "qwen-vl-plus" if image_b64 else "qwen3.6-plus"
        
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
            ],
            response_format={"type": "json_object"}
        )
        raw_content = completion.choices[0].message.content or ""
        json_str = ""
        if raw_content:
            # En sağlam JSON çıkartma yöntemi (İlk '{' ve son '}' arasını al)
            start_idx = raw_content.find('{')
            end_idx = raw_content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = raw_content[start_idx:end_idx+1]
            else:
                json_str = raw_content
                
        if not json_str.strip():
            return {"error": "EMPTY_RESPONSE", "details": "Qwen returned an empty response (probably timeout or API blockage).", "raw": raw_content}
            
        try:
            return json.loads(json_str)
        except Exception as json_e:
            return {"error": "JSON_DECODE_ERROR", "details": str(json_e), "raw": raw_content}
            
    except Exception as e:
        print(f"[QWEN] News Analysis error: {e}")
        return {"error": "API_ERROR", "details": str(e)}

def analyze_document_with_qwen(doc_text):
    """
    Deeply analyzes document (PDF/TXT) contents. Extracts risks and opportunities 
    from Tokenomics, lawsuit documents, whitepapers, or research reports.
    """
    print("[QWEN] Document Sniper activated...")
    
    if not QWEN_API_KEY:
        print("[ERROR] QWEN_API_KEY not found.")
        return None

    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url="https://hackathon.bitgetops.com/v1",
    )
    
    fng = get_fear_and_greed()
    
    system_prompt = (
        "You are a Top Tier Crypto Auditor and Institutional Researcher. "
        "You will be given the content of a PDF or text file (e.g., SEC Lawsuit file, Whitepaper, Tokenomics report). "
        "Your task is to read between the lines, find its impact on the project or the market, and detect hidden red flags or massive opportunities. "
        "Focus especially on vesting cliffs, inflation rates, or legal sanctions.\n\n"
        f"Current Market Sentiment: {fng}. Evaluate this in your analysis.\n\n"
        "BITGET PLAYBOOK RULES: Materialize the opportunities you see under 'playbook_strategy' (Execution Script).\n"
        "Please reply ONLY in the following JSON format: "
        '{"affected_symbol": "Exchange trading symbol (e.g., SOLUSDT) or null", "project_name": "Project or Coin Name", "decision": "BULLISH" | "BEARISH" | "NEUTRAL", "impact_score": 1-10, "confidence_score": 0-100, "macro_analysis": "Hidden dangers or massive opportunities in the document (Tokenomics risks etc.)", "reason": "Summary finding", "short_term": "Short-term expectation", "medium_term": "Medium-term expectation", "long_term": "Long-term expectation", "playbook_strategy": {"market_condition": "Market structure compatible with the situation in the document", "trigger": "Trade Entry trigger", "risk_management": "Capital/Risk management", "exit_conditions": "Stop-loss and Take-profit rules"}}'
    )
    
    try:
        completion = client.chat.completions.create(
            model="qwen3.6-plus",
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"DOCUMENT CONTENT:\n\n{doc_text[:30000]}"} # Limit text to roughly 30k chars
            ],
            response_format={"type": "json_object"}
        )
        
        result_json = completion.choices[0].message.content
        return json.loads(result_json)
        
    except Exception as e:
        print(f"[QWEN] Document Analysis error: {e}")
        return None

if __name__ == "__main__":
    # Test data
    mock_github = {
        "repo": "Uniswap/v4-core",
        "new_commits": 3,
        "commit_messages": "- feat: add hook support\n- fix: gas optimization\n- docs: update readme for v4 release"
    }
    mock_dao = {
        "space": "uniswap.eth",
        "title": "Deploy Uniswap V4 on Ethereum Mainnet",
        "state": "active",
        "winning_choice": "Yes, deploy V4",
        "body": "This proposal authorizes the deployment of Uniswap V4..."
    }
    print("Normal Analysis:", analyze_with_qwen(mock_github, mock_dao))
    
    print("Unlimited Sniper Analysis:", analyze_news_with_qwen("BREAKING: Solana Foundation announces direct partnership with Visa for instant USDC settlements globally!"))
