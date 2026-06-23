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
