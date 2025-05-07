# 🕷 GitHub Release & Commit Crawler

Một công cụ crawler tự động dùng Python để thu thập thông tin **release** và **commit giữa các phiên bản release** của các repository trên GitHub. Dữ liệu được lưu vào MySQL database.

---
**Submit version: `crawl-ver3.5`**  
## 📄 [DOCUMENTATION](https://docs.google.com/document/d/1lwXeUoKd8zy9hWcmY06YB_1gIMSSKhVdP6vh4iSh6rc/edit?tab=t.0#heading=h.br6grfny7kk8)

**_Thầy có thể vào đây để đọc full ạ 😄._**



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
├── images/
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
## ❗ Những vấn đề khi thực hiện dự án

### 🔒 Rate Limit của GitHub API
- GitHub API giới hạn:
  - **50 requests/giờ** với các request **không có token** (unauthenticated).
  - **5000 requests/giờ** khi sử dụng **Personal Access Token (PAT)**.
- Tuy nhiên, hệ thống cần crawl dữ liệu từ hàng ngàn repositories lớn ⇒ giới hạn này là **rào cản lớn** dẫn đến:
  - Thời gian xử lý **kéo dài**.
  - Phải **timeout 1 giờ** mỗi khi hết giới hạn request.

### 🐢 Tốc độ crawl chậm, chưa tối ưu tài nguyên hệ điều hành
- Ban đầu, hệ thống sử dụng **xử lý đơn luồng**, chưa tận dụng được hiệu quả của CPU.
- Điều này làm cho quá trình crawl dữ liệu trở nên **rất chậm** và **lãng phí tài nguyên**.

### 🔣 Ký tự đặc biệt trong response message
- Các response từ GitHub (releases, commits, ...) thường chứa:
  - **Ký tự đặc biệt** như `\n`, `\t`, `'`, `"` và cú pháp markdown.
- Điều này gây lỗi khi **insert vào MySQL** nếu không được xử lý đúng cách.

### 🛠️ Xử lý đọc/ghi và tương tác với cơ sở dữ liệu
- Hệ thống lâu dài và crawl đồng thời nhiều commits gây:
  - **Connection timeout** với MySQL.
  - Lưu từng commit sau mỗi timeout gây **tắc nghẽn và nặng nề**.
- Việc mỗi luồng mở một kết nối riêng:
  - Nếu số lượng lớn ⇒ tạo hàng **trăm kết nối đồng thời**.
  - Gây **quá tải cho hệ điều hành và MySQL**, dễ dẫn tới timeout hoặc crash.

### ♻️ Vấn đề trùng commit giữa các release
- Khi dùng endpoint `/commits?sha=<tag>`:
  - GitHub trả về các commit **có thể truy cập được từ tag đó**.
- Do các tag thường trỏ tới các commit trong nhánh chính (`main`), nên:
  - Các tag khác nhau thường **chia sẻ lịch sử commit giống nhau**.
  - Ví dụ:
    - `tag v1.2.0` và `tag v1.2.1` có thể trả về danh sách commit **giống nhau gần như hoàn toàn**.
  - Dẫn tới **danh sách bị trùng lặp** giữa các release.




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
![Schema](images/db.png)


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
### Cải tiến qua từng phiên bản

---

## 🚀 Phiên bản 1.0.0 – Triển khai ban đầu

### 📌 Cách tiếp cận
Trước hết, sử dụng selenium để crawl thông tin về toàn bộ 5000 repo có số sao cao nhất từ GitStar
Lưu 5000 repo đó vào bảng repo trong database, các thao tác crawl commit và release sẽ lấy thông tin từ bảng này.
Crawl tuần tự theo thứ tự: repo → release → commit bằng cách sử dụng GithubAPI kết hợp với các thông tin được lấy từ bảng repo trong cơ sở dữ liệu



### ✅ Kết quả
Crawl thành công toàn bộ 5000 repo từ GitStar.
Bước đầu đã crawl được thông tin của các release và commit và lưu xuống cơ sở dữ liệu thành công.



### ⚠️ Vấn đề
Giới hạn của GitHub API là 5000 request/token/giờ khiến việc crawl toàn bộ thông tin trở nên chậm và không hiệu quả.


### 🔍 Kết luận
Phương pháp tuần tự không phù hợp cho quy mô lớn khi lượng dữ liệu cần crawl là quá nhiều sẽ dẫn tới tốc độ chạy chậm chạp


---

## ⚡ Phiên bản 2.0.0 – Tối ưu hóa khả năng của GitHub API

### 📌 Cách tiếp cận
Dự kiến ban đầu vẫn là crawl toàn bộ rồi mới truy vấn tiếp theo thứ tự.
Tuy nhiên, nhận thấy số lượng request tăng lũy tiến, không thể mở rộng dù có 3 tokens.



### ✅ Giải pháp
Giảm thiểu số lần request API của github: Khi crawl được một release, lập tức crawl toàn bộ commit liên quan, thay vì để sau cùng, từ đó giảm request dư thừa, tận dụng tối đa số lượng request được phép mỗi giờ.



### 🔍 Kết luận
Cải tiến này giúp rút ngắn thời gian crawl đáng kể và sử dụng API hiệu quả hơn.
Tuy nhiên giải pháp này vẫn gặp vấn đề về rate limit khi chạy chưa được bao lâu thì token đã hết quota.



---

## 🔄 Phiên bản 2.1.0 – Giải pháp cho rate limit, tối ưu CPU

### ✨ Tính năng mới
Xoay vòng token khi bị giới hạn request.
Sử dụng đa luồng để crawl song song, rút ngắn thời gian xử lý toàn cục.



### ⚠️ Vấn đề mới
Lỗi khi insert dữ liệu vào MySQL do chứa các ký tự đặc biệt như \n, \t, ', ".


### ✅ Giải pháp
Bật hỗ trợ UTF-8 (Unicode) cho MySQL để đảm bảo lưu trữ chính xác các ký tự đặc biệt.


### 🔍 Kết quả
Phiên bản này có tốc độ crawl nhanh hơn nhiều so với các phiên bản trước, nhờ việc triển khai đa luồng, đồng thời thời gian và lượng thông tin crawl được cũng gia tăng đáng kể nhờ cơ chế xoay vòng token
Tuy nhiên, chính vì workload tăng đã làm lộ ra một số vấn đề của hệ thống, đặc biệt là vấn đề khi tương tác với cơ sở dữ liệu
---

## 🔧 Phiên bản 2.1.1 – Ổn định hóa kết nối

### ⚠️ Vấn đề
Lỗi connection timeout khi giữ kết nối MySQL quá lâu trong quá trình insert nhiều commit.

  
### ✅ Giải pháp
Tạo mới kết nối cho mỗi lần lưu commit để tránh timeout.


### 🔍 Hạn chế
Giải pháp này hoạt động tốt đối với giải pháp hiện tại của nhóm, nhưng để hệ thống phát triển lên cao hơn thì còn nhiều điểm yếu.


---

## 🧩 Phiên bản 2.2.0 – Tối ưu kết nối MySQL

### ⚠️ Vấn đề
Với đa luồng, số lượng request khổng lồ khiến hệ thống phải mở hàng trăm kết nối cùng lúc, dẫn đến quá tải.


### ✅ Giải pháp
Sử dụng connection pool (khoảng 30 kết nối) để tái sử dụng kết nối có sẵn thay vì tạo mới.
Chỉ tạo kết nối cho mỗi release, không mở cho từng commit riêng lẻ nữa.



### 🔍 Kết quả
Hệ thống ổn định hơn, hiệu suất cải thiện rõ rệt nhờ việc tiết kiệm thời gian và tài nguyên khởi tạo kết nối tới cơ sở dữ liệu
Việc mở lượng kết nối lớn cho phép tận dụng sức mạnh của hệ thống tốt hơn, tránh việc phải xếp hàng



---

## 🔁 Phiên bản 3.0.0 – Xử lý trùng lặp commit giữa các release

### ⚠️ Vấn đề
GitHub API trả về commit history của nhánh chính khi truyền sha=<tag> ⇒ dẫn đến các tag (ví dụ v1.2.0 và v1.2.1) có danh sách commit giống nhau đến 90%.


### 📌 Nguyên nhân
Các tag chia sẻ cùng commit history, vì vậy mỗi lần query theo tag, kết quả chứa các commit đã từng xuất hiện ở tag trước.


### ✅ Giải pháp
Cần lọc trùng commit giữa các release, chỉ giữ các commit thực sự mới so với tag trước.
Để kiểm tra các commit bị trùng, cần so sánh danh sách commit sha giữa các tag.
Giữ lại phần diff giữa các release thay vì toàn bộ danh sách.



---

## 🧼 Phiên bản 3.5.0 – Refactor hệ thống

### 🎯 Mục tiêu
Cải thiện khả năng bảo trì và phát triển của hệ thống.

  
### 📦 Tác vụ thực hiện
Tách các file theo chức năng: chia rõ phần xử lý API, database, crawl logic,...
Tách các query SQL riêng biệt: tránh việc hard-code SQL trong logic xử lý, dễ bảo trì và cải tiến.
Tách các biến cục bộ: để đảm bảo phạm vi rõ ràng, giảm rối code, dễ debug và tối ưu bộ nhớ.
Tách các khối code có tính tái sử dụng thành các hàm riêng



### ✅ Kết quả
Dễ dàng nâng cấp logic xử lý hoặc thay thế thành phần.
Hệ thống code rõ ràng hơn, dễ đọc và kiểm soát.
### Tổng kết

| **Tính năng**                 | **Mô tả chi tiết**                                                                 |
|------------------------------|-------------------------------------------------------------------------------------|
| **Xoay vòng nhiều token**      | Tự động đổi token khi gặp rate limit và sleep khi tất cả token hết request       |
| **Database connection pool**          | Tái sử dụng kết nối thay vì tạo mới mỗi lần, giảm chi phí mở kết nối đến database.                    |
| **Multithreading** | Crawl với nhiều luồng, tăng khả năng xử lý bất đồng bộ        |
| **Sử dụng Github API /compare** | Tránh trùng lặp các commit đã tồn tại trong release trước     |
| **Sử dụng RDBMS MySQL Workbench**        | Cho phép dữ liệu chứa các kí tự đặc biệt, markdown           |
| **README**      | Mô tả quá trình thực hiện, khó khăn và giải pháp một cách tường minh   |

# Crawl Benchmark Summary
| Version  | **8‑Repo Metrics**            |               |                         | **40‑Repo Metrics** |              |                  |                |
|----------|-------------------------------|---------------|-------------------------|---------------------|--------------|------------------|----------------|
|          | Total time                    | Avg per repo  | Est. full (5 000 repos) | Releases            | Commits      | Time per repo    | Total time     |
| **ver2** | 44.75 s                       | 5.59 s/repo   | 7.8 h                   | N/A                 | N/A          | N/A              | N/A            |
| **ver3** | 3.90 s                        | 0.49 s/repo   | 0.7 h                   | 7 265               | 2 338 144    | 31 s/repo        | 1 264 s        |

*The first 8 repos are lightweight (few commits/releases). The 40-repo batch is more representative and includes heavy repos like `facebook/react`, `nextjs`, etc.*

**Note:** `ver2` does not include metrics for the 40-repo batch due to poor performance, lack of optimization, and frequent MySQL timeouts during larger crawls.
📄 License
MIT License © 2025

