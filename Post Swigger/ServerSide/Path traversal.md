<!-- TOC -->
## Mục lục

- [Path traversal](#path-traversal)
  - [Khái niệm](#khái-niệm)
  - [Đọc tệp](#đọc-tệp)
  - [Lỗi phổ biến](#lỗi-phổ-biến)
  - [Phòng chống](#phòng-chống)
- [WU 6 lab](#wu-6-lab)
    - [File path traversal - simple case](#file-path-traversal---simple-case)
    - [File path traversal, traversal sequences blocked with absolute path bypass](#file-path-traversal-traversal-sequences-blocked-with-absolute-path-bypass)
    - [File path traversal, traversal sequences stripped non-recursively](#file-path-traversal-traversal-sequences-stripped-non-recursively)
    - [File path traversal, traversal sequences stripped with superfluous URL-decode](#file-path-traversal-traversal-sequences-stripped-with-superfluous-url-decode)
    - [File path traversal, validation of start of path](#file-path-traversal-validation-of-start-of-path)
    - [File path traversal, validation of file extension with null byte bypass](#file-path-traversal-validation-of-file-extension-with-null-byte-bypass)
<!-- /TOC -->
# Path traversal
## Khái niệm
Path traversal (còn gọi là directory traversal) là kiểu lỗ hổng cho phép kẻ tấn công đọc các tệp (file) tùy ý trên máy chủ đang chạy ứng dụng. Những tệp này có thể bao gồm:

- Mã nguồn và dữ liệu của ứng dụng.
- Thông tin xác thực (credentials) của các hệ thống back-end.
- Các tệp nhạy cảm của hệ điều hành.

Trong một số trường hợp, kẻ tấn công còn có thể ghi vào các tệp tùy ý trên máy chủ, từ đó thay đổi dữ liệu hoặc hành vi của ứng dụng và cuối cùng chiếm quyền kiểm soát hoàn toàn máy chủ.
## Đọc tệp
Hãy tưởng tượng một ứng dụng mua sắm hiển thị ảnh của các mặt hàng đang bán. Ứng dụng có thể tải một ảnh bằng HTML sau:

```php
<img src="/loadImage?filename=218.png">
```

URL `loadImage` nhận tham số `filename` và trả về nội dung của tệp được chỉ định. Các tệp ảnh được lưu trên đĩa tại vị trí `/var/www/images/`. Để trả về một ảnh, ứng dụng nối tên tệp được yêu cầu vào thư mục gốc này và dùng API hệ thống tệp để đọc nội dung tệp. Nói cách khác, ứng dụng đọc từ đường dẫn tệp sau:

```php
/var/www/images/218.png
```

Ứng dụng này không triển khai bất kỳ biện pháp phòng vệ nào chống lại tấn công path traversal. Do đó, kẻ tấn công có thể yêu cầu URL sau để truy xuất tệp `/etc/passwd` từ hệ thống tệp của máy chủ:
```php
<https://insecure-website.com/loadImage?filename=../../../etc/passwd>
```

Điều này khiến ứng dụng đọc từ đường dẫn tệp sau:

```php
/var/www/images/../../../etc/passwd
```

Chuỗi `../` là hợp lệ trong một đường dẫn tệp và có nghĩa là lùi lên một cấp trong cấu trúc thư mục. Ba chuỗi `../` liên tiếp sẽ lùi từ `/var/www/images/` lên đến gốc hệ thống tệp, vì vậy tệp thực sự được đọc là:

```php
/etc/passwd
```

Trên các hệ điều hành dựa trên Unix, đây là một tệp chuẩn chứa thông tin chi tiết về các người dùng đã đăng ký trên máy chủ, nhưng kẻ tấn công có thể lấy các tệp tùy ý khác bằng cùng kỹ thuật này.
Trên Windows, cả `../` và `..\\` đều là các chuỗi traversal thư mục hợp lệ. Sau đây là ví dụ về một cuộc tấn công tương đương nhắm vào máy chủ chạy Windows:

```php
<https://insecure-website.com/loadImage?filename=>..\\..\\..\\windows\\win.ini
```
## Lỗi phổ biến
1. Nhiều ứng dụng đưa `input` của người dùng vào đường dẫn tệp đã triển khai các biện pháp phòng vệ chống tấn công path traversal. Tuy nhiên, những biện pháp này thường có thể bị vượt qua.

Nếu một ứng dụng loại bỏ (strip) hoặc chặn các chuỗi traversal thư mục khỏi tên tệp do người dùng cung cấp, vẫn có thể vượt qua phòng vệ bằng nhiều kỹ thuật khác nhau.

Bạn có thể sử dụng một đường dẫn tuyệt đối tính từ gốc hệ thống tệp, chẳng hạn `filename=/etc/passwd`, để tham chiếu trực tiếp đến tệp mà không cần dùng các chuỗi traversal.

2.  Bạn có thể sử dụng các chuỗi traversal thư mục lồng nhau, chẳng hạn `....//` hoặc `....\\/`. Những chuỗi này sẽ trở về chuỗi traversal đơn giản khi chuỗi lồng bên trong bị loại bỏ.
3. Trong một số ngữ cảnh, chẳng hạn trong đường dẫn URL hoặc tham số `filename` của một yêu cầu `multipart/form-data`, máy chủ web có thể loại bỏ bất kỳ chuỗi traversal thư mục nào trước khi chuyển đầu vào của bạn đến ứng dụng. Đôi khi bạn có thể vượt qua kiểu làm sạch này bằng cách mã hóa URL (URL encoding), hoặc thậm chí mã hóa URL hai lần (double URL encoding) các ký tự `../`. Điều này lần lượt tạo ra `%2e%2e%2f` và `%252e%252e%252f`. Nhiều dạng mã hóa không tiêu chuẩn khác, như `..%c0%af` hoặc `..%ef%bc%8f`, cũng có thể hoạt động.
4. Một ứng dụng có thể yêu cầu tên tệp do người dùng cung cấp phải bắt đầu bằng thư mục gốc dự kiến, chẳng hạn `/var/www/images`. Trong trường hợp này, vẫn có thể khai thác bằng cách chèn thư mục bắt buộc đó rồi thêm các chuỗi traversal phù hợp phía sau.

Ví dụ:

```
filename=/var/www/images/../../../etc/passwd
```

Khi đó, ứng dụng sẽ hợp lệ hóa đường dẫn bắt đầu từ `/var/www/images`, nhưng chuỗi `../../../` sẽ đưa bạn thoát ra ngoài và truy cập đến `/etc/passwd`.

5. Một ứng dụng có thể yêu cầu tên tệp do người dùng cung cấp phải **kết thúc bằng một phần mở rộng cụ thể**, chẳng hạn `.png`. Trong trường hợp này, có thể khai thác bằng cách sử dụng **null byte** (`%00`) để chấm dứt đường dẫn tệp hiệu lực **trước** khi phần mở rộng bắt buộc được thêm vào.
Ví dụ:

```
filename=../../../etc/passwd%00.png
```

Khi đó, hệ thống tệp sẽ coi chuỗi dừng ở `%00`, và tệp thực sự được đọc là:

```
/etc/passwd
```

Trong khi ứng dụng vẫn “nghĩ” rằng đường dẫn kết thúc bằng `.png`.

> **Lưu ý** Kỹ thuật null byte injection thường chỉ hoạt động trên các ngôn ngữ/hệ thống cũ, chẳng hạn C/PHP phiên bản cũ; nhiều framework và API hiện đại đã vá không cho `%00` kết thúc chuỗi nữa.


## Phòng chống
Cách hiệu quả nhất để ngăn chặn lỗ hổng path traversal là **không truyền trực tiếp đầu vào từ người dùng vào API hệ thống tệp**. Nhiều chức năng ứng dụng hiện tại có thể được viết lại để đạt hành vi tương tự nhưng an toàn hơn.

Nếu không thể tránh việc truyền đầu vào của người dùng cho API hệ thống tệp, bạn nên áp dụng **hai lớp phòng vệ** sau:

1. **Xác thực đầu vào của người dùng trước khi xử lý**
    - Tốt nhất là so sánh đầu vào với một **danh sách trắng (whitelist)** các giá trị được phép.
    - Nếu không thể, hãy đảm bảo đầu vào chỉ chứa các ký tự hợp lệ, ví dụ chỉ cho phép ký tự chữ và số.
2. **Chuẩn hóa đường dẫn (canonicalize) và kiểm tra**
    - Sau khi xác thực, nối đầu vào với thư mục gốc đã định sẵn.
    - Dùng API hệ thống tệp của nền tảng để chuẩn hóa đường dẫn.
    - Kiểm tra xem đường dẫn chuẩn hóa có bắt đầu bằng thư mục gốc mong đợi hay không.
Ví dụ với Java:

```java
File file = new File(BASE_DIRECTORY, userInput);
if (file.getCanonicalPath().startsWith(BASE_DIRECTORY)) {
    // Xử lý file an toàn
}
```

Ở đây, `getCanonicalPath()` giúp loại bỏ các chuỗi `../` và chuẩn hóa đường dẫn, đảm bảo rằng tệp được truy cập không thể thoát ra ngoài thư mục gốc cho phép.

# WU 6 lab
 
- [x] File path traversal - Simple case
- [x] File path traversal - Traversal sequences blocked with absolute path bypass
- [x] File path traversal - Traversal sequences stripped non-recursively
- [x] File path traversal - Traversal sequences stripped with superfluous URL-decode
- [x] File path traversal - Validation of start of path
- [x] File path traversal - Validation of file extension with null byte bypass

### File path traversal - simple case
![](../../image/Pasted%20image%2020260422150315.png)
- tại trang web của bài lab, vào 1 sản phẩm bất kì và chọn xem 1 ảnh, trong burp, tìm request đó và gửi tới repeater
- tham số `filename=1.jpg` là nơi hệ thống nhận tên file để đọc

- sửa payload thành `filename=../../../etc/passwd`
vì thông thường các ảnh sẽ lưu ở: `/var/www/images/`
mỗi lần ../ sẽ đưa ta trở lại thư mục cha, 3 lần sẽ đưa ta từ /images về /www; từ /www về /var; và từ /var về thư mục root /
![](../../image/Pasted%20image%2020260422150612.png)

### File path traversal, traversal sequences blocked with absolute path bypass

- ở lab tiếp theo, khi thử cùng 1 payload tương tự, server trả về
![](../../image/Pasted%20image%2020260422151001.png)


- nhưng khi payload: `filename=/etc/passwd` thì
![](../../image/Pasted%20image%2020260422151359.png)

- có thể bài lab đã chặn hoặc lọc các ký tự như ../ nhưng ko chặn input băt đầu bằng / , và hệ thống có thể bỏ qua phần tiền tố trước đó và đi thẳng đến đường dẫn chỉ định

### File path traversal, traversal sequences stripped non-recursively

- ở bài lab này, khi thử các payload:
	```
	../../../etc/passwd
	/etc/passwd
	%2E%2E%2F%2E%2E%2F%2E%2E%2Fetc%2Fpasswd
	```
server đều báo lỗi
- dự đoán hệ thống đã sử dụng bộ lọc để bỏ đi chuỗi ../ từ input truyền vào
- => lồng chuỗi ../ vào giữa 1 cụm ../ khác
![](../../image/Pasted%20image%2020260413012335.png)
![](../../image/Pasted%20image%2020260422152910.png)
=> bộ lọc ko có tính đệ quy, nó chỉ quét và xóa 1 lần duy nhất

### File path traversal, traversal sequences stripped with superfluous URL-decode

- các payload khác đều bị filtered hoặc bị chặn, cần encode url trước khi đưa vào
chuỗi `%252E%252E%252F%252E%252E%252F%252E%252E%252F` là encode 2 lần của ../../../
- thông thường các webserver sẽ tự động decode url để hiểu tham số và khi ứng dụng nhận được url đã giải mã nên bộ lọc sẽ chặn
![](../../image/Pasted%20image%2020260423141301.png)

hoặc
![](../../image/Pasted%20image%2020260423141729.png)

### File path traversal, validation of start of path

![](../../image/Pasted%20image%2020260423142425.png)
mỗi lần ../ sẽ đưa ta trở lại thư mục cha, 3 lần sẽ đưa ta từ /images về /www; từ /www về /var; và từ /var về thư mục root /
### File path traversal, validation of file extension with null byte bypass
**null byte injection (%00)**: dùng để bỏ qua phần mở rộng tệp tin bị hệ thống ép buộc
	- mọi kí tự đứng sau %00 sẽ bị bỏ qua
![](../../image/Pasted%20image%2020260423143902.png)

- khi thêm đuôi .jpg hoặc .png với bypass
=> có thể hệ thống check input trước xem có kết thúc bằng đuôi jpg, png trước, nếu có thì hệ thống mới bắt đầu đọc và thực thi
- 
![](../../image/Pasted%20image%2020260423144042.png)

- từ php 5.3.4 trở đi thì trick %00 này đã đc fix