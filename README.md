
# 🚗 Chotot Car Crawler - Dự án Thu thập Dữ liệu Xe từ Chotot.com

Dự án này giúp tự động thu thập dữ liệu xe ô tô từ trang [chotot.com](https://www.chotot.com), lưu trữ vào cơ sở dữ liệu MySQL, đồng thời cung cấp giao diện web đơn giản để hiển thị dữ liệu. Hệ thống được container hóa bằng Docker để dễ triển khai và mở rộng.

---

## 📦 Cấu trúc thư mục chính

```
CRAWLING-DATA/
│
├── api-gateway/              # (Tuỳ chọn) Cổng API để truy cập dữ liệu tập trung
│   ├── Dockerfile            # Dockerfile cho api-gateway
│   ├── nginx.conf            # Cấu hình nginx cho api-gateway
│
├── data_crawling/            # Script crawl dữ liệu từ Chotot
│   ├── __pycache__/          # Cache Python
│   ├── app.py                # Script chính crawl dữ liệu
│   ├── data_crawling.log     # File log của quá trình crawl
│   ├── Dockerfile            # Dockerfile cho data_crawling
│   ├── requirements.txt      # Thư viện Python cho crawling
│   └── scheduler.py          # Script scheduler chạy crawl định kỳ
│
├── data_ingestion/           # Xử lý và lưu dữ liệu vào database
│   ├── app.py                # Script xử lý dữ liệu, đẩy vào DB
│   ├── Dockerfile            # Dockerfile cho data_ingestion
│   └── requirements.txt      # Thư viện Python cho ingestion
│
├── database-api/             # API truy vấn cơ sở dữ liệu
│   ├── app.py                # Flask/FastAPI app để query DB
│   ├── Dockerfile            # Dockerfile cho database-api
│   └── requirements.txt      # Thư viện cho database-api
│
├── init_db/
│   └── init.sql              # Script tạo bảng và dữ liệu mẫu cho MySQL
│
├── landing-zone/
│   ├── data.json             # Dữ liệu JSON tạm thời sau khi crawl
│   └── last_hash.txt         # Ghi hash dữ liệu cuối cùng để tránh trùng lặp
│
├── mysql_data/               # Volume dữ liệu MySQL (tự động tạo khi chạy container)
│
├── web-page/                 # Giao diện web hiển thị dữ liệu
│   ├── static/
│   │   └── style.css         # CSS cho giao diện
│   ├── templates/
│   │   └── index.html        # Giao diện HTML hiển thị dữ liệu
│   ├── app.py                # Flask web app
│   └── requirements.txt      # Thư viện cho Flask web-page
│
├── Dockerfile                # Dockerfile build app tổng thể
├── docker-compose.yml        # Cấu hình Docker Compose để chạy đa container
├── requirements.txt          # Thư viện chung cho crawler và ingestion
└── README.md                 # Hướng dẫn sử dụng dự án
```

---

## ⚙️ Công nghệ sử dụng

- **Python 3.10**
- **Requests** – Crawl dữ liệu
- **FlaskApi** – Giao diện web
- **MySQL** – Cơ sở dữ liệu lưu trữ
- **Docker, Docker Compose** – Triển khai

---

## 🚀 Cách sử dụng

### 1. Cài đặt Docker & Docker Compose

> Yêu cầu cài đặt: [Docker](https://www.docker.com/products/docker-desktop)

### 2. Build và chạy toàn bộ hệ thống

```bash
docker-compose up --build
```

Docker Compose sẽ tự động:
- Build image cho Flask Web và service crawl
- Khởi tạo container MySQL, chạy `init.sql`
- Tạo dữ liệu trong MySQL
- Chạy giao diện web tại `http://localhost:5000`

---

## 🌐 Truy cập

- Web hiển thị dữ liệu: [http://localhost:5000](http://localhost:5000)
- MySQL container: `localhost:3306` (user: `root`, password: ``)

---

## 🧪 Thao tác thủ công

### Crawl dữ liệu

```bash
python data_crawling/chotot_car.py
```

### Ingest dữ liệu vào MySQL

```bash
python data_ingestion/load_data.py
```

---

## 🛑 Dừng hệ thống

```bash
docker-compose down
```

---

## ✅ TODO

- [ ] Thêm bộ lọc dữ liệu theo khu vực/loại xe/tìm kiếm
- [ ] Lưu log crawl định kỳ
- [ ] Triển khai API Gatewa

---

## 📄 Giấy phép

Dự án phục vụ **mục đích học tập, nghiên cứu**. Không sử dụng cho mục đích thương mại.

---

## 📧 Liên hệ

**Author:** [Your Name]  
📩 Email: your.email@example.com  
🌐 Github: [your-github-link]
