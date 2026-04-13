# LAB 3. TRIỂN KHAI CD CHO ỨNG DỤNG PYTHON VỚI GHCR VÀ RUNNER TRONG WSL

## 3.1. Mục tiêu

Sau lab này, học viên sẽ:

* Biết đóng gói ứng dụng Python thành Docker image
* Biết dùng GitHub Actions để build image và đẩy lên **GitHub Container Registry (GHCR)**
* Biết tạo **self-hosted runner** cho repository GitHub
* Biết chạy runner trong **Docker bên trong WSL**
* Biết thiết lập quy trình **CD**: khi push code lên nhánh `main`, image mới được build và app trong WSL được tự động cập nhật lại

GitHub có tài liệu chính thức cho cả việc publish Docker images bằng Actions, dùng self-hosted runners, và chọn runner bằng labels. GHCR là container registry của GitHub Packages, cho phép lưu image trong tài khoản hoặc tổ chức GitHub. ([GitHub Docs][1])

---

## 3.2. Ý tưởng trước khi làm

Ở lab trước, nếu triển khai thủ công thì mỗi lần cập nhật phiên bản mới, bạn thường phải:

* vào máy chạy ứng dụng
* pull code mới
* cài lại dependencies
* restart app

Cách đó có 3 nhược điểm:

* dễ sai thao tác
* khó đồng nhất môi trường
* mất thời gian khi lặp đi lặp lại

Với cách làm trong lab này:

* ứng dụng Python được đóng gói thành **Docker image**
* GitHub Actions sẽ tự build image
* image được đẩy lên **GHCR**
* một **runner tự host trong WSL** sẽ nhận lệnh deploy
* runner kéo image mới và restart container app

Nói ngắn gọn:

**Build ở GitHub Actions, run ở WSL**

GHCR được GitHub mô tả là container registry để lưu container images và có thể gắn với repository. GitHub Actions cũng hỗ trợ publish Docker image trực tiếp từ workflow. ([GitHub Docs][1])

---

## 3.3. Mô hình triển khai

```text
Lập trình viên push code lên GitHub
        ↓
GitHub Actions build image
        ↓
Push image lên GHCR
        ↓
Workflow deploy chạy trên self-hosted runner trong WSL
        ↓
Runner pull image mới
        ↓
Docker Compose restart app
```

Trong mô hình này:

* **GitHub-hosted runner** dùng để build image
* **self-hosted runner trong WSL** dùng để deploy
* runner deploy được chọn bằng `runs-on` và label tùy chỉnh, đúng theo cách GitHub hỗ trợ cho self-hosted runners. ([GitHub Docs][2])

---

## 3.4. Điều kiện chuẩn bị

Bạn cần có:

* Windows có **WSL 2**
* Docker Desktop
* một distro WSL, ví dụ Ubuntu
* tài khoản GitHub
* một repository GitHub chứa source code Python

Docker khuyến nghị với Windows + WSL nên dùng **Docker Desktop với WSL 2 backend**, bật tích hợp WSL trong Docker Desktop, và tránh cài Docker Engine trực tiếp trong distro WSL song song với Docker Desktop để không bị xung đột. Docker cũng nêu nên dùng WSL bản mới và ưu tiên làm việc trong filesystem Linux để có hiệu năng tốt hơn. ([Docker Documentation][3])

---

## 3.5. Bước 1 - Chuẩn bị môi trường WSL và Docker

Mở PowerShell:

```powershell
wsl --install
wsl --update
```

Cài Docker Desktop trên Windows, sau đó bật:

* **Use WSL 2 based engine**
* **WSL Integration** cho distro Ubuntu của bạn

Vào WSL, kiểm tra Docker:

```bash
docker version
docker ps
```

Nếu hai lệnh chạy được, môi trường đã sẵn sàng. Docker Desktop có hướng dẫn chính thức cho WSL 2 backend và WSL integration. ([Docker Documentation][3])

---

## 3.6. Bước 2 - Chuẩn bị source code Python

Ví dụ app Flask đơn giản:

### `app.py`

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Python app deployed by GHCR + WSL runner!"
```

### `requirements.txt`

```txt
flask==3.1.0
gunicorn==23.0.0
```

### `Dockerfile`

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 3.7. Bước 3 - Tạo self-hosted runner trong GitHub

Vào repository của bạn:

**Settings → Actions → Runners → New self-hosted runner**

GitHub cho phép thêm self-hosted runner ở cấp repository nếu bạn là chủ repository hoặc có quyền phù hợp. Khi thêm runner, GitHub sẽ cung cấp thông tin cấu hình và token đăng ký runner. ([GitHub Docs][4])

Bạn cần ghi lại:

* URL repo, ví dụ: `https://github.com/USERNAME/REPO`
* `RUNNER_TOKEN`
* tên runner, ví dụ: `wsl-runner-01`
* labels, ví dụ: `wsl,docker,cd`

GitHub hỗ trợ labels tùy chỉnh cho self-hosted runner và workflow có thể chọn runner theo labels này. ([GitHub Docs][5])

---

## 3.8. Bước 4 - Chạy runner trong Docker bên trong WSL

Tạo thư mục chạy runner:

```bash
mkdir -p ~/gh-runner
cd ~/gh-runner
```

Tạo file `docker-compose.yml`:

```yaml
services:
  gh-runner:
    image: myoung34/github-runner:latest
    container_name: gh-runner
    restart: unless-stopped
    environment:
      REPO_URL: https://github.com/USERNAME/REPO
      RUNNER_NAME: wsl-runner-01
      RUNNER_SCOPE: repo
      LABELS: wsl,docker,cd
      RUNNER_WORKDIR: /tmp/runner/work
      RUNNER_TOKEN: REPLACE_WITH_RUNNER_TOKEN
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./runner-data:/runner
    privileged: true
```

Chạy runner:

```bash
docker compose up -d
docker logs -f gh-runner
```

### Giải thích

* `REPO_URL`: repository GitHub cần gắn runner
* `RUNNER_NAME`: tên runner hiển thị trên GitHub
* `LABELS`: nhãn để workflow chọn đúng runner
* `RUNNER_TOKEN`: token GitHub cấp khi tạo runner
* mount `/var/run/docker.sock`: để runner container điều khiển Docker daemon của WSL host

Sau khi chạy thành công, vào GitHub bạn sẽ thấy runner ở trạng thái **online**.

> Ghi chú: GitHub chính thức hỗ trợ self-hosted runners, nhưng cách “gói runner thành Docker container” ở đây là cách triển khai thực hành phổ biến. Về mặt vận hành, bạn vẫn đang tự quản lý hạ tầng runner của mình. GitHub nhấn mạnh self-hosted runner là môi trường do bạn tự chịu trách nhiệm quản trị và bảo mật. ([GitHub Docs][6])

---

## 3.9. Bước 5 - Tạo workflow build image lên GHCR

Tạo file:

### `.github/workflows/build.yml`

```yaml
name: Build and Push GHCR Image

on:
  push:
    branches: [ "main" ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/python-app

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout source
        uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=latest
            type=sha

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

### Giải thích

* Workflow chạy khi có `push` lên nhánh `main`
* `packages: write` cho phép push image lên GHCR
* image được đặt tên theo dạng:

```text
ghcr.io/USERNAME/REPO/python-app:latest
```

GitHub có hướng dẫn chính thức cho việc publish Docker images bằng GitHub Actions, và GHCR là container registry chính thức của GitHub Packages. ([GitHub Docs][1])

---

## 3.10. Bước 6 - Tạo workflow deploy trên runner trong WSL

Tạo file:

### `.github/workflows/deploy.yml`

```yaml
name: Deploy to WSL Runner

on:
  workflow_run:
    workflows: ["Build and Push GHCR Image"]
    types:
      - completed

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: [self-hosted, wsl, docker, cd]

    steps:
      - name: Log in to GHCR
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin

      - name: Create deploy directory
        run: mkdir -p ~/deploy-python-app

      - name: Write compose file
        run: |
          cat > ~/deploy-python-app/docker-compose.yml <<'EOF'
          services:
            app:
              image: ghcr.io/${{ github.repository }}/python-app:latest
              container_name: python-app
              restart: unless-stopped
              ports:
                - "5000:5000"
          EOF

      - name: Pull latest image
        run: docker compose -f ~/deploy-python-app/docker-compose.yml pull

      - name: Restart app
        run: docker compose -f ~/deploy-python-app/docker-compose.yml up -d

      - name: Show running containers
        run: docker ps
```

### Giải thích

* Workflow này chỉ chạy sau khi workflow build kết thúc thành công
* `runs-on: [self-hosted, wsl, docker, cd]` chọn đúng runner trong WSL
* runner login vào GHCR, pull image mới, sau đó restart app bằng Docker Compose

GitHub hỗ trợ chọn self-hosted runner bằng labels trong `runs-on`, đúng như cấu hình ở trên. ([GitHub Docs][7])

---

## 3.11. Bước 7 - Cấu trúc thư mục hoàn chỉnh

```text
your-project/
├─ app.py
├─ requirements.txt
├─ Dockerfile
└─ .github/
   └─ workflows/
      ├─ build.yml
      └─ deploy.yml
```

---

## 3.12. Bước 8 - Chạy thử toàn bộ pipeline

Commit và push code:

```bash
git add .
git commit -m "setup CD with GHCR and WSL runner"
git push origin main
```

### Điều gì sẽ xảy ra

1. GitHub-hosted runner build Docker image
2. image được push lên GHCR
3. workflow deploy được kích hoạt
4. self-hosted runner trong WSL nhận job
5. runner pull image mới
6. app được restart bằng Docker Compose

---

## 3.13. Kiểm tra kết quả

Trong WSL:

```bash
docker ps
```

Bạn sẽ thấy container `python-app` đang chạy.

Xem image:

```bash
docker images
```

Mở trình duyệt:

```text
http://localhost:5000
```

Nếu mọi thứ đúng, bạn sẽ thấy nội dung:

```text
Hello from Python app deployed by GHCR + WSL runner!
```

---

## 3.14. Các lỗi thường gặp

### 1. Runner không nhận job

Nguyên nhân thường là label không khớp.

Ví dụ runner có:

```text
wsl,docker,cd
```

thì workflow phải có:

```yaml
runs-on: [self-hosted, wsl, docker, cd]
```

GitHub dùng labels để định tuyến job đến self-hosted runner phù hợp. ([GitHub Docs][7])

### 2. Không login hoặc pull được image từ GHCR

Cần kiểm tra:

* workflow build có `packages: write`
* package GHCR có quyền truy cập phù hợp
* repository và package đã được liên kết đúng

GitHub cho biết container registry có thể gắn với repository và quản lý quyền theo repository hoặc granular permissions. ([GitHub Docs][8])

### 3. Docker không chạy trong WSL

Thường do:

* chưa bật WSL integration trong Docker Desktop
* Docker Desktop đang ở Windows container mode
* cài Docker Engine trực tiếp trong WSL gây xung đột với Docker Desktop

Docker mô tả rõ các điều kiện này trong tài liệu WSL 2 backend. ([Docker Documentation][3])

### 4. Hiệu năng chậm

Nên đặt source code trong filesystem Linux của WSL thay vì thư mục mounted từ Windows để giảm overhead I/O. Docker nêu đây là best practice khi dùng WSL 2 với Docker Desktop. ([Docker Documentation][9])

---

## 3.15. Tổng kết

Sau lab này, bạn đã xây dựng được một quy trình CD hoàn chỉnh:

* source code Python được đóng gói bằng Docker
* GitHub Actions build image tự động
* image được đẩy lên GHCR
* self-hosted runner trong WSL tự động pull image mới
* ứng dụng được triển khai lại mà không cần thao tác thủ công

Đây là mô hình rất phù hợp để học CD trên máy cá nhân trước khi chuyển sang VPS hoặc server cloud thật.

---

[1]: https://docs.github.com/actions/guides/publishing-docker-images?utm_source=chatgpt.com "Publishing Docker images"
[2]: https://docs.github.com/actions/using-github-hosted-runners/about-github-hosted-runners?utm_source=chatgpt.com "GitHub-hosted runners"
[3]: https://docs.docker.com/desktop/features/wsl/?utm_source=chatgpt.com "Docker Desktop WSL 2 backend on Windows"
[4]: https://docs.github.com/actions/hosting-your-own-runners/adding-self-hosted-runners?utm_source=chatgpt.com "Adding self-hosted runners"
[5]: https://docs.github.com/actions/hosting-your-own-runners/using-labels-with-self-hosted-runners?utm_source=chatgpt.com "Using labels with self-hosted runners"
[6]: https://docs.github.com/actions/hosting-your-own-runners?utm_source=chatgpt.com "Self-hosted runners"
[7]: https://docs.github.com/actions/using-jobs/choosing-the-runner-for-a-job?utm_source=chatgpt.com "Choosing the runner for a job"
[8]: https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry?utm_source=chatgpt.com "Working with the Container registry"
[9]: https://docs.docker.com/desktop/features/wsl/best-practices/?utm_source=chatgpt.com "WSL 2 best practices for Docker Desktop on Windows"
