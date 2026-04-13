# LAB 3. TỰ ĐỘNG HÓA CI/CD CHO ỨNG DỤNG PYTHON VỚI GITHUB ACTIONS

## 4.1. Mục tiêu

Sau lab này, học viên sẽ:

* Biết tạo GitHub Secrets
* Biết viết workflow GitHub Actions
* Biết tự động build Docker image khi push code
* Biết tự động SSH vào VPS để deploy
* Biết quy trình cập nhật và rollback phiên bản

---

## 4.2. Ý tưởng tổng thể

Ở Lab 2, mỗi lần cập nhật ứng dụng, bạn phải làm thủ công:

* sửa code
* commit
* push
* build image thủ công
* push image thủ công
* SSH vào VPS
* pull image mới
* stop container cũ
* run container mới

CI/CD giúp tự động hóa gần như toàn bộ chuỗi này.

Với ứng dụng weather FastAPI, quy trình sẽ là:

* Khi push code lên nhánh `main`
* GitHub Actions tự động build image Docker mới
* Tự động push image lên Docker Hub
* Tự động SSH vào VPS
* Kéo image mới về
* Dừng container cũ
* Chạy container mới

Ý tưởng này chính là phần cốt lõi của Lab 3 mẫu bạn đưa ra, chỉ khác là mình áp dụng cho project Python thay vì Node.js. 

---

## 4.3. Chuẩn bị trước khi làm

Bạn nên có sẵn:

* project weather FastAPI đã push lên GitHub
* Dockerfile đã chạy được ở Lab 2
* VPS đã cài Docker
* tài khoản Docker Hub

Cấu trúc project ví dụ:

```text
weather-app/
├── main.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── templates/
    └── index.html
```

---

## 4.4. Bước 1: Tạo Secrets trên GitHub

Vào repository trên GitHub.

Đi theo đường dẫn:

```text
Settings → Secrets and variables → Actions
```

Chọn:

```text
New repository secret
```

Tạo các secret sau.

### 1. Docker Hub

```text
DOCKER_USERNAME
DOCKER_PASSWORD
```

### 2. VPS

```text
VPS_HOST
VPS_USERNAME
VPS_PASSWORD
```

Nếu dùng SSH key thay cho mật khẩu thì tạo:

```text
VPS_SSH_KEY
```

### Ý nghĩa

GitHub Actions sẽ đọc các thông tin này mà không cần ghi cứng trực tiếp trong file workflow. Đây chính là cách tổ chức mà mẫu Lab 3 đã dùng. 

---

## 4.5. Bước 2: Tạo workflow deploy.yml

Trong source code trên máy local, tạo thư mục:

```text
.github/workflows/
```

Tạo file:

```text
deploy.yml
```

Nội dung cho ứng dụng Python FastAPI:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: ["main"]

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Lấy source code
        uses: actions/checkout@v4

      - name: Đăng nhập Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build và Push Docker Image
        run: |
          docker build -t ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }} .
          docker push ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}

  deploy-to-vps:
    needs: build-and-push
    runs-on: ubuntu-latest

    steps:
      - name: SSH vào VPS và Deploy
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USERNAME }}
          password: ${{ secrets.VPS_PASSWORD }}
          script: |
            docker pull ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
            docker stop weather-app-container || true
            docker rm weather-app-container || true
            docker run -d -p 80:8000 --name weather-app-container ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
```

---

## 4.6. Giải thích workflow

### Phần 1: Trigger

```yaml
on:
  push:
    branches: ["main"]
```

Mỗi khi có code được push lên nhánh `main`, workflow sẽ tự động chạy.

---

### Phần 2: Job `build-and-push`

Job này sẽ:

* checkout source code
* đăng nhập Docker Hub
* build image Docker
* push image lên Docker Hub

Tên image trong lab này là:

```text
<dockerhub_username>/weather-fastapi:<commit_sha>
```

Ví dụ:

```text
dungpham/weather-fastapi:3f61b6f...
```

---

### Phần 3: Job `deploy-to-vps`

Job này chỉ chạy sau khi build thành công nhờ:

```yaml
needs: build-and-push
```

Sau đó workflow sẽ:

* SSH vào VPS
* kéo image mới nhất về
* dừng container cũ
* xóa container cũ
* chạy container mới

Mẫu workflow Node.js bạn đưa cũng dùng chính logic này, chỉ đổi tên image, tên container và cổng cho phù hợp với FastAPI weather app. 

---

### Vì sao dùng `${{ github.sha }}`

Đây là mã commit hiện tại.

Mỗi lần push sẽ tạo ra một tag image riêng, giúp:

* dễ truy vết bản deploy
* rollback nhanh
* không bị đè lẫn giữa các phiên bản

---

## 4.7. Bước 3: Commit và push workflow lên GitHub

Trên máy local, chạy:

```bash
git add .
git commit -m "Add CI/CD workflow for weather app"
git push origin main
```

### Kết quả mong đợi

GitHub Actions sẽ tự động được kích hoạt.

---

## 4.8. Bước 4: Theo dõi pipeline

Trên GitHub, vào tab:

```text
Actions
```

Bạn sẽ thấy workflow đang chạy.

### Cần quan sát

* Job `build-and-push` có thành công không
* Job `deploy-to-vps` có thành công không

Nếu cả hai job thành công, workflow sẽ có dấu xanh.

---

## 4.9. Bước 5: Kiểm tra cập nhật ứng dụng

Mở file `templates/index.html` hoặc `main.py` và sửa nội dung hiển thị. Ví dụ đổi tiêu đề:

```html
<h1>🌤️ Weather App CI/CD Demo</h1>
```

Sau đó chạy:

```bash
git add .
git commit -m "Update weather app UI for CI/CD test"
git push origin main
```

Chờ workflow chạy xong, rồi mở trình duyệt:

```text
http://<IP_VPS_CUA_BAN>
```

### Kết quả mong đợi

Website hiển thị nội dung mới.

Điều này chứng minh:

* code mới đã được build
* image mới đã được push
* VPS đã tự deploy bản mới

---

## 4.10. Bước 6: Rollback khi bản mới có lỗi

Giả sử bản mới lỗi, bạn muốn quay về image cũ ổn định.

SSH vào VPS và chạy:

```bash
docker stop weather-app-container
docker rm weather-app-container
docker run -d -p 80:8000 --name weather-app-container <your_dockerhub_username>/weather-fastapi:<old_tag>
```

Ví dụ:

```bash
docker stop weather-app-container
docker rm weather-app-container
docker run -d -p 80:8000 --name weather-app-container dungpham/weather-fastapi:v1.0.0
```

Hoặc nếu trước đó bạn đã deploy bằng `github.sha`, bạn có thể rollback về một commit cũ:

```bash
docker run -d -p 80:8000 --name weather-app-container dungpham/weather-fastapi:3f61b6fabc123
```

### Ý nghĩa

Bạn không cần sửa code ngay lập tức.

Chỉ cần chạy lại image ổn định trước đó là hệ thống có thể hoạt động lại nhanh chóng.

Đây cũng là một ý chính trong lab mẫu của bạn. 

---

# PHẦN 5. TỔNG HỢP KIẾN THỨC SAU 3 LAB

## 5.1. So sánh 3 cách triển khai

### Cách 1: Deploy thủ công bằng PM2

**Ưu điểm**

* Dễ hiểu
* Phù hợp cho người mới
* Nhìn rõ từng bước ứng dụng chạy như thế nào

**Nhược điểm**

* Dễ sai thao tác
* Khó lặp lại
* Môi trường VPS dễ bị lẫn nhiều thứ

---

### Cách 2: Docker

**Ưu điểm**

* Môi trường nhất quán hơn
* Dễ versioning
* VPS gọn hơn
* Không cần cài trực tiếp toàn bộ thư viện app trên VPS

**Nhược điểm**

* Cần hiểu image, container, registry
* Phải làm quen thêm với Dockerfile và lệnh Docker

---

### Cách 3: CI/CD với GitHub Actions

**Ưu điểm**

* Tự động hóa gần như toàn bộ
* Triển khai nhanh hơn
* Giảm thao tác thủ công
* Dễ mở rộng khi làm việc nhóm

**Nhược điểm**

* Thiết lập ban đầu kỹ hơn
* Cần quản lý secrets cẩn thận
* Debug pipeline ban đầu có thể hơi mất thời gian

Cách so sánh này bám sát phần tổng hợp của mẫu Lab 3 bạn gửi. 

---

# PHẦN 6. LỖI THƯỜNG GẶP VÀ CÁCH XỬ LÝ

## 1. Không truy cập được website

Kiểm tra:

* VPS có mở cổng `80` không
* container có đang chạy không
* firewall có chặn cổng không

Lệnh kiểm tra:

```bash
docker ps
ufw status
```

---

## 2. Docker build thất bại trong GitHub Actions

Kiểm tra:

* file `Dockerfile` có đúng không
* `requirements.txt` có thiếu package không
* project có copy đúng file `templates/` không

---

## 3. Docker push thất bại

Kiểm tra:

* `DOCKER_USERNAME`
* `DOCKER_PASSWORD`
* tên image có đúng không
* tài khoản Docker Hub có quyền push repo đó không

---

## 4. SSH action không deploy được

Kiểm tra:

* `VPS_HOST`
* `VPS_USERNAME`
* `VPS_PASSWORD`
* VPS có cho phép SSH bằng password không

Nếu không cho password login, hãy chuyển sang SSH key.

---

## 5. Container chạy rồi nhưng app lỗi

Xem log:

```bash
docker logs weather-app-container
```

Các lỗi thường gặp:

* thiếu thư mục `templates`
* sai tên `main:app`
* app chạy cổng khác `8000`
* `docker run` map sai cổng

---

## 6. VPS bị trùng cổng

Nếu trước đó bạn vẫn đang chạy app bằng PM2 hoặc container cũ, cổng `80` hoặc `8000` có thể bị chiếm.

Kiểm tra và dọn:

```bash
docker ps -a
pm2 list
```

Dừng container cũ:

```bash
docker stop weather-app-container
docker rm weather-app-container
```

---

# PHẦN 7. KẾT LUẬN LAB 3

Sau lab này, học viên hiểu được:

* GitHub Actions có thể tự động build và deploy ứng dụng Python
* Docker giúp chuẩn hóa môi trường chạy
* VPS chỉ cần kéo image mới và chạy container
* Mỗi commit có thể trở thành một phiên bản deploy riêng
* Rollback nhanh hơn nhờ dùng tag image

Lab 3 hoàn thiện chuỗi kiến thức từ:

* **Lab 1:** deploy thủ công và quản lý tiến trình
* **Lab 2:** đóng gói ứng dụng bằng Docker
* **Lab 3:** tự động hóa CI/CD

Toàn bộ logic này được xây lại từ khung Lab 3 bạn gửi, nhưng áp dụng trực tiếp cho ứng dụng Python weather FastAPI. 

---

## Mẫu workflow nâng cấp hơn

Nếu bạn muốn có thêm tag `latest`, đây là bản workflow cải tiến:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: ["main"]

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Lấy source code
        uses: actions/checkout@v4

      - name: Đăng nhập Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build và Push Docker Image
        run: |
          docker build \
            -t ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }} \
            -t ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:latest \
            .
          docker push ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
          docker push ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:latest

  deploy-to-vps:
    needs: build-and-push
    runs-on: ubuntu-latest

    steps:
      - name: SSH vào VPS và Deploy
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USERNAME }}
          password: ${{ secrets.VPS_PASSWORD }}
          script: |
            docker pull ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
            docker stop weather-app-container || true
            docker rm weather-app-container || true
            docker run -d -p 80:8000 --name weather-app-container ${{ secrets.DOCKER_USERNAME }}/weather-fastapi:${{ github.sha }}
```
