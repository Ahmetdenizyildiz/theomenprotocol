import sys
import json
import warnings
warnings.filterwarnings("ignore")

from qwen_brain import analyze_news_with_qwen, analyze_document_with_qwen

def print_result(title, result):
    print(f"\n{'='*70}\n{title}\n{'='*70}")
    if result:
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print("NO RESULT OR ERROR")

print("🚀 BÜTÜN YETKİ BENDE: Omni-Alpha Otonom Testleri Başlıyor...\n")

# Test 1: Dev Makroekonomik Haber
news1 = "BREAKING: Federal Reserve announces a surprise 50 bps interest rate cut citing slowing inflation and rising unemployment. Meanwhile, Binance cold wallets just transferred 10,000 ETH to their hot wallets."
res1 = analyze_news_with_qwen(news1)
print_result("TEST 1: Makroekonomik Şok Haberi\n(Beklenti: Yüksek Etki Puanı, Kapsamlı Playbook Stratejisi)", res1)

# Test 2: Muhabir Sansürü (Wu Blockchain) Testi
news2 = "Wu Blockchain reports that a minor developer in the Ethereum ecosystem bought a new house."
res2 = analyze_news_with_qwen(news2)
print_result("TEST 2: Gazeteci/Muhabir Manipülasyonu\n(Beklenti: Düşük Etki Puanı (1-3), Pas Geçilecek İşlem)", res2)

# Test 3: Gizli Belge (Document Sniper) Testi
doc_text = "CONFIDENTIAL: The founding team has decided to bypass the vesting schedule. Tomorrow at 12:00 PM UTC, 45% of the total token supply will be unlocked and distributed directly to early VCs and team members."
res3 = analyze_document_with_qwen(doc_text)
print_result("TEST 3: Gizli Tokenomics Belgesi Sızıntısı\n(Beklenti: Dev Düşüş Sinyali (BEARISH), Short/Satış Stratejisi)", res3)

print("\n✅ Tüm testler başarıyla tamamlandı!")
