<!-- TOC -->
## Mục lục

- [GraphQL API vulnerabilities](#graphql-api-vulnerabilities)
  - [What is GraphQL?](#what-is-graphql)
  - [How GraphQL works](#how-graphql-works)
  - [What is a GraphQL schema?](#what-is-a-graphql-schema)
  - [What are GraphQL queries?](#what-are-graphql-queries)
  - [What are GraphQL mutations?](#what-are-graphql-mutations)
  - [Components of queries and mutations](#components-of-queries-and-mutations)
    - [Fields](#fields)
    - [Arguments](#arguments)
    - [Variables](#variables)
    - [Aliases](#aliases)
  - [Subscriptions](#subscriptions)
  - [Introspection](#introspection)
  - [Finding GraphQL endpoints](#finding-graphql-endpoints)
    - [Universal queries](#universal-queries)
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
- [WU](#wu)
  - [Accessing private GraphQL posts](#accessing-private-graphql-posts)
  - [Accidents exposure private graphQL fields](#accidents-exposure-private-graphql-fields)
  - [Finding a hidden GraphQL endpoint](#finding-a-hidden-graphql-endpoint)
  - [Bypassing GraphQL brute force protections](#bypassing-graphql-brute-force-protections)
  - [Performing CSRF exploits over GraphQL](#performing-csrf-exploits-over-graphql)
<!-- /TOC -->

# GraphQL API vulnerabilities

GraphQL API có thể phát sinh nhiều lỗ hổng do lỗi thiết kế và triển khai. Một ví dụ quen thuộc là tính năng **introspection** bị để mở, cho phép attacker gửi truy vấn để thu thập thông tin chi tiết về schema. Các cuộc tấn công vào GraphQL thường xuất hiện dưới dạng những request được chế tác đặc biệt nhằm lấy dữ liệu, thực hiện hành động trái phép, vượt qua cơ chế bảo vệ, hoặc làm lộ thông tin nhạy cảm. Mức độ ảnh hưởng có thể rất nghiêm trọng nếu attacker leo thang được quyền, truy cập được object không thuộc quyền của mình, hoặc khai thác thành công CSRF thông qua mutation.

GraphQL không phải là một cơ chế bảo mật, cũng không tự động an toàn hơn REST. Nó chỉ là một cách tổ chức và truy vấn API khác với REST. Nếu hệ thống phía server kiểm soát quyền kém, xử lý input không chặt, hoặc để lộ quá nhiều thông tin về schema, attacker vẫn có thể khai thác rất hiệu quả. Điểm khác biệt nằm ở chỗ GraphQL tập trung rất nhiều khả năng vào một endpoint duy nhất, nên khi endpoint đó bị kiểm thử đúng cách, attacker thường có thể khám phá và khai thác nhanh hơn so với các API truyền thống.

## What is GraphQL?

GraphQL là một ngôn ngữ truy vấn dành cho API. Thay vì server trả về một cấu trúc dữ liệu cố định cho mỗi endpoint như trong nhiều REST API, GraphQL cho phép client mô tả chính xác mình muốn lấy những field nào. Điều này giúp frontend tối ưu hơn vì chỉ lấy đúng dữ liệu cần thiết, nhưng cũng đồng thời tăng bề mặt tấn công, do client có quyền chủ động chọn field, object và mối quan hệ cần truy vấn.

Một GraphQL API thường được định nghĩa bằng một **schema**. Schema mô tả các kiểu dữ liệu, field, operation và kiểu trả về mà API hỗ trợ. Client dùng schema này để gửi các **query** nhằm đọc dữ liệu và **mutation** nhằm thay đổi dữ liệu. Ngoài ra còn có nhiều thành phần quan trọng khác như **arguments**, **variables**, **aliases**, **subscriptions** và **introspection**.

Trong thực tế pentest, hiểu những khái niệm này rất quan trọng, vì phần lớn kỹ thuật khai thác GraphQL đều xoay quanh việc:
- tìm endpoint GraphQL;
- tìm hoặc suy ra schema;
- xác định field, query và mutation có giá trị;
- thay đổi arguments hoặc variables để truy cập dữ liệu trái phép;
- lợi dụng aliases để thực hiện nhiều thao tác trong cùng một request;
- kiểm tra mutation có bị CSRF hay không.

## How GraphQL works

GraphQL hoạt động theo mô hình một request mô tả dữ liệu cần lấy hoặc hành động cần thực hiện. Server nhận request đó, đối chiếu với schema, thực hiện các resolver tương ứng rồi trả về dữ liệu theo đúng cấu trúc mà client yêu cầu.

Điều này khiến GraphQL rất mạnh vì chỉ với một request, client có thể lấy đồng thời nhiều object có liên quan với nhau. Tuy nhiên, cũng chính vì thế mà nếu quyền hạn được kiểm tra không chặt ở từng resolver hoặc từng field, attacker có thể dùng một request để trích xuất dữ liệu rất sâu mà frontend thông thường không bao giờ hiển thị.

Một GraphQL request thường bao gồm:
- phần operation, ví dụ query hoặc mutation;
- phần field muốn lấy hoặc hành động muốn gọi;
- các arguments hoặc variables nếu cần truyền giá trị động.

Response thường có dạng JSON với phần `data`, và nếu có lỗi thì thêm phần `errors`. Trong pentest, trường `errors` rất đáng chú ý vì đôi khi nó tiết lộ tên field, tên type hoặc gợi ý về schema.

## What is a GraphQL schema?

Schema là phần mô tả cấu trúc của GraphQL API. Nó định nghĩa:
- những type nào tồn tại;
- mỗi type có những field nào;
- field nào nhận argument;
- query nào cho phép đọc dữ liệu;
- mutation nào cho phép thay đổi dữ liệu.

Schema giống như một “bản đồ” của toàn bộ API. Nếu attacker lấy được schema, việc khai thác dễ hơn rất nhiều vì không phải đoán mò endpoint hay tham số như với nhiều REST API. Thay vào đó, attacker có thể biết chính xác:
- tên mutation nhạy cảm;
- field riêng tư nhưng vẫn tồn tại;
- object nào có quan hệ với object nào;
- argument nào có vẻ dùng để tham chiếu trực tiếp tới object.

Do đó, việc lộ schema thông qua introspection hoặc error message thường không phải là lỗ hổng cuối cùng, nhưng là một lợi thế cực lớn cho attacker.

## What are GraphQL queries?

Query là operation dùng để đọc dữ liệu. Client có thể yêu cầu đúng những field cần thiết thay vì nhận toàn bộ object. Điều này rất thuận tiện cho frontend, nhưng về góc độ bảo mật, nó tạo cơ hội để attacker yêu cầu thêm những field mà frontend bình thường không sử dụng.

Nếu backend không kiểm soát quyền ở mức field hoặc object, attacker có thể:
- thêm field nhạy cảm vào query;
- thay `id` để lấy object của user khác;
- truy cập bài viết riêng tư;
- lấy thông tin nội bộ chưa bao giờ xuất hiện trên giao diện.

## What are GraphQL mutations?

Mutation là operation dùng để thay đổi trạng thái hệ thống. Ví dụ:
- đăng nhập;
- đăng ký;
- đổi email;
- đổi mật khẩu;
- xóa object;
- tạo bài viết;
- cập nhật thông tin người dùng.

Mutation thường là nơi rủi ro nhất trong GraphQL API vì nó gắn trực tiếp với hành động nhạy cảm. Nếu mutation nhận input từ client mà backend không xác thực và kiểm tra quyền đúng cách, attacker có thể sửa hoặc xóa dữ liệu trái phép.

Mutation cũng là mục tiêu chính khi test CSRF. Nếu GraphQL endpoint chấp nhận request theo cách mà trình duyệt có thể gửi xuyên site, mutation hoàn toàn có thể bị khai thác qua CSRF như bất kỳ API nào khác.

## Components of queries and mutations

Queries và mutations được ghép từ nhiều thành phần nhỏ. Những thành phần này rất quen thuộc với lập trình viên GraphQL, nhưng với pentester thì cũng là các điểm cần chú ý đặc biệt.

### Fields

Field là đơn vị dữ liệu cơ bản mà client yêu cầu. Chính nhờ khả năng tự chọn field mà GraphQL trở nên linh hoạt. Nhưng cũng vì vậy, attacker có thể thử thêm các field không được frontend dùng tới để xem backend có trả về hay không.

### Arguments

Arguments là giá trị truyền vào field hoặc operation. Chúng rất thường được dùng để chọn object cần trả về, ví dụ `id`, `username`, `slug`, `postId` hoặc `userId`. Nếu backend dùng trực tiếp những arguments này để truy vấn dữ liệu mà không áp kiểm tra quyền, GraphQL API có thể dính IDOR hoặc các lỗi object-level authorization.

Đây là một trong những kiểu lỗi thực tế nhất khi pentest GraphQL: chỉ cần thay đổi một `id`, attacker có thể truy cập object của người khác nếu backend không kiểm tra đúng.

### Variables

Variables cho phép truyền giá trị động tách khỏi nội dung query chính. Điều này giúp query dễ tái sử dụng hơn, nhưng không làm thay đổi bản chất bảo mật. Nếu server tin vào variable do client gửi mà không kiểm tra quyền hoặc kiểu dữ liệu, lỗ hổng vẫn xuất hiện như khi dùng inline arguments.

### Aliases

Aliases cho phép gọi cùng một field hoặc mutation nhiều lần trong cùng một request nhưng dưới những tên khác nhau. Đây là một tính năng hợp lệ của GraphQL, nhưng có thể bị attacker lợi dụng để bypass các cơ chế rate limit hoặc brute-force protection nếu hệ thống chỉ đếm số lượng request HTTP.

Ví dụ, attacker có thể gửi hàng chục mutation đăng nhập trong cùng một request duy nhất bằng alias, thay vì gửi hàng chục request riêng biệt.

## Subscriptions

Subscriptions là cơ chế cho phép client nhận cập nhật theo thời gian thực khi dữ liệu thay đổi. Chủ đề này không phải trọng tâm chính trong topic GraphQL API vulnerabilities của PortSwigger, nhưng cần hiểu rằng nó cũng là một phần của hệ sinh thái GraphQL. Nếu một ứng dụng dùng subscriptions, pentester vẫn cần kiểm tra logic xác thực, quyền truy cập và cách dữ liệu được phát tới client.

Dù subscriptions không được nhấn mạnh nhiều trong các lab GraphQL cơ bản, sự tồn tại của chúng cho thấy GraphQL không chỉ là truy vấn đồng bộ đơn giản. Nó có thể mở thêm bề mặt tấn công tùy theo cách triển khai.

## Introspection

Introspection là cơ chế cho phép một GraphQL API mô tả chính nó. Client có thể hỏi API những câu như:
- có những type nào;
- query nào tồn tại;
- mutation nào tồn tại;
- field nào thuộc về type nào;
- mỗi field nhận argument gì;
- kiểu trả về là gì.

Đây là một tính năng rất hữu ích trong phát triển vì giúp tooling và IDE làm việc dễ dàng hơn. Nhưng nếu để mở trên production, attacker có thể dùng nó để dựng lại gần như toàn bộ schema.

Tự bản thân introspection không nhất thiết là lỗ hổng nghiêm trọng, nhưng nó làm quá trình reconnaissance nhanh hơn rất nhiều. Một attacker không còn phải đoán mò tên query hay mutation nữa. Thay vào đó, họ có thể hỏi thẳng API về những gì tồn tại.

## Finding GraphQL endpoints

Khi pentest GraphQL, bước đầu tiên là xác định endpoint. Không giống REST nơi nhiều chức năng được tách thành nhiều URL khác nhau, GraphQL thường gom hầu hết thao tác vào một số rất ít endpoint, đôi khi chỉ một endpoint duy nhất.

Những vị trí phổ biến cần thử gồm:
- `/graphql`
- `/api`
- `/api/graphql`
- `/graphql/v1`
- `/graphql/graphql`

Ngoài các đường dẫn phổ biến, cũng nên chú ý tới traffic frontend. Một số ứng dụng không lộ rõ endpoint trên giao diện, nhưng request của frontend trong HTTP history hoặc JavaScript bundle có thể chỉ ra nơi GraphQL đang được sử dụng.

### Universal queries

Một cách xác nhận rất nhanh là gửi universal query:

```graphql
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