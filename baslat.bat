@echo off
chcp 65001 > nul
title OREM Yonetim Sistemi Baslatici

echo =======================================================
echo          OREM YONETIM SISTEMI BASLATILIYOR...
echo =======================================================
echo.

:: 1. Backend Baslat
echo [1/3] Backend API sunucusu baslatiliyor (Port 8000)...
start "OREM - Backend API" cmd /k "cd backend && venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 2. Frontend Baslat
echo [2/3] Frontend Vite sunucusu baslatiliyor (Port 5173)...
start "OREM - Frontend React" cmd /k "cd frontend && npm run dev -- --host 0.0.0.0"

:: 3. Cloudflare Tüneli (Mobil Giriş İçin)
echo [3/3] Mobil erisim baglantisi (Cloudflare Tunnel) hazirlaniyor...
echo.
echo =======================================================
echo Yerel Giris (Bilgisayar): http://localhost:5173
echo Varsayilan Giris: admin / admin123
echo =======================================================
echo.
echo Asagida Cloudflare tarafindan uretilen "https://....trycloudflare.com"
echo baglantisini kopyalayip telefonunuzun tarayicisindan girebilirsiniz:
echo.

cloudflared.exe tunnel --url http://localhost:5173
