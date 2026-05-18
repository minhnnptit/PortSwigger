java
[...]/?search=Fish+%26+Chips
```

Điều này đảm bảo rằng ký tự ampersand sẽ không bị hiểu nhầm là ký tự phân tách.

> **Lưu ý** Mặc dù ký tự khoảng trắng có thể được mã hóa dưới dạng `%20`, nó thường được biểu diễn bằng dấu cộng (`+`) thay vào đó, như trong ví dụ ở trên.

Mọi đầu vào dựa trên URL đều được máy chủ tự động giải mã URL trước khi gán cho các biến tương ứng. Điều này có nghĩa là, theo quan điểm của hầu hết máy chủ, các chuỗi như `%22`, `%3C` và `%3E` trong một tham số truy vấn tương đương với các ký tự `"`, `<` và `>` tương ứng. Nói cách khác, bạn có thể chèn dữ liệu đã mã hóa theo URL thông qua URL và nó thường vẫn được ứng dụng phía máy chủ giải thích đúng.

Thỉnh thoảng, bạn có thể thấy rằng WAF và những công cụ tương tự không giải mã URL đầu vào của bạn đúng cách khi kiểm tra. Trong trường hợp này, bạn có thể tuồn payload tới ứng dụng phía máy chủ đơn giản bằng cách mã hóa bất kỳ ký tự hoặc từ nào bị liệt vào danh sách đen. Ví dụ, trong một cuộc tấn công SQL injection, bạn có thể mã hóa các từ khóa, nên `SELECT` sẽ trở thành `%53%45%4C%45%43%54` và cứ như vậy.

## Double URL Encoding


Vì lý do này hay lý do khác, một số máy chủ thực hiện hai lần giải mã URL trên bất kỳ URL nào mà chúng nhận được. Điều này không nhất thiết là vấn đề nếu các cơ chế bảo mật cũng thực hiện giải mã hai lần khi kiểm tra đầu vào. Ngược lại, sự khác biệt này cho phép kẻ tấn công tuồn đầu vào độc hại tới back-end bằng cách đơn giản là mã hóa nó hai lần.

Giả sử bạn đang cố chèn một PoC XSS chuẩn, chẳng hạn `<img src=x onerror=alert(1)>`, thông qua một tham số truy vấn. Trong trường hợp này, URL có thể trông giống như sau:

```java
[...] /?search=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E
```

Khi kiểm tra yêu cầu, nếu một WAF thực hiện giải mã URL theo chuẩn, nó sẽ dễ dàng nhận diện payload nổi tiếng này. Yêu cầu sẽ bị chặn trước khi tới back-end. Nhưng nếu bạn mã hóa kép (double-encode) phần chèn mã? Trên thực tế, điều này có nghĩa là các ký tự `%` sẽ được thay thế bằng `%25`:

```java
[...] /?search=%253Cimg%2520src%253Dx%2520onerror%253Dalert(1)%253E
```

Vì WAF chỉ giải mã một lần, nó có thể không phát hiện được rằng yêu cầu là nguy hiểm. Nếu máy chủ back-end sau đó giải mã hai lần đầu vào này, payload sẽ được chèn thành công.

## HTML Encoding


Trong tài liệu HTML, một số ký tự nhất định cần được thoát (escape) hoặc mã hóa để ngăn trình duyệt hiểu nhầm chúng là một phần của đánh dấu. Việc này được thực hiện bằng cách thay thế các ký tự gây vấn đề bằng một tham chiếu (reference), bắt đầu bằng ký tự ampersand (&) và kết thúc bằng dấu chấm phẩy (;). Trong nhiều trường hợp, một tên có thể được dùng làm tham chiếu. Ví dụ, chuỗi `&colon;` biểu diễn ký tự dấu hai chấm.

Ngoài ra, tham chiếu có thể được cung cấp bằng mã điểm ký tự theo thập phân hoặc hệ hex, trong trường hợp này là `&#58;` và `&#x3a;` tương ứng.

Trong những vị trí cụ thể bên trong HTML, chẳng hạn như nội dung văn bản của một phần tử hoặc giá trị của một thuộc tính, trình duyệt sẽ tự động giải mã các tham chiếu này khi phân tích (parse) tài liệu. Khi chèn payload vào những vị trí như vậy, đôi khi bạn có thể lợi dụng điều này để che giấu payload cho các cuộc tấn công phía client, khiến chúng không bị phát hiện bởi các cơ chế phòng vệ phía server.

Nếu nhìn kỹ payload XSS trong ví dụ trước, lưu ý rằng payload đang được chèn vào bên trong một thuộc tính HTML, cụ thể là bộ xử lý sự kiện `onerror`. Nếu các kiểm tra phía server đang tìm kiếm payload `alert()` một cách rõ ràng, họ có thể sẽ không phát hiện được nếu bạn mã hóa HTML một hoặc nhiều ký tự:

```html
<img src=x onerror="&#x61;lert(1)">
```

Khi trình duyệt hiển thị trang, nó sẽ giải mã và thực thi payload đã chèn.

> Số 0 dẫn đầu

Thú vị là, khi dùng mã hóa HTML theo dạng thập phân hoặc hex, bạn có thể tùy ý thêm một số lượng không đổi các chữ số 0 ở trước mã điểm. Một số WAF và bộ lọc đầu vào khác không xử lý đầy đủ trường hợp này.

Nếu payload của bạn vẫn bị chặn sau khi mã hóa HTML, bạn có thể thoát bộ lọc chỉ bằng cách thêm vài chữ số 0 ở trước mã điểm:

```html
<a href="javascript&#00000000000058;alert(1)">Click me</a>
```

## XML Encoding


XML liên quan chặt chẽ đến HTML và cũng hỗ trợ mã hóa ký tự bằng cùng các chuỗi escape dạng số. Điều này cho phép bạn đưa các ký tự đặc biệt vào nội dung văn bản của các phần tử mà không làm hỏng cú pháp, điều này hữu ích khi kiểm thử XSS thông qua đầu vào dựa trên XML, ví dụ.

Ngay cả khi bạn không cần mã hóa bất kỳ ký tự đặc biệt nào để tránh lỗi cú pháp, bạn vẫn có thể lợi dụng hành vi này để che giấu payload tương tự như khi mã hóa HTML. Sự khác biệt là payload của bạn được server tự giải mã (server-side), thay vì được trình duyệt giải mã phía client. Điều này hữu ích để vượt qua WAF và các bộ lọc khác, vốn có thể chặn yêu cầu của bạn nếu chúng phát hiện các từ khóa liên quan tới tấn công SQL injection.

```xml
<stockCheck>
    <productId>
        123
    </productId>
    <storeId>
        999 &#x53;ELECT * FROM information_schema.tables
    </storeId>
</stockCheck>

```

## Unicode Escaping

Các chuỗi escape Unicode gồm tiền tố `\\u` theo sau bởi mã hex 4 chữ số cho ký tự. Ví dụ, `\\u003a` biểu diễn dấu hai chấm. ES6 cũng hỗ trợ dạng escape Unicode mới dùng ngoặc nhọn: `\\u{3a}`.

Khi phân tích chuỗi, hầu hết ngôn ngữ lập trình sẽ giải mã những escape Unicode này. Điều này bao gồm cả engine JavaScript được trình duyệt sử dụng. Khi chèn vào ngữ cảnh chuỗi, bạn có thể che giấu payload phía client bằng Unicode, giống như chúng ta đã làm với escape HTML ở ví dụ phía trên.

Ví dụ, giả sử bạn đang cố khai thác DOM XSS nơi đầu vào của bạn được truyền tới sink `eval()` dưới dạng một chuỗi. Nếu các lần thử ban đầu bị chặn, hãy thử escape một trong các ký tự như sau:

```jsx
eval("\\u0061lert(1)")
```

Vì điều này vẫn giữ ở dạng đã mã hóa phía server, nó có thể không bị phát hiện cho đến khi trình duyệt giải mã lại.

> **Lưu ý**
> 
> Bên trong một chuỗi, bạn có thể escape bất kỳ ký tự nào theo cách này. Tuy nhiên, bên ngoài chuỗi, escape một số ký tự sẽ gây lỗi cú pháp. Điều này bao gồm dấu ngoặc mở và đóng, ví dụ.

Cũng đáng lưu ý rằng dạng escape Unicode kiểu ES6 cho phép thêm số 0 dẫn đầu tùy ý, nên một số WAF có thể dễ bị qua mặt bằng kỹ thuật giống như ta đã dùng cho mã hóa HTML. Ví dụ:

```html
<a href="javascript:\\u{00000000061}alert(1)">Click me</a>

```

## Hex Escaping


Một lựa chọn khác khi chèn vào ngữ cảnh chuỗi là sử dụng các escape dạng hex, biểu diễn ký tự bằng mã điểm hex của nó, có tiền tố `\\x`. Ví dụ, chữ thường **a** được biểu diễn bằng `\\x61`.

Giống như các escape Unicode, những chuỗi này sẽ được giải mã phía client miễn là đầu vào được đánh giá như một chuỗi:

```jsx
eval("\\x61lert")
```

Lưu ý rằng đôi khi bạn cũng có thể che giấu các câu lệnh SQL theo cách tương tự bằng tiền tố `0x`. Ví dụ, `0x53454c454354` có thể được giải mã để tạo thành từ khóa `SELECT`.

## Octal Escaping


Escape bát phân hoạt động tương tự như escape hex, ngoại trừ việc các tham chiếu ký tự sử dụng hệ đếm cơ số 8 thay vì cơ số 16. Chúng được tiền tố bằng một dấu gạch chéo ngược đứng một mình (backslash), nghĩa là chữ thường `a` được biểu diễn bằng `\\141`.

```jsx
eval("\\141lert(1)")
```
## Multiple Encodings


Cần lưu ý rằng bạn có thể kết hợp nhiều kiểu mã hóa để giấu payload phía sau nhiều lớp obfuscation. Hãy xem URL `javascript:` trong ví dụ sau:

```html
<a href="javascript:&bsol;u0061lert(1)">Click me</a>
```

Trình duyệt sẽ đầu tiên HTML-decode `&bsol;`, dẫn tới một dấu gạch chéo ngược (backslash). Điều này biến các ký tự `u0061` vốn vô nghĩa thành escape unicode `\\u0061`:

```html
<a href="javascript:\\u0061lert(1)">Click me</a>
```

Sau đó chuỗi này được giải mã thêm một lần nữa để tạo thành một payload XSS hoạt động:

```html
<a href="javascript:alert(1)">Click me</a>
```

Rõ ràng, để chèn payload thành công theo cách này, bạn cần hiểu rõ các bước giải mã được thực hiện trên đầu vào của mình và thứ tự thực hiện các bước đó.
## SQL CHAR()

Mặc dù không hẳn là một dạng mã hóa, trong một số trường hợp, bạn có thể che giấu các cuộc tấn công SQL injection bằng cách dùng hàm `CHAR()`. Hàm này nhận một mã điểm theo thập phân hoặc hex và trả về ký tự tương ứng. Mã hex phải được tiền tố bằng `0x`. Ví dụ, cả `CHAR(83)` và `CHAR(0x53)` đều trả về chữ hoa `S`.

Bằng cách nối các giá trị trả về, bạn có thể dùng cách tiếp cận này để che giấu các từ khóa bị chặn. Ví dụ, ngay cả khi `SELECT` bị liệt vào danh sách đen, đoạn chèn sau đây ban đầu có vẻ vô hại:

```sql
CHAR(83)+CHAR(69)+CHAR(76)+CHAR(69)+CHAR(67)+CHAR(84)
```

Tuy nhiên, khi đoạn này được xử lý như SQL bởi ứng dụng, nó sẽ động cấu thành từ khóa `SELECT` và thực thi truy vấn đã chèn.
# Burp Scanner

<!-- TOC -->
## Mục lục

- [Double URL Encoding](#double-url-encoding)
- [HTML Encoding](#html-encoding)
- [XML Encoding](#xml-encoding)
- [Unicode Escaping](#unicode-escaping)
- [Hex Escaping](#hex-escaping)
- [Octal Escaping](#octal-escaping)
- [Multiple Encodings](#multiple-encodings)
- [SQL CHAR()](#sql-char)
- [**Scanning a specific request**](#scanning-a-specific-request)
- [**Scanning custom insertion points**](#scanning-custom-insertion-points)
- [**Scanning non-standard data structures**](#scanning-non-standard-data-structures)
- [Discovering vulnerabilities quickly with targeted scanning](#discovering-vulnerabilities-quickly-with-targeted-scanning)
- [Scanning non-standard data structures](#scanning-non-standard-data-structures-1)
<!-- /TOC -->

Trong phần này, chúng tôi sẽ chỉ cho bạn một số cách để tối ưu hóa quy trình kiểm thử thủ công bằng cách sử dụng Burp Scanner như một công cụ bổ trợ cho kiến thức và trực giác của bạn. Điều này không chỉ giúp bạn bao quát nhiều mục tiêu hơn, mà còn cho phép bạn dành thời gian ở những chỗ thực sự quan trọng thay vì phải lao vào những công việc chuẩn bị nhàm chán.

## **Scanning a specific request**

Khi bạn gặp một chức năng hoặc hành vi đáng chú ý, phản xạ đầu tiên có thể là gửi các yêu cầu liên quan tới Repeater hoặc Intruder để điều tra sâu hơn. Nhưng thường sẽ có lợi khi bạn đồng thời chuyển yêu cầu đó cho Burp Scanner. Nó có thể xử lý các khía cạnh lặp đi lặp lại của kiểm thử trong khi bạn dùng kỹ năng của mình ở những chỗ mang nhiều giá trị hơn.

Nếu bạn nhấp chuột phải vào một yêu cầu và chọn **Do active scan**, Burp Scanner sẽ sử dụng cấu hình mặc định để đánh giá chỉ riêng yêu cầu này.

![](../../image/Pasted%20image%2020260506054933.png)
Cách này có thể không phát hiện hết mọi lỗ hổng, nhưng nó có thể gợi ý ra một số điểm chỉ trong vài giây mà nếu làm tay có thể mất hàng giờ để tìm ra. Nó cũng có thể giúp bạn loại trừ một số tấn công gần như ngay lập tức. Bạn vẫn có thể thực hiện các kiểm thử nhắm mục tiêu hơn bằng các công cụ thủ công của Burp, nhưng bạn sẽ tập trung nỗ lực vào các đầu vào cụ thể và phạm vi lỗ hổng khả dĩ hẹp hơn.

Ngay cả khi bạn đã dùng Burp Scanner để tiến hành crawl và audit chung cho các mục tiêu mới, chuyển sang cách tiếp cận audit có mục tiêu hơn này có thể giảm đáng kể thời gian quét tổng thể.


## **Scanning custom insertion points**


Rõ ràng lợi ích của việc giới hạn quét vào một yêu cầu duy nhất, nhưng bạn có thể tiến xa hơn bằng cách chỉ kiểm thử các đầu vào cụ thể trong yêu cầu đó. Bạn có thể làm điều này từ trình soạn tin nhắn (message editor).

Bôi đen điểm chèn (insertion point) bạn quan tâm, sau đó nhấp phải và chọn **Scan selected insertion point**.
![](../../image/Pasted%20image%2020260506054941.png)
Tính năng này cho phép bạn tập trung vào đầu vào mà bạn quan tâm, thay vì quét thêm những nội dung mà bạn biết là ít khả năng mang lại giá trị.

Mặc dù bạn có thể định nghĩa một điểm chèn đơn bằng Intruder, thường sẽ nhanh hơn nếu dùng extension **Scan manual insertion point**. Bạn có thể bôi đen bất kỳ dãy ký tự nào trong yêu cầu - thường là giá trị tham số - và chọn **Extensions > Scan manual insertion point** từ menu ngữ cảnh.

Cách tiếp cận này có thể cho kết quả cực nhanh, cung cấp cho bạn thứ để làm việc chỉ trong vài giây. Nó cũng cho phép bạn chọn quét những đầu vào mà Burp Scanner thường không dùng, chẳng hạn như giá trị header tuỳ chỉnh.

## **Scanning non-standard data structures**

Vì bạn có thể tự do định nghĩa các điểm chèn (insertion points) ở bất kỳ vị trí nào, bạn cũng có thể nhắm tới một chuỗi con cụ thể bên trong một giá trị. Điều này, cùng với những thứ khác, hữu ích khi quét các cấu trúc dữ liệu phi chuẩn.

Khi xử lý các định dạng phổ biến, như JSON, Burp Scanner có thể phân tích dữ liệu và đặt payload vào vị trí chính xác mà không làm hỏng cấu trúc. Tuy nhiên, hãy cân nhắc một tham số có dạng như sau:

```
user=048857-carlos
```

Dựa trên trực giác, chúng ta có thể đoán rằng back-end sẽ xử lý giá trị này như hai giá trị riêng biệt: một ID nào đó và một tên người dùng (username), được phân tách bằng dấu gạch ngang. Tuy nhiên, Burp Scanner sẽ coi toàn bộ chuỗi này là một giá trị duy nhất. Kết quả là, nó sẽ chỉ đặt payload ở cuối tham số, hoặc thay thế toàn bộ giá trị.

Để hỗ trợ quét các cấu trúc dữ liệu phi chuẩn, bạn có thể quét chỉ một phần của tham số. Trong ví dụ này, bạn có thể muốn nhắm tới `carlos`. Bạn chỉ cần bôi đen `carlos` trong trình soạn tin nhắn, sau đó nhấp phải và chọn **Scan selected insertion point**.

# WU
- [x] Discovering vulnerabilities quickly with target scanning
- [ ] Scanning non-standard data structures

## Discovering vulnerabilities quickly with targeted scanning

- vào burp, cho url bài lab vào target để scan
![](../../image/Pasted%20image%2020260506155849.png)
- thu được tất cả các url của mục tiêu, ta thấy có file .js xử lí payload của phần checkstock
![](../../image/Pasted%20image%2020260506155944.png)

- Chức năng `Check stock` nhận dữ liệu đầu vào từ người dùng dưới định dạng `application/x-www-form-urlencoded` (ví dụ: `productId=1&storeId=1`). Tuy nhiên, ở phía backend (server-side), dữ liệu này được nhúng (embed) vào một tài liệu XML trước khi xử lý. Do ứng dụng không kiểm tra kỹ dữ liệu đầu vào và XML parser hỗ trợ tính năng XInclude, kẻ tấn công có thể chèn các namespace và thẻ XInclude độc hại để buộc server đọc các tệp tin nội bộ.

payload: `<qby xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></qby>`

![](../../image/Pasted%20image%2020260506160444.png)


## Scanning non-standard data structures

- khi login bằng wiener:peter, nhìn vào response của gói tin reqeust tới /my-account:
cookie trả về có dạng user:token bất kì
![](../../image/Pasted%20image%2020260506162649.png)
- giả định bên server chỉ kiểm tra tên user mà bỏ qua phần token phía sau


