
GET /user/personal-info?user=carlos
```

Hầu hết các website sẽ có biện pháp ngăn kẻ tấn công chỉ đơn giản thay đổi tham số này để truy cập vào trang tài khoản của người dùng tùy ý. Tuy nhiên, đôi khi logic tải từng mục dữ liệu riêng lẻ lại không đủ chặt chẽ.

Kẻ tấn công có thể không tải được toàn bộ trang tài khoản của người dùng khác, nhưng logic lấy và render địa chỉ email đã đăng ký của người dùng, chẳng hạn, có thể không kiểm tra rằng tham số `user` khớp với người dùng đang đăng nhập. Trong trường hợp này, chỉ cần thay đổi tham số `user` cũng cho phép kẻ tấn công hiển thị địa chỉ email của người dùng tùy ý ngay trên trang tài khoản của mình.

### Sources code disclosure via backup files
Khi kẻ tấn công có quyền truy cập vào mã nguồn, việc hiểu hành vi của ứng dụng và xây dựng các cuộc tấn công nghiêm trọng trở nên dễ dàng hơn rất nhiều. Thậm chí, dữ liệu nhạy cảm đôi khi còn được hard-code trực tiếp trong mã nguồn, điển hình như khóa API hoặc thông tin xác thực để truy cập các thành phần back-end.

Nếu bạn nhận diện được rằng một công nghệ mã nguồn mở nào đó đang được sử dụng, điều này có thể cung cấp quyền truy cập dễ dàng vào một phần giới hạn mã nguồn.

Đôi khi, còn có thể khiến website vô tình lộ chính mã nguồn của nó. Trong quá trình thu thập thông tin (mapping) một website, bạn có thể phát hiện ra rằng một số tệp mã nguồn được tham chiếu trực tiếp. Thông thường, việc yêu cầu (request) những tệp này sẽ không tiết lộ mã nguồn. Khi máy chủ xử lý tệp có phần mở rộng như `.php`, nó sẽ thường **thực thi** mã thay vì gửi nguyên văn nội dung cho client. Tuy nhiên, trong một số tình huống, bạn có thể lừa website trả về nội dung của tệp thay vì thực thi. Ví dụ, các trình soạn thảo văn bản thường tạo ra tệp sao lưu tạm thời trong khi chỉnh sửa tệp gốc. Những tệp này thường được đánh dấu bằng cách thêm dấu ngã (`~`) vào cuối tên tệp hoặc dùng phần mở rộng khác. Việc gửi yêu cầu đến tệp mã nguồn kèm theo phần mở rộng sao lưu đôi khi cho phép bạn đọc được nội dung tệp trong phản hồi.

Khi kẻ tấn công đã có quyền truy cập mã nguồn, đây có thể là một bước tiến lớn giúp nhận diện và khai thác thêm nhiều lỗ hổng khác vốn gần như không thể phát hiện được. Một ví dụ là **insecure deserialization (giải tuần tự không an toàn)**. Chúng ta sẽ nghiên cứu kỹ lỗ hổng này ở một chủ đề riêng.

### Information disclosure via due to insecure configuration
Đôi khi website trở nên dễ bị tấn công do cấu hình không đúng cách. Điều này đặc biệt phổ biến bởi việc sử dụng rộng rãi các công nghệ bên thứ ba, vốn có vô số tùy chọn cấu hình mà người triển khai không nhất thiết hiểu rõ.

Trong một số trường hợp khác, lập trình viên có thể quên vô hiệu hóa các tùy chọn gỡ lỗi trong môi trường production. Ví dụ, phương thức **HTTP TRACE** được thiết kế cho mục đích chẩn đoán. Nếu được bật, máy chủ web sẽ phản hồi các request sử dụng phương thức TRACE bằng cách phản chiếu chính xác request đã nhận trong response. Hành vi này thường vô hại, nhưng đôi khi có thể dẫn đến việc tiết lộ thông tin, chẳng hạn như tên của các header xác thực nội bộ (internal authentication headers) được reverse proxy thêm vào trong request.

### Version control history 
Hầu như tất cả các website đều được phát triển bằng một hệ thống kiểm soát phiên bản nào đó, chẳng hạn như **Git**. Theo mặc định, một dự án Git sẽ lưu trữ toàn bộ dữ liệu kiểm soát phiên bản trong một thư mục có tên là `.git`. Thỉnh thoảng, các website lại vô tình để lộ thư mục này trong môi trường production. Trong trường hợp đó, bạn có thể truy cập nó chỉ bằng cách duyệt tới `/.git`.

Mặc dù việc duyệt thủ công cấu trúc file và nội dung thô thường không khả thi, nhưng có nhiều phương pháp để tải toàn bộ thư mục `.git`. Sau đó, bạn có thể mở nó bằng Git cài đặt trên máy của mình để truy cập lịch sử kiểm soát phiên bản của website. Điều này có thể bao gồm log ghi lại các thay đổi đã commit và các thông tin thú vị khác.

Điều này có thể không cho bạn quyền truy cập toàn bộ mã nguồn, nhưng việc so sánh **diff** sẽ cho phép bạn đọc được các đoạn mã nhỏ. Giống như bất kỳ mã nguồn nào, bạn cũng có thể tìm thấy dữ liệu nhạy cảm được hard-code trong một số dòng thay đổi.
## Phòng chống

Việc ngăn chặn hoàn toàn tiết lộ thông tin là khó khăn do có vô số cách mà nó có thể xảy ra. Tuy nhiên, có một số thực hành tốt (best practice) chung mà bạn có thể áp dụng để giảm thiểu rủi ro kiểu lỗ hổng này len lỏi vào chính website của mình.

- Đảm bảo tất cả những người tham gia xây dựng website đều hiểu rõ thông tin nào được coi là nhạy cảm. Đôi khi những thông tin tưởng như vô hại lại hữu ích với kẻ tấn công hơn mọi người nghĩ. Việc nhấn mạnh các nguy cơ này có thể giúp tổ chức của bạn xử lý thông tin nhạy cảm một cách an toàn hơn nói chung.
- Kiểm toán (audit) mã để tìm khả năng tiết lộ thông tin như một phần của quy trình QA hoặc build. Một số tác vụ liên quan có thể tự động hóa tương đối dễ, chẳng hạn như loại bỏ chú thích của lập trình viên.
- Sử dụng thông báo lỗi chung chung (generic) càng nhiều càng tốt. Đừng cung cấp manh mối về hành vi ứng dụng cho kẻ tấn công một cách không cần thiết.
- Kiểm tra kỹ rằng mọi tính năng gỡ lỗi (debug) hoặc chẩn đoán đều đã bị vô hiệu hóa trên môi trường production.
- Đảm bảo bạn hiểu đầy đủ các thiết lập cấu hình và hàm ý bảo mật của bất kỳ công nghệ bên thứ ba nào được triển khai. Hãy dành thời gian tìm hiểu và vô hiệu hóa mọi tính năng, thiết lập mà bạn thực sự không cần.

# WU 

<!-- TOC -->
## Mục lục

  - [Sources code disclosure via backup files](#sources-code-disclosure-via-backup-files)
  - [Information disclosure via due to insecure configuration](#information-disclosure-via-due-to-insecure-configuration)
  - [Version control history](#version-control-history)
- [Phòng chống](#phòng-chống)
  - [Information disclosure in error messages](#information-disclosure-in-error-messages)
  - [Information disclosure on debug page](#information-disclosure-on-debug-page)
  - [Source code disclosure via backup files](#source-code-disclosure-via-backup-files)
  - [Authentication bypass via information disclosure](#authentication-bypass-via-information-disclosure)
  - [Information disclosure in version control history](#information-disclosure-in-version-control-history)
<!-- /TOC -->

- [x] Information disclosure in error messages
- [x] Information disclosure on debug page
- [x] Source code disclosure via backup files
- [x] Authentication bypass via information disclosure
- [x] Information disclosure in version control history

### Information disclosure in error messages
- trang web hiển thị các sản phẩm theo productId
- thử đổi id sang dạng chuỗi bất kì để xem trang web có trả về thông báo gì hay ko
![](../../image/Pasted%20image%2020260501205441.png)
=> web đã tiết lộ trang web sử dụng apache struts
### Information disclosure on debug page

- dùng burp để scan 1 loạt các subdomain của trang web
![](../../image/Pasted%20image%2020260501205940.png)
- truy cập thử /cgi-bin/phpinfo.php, ta thấy secret-key ở đây

![](../../image/Pasted%20image%2020260501205925.png)

### Source code disclosure via backup files

- dùng burp để scan các subdomain của web
![](../../image/Pasted%20image%2020260501210330.png)

- truy cập /backup/ProductTemplate.java.bak và thấy db dùng Postgressql cùng mật khẩu
![](../../image/Pasted%20image%2020260501210424.png)
### Authentication bypass via information disclosure
- bài lab yêu cầu truy cập vào tài khoản admin
![](../../image/Pasted%20image%2020260501210844.png)
- gửi gói tin này sang repeater và TRACE thử gói tin này, ta thấy response có 1 header là X-Custom-IP-Authorization: 117.5.153.205, cho thấy hệ thống đang sử dụng một cơ chế kiểm tra IP tùy chỉnh.
![](../../image/Pasted%20image%2020260501211410.png)
- ta vào proxy để tùy chỉnh header này về 127.0.0.1 sau đó gửi lại gói tin ở repeater
![](../../image/Pasted%20image%2020260501211725.png)


![](../../image/Pasted%20image%2020260501211650.png)
### Information disclosure in version control history

- dùng burp để scan các subdomain của lab
![](../../image/Pasted%20image%2020260501212414.png)

- thấy /.git có thể chứa thông tin version
![](../../image/Pasted%20image%2020260501212434.png)
![](../../image/Pasted%20image%2020260501212754.png)
![](../../image/Pasted%20image%2020260501212814.png)
- cần tải file git về xem lịch sử commit (dùng wsl và sử dụng wget để tải về)
![](../../image/Pasted%20image%2020260501213748.png)