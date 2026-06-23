import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_session = None

def get_session():
    """
    Tüm projedeki API istekleri için tek bir Bağlantı Havuzu (Connection Pool) döndürür.
    429 (Too Many Requests), 500, 502, 503, 504 hatalarında otomatik tekrar dener.
    """
    global _session
    if _session is None:
        _session = requests.Session()
        
        # Yeniden deneme (Retry) stratejisi oluştur:
        # backoff_factor=1 demek: 1s, 2s, 4s, 8s şeklinde bekler.
        # toplam 3 kere dener.
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
        
    return _session

def fetch_url_text(url):
    """
    Verilen URL'nin içeriğini BeautifulSoup ile kazır.
    """
    from bs4 import BeautifulSoup
    try:
        session = get_session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Gereksiz etiketleri kaldır (script, style vb.)
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        # Sadece ilk 8000 karakteri al ki Qwen limiti aşılmasın
        return text[:8000]
    except Exception as e:
        print(f"[HTTP Utils] fetch_url_text error for {url}: {e}")
        return None
