```table-of-contents
```

# Information disclosure
## Khái niệm
![](../../image/Pasted%20image%2020260501203430.png)
Tiết lộ thông tin (còn gọi là rò rỉ thông tin) là khi một website vô tình để lộ thông tin nhạy cảm cho người dùng của nó. Tùy theo bối cảnh, website có thể rò rỉ đủ loại thông tin cho kẻ tấn công tiềm năng, bao gồm:

- Dữ liệu về người dùng khác, như tên người dùng (username) hoặc thông tin tài chính
- Dữ liệu thương mại hoặc kinh doanh nhạy cảm
- Chi tiết kỹ thuật về website và hạ tầng của nó

Mối nguy của việc rò rỉ dữ liệu người dùng hoặc dữ liệu kinh doanh nhạy cảm là khá rõ ràng, nhưng việc tiết lộ thông tin kỹ thuật đôi khi cũng nghiêm trọng không kém. Dù một phần thông tin này có thể chỉ hữu ích hạn chế, nó vẫn có thể là điểm khởi đầu để lộ ra thêm bề mặt tấn công, nơi có thể tồn tại các lỗ hổng thú vị khác. Lượng kiến thức bạn thu thập được thậm chí có thể là mảnh ghép còn thiếu khi cố gắng xây dựng các cuộc tấn công phức tạp với mức độ nghiêm trọng cao.

Thỉnh thoảng, thông tin nhạy cảm có thể bị sơ suất rò rỉ cho những người dùng chỉ đơn giản duyệt website theo cách bình thường. Tuy nhiên, phổ biến hơn là kẻ tấn công cần chủ động “gây ra” việc tiết lộ thông tin bằng cách tương tác với website theo những cách bất ngờ hoặc ác ý. Sau đó, họ sẽ cẩn thận nghiên cứu các phản hồi của website để cố gắng nhận diện hành vi đáng chú ý.

Một số ví dụ cơ bản về tiết lộ thông tin như sau:

- Tiết lộ tên các thư mục ẩn, cấu trúc và nội dung của chúng thông qua tệp `robots.txt` hoặc bật liệt kê thư mục (directory listing)
- Cung cấp quyền truy cập vào các tệp mã nguồn thông qua những bản sao lưu tạm thời
- Nêu tường minh tên bảng hoặc tên cột cơ sở dữ liệu trong thông báo lỗi
- Phơi bày không cần thiết thông tin cực kỳ nhạy cảm, như chi tiết thẻ tín dụng
- Hard-code khóa API, địa chỉ IP, thông tin xác thực cơ sở dữ liệu, v.v. trong mã nguồn
- Gợi ý về sự tồn tại hay không tồn tại của tài nguyên, tên người dùng, v.v. thông qua những khác biệt tinh vi trong hành vi của ứng dụng

## Nguyên nhân
Lỗ hổng tiết lộ thông tin có thể phát sinh theo vô số cách khác nhau, nhưng nhìn chung có thể phân loại như sau:

- Không loại bỏ nội dung nội bộ khỏi nội dung công khai. Ví dụ, các chú thích (comment) của nhà phát triển trong markup đôi khi vẫn hiển thị với người dùng trên môi trường production.
- Cấu hình không an toàn của website và các công nghệ liên quan. Ví dụ, không vô hiệu hóa các tính năng gỡ lỗi (debug) và chẩn đoán có thể cung cấp cho kẻ tấn công các công cụ hữu ích để thu thập thông tin nhạy cảm. Các cấu hình mặc định cũng có thể khiến website dễ bị tấn công, chẳng hạn như hiển thị thông báo lỗi quá chi tiết (verbose).
- Thiết kế và hành vi ứng dụng có lỗi. Ví dụ, nếu website trả về các phản hồi khác nhau ứng với từng trạng thái lỗi, điều này có thể cho phép kẻ tấn công liệt kê (enumerate) dữ liệu nhạy cảm, như thông tin đăng nhập hợp lệ.
## Hậu quả
Lỗ hổng tiết lộ thông tin có thể gây tác động cả trực tiếp lẫn gián tiếp, tùy thuộc vào mục đích của website và, do đó, vào loại thông tin mà kẻ tấn công có thể thu được. Trong một số trường hợp, chỉ riêng việc để lộ thông tin nhạy cảm đã có thể gây tác động lớn đối với các bên bị ảnh hưởng. Ví dụ, một cửa hàng trực tuyến làm rò rỉ chi tiết thẻ tín dụng của khách hàng rất có thể sẽ dẫn đến hậu quả nghiêm trọng.

Ngược lại, việc rò rỉ thông tin kỹ thuật, như cấu trúc thư mục hoặc các framework bên thứ ba đang được sử dụng, có thể có ít hoặc không có tác động trực tiếp. Tuy nhiên, rơi vào tay kẻ xấu, đây có thể là mảnh thông tin then chốt để dựng nên nhiều kỹ thuật khai thác khác. Mức độ nghiêm trọng trong trường hợp này phụ thuộc vào việc kẻ tấn công có thể làm gì với thông tin đó.

Cách đánh giá mức độ nghiêm trọng của lỗ hổng tiết lộ thông tin

Mặc dù tác động cuối cùng có thể rất nghiêm trọng, nhưng chỉ trong những trường hợp cụ thể thì việc tiết lộ thông tin mới tự thân là một vấn đề có mức độ nghiêm trọng cao. Trong quá trình kiểm thử, đặc biệt là với thông tin kỹ thuật, phát hiện này thường chỉ thực sự đáng quan tâm nếu bạn có thể chứng minh cách kẻ tấn công có thể sử dụng nó để gây hại.

Ví dụ, việc biết một website đang sử dụng phiên bản framework cụ thể là thông tin hữu dụng hạn chế nếu phiên bản đó đã được vá đầy đủ. Tuy nhiên, thông tin này trở nên quan trọng khi website dùng phiên bản cũ có chứa lỗ hổng đã biết. Trong trường hợp này, thực hiện một cuộc tấn công tàn phá có thể đơn giản chỉ là áp dụng một exploit đã được công bố công khai.

Điều quan trọng là phải cân nhắc hợp lý khi bạn phát hiện có khả năng rò rỉ thông tin nhạy cảm. Rất có thể những chi tiết kỹ thuật nhỏ nhặt có thể được tìm ra bằng nhiều cách trên nhiều website mà bạn kiểm thử. Do đó, trọng tâm chính của bạn nên là tác động và khả năng khai thác của thông tin bị rò rỉ, chứ không chỉ sự hiện diện của việc tiết lộ thông tin như một vấn đề độc lập. Ngoại lệ rõ ràng là khi thông tin bị rò rỉ nhạy cảm đến mức tự thân nó đã xứng đáng được chú ý.

## khai thác
### Files for web crawlers
Nhiều website cung cấp các tệp tại `/robots.txt` và `/sitemap.xml` để hỗ trợ crawler điều hướng trang web của họ. Trong số các thông tin khác, các tệp này thường liệt kê những thư mục cụ thể mà crawler nên bỏ qua, ví dụ, vì chúng có thể chứa thông tin nhạy cảm.

Do các tệp này thường không được liên kết trực tiếp từ trong website, chúng có thể sẽ không xuất hiện ngay trong site map của Burp. Tuy nhiên, bạn vẫn nên thử truy cập thủ công vào `/robots.txt` hoặc `/sitemap.xml` để xem có tìm được thông tin hữu ích nào không.

### Directory listings
Máy chủ web có thể được cấu hình để tự động liệt kê nội dung của các thư mục không có trang index. Điều này có thể hỗ trợ kẻ tấn công bằng cách cho phép chúng nhanh chóng xác định các tài nguyên trong một đường dẫn nhất định, rồi trực tiếp phân tích và tấn công các tài nguyên đó. Nó đặc biệt làm tăng nguy cơ lộ lọt các tệp nhạy cảm trong thư mục vốn không được dự định cho người dùng truy cập, chẳng hạn như tệp tạm (temporary files) và crash dump.

Danh sách thư mục (directory listing) tự nó không nhất thiết là một lỗ hổng bảo mật. Tuy nhiên, nếu website cũng đồng thời không triển khai kiểm soát truy cập đúng cách, thì việc tiết lộ sự tồn tại và vị trí của các tài nguyên nhạy cảm theo cách này rõ ràng là một vấn đề.

### Developer comment
Trong quá trình phát triển, các chú thích (comment) HTML nội tuyến đôi khi được thêm vào trong markup. Thông thường, những chú thích này sẽ được loại bỏ trước khi triển khai thay đổi lên môi trường production. Tuy nhiên, đôi khi chúng có thể bị quên, bỏ sót, hoặc thậm chí cố tình để lại vì ai đó không nhận thức đầy đủ về tác động bảo mật. Mặc dù các chú thích này không hiển thị trên trang được render, chúng có thể dễ dàng được truy cập bằng Burp, hoặc ngay cả công cụ Developer Tools tích hợp sẵn của trình duyệt.

Đôi khi, những chú thích này chứa thông tin hữu ích cho kẻ tấn công. Ví dụ, chúng có thể gợi ý về sự tồn tại của các thư mục ẩn hoặc cung cấp manh mối về logic của ứng dụng.

### Error messages
Một trong những nguyên nhân phổ biến nhất gây ra tiết lộ thông tin là các thông báo lỗi chi tiết quá mức (verbose error messages). Về nguyên tắc, bạn nên chú ý kỹ đến mọi thông báo lỗi mà bạn gặp trong quá trình kiểm thử.

Nội dung của thông báo lỗi có thể tiết lộ thông tin về kiểu dữ liệu hoặc input mà một tham số cụ thể mong đợi. Điều này có thể giúp bạn thu hẹp phạm vi tấn công bằng cách xác định những tham số có thể khai thác. Nó thậm chí còn giúp bạn không tốn thời gian thử những payload chắc chắn sẽ không hoạt động.

Thông báo lỗi chi tiết cũng có thể tiết lộ thông tin về các công nghệ mà website đang sử dụng. Ví dụ, chúng có thể nêu rõ tên của template engine, loại cơ sở dữ liệu, hoặc máy chủ mà website dùng, kèm cả số phiên bản. Đây là thông tin hữu ích vì bạn có thể dễ dàng tìm kiếm các exploit đã được công bố cho phiên bản đó. Tương tự, bạn có thể kiểm tra xem có lỗi cấu hình phổ biến hoặc thiết lập mặc định nguy hiểm nào có thể khai thác hay không. Một số điều này thậm chí còn được ghi rõ trong tài liệu chính thức.

Bạn cũng có thể phát hiện rằng website đang dùng một framework mã nguồn mở. Trong trường hợp đó, bạn có thể nghiên cứu mã nguồn công khai, vốn là tài nguyên vô giá để xây dựng exploit của riêng mình.

Ngoài ra, sự khác biệt giữa các thông báo lỗi cũng có thể tiết lộ hành vi ứng dụng khác nhau đang diễn ra phía sau. Việc quan sát sự khác biệt trong thông báo lỗi là một yếu tố then chốt trong nhiều kỹ thuật, chẳng hạn như SQL Injection, liệt kê tên người dùng (username enumeration), v.v.

### Debugging data
Vì mục đích gỡ lỗi, nhiều website tạo ra các thông báo lỗi tùy chỉnh và log chứa một lượng lớn thông tin về hành vi của ứng dụng. Trong khi những thông tin này hữu ích trong giai đoạn phát triển, thì nếu bị rò rỉ ở môi trường production, chúng cũng cực kỳ hữu ích cho kẻ tấn công.

Các thông báo debug đôi khi có thể chứa thông tin quan trọng để xây dựng một cuộc tấn công, bao gồm:

- Giá trị của các biến phiên (session variables) quan trọng có thể bị thao túng thông qua input của người dùng
- Tên host và thông tin xác thực của các thành phần back-end
- Tên tệp và thư mục trên máy chủ
- Các khóa được sử dụng để mã hóa dữ liệu truyền qua client

Thông tin gỡ lỗi đôi khi còn được ghi lại trong một tệp log riêng. Nếu kẻ tấn công có thể truy cập vào tệp này, nó có thể trở thành tài liệu tham khảo hữu ích để hiểu trạng thái runtime của ứng dụng. Đồng thời, nó cũng có thể cung cấp nhiều manh mối về cách chúng có thể đưa vào các input được thiết kế đặc biệt để thao túng trạng thái ứng dụng và kiểm soát thông tin nhận được.

### Users account pages

Theo bản chất, trang hồ sơ hoặc tài khoản của người dùng thường chứa thông tin nhạy cảm, chẳng hạn như địa chỉ email, số điện thoại, khóa API, v.v. Vì người dùng thông thường chỉ có quyền truy cập vào trang tài khoản của chính họ, nên điều này tự thân không phải là một lỗ hổng. Tuy nhiên, một số website có lỗi logic tiềm ẩn, cho phép kẻ tấn công lợi dụng để xem dữ liệu của người dùng khác.

Ví dụ, hãy xét một website xác định trang tài khoản cần tải dựa trên một tham số user:

```
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