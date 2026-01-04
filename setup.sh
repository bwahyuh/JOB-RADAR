#!/bin/bash

echo "🚀 Memulai Setup Job Radar ID..."

# 1. Cek apakah venv sudah ada
if [ -d "venv" ]; then
    echo "✅ Virtual Environment ditemukan."
else
    echo "📦 Membuat Virtual Environment baru..."
    python3 -m venv venv
fi

# 2. Aktifkan Venv
source venv/bin/activate

# 3. Install Dependencies
echo "⬇️  Menginstall Dependencies dari requirements.txt..."
pip install -r requirements.txt

echo "🎉 Setup Selesai! Jalankan 'source venv/bin/activate' untuk masuk."