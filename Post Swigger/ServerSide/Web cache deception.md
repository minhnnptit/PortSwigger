```table-of-contents
```
# Web cache deception
## Giới thiệu

Web cache deception là một lỗ hổng cho phép kẻ tấn công đánh lừa bộ nhớ đệm web (cache) lưu trữ nội dung nhạy cảm, có tính động. Nguyên nhân xuất phát từ sự khác biệt trong cách máy chủ cache và máy chủ nguồn (origin) xử lý các yêu cầu.

Trong một cuộc tấn công web cache deception, kẻ tấn công dụ nạn nhân truy cập một URL độc hại, khiến trình duyệt của nạn nhân gửi một yêu cầu mơ hồ để lấy nội dung nhạy cảm. Bộ nhớ đệm hiểu nhầm đây là yêu cầu đối với tài nguyên tĩnh và lưu phản hồi lại. Sau đó, kẻ tấn công chỉ cần yêu cầu cùng URL để truy cập phản hồi đã được cache, từ đó chiếm quyền truy cập trái phép vào thông tin riêng tư.
![](../../image/Pasted%20image%2020260503001715.png)
> **Lưu ý**
> 
> Cần phân biệt web cache deception với web cache poisoning. Cả hai đều khai thác cơ chế bộ nhớ đệm, nhưng cách thức khác nhau:
> 
> - **Web cache poisoning** thao túng các khóa cache (cache keys) để chèn nội dung độc hại vào một phản hồi đã được cache, sau đó phản hồi độc hại này sẽ được phân phát cho người dùng khác.
> - **Web cache deception** lợi dụng các quy tắc cache để đánh lừa cache lưu trữ nội dung nhạy cảm hoặc riêng tư, mà kẻ tấn công có thể truy cập về sau.
> 
> Để biết thông tin chi tiết hơn về web cache poisoning, hãy tham khảo chủ đề _Web cache poisoning_ trong PortSwigger Academy.

## Web caches

**Web cache** là một hệ thống nằm giữa máy chủ gốc (origin server) và người dùng. Khi một client gửi yêu cầu đến một tài nguyên tĩnh, yêu cầu này trước tiên sẽ được chuyển đến cache.

- Nếu cache **không có bản sao** của tài nguyên (gọi là _cache miss_), yêu cầu sẽ được chuyển tiếp đến máy chủ gốc để xử lý và phản hồi. Phản hồi sau đó được gửi về cache trước khi được trả về cho người dùng. Cache sẽ dùng một tập hợp quy tắc cấu hình sẵn để quyết định có lưu phản hồi này hay không.
- Khi có một yêu cầu khác cho cùng tài nguyên tĩnh trong tương lai, cache sẽ trả trực tiếp bản sao đã lưu cho người dùng (gọi là _cache hit_).
![](../../image/Pasted%20image%2020260503001746.png)

Caching đã trở thành một phần phổ biến và then chốt trong việc phân phối nội dung web, đặc biệt với sự phát triển mạnh mẽ của **Content Delivery Networks (CDNs)**. CDNs sử dụng caching để lưu trữ các bản sao nội dung trên nhiều máy chủ phân tán khắp thế giới.

Nhờ đó, CDNs tăng tốc độ phân phối bằng cách phục vụ nội dung từ máy chủ gần người dùng nhất, giúp giảm thời gian tải bằng cách rút ngắn quãng đường mà dữ liệu phải di chuyển.

---

### Cache keys

---

Khi cache nhận một HTTP request, nó cần quyết định xem có phản hồi nào đã được lưu trong cache để phục vụ trực tiếp hay không, hoặc phải chuyển tiếp request đến máy chủ gốc.

Cache đưa ra quyết định này bằng cách tạo ra một **“cache key”** từ các thành phần của HTTP request. Thông thường, cache key bao gồm **đường dẫn URL (URL path)** và **tham số truy vấn (query parameters)**, nhưng nó cũng có thể bao gồm nhiều thành phần khác như **HTTP headers** hoặc **content type**.

Nếu cache key của request đến trùng với cache key của một request trước đó, cache sẽ coi chúng là tương đương và phục vụ lại bản sao phản hồi đã được lưu trữ.

---

### Cache rules

---

**Cache rules** quyết định những gì có thể được cache và trong bao lâu.

Thông thường, cache rules được thiết lập để lưu trữ **tài nguyên tĩnh (static resources)**, vốn ít thay đổi và thường được tái sử dụng trên nhiều trang. Ngược lại, **nội dung động (dynamic content)** thường **không được cache** vì có khả năng chứa thông tin nhạy cảm, đồng thời cần đảm bảo người dùng luôn nhận được dữ liệu mới nhất trực tiếp từ máy chủ.

Các cuộc tấn công **web cache deception** khai thác cách các cache rules được áp dụng, vì vậy cần nắm rõ một số loại quy tắc phổ biến, đặc biệt là những quy tắc dựa trên chuỗi xác định trong đường dẫn URL của request. Ví dụ:

- **Static file extension rules** – Quy tắc dựa trên phần mở rộng tệp của tài nguyên được yêu cầu, ví dụ: `.css` cho stylesheet hoặc `.js` cho JavaScript.
- **Static directory rules** – Quy tắc áp dụng cho tất cả các URL có tiền tố xác định. Thường dùng để nhắm đến các thư mục chỉ chứa tài nguyên tĩnh, ví dụ: `/static` hoặc `/assets`.
- **File name rules** – Quy tắc áp dụng cho các tệp cụ thể cần thiết cho hoạt động web và hiếm khi thay đổi, ví dụ: `robots.txt` hoặc `favicon.ico`.

Ngoài ra, cache cũng có thể triển khai **quy tắc tùy chỉnh** dựa trên các tiêu chí khác, chẳng hạn như tham số URL hoặc phân tích động.

---

## Xây dựng cuộc tấn công

---

Nói chung, việc xây dựng một **cuộc tấn công web cache deception** cơ bản thường bao gồm các bước sau:

1. **Xác định endpoint mục tiêu**
    - Tìm một endpoint trả về **phản hồi động có chứa thông tin nhạy cảm**.
    - Kiểm tra kỹ phản hồi trong Burp, vì một số thông tin nhạy cảm có thể **không hiển thị trên trang web đã render**.
    - Tập trung vào các endpoint hỗ trợ **GET, HEAD, hoặc OPTIONS**, vì các request thay đổi trạng thái của máy chủ gốc (như POST, PUT, DELETE) thường không được cache.
2. **Xác định sự khác biệt trong cách cache và máy chủ gốc phân tích đường dẫn URL**. Sự khác biệt này có thể xuất hiện trong cách chúng:
    - **Ánh xạ URL sang tài nguyên**.
    - **Xử lý các ký tự phân tách (delimiter characters)**.
    - **Chuẩn hóa đường dẫn (path normalization)**.
3. **Tạo URL độc hại**
    - Dựa trên sự khác biệt đã phát hiện, craft một URL độc hại để **đánh lừa cache lưu trữ phản hồi động**.
    - Khi nạn nhân truy cập URL này, phản hồi chứa thông tin của họ sẽ được lưu vào cache.
    - Sau đó, bạn có thể dùng Burp gửi request đến cùng URL để lấy **bản phản hồi đã cache chứa dữ liệu của nạn nhân**.
    - **Lưu ý:** Tránh thực hiện trực tiếp trong trình duyệt, vì một số ứng dụng có thể **redirect người dùng không có session** hoặc **vô hiệu hóa dữ liệu cục bộ**, che giấu đi lỗ hổng.

### Sử dụng Cache Buster


Khi kiểm thử sự khác biệt và xây dựng khai thác web cache deception, bạn cần đảm bảo rằng **mỗi request gửi đi đều có cache key khác nhau**. Nếu không, bạn có thể nhận lại phản hồi từ cache thay vì từ máy chủ gốc, làm sai lệch kết quả kiểm thử.

Vì **đường dẫn URL** và **các tham số truy vấn (query parameters)** thường được đưa vào cache key, bạn có thể thay đổi cache key bằng cách:

- Thêm một query string vào URL path.
- Thay đổi giá trị query string mỗi lần gửi request.

👉 Để tự động hóa việc này, bạn có thể dùng **Param Miner extension** trong Burp Suite:

1. Sau khi cài đặt extension, vào menu **Param Miner > Settings**.
2. Chọn **Add dynamic cachebuster**.
3. Từ lúc này, Burp sẽ tự động thêm một query string duy nhất vào mỗi request bạn gửi.
4. Bạn có thể xem các query string đã được thêm trong tab **Logger**.

---

### Phát hiện phản hồi được cache

---

Trong quá trình kiểm thử, việc nhận biết phản hồi có được lấy từ cache hay không là rất quan trọng. Để làm điều này, bạn cần xem xét **response headers** và **thời gian phản hồi (response times)**.

Một số **response header** có thể cho biết phản hồi đã được cache, ví dụ:

- **X-Cache header** cung cấp thông tin phản hồi có được lấy từ cache hay không. Các giá trị điển hình:
    - `X-Cache: hit` → Phản hồi được lấy từ cache.
    - `X-Cache: miss` → Cache không chứa phản hồi cho cache key của request, nên phản hồi được lấy từ máy chủ gốc. Trong hầu hết trường hợp, phản hồi này sau đó sẽ được cache. (Để xác nhận, hãy gửi lại request và kiểm tra xem giá trị có chuyển thành `hit` hay không.)
    - `X-Cache: dynamic` → Nội dung được máy chủ gốc tạo ra động. Thông thường, điều này nghĩa là phản hồi **không phù hợp để cache**.
    - `X-Cache: refresh` → Nội dung trong cache đã lỗi thời và cần được làm mới hoặc xác thực lại.
- **Cache-Control header** có thể chứa các chỉ thị (directive) cho phép cache, ví dụ: `public` kèm theo `max-age` lớn hơn 0.
    - Tuy nhiên, đây chỉ là gợi ý rằng tài nguyên **có thể được cache**. Không phải lúc nào nó cũng đồng nghĩa với việc phản hồi thực sự được cache, vì đôi khi cache có thể **ghi đè** lên header này.
- **Thời gian phản hồi (response time)**: Nếu bạn thấy có sự khác biệt lớn về tốc độ phản hồi cho cùng một request, phản hồi nhanh hơn thường cho thấy nó được phục vụ từ cache.

---

## Lỗ hổng

---

### **Static extension cache rules**

---

Các quy tắc cache thường nhắm đến tài nguyên tĩnh bằng cách khớp những phần mở rộng tệp phổ biến như `.css` hoặc `.js`. Đây là hành vi mặc định trong hầu hết các CDN.

Nếu tồn tại khác biệt trong cách **cache** và **máy chủ gốc (origin)** ánh xạ đường dẫn URL tới tài nguyên hoặc xử lý **ký tự phân tách (delimiters)**, kẻ tấn công có thể craft một yêu cầu tới **tài nguyên động** nhưng kèm **phần mở rộng tĩnh**—phần mở rộng này bị máy chủ gốc **bỏ qua**, nhưng lại được **cache** xem là hợp lệ để lưu trữ.

---

#### Path mapping discrepancies

---

**URL path mapping** là quá trình ánh xạ các đường dẫn URL tới tài nguyên trên máy chủ, chẳng hạn như file, script hoặc lệnh thực thi. Có nhiều kiểu ánh xạ khác nhau tùy theo framework và công nghệ sử dụng. Hai kiểu phổ biến nhất là **traditional URL mapping** và **RESTful URL mapping**:

1. Traditional URL mapping

Ánh xạ trực tiếp tới file trong hệ thống. Ví dụ:

```
<http://example.com/path/in/filesystem/resource.html>
```

- `http://example.com` → máy chủ.
- `/path/in/filesystem/` → đường dẫn thư mục trên hệ thống file máy chủ.
- `resource.html` → file cụ thể được truy cập.

1. RESTful URL mapping

Không ánh xạ trực tiếp tới cấu trúc file vật lý. Thay vào đó, nó trừu tượng hóa đường dẫn thành các phần logic trong API. Ví dụ:

```
<http://example.com/path/resource/param1/param2>
```

- `http://example.com` → máy chủ.
- `/path/resource/` → endpoint đại diện cho một tài nguyên.
- `param1` và `param2` → tham số đường dẫn được server xử lý để sinh phản hồi.

Sự **khác biệt trong cách cache và origin server ánh xạ URL path** có thể dẫn tới lỗ hổng **web cache deception**.

Ví dụ:

```
<http://example.com/user/123/profile/wcd.css>
```

- Máy chủ gốc (sử dụng **REST-style mapping**) có thể hiểu đây là request tới endpoint `/user/123/profile` và trả về thông tin profile của user `123`. Phần `wcd.css` bị bỏ qua như một tham số không quan trọng.
- Cache (sử dụng **traditional mapping**) có thể hiểu đây là request tới file `wcd.css` trong thư mục `/user/123/profile`. Vì đường dẫn kết thúc bằng `.css`, cache sẽ coi đây là tài nguyên tĩnh và lưu lại.

👉 Kết quả: Cache lưu trữ **profile data nhạy cảm** như thể đó là file CSS, từ đó tạo ra lỗ hổng.

---

#### Exploit

---

Để khai thác lỗ hổng web cache deception xuất phát từ **path mapping discrepancies**, bạn có thể thực hiện các bước kiểm thử sau:

1. Kiểm tra cách **origin server** ánh xạ URL path

- Thêm một đoạn path tùy ý vào URL của endpoint mục tiêu.
- Nếu phản hồi **vẫn chứa dữ liệu nhạy cảm giống như phản hồi gốc**, điều này cho thấy **origin server trừu tượng hóa đường dẫn và bỏ qua đoạn path thêm vào**.

**Ví dụ:**

- Gốc: `/api/orders/123` trả về thông tin order `123`.
    
- Thử: `/api/orders/123/foo` vẫn trả về thông tin order `123`.
    
    → Máy chủ gốc bỏ qua `/foo`.
    

1. Kiểm tra cách **cache** ánh xạ URL path

- Sửa URL sao cho khớp với một quy tắc cache bằng cách thêm **phần mở rộng tĩnh**.
- Ví dụ: `/api/orders/123/foo.js`

Nếu phản hồi **bị cache lại**, điều này cho thấy:

- Cache **diễn giải toàn bộ đường dẫn URL** có phần mở rộng tĩnh.
- Có quy tắc cache cho các request kết thúc bằng `.js`.

👉 Ngoài `.js`, bạn nên thử nhiều phần mở rộng khác: `.css`, `.ico`, `.exe`, ...

1. Craft URL tấn công

- Khi xác định được sự khác biệt, bạn có thể tạo URL trả về phản hồi động nhưng **được cache lưu trữ như tài nguyên tĩnh**.
- Lưu ý: Kiểu tấn công này **chỉ giới hạn ở endpoint cụ thể** mà bạn đã test, vì mỗi endpoint có thể có quy tắc ánh xạ khác nhau.

> **🔎 Lưu ý**
> 
> - **Burp Scanner** có thể tự động phát hiện lỗ hổng web cache deception gây ra bởi path mapping discrepancies trong quá trình audit.
> - Bạn cũng có thể dùng **Web Cache Deception Scanner BApp** để phát hiện các cấu hình cache sai.


---

#### **Delimiter discrepancies**

---

**Delimiters (ký tự phân tách)** được dùng để xác định ranh giới giữa các thành phần trong URL. Việc sử dụng một số ký tự và chuỗi làm delimiter thường đã được chuẩn hóa. Ví dụ: `?` thường dùng để tách **đường dẫn URL** và **query string**.

Tuy nhiên, do chuẩn URI (RFC) khá lỏng lẻo, nên vẫn tồn tại sự khác biệt trong cách các framework hoặc công nghệ xử lý delimiter.

Sự **khác biệt trong cách cache và origin server xử lý delimiter** có thể dẫn tới lỗ hổng **web cache deception**.

**Ví dụ 1:** Java Spring và dấu `;`

Request:

```
/profile;foo.css
```

- **Java Spring**: coi `;` là ký tự delimiter để thêm **matrix variables**. → Origin server cắt đường dẫn sau `/profile` và trả về thông tin profile.
- **Cache thông thường**: không coi `;` là delimiter → hiểu toàn bộ `/profile;foo.css` là đường dẫn.
    - Nếu cache có quy tắc lưu phản hồi với các request kết thúc bằng `.css`, nó sẽ cache thông tin profile như thể đó là file CSS.

Ví dụ 2: Ruby on Rails và dấu `.`

- `/profile` → được xử lý bởi formatter mặc định (HTML), trả về thông tin profile.
- `/profile.css` → `.css` được coi là định dạng phản hồi. Vì không có formatter CSS, request bị từ chối, trả về lỗi.
- `/profile.ico` → `.ico` không được Rails nhận diện. Request được chuyển cho formatter mặc định (HTML) → trả về thông tin profile.
    - Nếu cache được cấu hình để lưu các phản hồi kết thúc bằng `.ico`, nó sẽ cache profile info như thể đó là một file tĩnh `.ico`.

Ví dụ 3: Ký tự mã hóa `%00`

Request:

```
/profile%00foo.js
```

- **OpenLiteSpeed server**: coi `%00` (null byte) là delimiter. → Origin server hiểu đường dẫn là `/profile`.
- **Framework khác**: đa số trả về lỗi khi gặp `%00` trong URL.
- **Cache (Akamai, Fastly)**: coi `%00` và tất cả phần sau nó là một phần của đường dẫn. → Nếu cache có quy tắc cho `.js`, thông tin profile có thể bị lưu lại như file JS.

👉 Như vậy, các ký tự delimiter như `;`, `.`, `%00` và những ký tự được sử dụng không đồng nhất giữa các công nghệ có thể trở thành điểm khai thác trong **web cache deception**.

---

#### Exploit

---

Bạn có thể lợi dụng **delimiter discrepancies** để thêm một **phần mở rộng tĩnh** vào URL — phần này được cache coi là hợp lệ, nhưng lại bị origin server bỏ qua. Để làm được điều này, cần tìm ra một ký tự mà **origin server dùng như delimiter**, nhưng **cache thì không**.

1. **Xác định ký tự delimiter của origin server**

- Bước đầu: thêm một chuỗi tùy ý vào cuối URL của endpoint mục tiêu.
    - Ví dụ: `/settings/users/list` → `/settings/users/listaaa`.
    - Dùng phản hồi này làm tham chiếu.

**Lưu ý:**

Nếu phản hồi giống hệt với phản hồi gốc → request có thể bị **redirect**. Trong trường hợp đó, hãy chọn một endpoint khác để test.

- Tiếp theo: chèn một ký tự delimiter khả nghi giữa đường dẫn gốc và chuỗi tùy ý.
    
    - Ví dụ: `/settings/users/list;aaa`
    
    Diễn giải:
    
    - Nếu phản hồi **giống phản hồi gốc** → `;` được dùng như delimiter, origin server hiểu đường dẫn là `/settings/users/list`.
    - Nếu phản hồi **giống phản hồi có chuỗi thêm** → `;` không được dùng như delimiter, origin server hiểu đường dẫn là `/settings/users/list;aaa`.

1. **Kiểm tra cache xử lý delimiter như thế nào**

- Sau khi xác định ký tự delimiter của origin server, thêm **phần mở rộng tĩnh** vào cuối đường dẫn.
    - Ví dụ: `/settings/users/list;aaa.js`

Nếu phản hồi được cache → chứng tỏ:

- Cache **không dùng ký tự delimiter** đó, coi toàn bộ `/settings/users/list;aaa.js` là đường dẫn hợp lệ.
- Cache có quy tắc lưu phản hồi với request kết thúc bằng `.js`.

1. **Lưu ý khi khai thác**

- Cần test toàn bộ ký tự ASCII và nhiều phần mở rộng phổ biến: `.css`, `.ico`, `.exe`, ...
- Trong **labs của PortSwigger** có cung cấp danh sách ký tự delimiter để tham khảo. Có thể dùng **Burp Intruder** để test hàng loạt ký tự nhanh chóng.
    - Để tránh Burp Intruder tự động mã hóa delimiter, hãy tắt tính năng **Payload encoding** trong panel **Payloads**.

1. **Xây dựng exploit**

Ví dụ với payload:

```
/settings/users/list;aaa.js
```

- **Cache** hiểu đường dẫn là: `/settings/users/list;aaa.js`
- **Origin server** hiểu đường dẫn là: `/settings/users/list`
- Origin server trả về **thông tin động (profile info)** → bị cache lưu lại như thể đó là file `.js`.

👉 Vì delimiter thường được xử lý **nhất quán trong cùng một server**, kiểu tấn công này có thể áp dụng cho nhiều endpoint khác nhau.

1. **Hạn chế**

Một số ký tự delimiter có thể bị **trình duyệt nạn nhân xử lý trước** khi gửi request đến cache.

- Ví dụ: `{`, `}`, `<`, `>`, hoặc `#` → bị **URL-encode** hoặc **cắt ngắn đường dẫn**.
- Nếu cache hoặc origin server có giải mã các ký tự này, bạn có thể thử dùng **phiên bản đã encode** để khai thác.

---

#### Delimiter decoding discrepancies

---

Đôi khi, các website cần gửi dữ liệu trong URL có chứa những ký tự đặc biệt (ví dụ: delimiter). Để đảm bảo những ký tự này được xử lý như dữ liệu chứ không phải ký tự điều khiển, chúng thường được **mã hóa (URL-encoded)**.

Tuy nhiên, một số **bộ phân tích (parser)** sẽ **giải mã (decode)** một số ký tự trước khi xử lý URL. Nếu ký tự đó là delimiter, nó có thể bị coi như delimiter thật sự và làm **cắt ngắn đường dẫn URL**.

Sự khác biệt trong việc **cache** và **origin server** giải mã ký tự delimiter nào có thể dẫn đến việc chúng **diễn giải URL path khác nhau**, ngay cả khi cả hai đều dùng cùng một tập ký tự delimiter.

Ví dụ 1: `/profile%23wcd.css` (ký tự `#` được mã hóa thành `%23`)

- **Origin server**: giải mã `%23` → `#`. Vì `#` được dùng làm delimiter, nên server hiểu đường dẫn là `/profile` và trả về thông tin profile.
- **Cache**: cũng coi `#` là delimiter, nhưng **không giải mã `%23`**. Nó hiểu đường dẫn là `/profile%23wcd.css`.
    - Nếu cache có quy tắc lưu phản hồi cho request kết thúc bằng `.css`, nó sẽ lưu phản hồi này.

Ví dụ 2: `/myaccount%3fwcd.css` (ký tự `?` được mã hóa thành `%3f`)

- **Cache server**: áp dụng quy tắc cache dựa trên URL **chưa decode** → `/myaccount%3fwcd.css`. Vì đường dẫn kết thúc bằng `.css`, cache quyết định lưu phản hồi. Sau đó, nó **decode `%3f` → `?`** và chuyển request mới đến origin server.
- **Origin server**: nhận request `/myaccount?wcd.css`. Nó coi `?` là delimiter và hiểu đường dẫn là `/myaccount`.

Sự khác biệt về **thời điểm decode** (trước hay sau khi áp dụng quy tắc cache) và **ký tự nào được decode** giữa cache và origin server có thể bị khai thác để:

- Lưu dữ liệu động (ví dụ: thông tin người dùng) trong cache.
- Phục vụ dữ liệu nhạy cảm cho attacker như thể đó là tài nguyên tĩnh.

---

#### Exploit

---

Bạn có thể khai thác **sự khác biệt khi giải mã** bằng cách dùng **delimiter đã mã hóa** để thêm một **phần mở rộng tĩnh** vào đường dẫn — phần này được **cache** nhìn thấy nhưng **origin server** thì không.

Hãy sử dụng cùng phương pháp kiểm thử mà bạn dùng để xác định và khai thác **delimiter discrepancies**, nhưng thử với **nhiều ký tự đã mã hóa**. Đảm bảo bạn cũng kiểm thử các **ký tự không in được** đã mã hóa, đặc biệt là `%00`, `%0A` và `%09`. Nếu các ký tự này được giải mã, chúng cũng có thể **cắt ngắn URL path**.

---

### **Static directory cache rules**

---

Thông thường máy chủ web sẽ lưu tài nguyên tĩnh trong các thư mục chuyên biệt. Các quy tắc cache thường nhắm tới các thư mục này bằng cách khớp các tiền tố đường dẫn URL cụ thể, như `/static`, `/assets`, `/scripts` hoặc `/images`. Những quy tắc này cũng có thể dễ bị tấn công **web cache deception**.

---

#### **Normalization discrepancies**

---

**Normalization** là quá trình chuyển đổi các cách biểu diễn khác nhau của đường dẫn URL về một định dạng chuẩn. Quá trình này đôi khi bao gồm:

- Giải mã (decode) các ký tự đã mã hóa.
- Xử lý các đoạn `.` và `..` (dot-segments).

Tuy nhiên, mức độ chuẩn hóa thay đổi đáng kể giữa các parser khác nhau.

Sự khác biệt trong cách **cache** và **origin server** chuẩn hóa URL có thể cho phép kẻ tấn công tạo ra payload **path traversal** mà mỗi parser hiểu theo cách khác nhau.

**Ví dụ:**

```
/static/..%2fprofile
```

- **Origin server**: nếu nó **giải mã ký tự slash** (`%2f` → `/`) và **xử lý dot-segments**, đường dẫn được chuẩn hóa thành `/profile` → trả về thông tin profile.
- **Cache**: nếu nó **không xử lý dot-segments** hoặc **không giải mã slash**, nó sẽ hiểu đường dẫn là `/static/..%2fprofile`.
    - Nếu cache được cấu hình để lưu phản hồi cho request có tiền tố `/static`, nó sẽ cache và phục vụ thông tin profile.

> Lưu ý
> 
> Trong ví dụ trên, **mỗi dot-segment trong chuỗi path traversal cần được mã hóa**. Nếu không, **trình duyệt nạn nhân sẽ tự xử lý** (normalize) chúng trước khi gửi request đến cache.
> 
> 👉 Vì vậy, một **normalization discrepancy** có thể khai thác được chỉ khi **cache hoặc origin server**:
> 
> - Giải mã ký tự trong chuỗi path traversal, **và**
> - Xử lý dot-segments.

---

#### **Detect - Origin server**

---

Để kiểm tra cách **origin server** chuẩn hóa đường dẫn URL, hãy gửi một request đến **tài nguyên không được cache** kèm theo chuỗi **path traversal** và một thư mục tùy ý ở đầu đường dẫn.

👉 Cách chọn tài nguyên không cache: dùng các phương thức **non-idempotent** như `POST`.

**Ví dụ:**

- Gốc: `/profile`
- Test: `/aaa/..%2fprofile`

Kết quả có thể xảy ra:

- Nếu phản hồi **giống phản hồi gốc** (trả về thông tin profile) → Đường dẫn đã được hiểu là `/profile`.
    - Origin server **giải mã slash** (`%2f` → `/`) và **xử lý dot-segment** (`..`).
- Nếu phản hồi **khác phản hồi gốc** (ví dụ: trả về lỗi 404) → Đường dẫn được hiểu là `/aaa/..%2fprofile`.
    - Origin server **không giải mã slash** hoặc **không xử lý dot-segment**.

> 🔎 Lưu ý khi test normalization
> 
> - Khi test, hãy bắt đầu bằng việc **chỉ encode dấu slash thứ hai trong dot-segment** (`..%2f`).
>     - Điều này quan trọng vì một số CDN sẽ match trực tiếp **dấu slash ngay sau tiền tố thư mục tĩnh** (ví dụ: `/static`).
> - Ngoài ra, bạn có thể thử:
>     - **Encode toàn bộ chuỗi path traversal**, hoặc
>     - Encode dấu `.` thay vì dấu `/`.

👉 Những thay đổi này đôi khi sẽ ảnh hưởng đến việc parser có decode và xử lý chuỗi path traversal hay không.

---

#### **Detect - Cache server**

---

Có nhiều cách để kiểm tra cách **cache server** chuẩn hóa đường dẫn.

1. Xác định thư mục tĩnh tiềm năng

- Trong **Proxy > HTTP history**, tìm các request có tiền tố thư mục tĩnh phổ biến và phản hồi được cache.
- Lọc lịch sử để chỉ hiện các request có **mã 2xx** và MIME type như **script**, **images**, hoặc **CSS**.

1. Kiểm thử với chuỗi path traversal ở đầu đường dẫn

Chọn một request có phản hồi chắc chắn được cache, sau đó gửi lại request với chuỗi **path traversal** và một thư mục tùy ý ở đầu đường dẫn tĩnh.

**Ví dụ:**

```
/aaa/..%2fassets/js/stockCheck.js
```

- Nếu phản hồi **không còn được cache** → cache **không chuẩn hóa đường dẫn** trước khi ánh xạ tới endpoint. Điều này cho thấy có **quy tắc cache dựa trên tiền tố `/assets`**.
- Nếu phản hồi **vẫn được cache** → cache có thể đã chuẩn hóa thành `/assets/js/stockCheck.js`.

1. Kiểm thử với path traversal ngay sau tiền tố thư mục

Sửa đường dẫn từ:

```
/assets/js/stockCheck.js
```

thành:

```
/assets/..%2fjs/stockCheck.js
```

- Nếu phản hồi **không còn được cache** → cache **decode slash** và **xử lý dot-segment** khi chuẩn hóa, coi đường dẫn là `/js/stockCheck.js`. Điều này cho thấy có **quy tắc cache dựa trên tiền tố `/assets`**.
- Nếu phản hồi **vẫn được cache** → cache **không decode slash** hoặc **không xử lý dot-segment**, coi đường dẫn là `/assets/..%2fjs/stockCheck.js`.

1. Xác nhận quy tắc cache thực sự dựa trên thư mục

Trong cả hai trường hợp, phản hồi vẫn có thể bị cache do **quy tắc khác** (ví dụ: dựa trên phần mở rộng file).

- Để xác nhận, hãy thay phần sau tiền tố thư mục bằng chuỗi tùy ý, ví dụ:
    
    ```
    /assets/aaa
    ```
    
- Nếu phản hồi **vẫn được cache** → xác nhận rằng cache rule dựa trên tiền tố `/assets`.
    
- Nếu phản hồi **không được cache** → chưa thể loại trừ hoàn toàn quy tắc cache theo thư mục, vì **404 responses đôi khi không bị cache**.
    

> **🔎 Lưu ý**
> 
> Trong nhiều trường hợp, bạn **không thể xác định chắc chắn** liệu cache có decode dot-segment hoặc chuẩn hóa đường dẫn URL hay không, trừ khi thực sự thử nghiệm một exploit.

---

#### Exploit **- Origin server**

---

Nếu **origin server** xử lý và giải quyết các **dot-segment đã mã hóa** (ví dụ `..%2f`), nhưng **cache** thì không, bạn có thể khai thác sự khác biệt này bằng cách tạo payload theo cấu trúc sau:

```xml
/<static_directory_prefix>/..%2f<ddynamic_path>
```

Payload:

```
/assets/..%2fprofile
```

- **Cache** hiểu đường dẫn là:
    
    ```
    /assets/..%2fprofile
    ```
    
- **Origin server** hiểu đường dẫn là:
    
    ```
    /profile
    ```
    
- Origin server trả về **thông tin động (profile info)** → thông tin này được **cache lưu lại** như thể đó là tài nguyên tĩnh.
    

👉 Đây chính là cách khai thác lỗ hổng **normalization discrepancies** để biến dữ liệu động nhạy cảm thành dữ liệu tĩnh bị lưu trong cache.


---

#### Exploit **- Cache server**

---

Nếu **cache server** xử lý và giải quyết các **dot-segment đã mã hóa**, nhưng **origin server** thì không, bạn có thể khai thác sự khác biệt này bằng cách tạo payload theo cấu trúc:

```
/<dynamic_path>%2f%2e%2e%2f<static-directory-prefix>
```

> **🔎 Lưu ý**
> 
> - Khi khai thác theo hướng này, hãy **mã hóa toàn bộ các ký tự trong chuỗi path traversal**.
>     - Việc mã hóa giúp tránh các hành vi bất ngờ khi gặp delimiter.
>     - Không cần để dấu `/` chưa mã hóa sau tiền tố thư mục tĩnh, vì **cache sẽ tự giải mã**.

1. Path traversal **chưa đủ** để khai thác

Ví dụ payload:

```
/profile%2f%2e%2e%2fstatic
```

- **Cache** hiểu đường dẫn là: `/static`
- **Origin server** hiểu đường dẫn là: `/profile%2f%2e%2e%2fstatic`
- Kết quả: Origin server có thể trả về **lỗi** thay vì thông tin profile.

1. Kết hợp với delimiter

Để khai thác thành công, bạn cần tìm một **delimiter mà origin server sử dụng nhưng cache thì không**.

- Cách test: thêm delimiter khả nghi sau dynamic path.

Kịch bản:

- Nếu **origin server** dùng delimiter đó → nó sẽ cắt ngắn URL path và trả về dữ liệu động.
- Nếu **cache** không coi delimiter đó là đặc biệt → nó sẽ chuẩn hóa thành đường dẫn tĩnh và **cache phản hồi**.

1. Ví dụ thành công

Payload:

```xml
/<dynamic>%23%2f%2e%2e%2f<static_folder>
```

- **Cache** hiểu đường dẫn là: `/static`
- **Origin server** hiểu đường dẫn là: `/profile` (do `;` là delimiter)
- Origin server trả về **thông tin profile động**, sau đó bị **cache lưu lại** như thể đó là tài nguyên tĩnh.

👉 Đây là cách lợi dụng sự khác biệt chuẩn hóa của **cache server** để thực hiện **web cache deception exploit**.



---

### **File name cache rules**

---

Một số tệp như `robots.txt`, `index.html` và `favicon.ico` là các tệp phổ biến trên máy chủ web. Chúng thường được cache do ít thay đổi. Các quy tắc cache nhắm đến những tệp này bằng cách khớp chính xác chuỗi tên tệp.

Để xác định liệu có quy tắc cache theo tên tệp hay không, hãy gửi một yêu cầu GET cho một tệp có khả năng và kiểm tra xem phản hồi có được cache hay không.

---

#### **Detect**

---

Để kiểm tra cách máy chủ gốc chuẩn hóa đường dẫn URL, hãy dùng cùng phương pháp mà bạn đã sử dụng cho các quy tắc cache theo thư mục tĩnh.

Để kiểm tra cách cache chuẩn hóa đường dẫn URL, hãy gửi một yêu cầu với chuỗi path traversal và một thư mục tùy ý đặt trước tên tệp. Ví dụ, `/profile%2f%2e%2e%2findex.html`:

- Nếu phản hồi được cache, điều này cho thấy cache chuẩn hóa đường dẫn thành `/index.html`.
- Nếu phản hồi không được cache, điều này cho thấy cache không giải mã dấu gạch chéo và không xử lý dot-segment, diễn giải đường dẫn là `/profile%2f%2e%2e%2findex.html`.

---

#### Exploit

---

Vì phản hồi chỉ được cache nếu yêu cầu khớp chính xác tên tệp, bạn chỉ có thể khai thác khác biệt trong trường hợp máy chủ cache xử lý (resolve) dot-segment đã mã hóa, còn máy chủ gốc thì không. Hãy dùng cùng phương pháp như với các quy tắc cache theo thư mục tĩnh - chỉ cần thay tiền tố thư mục tĩnh bằng tên tệp.

Exploit:

```xml
/<dynamic>;%2f%2e%2e%2f<static_file>
```


---

## Ngăn chặn

---

Bạn có thể thực hiện một số biện pháp sau để ngăn chặn lỗ hổng web cache deception:

- Luôn sử dụng **Cache-Control header** để đánh dấu tài nguyên động, với các chỉ thị `no-store` và `private`.
- Cấu hình thiết lập **CDN** sao cho các quy tắc cache không ghi đè lên Cache-Control header.
- Kích hoạt bất kỳ cơ chế bảo vệ nào mà CDN của bạn hỗ trợ chống lại tấn công web cache deception. Nhiều CDN cho phép bạn đặt quy tắc cache kiểm tra xem **Content-Type của phản hồi** có khớp với **phần mở rộng file trong URL request** hay không. Ví dụ: **Cache Deception Armor** của Cloudflare.
- Xác minh rằng không tồn tại khác biệt giữa cách máy chủ gốc và cache diễn giải đường dẫn URL.

# WU
- [x] Exploiting path mapping for web cache deception
- [x] Exploiting path delimiters for web cache deception
- [x] Exploiting origin server normalization for web cache deception
- [x] Exploiting cache server normalization for web cache deception
- [x] Exploiting exact-match cache rules for web cache deception

## Exploiting path mapping for web cache deception
- ở bài lab này: tập trung vào kỹ thuật lợi dụng việc ánh xạ đường dẫn (Path Mapping) để lừa Cache Server lưu trữ thông tin nhạy cảm của người dùng vào một file tĩnh "giả".
thêm đuôi 123.js vào sau request GET tới trang cá nhân:
![](../../image/Pasted%20image%2020260503005813.png)

- trang web vẫn hiển thị nội dung trang cá nhân của bạn thay vì báo lỗi 404, chứng tỏ Origin Server có hỗ trợ Path Mapping.
- khi gửi request vài lần thấy: X-cache cứ miss rồi lại hit chứng tỏ file này đã được lưu vào Cache
![](../../image/Pasted%20image%2020260503005956.png)

![](../../image/Pasted%20image%2020260503010024.png)
- xây dựng payload: tạo một đường dẫn mà khi nạn nhânclick vào, thông tin của họ sẽ bị lưu lại.
![](../../image/Pasted%20image%2020260503010440.png)
- asans deliver to victim sau đó truy cập đương dẫn đó
![](../../image/Pasted%20image%2020260503010531.png)

## Exploiting path delimiters for web cache deception

- ở bài lab này: thay vì chỉ thêm một file ảo vào sau đường dẫn, chúng ta sẽ sử dụng các **ký tự phân tách đường dẫn (path delimiters)** để đánh lừa các thành phần trong hệ thống.
- gửi gói tin GET /my-account sang intruder để xem kí tự nào trả về 200 thay vì 404

![](../../image/Pasted%20image%2020260503011919.png)

- ta đã tìm được kí tự ; và ? đều trả về 200, còn lại các bước tương tự bài lab trên, chỉ cần gửi payload đến victim và truy cập url
![](../../image/Pasted%20image%2020260503012149.png)



## Exploiting origin server normalization for web cache deception

- ở bài lab này, ta lợi dụng cách **chuẩn hóa đường dẫn (Normalization)** khác nhau giữa Cache và Origin Server
- **Cache Server :** Nó thấy URL bắt đầu bằng `/resources/`. Nó có một quy tắc (Cache Rule) là: _"Bất cứ thứ gì nằm trong thư mục /resources đều là file tĩnh, hãy lưu nó vào bộ nhớ đệm!"_. Nó không quan tâm đến dấu `..%2f`.
- **Origin Server:** Khi nhận được `/resources/..%2fmy-account`, nó sẽ thực hiện **giải mã URL (Decode)** `%2f` thành `/` và **chuẩn hóa (Normalize)** `..` để quay ngược thư mục. Kết quả là nó hiểu bạn đang muốn truy cập vào `/my-account`.

- bruteforce thấy dấu ? trả về 200
![](../../image/Pasted%20image%2020260503013443.png)

- chuyển sang repeater thử gửi payload: `/aaa/..%2fmy-account`
- vì Origin Server hiểu `/aaa/..%2f` nghĩa là _"vào aaa rồi thoát ra ngay"_, cuối cùng vẫn là `/my-account`
![](../../image/Pasted%20image%2020260503013534.png)

- gửi thử 1 request ở /resources: thấy X-cache cứ hit rồi miss => Cache Server mặc định lưu mọi thứ trong `/resources`.
![](../../image/Pasted%20image%2020260503013802.png)
- ta sẽ cần một URL mà:
1. **Cache Server nhìn vào:** Thấy bắt đầu bằng `/resources/` nên sẽ Cache nó.
2. **Origin Server nhìn vào:** Sau khi chuẩn hóa sẽ trả về trang `/my-account`
`<script>document.location="https://0a8800b003c6441a804f265c004b0039.web-security-academy.net/resources/..%2fmy-account?wcd"</script>`

Thêm `?wcd` để làm **cache buster**, đảm bảo không nhận lại bản cache cũ 
- gửi tới victime và vào url để solved

![](../../image/Pasted%20image%2020260503014011.png)
## Exploiting cache server normalization for web cache deception

- ngược lại với lab trên là Origin Server tự chuẩn hóa URL, còn ở bài này, **Cache Server** mới là bên thực hiện chuẩn hóa (Normalization).
- - **Origin Server:** Khi nhận được dấu `%23` (mã hóa của `#`), nó coi đó là một **Path Delimiter**. Nó sẽ cắt bỏ toàn bộ phần sau dấu `%23` và chỉ xử lý phần `/my-account`. Nó **KHÔNG** tự chuẩn hóa các dấu `..%2f`.
- **Cache Server:** Nó thực hiện **Giải mã (Decode)** và **Chuẩn hóa (Normalize)** URL trước khi áp dụng các quy tắc Cache. Khi thấy `/my-account%23%2f%2e%2e%2fresources`, nó chuẩn hóa thành `/resources` và tin rằng đây là một file tĩnh hợp lệ để lưu trữ.

- bruteforce để xem origin server chấp nhận kí tự nào
![](../../image/Pasted%20image%2020260503014602.png)

- - Các ký tự `#`, `?`, `%23`, và `%3f` trả về **200 OK**. ta sẽ bỏ qua `#` vì trình duyệt sẽ cắt nó trước khi gửi đi. Chúng ta sẽ tập trung vào bản mã hóa của nó là **`%23`**.

- payload: `/aaa/..%2fresources/some-file`: X-cache miss rồi hit , nghĩa là cache server đã chuẩn hóa đường dẫn thành /resources/ và lưu nó vào bộ đệm
![](../../image/Pasted%20image%2020260503014814.png)

=> payload: một URL "hai mặt": `/my-account%23%2f%2e%2e%2fresources`
1. **Origin Server thấy:** `/my-account` (vì bị chặn bởi `%23`) -> Trả về trang cá nhân.
2. **Cache Server thấy:** `/my-account# /../resources` -> Sau khi chuẩn hóa thành `/resources`, nó quyết định Cache trang này lại.
<script>document.location="https://[YOUR-LAB-ID].web-security-academy.net/my-account%23%2f%2e%2e%2fresources?wcd"</script>



![](../../image/Pasted%20image%2020260503015146.png)

## Exploiting exact-match cache rules for web cache deception
 - ở bài lab này, Cache Server không dùng các quy tắc chung chung như "thư mục `/resources`" hay "đuôi file `.js`". Thay vào đó, nó có một **quy tắc khớp chính xác (Exact-match)**: Nó chỉ cache những file cụ thể mà nó tin là tĩnh, ví dụ như `/robots.txt`
- Sự lệch pha ở bài này nằm ở việc kết hợp giữa **Path Delimiter** và **Exact-match Normalization**:
- **Cache Server:** Nó được cấu hình cực kỳ chặt chẽ: _"Chỉ cache file /robots.txt"_. Tuy nhiên, nó lại có một điểm yếu là nó thực hiện **Normalization** (chuẩn hóa đường dẫn). Khi thấy `/my-account;..%2frobots.txt`, nó giải mã và hiểu rằng đây chính là file `/robots.txt` nên nó lưu vào bộ đệm.
- **Origin Server:** Khi thấy dấu `;`, nó coi đó là điểm dừng (delimiter) và chỉ xử lý phần `/my-account`. Nó không quan tâm đến phần "đuôi" `/robots.txt` phía sau.


- thử đường dẫn : /robots.txt thấy X-cache miss rồi hit => 
![](../../image/Pasted%20image%2020260503015800.png)

- bruteforce: thấy `;` và `?` là hai delimiter được chấp nhận.
![](../../image/Pasted%20image%2020260503020140.png)

- Xác nhận khả năng chuẩn hóa của Cache: Thử `/aaa/..%2frobots.txt`. thấy `X-Cache: hit`, nghĩa là Cache Server sẽ chuẩn hóa mọi đường dẫn về `/robots.txt` nếu phần cuối khớp.
![](../../image/Pasted%20image%2020260503020304.png)
 =>
 cần một URL làm sao để lừa được cả hai bên:
- **Payload:** `/my-account;%2f%2e%2e%2frobots.txt`
- **Origin Server thấy:** `/my-account` (do dấu `;`) -> Trả về trang cá nhân của người đang đăng nhập.
- **Cache Server thấy:** `/my-account; /../robots.txt` -> Chuẩn hóa thành `/robots.txt` -> **Lưu nội dung vào cache**.

Mục tiêu bài này không phải là API Key, mà là **CSRF Token** để thực hiện hành động thay đổi Email của Admin.
1. **Gửi Exploit:** Lừa Admin truy cập URL trên qua Exploit Server.
2. **Lấy Token:** Dùng Repeater gửi request đến đúng URL đó. Trong nội dung trả về từ Cache, ta sẽ thấy mã CSRF Token của Admin. 

![](../../image/Pasted%20image%2020260503021250.png)

- deliver đến victim, sau đó vào burp gửi 1 gói tin bất kì để lấy crsf của admin
- sau đó quay lại request đổi email và thay crsf của admin vào đây, chuột phải chọn engagement tools và generate csrf PoCs
- quay lại exploit web để copy đoạn html này deliver to victim
