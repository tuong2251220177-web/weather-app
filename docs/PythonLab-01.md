# 🧪 Lab: Deploy App Python FastAPI lên VPS + PM2

## 🎯 Mục tiêu

* Clone project từ GitHub
* Chạy thử app FastAPI
* Hiểu vì sao app bị sập khi đóng SSH
* Dùng PM2 để giữ app chạy nền
* Thiết lập auto start khi reboot VPS

---

# 🧱 Yêu cầu

* Có VPS (Ubuntu)
* Có project FastAPI (weather-app của bạn)
* Có GitHub repo

---

# 🔐 Bước 1: SSH vào VPS

```bash
ssh root@<IP_VPS>
```

Nếu hỏi:

```text
Are you sure you want to continue connecting?
```

👉 gõ:

```bash
yes
```

---

# 🔄 Bước 2: Update hệ điều hành

```bash
apt update && apt upgrade -y
```

---

# 🛠️ Bước 3: Cài môi trường cần thiết

```bash
apt install python3 python3-pip python3-venv git nodejs npm -y
```

---

# 📥 Bước 4: Clone project từ GitHub

```bash
git clone https://github.com/your-username/weather-app.git
cd weather-app
```

---

# 🐍 Bước 5: Tạo môi trường ảo Python

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 📦 Bước 6: Cài thư viện

Nếu có `requirements.txt`:

```bash
pip install -r requirements.txt
```

Nếu chưa có:

```bash
pip install fastapi uvicorn jinja2 requests
```

---

# ▶️ Bước 7: Chạy thử app

```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Mở trình duyệt:

```text
http://<IP_VPS>:8000
```

👉 Bạn sẽ thấy web thời tiết chạy

---

## 💥 Trải nghiệm lỗi (quan trọng)

Quay lại terminal → nhấn:

```bash
Ctrl + C
```

Hoặc đóng SSH

👉 Refresh web → **app bị sập**

### 📌 Bài học

App đang chạy gắn với phiên SSH → đóng terminal là chết

---

# ⚙️ Bước 8: Cài PM2

```bash
npm install -g pm2
```

---

# 🚀 Bước 9: Chạy app bằng PM2

```bash
pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000" --name weather-fastapi
```

---

## 🔍 Kiểm tra

```bash
pm2 list
```

👉 phải thấy:

```text
weather-fastapi   online
```

---

## 🌐 Test lại

Mở lại:

```text
http://<IP_VPS>:8000
```

👉 App vẫn chạy

---

## 🔥 Test thực tế

Đóng SSH hoặc tắt terminal → app vẫn sống

---

# 💾 Bước 10: Lưu trạng thái PM2

```bash
pm2 save
```

---

# 🔄 Bước 11: Auto start khi reboot VPS

Chạy:

```bash
pm2 startup
```

👉 sẽ hiện 1 lệnh dạng:

```bash
sudo env "PATH=..." pm2 startup systemd -u <user> --hp /home/<user>
```

👉 copy & chạy lại lệnh đó

---

## 💾 Lưu lại lần nữa

```bash
pm2 save
```

---

# 🔁 Bước 12: Test reboot VPS

```bash
sudo reboot
```

Sau khi VPS lên lại:

```bash
pm2 list
```

👉 nếu vẫn `online` → thành công 🎉

---

# 🔓 (Optional) Mở port firewall

Nếu không truy cập được web:

```bash
ufw allow 8000
ufw enable
```

---

# 🧰 Các lệnh PM2 quan trọng

## Xem app

```bash
pm2 list
```

## Xem log

```bash
pm2 logs weather-fastapi
```

## Restart

```bash
pm2 restart weather-fastapi
```

## Stop

```bash
pm2 stop weather-fastapi
```

## Delete

```bash
pm2 delete weather-fastapi
```

---

# 📁 Cấu trúc project

```text
weather-app/
├── main.py
├── requirements.txt
├── templates/
│   └── index.html
└── venv/
```

---

# ⚠️ Lưu ý quan trọng

## ❌ Không dùng `--reload` khi deploy

Sai:

```bash
--reload
```

Đúng:

```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ❌ Không dùng sudo với PM2

Sai:

```bash
sudo pm2 start ...
```

Đúng:

```bash
pm2 start ...
```

---

# 🎯 Tổng kết nhanh

```bash
ssh root@IP
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git nodejs npm -y

git clone repo
cd project

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000" --name weather-fastapi
pm2 save
pm2 startup
pm2 save
```

---

