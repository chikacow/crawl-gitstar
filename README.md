# 🕷 GitHub Release & Commit Crawler

Một công cụ crawler tự động dùng Python để thu thập thông tin **release** và **commit giữa các phiên bản release** của các repository trên GitHub. Dữ liệu được lưu vào MySQL database.

---
**Submit version: `crawl-ver3.5`**  
📄 [Documentation](https://docs.google.com/document/d/1lwXeUoKd8zy9hWcmY06YB_1gIMSSKhVdP6vh4iSh6rc/edit?tab=t.0#heading=h.br6grfny7kk8)


``` directory
crawl-gitstar/
│── crawl-repo-gitstar/
│   ├── chromedriver
│   ├── crawl.py
|
├── crawl-ver3.5/
|   ├── .env
│   ├── crawler/   
|   	├── repo_crawler.py
|	├── release_crawler.py
|	└── commit_crawler.py
│   ├── db.py
│   ├── config.py
│   ├── token_manager.py
│   └── main.py
|
├── crawl-ver4-beta/
|   ├── .env
│   ├── db.py
|   ├── github_crawler.py
|   ├── token_manager.py
│   └── main.py
│
├── old-version/
│   ├── crawl-v1.py
│   ├── crawl_release_v2_final.py
│   └── sample_token_switch.py
│
├── main.py
└── README.md
```
---

## 📦 Tính năng

- ✅ Thu thập toàn bộ danh sách release của một repository.
- 🔍 Với mỗi cặp release liên tiếp, sử dụng GitHub Compare API để lấy các commit ở giữa.
- ⚡ Hỗ trợ đa luồng để tăng tốc độ crawl.
- 🔁 Tự động chuyển đổi giữa các GitHub token nếu quota bị hết.
- 🛢 Sử dụng connection pool cho MySQL để tối ưu hóa hiệu suất kết nối.

---

## 🛠 Cách hoạt động

Công cụ hoạt động theo các bước chính sau:

### 1. Tải danh sách repository

Crawler lấy dữ liệu từ bảng `repo` trong database MySQL, mỗi repo bao gồm:
- `id`: ID của repo
- `user`: Tên chủ sở hữu
- `name`: Tên repository

### 2. Thu thập release

Với mỗi repository, hàm `crawl_release()` sẽ gọi GitHub API để lấy toàn bộ danh sách các release.  
Mỗi release được lưu vào bảng `release` cùng với nội dung và thông tin liên kết đến repo tương ứng.

### 3. Lấy commit giữa các release

Sử dụng GitHub Compare API, hàm `crawl_commit_between_tags()` sẽ lấy toàn bộ commit nằm giữa từng cặp release liên tiếp.  
Các commit này sẽ được lưu vào bảng `commit`.

### 4. Quản lý token linh hoạt

Lớp `TokenManager` cho phép chuyển đổi giữa nhiều GitHub token. Khi một token bị rate limit, hệ thống sẽ tự động chuyển sang token tiếp theo.

### 5. Ghi dữ liệu vào MySQL hiệu quả

MySQL sử dụng **connection pooling** để tái sử dụng kết nối và giảm độ trễ khi ghi dữ liệu.

### 6. Chạy đa luồng

Mỗi repository sẽ được xử lý trong một **thread riêng biệt**, giúp tăng tốc độ crawl đáng kể.

---

## 🚀 Cách chạy

### 1. Clone repository

```bash
git clone https://github.com/your-username/github-crawler.git
cd github-crawler

pip install -r requirements.txt
```
### 2. Tạo database MySQL

Tạo một schema tên crawl và 3 bảng sau:

```sql
CREATE TABLE IF NOT EXISTS `release` (
	`id` int NOT NULL UNIQUE,
    `version` text NOT NULL,
	`content` text NOT NULL,
	`repoID` int NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `repo` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`user` text NOT NULL,
	`name` text NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `commit` (
	`hash` text NOT NULL,
	`message` text NOT NULL,
	`releaseID` int NOT NULL
);


ALTER TABLE `release` ADD CONSTRAINT `release_fk0` FOREIGN KEY (`repoID`) REFERENCES `repo`(`id`);
ALTER TABLE `commit` ADD CONSTRAINT `commit_fk2` FOREIGN KEY (`releaseID`) REFERENCES `release`(`id`);

```

### 3. Tạo file .env chứa GitHub tokens
Tạo file .env cùng cấp với script và thêm các token GitHub:

```env
GITHUB_TOKEN_1=ghp_abc123...
GITHUB_TOKEN_2=ghp_def456...
GITHUB_TOKEN_3=ghp_ghi789...
GITHUB-TOKEN-4=...
```

### 4. Cấu hình MySQL trong script
Mở file script và thay đổi phần dbconfig nếu cần:

```python
dbconfig = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "crawl",
    
}
```
### 5. Chạy crawler
```bash

python crawler.py
```

### Tutorials: (ver 3.5)

- Set up database, tạo các bảng và liên kết các bảng theo yêu cầu

- Sử dụng selenium và chromedriver để crawl toàn bộ 5000 repo nhiều sao nhất từ GitStar (folder crawl-gitstar)

- Triển khai các ý dưới đây cho các hàm crawl_repo(), crawl_commit(), crawl_release()

  - Khi crawl được một release, lập tức crawl toàn bộ commit liên quan, thay vì để sau cùng.

  - Triển khai cơ chế xoay vòng tokens khi bị giới hạn request bằng cách triển khai lớp TokenManager
  
  - Sử dụng đa luồng để crawl song song, rút ngắn thời gian xử lý toàn cục.
  
  - Tạo mới kết nối cho mỗi lần lưu commit để tránh timeout.
  
  - Sử dụng connection pool để tái sử dụng kết nối có sẵn thay vì tạo mới.
  
  - Chỉ tạo kết nối cho mỗi release, không mở cho từng commit riêng lẻ nữa.
  
  - Các tag chia sẻ cùng commit history, vì vậy mỗi lần query theo tag, kết quả chứa các commit đã từng xuất hiện ở tag trước.
  
  - Lọc trùng commit giữa các release bằng cách so sánh danh sách commit sha giữa các tag, chỉ giữ các commit thực sự mới so với tag trước.

- Cải thiện khả năng bảo trì và phát triển của hệ thống bằng việc tách nhỏ file tổng thành các file chức năng riêng biệt, có tính tái sử dụng hơn. Các query tới database cũng cần được tách riêng giúp logic tường minh và dễ cải tiến.

### Tổng kết

| Trạng thái                                    | Mô Tả                                                                                             |
|------------------------------------------|--------------------------------------------------------------------------------------------------|
| Done                                     | Triển khai được crawler cơ bản, thu thập tự động (có thể bị chặn)                                |
| Done                                     | Đánh giá và nêu nguyên nhân của các vấn đề gặp phải                                              |
| Done                                     | Cải tiến và so sánh hiệu suất với phiên bản ban đầu                                               |
| Done                                     | Tối ưu quá trình đọc ghi database                                                                  |
| Done                                     | Song song hoá (đa luồng) quá trình crawl                                                         |
| Done	                                   | Giải quyết vấn đề crawler bị trang web chặn khi truy cập quá nhiều bằng một số kỹ thuật hoặc design pattern tương ứng |
| Done                                     | Đánh giá các giải pháp tối ưu khác nhau                                                           |


📄 License
MIT License © 2025

