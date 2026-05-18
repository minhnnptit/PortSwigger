```table-of-contents
```

# Khái niệm

Web cache poisoning (đầu độc bộ nhớ đệm web) là một kỹ thuật nâng cao, trong đó kẻ tấn công khai thác hành vi của máy chủ web và bộ nhớ đệm (cache) để một phản hồi HTTP độc hại được phục vụ cho những người dùng khác.

Về cốt lõi, web cache poisoning gồm hai giai đoạn. Trước hết, kẻ tấn công phải tìm cách khiến máy chủ back-end tạo ra một phản hồi vô tình chứa một loại payload nguy hiểm nào đó. Khi đã thành công, chúng cần bảo đảm phản hồi này được lưu vào bộ nhớ đệm và sau đó được phục vụ cho các nạn nhân mục tiêu.

Một bộ nhớ đệm bị đầu độc có thể trở thành phương tiện gây hại nghiêm trọng để phân phối nhiều kiểu tấn công khác nhau, khai thác các lỗ hổng như XSS, chèn JavaScript, chuyển hướng mở (open redirection), v.v.
# Hoạt động


Để hiểu vì sao phát sinh các lỗ hổng web cache poisoning, điều quan trọng là phải nắm được kiến thức cơ bản về cách bộ nhớ đệm (web cache) vận hành.

Nếu máy chủ phải gửi một phản hồi mới cho từng yêu cầu (HTTP request) riêng lẻ, điều này rất có thể sẽ làm quá tải máy chủ, dẫn đến độ trễ và trải nghiệm người dùng kém, đặc biệt trong các giai đoạn cao điểm. Caching chủ yếu là một phương thức nhằm giảm bớt các vấn đề như vậy.

Cache nằm giữa máy chủ và người dùng, nơi nó lưu (cache) các phản hồi cho những yêu cầu cụ thể, thường trong một khoảng thời gian cố định. Nếu một người dùng khác gửi một yêu cầu tương đương, cache chỉ đơn giản phục vụ trực tiếp cho người dùng một bản sao của phản hồi đã được lưu, không cần bất kỳ tương tác nào từ back-end. Điều này giúp giảm tải đáng kể cho máy chủ bằng cách giảm số lượng yêu cầu trùng lặp mà máy chủ phải xử lý.
![](../../image/Pasted%20image%2020260507105603.png)

## Cache keys


Khi cache nhận một yêu cầu HTTP, trước tiên nó phải xác định xem có một phản hồi đã được lưu mà nó có thể phục vụ trực tiếp hay không, hoặc nó phải chuyển tiếp yêu cầu để back-end xử lý. Cache nhận diện các yêu cầu tương đương bằng cách so sánh một tập con được định nghĩa trước của các thành phần trong yêu cầu, gọi chung là “cache key”. Thông thường, phần này sẽ bao gồm dòng yêu cầu (request line) và header Host. Những thành phần của yêu cầu không nằm trong cache key được gọi là “unkeyed”.

Nếu cache key của một yêu cầu đến khớp với key của một yêu cầu trước đó, thì cache xem chúng là tương đương. Kết quả là, nó sẽ phục vụ một bản sao của phản hồi đã được lưu được tạo ra cho yêu cầu ban đầu. Điều này áp dụng cho tất cả các yêu cầu tiếp theo có cache key khớp, cho đến khi phản hồi đã lưu hết hạn.

Điểm mấu chốt là các thành phần khác của yêu cầu hoàn toàn bị cache bỏ qua. Chúng ta sẽ phân tích kỹ hơn tác động của hành vi này ở phần sau.

# Hậu quả

Tác động của web cache poisoning phụ thuộc nhiều vào hai yếu tố chính:

- **Kẻ tấn công thực sự có thể đưa những gì vào cache thành công**
    
    Vì bộ nhớ đệm bị đầu độc chủ yếu là phương tiện phân phối thay vì một cuộc tấn công độc lập, nên tác động của web cache poisoning gắn chặt với mức độ nguy hại của payload được tiêm. Cũng như hầu hết các kiểu tấn công khác, web cache poisoning có thể được kết hợp với các tấn công khác để leo thang mức độ ảnh hưởng hơn nữa.
    
- **Lượng truy cập của trang bị ảnh hưởng**
    
    Phản hồi bị đầu độc chỉ được phục vụ cho người dùng truy cập trang bị ảnh hưởng trong khi cache đang bị đầu độc. Do đó, tác động có thể dao động từ không đáng kể đến rất lớn tùy thuộc vào mức độ phổ biến của trang. Ví dụ, nếu kẻ tấn công đầu độc được phản hồi được cache của trang chủ một website lớn, cuộc tấn công có thể ảnh hưởng đến hàng nghìn người dùng mà không cần bất kỳ tương tác tiếp theo nào từ kẻ tấn công.
    

> **Lưu ý** Thời lượng lưu của một mục cache không nhất thiết ảnh hưởng đến tác động của web cache poisoning. Một cuộc tấn công thường có thể được viết script để đầu độc lại cache vô thời hạn.

# Xây dựng cuộc tấn công

Nói chung, việc xây dựng một cuộc tấn công web cache poisoning cơ bản gồm các bước sau:

- Xác định và đánh giá các đầu vào không được đưa vào khóa cache (unkeyed inputs)
- Khiến máy chủ back-end phát sinh một phản hồi có hại
- Làm cho phản hồi đó được lưu vào bộ nhớ đệm (cached)

## Identify and evaluate unkeyed inputs

Bất kỳ cuộc tấn công web cache poisoning nào cũng dựa vào việc thao túng các đầu vào không được đưa vào khóa cache (unkeyed), chẳng hạn như các header. Bộ nhớ đệm web bỏ qua các đầu vào unkeyed khi quyết định có phục vụ một phản hồi đã được lưu cache cho người dùng hay không. Hành vi này có nghĩa là bạn có thể dùng chúng để chèn payload và tạo ra một phản hồi “bị đầu độc” mà, nếu được cache, sẽ được phục vụ cho tất cả người dùng có yêu cầu trùng khớp cache key. Do đó, bước đầu tiên khi xây dựng một cuộc tấn công web cache poisoning là xác định các đầu vào unkeyed mà máy chủ hỗ trợ.

Bạn có thể xác định các đầu vào unkeyed thủ công bằng cách thêm các đầu vào ngẫu nhiên vào yêu cầu và quan sát xem chúng có ảnh hưởng đến phản hồi hay không. Điều này có thể hiển nhiên, như phản xạ đầu vào trực tiếp trong phản hồi, hoặc kích hoạt một phản hồi hoàn toàn khác. Tuy nhiên, đôi khi ảnh hưởng tinh vi hơn và cần một chút “phá án” để tìm ra. Bạn có thể dùng các công cụ như Burp Comparer để so sánh phản hồi có và không có đầu vào đã chèn, nhưng việc này vẫn đòi hỏi khá nhiều công sức thủ công.
### Param Miner

May mắn là bạn có thể tự động hóa quá trình xác định các đầu vào unkeyed bằng cách thêm tiện ích mở rộng Param Miner vào Burp từ BApp store. Để dùng Param Miner, bạn chỉ cần nhấp chuột phải vào một yêu cầu muốn điều tra và chọn “Guess headers”. Param Miner sau đó chạy nền, gửi các yêu cầu chứa những đầu vào khác nhau từ danh sách header tích hợp, phong phú của nó. Nếu một yêu cầu chứa đầu vào đã chèn có ảnh hưởng đến phản hồi, Param Miner sẽ ghi nhận điều này trong Burp, hoặc ở khung “Issues” nếu bạn dùng Burp Suite Professional, hoặc trong thẻ “Output” của tiện ích (“Extensions” > “Installed” > “Param Miner” > “Output”) nếu bạn dùng Burp Suite Community Edition.

Ví dụ, trong ảnh chụp màn hình sau, Param Miner đã tìm thấy một header unkeyed `X-Forwarded-Host` trên trang chủ của website:

> **Caution:** Khi kiểm thử các đầu vào unkeyed trên một website đang hoạt động, có rủi ro vô tình khiến cache phục vụ các phản hồi bạn tạo ra cho người dùng thật. Vì vậy, điều quan trọng là bảo đảm mọi yêu cầu của bạn đều có một cache key duy nhất để chỉ được phục vụ cho chính bạn. Để làm điều này, bạn có thể thủ công thêm một cache buster (chẳng hạn một tham số duy nhất) vào dòng yêu cầu mỗi lần gửi. Ngoài ra, nếu bạn dùng Param Miner, có các tùy chọn để tự động thêm cache buster vào mọi yêu cầu.

## Gây ra phản hồi độc hại từ máy chủ back-end

Khi bạn đã xác định được một đầu vào **unkeyed**, bước tiếp theo là đánh giá chính xác website xử lý đầu vào đó như thế nào. Hiểu rõ điều này là then chốt để có thể khiến máy chủ trả về một phản hồi độc hại. Nếu một đầu vào được phản xạ trong phản hồi từ máy chủ mà không được **sanitize** đúng cách, hoặc được dùng để sinh ra dữ liệu khác một cách động, thì đây là một điểm vào tiềm năng cho tấn công web cache poisoning.
## **Làm cho phản hồi được lưu vào cache**

Việc thao túng đầu vào để tạo ra phản hồi độc hại mới chỉ là một nửa chặng đường; nó không mang lại nhiều hiệu quả trừ khi bạn có thể khiến phản hồi đó được lưu vào cache, điều mà đôi khi khá khó.

Việc một phản hồi có được cache hay không có thể phụ thuộc vào nhiều yếu tố, như đuôi tệp (`file extension`), kiểu nội dung (`Content-Type`), `route`, mã trạng thái (`status code`) và các `header` phản hồi. Có lẽ bạn sẽ cần dành thời gian thử nghiệm các yêu cầu trên những trang khác nhau và quan sát hành vi của cache. Khi bạn tìm ra cách để một phản hồi chứa dữ liệu độc hại của mình được cache, bạn đã sẵn sàng để phát tán mã độc đến người dùng nạn nhân.
# **Khai thác các lỗi thiết kế của cache**

Trong phần này, chúng ta sẽ xem xét kỹ hơn cách các lỗ hổng web cache poisoning có thể phát sinh do những khiếm khuyết chung trong thiết kế của bộ nhớ đệm (cache). Chúng ta cũng sẽ minh họa cách các khiếm khuyết này có thể bị khai thác.

Tóm lại, website sẽ dễ bị web cache poisoning nếu xử lý đầu vào không thuộc khóa cache (unkeyed input) theo cách không an toàn và cho phép các phản hồi HTTP tiếp theo được lưu vào bộ nhớ đệm. Lỗ hổng này có thể được sử dụng như một phương thức phân phối cho nhiều kiểu tấn công khác nhau.

## XSS

Có lẽ lỗ hổng web cache poisoning dễ khai thác nhất là khi đầu vào **unkeyed** được phản xạ trong một phản hồi có thể được cache mà không được **sanitize** đúng cách.

Ví dụ, hãy xem xét yêu cầu và phản hồi sau:

```
GET /en?region=uk HTTP/1.1
Host: innocent-website.com
X-Forwarded-Host: innocent-website.co.uk

HTTP/1.1 200 OK
Cache-Control: public
<meta property="og:image" content="<https://innocent-website.co.uk/cms/social.png>" />
```

Ở đây, giá trị của header `X-Forwarded-Host` đang được dùng để tạo động URL ảnh Open Graph, và sau đó được phản xạ trong phản hồi. Quan trọng với web cache poisoning là header `X-Forwarded-Host` thường là unkeyed. Trong ví dụ này, cache có thể bị đầu độc bằng một phản hồi chứa payload XSS đơn giản:

```
GET /en?region=uk HTTP/1.1
Host: innocent-website.com
X-Forwarded-Host: a."><script>alert(1)</script>"

HTTP/1.1 200 OK
Cache-Control: public
<meta property="og:image" content="<https://a>."><script>alert(1)</script>"/cms/social.png" />
```

Nếu phản hồi này bị cache, tất cả người dùng truy cập `/en?region=uk` sẽ được phục vụ payload XSS này. Ví dụ này chỉ gây ra một `alert` trong trình duyệt nạn nhân, nhưng một cuộc tấn công thực sự có thể đánh cắp mật khẩu và chiếm đoạt tài khoản người dùng.
## **Unsafe handling of resource imports**

Một số website sử dụng các header unkeyed để sinh động các URL dùng để nhập (import) tài nguyên, chẳng hạn các file JavaScript được host bên ngoài. Trong trường hợp này, nếu kẻ tấn công thay đổi giá trị của header tương ứng sang một domain do họ kiểm soát, họ có thể thao túng URL để trỏ tới file JavaScript độc hại của chính họ.

Nếu phản hồi chứa URL độc hại này bị cache, file JavaScript của kẻ tấn công sẽ bị import và thực thi trong phiên trình duyệt của bất kỳ người dùng nào có yêu cầu khớp cache key.

```
GET / HTTP/1.1
Host: innocent-website.com
X-Forwarded-Host: evil-user.net
User-Agent: Mozilla/5.0 Firefox/57.0

HTTP/1.1 200 OK
<script src="<https://evil-user.net/static/analytics.js>"></script>
```
## **Cookie-handling vulnerabilities**

Cookie thường được dùng để sinh động nội dung trong một phản hồi. Một ví dụ phổ biến có thể là cookie cho biết ngôn ngữ ưa thích của người dùng, sau đó được dùng để load phiên bản tương ứng của trang:

```
GET /blog/post.php?mobile=1 HTTP/1.1
Host: innocent-website.com
User-Agent: Mozilla/5.0 Firefox/57.0
Cookie: language=pl;
Connection: close
```

Trong ví dụ này, phiên bản tiếng Ba Lan của một bài blog đang được yêu cầu. Lưu ý rằng thông tin về phiên bản ngôn ngữ nào sẽ được phục vụ chỉ nằm trong header `Cookie`. Giả sử rằng cache key chứa dòng yêu cầu (request line) và header `Host`, nhưng **không** chứa header `Cookie`. Trong trường hợp này, nếu phản hồi cho yêu cầu này bị cache, thì tất cả những người dùng truy cập bài blog đó sau này sẽ nhận được phiên bản tiếng Ba Lan, bất kể họ thực sự chọn ngôn ngữ nào.

Việc cache xử lý cookie sai cách như vậy cũng có thể bị khai thác bằng kỹ thuật web cache poisoning. Tuy nhiên, trong thực tế, vector này tương đối hiếm so với đầu độc cache dựa trên header. Khi tồn tại lỗ hổng đầu độc cache dựa trên cookie, chúng thường bị phát hiện và khắc phục nhanh chóng vì người dùng hợp lệ đôi khi vô tình làm đầu độc cache.
## **Multiple headers**

Một số website dễ bị khai thác bằng các exploit web cache poisoning đơn giản, như đã minh họa ở trên. Tuy nhiên, những website khác yêu cầu các tấn công tinh vi hơn và chỉ trở nên dễ bị tấn công khi kẻ tấn công có thể tạo một yêu cầu thao túng nhiều đầu vào **unkeyed**.

Ví dụ, giả sử một website yêu cầu giao tiếp an toàn qua HTTPS. Để thực thi điều này, nếu nhận được một yêu cầu sử dụng giao thức khác, website sẽ động tạo một redirect tới chính nó sử dụng HTTPS:

```
GET /random HTTP/1.1
Host: innocent-site.com
X-Forwarded-Proto: http

HTTP/1.1 301 moved permanently
Location: <https://innocent-site.com/random>
```

Bản thân hành vi này không nhất thiết là dễ bị tấn công. Tuy nhiên, bằng cách kết hợp với những gì ta đã học trước đó về các lỗ hổng trong URL được sinh động, kẻ tấn công có thể khai thác hành vi này để tạo ra một phản hồi có thể được cache mà chuyển hướng người dùng tới một URL độc hại.
## Phản hồi tiết lộ quá nhiều thông tin

Đôi khi các website tự làm mình dễ bị web cache poisoning hơn bằng cách tiết lộ quá nhiều thông tin về bản thân và hành vi của chúng.
### **Các chỉ dẫn Cache-Control**

Một trong những thách thức khi xây dựng cuộc tấn công web cache poisoning là đảm bảo rằng phản hồi độc hại được lưu vào cache. Việc này có thể đòi hỏi khá nhiều thử nghiệm thủ công để nghiên cứu hành vi của cache. Tuy nhiên, đôi khi các phản hồi rõ ràng tiết lộ một số thông tin mà kẻ tấn công cần để đầu độc cache thành công.

Một ví dụ như khi phản hồi chứa thông tin về tần suất cache bị xóa (purge) hoặc độ tuổi của phản hồi đang được cache:

```
HTTP/1.1 200 OK
Via: 1.1 varnish-v4
Age: 174
Cache-Control: public, max-age=1800
```

Mặc dù điều này không trực tiếp dẫn tới lỗ hổng web cache poisoning, nhưng nó giúp kẻ tấn công tiết kiệm công sức thử nghiệm thủ công vì họ biết chính xác khi nào nên gửi payload để đảm bảo payload đó được cache.

Kiến thức này cũng cho phép những cuộc tấn công tinh vi hơn. Thay vì gửi một lượng lớn yêu cầu tới back-end cho tới khi một yêu cầu thành công (cách này có thể gây chú ý), kẻ tấn công có thể canh thời gian cẩn thận và chỉ gửi một yêu cầu độc hại duy nhất để đầu độc cache.

### **Header Vary**

Cách sử dụng thô sơ mà header `Vary` thường được áp dụng cũng có thể giúp đỡ kẻ tấn công. Header `Vary` chỉ định danh sách các header bổ sung nên được coi là một phần của cache key ngay cả khi chúng thường là unkeyed. Nó thường được dùng để chỉ rằng header `User-Agent` là có khóa (keyed), ví dụ, để nếu phiên bản mobile của một website được cache thì sẽ không bị phục vụ cho người dùng không phải mobile.

Thông tin này cũng có thể được tận dụng để xây dựng một cuộc tấn công nhiều bước nhằm nhắm tới một tập người dùng cụ thể. Ví dụ, nếu kẻ tấn công biết header `User-Agent` là một phần của cache key, bằng cách xác định trước user-agent của nạn nhân mục tiêu, họ có thể tùy chỉnh cuộc tấn công sao cho chỉ những người dùng có user-agent đó bị ảnh hưởng. Hoặc họ có thể tìm ra user-agent được dùng nhiều nhất để truy cập site, rồi tùy chỉnh cuộc tấn công để ảnh hưởng tới nhiều người nhất theo cách đó.
## DOM

Như đã thảo luận trước đó, nếu website sử dụng không an toàn các header unkeyed để import file, điều này có thể bị kẻ tấn công lợi dụng để import file độc hại thay vào. Tuy nhiên, điều này áp dụng cho nhiều loại file chứ không chỉ riêng file JavaScript.

Nhiều website sử dụng JavaScript để fetch và xử lý dữ liệu bổ sung từ back-end. Nếu một script xử lý dữ liệu từ server một cách không an toàn, điều này có thể dẫn tới đủ loại lỗ hổng dựa trên DOM.

Ví dụ, một kẻ tấn công có thể đầu độc cache bằng một phản hồi import một file JSON chứa payload sau:

```json
{"someProperty" : "<svg onload=alert(1)>"}
```

Nếu website sau đó truyền giá trị của thuộc tính này vào một sink hỗ trợ thực thi mã động, payload sẽ được thực thi trong ngữ cảnh phiên trình duyệt của nạn nhân.

Nếu bạn sử dụng web cache poisoning để khiến một website tải dữ liệu JSON độc hại từ server của bạn, bạn có thể cần cấp quyền truy cập cho website tới JSON bằng CORS:

```
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *

{
    "malicious json" : "malicious json"
}
```

## **Chaining web cache**

Như đã thấy ở phần trước, đôi khi kẻ tấn công chỉ có thể khiến máy chủ trả về một phản hồi độc hại bằng cách tạo một yêu cầu sử dụng nhiều header. Điều tương tự cũng đúng với các loại tấn công khác. Web cache poisoning đôi khi đòi hỏi kẻ tấn công phải xâu chuỗi nhiều kỹ thuật mà chúng ta đã thảo luận. Bằng cách xâu chuỗi các lỗ hổng khác nhau, thường có thể lộ ra những lớp lỗ hổng bổ sung vốn ban đầu không thể khai thác được.

# Khai thác các lỗi triển khai cache

Trong các lab trước, bạn đã học cách khai thác lỗ hổng web cache poisoning bằng cách thao túng các đầu vào unkeyed điển hình, như header HTTP và cookie. Mặc dù phương pháp này hiệu quả, nó chỉ chạm tới bề mặt những gì có thể xảy ra với web cache poisoning.

Trong phần này, chúng ta sẽ minh họa cách bạn có thể tiếp cận bề mặt tấn công rộng hơn nhiều cho web cache poisoning bằng cách khai thác các đặc thù trong các triển khai hệ thống cache cụ thể. Cụ thể, chúng ta sẽ xem xét vì sao các khiếm khuyết trong cách sinh khóa cache (cache key) đôi khi có thể khiến website dễ bị đầu độc cache thông qua những lỗ hổng riêng biệt vốn truyền thống bị coi là không thể khai thác. Chúng ta cũng sẽ chỉ ra cách bạn có thể đưa các kỹ thuật cổ điển tiến xa hơn để có khả năng đầu độc các bộ nhớ đệm ở cấp ứng dụng (application-level caches), thường mang lại kết quả tàn phá nghiêm trọng.

Những kỹ thuật này được ghi nhận lần đầu bởi Giám đốc Nghiên cứu của chúng tôi, James Kettle, trong bài trình bày “Web Cache Entanglement: Novel Pathways to Poisoning” tại BlackHat USA 2020. Nếu bạn quan tâm tới cách ông ấy phát hiện và khai thác các lỗ hổng này ngoài đời thật, bạn có thể truy cập bản ghi bài trình bày và whitepaper kèm theo từ trang nghiên cứu của chúng tôi.

## **Lỗ hổng khóa cache**

Nói chung, các website lấy hầu hết dữ liệu đầu vào từ **đường dẫn URL (URL path)** và **chuỗi truy vấn (query string)**. Do đó, đây là một bề mặt tấn công đã được khai thác nhiều cho các kỹ thuật tấn công khác nhau. Tuy nhiên, vì **dòng yêu cầu (request line)** thường là một phần của khóa cache, những đầu vào này truyền thống không được coi là phù hợp để đầu độc cache. Bất kỳ payload nào chèn qua các đầu vào **được khóa (keyed inputs)** sẽ hoạt động như một **cache buster**, nghĩa là mục cache bị đầu độc của bạn hầu như chắc chắn sẽ không bao giờ được phục vụ cho người dùng khác.

Tuy nhiên, khi xem xét kỹ hơn, hành vi của các hệ thống cache riêng lẻ không phải lúc nào cũng như bạn mong đợi. Trong thực tế, nhiều website và CDN thực hiện các biến đổi khác nhau trên các thành phần được khóa khi chúng được lưu vào khóa cache. Điều này có thể bao gồm:

- Loại trừ chuỗi truy vấn (excluding the query string)
- Lọc ra những tham số truy vấn cụ thể (filtering out specific query parameters)
- Chuẩn hóa đầu vào trong các thành phần được khóa (normalizing input in keyed components)

Những biến đổi này có thể tạo ra một vài đặc điểm kỳ quặc không mong đợi. Chúng chủ yếu dựa trên sự khác biệt giữa dữ liệu được ghi vào khóa cache và dữ liệu được truyền vào mã ứng dụng, mặc dù tất cả đều bắt nguồn từ cùng một đầu vào. Những lỗi khóa cache này có thể bị lợi dụng để đầu độc cache thông qua các đầu vào mà ban đầu có vẻ không thể sử dụng được.

Trong trường hợp các bộ nhớ đệm tích hợp hoàn toàn ở cấp ứng dụng (application-level caches), những khác biệt này có thể còn cực đoan hơn. Thực tế cho thấy các cache nội bộ có thể khó đoán đến mức đôi khi rất khó để kiểm thử chúng mà không vô tình đầu độc cache cho người dùng thật.
## Phương pháp dò lỗi

Phương pháp dò tìm các lỗi triển khai cache khác với phương pháp cổ điển của web cache poisoning một chút. Những kỹ thuật mới này dựa trên các khiếm khuyết trong triển khai và cấu hình cụ thể của cache, vốn có thể khác nhau rất nhiều giữa các trang. Điều này có nghĩa là bạn cần hiểu sâu hơn về cache mục tiêu và hành vi của nó.

Trong phần này, chúng tôi sẽ phác thảo phương pháp tổng quát để dò xét cache nhằm hiểu hành vi của nó và xác định bất kỳ khiếm khuyết tiềm ẩn nào. Sau đó, chúng tôi sẽ cung cấp một số ví dụ cụ thể hơn về các lỗi khóa cache phổ biến và cách bạn có thể khai thác chúng.

Phương pháp bao gồm các bước sau:

- Xác định một **cache oracle** phù hợp
- Thăm dò cách xử lý thành phần khóa (probe key handling)
- Xác định một gadget có thể khai thác được


### **Xác định một cache oracle phù hợp**


Bước đầu tiên là xác định một “cache oracle” phù hợp để bạn dùng cho việc thử nghiệm. Cache oracle đơn giản chỉ là một trang hoặc endpoint cung cấp phản hồi về hành vi của cache. Nó cần phải có thể được cache và phải chỉ ra theo cách nào đó rằng bạn nhận được phản hồi từ cache hay trực tiếp từ server. Phản hồi này có thể ở nhiều dạng, chẳng hạn:

- Một header HTTP cho biết rõ ràng bạn có cache hit hay không
- Thay đổi có thể quan sát được ở nội dung động
- Thời gian phản hồi khác biệt

Lý tưởng nhất là cache oracle cũng phản chiếu toàn bộ URL và ít nhất một tham số truy vấn trong phản hồi. Điều này sẽ giúp dễ nhận thấy các sai khác trong cách phân tích giữa cache và ứng dụng, điều hữu ích khi xây dựng các exploit khác sau này.

Nếu bạn xác định được rằng một cache bên thứ ba cụ thể đang được sử dụng, bạn cũng có thể tham khảo tài liệu tương ứng. Tài liệu đó có thể chứa thông tin về cách khóa cache mặc định được tạo. Bạn thậm chí có thể tình cờ tìm thấy các mẹo hữu dụng, chẳng hạn các tính năng cho phép bạn xem trực tiếp khóa cache. Ví dụ, các trang dùng Akamai có thể hỗ trợ header `Pragma: akamai-x-get-cache-key`, bạn có thể dùng để hiện khóa cache trong header phản hồi:

```
GET /?param=1 HTTP/1.1
Host: innocent-website.com
Pragma: akamai-x-get-cache-key

HTTP/1.1 200 OK
X-Cache-Key: innocent-website.com/?param=1
```
### Thăm dò cách xử lý thành phần khóa

Bước tiếp theo là điều tra xem cache có thực hiện bất kỳ xử lý bổ sung nào đối với đầu vào của bạn khi tạo khóa cache hay không. Bạn đang tìm kiếm một bề mặt tấn công bổ sung ẩn trong các thành phần ban đầu có vẻ được khóa.

Bạn nên chú ý cụ thể tới bất kỳ biến đổi nào đang diễn ra. Có thành phần nào bị loại trừ khỏi một thành phần được khóa khi nó được thêm vào khóa cache không? Ví dụ phổ biến là loại trừ một số tham số truy vấn cụ thể, hoặc thậm chí loại trừ toàn bộ query string, và loại bỏ port khỏi header Host.

Nếu bạn may mắn có quyền truy cập trực tiếp vào khóa cache, bạn chỉ cần so sánh khóa sau khi chèn các đầu vào khác nhau. Nếu không, bạn có thể dùng hiểu biết về cache oracle để suy luận xem liệu bạn có nhận được phản hồi đã được cache hay không. Với mỗi trường hợp muốn kiểm tra, bạn gửi hai yêu cầu tương tự và so sánh các phản hồi.

Giả sử cache oracle giả định của chúng ta là trang chủ của website mục tiêu. Trang này tự động redirect người dùng tới một trang theo vùng (region-specific page). Nó dùng header `Host` để sinh động header `Location` trong phản hồi:

```
GET / HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 302 Moved Permanently
Location: <https://vulnerable-website.com/en>
Cache-Status: miss
```

Để kiểm tra xem port có bị loại khỏi khóa cache hay không, trước tiên ta cần gửi một yêu cầu có port tuỳ ý và đảm bảo rằng ta nhận được một phản hồi mới từ server phản ánh đầu vào này:

```
GET / HTTP/1.1
Host: vulnerable-website.com:1337

HTTP/1.1 302 Moved Permanently
Location: <https://vulnerable-website.com:1337/en>
Cache-Status: miss
```

Tiếp theo, ta gửi một yêu cầu khác, lần này không chỉ định port:

```
GET / HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 302 Moved Permanently
Location: <https://vulnerable-website.com:1337/en>
Cache-Status: hit
```

Như bạn thấy, chúng ta đã được phục vụ phản hồi đã được cache mặc dù header `Host` trong yêu cầu không chỉ định port. Điều này chứng tỏ port bị loại khỏi khóa cache. Quan trọng là, header đầy đủ vẫn được truyền vào mã ứng dụng và phản chiếu trong phản hồi.

Tóm lại, mặc dù header `Host` là thành phần được khóa, cách nó bị biến đổi bởi cache cho phép ta truyền một payload vào ứng dụng trong khi vẫn giữ một cache key “bình thường” sẽ được ánh xạ tới các yêu cầu của người dùng khác. Hành vi dạng này là khái niệm then chốt đứng sau tất cả các exploit mà chúng ta sẽ thảo luận trong phần này.

Bạn có thể dùng cách tiếp cận tương tự để nghiên cứu bất kỳ xử lý nào khác đối với đầu vào của bạn bởi cache. Đầu vào có bị chuẩn hóa theo cách nào không? Nó được lưu trữ như thế nào? Bạn có nhận thấy bất kỳ bất thường nào không? Chúng ta sẽ đề cập cách trả lời các câu hỏi này sau bằng các ví dụ cụ thể.

### **Xác định một gadget có thể khai thác được**


Tới lúc này, bạn nên đã có một hiểu biết khá vững về cách cache của website mục tiêu hoạt động và có thể đã tìm thấy một vài lỗi thú vị trong cách khóa cache được cấu tạo. Bước cuối cùng là xác định một **gadget** phù hợp mà bạn có thể xâu chuỗi với lỗi khóa cache này. Đây là kỹ năng quan trọng vì mức độ nghiêm trọng của bất kỳ cuộc tấn công web cache poisoning nào phụ thuộc nhiều vào gadget mà bạn có thể khai thác.

Các gadget này thường là các lỗ hổng phía client cổ điển, như XSS phản chiếu (reflected XSS) và open redirect. Bằng cách kết hợp chúng với web cache poisoning, bạn có thể tăng đáng kể mức độ nghiêm trọng của các cuộc tấn công này, biến một lỗ hổng phản chiếu thành dạng lưu trữ (stored). Thay vì phải thao túng nạn nhân truy cập một URL đặc biệt, payload của bạn sẽ tự động được phục vụ cho bất kỳ ai truy cập URL hợp lệ, bình thường.

Có lẽ thú vị hơn, các kỹ thuật này cho phép bạn khai thác một số lỗ hổng chưa được phân loại mà thường bị xem là “không thể khai thác” và bị bỏ qua không vá. Điều này bao gồm việc sử dụng nội dung động trong các file tài nguyên, và các exploit đòi hỏi các yêu cầu bị tạo lỗi (malformed requests) mà trình duyệt bình thường sẽ không gửi.

# **Khai thác các lỗi khóa cache**

Bây giờ bạn đã quen với phương pháp tổng quát, hãy xem một số lỗi khóa cache điển hình và cách bạn có thể khai thác chúng. Chúng ta sẽ đề cập:

- Port không được khóa
- Chuỗi truy vấn không được khóa — LABS
- Tham số truy vấn không được khóa — LABS
- Che giấu tham số cache — LABS
- Khóa cache bị chuẩn hóa — LABS
- Tiêm vào khóa cache — LABS
- Đầu độc cache nội bộ — LABS
## Port không được khóa

Header `Host` thường là một phần của khóa cache và vì vậy ban đầu có vẻ không phải là nơi thích hợp để chèn payload. Tuy nhiên, một số hệ thống cache sẽ phân tích header này và **loại bỏ port khỏi khóa cache**.

Trong trường hợp này, bạn có thể tận dụng header để thực hiện web cache poisoning. Ví dụ, xét trường hợp đã đề cập trước đó, nơi URL chuyển hướng được tạo động dựa trên header `Host`. Việc thêm một port tùy ý vào yêu cầu có thể cho phép bạn cấu thành một cuộc tấn công từ chối dịch vụ (DoS): tất cả người dùng truy cập trang chủ sẽ bị chuyển hướng tới một cổng vô dụng, làm “sập” trang chủ cho tới khi cache hết hạn.

Loại tấn công này còn có thể bị leo thang nếu website cho phép bạn chỉ định **port không phải số**. Ví dụ, bạn có thể dùng điều đó để tiêm một payload XSS.
## Chuỗi truy vấn không được khóa

Giống như header **Host**, dòng yêu cầu (request line) thường được đưa vào khóa. Tuy nhiên, một trong những biến đổi khóa cache phổ biến nhất là **loại trừ toàn bộ chuỗi truy vấn** (query string).

### Phát hiện

Nếu phản hồi báo rõ ràng cho bạn biết liệu bạn có nhận được cache hit hay không, biến đổi này tương đối dễ phát hiện — nhưng nếu không? Điều này làm cho các trang động trông như thể hoàn toàn tĩnh vì có thể khó biết bạn đang giao tiếp với cache hay với server.

Để nhận diện một trang động, bạn thường quan sát xem việc thay đổi giá trị tham số có ảnh hưởng tới phản hồi hay không. Nhưng nếu query string không được đưa vào khóa, hầu hết thời gian bạn vẫn sẽ nhận được cache hit, và do đó phản hồi không thay đổi bất kể bạn thêm tham số gì. Rõ ràng điều này cũng làm cho các tham số phá cache (cache-buster) truyền thống dựa trên query string trở nên vô dụng.

May mắn thay, có các cách thay thế để thêm cache buster, ví dụ thêm nó vào một header được khóa (keyed header) mà không can thiệp vào hành vi ứng dụng. Một vài ví dụ điển hình bao gồm:

- `Accept-Encoding: gzip, deflate, cachebuster`
- `Accept: */*, text/cachebuster`
- `Cookie: cachebuster=1`
- `Origin: <https://cachebuster.vulnerable-website.com`>

Nếu bạn dùng Param Miner, bạn cũng có thể chọn các tuỳ chọn **"Add static/dynamic cache buster"** và **"Include cache busters in headers"**. Khi đó nó sẽ tự động thêm cache buster vào các header thường được khóa trong mọi yêu cầu bạn gửi bằng công cụ kiểm thử thủ công của Burp.

Một cách tiếp cận khác là xem có bất kỳ sai khác nào giữa cách cache và back-end chuẩn hóa (normalize) đường dẫn hay không. Vì path gần như chắc chắn được khóa, bạn đôi khi có thể lợi dụng điều này để gửi các yêu cầu có các khóa khác nhau nhưng vẫn trúng cùng endpoint. Ví dụ, các mục sau đây có thể được cache riêng biệt nhưng được coi là tương đương với `GET /` trên back-end:

- Apache: `GET //`
- Nginx: `GET /%2F`
- PHP: `GET /index.php/xyz`
- .NET: `GET /(A(xyz)/`

Các biến đổi này đôi khi có thể che đi những lỗ hổng reflected XSS đáng chú ý. Nếu tester hay các trình quét tự động chỉ nhận được các phản hồi đã được cache mà không nhận ra, có thể nhìn giống như không có reflected XSS trên trang.


### Khai thác

Việc loại trừ query string khỏi khóa cache thực tế có thể làm cho những lỗ hổng reflected XSS trở nên nghiêm trọng hơn.

Thông thường, một cuộc tấn công như vậy phụ thuộc vào việc dụ nạn nhân truy cập một URL được tạo độc hại. Tuy nhiên, nếu đầu độc cache thông qua query string không được khóa, payload sẽ được phục vụ cho những người dùng truy cập một URL hoàn toàn bình thường. Điều này có khả năng ảnh hưởng tới một lượng lớn nạn nhân hơn mà không cần bất kỳ tương tác tiếp theo nào từ kẻ tấn công.

## Tham số truy vấn không được khóa

Cho đến nay ta đã thấy rằng trên một số website, toàn bộ chuỗi truy vấn (query string) bị loại khỏi khóa cache. Nhưng một số website chỉ loại trừ những tham số truy vấn cụ thể mà không liên quan tới ứng dụng back-end, chẳng hạn các tham số phục vụ phân tích (analytics) hoặc phục vụ quảng cáo có mục tiêu. Các tham số UTM như `utm_content` là những ứng viên tốt để kiểm tra trong quá trình thử nghiệm.

Những tham số đã bị loại khỏi khóa cache có khả năng ít ảnh hưởng đáng kể tới phản hồi. Khả năng cao là sẽ không có gadget hữu dụng nào chấp nhận dữ liệu từ những tham số này. Tuy nhiên, một số trang xử lý toàn bộ URL một cách dễ bị tổn thương, khiến có thể khai thác được các tham số bất kỳ.

## Che giấu tham số cache

Nếu bộ nhớ đệm loại trừ một tham số vô hại khỏi khóa bộ nhớ đệm (cache key), và bạn không tìm được gadget có thể khai thác dựa trên toàn bộ URL, bạn hoàn toàn có thể nghĩ là đã bế tắc. Tuy nhiên, chính ở điểm này lại có thể xuất hiện những điều thú vị.

Nếu bạn xác định được cách bộ nhớ đệm phân tích (parse) URL để nhận diện và loại bỏ những tham số không mong muốn, bạn có thể phát hiện ra những bất nhất (quirk) đáng chú ý. Điều đặc biệt quan tâm là các khác biệt trong cách phân tích giữa bộ nhớ đệm và ứng dụng. Điều này có khả năng cho phép bạn lén đưa các tham số tùy ý vào logic ứng dụng bằng cách “che dấu” (cloak) chúng trong một tham số bị loại trừ.

Ví dụ, quy ước thông thường là một tham số sẽ được tiền tố bởi dấu hỏi (?) nếu nó là tham số đầu tiên trong chuỗi truy vấn, hoặc bằng dấu & nếu không phải là tham số đầu. Một số thuật toán phân tích kém sẽ coi bất kỳ dấu `?` nào cũng là bắt đầu của một tham số mới, bất kể nó có phải là tham số đầu hay không.

Giả sử thuật toán loại trừ tham số khỏi khóa bộ nhớ đệm hoạt động theo cách này, nhưng thuật toán của server chỉ chấp nhận dấu `?` đầu tiên như một ký tự phân cách. Xét yêu cầu sau:

```graphql
GET /?example=123?excluded_param=bad-stuff-here
```

Trong trường hợp này, bộ nhớ đệm sẽ nhận diện hai tham số và loại bỏ tham số thứ hai khỏi khóa bộ nhớ đệm. Tuy nhiên, server không chấp nhận dấu `?` thứ hai là ký tự phân cách và thay vào đó chỉ nhìn thấy một tham số example, có giá trị là toàn bộ phần còn lại của chuỗi truy vấn — bao gồm payload của chúng ta. Nếu giá trị của example được đưa vào một gadget hữu ích, chúng ta đã thành công chèn payload mà không làm thay đổi cache key.
### Khai thác các bất đồng trong việc phân tích tham số

Các vấn đề cloaking tham số tương tự có thể xuất hiện theo chiều ngược lại, khi phía back-end nhận diện các tham số khác biệt mà bộ nhớ đệm thì không. Ví dụ, framework Ruby on Rails hiểu cả dấu ampersand `&` và dấu chấm phẩy `;` như ký tự phân tách. Khi kết hợp với một bộ nhớ đệm không chấp nhận điều này, bạn có thể khai thác một quirk khác để ghi đè giá trị của một tham số được đưa vào khóa trong logic ứng dụng.

Xét yêu cầu sau:

```graphql
GET /?keyed_param=abc&excluded_param=123;keyed_param=bad-stuff-here
```

Như tên gọi cho thấy, `keyed_param` được đưa vào khóa bộ nhớ đệm, còn `excluded_param` thì không. Nhiều bộ nhớ đệm chỉ xử lý điều này như hai tham số, bị phân tách bởi ampersand:

```graphql
keyed_param=abc
excluded_param=123;keyed_param=bad-stuff-here
```

Khi thuật toán phân tích loại bỏ `excluded_param`, khóa bộ nhớ đệm sẽ chỉ chứa `keyed_param=abc`. Trên back-end, tuy nhiên, Ruby on Rails nhìn thấy dấu chấm phẩy và tách chuỗi truy vấn thành ba tham số riêng biệt:

```graphql
keyed_param=abc
excluded_param=123
keyed_param=bad-stuff-here
```

Nhưng giờ đây xuất hiện một `keyed_param` trùng lặp. Đây là lúc `quirk` thứ hai phát huy tác dụng. Nếu có tham số trùng lặp với các giá trị khác nhau, Ruby on Rails sẽ ưu tiên phần tử xuất hiện sau cùng. Kết quả cuối cùng là khóa bộ nhớ đệm chứa một giá trị tham số vô hại, cho phép phản hồi được phục vụ từ cache như bình thường cho người dùng khác. Trên back-end, cùng một tham số lại có một giá trị hoàn toàn khác — chính là payload mà ta chèn vào. Giá trị thứ hai này sẽ được truyền vào gadget và phản ánh trong phản hồi bị nhiễm độc.

Khai thác này có thể đặc biệt mạnh nếu nó cho bạn quyền điều khiển một hàm sẽ được thực thi. Ví dụ, nếu một trang web sử dụng JSONP để thực hiện yêu cầu đa miền, thường sẽ có một tham số callback để thực thi một hàm nhất định trên dữ liệu trả về:

```graphql
GET /jsonp?callback=innocentFunction
```

Trong trường hợp này, bạn có thể dùng các kỹ thuật trên để ghi đè hàm callback mong đợi và thực thi JavaScript tùy ý.
### Khai thác hỗ trợ **fat GET**

Trong một vài trường hợp, HTTP method có thể **không được đưa vào key**. Điều này có thể cho phép bạn nhiễm độc cache bằng một yêu cầu `POST` chứa payload độc hại trong thân (body). Payload đó sau đó thậm chí có thể được phục vụ như phản hồi cho các yêu cầu `GET` của người dùng. Mặc dù kịch bản này khá hiếm, đôi khi bạn có thể đạt được hiệu ứng tương tự bằng cách đơn giản thêm một thân vào yêu cầu `GET` để tạo một **`fat GET`**:

```
GET /?param=innocent HTTP/1.1
…
param=bad-stuff-here
```

Trong trường hợp này, cache-key sẽ dựa trên **dòng yêu cầu (request line)**, nhưng giá trị tham số ở phía server sẽ được lấy từ **thân**.

Điều này chỉ khả thi nếu một website chấp nhận các yêu cầu `GET` có thân; tuy nhiên có những cách xử lý thay thế. Đôi khi bạn có thể khuyến khích việc xử lý `fat GET` bằng cách ghi đè phương thức HTTP, ví dụ:

```
GET /?param=innocent HTTP/1.1
Host: innocent-website.com
X-HTTP-Method-Override: POST
…
param=bad-stuff-here
```

Miễn là header **`X-HTTP-Method-Override`** **không được đưa vào khóa**, bạn có thể gửi một yêu cầu giả pseudo-POST trong khi vẫn giữ được khóa GET dựa trên dòng yêu cầu.

### Khai thác nội dung động trong việc import tài nguyên

Các tệp tài nguyên được import thường là tĩnh nhưng một số tệp phản chiếu input từ chuỗi truy vấn. Điều này thường được coi là vô hại bởi vì trình duyệt hiếm khi thực thi những tệp này khi xem trực tiếp, và kẻ tấn công không có quyền kiểm soát các URL được dùng để tải các phụ tài nguyên của một trang. Tuy nhiên, bằng cách kết hợp điều này với nhiễm độc bộ nhớ đệm web, đôi khi bạn có thể tiêm nội dung vào tệp tài nguyên.

Ví dụ, hãy xét một trang phản chiếu chuỗi truy vấn hiện tại trong một câu lệnh import:

```
GET /style.css?excluded_param=123);@import… HTTP/1.1

HTTP/1.1 200 OK
…
@import url(/site/home/index.part1.8a6715a2.css?excluded_param=123);@import…
```

Bạn có thể khai thác hành vi này để chèn CSS độc hại, từ đó chiết xuất thông tin nhạy cảm từ bất kỳ trang nào import `/style.css`.

Nếu trang import tệp CSS không chỉ định doctype, bạn thậm chí có thể khai thác các tệp CSS tĩnh. Với cấu hình phù hợp, trình duyệt sẽ đơn giản quét toàn bộ tài liệu tìm CSS rồi thực thi nó. Điều này có nghĩa là đôi khi bạn có thể nhiễm độc các tệp CSS tĩnh bằng cách làm trigg­er một lỗi phía server mà phản chiếu tham số truy vấn bị loại trừ:

```
GET /style.css?excluded_param=alert(1)%0A{}*{color:red;} HTTP/1.1

HTTP/1.1 200 OK
Content-Type: text/html
…
This request was blocked due to…alert(1){}*{color:red;}
```
## Khóa cache bị chuẩn hóa

Bất kỳ việc chuẩn hóa nào áp dụng cho khóa bộ nhớ đệm cũng có thể tạo ra hành vi có thể khai thác được. Thực tế, đôi khi nó còn cho phép một số khai thác mà bình thường gần như không thể thực hiện được.

Ví dụ, khi bạn tìm thấy XSS phản chiếu trong một tham số, thường thì khó có thể khai thác thực tế. Nguyên nhân là các trình duyệt hiện đại thường tự **mã hóa URL** các ký tự cần thiết khi gửi yêu cầu, và server không giải mã chúng. Kết quả là phản hồi mà nạn nhân nhận được chỉ chứa một chuỗi đã được mã hóa URL nên vô hại.

Một số triển khai cache chuẩn hóa input được đưa vào khóa khi thêm vào cache key. Trong trường hợp này, cả hai yêu cầu sau sẽ có cùng một khóa:

```
GET /example?param="><test>
GET /example?param=%22%3e%3ctest%3e
```

Hành vi này có thể cho phép bạn khai thác những lỗ hổng XSS mà bình thường bị coi là “không thể khai thác”. Nếu bạn gửi một yêu cầu độc hại bằng Burp Repeater, bạn có thể nhiễm độc cache với payload XSS **không được mã hóa**. Khi nạn nhân truy cập URL độc hại, payload sẽ vẫn bị trình duyệt của họ mã hóa theo URL; tuy nhiên, một khi URL được chuẩn hóa bởi cache, nó sẽ có cùng cache key với phản hồi chứa payload không mã hóa của bạn.

Kết quả là cache sẽ phục vụ phản hồi bị nhiễm độc và payload sẽ được thực thi phía client. Bạn chỉ cần đảm bảo cache đã bị nhiễm khi nạn nhân truy cập URL.

## Tiêm vào khóa cache

Bạn đôi khi sẽ phát hiện một lỗ hổng phía client trong một header được đưa vào khóa. Đây cũng là một vấn đề “không thể khai thác” cổ điển, nhưng đôi khi có thể bị khai thác bằng nhiễm độc bộ nhớ đệm.

Các thành phần được đưa vào khóa thường được gộp lại trong một chuỗi để tạo cache key. Nếu cache không thực hiện việc thoát (escape) đúng các ký tự phân cách giữa các thành phần, bạn có thể lợi dụng hành vi này để tạo hai yêu cầu khác nhau nhưng lại có cùng một cache key.

Ví dụ sau sử dụng hai dấu gạch dưới để phân tách các thành phần khác nhau trong cache key và không thoát chúng. Bạn có thể khai thác điều này bằng cách đầu tiên nhiễm độc cache với một yêu cầu chứa payload của bạn trong header tương ứng được đưa vào khóa:

```
GET /path?param=123 HTTP/1.1
Origin: '-alert(1)-'__

HTTP/1.1 200 OK
X-Cache-Key: /path?param=123__Origin='-alert(1)-'__

<script>…'-alert(1)-'…</script>
```

Nếu bạn sau đó khiến nạn nhân truy cập URL sau, họ sẽ được phục vụ phản hồi đã bị nhiễm độc:

```
GET /path?param=123__Origin='-alert(1)-'__ HTTP/1.1

HTTP/1.1 200 OK
X-Cache-Key: /path?param=123__Origin='-alert(1)-'__
X-Cache: hit

<script>…'-alert(1)-'…</script>
```
## Đầu độc cache nội bộ


Cho đến nay, chúng ta đã xem cách khai thác các lỗi trong cách triển khai bộ nhớ đệm web bên ngoài để mở rộng bề mặt tấn công ẩn trong các thành phần dường như được đưa vào khóa. Tuy nhiên, một số website triển khai hành vi caching trực tiếp bên trong ứng dụng bên cạnh việc sử dụng một thành phần ngoài riêng biệt. Điều này có thể mang lại một số lợi thế, chẳng hạn tránh được những bất đồng về phân tích mà ta đã xem trước đó.

Vì những bộ nhớ đệm tích hợp này được xây dựng dành riêng cho ứng dụng cụ thể, điều này cũng cho phép các nhà phát triển tùy chỉnh hành vi ở mức độ lớn hơn. Kết quả là, những bộ nhớ đệm này đôi khi có thể hoạt động theo những cách kỳ quặc mà bạn thường không thấy ở một bộ nhớ đệm ngoài tiêu chuẩn hơn, vốn phải tương thích với nhiều ứng dụng. Thỉnh thoảng, những hành vi lạ này cũng có thể tạo cơ hội cho một số khai thác poisoning bộ nhớ đệm có mức nghiêm trọng cao.

Thay vì lưu toàn bộ phản hồi, một số bộ nhớ đệm này chia phản hồi thành các mảnh có thể tái sử dụng và cache riêng lẻ từng mảnh. Ví dụ, một đoạn mã (snippet) để import một tài nguyên được sử dụng rộng rãi có thể được lưu như một mục cache độc lập. Người dùng sau đó có thể nhận phản hồi bao gồm sự trộn lẫn giữa nội dung từ server và một vài mảnh riêng lẻ lấy từ cache.

Vì các mảnh được cache này dự định tái sử dụng trên nhiều phản hồi khác nhau, khái niệm về cache key thực sự không còn phù hợp. Mỗi phản hồi chứa một mảnh nhất định sẽ tái sử dụng cùng mảnh cache đó, ngay cả khi phần còn lại của phản hồi hoàn toàn khác nhau. Trong kịch bản như vậy, việc poison cache có thể gây hậu quả rộng lớn, đặc biệt nếu bạn nhiễm độc một mảnh được dùng trên mọi trang. Do không có cache key, chỉ cần một yêu cầu là bạn đã có thể nhiễm độc mọi trang, cho mọi người dùng.

Điều này thường chỉ yêu cầu bạn sử dụng các kỹ thuật poisoning bộ nhớ đệm web cơ bản, chẳng hạn thao tác header Host.
### Cách xác định bộ nhớ đệm nội bộ

Một trong những thách thức do các cache ở mức ứng dụng tích hợp gây ra là chúng có thể khó nhận diện và điều tra vì thường không có phản hồi hiển thị ra phía người dùng. Để xác định những cache này, bạn có thể tìm vài dấu hiệu dễ nhận biết.

Ví dụ, nếu phản hồi phản chiếu sự trộn lẫn giữa cả input từ yêu cầu bạn vừa gửi và input từ một yêu cầu trước đó, đó là dấu hiệu chính rằng cache đang lưu mảnh thay vì toàn bộ phản hồi. Điều tương tự xảy ra nếu input của bạn được phản chiếu trong phản hồi của nhiều trang khác nhau, đặc biệt trên các trang mà bạn chưa từng cố gắng tiêm input.

Đôi khi, hành vi của cache đơn giản là kỳ lạ đến mức kết luận hợp lý nhất là phải có một bộ nhớ đệm nội bộ độc đáo và được tùy chỉnh.

Khi một website triển khai nhiều lớp caching, điều đó có thể khiến khó hiểu chuyện gì đang diễn ra phía sau hậu trường và khó nắm bắt hệ thống caching của website hoạt động như thế nào.

### Kiểm tra bộ nhớ đệm nội bộ một cách an toàn


Khi kiểm tra các bộ nhớ đệm web thông thường, chúng tôi khuyến nghị sử dụng **tham số phá cache (cache buster)** để ngăn phản hồi đã bị nhiễm độc của bạn được trả về cho người dùng khác. Tuy nhiên, nếu một bộ nhớ đệm tích hợp không có khái niệm về khóa (cache key), thì các thủ thuật phá cache truyền thống trở nên vô tác dụng. Điều này có nghĩa là rất dễ vô tình nhiễm độc cache cho người dùng thực.

Do đó, điều quan trọng là bạn phải cố gắng giảm thiểu thiệt hại có thể xảy ra khi kiểm thử các loại lỗ hổng này. Hãy suy nghĩ cẩn thận về tác động của payload bạn định chèn trước khi gửi mỗi yêu cầu. Cụ thể, bạn nên đảm bảo rằng chỉ nhiễm độc cache bằng cách sử dụng một tên miền do bạn kiểm soát, thay vì một tên miền ngẫu nhiên như “[evil-user.net](http://evil-user.net)”. Bằng cách này, bạn sẽ kiểm soát được những gì xảy ra tiếp theo nếu có sự cố.

# Bảo mật

Cách chắc chắn để ngăn ngừa nhiễm độc bộ nhớ đệm web rõ ràng là tắt hoàn toàn caching. Mặc dù với nhiều website điều này có thể không thực tế, trong một số trường hợp thì khả thi. Ví dụ, nếu bạn chỉ dùng caching vì nó được bật mặc định khi bạn áp dụng một CDN, bạn nên xem xét liệu các tùy chọn caching mặc định đó có thực sự phù hợp với nhu cầu của bạn hay không.

Ngay cả khi bạn cần dùng caching, giới hạn nó chỉ cho các phản hồi tĩnh (purely static responses) cũng là biện pháp hiệu quả, với điều kiện bạn đủ thận trọng khi xác định thứ gì được coi là “tĩnh”. Ví dụ, hãy đảm bảo rằng kẻ tấn công không thể lừa server backend lấy phiên bản tài nguyên tĩnh độc hại của họ thay vì tài nguyên hợp lệ.

Điều này cũng liên quan đến một điểm rộng hơn về an ninh web. Hầu hết website hiện nay tích hợp nhiều công nghệ bên thứ ba vào cả quy trình phát triển lẫn hoạt động hàng ngày. Dù hệ thống bảo mật nội bộ của bạn có mạnh tới đâu, ngay khi bạn tích hợp công nghệ của bên thứ ba vào môi trường, bạn đang phụ thuộc vào việc các nhà phát triển của công nghệ đó cũng chú ý đến bảo mật như bạn. Trên cơ sở “bạn chỉ an toàn bằng điểm yếu nhất của mình”, điều quan trọng là phải hiểu đầy đủ các hệ quả bảo mật của bất kỳ công nghệ bên thứ ba nào trước khi tích hợp nó.

Cụ thể trong bối cảnh nhiễm độc bộ nhớ đệm web, điều này không chỉ có nghĩa là quyết định có giữ caching ở trạng thái bật theo mặc định hay không, mà còn là xem xét các header nào được CDN của bạn hỗ trợ, ví dụ. Nhiều lỗ hổng web cache poisoning được mô tả ở trên lộ diện vì kẻ tấn công có thể thao túng một loạt header yêu cầu mơ hồ, nhiều header trong số đó hoàn toàn không cần thiết cho chức năng của website. Một lần nữa, bạn có thể tự phơi bày trước các kiểu tấn công này mà không nhận ra, chỉ vì bạn đã triển khai một công nghệ hỗ trợ các input không được đưa vào khóa theo mặc định. Nếu một header không cần thiết cho hoạt động của site, thì nó nên bị vô hiệu hóa.

Bạn cũng nên thực hiện các biện pháp phòng ngừa sau khi triển khai caching:

- Nếu bạn đang cân nhắc loại trừ một thứ gì đó khỏi cache key vì lý do hiệu năng, hãy chuyển hướng (rewrite) yêu cầu thay vì loại trừ.
- Không chấp nhận các yêu cầu fat GET. Hãy lưu ý rằng một số công nghệ bên thứ ba có thể cho phép điều này theo mặc định.
- Vá các lỗ hổng phía client ngay cả khi chúng có vẻ “không thể khai thác”. Một số lỗ hổng như vậy có thể thực sự bị khai thác do các quirk khó lường trong hành vi của cache. Có thể chỉ là vấn đề thời gian trước khi ai đó tìm ra một quirk—dù là liên quan đến cache hay thứ khác—khiến lỗ hổng này trở nên có thể khai thác.

# WU
- [x] Web cache poisoning with an unkeyed header
- [x] Web cache poisoning with an unkeyed cookie
- [x] Web cache poisoning with multiple headers
- [x] Targeted web cache poisoning using an unknown header
- [ ] Web cache poisoning to exploit a DOM vulnerability via a cache with strict cacheability criteria
- [ ] Combining web cache poisoning vulnerabilities
- [x] Web cache poisoning via an unkeyed query string
- [x] Web cache poisoning via an unkeyed query parameter
- [x] Parameter cloaking
- [x] Web cache poisoning via a fat GET request
- [x] URL normalization
- [ ] Cache key injection
- [ ] Internal cache poisoning

## Web cache poisoning with an unkeyed header

- **cache key** thường bao gồm: method, URL và host header
- **unkeyed header**: là những header ko nằm trong cache key. Nghĩa là dù ta thay đổi giá trị của header này, Cache vẫn coi đó là "cùng một request" và trả về bản lưu cũ. 

- đầu tiên là phải tìm ra unkeyed header.
- ở gói tin trên burp, gửi sang repeater, click chuột phải chọn extension => param miner => guess param
ở log thấy có thông báo rằng tools đã tìm ra cache poisoning với header X-forwarded-Host
![](../../image/Pasted%20image%2020260507151800.png)

- đổi thử thành minh.com sau đó gửi
![](../../image/Pasted%20image%2020260507152203.png)

thấy trong response đường dẫn file .js đã truyền minh.com vào để build lên url


- chuẩn bị payload: trên trang exploit, đổi đường dẫn file thành: `/resources/js/tracking.js`
- đổi x-forwarded-host sang địa chỉ của trang exploit
![](../../image/Pasted%20image%2020260511095740.png)
- và phần body: đổi sang: `alert(document.cookie)` và ấn stored.
- ấn send request liên tục tới khi thấy X-cache: hit và đợi victim truy cập vào trang chủ của lab để trigger alert
![](../../image/Pasted%20image%2020260511100059.png)


## Web cache poisoning with unkeyed cookie
- ở burp khi mở gói tin GET tới trang chủ, thấy 1 cookie: `fehost`:
![](../../image/Pasted%20image%2020260511102301.png)

`fehost` thường là viết tắt của **Front-End Host**. Đây là một loại **Session Cookie** hoặc **Persistence Cookie** được tạo ra bởi các thiết bị mạng ở tầng trung gian (như Load Balancer, Reverse Proxy, hoặc Web Cache).

Mục đích chính của cookie này là để duy trì **Session Stickiness** (hay còn gọi là Session Affinity):
- Khi một hệ thống có nhiều cụm server phía sau (Backend), Load Balancer sẽ cấp cho bạn một cái cookie `fehost`.
- Giá trị của `fehost` sẽ định danh một server cụ thể trong cụm backend đó.
- Ở các request tiếp theo, trình duyệt gửi kèm cookie này để Load Balancer biết đường mà "ném" bạn đúng vào cái server cũ, tránh việc bị mất session giữa chừng.

	ở bài này, khi ta nhập giá trị trong fehost, ở response thấy server đã đưa thẳng giá trị vào mã js ở phía client => tìm cách phá vỡ cấu trúc json để chèn xss
![](../../image/Pasted%20image%2020260511102514.png)

- khi ta nhập: `fehost=some-value"-alert(1)-"any-value`, server sẽ hiểu đây là một phép trừ giữa các chuỗi và một hàm `alert(1)`. Hàm này sẽ được thực thi ngay lập tức

```
<script>
    data = {"host":"...","path":"/","frontend":"some-value"-alert(1)-"any-value"}
</script>
```

gửi requests tới khi victim truy cập và trigger alert

## Web cache poisoning with multiple headers

Trong nhiều hệ thống thực tế, luồng xử lý mã nguồn đôi khi bị ẩn đi bởi các câu lệnh điều kiện `if/else`.
- Nếu bạn chỉ gửi `X-Forwarded-Host: hacker.com`, hệ thống có thể bỏ qua vì nó đang giao tiếp qua HTTPS mặc định.
- Tuy nhiên, nếu bạn gửi thêm `X-Forwarded-Scheme: http`, Backend sẽ bị đánh lừa rằng đây là một request không an toàn. Nó lập tức kích hoạt cơ chế **Force HTTPS Redirect** (ép chuyển hướng sang HTTPS).
![](../../image/Pasted%20image%2020260511105900.png)

![](../../image/Pasted%20image%2020260511111120.png)
- ở file tĩnh .js này, ta ép cache trả về 1 lệnh điều hướng sang trang exploit server 
- cả X-Forwarded-Host và X-Forwarded-Scheme đều là `unkeyed` (ko nằm trong cache keys)

- trên server exploit, đổi file path thành /resources/js/tracking.js và body thành alert(document.cookie) để trigger alert
- sau khi stored, gửi liên tục request chứa cụm Header độc hại vào file JS cho đến khi bạn thấy Header `X-Cache: hit`

## Targeted web cache poisoning using an unknown header

- sử dụng param miner để tìm những header ẩn
![](../../image/Pasted%20image%2020260511140601.png)

- phát hiện header X-host ko đc công bố
- thử thêm 1 tham số rác (cache-buster) vào url để tránh ảnh hưởng đến cache thực tế và chèn header vào requst
![](../../image/Pasted%20image%2020260511143706.png)

giá trị minh.com được server sử dụng để tạo đường dẫn tuyệt đối nạp file .js
- đồng thời trong response thấy có header: vary
![](../../image/Pasted%20image%2020260511144233.png)
Điều này chứng tỏ Server phân mảnh bộ nhớ đệm dựa trên trình duyệt. Payload đầu độc chỉ có tác dụng nếu `User-Agent` trong request của kẻ tấn công khớp hoàn toàn với `User-Agent` của nạn nhân.

- ở trong phần cmt cho phép chèn thẻ html
- Chèn một thẻ ảnh độc hại để ép trình duyệt của bất kỳ ai đọc bình luận phải tạo request ra máy chủ bên ngoài: `<img src="https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/minh-sniffing" />`

ở access log, ta thấy có lịch sử truy cập từ ip lạ đến
![](../../image/Pasted%20image%2020260511153315.png)

- quay lại burp, sửa user agent, copy exploit url vào X-host: và send request tới khi victim truy cập trang web và trigger alert để solve 
![](../../image/Pasted%20image%2020260511153425.png)


## Web cache poisoining via an unkeyed query string

- các hệ thống Cache sẽ sử dụng toàn bộ url (cả query string sau dấu ?) làm Cache key
	- tuy nhiên thực tế các trang web thường sử dụng các tham số dùng để theo dõi (tracking parameters) như `utm_source, utm_medium` hoặc các tham số nội bộ. Việc tạo ra hàng nghìn bản cache khác nhau chỉ vì khác cái mã tracking là vô cùng lãng phí tài nguyên
=> do đó, các quản trị viên thường cấu hình Cache bỏ qua toàn bộ hoặc một số tham số trên url khi tính toán Cache key. Điều này biến query string thành một **unkeyed input**
Lỗ hổng xảy ra khi tầng cache bỏ qua query string, và backend vẫn nhận query string và reflect nó vào thẳng mã nguồn html mà ko sanitization

- khi thêm query string vào request GET thì X-cache miss rồi hit, => query string là unkeyed
![](../../image/Pasted%20image%2020260512100245.png)
- **kỹ thuật Cache buster bằng origin header**: để ép cache tạo ra bản mới khi đang bị hit, sử dụng header Origin làm cache buster
ví dụ: `Origin: minh1`. mỗi khi đổi giá trị thì cache sẽ coi đó là 1 request mới hoàn toàn giúp ta xem sự reflect của payload dễ dàng hơn.

![](../../image/Pasted%20image%2020260512100700.png)

- mục tiêu là phá vỡ cấu trúc thẻ <link>
`/?evil='/><script>alert(1)</script>`
Khi nạp vào trang web, nó sẽ biến thành: `<link rel="canonical" href="/?evil='/><script>alert(1)</script>"/>` _(Dấu `'/>` sẽ đóng thuộc tính href và đóng thẻ link, cho phép thẻ script thực thi).

- sau khi test xong, xóa header Origin và gửi lại payload vài lần để 

## Web cache poisoning via unkeyed query parameter

- Sự khác biệt giữa Query String và Query Parameter
	- **Unkeyed Query String:** Cache bỏ qua _tất cả_ những gì nằm sau dấu `?`.
	- **Unkeyed Query Parameter:** Cache chỉ bỏ qua _một vài_ tham số cụ thể được định nghĩa trong whitelist/blacklist (ví dụ: `utm_id`, `fbclid`, `affiliate_id`).
	- Nếu Backend vẫn xử lý và phản chiếu (reflect) giá trị của một tham số vào trang web, nhưng tầng Cache lại cấu hình tham số đó là **Unkeyed**, kẻ tấn công có thể chèn mã độc vào tham số này. Cache sẽ lưu bản ghi nhiễm độc và phục vụ cho tất cả người dùng truy cập vào URL mà không có tham số đó
![](../../image/Pasted%20image%2020260512111734.png)
- sử dụng param miner và guess query param, phát hiện tham số ẩn `utm_content`
![](../../image/Pasted%20image%2020260512112229.png)
- gửi request với param và thấy X-cache trả về hit => `utm_content` là unkeyed param 
![](../../image/Pasted%20image%2020260512112756.png)
tham số reflect ở thẻ <link ref canonical>

![](../../image/Pasted%20image%2020260512113740.png)

- gửi payload vài lần để X-cache hit để solved bài lab

## Web cache poisoning via fat GET request

- Thông thường, một request `GET` không có Body (thân hàm). Tuy nhiên, một số hệ thống hoặc thư viện HTTP vẫn cho phép gửi kèm dữ liệu trong Body của một request `GET`. Đây gọi là **"Fat GET"**. Lỗ hổng sẽ xảy ra nếu:
	- - **Tầng Cache:** Chỉ nhìn vào **URL** để xác định Cache Key và bỏ qua hoàn toàn Body của request `GET`.
	- **Tầng Backend:** Lại ưu tiên lấy dữ liệu từ **Body** nếu nó trùng tên với tham số trên URL (Tham số bị ghi đè - Parameter Overriding).
- nhìn vào burp, mỗi lần ấn vào trang web thì đều có 1 script là geolocate.js gọi đến function setCountryCookie.
![](../../image/Pasted%20image%2020260512142140.png)

- thêm 1 dòng ở phần body để chèn thêm giá trị khác cho callback
![](../../image/Pasted%20image%2020260512143752.png)
- ta thấy kết quả reflect vào hàm mới trong response
- đợi cache reset bản ghi và thay callback thành alert(1) và send tới server để victim truy cập
![](../../image/Pasted%20image%2020260512143926.png)


## Parameter cloaking
- đây là kỹ thuật kết hợp của 2 yếu tố: unkeyed param và sự khác biệt về delimeter discrepancy 
	- - **Tầng Cache (VD: Varnish, Cloudflare):** Thường tuân thủ nghiêm ngặt chuẩn HTTP, nó chỉ coi dấu `&` là ký tự phân cách giữa các tham số.
	- **Tầng Backend (VD: Ruby on Rails, Java Spring):** Nhiều framework web cũ hoặc cấu hình đặc biệt lại chấp nhận cả dấu `&` và dấu `;` làm ký tự phân cách.
dùng param miner để guess query param: thấy thông báo param cloaking, param ẩn là utm_content
![](../../image/Pasted%20image%2020260512151049.png)
![](../../image/Pasted%20image%2020260512151040.png)


![](../../image/Pasted%20image%2020260512153033.png)
giá trị của param reflect trong thẻ <link rel canonical>

- thử chèn thêm param với dấu ; thì thấy backend có nhận diện dấu `;`
- xóa param rác và thay giá trị thành alert(1) và spam đến khi victim truy cập lab
![](../../image/Pasted%20image%2020260512154541.png)


## URL normalization
- khi gửi 1 http requests, url thường chứa các ký tự đặc biệt đã đươc url encoding để đảm bảo truyền tải an toàn
- URL normallization là quá trình mà 1 server dịch và chuẩn hóa url về 1 định dạng chuẩn thống nhất trước khi xử lí logic.
	- ví dụ: biến %3e thành > hoặc rút gọn /abc/../js/ thành /js/

=> lỗ hổng ko nằm ở việc chuẩn hóa mà ở sự ko đồng nhất (inconsistency/discrepancy) giữa các thiết bị
Trong một hệ thống hiện đại, request của bạn sẽ đi qua **Cache (CDN/WAF)** trước khi đến **Backend**.
- **Trường hợp 1 (Tầng Cache an toàn):** Cache thường được cấu hình để "lười biếng". Nó nhận URL sao thì để nguyên vậy để tính **Cache Key** (không giải mã, không rút gọn thư mục).
- **Trường hợp 2 (Tầng Backend nhiệt tình):** Các framework Backend (như Spring, Flask, Ruby on Rails) lại tự động chuẩn hóa toàn bộ URL trước khi đọc tham số hoặc định tuyến (Routing).
👉 **Vấn đề:** Cache và Backend đang nhìn vào một URL nhưng lại hiểu thành hai ý nghĩa khác nhau!

- ở bài lab, có thể thấy trang web reflect bất cứ  chuỗi nào ta nhập vào request get
![](../../image/Pasted%20image%2020260512223821.png)

- trên web, copy phần payload và deliver to victim để solved
