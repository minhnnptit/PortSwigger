```table-of-contents
```

# Giới thiệu

Trong phần này, chúng ta sẽ thảo luận cách mà các cấu hình sai và logic nghiệp vụ lỗi có thể khiến các website phơi nhiễm với nhiều loại tấn công thông qua trường Host của HTTP. Chúng tôi sẽ phác thảo phương pháp ở mức cao để xác định các website dễ bị tấn công bởi tiêu đề Host HTTP và minh họa cách bạn có thể khai thác điều này cho các loại tấn công sau:

- Đầu độc quy trình đặt lại mật khẩu
- Đầu độc bộ nhớ đệm web
- Khai thác các lỗ hổng phía máy chủ cổ điển
- Vượt qua xác thực
- Dò host ảo bằng phương pháp brute-force
- SSRF dựa trên định tuyến
- Tấn công trạng thái kết nối
# Khái niệm

---

Tiêu đề Host của HTTP là một trường yêu cầu bắt buộc kể từ HTTP/1.1. Trường này chỉ định tên miền mà client muốn truy cập. Ví dụ, khi người dùng truy cập `https://portswigger.net/web-security`, trình duyệt của họ sẽ tạo một yêu cầu chứa trường Host như sau:

```
GET /web-security HTTP/1.1
Host: portswigger.net
```

Trong một số trường hợp, chẳng hạn khi yêu cầu bị chuyển tiếp bởi một hệ thống trung gian, giá trị Host có thể bị thay đổi trước khi đến thành phần back-end dự kiến. Chúng ta sẽ thảo luận chi tiết hơn về kịch bản này ở phần dưới.

# Mục đích


Mục đích của tiêu đề Host HTTP là giúp xác định thành phần back-end mà client muốn giao tiếp. Nếu yêu cầu không chứa trường Host, hoặc nếu trường Host bị sai định dạng theo bất kỳ cách nào, điều này có thể dẫn tới sự nhầm lẫn khi định tuyến các yêu cầu đến ứng dụng dự định.

Về mặt lịch sử, sự mơ hồ này không tồn tại bởi vì mỗi địa chỉ IP trước đây chỉ lưu trữ nội dung cho một miền duy nhất. Ngày nay, do xu hướng ngày càng gia tăng của các giải pháp dựa trên đám mây và việc thuê ngoài nhiều phần kiến trúc liên quan, nhiều website và ứng dụng thường cùng truy cập qua một địa chỉ IP. Cách làm này cũng phổ biến một phần do sự cạn kiệt địa chỉ IPv4.

Khi nhiều ứng dụng truy cập qua cùng một địa chỉ IP, điều này thường là kết quả của một trong các kịch bản sau.

## Virtual hosting


Một kịch bản là khi một máy chủ web duy nhất lưu trữ nhiều website hoặc ứng dụng. Đây có thể là nhiều website của cùng một chủ sở hữu, nhưng cũng có thể là các website của những chủ sở hữu khác nhau được lưu trữ trên cùng một nền tảng chia sẻ. Hiện tượng này ít phổ biến hơn trước nhưng vẫn xảy ra với một số dịch vụ SaaS trên đám mây.

Trong cả hai trường hợp, mặc dù mỗi website sẽ có tên miền khác nhau, chúng cùng chia sẻ một địa chỉ IP chung của máy chủ. Các website được lưu trữ theo cách này trên cùng một máy chủ được gọi là “host ảo” (virtual hosts).

Đối với người dùng thông thường khi truy cập website, một host ảo thường không phân biệt được với một website được lưu trữ trên máy chủ riêng.

## Định tuyến lưu lượng qua hệ thống trung gian


Một kịch bản phổ biến khác là khi các website được lưu trữ trên các máy chủ back-end riêng biệt, nhưng toàn bộ lưu lượng giữa client và các server lại được định tuyến qua một hệ thống trung gian. Đây có thể là một bộ cân bằng tải (load balancer) đơn giản hoặc một reverse proxy. Thiết lập này đặc biệt phổ biến khi client truy cập website qua một mạng phân phối nội dung (CDN).

Trong trường hợp này, mặc dù các website được lưu trữ trên các máy chủ back-end khác nhau, tất cả tên miền của chúng đều trỏ về một địa chỉ IP duy nhất của thành phần trung gian. Điều này tạo ra những thách thức tương tự như virtual hosting vì reverse proxy hoặc bộ cân bằng tải cần biết back-end thích hợp để định tuyến từng yêu cầu.

## HTTP Host header giải quyết vấn đề này như thế nào?


Trong cả hai kịch bản trên, trường Host được dùng để chỉ định người nhận dự định. Một phép ẩn dụ thông dụng là quá trình gửi thư tới ai đó sống trong một toà chung cư. Cả toà nhà có cùng một địa chỉ đường phố, nhưng phía sau địa chỉ đó có nhiều căn hộ khác nhau cần nhận thư đúng người. Một cách để giải quyết là ghi số căn hộ hoặc tên người nhận vào địa chỉ. Trong các thông điệp HTTP, tiêu đề Host đóng vai trò tương tự.

Khi trình duyệt gửi yêu cầu, URL đích sẽ được phân giải tới địa chỉ IP của một máy chủ cụ thể. Khi máy chủ này nhận yêu cầu, nó tham chiếu tới trường Host để xác định back-end dự định và chuyển tiếp yêu cầu tương ứng.

# Tấn công HTTP Host header là gì?


Tấn công tiêu đề Host HTTP lợi dụng các website dễ tổn thương khi xử lý giá trị của trường Host một cách không an toàn. Nếu máy chủ mặc định tin tưởng trường Host và không kiểm tra hoặc escape giá trị này đúng cách, kẻ tấn công có thể tận dụng đầu vào này để chèn các payload độc hại nhằm thao túng hành vi phía máy chủ. Các tấn công liên quan tới việc chèn payload trực tiếp vào trường Host thường được gọi là "Host header injection".

Các ứng dụng web đóng gói sẵn thường không biết chúng được triển khai trên domain nào trừ khi tên miền đó được chỉ định thủ công trong file cấu hình khi thiết lập. Khi cần biết domain hiện tại, ví dụ để tạo URL tuyệt đối được đưa vào email, chúng có thể lấy domain từ trường Host:

```html
<a href="https://_SERVER['HOST']/support">Liên hệ hỗ trợ</a>
```

Giá trị trường này cũng có thể được sử dụng trong nhiều tương tác giữa các hệ thống khác nhau trong hạ tầng của website.

Vì trường Host thực tế có thể bị điều khiển bởi người dùng, cách làm này có thể dẫn tới nhiều vấn đề. Nếu đầu vào không được escape hoặc kiểm tra đúng cách, trường Host là một vector tiềm năng để khai thác một loạt lỗ hổng khác, đáng chú ý nhất là:

- Đầu độc bộ nhớ đệm web
- Lỗi logic nghiệp vụ trong các chức năng cụ thể
- SSRF dựa trên định tuyến
- Các lỗ hổng phía máy chủ cổ điển, chẳng hạn như SQL injection
# Nguyên nhân


Lỗ hổng tiêu đề Host HTTP thường phát sinh do giả định sai lầm rằng trường này không thể bị người dùng điều khiển. Điều này dẫn tới việc đặt niềm tin một cách ngầm định vào trường Host và kết quả là thiếu kiểm tra hợp lệ (validation) hoặc thiếu escape giá trị của nó, mặc dù kẻ tấn công có thể dễ dàng sửa trường này bằng các công cụ như Burp Proxy.

Ngay cả khi bản thân trường Host được xử lý an toàn hơn, tùy vào cấu hình của các máy chủ xử lý yêu cầu đến, giá trị Host có thể bị ghi đè bằng cách chèn các trường header khác. Đôi khi chủ sở hữu website không biết rằng các header này được hỗ trợ theo mặc định và do đó chúng có thể không được kiểm soát chặt chẽ như nhau.

Thực tế, nhiều lỗ hổng này phát sinh không phải vì mã nguồn không an toàn mà vì cấu hình không an toàn của một hoặc nhiều thành phần trong hạ tầng liên quan. Những vấn đề cấu hình này có thể xảy ra vì website tích hợp các công nghệ bên thứ ba vào kiến trúc của họ mà không nhất thiết hiểu rõ các tuỳ chọn cấu hình và hệ quả an ninh của chúng.

# Kiểm thử

Để kiểm tra xem một website có dễ bị tấn công thông qua tiêu đề Host HTTP hay không, bạn sẽ cần một proxy chặn (intercepting proxy) như Burp Proxy, và các công cụ kiểm tra thủ công như Burp Repeater và Burp Intruder.

Nói ngắn gọn, bạn cần xác định xem có thể sửa trường Host và vẫn gửi được yêu cầu tới ứng dụng mục tiêu hay không. Nếu có, bạn có thể dùng trường này để dò hỏi ứng dụng và quan sát tác động của nó lên phản hồi.

## **Cung cấp tiêu đề Host tùy ý**

Khi dò tìm lỗ hổng chèn tiêu đề Host, bước đầu tiên là kiểm tra chuyện gì xảy ra khi bạn cung cấp một tên miền tùy ý, không được nhận dạng, qua trường Host.

Một số proxy chặn sẽ lấy địa chỉ IP đích trực tiếp từ trường Host, điều này khiến kiểu kiểm tra này gần như không thể thực hiện được; bất kỳ thay đổi nào bạn thực hiện trên trường này sẽ khiến yêu cầu được gửi tới một địa chỉ IP hoàn toàn khác. Tuy nhiên, Burp Suite giữ chính xác sự tách bạch giữa trường Host và địa chỉ IP đích. Sự tách bạch này cho phép bạn cung cấp bất kỳ tiêu đề Host tùy ý hoặc sai định dạng nào bạn muốn, đồng thời vẫn đảm bảo rằng yêu cầu được gửi tới đúng mục tiêu.

> **Mẹo**
> 
> URL đích được hiển thị ở đầu bảng (đối với Burp Repeater và chặn Proxy) hoặc trên thẻ **Target** trong Burp Intruder. Bạn có thể chỉnh sửa thủ công mục tiêu bằng cách nhấp vào biểu tượng cây bút.

Đôi khi, bạn vẫn có thể truy cập website mục tiêu ngay cả khi cung cấp một tiêu đề Host không mong đợi. Điều này có thể do nhiều lý do. Ví dụ, các server đôi khi được cấu hình với một tuỳ chọn mặc định hoặc dự phòng nếu chúng nhận yêu cầu cho những tên miền mà chúng không nhận ra. Nếu website mục tiêu của bạn vô tình là mặc định, bạn sẽ gặp may. Trong trường hợp đó, bạn có thể bắt đầu nghiên cứu xem ứng dụng làm gì với trường Host và liệu hành vi này có thể khai thác được hay không.

Ngược lại, vì trường Host là một phần nền tảng của cách website hoạt động, việc sửa đổi nó thường dẫn tới việc bạn không thể tiếp cận ứng dụng mục tiêu. Server front-end hoặc load balancer nhận yêu cầu của bạn có thể đơn giản là không biết phải chuyển tiếp tới đâu, dẫn tới một lỗi kiểu “Invalid Host header”. Điều này đặc biệt dễ xảy ra nếu mục tiêu của bạn được truy cập qua một CDN. Trong trường hợp đó, bạn nên chuyển sang thử một số kỹ thuật được nêu ở phần tiếp theo.

## Lỗi xác thực


Thay vì nhận được phản hồi “Invalid Host header”, bạn có thể thấy yêu cầu của mình bị chặn do một biện pháp bảo mật nào đó. Ví dụ, một số website sẽ kiểm tra xem tiêu đề Host có khớp với SNI trong quá trình bắt tay TLS hay không. Điều này không nhất thiết có nghĩa là chúng miễn nhiễm với các tấn công tiêu đề Host.

Bạn nên cố gắng hiểu cách website phân tích (parse) trường Host. Điều này đôi khi có thể tiết lộ các kẽ hở cho phép vượt qua việc xác thực. Ví dụ, một vài thuật toán phân tích sẽ loại bỏ phần cổng (port) khỏi trường Host, nghĩa là chỉ có tên miền được kiểm tra. Nếu bạn cũng có thể cung cấp một port không phải số, bạn có thể giữ nguyên tên miền để đảm bảo tiếp cận ứng dụng mục tiêu, đồng thời có khả năng chèn payload qua phần port.

```
GET /example HTTP/1.1
Host: vulnerable-website.com:bad-stuff-here
```

Một số site khác sẽ cố gắng áp dụng logic so khớp cho phép các subdomain tuỳ ý. Trong trường hợp này, bạn có thể vượt qua hoàn toàn việc xác thực bằng cách đăng ký một tên miền tùy ý kết thúc bằng cùng một chuỗi ký tự như tên miền được phép (whitelisted):

```
GET /example HTTP/1.1
Host: notvulnerable-website.com
```

Một lựa chọn khác là lợi dụng một subdomain kém bảo mật mà bạn đã kiểm soát:

```
GET /example HTTP/1.1
Host: hacked-subdomain.vulnerable-website.com
```

Để xem thêm ví dụ về các lỗi xác thực tên miền thường gặp, hãy tham khảo nội dung của chúng tôi về cách vượt qua các cơ chế phòng chống SSRF phổ biến và các lỗi phân tích (parsing) tiêu đề Origin.
## Gửi yêu cầu mơ hồ

Mã xác thực host và mã thực hiện hành vi dễ bị tổn thương thường nằm ở các thành phần ứng dụng khác nhau hoặc thậm chí trên các máy chủ riêng biệt. Bằng cách xác định và khai thác các khác biệt trong cách chúng lấy trường Host, bạn có thể phát sinh một yêu cầu mơ hồ — yêu cầu đó có thể trông như sử dụng host khác nhau tùy theo hệ thống nào đang xem nó.

Dưới đây là một vài ví dụ về cách bạn có thể tạo các yêu cầu mơ hồ.
### **Chèn nhiều tiêu đề Host trùng lặp**

Một cách tiếp cận là thử thêm nhiều tiêu đề Host trùng lặp. Thú thực, điều này thường chỉ dẫn tới yêu cầu bị chặn. Tuy nhiên, vì trình duyệt hiếm khi (hoặc hầu như không bao giờ) gửi kiểu yêu cầu này, đôi khi bạn sẽ gặp các nhà phát triển không lường trước kịch bản đó. Khi đó, bạn có thể làm lộ một số hành vi kỳ quặc thú vị.

Các hệ thống và công nghệ khác nhau sẽ xử lý trường hợp này khác nhau, nhưng thường một trong hai header sẽ được ưu tiên hơn header kia, dẫn tới việc ghi đè giá trị. Khi các hệ thống không đồng ý header nào là đúng, điều này có thể tạo ra sự khác biệt mà bạn có thể khai thác. Xem xét yêu cầu sau:

```
GET /example HTTP/1.1
Host: vulnerable-website.com
Host: bad-stuff-here
```

Giả sử front-end ưu tiên header xuất hiện trước, nhưng back-end ưu tiên header xuất hiện sau. Trong kịch bản đó, bạn có thể dùng header đầu tiên để đảm bảo yêu cầu được định tuyến tới mục tiêu mong muốn và dùng header thứ hai để truyền payload vào mã phía server.
### **Cung cấp URL tuyệt đối**

Mặc dù dòng yêu cầu thường chỉ định một đường dẫn tương đối trên miền được yêu cầu, nhiều máy chủ cũng được cấu hình để hiểu các yêu cầu có URL tuyệt đối.

Sự mơ hồ gây ra khi cung cấp cả URL tuyệt đối và tiêu đề Host cũng có thể tạo ra khác biệt giữa các hệ thống. Về lý thuyết, dòng yêu cầu nên được ưu tiên khi định tuyến, nhưng trong thực tế điều này không phải lúc nào cũng đúng. Bạn có thể khai thác các khác biệt này tương tự như với header Host trùng lặp.

```
GET <https://vulnerable-website.com/> HTTP/1.1
Host: bad-stuff-here
```

Lưu ý rằng bạn cũng có thể cần thử nghiệm với các giao thức khác nhau. Máy chủ đôi khi hành xử khác nhau tùy vào việc dòng yêu cầu chứa URL HTTP hay HTTPS.
### Line wrapping

Bạn cũng có thể phát hiện hành vi kỳ quặc bằng cách thụt lề các header HTTP với một ký tự cách. Một số máy chủ sẽ hiểu header bị thụt lề như là một dòng bọc (wrapped line) và do đó coi nó là một phần của giá trị header trước đó. Các máy chủ khác sẽ bỏ qua header bị thụt lề hoàn toàn.

Do cách xử lý rất không đồng nhất, thường sẽ có sự khác biệt giữa các hệ thống khác nhau khi xử lý yêu cầu của bạn. Ví dụ:

```
GET /example HTTP/1.1
    Host: bad-stuff-here
Host: vulnerable-website.com
```

Website có thể chặn các yêu cầu có nhiều tiêu đề Host, nhưng bạn có thể vượt qua validation đó bằng cách thụt lề một trong số chúng như trên. Nếu front-end bỏ qua header bị thụt lề, yêu cầu sẽ được xử lý như một yêu cầu bình thường tới `vulnerable-website.com`. Giả sử back-end lại bỏ qua khoảng trắng dẫn đầu và ưu tiên header xuất hiện trước khi có trùng lặp, sự khác biệt này có thể cho phép bạn truyền các giá trị tùy ý qua trường Host "bọc" đó.
### Các kỹ thuật khác

Đây chỉ là một mẫu nhỏ trong số nhiều cách có thể tạo các yêu cầu mơ hồ có hại. Ví dụ, bạn cũng có thể điều chỉnh nhiều kỹ thuật _HTTP request smuggling_ để cấu trúc các cuộc tấn công tiêu đề Host. Chúng tôi sẽ bàn chi tiết hơn vấn đề này trong chủ đề riêng về request smuggling.

## Chèn tiêu đề ghi đè Host

Ngay cả khi bạn không thể ghi đè trường Host bằng một yêu cầu mơ hồ, vẫn có những khả năng khác để ghi đè giá trị của nó trong khi giữ nguyên trường Host. Điều này bao gồm việc chèn payload của bạn thông qua một trong nhiều tiêu đề HTTP khác được thiết kế để phục vụ mục đích này, mặc dù thường là cho các trường hợp sử dụng vô hại hơn.

Như chúng ta đã thảo luận, các website thường được truy cập thông qua một hệ thống trung gian nào đó, chẳng hạn bộ cân bằng tải hoặc reverse proxy. Trong kiến trúc kiểu này, trường Host mà máy chủ back-end nhận được có thể chứa tên miền của một trong các hệ thống trung gian đó. Thông thường giá trị này không liên quan đến chức năng yêu cầu.

Để giải quyết vấn đề này, front-end có thể chèn tiêu đề `X-Forwarded-Host`, chứa giá trị Host ban đầu từ yêu cầu của client. Vì lý do này, khi tồn tại `X-Forwarded-Host`, nhiều framework sẽ tham chiếu tới trường này thay vì Host. Bạn có thể quan sát hành vi này ngay cả khi không có front-end thực sự sử dụng tiêu đề đó.

Bạn đôi khi có thể dùng `X-Forwarded-Host` để chèn đầu vào độc hại của mình trong khi né được bất kỳ cơ chế xác thực nào trên trường Host.

```
GET /example HTTP/1.1
Host: vulnerable-website.com
X-Forwarded-Host: bad-stuff-here
```

Mặc dù `X-Forwarded-Host` là tiêu chuẩn thực tế cho hành vi này, bạn có thể gặp các tiêu đề khác có mục đích tương tự, bao gồm:

- `X-Host`
- `X-Forwarded-Server`
- `X-HTTP-Host-Override`
- `Forwarded`

> **Mẹo**
> 
> Trong Burp Suite, bạn có thể dùng chức năng **"Guess headers"** của extension **Param Miner** để tự động dò các header được hỗ trợ bằng danh sách từ điển tích hợp phong phú của nó.

Về mặt an ninh, điều quan trọng cần lưu ý là một số website — có thể cả website của bạn — hỗ trợ kiểu hành vi này một cách không chủ ý. Thông thường điều này xảy ra vì một hoặc nhiều tiêu đề này được bật theo mặc định trong một số công nghệ bên thứ ba mà họ sử dụng.

# Xâm nhập

Một khi bạn đã xác định rằng bạn có thể truyền các tên host tùy ý tới ứng dụng mục tiêu, bạn có thể bắt đầu tìm cách để khai thác nó.

Trong phần này, chúng tôi sẽ cung cấp một số ví dụ về các tấn công tiêu đề Host HTTP thường gặp mà bạn có thể xây dựng. Chúng tôi cũng đã tạo một số website dễ bị tấn công có chủ ý để bạn có thể quan sát cách các khai thác này hoạt động và kiểm thử những gì bạn đã học.

Chúng tôi sẽ trình bày các ví dụ sau:

- Đầu độc quy trình đặt lại mật khẩu
- Đầu độc bộ nhớ đệm web
- Khai thác các lỗ hổng phía máy chủ cổ điển
- Vượt qua xác thực
- Dò host ảo bằng brute-force
- SSRF dựa trên định tuyến

## Đầu độc quy trình đặt lại mật khẩu

Đầu độc quy trình đặt lại mật khẩu là một kỹ thuật mà kẻ tấn công thao túng một website dễ bị tổn thương để buộc nó tạo một liên kết đặt lại mật khẩu trỏ tới một miền do kẻ tấn công kiểm soát. Hành vi này có thể bị lợi dụng để đánh cắp các token bí mật cần thiết cho việc đặt lại mật khẩu của người dùng bất kỳ và, cuối cùng, chiếm quyền truy cập vào tài khoản của họ.
### Nguyên lý hoạt động

Hầu như tất cả các website cần đăng nhập đều triển khai chức năng cho phép người dùng đặt lại mật khẩu khi quên. Có nhiều cách thực hiện việc này, với các mức độ an toàn và khả thi khác nhau. Một trong những phương pháp phổ biến nhất diễn ra như sau:

1. Người dùng nhập tên đăng nhập hoặc địa chỉ email và gửi yêu cầu đặt lại mật khẩu.
    
2. Website kiểm tra người dùng đó có tồn tại hay không rồi tạo một **mã thông báo** tạm thời, duy nhất, **có entropy cao**, và liên kết mã này với tài khoản người dùng trên back-end.
    
3. Website gửi email tới người dùng chứa một liên kết để đặt lại mật khẩu. Mã thông báo đặt lại duy nhất của người dùng được đưa vào như một **tham số truy vấn** của URL tương ứng:
    
    ```
    <https://normal-website.com/reset?token=0a1b2c3d4e5f6g7h8i9j>
    ```
    
4. Khi người dùng truy cập URL này, website kiểm tra mã thông báo được cung cấp có hợp lệ hay không và dùng nó để xác định tài khoản nào đang được đặt lại. Nếu mọi thứ như mong đợi, người dùng được phép nhập mật khẩu mới. Cuối cùng, mã thông báo bị hủy.
    

Quy trình này đủ đơn giản và tương đối an toàn so với một số cách khác. Tuy nhiên, tính an toàn của nó dựa trên nguyên tắc rằng chỉ có người dùng dự định mới truy cập được hộp thư email của họ, và do đó mới truy cập được mã thông báo duy nhất. **Password reset poisoning** là một phương pháp đánh cắp mã thông báo này để đổi mật khẩu của người dùng khác.
### Xây dựng cuộc tấn công

Nếu URL gửi tới người dùng được tạo động dựa trên đầu vào có thể kiểm soát được, chẳng hạn như trường Host, thì có thể dựng một cuộc tấn công đầu độc đặt lại mật khẩu như sau:

1. Kẻ tấn công có được địa chỉ email hoặc tên đăng nhập của nạn nhân (tùy yêu cầu) và gửi yêu cầu đặt lại mật khẩu thay cho nạn nhân. Khi gửi form, họ chặn yêu cầu HTTP tương ứng và sửa trường **Host** để trỏ tới một domain do họ kiểm soát. Ở ví dụ này, ta dùng `evil-user.net`.
    
2. Nạn nhân nhận được một email đặt lại mật khẩu thực từ website. Email này có vẻ chứa một liên kết bình thường để đặt lại mật khẩu và, quan trọng là, chứa một mã thông báo đặt lại mật khẩu hợp lệ liên kết với tài khoản của họ. Tuy nhiên, tên miền trong URL trỏ tới server của kẻ tấn công:
    
    ```
    <https://evil-user.net/reset?token=0a1b2c3d4e5f6g7h8i9j>
    ```
    
3. Nếu nạn nhân nhấp vào liên kết này (hoặc liên kết bị truy xuất theo cách khác, ví dụ bởi một trình quét antivirus), mã thông báo đặt lại mật khẩu sẽ được gửi tới server của kẻ tấn công.
    
4. Kẻ tấn công có thể truy cập URL thật của website dễ bị tổn thương và cung cấp mã thông báo bị đánh cắp qua tham số tương ứng. Họ sẽ có thể đặt lại mật khẩu của người dùng thành mật khẩu họ muốn và sau đó đăng nhập vào tài khoản đó.
    

Trong một cuộc tấn công thực tế, kẻ tấn công có thể tìm cách tăng xác suất nạn nhân nhấp vào liên kết bằng cách “làm ấm” nạn nhân trước với một thông báo vi phạm giả, ví dụ.

Ngay cả khi bạn không thể kiểm soát đường dẫn đặt lại mật khẩu, đôi khi bạn vẫn có thể dùng trường Host để chèn HTML vào các email nhạy cảm. Lưu ý rằng các client email thường không thực thi JavaScript, nhưng các kỹ thuật chèn HTML khác như **dangling markup** vẫn có thể áp dụng.

## Đầu độc Web cache qua Host Header

Khi dò tìm các khả năng tấn công qua tiêu đề Host, bạn thường gặp những hành vi có vẻ dễ tổn thương nhưng không thể khai thác trực tiếp. Ví dụ, bạn có thể phát hiện tiêu đề Host được phản chiếu trong markup phản hồi mà không được mã hóa HTML, hoặc thậm chí được dùng trực tiếp trong việc import script. Các lỗ hổng phản chiếu phía khách (client-side), như XSS, thường không thể khai thác khi nguyên nhân là do tiêu đề Host. Không có cách nào để kẻ tấn công ép trình duyệt của nạn nhân gửi một Host sai theo một cách có ích.

Tuy nhiên, nếu mục tiêu sử dụng bộ nhớ đệm web, bạn có thể biến lỗ hổng phản chiếu vô dụng này thành một lỗ hổng lưu trữ nguy hiểm bằng cách thuyết phục bộ nhớ đệm phục vụ một phản hồi đã bị nhiễm cho những người dùng khác.

Để dựng một cuộc tấn công đầu độc bộ nhớ đệm web, bạn cần gây ra một phản hồi từ server phản chiếu payload đã chèn. Thách thức là làm được điều này đồng thời vẫn bảo toàn một cache key mà những yêu cầu của người dùng khác cũng sẽ khớp. Nếu thành công, bước tiếp theo là khiến phản hồi độc hại này bị lưu vào bộ nhớ đệm. Sau đó, bất kỳ người dùng nào truy cập trang bị ảnh hưởng sẽ nhận được nội dung bị nhiễm.

Các bộ nhớ đệm độc lập (standalone) thông thường đưa tiêu đề Host vào cache key, vì vậy cách tấn công này thường hiệu quả hơn với các bộ nhớ đệm tích hợp ở tầng ứng dụng. Dẫu vậy, các kỹ thuật đã thảo luận trước đó đôi khi vẫn cho phép bạn đầu độc cả những bộ nhớ đệm độc lập.
## Khai thác các lỗ hổng phía máy chủ cổ điển

Mọi header HTTP đều là một vector tiềm năng để khai thác các lỗ hổng phía máy chủ cổ điển, và tiêu đề Host cũng không phải ngoại lệ. Ví dụ, bạn nên thử các kỹ thuật dò tìm SQL injection thông thường thông qua trường Host. Nếu giá trị của header được truyền vào một câu lệnh SQL, điều này có thể bị khai thác.
## Vượt qua xác thực

Vì những lý do khá rõ ràng, các website thường hạn chế truy cập một số chức năng chỉ dành cho **người dùng nội bộ**. Tuy nhiên, một số cơ chế **kiểm soát truy cập** của website lại đặt ra những giả định sai lầm, cho phép bạn **vượt qua** những hạn chế này chỉ bằng vài sửa đổi đơn giản trên tiêu đề **Host**. Việc này có thể làm lộ **bề mặt tấn công** lớn hơn, mở đường cho các khai thác khác.

## Dò host ảo bằng brute-force

Các công ty đôi khi mắc sai lầm khi lưu trữ cả những website truy cập công khai và các site nội bộ, riêng tư trên cùng một máy chủ. Máy chủ thường có cả địa chỉ IP công cộng và địa chỉ IP riêng. Vì hostname nội bộ có thể được phân giải về địa chỉ IP riêng, kịch bản này không phải lúc nào cũng phát hiện được chỉ bằng cách xem các bản ghi DNS:

```
www.example.com: 12.34.56.78
intranet.example.com: 10.0.0.132
```

Trong một số trường hợp, site nội bộ thậm chí có thể không có bản ghi DNS công khai liên quan. Tuy nhiên, kẻ tấn công thường có thể truy cập bất kỳ virtual host nào trên bất kỳ máy chủ nào mà họ có quyền truy cập, miễn là họ có thể đoán được tên host. Nếu họ đã phát hiện một tên miền ẩn bằng các phương tiện khác, chẳng hạn do rò rỉ thông tin, họ có thể đơn giản gửi yêu cầu trực tiếp tới nó. Ngược lại, họ có thể dùng các công cụ như Burp Intruder để brute-force các virtual host bằng một danh sách từ (wordlist) đơn giản gồm các subdomain ứng viên.

## SSRF dựa trên định tuyến

Đôi khi cũng có thể dùng tiêu đề Host để phát động các cuộc tấn công SSRF dựa trên định tuyến có tác động lớn. Những cuộc tấn công này đôi khi được gọi là “Host header SSRF attacks”, và đã được PortSwigger Research nghiên cứu sâu trong _Cracking the lens: targeting HTTP's hidden attack-surface_.

Các lỗ hổng SSRF cổ điển thường dựa trên XXE hoặc logic nghiệp vụ có thể khai thác, trong đó ứng dụng gửi các yêu cầu HTTP tới một URL được suy ra từ đầu vào có thể kiểm soát được bởi người dùng. Ngược lại, SSRF dựa trên định tuyến lợi dụng các thành phần trung gian phổ biến trong nhiều kiến trúc đám mây, bao gồm bộ cân bằng tải nội bộ và reverse proxy.

Mặc dù các thành phần này được triển khai với các mục đích khác nhau, về cơ bản chúng nhận các yêu cầu và chuyển tiếp chúng tới back-end thích hợp. Nếu chúng được cấu hình không an toàn để chuyển tiếp yêu cầu dựa trên một trường Host không được xác thực, chúng có thể bị thao túng để chuyển hướng yêu cầu tới bất kỳ hệ thống nào theo lựa chọn của kẻ tấn công.

Những hệ thống này là mục tiêu tuyệt vời. Chúng chiếm vị trí mạng có quyền hạn cho phép nhận yêu cầu trực tiếp từ web công cộng, đồng thời có thể truy cập nhiều — nếu không nói là toàn bộ — mạng nội bộ. Điều này biến tiêu đề Host thành một vector mạnh cho các cuộc tấn công SSRF, có khả năng biến một bộ cân bằng tải đơn giản thành cổng vào toàn bộ mạng nội bộ.

Bạn có thể dùng Burp Collaborator để giúp xác định những lỗ hổng này. Nếu bạn cung cấp domain của máy chủ Collaborator trong trường Host, và sau đó nhận được một lượt tra cứu DNS từ máy chủ mục tiêu hoặc một hệ thống nằm trên đường đi, điều này cho thấy bạn có thể điều hướng các yêu cầu tới các domain tùy ý.

Khi đã xác nhận rằng bạn có thể thao túng một thành phần trung gian để định tuyến yêu cầu tới một máy chủ công cộng tùy ý, bước tiếp theo là xem liệu bạn có thể lợi dụng hành vi này để truy cập các hệ thống chỉ dành cho mạng nội bộ hay không. Để làm điều đó, bạn cần xác định các địa chỉ IP riêng (private IP) đang được sử dụng trên mạng nội bộ của mục tiêu. Bên cạnh bất kỳ địa chỉ IP nào bị rò rỉ bởi ứng dụng, bạn cũng có thể quét các hostname thuộc về công ty để xem có hostname nào phân giải về địa chỉ IP riêng hay không. Nếu mọi cách khác đều thất bại, bạn vẫn có thể xác định các IP hợp lệ bằng cách brute-force các dải IP riêng tiêu chuẩn, chẳng hạn như `192.168.0.0/16`.

> **Ký hiệu CIDR**
> 
> Các dải địa chỉ IP thường được biểu diễn bằng ký hiệu CIDR, ví dụ `192.168.0.0/16`.
> 
> Địa chỉ IPv4 gồm bốn giá trị thập phân 8-bit gọi là “octet”, mỗi octet được ngăn cách bằng một dấu chấm. Giá trị của mỗi octet có thể nằm trong khoảng từ 0 đến 255, nghĩa là địa chỉ IPv4 thấp nhất là `0.0.0.0` và cao nhất là `255.255.255.255`.
> 
> Trong ký hiệu CIDR, địa chỉ IP thấp nhất của dải được viết rõ, theo sau là một số chỉ ra có bao nhiêu bit từ đầu địa chỉ được cố định cho toàn dải. Ví dụ, `10.0.0.0/8` chỉ ra rằng 8 bit đầu tiên được cố định (octet đầu tiên). Nói cách khác, dải này bao gồm mọi địa chỉ IP từ `10.0.0.0` đến `10.255.255.255`.


## Tấn công trạng thái kết nối


Vì lý do hiệu năng, nhiều website tái sử dụng kết nối cho nhiều vòng yêu cầu/phản hồi với cùng một client. Các HTTP server được triển khai kém đôi khi vận hành theo giả định nguy hiểm rằng một số thuộc tính, chẳng hạn như trường Host, là giống hệt cho tất cả các yêu cầu HTTP/1.1 được gửi qua cùng một kết nối. Điều này có thể đúng với các yêu cầu do trình duyệt gửi, nhưng không nhất thiết đúng với một chuỗi yêu cầu gửi từ Burp Repeater. Điều này có thể dẫn tới một số vấn đề tiềm ẩn.

Ví dụ, bạn đôi khi sẽ gặp những server chỉ thực hiện kiểm tra nghiêm ngặt trên yêu cầu đầu tiên mà chúng nhận được trên một kết nối mới. Trong trường hợp này, bạn có thể vượt qua kiểm tra đó bằng cách gửi một yêu cầu ban đầu trông vô hại rồi tiếp tục gửi yêu cầu độc hại xuống cùng một kết nối.

Nhiều reverse proxy sử dụng trường Host để định tuyến các yêu cầu tới back-end đúng. Nếu chúng giả định rằng tất cả các yêu cầu trên cùng một kết nối đều hướng tới cùng một host như yêu cầu ban đầu, điều này có thể cung cấp một vector hữu ích cho một số tấn công liên quan tới Host header, bao gồm SSRF dựa trên định tuyến, đầu độc quy trình đặt lại mật khẩu và đầu độc bộ nhớ đệm.
## SSRF thông qua dòng yêu cầu sai định dạng

Một số proxy tùy chỉnh đôi khi không kiểm tra (validate) dòng yêu cầu đúng cách, điều này có thể cho phép bạn cung cấp các đầu vào bất thường, sai định dạng và dẫn tới hậu quả không mong muốn.

Ví dụ, một reverse proxy có thể lấy phần path từ dòng yêu cầu, tiền tố nó bằng `http://backend-server`, và định tuyến yêu cầu tới URL upstream đó. Điều này hoạt động tốt nếu path bắt đầu bằng ký tự `/`, nhưng nếu nó bắt đầu bằng ký tự `@` thì sao?

```
GET @private-intranet/example HTTP/1.1
```

URL upstream kết quả sẽ là `http://backend-server@private-intranet/example`, mà đa số thư viện HTTP hiểu là một yêu cầu truy cập `private-intranet` với tên người dùng (username) là `backend-server`.
# Bảo mật

Để ngăn chặn các tấn công tiêu đề Host HTTP, cách đơn giản nhất là tránh sử dụng trường Host hoàn toàn trong mã phía server. Kiểm tra kỹ xem mỗi URL có thật sự cần là URL tuyệt đối hay không. Bạn thường sẽ thấy rằng có thể chỉ dùng URL tương đối. Thay đổi đơn giản này đặc biệt hữu ích để ngăn các lỗ hổng đầu độc bộ nhớ đệm web.

Các biện pháp khác để ngăn chặn tấn công tiêu đề Host HTTP bao gồm:
## **Bảo vệ URL tuyệt đối**

Khi buộc phải sử dụng URL tuyệt đối, hãy yêu cầu tên miền hiện tại được chỉ định thủ công trong file cấu hình và tham chiếu tới giá trị đó thay vì lấy từ trường Host. Cách làm này sẽ loại bỏ nguy cơ đầu độc liên kết đặt lại mật khẩu.

## **Xác thực trường Host**

Nếu bạn phải dùng trường Host, hãy đảm bảo xác thực nó đúng cách. Việc này nên bao gồm kiểm tra giá trị Host so với một danh sách domain được phép (whitelist/danh sách cho phép) và từ chối hoặc chuyển hướng bất kỳ yêu cầu nào tới các host không được nhận diện. Hãy tham khảo tài liệu của framework bạn đang dùng để biết cách làm cụ thể; ví dụ framework Django cung cấp tùy chọn `ALLOWED_HOSTS` trong file settings. Cách tiếp cận này sẽ giảm mức độ phơi nhiễm trước các cuộc tấn công chèn tiêu đề Host.
## **Không hỗ trợ các header ghi đè Host**

Cũng quan trọng là kiểm tra xem bạn có đang hỗ trợ các header bổ sung có thể được dùng để cấu thành các cuộc tấn công này hay không, đặc biệt là `X-Forwarded-Host`. Hãy nhớ rằng các header này có thể được bật theo mặc định.
## **Whitelist các domain được phép**

Để ngăn các tấn công dựa trên định tuyến vào hạ tầng nội bộ, hãy cấu hình bộ cân bằng tải hoặc bất kỳ reverse proxy nào để chỉ chuyển tiếp (forward) yêu cầu tới một danh sách domain được phép.
## **Cẩn trọng với các virtual host chỉ dùng nội bộ**

Khi sử dụng virtual hosting, tránh lưu trữ các website và ứng dụng chỉ dùng nội bộ trên cùng một máy chủ với nội dung hướng tới công chúng. Nếu không, kẻ tấn công có thể truy cập các domain nội bộ bằng cách thao túng trường Host.


# WU
- [x] Basic password reset poisoning
- [x] Web cache poisoning via ambiguous requests
- [x] Host header authentication bypass
- [x] Routing-based SSRF
- [x] SSRF via flawed request parsing
- [x] Host header authentication bypass (SMTP)
- [ ] Password reset poisoning via dangling markup

## Basic password reset poisoning

- mục tiêu của ta là tìm cách reset password cho carlos
- ấn thử forgot password cho wiener, ở email, link reset sẽ có 1 token để reset mật khẩu cho tài khoản
![](../../image/Pasted%20image%2020260507100007.png)
- ở burp repeater, khi mà thay Host header sang giá trị khác thì gói tin vẫn gửi thành công
- thay Host header thành link của url exploit của lab và đổi wiener thành carlos
![](../../image/Pasted%20image%2020260507100151.png)

- ở access log,  ta ghi nhân 1 log chứa token trả về
![](../../image/Pasted%20image%2020260507100229.png)
thay token này vào và reset password cho carlos

## Host header authentication bypass

- khi truy cập thử /admin thì bị từ chối vì ko có quyền
![](../../image/Pasted%20image%2020260507101935.png)

- gửi gói tin sang repeater, ở đây, thử thay Host thành localhost
![](../../image/Pasted%20image%2020260507102003.png)

=> server cho phép truy cập trang admin vì nhiều hệ thống quản trị (Admin Panel) được cấu hình để chỉ cho phép truy cập từ chính máy chủ đó (internal access) nhằm mục đích bảo mật. 

=> có thể xóa tài khoản carlos

## Web cache poisoning via ambiguous requests
- khi gửi request bằng repeater, ta thấy x-cache miss rồi hit
![](../../image/Pasted%20image%2020260515005600.png)

![](../../image/Pasted%20image%2020260515005656.png)

- khi thêm host thứ 2 vào request thì ở response backend cũng sử dụng host thứ 2 để tạo url script 
- vào trag exploit sửa lại path file và body sau đó ấn store
![](../../image/Pasted%20image%2020260515005825.png)
- mục tiêu là khi response HTML của trang lab load:

```
<script src="//EXPLOIT-SERVER/resources/js/tracking.js"></script>
```

thì browser sẽ lấy JavaScript từ exploit server và chạy `alert(document.cookie)`.

gửi lại request khi đã thay đổi host
![](../../image/Pasted%20image%2020260515005931.png)

- ấn vài lần để cache lưu và hiện hit
victim sẽ truy cập web và trigger sẽ xuất hiện


## Routing base SSRF

- khi thử sửa host header thành giá trị khác thì bị lỗi
![](../../image/Pasted%20image%2020260515010230.png)

request vẫn được gửi đến server lab thật, nhưng một thành phần trung gian/back-end lại dùng giá trị `Host` để **route request**. Nếu đặt `Host` thành một địa chỉ nội bộ như:

```
Host: 192.168.0.7
```

server có thể bị ép gửi request đến service nội bộ tương ứng. Đây là **routing-based SSRF**: bạn không nhập URL vào tham số như SSRF truyền thống, mà thao túng **Host header** để backend route request sang host khác. 

- vậy xóa host header cũ và insert burp collap payload, ở tab collaborator ấn poll now
![](../../image/Pasted%20image%2020260515010415.png)

- thấy interaction HTTP/DNS, nghĩa là middleware của website đã gửi request đến host bạn đặt trong `Host` header. Đây là bằng chứng có thể gây SSRF qua Host header.
- sau khi xác nhận SSRF, chuyển reqeust sang intruder, nhớ bỏ tích update host header
![](../../image/Pasted%20image%2020260515010529.png)
vì Nếu không tắt, Burp có thể tự sửa Host về domain lab thật và payload sẽ không chạy đúng.

- sửa host thành `192.168.0.$$` và chạy từ 0-255 để bruteforce
![](../../image/Pasted%20image%2020260515010851.png)

thấy giá trị 50 trả về 302

- truy cập được trang admin qua request
![](../../image/Pasted%20image%2020260515011011.png)
-
lấy giá trị csrf của admin

![](../../image/Pasted%20image%2020260515011256.png)

- sửa lại request thành POST và thêm crsf và username
![](../../image/Pasted%20image%2020260515011532.png)

## SSRF via flawed request parsing

- ở lab này, khi ta sửa host header và gửi thì bị chặn
![](../../image/Pasted%20image%2020260515011702.png)

=> có lớp validation host header
Muốn bypass, phải tạo một request “mơ hồ” bằng cách dùng **absolute URL trong request line** và **Host header khác**.

- sửa GET thành GET/your url lab: request dạng absolute-form.
![](../../image/Pasted%20image%2020260515011852.png)
- khi đó ta mới truy cập thành công 
- giờ đây khi sửa host header thành ip thì server mới thực thi vsaf gửi reqeust tới ip 
![](../../image/Pasted%20image%2020260515011936.png)
- bruteforce bằng intruder
![](../../image/Pasted%20image%2020260515012228.png)

- tương tự lab trước, sau khi login vào /admin, tìm thấy csrf trong repsonse
ta sửa reuqest thành GET .../admin/delete?csrf=xxx&username=carlos
chuột phảu để đổi mothod sang POST và gửi 

![](../../image/Pasted%20image%2020260515012425.png)

## Host validation bypass via connection state attack
- ở bài này, khi thử sửa GET sang /admin và host thành 192.168.0.1 thì bị mã 301, có thể bị redirect về home page
![](../../image/Pasted%20image%2020260515012625.png)

- tạo 1 group reqeust, 1 cái hợp lệ và cái còn lại như trên để thử gửi sang saerrver
- mục tiêu là request đầu tiên hợp lệ để mở connection
![](../../image/Pasted%20image%2020260515013013.png)
- gửi group voise single connection
- thấy request trả về 200 và truy cập được trang admin
- copy csrf của admin
- tương tự, sửa GET thành /admin/delete?csrf=xxx&username=carlos, sau đó change request method và gửi group như trên
![](../../image/Pasted%20image%2020260515013154.png)


