php
$transferAmount = $_POST['amount'];
$currentBalance = $user->getBalance();

if ($transferAmount <= $currentBalance) {
    // Thực hiện chuyển tiền
} else {
    // Chặn giao dịch: số dư không đủ
}
```

Nếu logic không ngăn chặn người dùng nhập giá trị âm, kẻ tấn công có thể lợi dụng để:
- Bỏ qua kiểm tra số dư.
- Thực hiện giao dịch ngược chiều.

Ví dụ, nếu kẻ tấn công gửi `-1000` vào tài khoản nạn nhân, hệ thống có thể hiểu rằng họ **nhận được 1000 USD từ nạn nhân**, vì điều kiện `-1000 <= currentBalance` luôn đúng → giao dịch được chấp nhận.

Những lỗi logic đơn giản như vậy có thể **gây hậu quả nghiêm trọng** nếu xảy ra trong chức năng quan trọng. Đặc biệt, chúng rất dễ bị bỏ sót trong quá trình phát triển và kiểm thử, do đầu vào bất thường thường đã bị **client-side validation** chặn ngay từ giao diện web.
**Khi kiểm thử ứng dụng**, bạn nên dùng các công cụ như **Burp Proxy** và **Burp Repeater** để thử gửi dữ liệu đầu vào bất thường:

- Các giá trị **quá lớn hoặc quá nhỏ** so với bình thường.
- Chuỗi văn bản **dài bất thường** trong các trường nhập liệu text.
- Thử nghiệm với **kiểu dữ liệu không mong đợi**.

Sau đó, quan sát phản hồi ứng dụng và tự đặt câu hỏi:

- Có giới hạn nào áp dụng cho dữ liệu không?
- Điều gì xảy ra khi đạt tới giới hạn?
- Có sự **biến đổi hoặc chuẩn hóa** nào đang áp dụng lên dữ liệu đầu vào không?

Những thử nghiệm này có thể giúp phát hiện ra các điểm yếu trong **xác thực dữ liệu**, từ đó cho phép bạn khai thác ứng dụng theo những cách **ngoài ý muốn của nhà phát triển**. Và hãy nhớ rằng: nếu một form trên website xử lý sai dữ liệu bất thường, khả năng cao **các form khác cũng mắc cùng lỗi**.

### Flawed assumptions about user behavior
Một trong những **nguyên nhân gốc rễ phổ biến nhất** của lỗ hổng logic là việc **đưa ra các giả định sai về hành vi người dùng**. Điều này có thể dẫn đến hàng loạt vấn đề khi lập trình viên **không lường trước các kịch bản nguy hiểm** có thể phá vỡ những giả định đó.

Trong phần này, chúng ta sẽ cùng xem qua một số **ví dụ cảnh báo** về các giả định thường gặp nhưng cần tránh, và minh họa cách chúng có thể dẫn đến những **lỗi logic nguy hiểm**.
### Trusted users won't always remain trustworthy
Một số ứng dụng có vẻ an toàn vì chúng triển khai các biện pháp tưởng chừng **rất chặt chẽ** để thực thi các quy tắc nghiệp vụ. Tuy nhiên, lỗi thường gặp là **giả định rằng khi người dùng đã vượt qua các cơ chế kiểm soát ban đầu thì họ (và dữ liệu của họ) sẽ mãi mãi đáng tin cậy**. Điều này dẫn đến việc từ thời điểm đó trở đi, các kiểm soát tương tự có thể bị **nới lỏng hoặc bỏ qua**.

Nếu các quy tắc nghiệp vụ và biện pháp bảo mật **không được áp dụng một cách nhất quán trên toàn ứng dụng**, thì sẽ hình thành những **lỗ hổng nguy hiểm** có thể bị kẻ tấn công lợi dụng.

### Users won't always supply mandatory input

Một ngộ nhận thường gặp là cho rằng người dùng **luôn luôn** nhập giá trị cho các trường bắt buộc. Trình duyệt có thể ngăn người dùng bình thường gửi form khi thiếu dữ liệu, nhưng như ta biết, **kẻ tấn công hoàn toàn có thể chỉnh sửa tham số trên đường truyền**. Thậm chí, họ còn có thể **xóa hẳn tham số**.

Điều này đặc biệt nguy hiểm trong trường hợp **nhiều chức năng cùng được triển khai trong một script phía server**. Khi đó, **sự có mặt hoặc vắng mặt của một tham số cụ thể** có thể quyết định đoạn mã nào sẽ được thực thi. Việc xóa tham số có thể giúp kẻ tấn công **truy cập vào các nhánh code vốn dĩ không được phép**.

Khi kiểm thử các lỗi logic, bạn nên thử **xóa từng tham số một** và quan sát phản hồi của ứng dụng. Cần lưu ý:

- Chỉ xóa **một tham số tại một thời điểm** để đảm bảo bạn tiếp cận được tất cả các nhánh code liên quan.
- Thử xóa cả **giá trị của tham số** lẫn **tên tham số**. Thông thường, server sẽ xử lý hai trường hợp này theo cách khác nhau.
- Theo dõi toàn bộ **quy trình nhiều bước (multi-stage workflow)** đến khi hoàn tất. Đôi khi việc thay đổi tham số ở bước đầu có thể ảnh hưởng đến hành vi ở những bước sau.
- Thao tác này áp dụng cho cả **tham số trong URL** lẫn **tham số trong POST body**, và đừng quên kiểm tra cả **cookie**.
Quy trình đơn giản này có thể làm lộ ra những hành vi bất thường của ứng dụng – và đôi khi những hành vi này hoàn toàn có thể khai thác.

### Users won't always follow the intended sequence
Nhiều giao dịch dựa trên **quy trình định sẵn** gồm một chuỗi các bước. Thông thường, giao diện web sẽ hướng dẫn người dùng thực hiện từng bước, rồi đưa họ sang bước kế tiếp khi hoàn thành bước hiện tại. Tuy nhiên, kẻ tấn công **không nhất thiết phải tuân theo đúng trình tự này**. Việc không tính đến khả năng đó có thể dẫn đến các lỗ hổng nguy hiểm và thậm chí **khá dễ khai thác**.

**Ví dụ:** Nhiều website triển khai **xác thực hai yếu tố (2FA)** yêu cầu người dùng:

1. Đăng nhập ở một trang.
2. Sau đó nhập mã xác thực ở một trang khác.

Nếu ứng dụng **giả định rằng người dùng luôn tuân theo quy trình đầy đủ** và do đó **không kiểm tra thực sự** xem họ có hoàn thành hay chưa, thì kẻ tấn công có thể **bỏ qua hoàn toàn bước 2FA**.

Việc giả định người dùng luôn tuân theo một trình tự sự kiện cố định có thể dẫn đến **nhiều vấn đề**, ngay cả trong **cùng một workflow hoặc chức năng**.

Với các công cụ như **Burp Proxy** và **Repeater**, khi kẻ tấn công đã thấy một request, họ có thể **gửi lại bất cứ lúc nào** và sử dụng **forced browsing** để tương tác với server **theo bất kỳ thứ tự nào**. Điều này cho phép họ thực hiện nhiều hành động trong khi ứng dụng đang ở một trạng thái **ngoài dự kiến**.
Cách phát hiện loại lỗ hổng này

Bạn có thể sử dụng **forced browsing** để gửi request theo một **trình tự ngoài ý muốn**, chẳng hạn:

- Bỏ qua một số bước.
- Truy cập một bước nhiều lần.
- Quay lại bước trước đó.
- Thử nhiều cách để truy cập cùng một bước.

Lưu ý rằng:

- Thông thường bạn chỉ cần gửi một **GET hoặc POST** đến URL cụ thể.
- Nhưng đôi khi cùng một URL có thể xử lý **nhiều bước khác nhau**, tùy thuộc vào **bộ tham số** bạn gửi.

Cũng như với mọi lỗi logic, bạn cần xác định:

- Các giả định mà nhà phát triển đã đưa ra là gì?
    
- Điểm bề mặt tấn công (attack surface) nằm ở đâu?
    
    → Từ đó tìm cách **phá vỡ các giả định** này.
Loại kiểm thử này thường gây ra **exception** vì biến mong đợi có thể bị `null` hoặc chưa khởi tạo. Khi ứng dụng rơi vào **trạng thái không nhất quán**, nó có thể phản hồi bằng lỗi hoặc phàn nàn.

Trong trường hợp này, bạn nên chú ý kỹ đến **thông báo lỗi** hoặc **thông tin debug** mà ứng dụng tiết lộ. Đây có thể là **nguồn thông tin quý giá**, giúp bạn:

- Tinh chỉnh tấn công.
- Hiểu rõ hành vi phía backend.

### Domain-specific flaws
Trong nhiều trường hợp, bạn sẽ gặp phải các lỗi logic gắn liền với **miền nghiệp vụ (business domain)** hoặc **mục đích hoạt động** của website.

Một ví dụ kinh điển là **chức năng giảm giá của cửa hàng trực tuyến** – đây là bề mặt tấn công quen thuộc khi săn lỗi logic. Nó có thể trở thành **“mỏ vàng” cho kẻ tấn công**, vì có vô số lỗi logic cơ bản trong cách áp dụng giảm giá.

**Ví dụ:**

Một cửa hàng online áp dụng giảm giá **10% cho đơn hàng trên 1000 USD**. Nếu logic nghiệp vụ **không kiểm tra lại đơn hàng sau khi áp dụng giảm giá**, kẻ tấn công có thể:

1. Thêm sản phẩm vào giỏ cho tới khi đạt ngưỡng 1000 USD.
2. Sau đó xóa các sản phẩm không muốn.
3. Cuối cùng đặt đơn hàng còn lại với mức giảm 10%, dù giá trị thực tế không đạt tiêu chí ban đầu.

Điểm cần chú ý

- Hãy tập trung vào các tình huống mà **giá trị nhạy cảm** (ví dụ: giá tiền, chiết khấu, hạn mức) thay đổi dựa trên **hành động do người dùng quyết định**.
- Cần hiểu rõ **thuật toán** mà ứng dụng sử dụng để điều chỉnh các giá trị này, cũng như **thời điểm** áp dụng điều chỉnh.
- Thông thường, bạn có thể thao túng ứng dụng để nó rơi vào **trạng thái không nhất quán**, nơi các điều chỉnh đã áp dụng **không còn khớp với điều kiện ban đầu mà lập trình viên mong muốn**.

Cách phát hiện các lỗ hổng đặc thù miền

- Suy nghĩ theo hướng: **mục tiêu của kẻ tấn công có thể là gì?**
- Tìm những cách **khác thường** để đạt được mục tiêu đó, sử dụng chính chức năng sẵn có.
- Điều này đôi khi đòi hỏi **kiến thức chuyên sâu về lĩnh vực**. Ví dụ: để hiểu lợi ích của việc buộc nhiều tài khoản follow bạn, bạn cần hiểu rõ cách hoạt động của **mạng xã hội**.

Nếu thiếu kiến thức miền, bạn có thể:

- Bỏ qua các hành vi nguy hiểm vì **không nhận ra hậu quả dây chuyền**.
- Không thấy được cách **kết hợp hai chức năng** có thể dẫn tới khai thác.

Lời khuyên

- Các ví dụ trong phần này thường lấy từ **cửa hàng trực tuyến** – một miền mà hầu hết mọi người đều quen thuộc.
- Nhưng khi **săn bug bounty, pentest, hoặc phát triển ứng dụng an toàn**, bạn có thể gặp phải ứng dụng trong các miền **ít quen thuộc hơn**.
- Trong trường hợp đó:
    - Hãy đọc kỹ **tài liệu**.
    - Trao đổi với **chuyên gia trong lĩnh vực** để lấy insight.
Nghe có vẻ mất thời gian, nhưng thực tế là: miền càng ít phổ biến thì khả năng cao nhiều tester khác đã bỏ sót rất nhiều lỗi – và đó chính là cơ hội của bạn.

### Providing an encryption oracle
Những tình huống nguy hiểm có thể xảy ra khi dữ liệu do người dùng kiểm soát được **mã hóa** và bản mã (ciphertext) sinh ra lại được **trả về cho người dùng** theo một cách nào đó. Kiểu đầu vào này đôi khi được gọi là một **“encryption oracle”**.

Kẻ tấn công có thể lợi dụng cơ chế này để **mã hóa dữ liệu tùy ý** bằng đúng thuật toán và khóa (key) mà ứng dụng đang sử dụng.

Điều này trở nên **nguy hiểm** khi trong ứng dụng tồn tại các đầu vào khác (cũng do người dùng kiểm soát) nhưng lại **yêu cầu dữ liệu đã được mã hóa bằng cùng thuật toán**. Khi đó, kẻ tấn công có thể dùng encryption oracle để tạo ra dữ liệu hợp lệ (đã được mã hóa đúng cách) rồi chèn vào các chức năng nhạy cảm khác.

Vấn đề càng nghiêm trọng hơn nếu trên ứng dụng tồn tại thêm một đầu vào khác cung cấp **chức năng ngược lại (giải mã – decryption oracle)**. Điều này sẽ cho phép kẻ tấn công giải mã dữ liệu, từ đó **hiểu rõ cấu trúc mong đợi**. Nhờ vậy, việc chế tạo payload độc hại trở nên dễ dàng hơn, dù thực tế là decryption oracle **không phải lúc nào cũng cần thiết** để tấn công thành công.

Mức độ nghiêm trọng của một **encryption oracle** phụ thuộc vào **chức năng nào khác trong ứng dụng** cũng sử dụng cùng thuật toán mà oracle này đang dùng.

### Email address parser discrepancies
Một số website thực hiện **phân tích địa chỉ email** để trích xuất domain và xác định người dùng thuộc tổ chức nào. Thoạt nhìn, quá trình này có vẻ đơn giản, nhưng trên thực tế nó lại **rất phức tạp**, ngay cả với các địa chỉ tuân thủ chuẩn RFC.

Các **sai lệch trong cách phân tích email** có thể phá vỡ logic nghiệp vụ. Sai lệch này xuất hiện khi **các phần khác nhau của ứng dụng xử lý email theo cách không nhất quán**.

Kẻ tấn công có thể khai thác điểm yếu này bằng các **kỹ thuật mã hóa (encoding techniques)** để che giấu một phần địa chỉ email. Nhờ vậy, họ có thể tạo ra các email trông như hợp lệ, vượt qua bước xác thực ban đầu, nhưng lại được **diễn giải khác đi** khi đến khâu xử lý logic phía server.

Tác động chính

- **Truy cập trái phép (unauthorized access):** Kẻ tấn công có thể đăng ký tài khoản bằng địa chỉ email trông như thuộc domain bị giới hạn.
- Nhờ đó, chúng có thể truy cập vào **khu vực nhạy cảm của ứng dụng**, chẳng hạn như **bảng điều khiển quản trị (admin panel)** hoặc các chức năng chỉ dành cho nhóm người dùng đặc quyền.

## Phòng tránh
Tóm lại, chìa khóa để ngăn ngừa lỗ hổng logic nghiệp vụ là:

- Đảm bảo **lập trình viên và tester hiểu rõ miền nghiệp vụ** mà ứng dụng phục vụ.
- Tránh đưa ra **giả định ngầm** về hành vi người dùng hoặc hành vi của các thành phần khác trong ứng dụng.
- Xác định rõ các **giả định về trạng thái phía server** và triển khai logic cần thiết để xác minh rằng các giả định này thực sự được đáp ứng. Điều này bao gồm việc kiểm tra giá trị của bất kỳ dữ liệu đầu vào nào có hợp lý trước khi xử lý tiếp hay không.

Ngoài ra, cần đảm bảo cả lập trình viên lẫn tester đều **hiểu rõ các giả định** này và cách ứng dụng **phải phản ứng trong từng kịch bản khác nhau**. Điều này giúp nhóm phát hiện lỗi logic càng sớm càng tốt. Để hỗ trợ, đội ngũ phát triển nên tuân thủ các **thực tiễn tốt nhất** sau đây:

- **Duy trì tài liệu thiết kế và luồng dữ liệu rõ ràng** cho tất cả giao dịch và workflow, ghi chú lại mọi giả định ở từng giai đoạn.
- **Viết code rõ ràng nhất có thể.** Nếu code khó hiểu, việc phát hiện lỗi logic cũng trở nên khó khăn. Lý tưởng nhất, code viết tốt sẽ không cần tài liệu mới hiểu được. Trong những trường hợp phức tạp không thể tránh, phải có **tài liệu chi tiết và dễ hiểu**, giúp lập trình viên và tester khác nắm rõ các giả định và hành vi mong đợi.
- Ghi chú mọi **tham chiếu tới code khác** có sử dụng mỗi thành phần. Cần suy nghĩ về các **tác động phụ** (side-effects) nếu kẻ tấn công thao túng các thành phần đó theo cách bất thường.
Do tính chất **tương đối đặc thù** của nhiều lỗi logic, rất dễ để xem chúng như một sai sót nhỏ mang tính cá nhân và bỏ qua. Tuy nhiên, như đã thấy, những lỗi này thường bắt nguồn từ **thói quen xấu ngay từ giai đoạn đầu xây dựng ứng dụng**.

Việc phân tích tại sao một lỗ hổng logic tồn tại ngay từ đầu, và tại sao đội ngũ lại bỏ sót nó, sẽ giúp bạn phát hiện ra **điểm yếu trong quy trình**. Bằng cách điều chỉnh nhỏ, bạn có thể tăng khả năng các lỗi tương tự sẽ được **ngăn chặn ngay từ đầu** hoặc **phát hiện sớm trong quá trình phát triển**.

# WU lab

<!-- TOC -->
## Mục lục

  - [Flawed assumptions about user behavior](#flawed-assumptions-about-user-behavior)
  - [Trusted users won't always remain trustworthy](#trusted-users-wont-always-remain-trustworthy)
  - [Users won't always supply mandatory input](#users-wont-always-supply-mandatory-input)
  - [Users won't always follow the intended sequence](#users-wont-always-follow-the-intended-sequence)
  - [Domain-specific flaws](#domain-specific-flaws)
  - [Providing an encryption oracle](#providing-an-encryption-oracle)
  - [Email address parser discrepancies](#email-address-parser-discrepancies)
- [Phòng tránh](#phòng-tránh)
- [Excessive trust in client-side controls](#excessive-trust-in-client-side-controls)
- [High-level logic vul](#high-level-logic-vul)
- [Inconsistent security controls](#inconsistent-security-controls)
- [Flawed enforcement of business rules](#flawed-enforcement-of-business-rules)
- [Low-level logic flaw](#low-level-logic-flaw)
- [Inconsistent handling of exceptional input](#inconsistent-handling-of-exceptional-input)
- [Weak isolation on dual-use endpoint](#weak-isolation-on-dual-use-endpoint)
- [Insufficient workflow validation](#insufficient-workflow-validation)
- [Authentication bypass via flawed state machine](#authentication-bypass-via-flawed-state-machine)
- [Infinite money logic flaw](#infinite-money-logic-flaw)
- [Authentication bypass via encryption oracle](#authentication-bypass-via-encryption-oracle)
- [Bypassing access controls using email address parsing discrepancies](#bypassing-access-controls-using-email-address-parsing-discrepancies)
<!-- /TOC -->
- [x] Excessive trust in client-side controls
- [x] High-level logic vulnerability
- [x] Inconsistent security controls
- [x] Flawed enforcement of business rules
- [x] Low-level logic flaw
- [x] Inconsistent handling of exceptional input
- [x] Weak isolation on dual-use endpoint
- [x] Insufficient workflow validation
- [x] Authentication bypass via flawed state machine
- [x] Infinite money logic flaw
- [x] Authentication bypass via encryption oracle
- [x] Information disclosure in error messages
- [x] Bypass access controls using email address parsing discrepancies

## Excessive trust in client-side controls

- ở repeater, thử sửa giá của 10 cái áo thành 1 đô
![](../../image/Pasted%20image%2020260501022637.png)

![](../../image/Pasted%20image%2020260501022554.png)
## High-level logic vul

- ở bài này, khi sửa số lương sang số thập phân thì bị lỗi, nhưng chuyển thành -1 thì server vẫn xử lí, tuy nhiên server ko cho thanh toán số âm
![](../../image/Pasted%20image%2020260501023805.png)

- có lẽ cần mua thêm đồ khác với số âm để giảm giá cái áo 1337 đô
![](../../image/Pasted%20image%2020260501024134.png)

## Inconsistent security controls

- thử dùng email exploit để đăng kí tài khoản
![](../../image/Pasted%20image%2020260501024934.png)
- đổi email sang đuôi @dontwannycry
![](../../image/Pasted%20image%2020260501024956.png)
- đã vào được admin panel và xóa tài khoản carlos
![](../../image/Pasted%20image%2020260501025242.png)

## Flawed enforcement of business rules

- bài lab này khi áp dụng coupon server đưa ra giảm được 5 đô
![](../../image/Pasted%20image%2020260501041939.png)

- ở cuối trang khi nhập 1 email bất kì được thêm 1 mã giảm giá khác
![](../../image/Pasted%20image%2020260501042329.png)

- khi ta nhập so le 2 mã code thì server liên tục giảm giá mà ko check, thiếu cơ chế kiểm tra các mã giảm giá 
![](../../image/Pasted%20image%2020260501042525.png)

## Low-level logic flaw
- ở bài lab này, server ko giới hạn số lượng áo mà user nhập vào
![](../../image/Pasted%20image%2020260501045433.png)
- cố gắng tìm cách để nhồi nhiều nhất số lượng áo vào để server gây ra lỗi tính toán, dùng intruder
![](../../image/Pasted%20image%2020260501045714.png)
ta tahays số tiền vượt quá định mức (có thể là int ) và thành số âm, giờ ta cần căn chỉnh ddeere số tiền về khoảng 100 đô
![](../../image/Pasted%20image%2020260501050258.png)
![](../../image/Pasted%20image%2020260501050832.png)
- thêm 1 số đồ khác để hoàn thành bài lab
![](../../image/Pasted%20image%2020260501050943.png)

## Inconsistent handling of exceptional input
- sử dụng email đc cấp để đăng ký 1 tài khoản
![](../../image/Pasted%20image%2020260501051130.png)

- khi đăng kí lại 1 email rất dài với đuôi @exploit-0a3800080344d56381f1b5f0017e0097.exploit-server.net, khi login vào tài khoản vừa tạo thấy email đã bị cắt chỉ còn 255 kí tự
![](../../image/Pasted%20image%2020260501052023.png)
=> phải chèn 239 kí tự trước @dontwannycry.com rồi đến phần đuôi email để đăng kí thành công
![](../../image/Pasted%20image%2020260501053138.png)

- sau khi đang kí thành công ta thấy email đã bị cắt đúng đến phần đuôi email
![](../../image/Pasted%20image%2020260501053126.png)

## Weak isolation on dual-use endpoint

- khi login bằng tài khoản wiener:peter, vào phần đổi password của tài khoản
- gửi request post sang repeater, sau khi xóa currrent-password đi và gửi lại gói tin thì vẫn nhận được thông báo là mật khẩu đổi thành công mà ko cần cung cấp mật khẩu hiện tại
![](../../image/Pasted%20image%2020260501143229.png)

- thử đổi tên user sang administrator và thử lại
![](../../image/Pasted%20image%2020260501143436.png)

- thành công login vào tài khoản administrator với mật khẩu 1
![](../../image/Pasted%20image%2020260501143449.png)

## Insufficient workflow validation

- ở bài này, khi ta thử thanh toán áo 1337$ thì server sẽ báo ko đủ tiên
- khi thử mua 1 món đồ khác trong khoảng 100$, ở trong burp, khi thanh toán, server sẽ reddirect sang 1 trang confirm
![](../../image/Pasted%20image%2020260501144105.png)

- thử cho lại áo vào giỏ hàng rồi gửi gói tin này sang burp repeater để confirm lại áo đã được thanh toán và refresh lại web
![](../../image/Pasted%20image%2020260501144231.png)

## Authentication bypass via flawed state machine
- ở bài lab này, khi login vào tài khoản wiener:peter, có 1 page để chọn role trức khi vào trang web của user
![](../../image/Pasted%20image%2020260501145048.png)
- thử bật intercept trong burrp login lại
- ngay sau khi login bằng wiener:peter, sẽ có gói tin get /role-selector hiện ra, drop gói tin này
- khi đó trang web sẽ báo gói tin bị drop bởi user, xóa /role-selector đi và enter để vào giao diện web, forward tất cả gói tin còn lại.
![](../../image/Pasted%20image%2020260501151218.png)

![](../../image/Pasted%20image%2020260501151137.png)

## Infinite money logic flaw

- ta thử thanh toán 1 cái giftcard 10$ trước, nhận được 1 mã code 

![](../../image/Pasted%20image%2020260501151552.png)
- ở dưới cùng của trang, nhập email và nhận được mã giảm giá
![](../../image/Pasted%20image%2020260501151816.png)

- thử thanh toán lại cái giftcard
![](../../image/Pasted%20image%2020260501151941.png)
- khi vào trang my-account để redeeem mã code, ta nhận lại được 10$
![](../../image/Pasted%20image%2020260501152042.png)

=> ta lãi được 3$, vậy có thể auto được quá trình mua giftcard này nhiều lần thì có thể mua được áo, ta lại sử dụng run a macro trong burp

![](../../image/Pasted%20image%2020260501152402.png)

- cấu hình request 4 để chọn mã code từ gift-card và cấu hình request 5 để nhập mã code từ request 4
- gửi request get-my-account sang intruder và chạy khoảng hơn 400 lần để có đủ tiền mua áo
![](../../image/Pasted%20image%2020260501162852.png)


## Authentication bypass via encryption oracle
- khi login bằng wiener:peter và chọn stay login, ở burp thấy cookie stay login đã bị mã hóa
![](../../image/Pasted%20image%2020260501160324.png)

- comment vào 1 bài post bất kì, sau đó thử lại với email ko hợp lệ, ta thấy có 1 thông báo nhảy ra
![](../../image/Pasted%20image%2020260501163109.png)
![](../../image/Pasted%20image%2020260501163124.png)

![](../../image/Pasted%20image%2020260501164502.png)
- khi ta gửi email ko hợp lệ, server sẽ mã hóa chuỗi này và trả về trong header notify
- copy cookie ở staylogin và dán vào chỗ notify:
![](../../image/Pasted%20image%2020260501171239.png)

- ở trong response thấy chuỗi được giải mã và trả về wiener:....


- thay wiener bằng administrator và gửi lại request để lấy notify
![](../../image/Pasted%20image%2020260501171606.png)

- gửi lại request với notify vừa lấy được
![](../../image/Pasted%20image%2020260501171757.png)

- vấn đề bây giờ là phải cắt được chuỗi đăng trước để bỏ đi cụm invalid ...., ta thêm thành aaaaaaaaa (9 chữ a) + administrator:timestramp để cho tròn 32 btyes đăng trước
- sau đó ở tab decoder, xóa đi 2 dòng đầu tiên sau khi decode url và decode base64
- rồi encode base64, encode url lại, ta thu được cookie hợp lệ
![](../../image/Pasted%20image%2020260501175843.png)

- test lại để kiểm tra: => thấy đã mất đi cụm invalid đăng trước
![](../../image/Pasted%20image%2020260501175921.png)
- trên broser hoặc burp sửa cookie thành chuỗi vừa thu được, sau đó load lại web, ta đã vào được trang admin
![](../../image/Pasted%20image%2020260501175659.png)

## Bypassing access controls using email address parsing discrepancies

- ở bài lab này:

- **Component A (Cấp quyền):** Kiểm tra xem email có kết thúc bằng `@dontwannacry.com` không để cấp quyền Admin.
- **Component B (Gửi Mail):** Thực hiện gửi link xác nhận về địa chỉ email để người dùng kích hoạt tài khoản.

Lỗ hổng nằm ở việc sử dụng **Ký tự chú thích (Comments)** hoặc **Ký tự điều khiển** mà Component A nghĩ là "tên miền", nhưng Component B lại coi là "phần thừa" và bỏ qua để gửi về email thật của bạn.

- khi đăng kí tài khoản, server chỉ cho phép đuôi của công ty mới có thể đăng kí 
![](../../image/Pasted%20image%2020260501180951.png)

- thử 1 số định dạng khác
	- **Thử ISO-8859-1:** `=?iso-8859-1?q?=61=62=63?=foo@ginandjuice.shop` -> Bị chặn (Security reasons).
	- **Thử UTF-8:** `=?utf-8?q?=61=62=63?=foo@ginandjuice.shop` -> Cũng bị chặn.
	- **Thử UTF-7:** `=?utf-7?q?&AGEAYgBj-?=foo@ginandjuice.shop`
- => ko thấy thông báo lỗi


- Bây giờ sẽ tạo một email mà:
	- **Hệ thống Validation:** Nhìn thấy nó kết thúc bằng `@ginandjuice.shop`.
	- **Hệ thống Gửi Mail:** Giải mã UTF-7 và thấy địa chỉ thật của bạn là `@exploit-server`.


ta có email là:  `attacker@exploit-0a4200110470d23181eb1a05019100e3.exploit-server.net`
**Cấu trúc Payload:** `=?utf-7?q?attacker&AEA-exploit-[ID-EXPLOIT-SERVER]&ACA-?=@ginandjuice.shop`


- `&AEA-` là mã hóa UTF-7 của ký tự `@`.
- `&ACA-` là mã hóa UTF-7 của ký tự khoảng trắng (Space).
- Khi giải mã, chuỗi này tương đương với: `attacker@[ID].exploit-server.net ?=@ginandjuice.shop`.
    
Hệ thống gửi mail sẽ chỉ quan tâm đến phần địa chỉ trước dấu cách và gửi link về Exploit Server 

![](../../image/Pasted%20image%2020260501182616.png)

