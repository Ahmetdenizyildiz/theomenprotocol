from http_utils import get_session

def scan_dao_proposals(space_id):
    """
    Snapshot.org üzerinden belirtilen projenin (space) en güncel aktif veya yeni bitmiş
    tekliflerini çeker.
    Örnek space_id: 'uniswap.eth'
    """
    print(f"[DAO] Snapshot '{space_id}' teklifleri taranıyor...")
    
    url = "https://hub.snapshot.org/graphql"
    
    # GraphQL sorgusu: Belirtilen space'teki son 2 teklifi çeker
    query = """
    query Proposals($space: String!) {
      proposals(
        first: 2,
        skip: 0,
        where: {
          space: $space
        },
        orderBy: "created",
        orderDirection: desc
      ) {
        id
        title
        body
        state
        created
        choices
        scores
        scores_total
      }
    }
    """
    
    variables = {
        "space": space_id
    }
    
    try:
        session = get_session()
        response = session.post(url, json={'query': query, 'variables': variables}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        proposals = data.get('data', {}).get('proposals', [])
        
        if not proposals:
            return None
            
        # En son teklifi doğrudan al, zaman sınırı koyma
        recent_proposals = proposals
        
        if not recent_proposals:
            return None
            
        latest_proposal = recent_proposals[0]
        
        # En çok oy alan seçeneği bul
        scores = latest_proposal.get('scores', [])
        choices = latest_proposal.get('choices', [])
        
        winning_choice = "Henüz Oy Yok"
        if scores and sum(scores) > 0:
            max_index = scores.index(max(scores))
            if max_index < len(choices):
                winning_choice = choices[max_index]
        
        return {
            "id": latest_proposal.get('id'),
            "space": space_id,
            "title": latest_proposal.get('title'),
            "body": latest_proposal.get('body')[:500] + "...", # Sadece ilk 500 karakteri al
            "state": latest_proposal.get('state'),
            "winning_choice": winning_choice
        }
        
    except Exception as e:
        print(f"[DAO] Hata oluştu: {e}")
        return None

if __name__ == "__main__":
    # Test
    result = scan_dao_proposals("uniswap.eth")
    print(result)
