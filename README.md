# FoodHub: Sistem Pemesanan Makanan Berbasis Microservices

FoodHub adalah aplikasi pemesanan makanan yang dibangun menggunakan arsitektur microservices. Sistem ini terdiri dari 3 service utama yang masing-masing berjalan secara independen dan memiliki database sendiri, serta berkomunikasi via REST API yang dirutekan melalui sebuah API Gateway.

## 🛠 Tech Stack

Proyek ini menggunakan teknologi berikut:
- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: MySQL (Setiap service memiliki database mandiri)
- **ORM**: SQLAlchemy
- **Autentikasi**: JWT (menggunakan `python-jose` + `passlib`)
- **Dokumentasi API**: Swagger UI (Built-in dari FastAPI)
- **Containerisasi**: Docker & Docker Compose
- **HTTP Client**: HTTPX (Untuk komunikasi antar microservices & Gateway)

## 📁 Struktur Folder

Proyek ini dibagi menjadi beberapa service yang independen:

```text
FoodHub/
├── docker-compose.yml       # Konfigurasi Docker Compose untuk seluruh infrastruktur
├── .env                     # File environment variabel global
├── mysql-init/
│   └── init.sql             # Script SQL otomatis untuk membuat 3 database terpisah
├── api-gateway/             # (Port 8000) Gateway untuk routing request
│   ├── main.py              
│   ├── requirements.txt
│   └── Dockerfile
├── user-service/            # (Port 8001) Service untuk User & Autentikasi JWT
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── auth.py
│   ├── requirements.txt
│   └── Dockerfile
├── menu-service/            # (Port 8002) Service untuk CRUD Kategori & Menu
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── requirements.txt
│   └── Dockerfile
└── order-service/           # (Port 8003) Service untuk Pembuatan Pesanan
    ├── main.py
    ├── models.py
    ├── schemas.py
    ├── database.py
    ├── requirements.txt
    └── Dockerfile
```

## 🚀 Cara Menjalankan Project

### Prasyarat:
Pastikan Anda sudah menginstal:
1. **Docker Desktop** (Pastikan statusnya *Running* / berjalan)
2. Jika menggunakan Windows, pastikan **WSL 2** sudah terinstal.

### Langkah-langkah Menjalankan:

1. Clone atau buka folder project ini di terminal VS Code Anda.
2. Jalankan perintah Docker Compose berikut untuk melakukan build dan menyalakan semua service:
   ```bash
   docker-compose up -d --build
   ```
3. Tunggu hingga proses build selesai. Docker akan otomatis men-download image MySQL dan Python, menginisialisasi database, dan menjalankan ke-4 service FastAPI secara bersamaan.

### 🌐 Mengakses API dan Dokumentasi (Swagger UI)

Setelah semua kontainer berstatus *Running*, Anda bisa mengakses dokumentasi API dari masing-masing service di browser:

- **API Gateway (Titik Akses Utama)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **User Service (Database: `user_db`)**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Menu Service (Database: `menu_db`)**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **Order Service (Database: `order_db`)**: [http://localhost:8003/docs](http://localhost:8003/docs)

### Cara Menghentikan Project
Untuk mematikan semua service, jalankan:
```bash
docker-compose down
```
Jika ingin mereset database beserta isinya, gunakan:
```bash
docker-compose down -v
```
