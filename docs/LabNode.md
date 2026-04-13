# TÀI LIỆU THỰC HÀNH CHI TIẾT

**Chủ đề:** Deploy ứng dụng Node.js từ thủ công đến CI/CD

---

## Mục tiêu chung

Sau khi hoàn thành 3 bài lab này, học viên sẽ:

- Hiểu cách đưa một ứng dụng Node.js lên VPS theo cách thủ công.
- Biết vì sao ứng dụng bị dừng khi đóng terminal và cách xử lý bằng PM2.
- Biết cách đóng gói ứng dụng bằng Docker để triển khai nhất quán hơn.
- Biết cách tự động hóa build và deploy bằng GitHub Actions.
- Làm quen với quy trình rollback khi phiên bản mới gặp lỗi.

## Ứng dụng mẫu dùng trong toàn bộ bài lab

Toàn bộ bài thực hành sử dụng một ứng dụng mẫu:

- Viết bằng **Node.js + Express**
- Chạy trên cổng **3000**
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

- Một VPS Ubuntu
- Biết các thông tin:
  - IP VPS
  - username đăng nhập: `root`
  - mật khẩu hoặc SSH Key

**Source code mẫu:**

Trên GitHub cần có một repository, ví dụ:

```
https://github.com/your-username/sample-node-app.git
```

Trong repository tối thiểu cần có:

- `app.js`
- `package.json`

Ví dụ nội dung file `app.js`:

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello World from Node.js App');
});

app.listen(3000, () => {
  console.log('App running on port 3000');
});
```

Ví dụ nội dung file `package.json`:

```json
{
  "name": "sample-node-app",
  "version": "1.0.0",
  "description": "Simple Node.js app for deployment practice",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

---

## LAB 1. DEPLOY THỦ CÔNG VÀ QUẢN LÝ TIẾN TRÌNH BẰNG PM2

### 2.1. Mục tiêu

Sau lab này, học viên sẽ:

- SSH được vào VPS
- Cài được Node.js, npm, Git
- Clone code từ GitHub về VPS
- Chạy được ứng dụng Node.js
- Hiểu vấn đề khi chạy app trực tiếp bằng terminal
- Dùng PM2 để giữ app chạy nền ngay cả khi ngắt kết nối SSH

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

### 2.4. Bước 3: Cài Node.js, npm và Git

```bash
apt install nodejs npm -y
apt install git -y
```

**Kiểm tra sau cài đặt:**

```bash
node -v
npm -v
git --version
```

> **Kết quả mong đợi:**
> ```
> v18.x.x
> 9.x.x
> git version 2.x.x
> ```

**Ý nghĩa:**

- `node`: chạy mã JavaScript phía server
- `npm`: cài thư viện Node.js
- `git`: tải source code từ GitHub

---

### 2.5. Bước 4: Clone source code từ GitHub

```bash
git clone https://github.com/your-username/sample-node-app.git
cd sample-node-app
```

**Kiểm tra nội dung thư mục:**

```bash
ls
```

> **Kết quả mong đợi:** Nhìn thấy các file:
> ```
> app.js
> package.json
> ```

---

### 2.6. Bước 5: Cài thư viện cho dự án

```bash
npm install
```

**Giải thích:** Lệnh này đọc file `package.json` và cài các dependency cần thiết, ví dụ `express`.

**Kiểm tra:**

```bash
ls
```

> **Kết quả mong đợi:** Bạn sẽ thấy thêm:
> ```
> node_modules
> package-lock.json
> ```

---

### 2.7. Bước 6: Chạy ứng dụng theo cách thủ công

```bash
node app.js
```

> **Kết quả mong đợi:** Terminal hiển thị:
> ```
> App running on port 3000
> ```

Mở trình duyệt và truy cập `http://<IP_VPS_CUA_BAN>:3000`. Bạn sẽ thấy:

```
Hello World from Node.js App
```

---

### 2.8. Bước 7: Quan sát vấn đề thực tế

Khi app đang chạy, nhấn `Ctrl + C`, sau đó refresh trình duyệt.

> **Hiện tượng:** Website không truy cập được nữa.

**Giải thích:** Khi chạy `node app.js`, ứng dụng đang gắn trực tiếp với phiên terminal hiện tại. Nếu bạn nhấn `Ctrl + C`, đóng terminal hoặc mất kết nối SSH, process cũng dừng theo.

> Đây là lý do không nên chạy ứng dụng production theo cách thủ công.

---

### 2.9. Bước 8: Cài PM2

```bash
npm install -g pm2
pm2 -v
```

**Giải thích:** PM2 là công cụ quản lý process cho Node.js, giúp:

- Chạy app nền
- Tự restart khi app lỗi
- Tự chạy lại khi VPS reboot

---

### 2.10. Bước 9: Khởi chạy app bằng PM2

```bash
cd ~/sample-node-app
pm2 start app.js --name "my-web-app"
```

**Kiểm tra:**

```bash
pm2 list
```

> **Kết quả mong đợi:** Thấy app `my-web-app` ở trạng thái `online`.

---

### 2.11. Bước 10: Lưu cấu hình PM2

```bash
pm2 save
```

**Giải thích:** Lưu danh sách process hiện tại để PM2 có thể khôi phục sau khi máy chủ restart.

---

### 2.12. Bước 11: Cấu hình PM2 tự khởi động cùng hệ thống

```bash
pm2 startup
```

Hệ thống sẽ in ra một lệnh dài, ví dụ:

```bash
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u root --hp /root
```

**Việc cần làm:** Copy chính xác dòng lệnh đó, dán lại vào terminal, nhấn Enter. Sau đó chạy:

```bash
pm2 save
```

---

### 2.13. Bước 12: Kiểm tra kết quả

Đóng terminal SSH, rồi mở trình duyệt và truy cập `http://<IP_VPS_CUA_BAN>:3000`.

> **Kết quả mong đợi:** Ứng dụng vẫn hoạt động bình thường.

---

### 2.14. Các lệnh PM2 quan trọng

| Lệnh | Mô tả |
|------|-------|
| `pm2 list` | Xem danh sách app |
| `pm2 logs my-web-app` | Xem log |
| `pm2 restart my-web-app` | Khởi động lại app |
| `pm2 stop my-web-app` | Dừng app |
| `pm2 delete my-web-app` | Xóa app khỏi PM2 |

---

### 2.15. Kết luận Lab 1

- Deploy thủ công là cách dễ bắt đầu nhưng chưa tối ưu
- Chạy app trực tiếp bằng `node app.js` rất dễ bị gián đoạn
- PM2 giải quyết bài toán chạy nền và tự khởi động lại

---

## LAB 2. ĐÓNG GÓI ỨNG DỤNG BẰNG DOCKER VÀ CHẠY TRÊN VPS

### 3.1. Mục tiêu

Sau lab này, học viên sẽ:

- Biết viết Dockerfile
- Biết build image từ source code
- Biết đẩy image lên Docker Hub
- Biết kéo image về VPS và chạy container
- Hiểu lợi ích của việc "build ở local, run ở server"

---

### 3.2. Ý tưởng trước khi làm

Ở Lab 1, VPS phải tự cài Node.js, npm, clone code và chạy `npm install`. Điều này dẫn đến máy chủ dễ bị "rác", khó đồng nhất môi trường và dễ phát sinh lỗi do khác phiên bản.

Với **Docker**:

- Việc build được đóng gói thành image
- VPS chỉ cần kéo image về và chạy
- Môi trường nhất quán hơn

---

### 3.3. Bước 1: Tạo Dockerfile trên máy local

Tạo file `Dockerfile` trong thư mục source code với nội dung:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "app.js"]
```

---

### 3.4. Giải thích từng dòng Dockerfile

| Dòng | Nội dung | Giải thích |
|------|----------|------------|
| 1 | `FROM node:18-alpine` | Dùng image nền là Node.js 18 bản Alpine, gọn nhẹ |
| 2 | `WORKDIR /app` | Tạo thư mục làm việc bên trong container |
| 3–4 | `COPY package*.json` + `RUN npm install` | Copy khai báo thư viện rồi cài dependency |
| 5 | `COPY . .` | Copy toàn bộ source code còn lại vào container |
| 6 | `EXPOSE 3000` | Khai báo ứng dụng chạy ở cổng 3000 |
| 7 | `CMD ["node", "app.js"]` | Lệnh mặc định để khởi chạy ứng dụng |

---

### 3.5. Bước 2: Đăng nhập Docker Hub trên máy local

```bash
docker login
```

Nhập Docker Hub username và password.

> **Kết quả mong đợi:** `Login Succeeded`

---

### 3.6. Bước 3: Build Docker image

```bash
docker build -t <your_dockerhub_username>/sample-node-app:v1.0.0 .
```

> **Lưu ý:** Dấu `.` ở cuối lệnh là bắt buộc — đại diện cho thư mục hiện tại chứa source code và Dockerfile.

**Kiểm tra image:**

```bash
docker images
```

> **Kết quả mong đợi:** Thấy image `<username>/sample-node-app   v1.0.0`

---

### 3.7. Bước 4: Push image lên Docker Hub

```bash
docker push <your_dockerhub_username>/sample-node-app:v1.0.0
```

> **Kết quả mong đợi:** Image được tải lên Docker Hub thành công.

---

### 3.8. Bước 5: Chuẩn bị VPS để chạy Docker

SSH vào VPS, dừng app PM2 nếu đang chạy, rồi cài Docker:

```bash
pm2 stop my-web-app
apt install docker.io -y
docker --version
```

---

### 3.9. Bước 6: Kéo image từ Docker Hub về VPS

```bash
docker pull <your_dockerhub_username>/sample-node-app:v1.0.0
docker images
```

> **Kết quả mong đợi:** Image được tải về VPS thành công.

---

### 3.10. Bước 7: Chạy container

```bash
docker run -d -p 80:3000 --name node-app-container <your_dockerhub_username>/sample-node-app:v1.0.0
```

**Giải thích:**

- `-d`: chạy nền
- `-p 80:3000`: ánh xạ cổng 80 của VPS tới cổng 3000 trong container
- `--name`: đặt tên container là `node-app-container`

> **Kết quả mong đợi:** Một chuỗi ID container được in ra.

---

### 3.11. Bước 8: Kiểm tra container đang chạy

```bash
docker ps
```

> **Kết quả mong đợi:** Container `node-app-container` ở trạng thái `Up`.

Mở trình duyệt và truy cập `http://<IP_VPS_CUA_BAN>` (không cần thêm `:3000` vì đang map cổng 80).

---

### 3.12. Một số lệnh Docker quan trọng

| Lệnh | Mô tả |
|------|-------|
| `docker ps` | Xem container đang chạy |
| `docker ps -a` | Xem tất cả container |
| `docker logs node-app-container` | Xem log container |
| `docker stop node-app-container` | Dừng container |
| `docker rm node-app-container` | Xóa container |
| `docker rmi <username>/sample-node-app:v1.0.0` | Xóa image |

---

### 3.13. Kết luận Lab 2

- Docker giúp đóng gói ứng dụng và môi trường chạy thành một đơn vị thống nhất
- VPS không cần cài nhiều thành phần như ở Lab 1
- Triển khai bằng image giúp dễ quản lý phiên bản hơn

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
name: CI/CD Pipeline

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
          docker build -t ${{ secrets.DOCKER_USERNAME }}/sample-node-app:${{ github.sha }} .
          docker push ${{ secrets.DOCKER_USERNAME }}/sample-node-app:${{ github.sha }}

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
            docker pull ${{ secrets.DOCKER_USERNAME }}/sample-node-app:${{ github.sha }}
            docker stop node-app-container || true
            docker rm node-app-container || true
            docker run -d -p 80:3000 --name node-app-container \
              ${{ secrets.DOCKER_USERNAME }}/sample-node-app:${{ github.sha }}
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

**Phần 2 — Job `build-and-push`:** Checkout source code → đăng nhập Docker Hub → build image → push image lên Docker Hub.

**Phần 3 — Job `deploy-to-vps`:** Chỉ chạy sau khi `build-and-push` thành công (`needs: build-and-push`). SSH vào VPS → pull image mới → dừng/xóa container cũ → chạy container mới.

> **Vì sao dùng `${{ github.sha }}`?** Đây là mã commit hiện tại. Mỗi lần push sẽ có một tag image riêng, giúp dễ truy vết và rollback.

---

### 4.6. Bước 3: Commit và push workflow lên GitHub

```bash
git add .
git commit -m "Add CI/CD workflow"
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

Sửa `app.js`:

```javascript
res.send('Hello CI/CD Deploy');
```

Sau đó:

```bash
git add .
git commit -m "Update text for CI/CD test"
git push origin main
```

Chờ workflow chạy xong, truy cập `http://<IP_VPS_CUA_BAN>`.

> **Kết quả mong đợi:** Nội dung mới xuất hiện trên website.

---

### 4.9. Bước 6: Rollback khi bản mới có lỗi

SSH vào VPS và chạy:

```bash
docker stop node-app-container
docker rm node-app-container
docker run -d -p 80:3000 --name node-app-container \
  <your_dockerhub_username>/sample-node-app:v1.0.0
```

> Không cần sửa code ngay — chỉ cần chạy lại image ổn định trước đó là hệ thống hoạt động lại nhanh chóng.

---

## PHẦN 5. TỔNG HỢP KIẾN THỨC SAU 3 LAB

### 5.1. So sánh 3 cách triển khai

| | Deploy thủ công | Docker | CI/CD |
|---|---|---|---|
| **Ưu điểm** | Dễ hiểu, phù hợp người mới | Môi trường nhất quán, dễ versioning | Tự động hóa, nhanh, ít sai sót |
| **Nhược điểm** | Dễ sai, app dễ dừng | Cần học khái niệm image/container/registry | Cần thiết lập ban đầu kỹ, quản lý secrets phức tạp |

---

## PHẦN 6. BÀI TẬP THỰC HÀNH ĐỀ XUẤT

**Bài tập 1:** Tự tạo một app Node.js mới có route `/about` và deploy bằng PM2.

**Bài tập 2:** Chỉnh Dockerfile để dùng `CMD ["npm", "start"]` thay vì `CMD ["node", "app.js"]`.

**Bài tập 3:** Sửa workflow để deploy trên cổng `8080:3000` và truy cập bằng `http://<IP_VPS>:8080`.

**Bài tập 4:** Tạo thêm tag Docker `latest` và push đồng thời cả `v1.0.0` và `latest`.

**Bài tập 5:** Cố tình làm app lỗi rồi thực hành rollback về bản cũ.

---

## PHẦN 7. LỖI THƯỜNG GẶP VÀ CÁCH XỬ LÝ

| Lỗi | Kiểm tra |
|-----|---------|
| Không truy cập được web | Cổng VPS có mở không, app có đang chạy không, firewall có chặn không |
| `npm install` lỗi | Phiên bản Node.js, file `package.json`, kết nối Internet của VPS |
| `docker pull` thất bại | Tên image đúng chưa, tag đúng chưa, đã push lên Docker Hub chưa |
| GitHub Actions fail ở đăng nhập Docker | `DOCKER_USERNAME`, `DOCKER_PASSWORD` có đúng không |
| SSH action không deploy được | `VPS_HOST`, `VPS_USERNAME`, `VPS_PASSWORD`, VPS có cho phép SSH bằng password không |
