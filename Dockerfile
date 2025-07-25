FROM python:3.10-slim

# Tạo thư mục làm việc trong container
WORKDIR /app

# Copy requirements trước để tận dụng cache Docker tốt hơn
COPY requirements.txt .

# Cài thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào thư mục /app
COPY . .

# Chạy bot
CMD ["python", "bot.py"]
