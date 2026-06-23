FROM python:3.10-slim

# Gerekli sistem paketlerini yükle (Ses analizi için ffmpeg hayati önem taşır)
RUN apt-get update && apt-get install -y ffmpeg gcc && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm dosyaları kopyala
COPY . .

# Botu çalıştır
CMD ["python", "telegram_bot.py"]
