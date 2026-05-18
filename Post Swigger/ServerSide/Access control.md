```table-of-contents
```
# Access control
## Khái niệm
Kiểm soát truy cập là việc áp dụng các ràng buộc về việc ai hoặc cái gì được ủy quyền thực hiện hành động hoặc truy cập tài nguyên. Trong ngữ cảnh ứng dụng web, kiểm soát truy cập phụ thuộc vào xác thực và quản lý phiên:

- **Xác thực (authentication)** xác nhận người dùng đúng là người mà họ tuyên bố.
- **Quản lý phiên (session management)** nhận diện những yêu cầu HTTP tiếp theo được thực hiện bởi cùng người dùng đó.
- **Kiểm soát truy cập (access control)** quyết định liệu người dùng có được phép thực hiện hành động mà họ đang cố gắng thực hiện hay không.

Các lỗi kiểm soát truy cập (broken access controls) rất phổ biến và thường là lỗ hổng bảo mật nghiêm trọng. Việc thiết kế và vận hành kiểm soát truy cập là một bài toán phức tạp và động, áp dụng các ràng buộc về kinh doanh, tổ chức và pháp lý lên một hiện thực kỹ thuật. Các quyết định thiết kế kiểm soát truy cập phải do con người đưa ra, vì vậy khả năng xảy ra sai sót là cao.
![](../../image/Pasted%20image%2020260501215614.png)

## Kiểm soát truy cập theo chiều dọc
Kiểm soát truy cập theo chiều dọc là các cơ chế hạn chế quyền truy cập vào các chức năng nhạy cảm cho các loại người dùng cụ thể.

Với kiểm soát truy cập theo chiều dọc, các loại người dùng khác nhau có quyền truy cập vào các chức năng ứng dụng khác nhau. Ví dụ, quản trị viên có thể sửa đổi hoặc xóa tài khoản của bất kỳ người dùng nào, trong khi người dùng thông thường không có quyền truy cập các thao tác này. Kiểm soát truy cập theo chiều dọc có thể là các triển khai chi tiết hơn (fine-grained) của các mô hình bảo mật được thiết kế để thực thi các chính sách nghiệp vụ như phân tách nhiệm vụ và đặc quyền tối thiểu.
## Kiểm soát truy cập theo chiều ngang
Kiểm soát truy cập theo chiều ngang là các cơ chế hạn chế quyền truy cập vào tài nguyên cho những người dùng cụ thể.

Với kiểm soát truy cập theo chiều ngang, những người dùng khác nhau có quyền truy cập vào một tập con các tài nguyên cùng loại. Ví dụ, một ứng dụng ngân hàng sẽ cho phép người dùng xem giao dịch và thực hiện thanh toán từ chính các tài khoản của họ, nhưng không phải từ các tài khoản của bất kỳ người dùng nào khác.
## Kiểm soát truy cập phụ thuộc ngữ cảnh
Kiểm soát truy cập phụ thuộc ngữ cảnh hạn chế quyền truy cập vào chức năng và tài nguyên dựa trên trạng thái của ứng dụng hoặc cách người dùng tương tác với ứng dụng.

Kiểm soát truy cập phụ thuộc ngữ cảnh ngăn người dùng thực hiện các hành động theo sai thứ tự. Ví dụ, một website bán lẻ có thể ngăn người dùng sửa đổi nội dung giỏ hàng sau khi họ đã thanh toán.
## Lỗ hổng
Lỗ hổng kiểm soát truy cập bị lỗi tồn tại khi người dùng có thể truy cập các tài nguyên hoặc thực hiện các hành động mà họ không được phép.
### Leo thang đặc quyền - Dọc

Nếu một người dùng có thể truy cập vào chức năng mà họ không được phép truy cập thì đây là leo thang đặc quyền theo chiều dọc. Ví dụ, nếu một người dùng không có quyền quản trị có thể truy cập vào trang quản trị nơi họ có thể xóa tài khoản người dùng, thì đây là leo thang đặc quyền theo chiều dọc.

#### Chức năng không được bảo vệ

Ở mức cơ bản nhất, leo thang đặc quyền theo chiều dọc xuất hiện khi một ứng dụng không thực thi bất kỳ biện pháp bảo vệ nào đối với các chức năng nhạy cảm. Ví dụ, các chức năng quản trị có thể được liên kết từ trang chào mừng của quản trị viên nhưng không có trên trang chào mừng của người dùng. Tuy nhiên, một người dùng vẫn có thể truy cập các chức năng quản trị bằng cách duyệt tới URL quản trị tương ứng.
Ví dụ, một website có thể lưu trữ chức năng nhạy cảm tại URL sau:

```
<https://insecure-website.com/admin>
```

URL này có thể truy cập bởi bất kỳ người dùng nào, không chỉ người dùng quản trị có liên kết tới chức năng này trong giao diện. Trong một số trường hợp, URL quản trị có thể bị tiết lộ ở các vị trí khác, chẳng hạn như tệp robots.txt:

```
<https://insecure-website.com/robots.txt>
```

Ngay cả khi URL không bị tiết lộ ở đâu, kẻ tấn công vẫn có thể sử dụng một danh sách từ (wordlist) để brute-force (vét cạn) vị trí của chức năng nhạy cảm.
Trong một số trường hợp, chức năng nhạy cảm được che giấu bằng cách gán cho nó một URL khó dự đoán hơn. Đây là ví dụ của cái gọi là “security by obscurity” (bảo mật nhờ che giấu). Tuy nhiên, việc ẩn chức năng nhạy cảm không cung cấp kiểm soát truy cập hiệu quả vì người dùng có thể phát hiện URL đã bị che giấu theo nhiều cách.

Hãy hình dung một ứng dụng lưu trữ các chức năng quản trị tại URL sau:

```
<https://insecure-website.com/administrator-panel-yb556>
```

URL này có thể không thể đoán trực tiếp bởi kẻ tấn công. Tuy nhiên, ứng dụng vẫn có thể làm rò rỉ URL cho người dùng. URL có thể bị tiết lộ trong JavaScript dùng để dựng giao diện người dùng dựa trên vai trò của người dùng:

```html
<script>
	var isAdmin = false;
	if (isAdmin) {
		...
		var adminPanelTag = document.createElement('a');
		adminPanelTag.setAttribute('href', '<https://insecure-website.com/administrator-panel-yb556>');
		adminPanelTag.innerText = 'Admin panel';
		...
	}
</script>
```
Đoạn script này thêm một liên kết vào giao diện người dùng nếu họ là người dùng quản trị. Tuy nhiên, script chứa URL này vẫn hiển thị cho tất cả người dùng, bất kể vai trò của họ.
#### Kiểm soát dựa trên tham số
Một số ứng dụng xác định quyền truy cập hoặc vai trò của người dùng tại thời điểm đăng nhập, rồi lưu thông tin này ở vị trí do người dùng kiểm soát. Điều này có thể là:

- Một trường ẩn.
- Một cookie.
- Một tham số chuỗi truy vấn được đặt sẵn.

Ứng dụng đưa ra quyết định kiểm soát truy cập dựa trên giá trị được gửi lên. Ví dụ:

```
<https://insecure-website.com/login/home.jsp?admin=true>
<https://insecure-website.com/login/home.jsp?role=1>
```

Cách tiếp cận này không an toàn vì người dùng có thể sửa đổi giá trị và truy cập vào các chức năng mà họ không được phép, chẳng hạn như các chức năng quản trị.

#### Cấu hình sai ở nền tảng
Một số ứng dụng thực thi kiểm soát truy cập ở tầng nền tảng bằng cách hạn chế truy cập vào các URL và phương thức HTTP cụ thể dựa trên vai trò của người dùng. Ví dụ, một ứng dụng có thể cấu hình một quy tắc như sau:

```
DENY: POST, /admin/deleteUser, managers
```

Quy tắc này từ chối quyền truy cập phương thức POST trên URL `/admin/deleteUser` đối với người dùng thuộc nhóm `managers`. Nhiều vấn đề có thể phát sinh trong tình huống này, dẫn đến việc bỏ qua (bypass) kiểm soát truy cập.

Một số framework ứng dụng hỗ trợ các header HTTP không tiêu chuẩn có thể được dùng để ghi đè URL trong yêu cầu gốc, như `X-Original-URL` và `X-Rewrite-URL`. Nếu một website sử dụng các biện pháp kiểm soát nghiêm ngặt phía trước (front-end) để hạn chế truy cập dựa trên URL, nhưng ứng dụng lại cho phép URL bị ghi đè thông qua một header trong yêu cầu, khi đó có thể bỏ qua kiểm soát truy cập bằng một yêu cầu như sau:

```
POST / HTTP/1.1
X-Original-URL: /admin/deleteUser
...
```

Một kiểu tấn công khác liên quan đến phương thức HTTP được sử dụng trong yêu cầu. Các cơ chế kiểm soát phía trước (front-end) được mô tả ở các phần trước hạn chế truy cập dựa trên URL và phương thức HTTP. Một số website chấp nhận các phương thức yêu cầu HTTP khác nhau khi thực hiện một hành động. Nếu kẻ tấn công có thể sử dụng phương thức GET (hoặc phương thức khác) để thực hiện hành động trên một URL bị hạn chế, họ có thể bỏ qua kiểm soát truy cập được triển khai ở tầng nền tảng.
#### Sai lệch khi đối sánh URL
Các website có thể khác nhau về mức độ nghiêm ngặt khi đối sánh đường dẫn của một yêu cầu đến với endpoint đã định nghĩa. Ví dụ, chúng có thể chấp nhận việc không nhất quán chữ hoa/chữ thường, vì vậy một yêu cầu tới `/ADMIN/DELETEUSER` vẫn có thể được ánh xạ tới endpoint `/admin/deleteUser`. Nếu cơ chế kiểm soát truy cập kém “khoan dung” hơn, nó có thể coi đây là hai endpoint khác nhau và do đó không thực thi đúng các hạn chế cần thiết.

Những sai lệch tương tự có thể phát sinh nếu các lập trình viên dùng framework Spring đã bật tùy chọn `useSuffixPatternMatch`. Tùy chọn này cho phép các đường dẫn có phần mở rộng tệp tùy ý được ánh xạ tới endpoint tương đương không có phần mở rộng. Nói cách khác, một yêu cầu tới `/admin/deleteUser.anything` vẫn sẽ khớp với mẫu `/admin/deleteUser`. Trước Spring 5.3, tùy chọn này được bật mặc định.

Trên các hệ thống khác, bạn có thể gặp sự khác biệt trong cách xử lý liệu `/admin/deleteUser` và `/admin/deleteUser/` có được coi là các endpoint riêng biệt hay không. Trong trường hợp này, bạn có thể bỏ qua kiểm soát truy cập bằng cách thêm một dấu gạch chéo kết thúc (trailing slash) vào đường dẫn.
### Leo thang đặc quyền ngang
Leo thang đặc quyền theo chiều ngang xảy ra nếu một người dùng có thể truy cập các tài nguyên thuộc về người dùng khác, thay vì chỉ các tài nguyên cùng loại của chính họ. Ví dụ, nếu một nhân viên có thể truy cập hồ sơ của các nhân viên khác cũng như của chính mình, thì đây là leo thang đặc quyền theo chiều ngang.

Các cuộc tấn công leo thang đặc quyền theo chiều ngang có thể sử dụng các phương pháp khai thác tương tự như leo thang đặc quyền theo chiều dọc. Ví dụ, một người dùng có thể truy cập trang tài khoản của chính họ bằng URL sau:

```
<https://insecure-website.com/myaccount?id=123>
```

Nếu kẻ tấn công sửa đổi giá trị tham số `id` thành của một người dùng khác, họ có thể giành quyền truy cập vào trang tài khoản của người dùng đó, cùng với dữ liệu và các chức năng liên quan.

> **Lưu ý**
> 
> Đây là ví dụ về lỗ hổng **tham chiếu đối tượng trực tiếp không an toàn (IDOR)**. Loại lỗ hổng này phát sinh khi các giá trị tham số do người dùng kiểm soát được sử dụng để truy cập trực tiếp vào tài nguyên hoặc chức năng.

Trong một số ứng dụng, tham số có thể khai thác không có giá trị có thể dự đoán. Ví dụ, thay vì một số tăng dần, một ứng dụng có thể sử dụng mã định danh duy nhất toàn cầu (GUID) để nhận diện người dùng. Điều này có thể ngăn kẻ tấn công đoán hoặc dự đoán định danh của người dùng khác. Tuy nhiên, các GUID thuộc về người dùng khác có thể bị lộ ở những nơi khác trong ứng dụng nơi người dùng được tham chiếu, chẳng hạn như tin nhắn của người dùng hoặc các bài đánh giá.
Trong một số trường hợp, ứng dụng có phát hiện khi người dùng không được phép truy cập tài nguyên và trả về một chuyển hướng tới trang đăng nhập. Tuy nhiên, phản hồi chứa chuyển hướng này vẫn có thể bao gồm một số dữ liệu nhạy cảm thuộc về người dùng mục tiêu, nên cuộc tấn công vẫn thành công.
### Leo thang đặc quyền ngang - dọc
Thường thì một cuộc tấn công leo thang đặc quyền theo chiều ngang có thể được chuyển thành leo thang đặc quyền theo chiều dọc bằng cách xâm phạm tài khoản của người dùng có đặc quyền cao hơn. Ví dụ, một leo thang theo chiều ngang có thể cho phép kẻ tấn công đặt lại hoặc chiếm đoạt mật khẩu của người dùng khác. Nếu kẻ tấn công nhắm mục tiêu một người dùng quản trị và chiếm đoạt tài khoản của họ, thì họ có thể giành quyền truy cập quản trị và do đó thực hiện leo thang đặc quyền theo chiều dọc.

Kẻ tấn công có thể giành quyền truy cập vào trang tài khoản của người dùng khác bằng kỹ thuật thao túng tham số (parameter tampering) đã mô tả cho leo thang theo chiều ngang:

```
<https://insecure-website.com/myaccount?id=456>
```

Nếu người dùng mục tiêu là quản trị viên ứng dụng, thì kẻ tấn công sẽ truy cập được vào trang tài khoản quản trị. Trang này có thể làm lộ mật khẩu của quản trị viên hoặc cung cấp cách để thay đổi nó, hoặc có thể cung cấp quyền truy cập trực tiếp vào các chức năng đặc quyền.

### Tham chiếu đối tượng trực tiếp ko an toàn (IDOR)

#### Khái niệm

Tham chiếu đối tượng trực tiếp không an toàn (IDOR) là một loại lỗ hổng kiểm soát truy cập phát sinh khi ứng dụng sử dụng đầu vào do người dùng cung cấp để truy cập trực tiếp các đối tượng. Thuật ngữ IDOR trở nên phổ biến nhờ xuất hiện trong OWASP Top Ten 2007. Tuy nhiên, đây chỉ là một ví dụ trong số nhiều sai sót khi hiện thực kiểm soát truy cập có thể dẫn đến việc kiểm soát truy cập bị bỏ qua. Lỗ hổng IDOR thường gắn với leo thang đặc quyền theo chiều ngang, nhưng cũng có thể phát sinh liên quan đến leo thang đặc quyền theo chiều dọc.

#### Database

Xét một website sử dụng URL sau để truy cập trang tài khoản khách hàng, bằng cách truy xuất thông tin từ cơ sở dữ liệu back-end:

```
<https://insecure-website.com/customer_account?customer_number=132355>
```

Ở đây, số khách hàng được sử dụng trực tiếp như một chỉ mục bản ghi trong các truy vấn thực hiện trên cơ sở dữ liệu back-end. Nếu không có các kiểm soát khác, kẻ tấn công chỉ cần sửa đổi giá trị `customer_number`, bỏ qua kiểm soát truy cập để xem hồ sơ của khách hàng khác. Đây là một ví dụ về lỗ hổng IDOR dẫn đến leo thang đặc quyền theo chiều ngang.

Kẻ tấn công có thể thực hiện cả leo thang đặc quyền theo chiều ngang lẫn theo chiều dọc bằng cách thay đổi người dùng thành một người dùng có đặc quyền cao hơn trong khi bỏ qua kiểm soát truy cập. Các khả năng khác bao gồm khai thác việc rò rỉ mật khẩu hoặc sửa đổi tham số sau khi kẻ tấn công đã vào được trang tài khoản của người dùng, chẳng hạn.

#### Static files

Lỗ hổng IDOR thường phát sinh khi các tài nguyên nhạy cảm được lưu trong các tệp tĩnh trên hệ thống tệp phía server. Ví dụ, một website có thể lưu bản ghi cuộc trò chuyện xuống đĩa bằng tên tệp tăng dần, và cho phép người dùng truy xuất chúng bằng cách truy cập URL như sau:

```
<https://insecure-website.com/static/12144.txt>
```

Trong tình huống này, kẻ tấn công chỉ cần sửa đổi tên tệp để lấy bản ghi do người dùng khác tạo và có thể thu được thông tin đăng nhập hoặc các dữ liệu nhạy cảm khác.

### Quy trình nhiều bước

Nhiều website triển khai các chức năng quan trọng thông qua một chuỗi các bước. Điều này thường xảy ra khi:

- Cần thu thập nhiều đầu vào hoặc tùy chọn khác nhau.
- Người dùng cần xem lại và xác nhận chi tiết trước khi hành động được thực thi.

Ví dụ, chức năng quản trị để cập nhật thông tin người dùng có thể bao gồm các bước sau:

1. Tải biểu mẫu chứa thông tin của một người dùng cụ thể.
2. Gửi các thay đổi.
3. Xem lại thay đổi và xác nhận.

Đôi khi, một website thực thi kiểm soát truy cập nghiêm ngặt ở một số bước nhưng lại bỏ qua các bước khác. Hãy hình dung một website áp dụng kiểm soát truy cập đúng ở bước 1 và bước 2, nhưng không áp dụng ở bước 3. Website giả định rằng người dùng chỉ có thể đến được bước 3 nếu họ đã hoàn thành các bước đầu tiên vốn đã được kiểm soát chặt chẽ.

Khi đó, kẻ tấn công có thể truy cập trái phép vào chức năng này bằng cách bỏ qua bước 1 và 2, rồi gửi trực tiếp yêu cầu cho bước 3 kèm các tham số cần thiết.

### Referer

Một số website dựa trên header **Referer** trong yêu cầu HTTP để thực thi kiểm soát truy cập. Header Referer có thể được trình duyệt thêm vào các yêu cầu để cho biết trang nào đã khởi tạo yêu cầu đó.

Ví dụ, một ứng dụng thực thi kiểm soát truy cập chặt chẽ đối với trang quản trị chính tại `/admin`, nhưng với các trang con như `/admin/deleteUser` thì chỉ kiểm tra header Referer. Nếu header Referer chứa URL `/admin` chính, thì yêu cầu sẽ được chấp nhận.

Trong trường hợp này, header Referer hoàn toàn có thể bị kẻ tấn công kiểm soát. Điều đó có nghĩa là họ có thể giả mạo các yêu cầu trực tiếp tới các trang con nhạy cảm bằng cách thêm Referer phù hợp, từ đó giành quyền truy cập trái phép.

### Vị trí

Một số website thực thi kiểm soát truy cập dựa trên vị trí địa lý của người dùng. Điều này có thể áp dụng, ví dụ, cho các ứng dụng ngân hàng hoặc dịch vụ truyền thông, nơi có các quy định pháp lý hoặc hạn chế kinh doanh theo khu vực. Các kiểm soát truy cập này thường có thể bị vượt qua bằng cách sử dụng web proxy, VPN, hoặc thao túng các cơ chế định vị phía client.
## Ngăn chặn

Có thể ngăn chặn lỗ hổng kiểm soát truy cập bằng cách áp dụng **phòng thủ nhiều lớp (defense-in-depth)** và tuân thủ các nguyên tắc sau:

- Không bao giờ chỉ dựa vào **che giấu (obfuscation)** để kiểm soát truy cập.
- Trừ khi một tài nguyên được thiết kế để công khai, hãy **từ chối truy cập theo mặc định**.
- Khi có thể, hãy sử dụng **một cơ chế thống nhất cho toàn ứng dụng** để thực thi kiểm soát truy cập.
- Ở cấp độ mã nguồn, bắt buộc lập trình viên phải **khai báo rõ ràng quyền truy cập được phép cho từng tài nguyên**, và mặc định từ chối truy cập.
- **Kiểm tra và đánh giá toàn diện** các cơ chế kiểm soát truy cập để đảm bảo chúng hoạt động đúng như thiết kế.

# WU 
- [ ] Unprotected admin functionality
- [ ] Unprotected admin functionality with unpredictable URL
- [ ] User role controlled by request parameter
- [ ] User role can be modified in user profile
- [ ] URL-based access control can be circumvented
- [ ] Method-based access control can be circumvented
- [ ] User ID controlled by request parameter
- [ ] User ID controlled by request parameter with unpredictable user IDs
- [ ] User ID controlled by request parameter with data leakage in redirect
- [ ] User ID controlled by request parameter with password disclosure
- [ ] Insecure direct object references
- [ ] Multi-step process with no access control on one step
- [ ] Referer-based access control

## Unprotected admin functionality
- dùng burp scan các subdomain và tìm được panel của admin
![](../../image/Pasted%20image%2020260501221747.png)

![](../../image/Pasted%20image%2020260501221722.png)

## Unprotected admin functionality with unpredictable URL
- dùng burp để scsan các subdomain khác của web
![](../../image/Pasted%20image%2020260501223241.png)
![](../../image/Pasted%20image%2020260501223228.png)


## User role controlled by request parameter

- khi login bằng wiener:peter nhìn vào gói tin trong burp thấy cookie của request post
![](../../image/Pasted%20image%2020260501223752.png)

- login lại và chặn các gói tin để sửa admin = true để xem có thể truy cập admin
![](../../image/Pasted%20image%2020260501224113.png)
- ở gói tin nào đều cần chuyển admin= true để ok bị mất quyền admin

## User role can be modified in user profile
- khi login vào wiener:peter, có mục để update email
- gửi gói tin này sang repeater và thêm roleid=2 vào trong json
![](../../image/Pasted%20image%2020260501225734.png)

- khi đó ta đã vào được panel của admin
![](../../image/Pasted%20image%2020260501225759.png)


## URL-based access control can be circumvented
- khi truy cập vào trang panel của admin
![](../../image/Pasted%20image%2020260501233528.png)
![](../../image/Pasted%20image%2020260501234158.png)
- thêm header X-Original-Url: /admin thay vì get trực tiếp

![](../../image/Pasted%20image%2020260501234144.png)
![](../../image/Pasted%20image%2020260501234450.png)
## Method-based access control can be circumvented
- ở bài lab này, ta có thể login vào tài khoản admin và nâng quyền cho tài khoản thường thành admin
![](../../image/Pasted%20image%2020260501235328.png)
- khi thử dùng cookie session của wiener (lúc này là tài khoản thường) và thực hiện nâng quyền thì bị unauthorize
![](../../image/Pasted%20image%2020260501235851.png)
- thay vì sử dụng post, ta thử dùng phương thức get
![](../../image/Pasted%20image%2020260502000056.png)
![](../../image/Pasted%20image%2020260502000048.png)
- Hệ thống không chặn gói tin ngay từ đầu.
- Nó đã đi qua được lớp bảo mật (Access Control) và tiến vào lớp xử lý dữ liệu.
- Lớp bảo mật chỉ được cấu hình để "canh gác" cho duy nhất phương thức `POST`

## User ID controlled by request parameter 
- leo thang theo chiều ngang, ta login vào tài khoản wiener:peter
- trên url đổi wiener sang carlos để truy cập được tài khoản của carlos
![](../../image/Pasted%20image%2020260501230414.png)


## User ID controlled by request parameter with unpredictable user IDS

- login vào tài khoản của wiener:peter, tìm bài post của carlos
![](../../image/Pasted%20image%2020260501230927.png)
- khi click vào ta thấy uid của carlos trên url
![](../../image/Pasted%20image%2020260501230947.png)

- quya lại /my-account đổi id sang carlod để vào tài khoản của carlos
![](../../image/Pasted%20image%2020260501231023.png)


## User ID controlled by request parameter with data leakage in redirect

- login vào tài khoản wiener:peter
- sau đó trên url đổi id từ wiener thành carlos
- web bị redirect về trang login nhưng trong response vẫn hiển thị api key của carlos
![](../../image/Pasted%20image%2020260501231838.png)

## User ID controlled by request parameter with  pasword disclosure
- login vào tài khoản wiener:peter
- trên url đổi id sang administrator
![](../../image/Pasted%20image%2020260501232314.png)
![](../../image/Pasted%20image%2020260501232424.png)

- thấy password của admin

## Insecure direct object references

- login vào tài khoản wiener:peter
- ở tab live chat, có chức năng download các script
- khi download ta thấy nó chỉ có từ 2.txt trở lên mà ko thấy 1.txt
![](../../image/Pasted%20image%2020260501233305.png)
- vào repeater để xem thử 1.txt
![](../../image/Pasted%20image%2020260501233227.png)
## Multi-step process with no access control on one step

- login vào tài khoản của admin và thử nâng quyền cho tài khoản carlos
- sau đó gửi 2 gói tin sang repeater rồi login vào tài khoản của wiener để lấy session của wiener
- trong repeater thay session của admin sang wiener và sửa carlos thành wiener rồi gửi lần lượt 2 gói tin đi
![](../../image/Pasted%20image%2020260502002637.png)
![](../../image/Pasted%20image%2020260502002457.png)
- server trả về 302 chứng tỏ ta đã nâng quyền thành công

![](../../image/Pasted%20image%2020260502002505.png)

## Referer-based access control

- login vào tài khoản admin và upgrade carlos
- gửi gói tin sang repeater, thay carlos thành wiener và cookie session của wiener
![](../../image/Pasted%20image%2020260502003027.png)
- trong reuqest đã có sẵn header referer: đây chính là "giấy thông hành" để đánh lừa Server rằng yêu cầu này đến từ trang quản trị.

![](../../image/Pasted%20image%2020260502003007.png)