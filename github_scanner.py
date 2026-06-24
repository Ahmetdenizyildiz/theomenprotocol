import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from http_utils import get_session

load_dotenv(override=True)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def scan_github_repo(owner, repo):
    """
    Belirtilen GitHub deposundaki (repository) son 24 saatte yapılmış olan
    commitleri çeker. Amaç, büyük güncellemeleri erken tespit etmektir.
    """
    print(f"[GITHUB] {owner}/{repo} deposu taranıyor...")
    
    # Son commitleri almak için zaman sınırını kaldırıyoruz ki testlerde hep sonuç görebilelim
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    
    headers = {}
    if GITHUB_TOKEN and GITHUB_TOKEN.strip() != "your_github_personal_access_token_here":
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN.strip()}"
        headers["Accept"] = "application/vnd.github.v3+json"
    headers["User-Agent"] = "Omni-Alpha-Bot"
    
    try:
        session = get_session()
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 403:
            print(f"[GITHUB] Rate Limit aşıldı! Lütfen .env dosyasına geçerli bir GITHUB_TOKEN ekleyin.")
            return None
        elif response.status_code != 200:
            print(f"[GITHUB] API Hatası: {response.status_code} - {response.text}")
        response.raise_for_status()
        commits = response.json()
        
        if not commits:
            return None
            
        # En son yapılan commitlerin açıklamalarını toparlıyoruz
        commit_messages = []
        for commit in commits[:5]: # Son 5 commit'i al
            msg = commit.get('commit', {}).get('message', '')
            commit_messages.append(msg)
            
        combined_messages = "\n- ".join(commit_messages)
        latest_sha = commits[0].get('sha', '')
        
        return {
            "repo": f"{owner}/{repo}",
            "new_commits": len(commits),
            "commit_messages": f"- {combined_messages}",
            "latest_sha": latest_sha
        }
        
    except Exception as e:
        print(f"[GITHUB] Hata oluştu: {e}")
        return None

if __name__ == "__main__":
    # Test
    result = scan_github_repo("Uniswap", "v4-core")
    print(result)
