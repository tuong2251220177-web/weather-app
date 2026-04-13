# LAB 2. ĐÓNG GÓI ỨNG DỤNG WEATHER BẰNG DOCKER VÀ CHẠY TRÊN VPS

## 3.1. Mục tiêu

Sau lab này, học viên sẽ:

* Biết viết `Dockerfile` cho ứng dụng Python FastAPI
* Biết build image từ source code trên máy local
* Biết đẩy image lên Docker Hub
* Biết kéo image về VPS và chạy container
* Hiểu lợi ích của việc **build ở local, run ở server**

---

## 3.2. Ý tưởng trước khi làm

Ở Lab 1, VPS phải tự:

* cài Python
* cài pip
* tạo virtual environment
* cài các thư viện bằng `pip install`
* chạy app bằng PM2

Điều này dẫn đến:

* máy chủ dễ bị lẫn nhiều môi trường
* khó đồng nhất giữa local và server
* dễ phát sinh lỗi do khác phiên bản Python hoặc thư viện

Với Docker:

* toàn bộ môi trường chạy được đóng gói thành **image**
* VPS chỉ cần kéo image về và chạy
* môi trường nhất quán hơn giữa local và production

---

## 3.3. Bước 1: Tạo Dockerfile trên máy local

Trên máy tính cá nhân, mở thư mục source code của project weather và tạo file tên:

```text
Dockerfile
```

Dán nội dung sau:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3.4. Giải thích từng dòng Dockerfile

### Dòng 1

```dockerfile
FROM python:3.11-slim
```

Dùng image nền là Python 3.11 bản slim, nhẹ hơn bản full.

### Dòng 2

```dockerfile
WORKDIR /app
```

Tạo thư mục làm việc bên trong container là `/app`.

### Dòng 3-4

```dockerfile
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
```

Copy file khai báo thư viện vào trước, sau đó cài dependencies.

### Dòng 5

```dockerfile
COPY . .
```

Copy toàn bộ source code còn lại vào container.

### Dòng 6

```dockerfile
EXPOSE 8000
```

Khai báo ứng dụng chạy ở cổng `8000`.

### Dòng 7

```dockerfile
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Lệnh mặc định để container khởi chạy ứng dụng FastAPI.

---

## 3.5. Bước 2: Tạo file requirements.txt

Nếu project chưa có file `requirements.txt`, hãy tạo file này trong thư mục gốc:

```txt
fastapi
uvicorn
jinja2
requests
```

---

## 3.6. Bước 3: Đăng nhập Docker Hub trên máy local

Mở terminal tại thư mục source code và chạy:

```bash
docker login
```

Nhập:

* Docker Hub username
* Docker Hub password

### Kết quả mong đợi

Hiển thị:

```text
Login Succeeded
```

---

## 3.7. Bước 4: Build Docker image

Chạy lệnh:

```bash
docker build -t <your_dockerhub_username>/weather-fastapi:v1.0.0 .
```

Ví dụ:

```bash
docker build -t dungpham/weather-fastapi:v1.0.0 .
```

### Lưu ý quan trọng

Dấu chấm `.` ở cuối lệnh là bắt buộc.
Nó đại diện cho thư mục hiện tại, nơi chứa source code và `Dockerfile`.

### Kết quả mong đợi

Build thành công và tạo image mới trên máy local.

### Kiểm tra image

```bash
docker images
```

Bạn sẽ thấy image dạng:

```text
dungpham/weather-fastapi   v1.0.0
```

---

## 3.8. Bước 5: Push image lên Docker Hub

Chạy:

```bash
docker push <your_dockerhub_username>/weather-fastapi:v1.0.0
```

Ví dụ:

```bash
docker push dungpham/weather-fastapi:v1.0.0
```

### Kết quả mong đợi

Image được tải lên Docker Hub thành công.

---

## 3.9. Bước 6: Chuẩn bị VPS để chạy Docker

SSH lại vào VPS:

```bash
ssh root@<IP_VPS_CUA_BAN>
```

Nếu trước đó app đang chạy bằng PM2 ở cổng `8000`, cần dừng app:

```bash
pm2 stop weather-fastapi
```

Hoặc nếu muốn xóa hẳn:

```bash
pm2 delete weather-fastapi
pm2 save
```

Cài Docker trên VPS:

```bash
apt update
apt install docker.io -y
```

### Kiểm tra Docker

```bash
docker --version
```

---

## 3.10. Bước 7: Kéo image từ Docker Hub về VPS

Chạy:

```bash
docker pull <your_dockerhub_username>/weather-fastapi:v1.0.0
```

Ví dụ:

```bash
docker pull dungpham/weather-fastapi:v1.0.0
```

### Kết quả mong đợi

Image được tải về VPS thành công.

### Kiểm tra

```bash
docker images
```

---

## 3.11. Bước 8: Chạy container

Chạy:

```bash
docker run -d -p 80:8000 --name weather-app-container <your_dockerhub_username>/weather-fastapi:v1.0.0
```

Ví dụ:

```bash
docker run -d -p 80:8000 --name weather-app-container dungpham/weather-fastapi:v1.0.0
```

### Giải thích

* `-d`: chạy nền
* `-p 80:8000`: ánh xạ cổng `80` của VPS tới cổng `8000` trong container
* `--name`: đặt tên container là `weather-app-container`

### Kết quả mong đợi

Một chuỗi ID container được in ra.

---

## 3.12. Bước 9: Kiểm tra container đang chạy

```bash
docker ps
```

### Kết quả mong đợi

Bạn thấy container `weather-app-container` ở trạng thái `Up`.

Mở trình duyệt và truy cập:

```text
http://<IP_VPS_CUA_BAN>
```

Lần này không cần thêm `:8000` vì đang map cổng `80`.

---

## 3.13. Nếu không truy cập được từ trình duyệt

Có thể firewall trên VPS chưa mở cổng `80`.

Nếu dùng UFW:

```bash
ufw allow 80
ufw enable
ufw status
```

Sau đó truy cập lại:

```text
http://<IP_VPS_CUA_BAN>
```

---

## 3.14. Một số lệnh Docker quan trọng

### Xem container đang chạy

```bash
docker ps
```

### Xem tất cả container

```bash
docker ps -a
```

### Xem log container

```bash
docker logs weather-app-container
```

### Dừng container

```bash
docker stop weather-app-container
```

### Chạy lại container đã dừng

```bash
docker start weather-app-container
```

### Xóa container

```bash
docker rm weather-app-container
```

### Xóa image

```bash
docker rmi <your_dockerhub_username>/weather-fastapi:v1.0.0
```

Ví dụ:

```bash
docker rmi dungpham/weather-fastapi:v1.0.0
```

---

## 3.15. Cấu trúc project mẫu

```text
weather-app/
├── main.py
├── requirements.txt
├── Dockerfile
└── templates/
    └── index.html
```

---

## 3.16. Quy trình đầy đủ từ local đến VPS

### Trên máy local

```bash
docker login
docker build -t <your_dockerhub_username>/weather-fastapi:v1.0.0 .
docker push <your_dockerhub_username>/weather-fastapi:v1.0.0
```

### Trên VPS

```bash
ssh root@<IP_VPS_CUA_BAN>
apt update
apt install docker.io -y
docker pull <your_dockerhub_username>/weather-fastapi:v1.0.0
docker run -d -p 80:8000 --name weather-app-container <your_dockerhub_username>/weather-fastapi:v1.0.0
docker ps
```

---

## 3.17. Kết luận Lab 2

Học viên hiểu được:

* Docker giúp đóng gói ứng dụng FastAPI và môi trường chạy thành một đơn vị thống nhất
* VPS không cần cài Python, pip hay virtualenv cho từng project
* Triển khai bằng image giúp dễ quản lý phiên bản hơn
* Có thể build ở local rồi chạy ở bất kỳ VPS nào có Docker

---

## 3.19. Bonus: thêm file .dockerignore

Để image gọn hơn, bạn nên tạo thêm file:

```text
.dockerignore
```

Nội dung:

```text
venv
__pycache__
.git
.gitignore
*.pyc
*.pyo
*.pyd
.env
```

File này giúp Docker không copy các thư mục và file không cần thiết vào image.
