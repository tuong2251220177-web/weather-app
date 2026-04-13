# TÀI LIỆU THỰC HÀNH CHI TIẾT

**Chủ đề:** Deploy ứng dụng Python FastAPI từ thủ công đến CI/CD

---

## Mục tiêu chung

Sau khi hoàn thành 3 bài lab này, học viên sẽ:

- Hiểu cách đưa một ứng dụng Python FastAPI lên VPS theo cách thủ công.
- Biết vì sao ứng dụng bị dừng khi đóng terminal và cách xử lý bằng Systemd.
- Biết cách đóng gói ứng dụng bằng Docker để triển khai nhất quán hơn.
- Biết cách tự động hóa build và deploy bằng GitHub Actions.
- Làm quen với quy trình rollback khi phiên bản mới gặp lỗi.

## Ứng dụng mẫu dùng trong toàn bộ bài lab

Toàn bộ bài thực hành sử dụng một ứng dụng mẫu:

- Viết bằng **Python + FastAPI + Uvicorn**
- Chạy trên cổng **8000**
- Cung cấp 3 tính năng chính:
  - Trang chủ: `/`
  - Xem thời tiết các thành phố Việt Nam: `/thoi-tiet`
  - Xem tỷ giá ngoại tệ so với VND: `/ty-gia`
- Hệ điều hành máy chủ là **Ubuntu**
- Source code được lưu trên **GitHub** cá nhân

---

## PHẦN 1. CHUẨN BỊ MÔI TRƯỜNG

### 1.1. Yêu cầu trước khi bắt đầu

Mỗi học viên cần chuẩn bị sẵn:

**Trên máy cá nhân:**

- Một máy tính có kết nối Internet
- Có cài Terminal:
  - Windows: PowerShell hoặc Windows Terminal
  - macOS/Linux: Terminal mặc định
- Có tài khoản GitHub
- Có tài khoản Docker Hub
- Có cài Git
- Có cài Docker Desktop nếu làm Lab 2 và Lab 3

**Trên máy chủ:**

- Một VPS Ubuntu (khuyến nghị Ubuntu 22.04)
- Biết các thông tin:
  - IP VPS
  - username đăng nhập: `root`
  - mật khẩu hoặc SSH Key

**Source code mẫu:**

Trên GitHub cần có một repository, ví dụ:

```
https://github.com/your-username/weather-fastapi.git
```

Trong repository tối thiểu cần có:

- `main.py`
- `requirements.txt`
- `templates/` (chứa các file HTML: `index.html`, `weather.html`, `exchange.html`)

Ví dụ nội dung file `main.py` (phiên bản rút gọn):

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI(title="Weather Vietnam App")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})
```

Ví dụ nội dung file `requirements.txt`:

```
fastapi
uvicorn
jinja2
requests
```

---

## LAB 1. DEPLOY THỦ CÔNG VÀ QUẢN LÝ TIẾN TRÌNH BẰNG SYSTEMD

### 2.1. Mục tiêu

Sau lab này, học viên sẽ:

- SSH được vào VPS
- Cài được Python 3, pip, Git
- Clone code từ GitHub về VPS
- Tạo được môi trường ảo (virtual environment)
- Chạy được ứng dụng FastAPI bằng Uvicorn
- Hiểu vấn đề khi chạy app trực tiếp bằng terminal
- Dùng Systemd để giữ app chạy nền ngay cả khi ngắt kết nối SSH

---

### 2.2. Bước 1: SSH vào VPS

Trên máy cá nhân, mở Terminal và chạy:

```bash
ssh root@<IP_VPS_CUA_BAN>
```

Ví dụ:

```bash
ssh root@192.168.1.100
```

Nếu hiện thông báo:

```
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Gõ `yes`, sau đó nhập mật khẩu VPS.

> **Kết quả mong đợi:** Bạn đăng nhập thành công vào VPS và thấy dấu nhắc lệnh:
> ```
> root@ubuntu:~#
> ```

> **Lỗi thường gặp:**
> - `Permission denied`: sai mật khẩu hoặc sai SSH Key
> - `Connection timed out`: sai IP hoặc VPS chưa mở
> - `Connection refused`: dịch vụ SSH trên VPS chưa chạy hoặc bị firewall chặn

---

### 2.3. Bước 2: Cập nhật hệ điều hành

```bash
apt update && apt upgrade -y
```

**Giải thích:**

- `apt update`: cập nhật danh sách package mới nhất
- `apt upgrade -y`: nâng cấp toàn bộ package đã cài

> **Kết quả mong đợi:** Hệ thống tải và cập nhật các package thành công, không báo lỗi nghiêm trọng.

---

### 2.4. Bước 3: Cài Python 3, pip và Git

```bash
apt install python3 python3-pip python3-venv -y
apt install git -y
```

**Kiểm tra sau cài đặt:**

```bash
python3 --version
pip3 --version
git --version
```

> **Kết quả mong đợi:**
> ```
> Python 3.12.x
> pip 24.x.x
> git version 2.x.x
> ```

**Ý nghĩa:**

- `python3`: trình thông dịch Python
- `pip3`: công cụ cài thư viện Python
- `git`: tải source code từ GitHub
- `python3-venv`: tạo môi trường ảo cô lập

---

### 2.5. Bước 4: Clone source code từ GitHub

```bash
git clone https://github.com/your-username/weather-fastapi.git
cd weather-fastapi
```

**Kiểm tra nội dung thư mục:**

```bash
ls
```

> **Kết quả mong đợi:** Nhìn thấy các file và thư mục:
> ```
> main.py
> requirements.txt
> templates/
> ```

---

### 2.6. Bước 5: Tạo môi trường ảo và cài thư viện

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Giải thích:**

- `python3 -m venv venv`: tạo môi trường ảo tên `venv`
- `source venv/bin/activate`: kích hoạt môi trường ảo
- `pip install -r requirements.txt`: cài các thư viện `fastapi`, `uvicorn`, `jinja2`, `requests`

> **Kết quả mong đợi:** Dấu nhắc lệnh có tiền tố `(venv)`:
> ```
> (venv) root@ubuntu:~/weather-fastapi#
> ```

**Kiểm tra:**

```bash
pip list
```

> Bạn sẽ thấy các package: `fastapi`, `uvicorn`, `jinja2`, `requests`.

---

### 2.7. Bước 6: Chạy ứng dụng theo cách thủ công

Chắc chắn đang ở trong môi trường ảo `(venv)`, chạy:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

> **Kết quả mong đợi:** Terminal hiển thị:
> ```
> INFO:     Started server process
> INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
> ```

Mở trình duyệt và truy cập `http://<IP_VPS_CUA_BAN>:8000`. Thử thêm các route:

- `http://192.168.1.100:8000/thoi-tiet`
- `http://192.168.1.100:8000/ty-gia`

---

### 2.8. Bước 7: Quan sát vấn đề thực tế

Khi app đang chạy, nhấn `Ctrl + C`, sau đó refresh trình duyệt.

> **Hiện tượng:** Website không truy cập được nữa.

**Giải thích:** Khi chạy `uvicorn main:app ...`, ứng dụng đang gắn trực tiếp với phiên terminal hiện tại. Nếu bạn nhấn `Ctrl + C`, đóng terminal hoặc mất kết nối SSH, process cũng dừng theo.

> Đây là lý do không nên chạy ứng dụng production theo cách thủ công.

---

### 2.9. Bước 8: Tạo Systemd Service

Systemd là công cụ quản lý service có sẵn trên Ubuntu, giúp:

- Chạy app nền tự động khi VPS khởi động
- Tự restart khi app gặp lỗi crash

Thoát môi trường ảo trước:

```bash
deactivate
```

Tạo file service:

```bash
nano /etc/systemd/system/weather-app.service
```

Dán nội dung sau vào file:

```ini
[Unit]
Description=Weather FastAPI Application
After=network.target

[Service]
User=root
WorkingDirectory=/root/weather-fastapi
ExecStart=/root/weather-fastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Lưu và thoát: nhấn `Ctrl + X` → `Y` → `Enter`.

**Giải thích:**

- `WorkingDirectory`: thư mục chứa source code
- `ExecStart`: lệnh khởi động app, dùng uvicorn từ bên trong `venv`
- `Restart=always`: tự khởi động lại nếu app bị crash

---

### 2.10. Bước 9: Kích hoạt và chạy Service

```bash
systemctl daemon-reload
systemctl enable weather-app
systemctl start weather-app
```

**Kiểm tra trạng thái:**

```bash
systemctl status weather-app
```

> **Kết quả mong đợi:** Trạng thái hiển thị `Active: active (running)`.

---

### 2.11. Bước 10: Kiểm tra kết quả

Đóng terminal SSH, rồi mở trình duyệt và truy cập `http://<IP_VPS_CUA_BAN>:8000`.

> **Kết quả mong đợi:** Ứng dụng vẫn hoạt động bình thường.

---

### 2.12. Các lệnh Systemd quan trọng

| Lệnh | Mô tả |
|------|-------|
| `systemctl status weather-app` | Xem trạng thái service |
| `journalctl -u weather-app -f` | Xem log realtime |
| `systemctl restart weather-app` | Khởi động lại service |
| `systemctl stop weather-app` | Dừng service |
| `systemctl disable weather-app` | Tắt tự khởi động |

---

### 2.13. Kết luận Lab 1

- Deploy thủ công là cách dễ bắt đầu nhưng chưa tối ưu
- Chạy app trực tiếp bằng `uvicorn` rất dễ bị gián đoạn
- Systemd giải quyết bài toán chạy nền và tự khởi động lại
- Virtual environment giúp cô lập thư viện Python tránh xung đột

---

## LAB 2. ĐÓNG GÓI ỨNG DỤNG BẰNG DOCKER VÀ CHẠY TRÊN VPS

### 3.1. Mục tiêu

Sau lab này, học viên sẽ:

- Biết viết Dockerfile cho ứng dụng Python
- Biết build image từ source code
- Biết đẩy image lên Docker Hub
- Biết kéo image về VPS và chạy container
- Hiểu lợi ích của việc "build ở local, run ở server"

---

### 3.2. Ý tưởng trước khi làm

Ở Lab 1, VPS phải tự cài Python, venv, clone code, chạy `pip install` và tạo systemd service thủ công. Điều này dẫn đến máy chủ dễ bị "rác", khó đồng nhất môi trường.

Với **Docker**:

- Việc build được đóng gói thành image
- VPS chỉ cần kéo image về và chạy container
- Môi trường nhất quán hơn

---

### 3.3. Bước 1: Tạo Dockerfile trên máy local

Tạo file `Dockerfile` trong thư mục source code với nội dung:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3.4. Giải thích từng dòng Dockerfile

| Dòng | Nội dung | Giải thích |
|------|----------|------------|
| 1 | `FROM python:3.12-slim` | Dùng image nền là Python 3.12 bản slim, gọn nhẹ |
| 2–3 | `ENV PYTHONDONTWRITEBYTECODE` + `ENV PYTHONUNBUFFERED` | Tắt file `.pyc`, buộc ghi log ra stdout |
| 4 | `WORKDIR /app` | Tạo thư mục làm việc bên trong container |
| 5–6 | `COPY requirements.txt` + `RUN pip install` | Copy khai báo thư viện rồi cài dependency, tận dụng Docker cache |
| 7 | `COPY . .` | Copy toàn bộ source code còn lại vào container |
| 8 | `EXPOSE 8000` | Khai báo ứng dụng chạy ở cổng 8000 |
| 9 | `CMD ["uvicorn", ...]` | Lệnh mặc định để khởi chạy ứng dụng bằng Uvicorn |

---

### 3.5. Bước 2: Tạo file .dockerignore

Tạo file `.dockerignore` để tránh copy file không cần thiết vào image:

```
.git
__pycache__
*.pyc
*.pyo
venv/
.env
```

**Giải thích:** Giúp image nhỏ hơn và bảo mật hơn (không lộ file `.env`).

---

### 3.6. Bước 3: Đăng nhập Docker Hub trên máy local

```bash
docker login
```

Nhập Docker Hub username và password.

> **Kết quả mong đợi:** `Login Succeeded`

---

### 3.7. Bước 4: Build Docker image

```bash
docker build -t <your_dockerhub_username>/weather-fastapi:v1.0.0 .
```

> **Lưu ý:** Dấu `.` ở cuối lệnh là bắt buộc — đại diện cho thư mục hiện tại chứa source code và Dockerfile.

**Kiểm tra image:**

```bash
docker images
```

> **Kết quả mong đợi:** Thấy image `<username>/weather-fastapi   v1.0.0`

---

### 3.8. Bước 5: Chạy thử container trên máy local

Trước khi push lên Docker Hub, hãy test để đảm bảo container chạy đúng:

```bash
docker run -d -p 8000:8000 --name weather-test <your_dockerhub_username>/weather-fastapi:v1.0.0
```

Mở trình duyệt và kiểm tra:

- `http://localhost:8000`
- `http://localhost:8000/thoi-tiet`
- `http://localhost:8000/ty-gia`

**Dọn dẹp sau khi test:**

```bash
docker stop weather-test
docker rm weather-test
```

---

### 3.9. Bước 6: Push image lên Docker Hub

```bash
docker push <your_dockerhub_username>/weather-fastapi:v1.0.0
```

> **Kết quả mong đợi:** Image được tải lên Docker Hub thành công.

---

### 3.10. Bước 7: Chuẩn bị VPS để chạy Docker

SSH vào VPS, dừng Systemd service nếu đang chạy, rồi cài Docker:

```bash
systemctl stop weather-app
systemctl disable weather-app
apt install docker.io -y
systemctl start docker
systemctl enable docker
docker --version
```

---

### 3.11. Bước 8: Kéo image từ Docker Hub về VPS

```bash
docker pull <your_dockerhub_username>/weather-fastapi:v1.0.0
docker images
```

> **Kết quả mong đợi:** Image được tải về VPS thành công.

---

### 3.12. Bước 9: Chạy container

```bash
docker run -d -p 80:8000 --name python-app-container <your_dockerhub_username>/weather-fastapi:v1.0.0
```

**Giải thích:**

- `-d`: chạy nền
- `-p 80:8000`: ánh xạ cổng 80 của VPS tới cổng 8000 trong container
- `--name`: đặt tên container là `python-app-container`

> **Kết quả mong đợi:** Một chuỗi ID container được in ra.

---

### 3.13. Bước 10: Chạy bằng Docker Compose (nâng cao)

Tạo file `docker-compose.yml` trên VPS:

```bash
nano docker-compose.yml
```

Dán nội dung:

```yaml
services:
  app:
    image: giangltdau/weather-fastapi:latest
    container_name: my-python-app
    restart: unless-stopped
    ports:
      - "8000:8000"
```

Cài Docker Compose và chạy:

```bash
apt install docker-compose-plugin -y
docker compose up -d
docker compose ps
```

**Giải thích:**

- `restart: unless-stopped`: container tự khởi động lại sau khi VPS reboot
- `docker-compose.yml`: dễ đọc và dễ chỉnh hơn lệnh `docker run` dài dòng

---

### 3.14. Bước 11: Kiểm tra container đang chạy

```bash
docker ps
```

> **Kết quả mong đợi:** Container ở trạng thái `Up`.

Mở trình duyệt và truy cập `http://<IP_VPS_CUA_BAN>` (không cần thêm `:8000` vì đang map cổng 80).

---

### 3.15. Một số lệnh Docker quan trọng

| Lệnh | Mô tả |
|------|-------|
| `docker ps` | Xem container đang chạy |
| `docker ps -a` | Xem tất cả container |
| `docker logs python-app-container` | Xem log container |
| `docker stop python-app-container` | Dừng container |
| `docker rm python-app-container` | Xóa container |
| `docker rmi <username>/weather-fastapi:v1.0.0` | Xóa image |

---

### 3.16. Kết luận Lab 2

- Docker giúp đóng gói ứng dụng và môi trường chạy thành một đơn vị thống nhất
- VPS không cần cài Python, venv hay quản lý service thủ công như ở Lab 1
- Triển khai bằng image giúp dễ quản lý phiên bản hơn
- Docker Compose là cách quản lý container tốt hơn câu lệnh `docker run`

---

## LAB 3. TỰ ĐỘNG HÓA CI/CD VỚI GITHUB ACTIONS

### 4.1. Mục tiêu

Sau lab này, học viên sẽ:

- Biết tạo GitHub Secrets
- Biết viết workflow GitHub Actions
- Biết tự động build image khi push code
- Biết tự động SSH vào VPS để deploy
- Biết quy trình cập nhật và rollback phiên bản

---

### 4.2. Ý tưởng tổng thể

Trước đây, mỗi lần cập nhật ứng dụng, bạn phải thực hiện thủ công:

> sửa code → commit → push → build image → push image → SSH vào VPS → pull → stop container cũ → run container mới

**CI/CD sẽ tự động hóa toàn bộ chuỗi này.**

---

### 4.3. Bước 1: Tạo Secrets trên GitHub

Vào repository → **Settings → Secrets and variables → Actions → New repository secret**.

Tạo các secret sau:

**Docker Hub:**

- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

**VPS:**

- `VPS_HOST`
- `VPS_USERNAME`
- `VPS_PASSWORD` (hoặc `VPS_SSH_KEY` nếu dùng SSH Key)

---

### 4.4. Bước 2: Tạo workflow deploy.yml

Tạo file `.github/workflows/deploy.yml` với nội dung:

```yaml
name: CI/CD Pipeline - Weather FastAPI

on:
  push:
    branches: [ "main" ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Lấy source code
        uses: actions/checkout@v3

      - name: Đăng nhập Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build và Push Docker Image
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }} .
          docker tag ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }} \
                     ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
          docker push ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:latest

  deploy-to-vps:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: SSH vào VPS và Deploy
        uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USERNAME }}
          password: ${{ secrets.VPS_PASSWORD }}
          script: |
            docker pull ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
            docker stop python-app-container || true
            docker rm python-app-container || true
            docker run -d -p 80:8000 --name python-app-container \
              ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
```

---

### 4.5. Giải thích workflow

**Phần 1 — Trigger:**

```yaml
on:
  push:
    branches: [ "main" ]
```

Mỗi khi có code được push lên nhánh `main`, workflow sẽ chạy.

**Phần 2 — Job `build-and-push`:** Checkout source code → đăng nhập Docker Hub → build image với tag là mã commit → tag thêm `latest` → push cả hai lên Docker Hub.

**Phần 3 — Job `deploy-to-vps`:** Chỉ chạy sau khi `build-and-push` thành công (`needs: build-and-push`). SSH vào VPS → pull image mới → dừng/xóa container cũ → chạy container mới.

> **Vì sao dùng `${{ github.sha }}`?** Đây là mã commit hiện tại. Mỗi lần push sẽ có một tag image riêng, giúp dễ truy vết và rollback. Tag `latest` luôn trỏ đến bản mới nhất để tiện dùng với Docker Compose.

---

### 4.6. Bước 3: Commit và push workflow lên GitHub

```bash
git add .
git commit -m "Add CI/CD workflow for FastAPI"
git push origin main
```

> **Kết quả mong đợi:** GitHub Actions tự động được kích hoạt.

---

### 4.7. Bước 4: Theo dõi pipeline

Trên GitHub, vào tab **Actions**. Quan sát:

- Job `build-and-push` có thành công không
- Job `deploy-to-vps` có thành công không

Nếu thành công, workflow sẽ có dấu màu xanh.

---

### 4.8. Bước 5: Kiểm tra cập nhật ứng dụng

Mở `main.py` và thêm một thành phố mới vào dict `CITIES`:

```python
"Cần Thơ": {"lat": 10.0452, "lon": 105.7469},
```

Sau đó:

```bash
git add .
git commit -m "Add Can Tho city to weather app"
git push origin main
```

Chờ workflow chạy xong, truy cập `http://<IP_VPS_CUA_BAN>/thoi-tiet`.

> **Kết quả mong đợi:** Thành phố Cần Thơ xuất hiện trên trang thời tiết.

---

### 4.9. Bước 6: Rollback khi bản mới có lỗi

SSH vào VPS và chạy:

```bash
docker stop python-app-container
docker rm python-app-container
docker run -d -p 80:8000 --name python-app-container \
  <your_dockerhub_username>/weather-fastapi:v1.0.0
```

> Không cần sửa code ngay — chỉ cần chạy lại image ổn định trước đó là hệ thống hoạt động lại nhanh chóng. Đây là một trong những lợi ích lớn nhất của việc quản lý phiên bản image bằng tag.

---

## PHẦN 5. TỔNG HỢP KIẾN THỨC SAU 3 LAB

### 5.1. So sánh 3 cách triển khai

| | Deploy thủ công + Systemd | Docker | CI/CD |
|---|---|---|---|
| **Ưu điểm** | Dễ hiểu, phù hợp người mới, chi phí thấp | Môi trường nhất quán, dễ versioning, VPS gọn | Tự động hóa, nhanh, ít sai sót, dễ mở rộng team |
| **Nhược điểm** | Phải cài nhiều thứ, dễ sai, khó đồng nhất | Cần học khái niệm image/container/registry | Cần thiết lập ban đầu kỹ, quản lý secrets phức tạp |

---

## PHẦN 6. BÀI TẬP THỰC HÀNH ĐỀ XUẤT

**Bài tập 1:** Thêm 2 thành phố mới vào dict `CITIES` trong `main.py` (ví dụ: Huế, Nha Trang), deploy thủ công lên VPS bằng Systemd.

**Bài tập 2:** Chỉnh Dockerfile để thêm biến môi trường `ENV APP_ENV=production`. Sau đó build lại và kiểm tra:

```bash
docker exec python-app-container env | grep APP_ENV
```

**Bài tập 3:** Sửa workflow để deploy trên cổng `8080:8000` và truy cập bằng `http://<IP_VPS>:8080`.

**Bài tập 4:** Tạo thêm tag Docker `v2.0.0` sau khi thêm tính năng mới, push đồng thời cả `v2.0.0` và `latest`. Sau đó thực hành rollback về `v1.0.0`.

**Bài tập 5:** Chỉnh workflow để chỉ chạy CI/CD khi có thay đổi ở các file `main.py`, `requirements.txt`, hoặc `templates/**`.

```yaml
on:
  push:
    branches: [ "main" ]
    paths:
      - "main.py"
      - "requirements.txt"
      - "templates/**"
```
