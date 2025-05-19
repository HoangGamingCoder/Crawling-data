FROM python:3.10-slim

# Tạo thư mục làm việc
WORKDIR /app

# Copy mã nguồn và requirements
COPY . /app

# Cài đặt thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Expose cổng 5001
EXPOSE 5001

# Chạy FastAPI bằng uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
