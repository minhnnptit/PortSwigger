```table-of-contents
```
# API testing

## API recon

---

Để bắt đầu kiểm thử API, trước tiên bạn cần thu thập càng nhiều thông tin về API càng tốt, nhằm xác định **bề mặt tấn công (attack surface)** của nó.

Bước đầu tiên là **xác định các endpoint của API**. Endpoint là những vị trí mà API nhận request liên quan đến một tài nguyên (resource) cụ thể trên server. Ví dụ, hãy xem xét request sau:

```
GET /api/books HTTP/1.1
Host: example.com
```

Endpoint API trong request này là `/api/books`. Khi gửi request này, API sẽ phản hồi danh sách các cuốn sách từ thư viện. Một endpoint khác có thể là `/api/books/mystery`, dùng để lấy danh sách các cuốn sách thuộc thể loại “mystery”.

Sau khi xác định được các endpoint, bạn cần hiểu rõ cách tương tác với chúng. Điều này giúp bạn xây dựng các HTTP request hợp lệ để tiến hành kiểm thử API. Cụ thể, bạn cần thu thập thông tin về:

- **Dữ liệu đầu vào (input data)** mà API xử lý, bao gồm cả tham số bắt buộc và tùy chọn.
- **Kiểu request** mà API chấp nhận, bao gồm các HTTP method được hỗ trợ (GET, POST, PUT, DELETE, ...) và các định dạng media (JSON, XML, v.v.).
- **Rate limiting và cơ chế xác thực (authentication mechanisms)** mà API áp dụng.

---

## **API documentation**

---

API thường được cung cấp **tài liệu hướng dẫn** để lập trình viên biết cách sử dụng và tích hợp với chúng.

Tài liệu có thể tồn tại dưới hai dạng: **dành cho con người đọc (human-readable)** và **dành cho máy đọc (machine-readable)**:

- **Human-readable documentation**: được thiết kế để lập trình viên dễ dàng hiểu cách sử dụng API. Nó có thể bao gồm giải thích chi tiết, ví dụ minh họa và các kịch bản sử dụng thực tế.
- **Machine-readable documentation**: được thiết kế để phần mềm xử lý, phục vụ các tác vụ tự động như tích hợp API hoặc kiểm thử/validate API. Tài liệu dạng này thường được viết bằng các định dạng có cấu trúc như **JSON** hoặc **XML**.

Tài liệu API thường được công khai, đặc biệt nếu API được thiết kế cho lập trình viên bên ngoài sử dụng. Trong trường hợp này, khi tiến hành **API recon**, bước đầu tiên luôn là **xem xét tài liệu API**.

Ngay cả khi tài liệu API không được công khai, bạn vẫn có thể truy cập được nó bằng cách duyệt qua các ứng dụng có sử dụng API đó.

Để thực hiện, bạn có thể dùng **Burp Scanner** để crawl toàn bộ API. Ngoài ra, bạn cũng có thể duyệt ứng dụng thủ công bằng **Burp's browser**. Hãy tìm kiếm các endpoint có khả năng liên quan đến tài liệu API, ví dụ:

```
/api
/swagger/index.html
/openapi.json
```

Khi bạn phát hiện một endpoint cho một resource, hãy nhớ kiểm tra cả **base path**. Ví dụ, nếu bạn tìm thấy endpoint:

```
/api/swagger/v1/users/123
```

thì bạn nên tiếp tục điều tra các đường dẫn liên quan như:

```
/api/swagger/v1
/api/swagger
/api
```

Bạn cũng có thể sử dụng **Intruder** cùng với một danh sách các đường dẫn phổ biến (common paths) để dò tìm tài liệu API.

Bạn có thể tận dụng nhiều công cụ tự động để phân tích bất kỳ tài liệu API dạng **machine-readable** nào mà bạn tìm được.

- Bạn có thể dùng **Burp Scanner** để crawl và audit tài liệu **OpenAPI**, hoặc các tài liệu khác ở định dạng **JSON** hoặc **YAML**.
- Bạn cũng có thể phân tích tài liệu OpenAPI bằng cách sử dụng **OpenAPI Parser BApp** (một Burp Extension).
- Ngoài ra, bạn có thể dùng các công cụ chuyên dụng để kiểm thử những endpoint được mô tả trong tài liệu, chẳng hạn như **Postman** hoặc **SoapUI**.

👉 Trong thực tế pentest, việc có được file **openapi.json** hoặc **swagger.yaml** là cực kỳ giá trị, vì:

- Nó thường liệt kê đầy đủ các **endpoint** và **parameter**.
- Có thể tiết lộ cơ chế **authentication/authorization**.
- Dễ dàng nhập trực tiếp vào Postman hoặc Burp để tự động hóa kiểm thử.

---

## **Identifying API endpoints**

---

Bạn cũng có thể thu thập được rất nhiều thông tin bằng cách duyệt qua các ứng dụng có sử dụng API. Đây là việc đáng thực hiện ngay cả khi bạn đã có tài liệu API, bởi vì đôi khi tài liệu có thể **không chính xác hoặc đã lỗi thời**.

- Bạn có thể sử dụng **Burp Scanner** để crawl ứng dụng, sau đó **tự tay phân tích** các bề mặt tấn công tiềm năng bằng **Burp’s browser**.
- Khi duyệt ứng dụng, hãy để ý đến **các mẫu URL** gợi ý về API endpoint, chẳng hạn như `/api/`.
- Đồng thời, cần chú ý đến **các file JavaScript** – bởi chúng có thể chứa các tham chiếu tới những API endpoint mà bạn chưa từng kích hoạt trực tiếp qua trình duyệt.
- Burp Scanner có khả năng **tự động trích xuất một số endpoint** trong quá trình crawl, nhưng nếu bạn muốn **khai thác mạnh hơn**, có thể sử dụng **JS Link Finder BApp**.
- Ngoài ra, bạn cũng có thể **thủ công review các file JavaScript** trong Burp để tìm thêm endpoint.

👉 Trong thực chiến, phân tích **JavaScript client-side** thường giúp tìm được:

- **Hidden endpoints** (chỉ được gọi qua AJAX/Fetch).
- **API key hardcode** trong source JS.
- **Debug/test endpoints** bị bỏ quên.

Sau khi bạn đã xác định được các **API endpoint**, hãy tiến hành tương tác với chúng bằng cách sử dụng **Burp Repeater** và **Burp Intruder**. Việc này giúp bạn quan sát hành vi của API và phát hiện thêm **bề mặt tấn công (attack surface)** mới.

Ví dụ, bạn có thể thử kiểm tra cách API phản hồi khi thay đổi **HTTP method** (GET, POST, PUT, DELETE, …) hoặc **media type** (JSON, XML, form-data, …).

Trong quá trình tương tác với API, hãy phân tích kỹ các **thông báo lỗi** và **phản hồi trả về**. Nhiều khi chúng tiết lộ những thông tin hữu ích, cho phép bạn xây dựng một HTTP request hợp lệ hoặc phát hiện ra lỗ hổng tiềm ẩn.

👉 Trong thực chiến, việc quan sát kỹ response có thể dẫn đến:

- **Information disclosure** (stack trace, error code, debug message).
- Xác định **parameter validation** (tham số nào là bắt buộc, kiểu dữ liệu).
- Phát hiện các cơ chế **authorization bypass** khi thử thay đổi method (ví dụ: `GET` bị chặn nhưng `POST`/`PUT` lại hoạt động).

**HTTP method** xác định hành động sẽ được thực hiện trên một tài nguyên (resource). Ví dụ:

- **GET** – Truy xuất dữ liệu từ một resource.
- **PATCH** – Áp dụng các thay đổi một phần cho resource.
- **OPTIONS** – Truy xuất thông tin về các loại request method mà một resource hỗ trợ.

Một **API endpoint** có thể hỗ trợ nhiều HTTP method khác nhau. Do đó, việc kiểm thử tất cả các method tiềm năng là rất quan trọng trong quá trình phân tích endpoint. Điều này có thể giúp bạn phát hiện thêm chức năng ẩn, từ đó mở rộng **bề mặt tấn công (attack surface)**.

Ví dụ: endpoint `/api/tasks` có thể hỗ trợ các method sau:

```
GET /api/tasks       → Truy xuất danh sách task
POST /api/tasks      → Tạo một task mới
DELETE /api/tasks/1  → Xóa task có ID = 1
```

Bạn có thể sử dụng **HTTP verbs list** tích hợp trong **Burp Intruder** để tự động thử lần lượt nhiều HTTP method khác nhau.

> ⚠️ **Lưu ý** Khi kiểm thử các HTTP method, hãy ưu tiên thao tác với **đối tượng có mức độ ưu tiên thấp**. Điều này giúp bạn tránh gây ra hậu quả không mong muốn, chẳng hạn như thay đổi dữ liệu quan trọng hoặc tạo ra quá nhiều bản ghi rác trong hệ thống.

👉 Trong thực chiến, kỹ thuật này thường được gọi là **HTTP Verb Tampering** hoặc **Method Enumeration**, có thể dẫn đến:

- **Bypass authentication/authorization** (ví dụ: `GET` bị chặn nhưng `HEAD` hoặc `OPTIONS` vẫn trả dữ liệu).
- **Privilege escalation** nếu một method không được bảo vệ đúng cách (ví dụ: `DELETE` hoặc `PUT` mở mà không cần quyền).
- **Information disclosure** từ response của `OPTIONS`.

Các **API endpoint** thường yêu cầu dữ liệu được gửi theo một định dạng cụ thể. Do đó, API có thể phản hồi khác nhau tùy thuộc vào **content type** của dữ liệu trong request. Việc thay đổi content type có thể giúp bạn:

- **Kích hoạt lỗi** và thu được thông tin hữu ích.
- **Bypass** các cơ chế phòng thủ yếu kém.
- **Khai thác sự khác biệt trong logic xử lý**. Ví dụ: một API có thể an toàn khi xử lý dữ liệu JSON, nhưng lại dễ bị tấn công **injection** khi xử lý XML.

Để thay đổi content type, bạn chỉnh sửa **Content-Type header** trong request, đồng thời định dạng lại phần **request body** cho phù hợp.

Bạn có thể sử dụng **Content Type Converter BApp** để tự động chuyển đổi dữ liệu trong request giữa **XML** và **JSON**.

Sau khi bạn đã xác định được một số **API endpoint ban đầu**, bạn có thể sử dụng **Burp Intruder** để dò tìm thêm các endpoint ẩn.

Ví dụ: giả sử bạn đã tìm được một endpoint để cập nhật thông tin người dùng:

```
PUT /api/user/update
```

Để phát hiện các endpoint ẩn, bạn có thể dùng Burp Intruder để fuzz vị trí `/update` trong path với một wordlist chứa các hàm phổ biến khác, chẳng hạn như:

```
/api/user/delete
/api/user/add
```

Khi tìm kiếm các endpoint ẩn, hãy sử dụng **wordlist** dựa trên:

- **Quy ước đặt tên phổ biến của API** (common API naming conventions).
- **Thuật ngữ trong ngành** (industry terms).
- **Từ khóa đặc thù của ứng dụng mục tiêu**, dựa trên quá trình recon ban đầu (ví dụ: “order”, “invoice”, “cart”, … trong ứng dụng thương mại điện tử).

👉 Trong thực chiến, kỹ thuật này thường gọi là **Endpoint Fuzzing / API Path Bruteforcing** và có thể dẫn đến:

- **Phát hiện tính năng chưa được tài liệu hóa (undocumented endpoints)**.
- **Admin/debug endpoints** bị bỏ quên.
- **Functionality abuse** (ví dụ: `/delete`, `/disable`, `/export`).

---

## **Finding hidden parameters**

---

Trong quá trình **API recon**, bạn có thể phát hiện ra các **tham số (parameters) không được tài liệu hóa**, nhưng API vẫn hỗ trợ. Việc khai thác các tham số này có thể cho phép bạn thay đổi hành vi của ứng dụng.

**Burp Suite** cung cấp nhiều công cụ giúp xác định tham số ẩn:

- **Burp Intruder**: cho phép bạn tự động phát hiện tham số ẩn bằng cách sử dụng **wordlist các tên tham số phổ biến** để thay thế tham số hiện có hoặc thêm tham số mới. Hãy đảm bảo bổ sung cả các tên có liên quan đến ứng dụng mục tiêu, dựa trên kết quả recon ban đầu.
- **Param Miner BApp**: công cụ này có thể tự động đoán tới **65.536 tên tham số cho mỗi request**. Param Miner còn có khả năng tự động dự đoán các tên tham số liên quan đến ứng dụng, dựa trên thông tin thu thập được từ scope.
- **Content Discovery tool**: giúp phát hiện **các nội dung không được liên kết trực tiếp** từ giao diện người dùng, bao gồm cả tham số ẩn.

👉 Trong thực chiến, tham số ẩn có thể dẫn đến:

- **Bypass logic** (ví dụ: `?debug=true`, `?admin=1`).
- **Thay đổi hành vi API** (ẩn/hiện dữ liệu, bật chế độ test, override quyền).
- **Parameter Pollution / Tampering** → tạo ra lỗi xử lý hoặc bỏ qua validation.
- **Mass Assignment** nếu backend binding trực tiếp tham số → chiếm quyền hoặc thay đổi field nhạy cảm (role, isAdmin, balance).

---

## **Mass assignment vulnerabilities**

---

**Mass assignment** (còn gọi là **auto-binding**) có thể vô tình tạo ra **các tham số ẩn**.

Lỗ hổng này xảy ra khi **framework phần mềm** tự động ánh xạ (bind) các tham số từ request tới các trường (fields) của một **đối tượng nội bộ**.

Kết quả là ứng dụng có thể hỗ trợ và xử lý cả những tham số **không bao giờ được lập trình viên dự định chấp nhận**. Điều này mở ra khả năng kẻ tấn công thêm, sửa hoặc lợi dụng các field nhạy cảm, dẫn đến thay đổi hành vi ứng dụng hoặc leo thang đặc quyền.

Do **Mass Assignment** tạo ra tham số từ các **field trong object**, bạn thường có thể phát hiện ra các tham số ẩn bằng cách **thủ công phân tích các object** mà API trả về.

Ví dụ:

- Khi thực hiện request:

```
PATCH /api/users/
```

cho phép user cập nhật `username` và `email`, với dữ liệu JSON:

```json
{
    "username": "wiener",
    "email": "wiener@example.com"
}
```

- Trong khi đó, một request song song:

```
GET /api/users/123
```

trả về dữ liệu JSON:

```json
{
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "isAdmin": "false"
}
```

Điều này cho thấy có khả năng các tham số **id** và **isAdmin** cũng được **bind** tới object nội bộ của user, bên cạnh những tham số mà người dùng được phép chỉnh sửa (`username`, `email`).

Để kiểm tra xem bạn có thể **sửa đổi giá trị tham số ẩn `isAdmin`** hay không, hãy thêm nó vào request **PATCH** như sau:

```json
{
    "username": "wiener",
    "email": "wiener@example.com",
    "isAdmin": false
}
```

Ngoài ra, thử gửi một request PATCH với giá trị **không hợp lệ** cho tham số `isAdmin`:

```json
{
    "username": "wiener",
    "email": "wiener@example.com",
    "isAdmin": "foo"
}
```

Nếu ứng dụng phản hồi khác nhau giữa hai trường hợp, điều này cho thấy giá trị **không hợp lệ** có ảnh hưởng đến logic xử lý, còn giá trị hợp lệ thì không. Đây có thể là dấu hiệu cho thấy tham số `isAdmin` **có thể được cập nhật bởi user**.

Sau đó, thử gửi một request PATCH với `isAdmin` đặt thành `true` để khai thác lỗ hổng:

```json
{
    "username": "wiener",
    "email": "wiener@example.com",
    "isAdmin": true
}
```

Nếu giá trị `isAdmin` trong request được ánh xạ (bound) trực tiếp vào object user **mà không qua kiểm tra/validation hoặc lọc dữ liệu (sanitization)**, thì user `wiener` có thể **bị cấp quyền admin một cách sai lệch**.

Để xác minh điều này, hãy đăng nhập và duyệt ứng dụng dưới user `wiener` để kiểm tra xem bạn có thể truy cập vào các chức năng dành riêng cho admin hay không.

---

## **Preventing vulnerabilities in APIs**

---

Khi thiết kế API, hãy đảm bảo rằng vấn đề bảo mật được xem xét ngay từ đầu. Đặc biệt, hãy chắc chắn rằng bạn:

- Bảo mật tài liệu của mình nếu bạn không có ý định để API được truy cập công khai.
- Đảm bảo tài liệu luôn được cập nhật để những người kiểm thử hợp pháp có thể có cái nhìn đầy đủ về bề mặt tấn công của API.
- Áp dụng danh sách cho phép (allowlist) đối với các phương thức HTTP được chấp nhận.
- Xác thực rằng kiểu nội dung (content type) là đúng như mong đợi cho từng yêu cầu hoặc phản hồi.
- Sử dụng các thông báo lỗi chung để tránh tiết lộ thông tin có thể hữu ích cho kẻ tấn công.
- Áp dụng các biện pháp bảo vệ trên tất cả các phiên bản của API, không chỉ phiên bản đang chạy trong môi trường sản xuất.
- Để ngăn chặn lỗ hổng gán hàng loạt (mass assignment), hãy lập danh sách cho phép các thuộc tính có thể được người dùng cập nhật, và lập danh sách chặn các thuộc tính nhạy cảm mà người dùng không nên cập nhật.

---

## **Server-side parameter pollution**

---

Một số hệ thống có chứa API nội bộ không thể truy cập trực tiếp từ Internet. **Ô nhiễm tham số phía máy chủ** xảy ra khi một website nhúng đầu vào của người dùng vào một yêu cầu phía máy chủ tới API nội bộ mà không mã hóa đầy đủ. Điều này có nghĩa là kẻ tấn công có thể thao túng hoặc chèn thêm tham số, cho phép chúng, ví dụ như:

- Ghi đè lên các tham số hiện có.
- Thay đổi hành vi của ứng dụng.
- Truy cập dữ liệu trái phép.

Bạn có thể kiểm thử bất kỳ đầu vào nào của người dùng để phát hiện ô nhiễm tham số, ví dụ: **tham số truy vấn, trường biểu mẫu, header, và tham số đường dẫn URL** đều có thể dễ bị khai thác.

> **Lưu ý**
> 
> Lỗ hổng này đôi khi được gọi là **HTTP parameter pollution**. Tuy nhiên, thuật ngữ này cũng được sử dụng để chỉ một kỹ thuật bypass tường lửa ứng dụng web (WAF). Để tránh nhầm lẫn, trong chủ đề này chúng ta chỉ gọi là **server-side parameter pollution**.
> 
> Ngoài ra, mặc dù tên gọi tương tự, lớp lỗ hổng này **hầu như không liên quan** đến **server-side prototype pollution**.

---

### **Query string**

---

Để kiểm thử **server-side parameter pollution** trong query string, bạn chèn các ký tự cú pháp của query như `#`, `&`, và `=` vào đầu vào của mình và quan sát cách ứng dụng phản hồi.

Hãy xem xét một ứng dụng dễ bị tấn công, cho phép bạn tìm kiếm người dùng khác dựa trên **username**. Khi bạn tìm kiếm một người dùng, trình duyệt của bạn sẽ gửi yêu cầu sau:

```
GET /userSearch?name=peter&back=/home
```

Để truy xuất thông tin người dùng, máy chủ sẽ gửi một yêu cầu đến API nội bộ như sau:

```
GET /users/search?name=peter&publicProfile=true
```

Bạn có thể sử dụng ký tự `#` đã được mã hóa URL (**`%23`**) để cố gắng **cắt cụt** (truncate) request phía server. Để giúp bạn dễ dàng diễn giải phản hồi, bạn cũng có thể thêm một chuỗi ký tự sau dấu `#`.

Ví dụ, bạn có thể chỉnh sửa query string thành:

```
GET /userSearch?name=peter%23foo&back=/home
```

Phía front-end sẽ cố gắng truy cập URL sau:

```
GET /users/search?name=peter#foo&publicProfile=true
```

> Lưu ý: Bạn bắt buộc phải URL-encode ký tự #. Nếu không, ứng dụng front-end sẽ coi nó như một fragment identifier (định danh đoạn tài liệu) và sẽ không gửi nó đến API nội bộ.

Hãy xem xét phản hồi để tìm manh mối liệu query có bị cắt cụt hay không.

- Nếu phản hồi trả về thông tin người dùng **peter**, có khả năng server-side query đã bị cắt cụt.
- Nếu phản hồi trả về thông báo lỗi như **Invalid name**, ứng dụng có thể đã coi `foo` là một phần của username. Điều này gợi ý rằng server-side request **chưa bị cắt cụt**.

Nếu bạn có thể **cắt cụt** được request phía server, điều này sẽ loại bỏ yêu cầu rằng trường `publicProfile` phải được đặt thành `true`. Bạn có thể khai thác điều này để truy xuất các **profile người dùng không công khai**.

Bạn có thể sử dụng ký tự `&` đã được mã hóa URL (**`%26`**) để cố gắng **thêm một tham số thứ hai** vào request phía server.

Ví dụ, bạn có thể chỉnh sửa query string như sau:

```
GET /userSearch?name=peter%26foo=xyz&back=/home
```

Điều này dẫn đến việc server-side gửi request tới API nội bộ như sau:

```
GET /users/search?name=peter&foo=xyz&publicProfile=true
```

Hãy phân tích phản hồi để tìm manh mối về cách tham số bổ sung được xử lý:

- Nếu phản hồi **không thay đổi**, điều này có thể chỉ ra rằng tham số đã được chèn thành công nhưng bị ứng dụng **bỏ qua**.

Để có cái nhìn đầy đủ hơn, bạn cần tiếp tục **kiểm thử thêm** với nhiều biến thể khác nhau.

Nếu bạn có thể **sửa đổi query string**, bạn có thể thử **thêm một tham số hợp lệ** khác vào request phía server.

> **Tài liệu liên quan**
> 
> Để biết cách **xác định các tham số có thể chèn** vào query string, tham khảo phần **Finding hidden parameters**.

Ví dụ:

Nếu bạn đã xác định được tham số `email`, bạn có thể thêm nó vào query string như sau:

```
GET /userSearch?name=peter%26email=foo&back=/home
```

Khi đó, server sẽ gửi request tới API nội bộ như sau:

```
GET /users/search?name=peter&email=foo&publicProfile=true
```

Hãy phân tích phản hồi để tìm dấu hiệu xem **tham số bổ sung được xử lý như thế nào**.

Để xác nhận ứng dụng có bị **Server-Side Parameter Pollution (SSPP)** hay không, bạn có thể thử **ghi đè tham số gốc** bằng cách chèn thêm một tham số khác **cùng tên**.

Ví dụ:

Bạn sửa query string thành:

```
GET /userSearch?name=peter%26name=carlos&back=/home
```

Khi đó, server sẽ gửi request nội bộ đến API như sau:

```
GET /users/search?name=peter&name=carlos&publicProfile=true
```

API nội bộ sẽ nhận thấy có **2 tham số `name`**. Ảnh hưởng của việc này phụ thuộc vào cách ứng dụng xử lý tham số trùng lặp, và điều này thay đổi theo công nghệ web:

- **PHP**: chỉ lấy **tham số cuối cùng** → kết quả tìm kiếm `carlos`.
- **[ASP.NET](http://ASP.NET)**: **ghép giá trị** của các tham số → kết quả `peter,carlos`, có thể gây lỗi `Invalid username`.
- **Node.js / Express**: chỉ lấy **tham số đầu tiên** → kết quả vẫn là `peter`, không thay đổi.

Khả năng khai thác

Nếu bạn có thể **ghi đè thành công tham số gốc**, bạn có thể khai thác để leo thang.

Ví dụ: chèn `name=administrator` → request có thể trở thành:

```
GET /users/search?name=administrator&publicProfile=true
```

Điều này có thể cho phép bạn **đăng nhập với tư cách administrator** hoặc truy cập dữ liệu nhạy cảm.

---

### REST Path

---

Một **RESTful API** có thể đặt **tên tham số và giá trị** trực tiếp trong **đường dẫn URL**, thay vì trong query string.

Ví dụ, xem xét đường dẫn:

```
/api/users/123
```

Đường dẫn này có thể được phân tích như sau:

- `/api` → endpoint gốc của API
- `/users` → resource (tài nguyên), ở đây là **người dùng**
- `/123` → tham số, là **ID của user cụ thể**

Giả sử ứng dụng cho phép chỉnh sửa hồ sơ người dùng dựa trên **username**. Request được gửi như sau:

```
GET /edit_profile.php?name=peter
```

Điều này dẫn đến request nội bộ (server-side request) được gửi đi:

```
GET /api/private/users/peter
```

Kẻ tấn công có thể **manipulate tham số trong URL path** để khai thác API.

Để kiểm tra lỗ hổng này, ta thêm **chuỗi Path Traversal** vào tham số và quan sát phản hồi của ứng dụng.

Ví dụ, gửi giá trị URL-encoded `peter/../admin` cho tham số `name`:

```
GET /edit_profile.php?name=peter%2f..%2fadmin
```

Khi đó request phía server sẽ trở thành:

```
GET /api/private/users/peter/../admin
```

Nếu **client phía server** hoặc **back-end API** thực hiện **chuẩn hóa đường dẫn (path normalization)**, thì đường dẫn này sẽ được giải quyết thành:

```
/api/private/users/admin
```

---

### **Structured data formats**

---

Kẻ tấn công có thể thao túng các tham số để khai thác **lỗ hổng trong quá trình xử lý các định dạng dữ liệu cấu trúc** của server, chẳng hạn như **JSON** hoặc **XML**.

Để kiểm thử điều này, bạn chèn **dữ liệu cấu trúc bất ngờ** vào đầu vào của người dùng và quan sát cách server phản hồi.

Xem xét một ứng dụng cho phép người dùng chỉnh sửa hồ sơ, sau đó áp dụng các thay đổi bằng request tới **API phía server**.

Khi bạn chỉnh sửa tên, trình duyệt gửi request:

```
POST /myaccount
name=peter
```

Điều này dẫn tới request phía server:

```
PATCH /users/7312/update
{"name":"peter"}
```

Bạn có thể thử thêm tham số `access_level` vào request như sau:

```
POST /myaccount
name=peter","access_level":"administrator
```

Nếu **đầu vào người dùng được thêm trực tiếp vào JSON phía server mà không có validation hoặc sanitization đầy đủ**, request phía server sẽ trở thành:

```
PATCH /users/7312/update
{name="peter","access_level":"administrator"}
```

Điều này có thể dẫn tới việc **user `peter` được cấp quyền administrator**.

> **Tài liệu liên quan**
> 
> Để biết cách xác định các tham số có thể chèn vào query string, xem phần **Finding hidden parameters**.

Xem xét một ví dụ tương tự, nhưng **đầu vào người dùng ở phía client là dữ liệu JSON**.

Khi bạn chỉnh sửa tên, trình duyệt gửi request:

```
POST /myaccount
{"name": "peter"}
```

Điều này dẫn tới request phía server:

```
PATCH /users/7312/update
{"name":"peter"}
```

Bạn có thể thử thêm tham số `access_level` vào request như sau:

```
POST /myaccount
{"name": "peter\\",\\"access_level\\":\\"administrator"}
```

Nếu **đầu vào người dùng được giải mã (decoded) và thêm trực tiếp vào JSON phía server mà không có encoding đầy đủ**, request phía server sẽ trở thành:

```
PATCH /users/7312/update
{"name":"peter","access_level":"administrator"}
```

Điều này một lần nữa có thể dẫn tới việc **user `peter` được cấp quyền administrator**.

**Lưu ý về Structured Format Injection**

- Injection định dạng cấu trúc cũng có thể xảy ra trong **response**.
- Ví dụ: nếu đầu vào của người dùng được lưu trong cơ sở dữ liệu một cách an toàn, sau đó nhúng vào **JSON response** từ back-end API mà không encoding đầy đủ, thì vẫn có thể khai thác.
- Bạn có thể phát hiện và khai thác **structured format injection** trong response tương tự như cách thực hiện với request.

> **Lưu ý**
> 
> Ví dụ trên sử dụng **JSON**, nhưng **server-side parameter pollution** có thể xảy ra với bất kỳ định dạng dữ liệu cấu trúc nào.
> 
> - Ví dụ với **XML**, xem phần **XInclude attacks** trong chủ đề **XML External Entity (XXE) Injection**.

---

## Tools

---

Burp bao gồm các công cụ tự động có thể giúp bạn phát hiện các lỗ hổng **Server-Side Parameter Pollution (SSPP)**.

- **Burp Scanner** tự động phát hiện những **biến đổi đầu vào đáng ngờ** khi thực hiện audit. Những biến đổi này xảy ra khi ứng dụng nhận đầu vào từ người dùng, xử lý theo một cách nào đó, rồi tiếp tục xử lý kết quả.
    - Hành vi này không nhất thiết là một lỗ hổng, vì vậy bạn cần **kiểm thử thêm bằng các kỹ thuật thủ công** đã nêu ở trên.
    - Để biết thêm thông tin, xem phần **Suspicious input transformation issue definition**.
- Bạn cũng có thể sử dụng **Backslash Powered Scanner BApp** để xác định các lỗ hổng **server-side injection**.
    - Công cụ này phân loại các đầu vào thành: **boring** (không đáng chú ý), **interesting** (đáng chú ý), hoặc **vulnerable** (dễ bị khai thác).
    - Bạn sẽ cần điều tra các đầu vào **interesting** bằng các kỹ thuật thủ công như đã nêu ở trên.
    - Để biết thêm chi tiết, xem tài liệu **Backslash Powered Scanning: hunting unknown vulnerability classes whitepaper**.

---

## Ngăn chặn Server-Side Parameter Pollution

---

Để ngăn chặn **server-side parameter pollution**, hãy:

- Sử dụng **allowlist** để xác định các ký tự **không cần mã hóa**.
- Đảm bảo rằng **tất cả các đầu vào khác từ người dùng được mã hóa** trước khi đưa vào request phía server.
- Đồng thời, đảm bảo rằng **mọi đầu vào tuân thủ đúng định dạng và cấu trúc** mà ứng dụng mong đợi.
# WU

- [ ] Exploiting an API endpoint using documentation
- [ ] Exploiting unused API endpoint
- [ ] Finding and exploiting an unused API endpoint
- [ ] Exploiting a mass assignment vulnerability
- [ ] Exploiting server-side parameter pollution in a REST URL

## Exploiting an API endpoint using documentation

dùng burp scan trang web, ta thấy có url của api
![](../../image/Pasted%20image%2020260502224453.png)

![](../../image/Pasted%20image%2020260502224534.png)

## Exploiting server-side parameter pollution in a query string

- thử vào forgot password và nhập administrator
![](../../image/Pasted%20image%2020260502231111.png)
- nếu thay username bằng giá trị khác ko hợp lệ:
![](../../image/Pasted%20image%2020260502231129.png)
- thử nối chuỗi vào sau admin +. hệ thống vẫn xử lí
![](../../image/Pasted%20image%2020260502231242.png)

- thử thay dấu & thành dấu #
![](../../image/Pasted%20image%2020260502231346.png)
=> bên server có 1 para tên là field
![](../../image/Pasted%20image%2020260502231518.png)
khi thử lại với payload trên thì response quay trở lại là invalid field, gửi reques sang intruder và chọn serverside variable name ở phần payload thay vào x

![](../../image/Pasted%20image%2020260502231740.png)
- sau khi bruteforce thấy có 2 field trả vè 200 là email và username
![](../../image/Pasted%20image%2020260502231823.png)
![](../../image/Pasted%20image%2020260502231830.png)
- quay trở lại request get /static/js/forgotPassword.js, có 1 hàm chứa param: reset_token
![](../../image/Pasted%20image%2020260502232027.png)

![](../../image/Pasted%20image%2020260502232123.png)

- trên url ở web thêm param reset_token và giá trị vào để đổi mật khẩu của admin và truy cập
![](../../image/Pasted%20image%2020260502232256.png)

## Finding and exploiting an unused API endpoint
- bài lab yêu cầu ta tìm 1 api ẩn để mua được cái áo 1337$
login và mua thử cái áo, tất nhiên là ko được
![](../../image/Pasted%20image%2020260502232551.png)
- ở burp thấy 1 số reqeust đáng chú ý:
![](../../image/Pasted%20image%2020260502232627.png)
- thử xem ngoài GET dùng methods khác thì server trả về gì
với method PATCH thấy response đáng chú ý:
![](../../image/Pasted%20image%2020260502232826.png)

- chuột phải chọn extension để convert sang json (extension content type convert trên bwapp) và gửi
![](../../image/Pasted%20image%2020260502233017.png)

![](../../image/Pasted%20image%2020260502233045.png)
- thêm các param theo response trả về
![](../../image/Pasted%20image%2020260502233150.png)
- khi quay lại xem giá thì đã thay đổi
![](../../image/Pasted%20image%2020260502233210.png)
- vậy đơn giản cuối cùng ta gửi lại requst với price = 0
![](../../image/Pasted%20image%2020260502233314.png)
- quay lại web và mua áo
## Exploiting a mass assignment vulnerability
- bài lab yêu cầu ta tìm 1 lỗ hổng mass assignent để mua duduojcw áo 1337$
- ở burp ta có 2 request khi mua áo
![](../../image/Pasted%20image%2020260502233648.png)
![](../../image/Pasted%20image%2020260502233656.png)
- có thể thấy là ở reqeust GET có nhiều param hơn so với POST, thử xem có thể thêm các param này vào request khác để test thử
- khi thêm param item_price sang thì server vẫn xử lí, nhưng vẫn chưa thanh toàn thành công, thêm nốt param còn lại
![](../../image/Pasted%20image%2020260502233844.png)

- khi đổi thành giảm giá 100% thì server đã báo thành công, trả về 1 localtion

![](../../image/Pasted%20image%2020260502234010.png)
![](../../image/Pasted%20image%2020260502234055.png)

## Exploiting server-side parameter pollution in a REST URL
- ở bài lab này ta cần tìm cách login vào admin và xóa carlos
request forgotpassword trả về dữ liệu dạng json
![](../../image/Pasted%20image%2020260502234403.png)- khi thử với username khác

![](../../image/Pasted%20image%2020260502234435.png)
![](../../image/Pasted%20image%2020260502234456.png)

- thử param polution với & và #
![](../../image/Pasted%20image%2020260502234635.png)
=> có khả năng input sẽ được đưa vào như là path trong url để truy vấn trên server

- **confirm là server bị path traversal**
![](../../image/Pasted%20image%2020260502234804.png)
- tìm ra thư mục root
![](../../image/Pasted%20image%2020260502234852.png)
- bruteforce các api 
![](../../image/Pasted%20image%2020260502235116.png)
- tất cả đều tra về 500 nhưng openapi.json có length dài hơn bất thường
![](../../image/Pasted%20image%2020260502235203.png)

![](../../image/Pasted%20image%2020260502235450.png)
![](../../image/Pasted%20image%2020260502235458.png)
- thấy có phần path, copy đoạn này
![](../../image/Pasted%20image%2020260502235621.png)
![](../../image/Pasted%20image%2020260502235714.png)
- trường field chưa có giá trị, ta tìm cách bruteforce, chon server side variable name
![](../../image/Pasted%20image%2020260502235932.png)
- sau khi bruteforce, ta thấy có 2 trường username và email trả về 200
![](../../image/Pasted%20image%2020260503000112.png)
![](../../image/Pasted%20image%2020260503000151.png)
![](../../image/Pasted%20image%2020260503000202.png)

- quay lại tìm kiếm ở file forgotpassword.js, ta thấy có hàm xử lí token khi quên mật khẩu và param 
![](../../image/Pasted%20image%2020260503000349.png)
- thử xem field passwordResetToken có hợp lệ không
![](../../image/Pasted%20image%2020260503000444.png)

- sau cùng, nhập token vào url để đổi mật khẩu và login admin


