import json
from github_scanner import scan_github_repo
from dao_scanner import scan_dao_proposals
from trade_engine import get_current_price

print("--- GITHUB TEST ---")
gh = scan_github_repo("Uniswap", "v4-core")
print(json.dumps(gh, indent=2, ensure_ascii=False))

print("\n--- DAO TEST ---")
dao = scan_dao_proposals("uniswap.eth")
print(json.dumps(dao, indent=2, ensure_ascii=False))

print("\n--- PRICE TEST ---")
price = get_current_price("UNIUSDT")
print(f"UNI/USDT Fiyatı: {price}")
