```table-of-contents
```
# SSRF
## Khái niệm

---

Server-side request forgery là một lỗ hổng bảo mật web cho phép kẻ tấn công khiến ứng dụng phía máy chủ thực hiện các yêu cầu tới những đích không mong muốn.

Trong một cuộc tấn công SSRF điển hình, kẻ tấn công có thể khiến máy chủ thiết lập kết nối tới các dịch vụ chỉ dành cho nội bộ trong hạ tầng của tổ chức. Ở các trường hợp khác, họ có thể buộc máy chủ kết nối tới các hệ thống bên ngoài tùy ý. Điều này có thể làm rò rỉ dữ liệu nhạy cảm, chẳng hạn như thông tin xác thực ủy quyền.

![[Pasted image 20260502041000.png]]

---

## Hậu quả

---

Một cuộc tấn công SSRF thành công thường có thể dẫn đến các hành động trái phép hoặc truy cập dữ liệu trong nội bộ tổ chức. Điều này có thể xảy ra trong chính ứng dụng dễ bị tổn thương, hoặc trên các hệ thống backend khác mà ứng dụng có thể giao tiếp. Trong một số tình huống, lỗ hổng SSRF có thể cho phép kẻ tấn công thực thi lệnh tùy ý.

Một khai thác SSRF khiến máy chủ tạo kết nối tới các hệ thống bên thứ ba bên ngoài có thể dẫn đến các cuộc tấn công độc hại tiếp theo. Những cuộc tấn công này có thể trông như bắt nguồn từ tổ chức đang lưu trữ ứng dụng dễ bị tấn công.

---

## Tấn công SSRF

---

Các cuộc tấn công SSRF thường lợi dụng các mối quan hệ tin cậy để leo thang từ ứng dụng dễ bị tổn thương và thực hiện các hành động trái phép. Những mối quan hệ tin cậy này có thể tồn tại đối với chính máy chủ hoặc đối với các hệ thống backend khác trong cùng một tổ chức.

---

### Server

---

Trong một cuộc tấn công SSRF nhắm vào máy chủ, kẻ tấn công khiến ứng dụng thực hiện một yêu cầu HTTP quay trở lại chính máy chủ đang lưu trữ ứng dụng thông qua giao diện mạng loopback. Điều này thường liên quan đến việc cung cấp một URL có tên máy chủ (hostname) như 127.0.0.1 (một địa chỉ IP dành riêng trỏ đến bộ điều hợp loopback) hoặc localhost (tên thường dùng cho cùng bộ điều hợp).

Ví dụ, hãy hình dung một ứng dụng mua sắm cho phép người dùng xem một mặt hàng có còn trong kho tại một cửa hàng cụ thể hay không. Để cung cấp thông tin tồn kho, ứng dụng phải truy vấn nhiều REST API backend khác nhau. Ứng dụng làm điều này bằng cách truyền URL đến endpoint API backend liên quan thông qua một yêu cầu HTTP từ phía frontend. Khi người dùng xem trạng thái tồn kho của một mặt hàng, trình duyệt của họ thực hiện yêu cầu sau:

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://stock.weliketoshop.net:8080/product/stock/check%3FproductId%3D6%26storeId%3D1
```

Điều này khiến máy chủ thực hiện một yêu cầu đến URL đã chỉ định, truy xuất trạng thái tồn kho và trả về cho người dùng.

Trong ví dụ này, kẻ tấn công có thể sửa đổi yêu cầu để chỉ định một URL cục bộ trên máy chủ:

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://localhost/admin
```

Máy chủ sẽ lấy nội dung của URL `/admin` và trả về cho người dùng.

Kẻ tấn công có thể truy cập URL `/admin`, nhưng chức năng quản trị thông thường chỉ khả dụng cho người dùng đã xác thực. Điều này có nghĩa là kẻ tấn công sẽ không thấy điều gì đáng chú ý. Tuy nhiên, nếu yêu cầu đến URL `/admin` xuất phát từ máy cục bộ, các kiểm soát truy cập thông thường sẽ bị bỏ qua. Ứng dụng sẽ cấp toàn quyền truy cập vào chức năng quản trị vì yêu cầu có vẻ như bắt nguồn từ một vị trí đáng tin cậy.

Vì sao các ứng dụng lại hành xử như vậy và ngầm tin cậy các yêu cầu đến từ máy cục bộ? Điều này có thể xuất phát từ nhiều lý do:

- Kiểm tra kiểm soát truy cập có thể được triển khai ở một thành phần khác đặt trước máy chủ ứng dụng. Khi kết nối được thực hiện quay lại chính máy chủ, bước kiểm tra này bị bỏ qua.
- Vì mục đích khôi phục thảm họa, ứng dụng có thể cho phép truy cập quản trị mà không cần đăng nhập đối với bất kỳ người dùng nào đến từ máy cục bộ. Điều này cung cấp cách để quản trị viên khôi phục hệ thống nếu họ mất thông tin xác thực, và giả định rằng chỉ người dùng hoàn toàn đáng tin mới truy cập trực tiếp từ máy chủ.
- Giao diện quản trị có thể lắng nghe trên một cổng khác với ứng dụng chính và có thể không thể được người dùng truy cập trực tiếp.

Những mối quan hệ tin cậy kiểu này, khi các yêu cầu xuất phát từ máy cục bộ được xử lý khác với các yêu cầu thông thường, thường khiến SSRF trở thành một lỗ hổng nghiêm trọng.

---

### Back-end System

---

Trong một số trường hợp, máy chủ ứng dụng có thể tương tác với các hệ thống backend mà người dùng không thể truy cập trực tiếp. Các hệ thống này thường có địa chỉ IP riêng (private) không thể định tuyến (non-routable). Các hệ thống backend thông thường được bảo vệ bởi cấu trúc liên kết mạng, vì vậy chúng thường có tư thế bảo mật yếu hơn. Trong nhiều trường hợp, các hệ thống backend nội bộ chứa chức năng nhạy cảm có thể được truy cập mà không cần xác thực bởi bất kỳ ai có thể tương tác với các hệ thống này.

Trong ví dụ trước, giả sử có một giao diện quản trị tại URL backend `http://192.168.0.68/admin`. Kẻ tấn công có thể gửi yêu cầu sau để khai thác lỗ hổng SSRF và truy cập giao diện quản trị:

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://192.168.0.68/admin
```

---

## Bảo mật

---

Thường thấy các ứng dụng vừa tồn tại hành vi SSRF vừa triển khai những biện pháp phòng vệ nhằm ngăn chặn việc khai thác độc hại. Tuy nhiên, các biện pháp này nhiều khi vẫn có thể bị lách qua.

---

### **Blacklist-based input filters**

---

Một số ứng dụng chặn đầu vào chứa các hostname như `127.0.0.1` và `localhost`, hoặc các URL nhạy cảm như `/admin`. Trong tình huống này, bạn thường có thể lách bộ lọc bằng các kỹ thuật sau:

- Sử dụng các biểu diễn IP thay thế của `127.0.0.1`, chẳng hạn `2130706433`, `017700000001`, hoặc `127.1`.
- Đăng ký một tên miền của riêng bạn trỏ (resolve) về `127.0.0.1`. Bạn có thể sử dụng `spoofed.burpcollaborator.net` cho mục đích này.
- Che giấu (obfuscate) các chuỗi bị chặn bằng mã hóa URL (URL encoding) hoặc thay đổi chữ hoa/thường.
- Cung cấp một URL do bạn kiểm soát, URL này chuyển hướng (redirect) tới URL mục tiêu. Hãy thử sử dụng các mã chuyển hướng khác nhau, cũng như các giao thức khác nhau cho URL đích. Ví dụ, chuyển từ URL http: sang https: trong quá trình chuyển hướng đã được chứng minh có thể vượt qua một số bộ lọc chống SSRF.

---

### **Whitelist-based input filters**

---

Một số ứng dụng chỉ cho phép các đầu vào khớp với danh sách trắng các giá trị được phép. Bộ lọc có thể tìm sự khớp ở phần đầu của đầu vào hoặc ở phần nằm bên trong nó. Bạn có thể vượt qua bộ lọc này bằng cách khai thác các điểm không nhất quán trong việc phân tích cú pháp URL.

Đặc tả URL chứa một số đặc điểm rất dễ bị bỏ sót khi triển khai việc phân tách và xác thực URL theo cách “ad-hoc” như thế này:

- Bạn có thể nhúng thông tin xác thực vào URL trước hostname, bằng ký tự `@`. Ví dụ:
    
    ```
    <https://expected-host:fakepassword@evil-host>
    ```
    
- Bạn có thể dùng ký tự `#` để chỉ định một URL fragment. Ví dụ:
    
    ```
    <https://evil-host#expected-host>
    ```
    
- Bạn có thể tận dụng hệ phân cấp đặt tên DNS để đặt phần giá trị bắt buộc vào một tên miền đủ đầy (FQDN) do bạn kiểm soát. Ví dụ:
    
    ```
    <https://expected-host.evil-host>
    ```
    
- Bạn có thể mã hóa URL (URL-encode) các ký tự để gây nhiễu code phân tích URL. Điều này đặc biệt hữu ích nếu phần code triển khai bộ lọc xử lý các ký tự đã mã hóa URL khác với phần code thực hiện yêu cầu HTTP ở backend. Bạn cũng có thể thử mã hóa hai lần (double-encoding); một số máy chủ giải mã URL theo kiểu đệ quy đối với đầu vào chúng nhận được, điều này có thể dẫn đến các sai khác bổ sung.
    
- Bạn có thể kết hợp các kỹ thuật này với nhau.
    

---

### Open redirection

---

Đôi khi có thể vượt qua các biện pháp phòng vệ dựa trên bộ lọc bằng cách khai thác một lỗ hổng chuyển hướng mở.

Trong ví dụ trước, giả sử URL do người dùng gửi lên được kiểm tra nghiêm ngặt để ngăn chặn việc khai thác độc hại của hành vi SSRF. Tuy nhiên, ứng dụng với các URL được phép lại chứa lỗ hổng chuyển hướng mở. Miễn là API được dùng để thực hiện yêu cầu HTTP ở backend hỗ trợ chuyển hướng, bạn có thể dựng một URL thỏa mãn bộ lọc và dẫn đến việc yêu cầu bị chuyển hướng tới đích backend mong muốn.

Ví dụ, ứng dụng chứa một lỗ hổng chuyển hướng mở trong đó URL sau:

```
/product/nextProduct?currentProductId=6&path=http://evil-user.net
```

trả về một chuyển hướng tới:

```
<http://evil-user.net>
```

Bạn có thể tận dụng lỗ hổng chuyển hướng mở để vượt qua bộ lọc URL và khai thác lỗ hổng SSRF như sau:

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://weliketoshop.net/product/nextProduct?currentProductId=6&path=http://192.168.0.68/admin
```

Khai thác SSRF này hoạt động vì ứng dụng trước tiên xác thực rằng URL stockAPI được cung cấp nằm trên một miền được cho phép, và điều đó là đúng. Ứng dụng sau đó gửi yêu cầu tới URL đã cung cấp, điều này kích hoạt chuyển hướng mở. Nó theo chuyển hướng và gửi yêu cầu tới URL nội bộ do kẻ tấn công lựa chọn.

---

## Blind SSRF

---

### Khái niệm

---

Lỗ hổng SSRF mù xảy ra khi bạn có thể khiến ứng dụng phát sinh một yêu cầu HTTP ở backend tới URL do bạn cung cấp, nhưng phản hồi từ yêu cầu backend đó không được trả về trong phản hồi frontend của ứng dụng.

SSRF mù khó khai thác hơn nhưng đôi khi có thể dẫn đến thực thi mã từ xa (RCE) hoàn toàn trên máy chủ hoặc các thành phần backend khác.

---

### Hậu quả

---

Tác động của lỗ hổng SSRF mù thường thấp hơn so với các lỗ hổng SSRF đầy đủ thông tin do tính chất một chiều của chúng. Chúng không thể bị khai thác một cách đơn giản để truy xuất dữ liệu nhạy cảm từ các hệ thống backend, mặc dù trong một số tình huống vẫn có thể bị khai thác để đạt được thực thi mã từ xa hoàn toàn.

---

### Nhận biết

---

Cách đáng tin cậy nhất để phát hiện lỗ hổng SSRF mù là sử dụng các kỹ thuật out-of-band (OAST). Điều này liên quan đến việc cố gắng kích hoạt một yêu cầu HTTP tới một hệ thống bên ngoài do bạn kiểm soát và giám sát các tương tác mạng với hệ thống đó.

Cách dễ và hiệu quả nhất để dùng kỹ thuật out-of-band là sử dụng Burp Collaborator. Bạn có thể dùng Burp Collaborator để tạo các tên miền duy nhất, gửi chúng trong payload tới ứng dụng và theo dõi mọi tương tác với các tên miền đó. Nếu quan sát thấy một yêu cầu HTTP đến xuất phát từ ứng dụng, thì ứng dụng đó dễ bị SSRF.

> **Lưu ý**
> 
> Khi kiểm thử lỗ hổng SSRF, khá phổ biến việc quan sát thấy một tra cứu DNS (DNS look-up) cho tên miền Collaborator đã cung cấp, nhưng không có yêu cầu HTTP tiếp theo. Điều này thường xảy ra vì ứng dụng đã cố gắng thực hiện một yêu cầu HTTP tới tên miền đó (khiến xuất hiện tra cứu DNS ban đầu) nhưng yêu cầu HTTP thực tế bị chặn bởi cơ chế lọc ở cấp mạng. Khá phổ biến là hạ tầng cho phép lưu lượng DNS đi ra ngoài (outbound) vì cần cho nhiều mục đích, nhưng lại chặn các kết nối HTTP tới những đích không mong đợi.

Việc chỉ đơn thuần xác định một lỗ hổng SSRF mù có thể kích hoạt các yêu cầu HTTP out-of-band tự thân nó không cung cấp một con đường dẫn tới khả năng khai thác. Vì bạn không thể xem phản hồi từ yêu cầu backend, hành vi này không thể được dùng để khám phá nội dung trên các hệ thống mà máy chủ ứng dụng có thể truy cập. Tuy nhiên, nó vẫn có thể được tận dụng để thăm dò các lỗ hổng khác trên chính máy chủ hoặc trên các hệ thống backend khác. Bạn có thể quét mù không gian địa chỉ IP nội bộ, gửi các payload được thiết kế để phát hiện các lỗ hổng đã biết. Nếu các payload đó cũng sử dụng kỹ thuật out-of-band mù, bạn có thể phát hiện ra một lỗ hổng nghiêm trọng trên một máy chủ nội bộ chưa được vá.

Một hướng khác để khai thác lỗ hổng SSRF mù là khiến ứng dụng kết nối tới một hệ thống do kẻ tấn công kiểm soát và trả về các phản hồi độc hại cho HTTP client thực hiện kết nối. Nếu bạn có thể khai thác một lỗ hổng phía client nghiêm trọng trong phần triển khai HTTP của máy chủ, bạn có thể đạt được thực thi mã từ xa trong hạ tầng ứng dụng.

---

### Tìm bề mặt tấn công ẩn

---

Nhiều lỗ hổng server-side request forgery khá dễ phát hiện vì lưu lượng thông thường của ứng dụng có các tham số yêu cầu chứa URL đầy đủ. Những ví dụ SSRF khác thì khó xác định hơn.

---

#### URL - part

---

Đôi khi, ứng dụng chỉ đặt một hostname hoặc một phần đường dẫn URL vào các tham số của yêu cầu. Giá trị được gửi lên sau đó sẽ được ghép (server-side) thành một URL đầy đủ để thực hiện request. Nếu giá trị đó dễ dàng được nhận ra là một hostname hoặc một đường dẫn URL, thì bề mặt tấn công tiềm năng có thể hiển nhiên. Tuy nhiên, khả năng khai thác thành SSRF “đầy đủ” có thể bị hạn chế vì bạn không kiểm soát được toàn bộ URL sẽ được yêu cầu.

---

#### URL in data

---

Một số ứng dụng truyền dữ liệu ở các định dạng cho phép nhúng URL, và các URL này có thể được parser của định dạng gọi ra để xử lý. Ví dụ rõ ràng nhất là định dạng **XML**, vốn được sử dụng rộng rãi trong các ứng dụng web để truyền dữ liệu có cấu trúc từ client đến server. Khi một ứng dụng chấp nhận dữ liệu ở định dạng XML và phân tích cú pháp (parse) nó, ứng dụng có thể dễ bị tấn công **XXE injection**. Nó cũng có thể dễ bị tấn công **SSRF thông qua XXE**. (Phần này sẽ được trình bày chi tiết hơn khi nói về lỗ hổng XXE injection.)

---

#### Referer header

---

Một số ứng dụng sử dụng phần mềm phân tích (analytics) phía máy chủ để theo dõi khách truy cập. Phần mềm này thường ghi lại header **Referer** trong các yêu cầu để theo dõi các liên kết đến. Thông thường, phần mềm phân tích này sẽ truy cập (visit) bất kỳ URL bên thứ ba nào xuất hiện trong Referer header. Việc này nhằm phân tích nội dung của các site giới thiệu (referring sites), bao gồm cả anchor text được sử dụng trong liên kết đến.

Do đó, **Referer header** thường là một bề mặt tấn công hữu ích cho lỗ hổng SSRF.

# WU
- [x] Basic SSRF against the local server
- [x] Basic SSRF against another back-end system
- [x] SSRF with blacklist-based input filter
- [x] SSRF with whitelist-based input filter
- [x] SSRF with filter bypass via open redirection vulnerability
- [x] Blind SSRF with out-of-band detection
- [x] Blind SSRF with Shellshock exploitation

## Basic SSRF against the local server
- ở request check stock, thấy stockAPI đi kèm 1 link http tới server để tìm thông tin, ta có thể tấn công ssrf ở đây

![[Pasted image 20260502042733.png]]

- điền thêm url để xóa carlos
![[Pasted image 20260502042813.png]]


## Basic SSRF against against another back-end system
- bài lab yêu cầu chúng ta sử dụng function ở phần check stock để scan dải 192.168.1.x  ở port 8080 để xóa user carlos
- gửi request tới intruder
![[Pasted image 20260502043141.png]]
![[Pasted image 20260502043248.png]]

- attack và xem kết quả
![[Pasted image 20260502043313.png]]

- ở repeater sửa gói tin để xóa carlos
![[Pasted image 20260502043541.png]]

## Blind SSRF with out-of-band detection
 - bài lab sử dụng phần mềm phân tích dữ liệu, phần mềm này sẽ truy xuất URL được chỉ định trong header Referer khi một trang sản phẩm được tải.
- ta cần request HTTP đến máy chủ Burp Collaborator để solved bài alb
- gửi request tới repeater và thay phần referer thành url của burp colla
![[Pasted image 20260502044344.png]]
- ở bên tab burp colla ấn poll now để solved
![[Pasted image 20260502044407.png]]

## SSRF with blacklist-based input filter
- lab yêu cầu thay đổi URL kiểm tra tồn kho để truy cập giao diện quản trị tại http://localhost/admin và xóa người dùng carlos.
![[Pasted image 20260502045033.png]]
- khi thử /admin hay ip đều bị block
- ta cần obfucatate trước khi đưa vào
![[Pasted image 20260502045126.png]]
- admin cũng cần obfuscate
![[Pasted image 20260502045854.png]]

- ![[Pasted image 20260502045930.png]]

## SSRF with filter bypass via open redirection vulnerability
- bài lab yêu cầu check url ở checkstock để truy cập /admin và xóa carlos
![[Pasted image 20260502050333.png]]
- thử thay đổi path sang /admin
![[Pasted image 20260502050404.png]]
- copy toàn bộ url ở get để gửi sang request POST
![[Pasted image 20260502050650.png]]


![[Pasted image 20260502050758.png]]

## Blind SSRF with Shellshock exploitation
- bài lab sử dụng phần mềm phân tích truy xuất URL được chỉ định trong tiêu đề Referer khi trang sản phẩm được tải. sử dụng chức năng này để tấn công SSRF mù nhắm vào192.168.0.X trên cổng 8080 sử dụng một payload Shellshock 
- gửi gói tin get product id sang intruder
![[Pasted image 20260502051438.png]]
![[Pasted image 20260502052024.png]]
## SSRF with whitelist-based input filter
- bài lab yêu cầu  truy cập vào /admin và xóa carlos
![[Pasted image 20260502052405.png]]
- url cần có stock.weliketoshop.net
![[Pasted image 20260502052547.png]]
