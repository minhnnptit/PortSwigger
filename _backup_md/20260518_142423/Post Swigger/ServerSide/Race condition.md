```table-of-contents
```

# Race condition
## Limit overrun
Dạng race condition nổi tiếng nhất cho phép bạn vượt qua một số giới hạn do logic nghiệp vụ của ứng dụng áp đặt.

Ví dụ, xét một cửa hàng trực tuyến cho phép bạn nhập mã khuyến mãi trong quá trình thanh toán để nhận giảm giá một lần cho đơn hàng. Để áp dụng khoản giảm giá này, ứng dụng có thể thực hiện các bước ở mức khái quát sau:

- Kiểm tra rằng bạn chưa sử dụng mã này trước đó.
- Áp dụng mức giảm vào tổng tiền đơn hàng.
- Cập nhật bản ghi trong cơ sở dữ liệu để phản ánh việc bạn đã sử dụng mã này.

Nếu sau đó bạn cố gắng sử dụng lại mã này, các kiểm tra ban đầu được thực hiện ở đầu quy trình sẽ ngăn bạn làm điều này:
![[Pasted image 20260502005026.png]]
Bây giờ hãy xem điều gì sẽ xảy ra nếu một người dùng chưa từng áp dụng mã giảm giá này trước đó cố gắng áp dụng nó hai lần gần như cùng một thời điểm:
![[Pasted image 20260502005050.png]]
Như bạn có thể thấy, ứng dụng chuyển qua một trạng thái con tạm thời; tức là một trạng thái mà nó đi vào rồi thoát ra trước khi việc xử lý yêu cầu hoàn tất. Trong trường hợp này, trạng thái con bắt đầu khi máy chủ bắt đầu xử lý yêu cầu đầu tiên và kết thúc khi nó cập nhật cơ sở dữ liệu để cho biết rằng bạn đã sử dụng mã này. Điều này tạo ra một cửa sổ race nhỏ trong đó bạn có thể lặp lại việc nhận giảm giá bao nhiêu lần tùy thích.

Có nhiều biến thể của kiểu tấn công này, bao gồm:

- Đổi (redeem) thẻ quà tặng nhiều lần
- Đánh giá một sản phẩm nhiều lần
- Rút hoặc chuyển tiền vượt quá số dư tài khoản
- Tái sử dụng một lời giải CAPTCHA
- Vượt qua giới hạn tốc độ (rate limit) chống brute-force

Các trường hợp vượt giới hạn (limit overrun) là một phân loại con của lỗi “time-of-check to time-of-use” (TOCTOU). Ở phần sau của chủ đề này, chúng ta sẽ xem xét một số ví dụ về lỗ hổng race condition không thuộc bất kỳ danh mục nào trong số này.
## Burp repeater
Quy trình phát hiện và khai thác race condition vượt giới hạn tương đối đơn giản. Ở mức khái quát, bạn chỉ cần:

- Xác định một endpoint dùng-một-lần (single-use) hoặc bị giới hạn tần suất (rate-limited) có tác động đến bảo mật hoặc mục đích hữu ích khác.
- Gửi nhiều yêu cầu tới endpoint này liên tiếp trong thời gian rất ngắn để xem bạn có thể vượt qua giới hạn đó hay không.

Thách thức chính là canh thời điểm gửi yêu cầu sao cho ít nhất hai “cửa sổ race” (race windows) trùng nhau, gây ra va chạm (collision). Cửa sổ này thường chỉ kéo dài vài mili-giây và thậm chí có thể ngắn hơn.

Ngay cả khi bạn gửi tất cả yêu cầu đúng cùng một thời điểm, trong thực tế vẫn có nhiều yếu tố bên ngoài không thể kiểm soát và khó dự đoán ảnh hưởng tới thời điểm máy chủ xử lý từng yêu cầu và thứ tự xử lý chúng.
![[Pasted image 20260502005137.png]]
Burp Suite 2023.9 bổ sung các khả năng mạnh mẽ mới cho Burp Repeater, cho phép bạn dễ dàng gửi một nhóm yêu cầu song song theo cách giảm đáng kể tác động của một trong các yếu tố gây nhiễu, cụ thể là **network jitter**. Burp sẽ tự động điều chỉnh kỹ thuật được sử dụng để phù hợp với phiên bản HTTP mà máy chủ hỗ trợ:

- Với **HTTP/1**, nó sử dụng kỹ thuật đồng bộ byte cuối (last-byte synchronization technique) kinh điển.
- Với **HTTP/2**, nó sử dụng kỹ thuật **single-packet attack**, lần đầu tiên được PortSwigger Research trình diễn tại Black Hat USA 2023.

Kỹ thuật _single-packet attack_ cho phép bạn vô hiệu hóa hoàn toàn sự can thiệp từ network jitter bằng cách dùng một gói tin TCP duy nhất để hoàn tất đồng thời 20–30 yêu cầu.![[Pasted image 20260502005149.png]]
Mặc dù đôi khi chỉ cần hai yêu cầu là đủ để kích hoạt khai thác, nhưng việc gửi một số lượng lớn yêu cầu theo cách này sẽ giúp giảm thiểu độ trễ nội bộ, hay còn gọi là **server-side jitter**. Điều này đặc biệt hữu ích trong giai đoạn khám phá ban đầu. Phương pháp luận này sẽ được trình bày chi tiết hơn ở phần sau.

> **Cách làm** Sau khi bắt Request và Send to Repeater thì sẽ click Custom actions ở hàng dọc bên phải Chọn New → From template → Trigger race condition → Sử dụng template này Có thể tùy chỉnh số lần gửi request nếu muốn, sau đó click run để bắt đầu attack

## Turbo Intruder
Turbo Intruder yêu cầu có một mức thành thạo nhất định với **Python**, nhưng lại phù hợp cho các cuộc tấn công phức tạp hơn, chẳng hạn như:

- Các tình huống cần thử lại nhiều lần (multiple retries)
- Canh thời gian gửi yêu cầu theo nhịp lệch (staggered request timing)
- Hoặc khi cần gửi một số lượng cực lớn yêu cầu.

Để sử dụng kỹ thuật _single-packet attack_ trong **Turbo Intruder**:

1. Đảm bảo rằng mục tiêu hỗ trợ **HTTP/2**. (_Single-packet attack_ không tương thích với HTTP/1).
2. Thiết lập các tùy chọn cấu hình `engine=Engine.BURP2` và `concurrentConnections=1` cho request engine.
3. Khi đưa yêu cầu vào hàng đợi (queueing requests), hãy **nhóm** chúng lại bằng cách gán chúng cho một **gate** có tên, sử dụng tham số `gate` trong phương thức `engine.queue()`.
4. Để gửi tất cả các yêu cầu trong một nhóm, mở **gate** tương ứng bằng phương thức `engine.openGate()`.

Ví dụ:
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                            concurrentConnections=1,
                            engine=Engine.BURP2
                            )

    # queue 20 requests trong gate '1'
    for i in range(20):
        engine.queue(target.req, gate='1')

    # gửi tất cả requests trong gate '1' song song
    engine.openGate('1')
```

Để biết thêm chi tiết, hãy tham khảo template **[race-single-packet-attack.py](http://race-single-packet-attack.py)** được cung cấp trong thư mục ví dụ mặc định của Turbo Intruder.

> **Cách làm** Bôi đen phần muốn bruteforce → Right Click → Extension → Turbo Intruder → Send to Turbo Intruder Chọn file python là `examples/race-single-packet-attack.py` sau đó chỉnh sửa thêm password vào bằng `password=wordlists.clipboard` nó sẽ tự đống lấy danh sách bằng phần copy Click attack (Khoảng chục cái 1 lần), xem request nào trả về 302 tức đăng nhập thành công

## Hidden multi-step sequences
Trong thực tế, một yêu cầu HTTP đơn lẻ có thể khởi tạo cả một **chuỗi nhiều bước** ở phía sau, khiến ứng dụng chuyển qua nhiều **trạng thái ẩn** (sub-states) mà nó đi vào rồi thoát ra trước khi việc xử lý yêu cầu hoàn tất.

Nếu bạn có thể xác định được một hoặc nhiều yêu cầu HTTP gây ra sự tương tác với cùng một dữ liệu, bạn có thể khai thác các trạng thái ẩn này để làm lộ ra những biến thể nhạy cảm về thời gian của các lỗi logic thường thấy trong **quy trình nhiều bước (multi-step workflows)**. Điều này mở ra khả năng khai thác race condition vượt xa các trường hợp **limit overrun**.

Ví dụ: bạn có thể đã quen với các luồng xác thực đa yếu tố (**MFA**) bị lỗi, cho phép bạn thực hiện phần đầu tiên của đăng nhập bằng thông tin xác thực đã biết, sau đó đi thẳng vào ứng dụng thông qua kỹ thuật **forced browsing**, về cơ bản là **bỏ qua MFA hoàn toàn**.

> **Lưu ý**
> 
> Nếu bạn chưa quen với kiểu khai thác này, hãy tham khảo lab **2FA simple bypass** trong chủ đề _Authentication vulnerabilities_.

Đoạn giả mã sau minh họa cách một website có thể dễ bị tấn công bởi biến thể race condition của kỹ thuật này:
```python
session['userid'] = user.userid
if user.mfa_enabled:
    session['enforce_mfa'] = True
    # generate and send MFA code to user
    # redirect browser to MFA code entry form
```

Như bạn thấy, đây thực chất là một **chuỗi nhiều bước** trong phạm vi của một **yêu cầu đơn lẻ**. Quan trọng nhất, nó chuyển qua một **trạng thái con (sub-state)** trong đó người dùng **tạm thời có một phiên đăng nhập hợp lệ**, nhưng **MFA chưa được thực thi**.

Kẻ tấn công có thể lợi dụng điều này bằng cách gửi song song một yêu cầu đăng nhập và một yêu cầu khác tới một endpoint nhạy cảm yêu cầu xác thực.

Ở các phần sau, chúng ta sẽ xem thêm nhiều ví dụ khác về **hidden multi-step sequences**, và bạn cũng sẽ có cơ hội thực hành khai thác chúng trong các **lab tương tác**. Tuy nhiên, vì những lỗ hổng này khá phụ thuộc vào từng ứng dụng cụ thể, nên trước hết việc quan trọng là phải hiểu rõ **phương pháp tổng quát** để có thể nhận diện chúng hiệu quả, cả trong môi trường lab lẫn ngoài thực tế.
## Phương pháp
Để phát hiện và khai thác các **chuỗi nhiều bước ẩn (hidden multi-step sequences)**, chúng tôi khuyến nghị áp dụng **phương pháp luận** sau, được tóm lược từ whitepaper _Smashing the state machine: The true potential of web race conditions_ của **PortSwigger Research**.

---

### Dự đoán va chạm

---

Việc kiểm thử mọi endpoint là điều không khả thi. Sau khi lập bản đồ (mapping) trang web mục tiêu như bình thường, bạn có thể **giảm số lượng endpoint cần kiểm thử** bằng cách tự đặt ra những câu hỏi sau:

- **Endpoint này có quan trọng về mặt bảo mật không?** Nhiều endpoint không chạm đến các chức năng quan trọng, do đó không đáng để kiểm thử.
- **Có khả năng xảy ra va chạm không?** Để xảy ra một va chạm thành công, bạn thường cần từ **hai yêu cầu trở lên** cùng kích hoạt các thao tác trên **cùng một bản ghi**.

![[Pasted image 20260502011004.png]]
Ví dụ, xét hai cách triển khai tính năng đặt lại mật khẩu (password reset):

- **Trường hợp 1**: Gửi song song yêu cầu đặt lại mật khẩu cho **hai người dùng khác nhau** → khó xảy ra va chạm vì thay đổi diễn ra trên **hai bản ghi riêng biệt**.
- **Trường hợp 2**: Cách triển khai cho phép bạn chỉnh sửa **cùng một bản ghi** bằng các yêu cầu cho hai người dùng khác nhau → có khả năng xảy ra va chạm.

---

### Thăm dò manh mối

---

Để nhận ra các manh mối, trước hết bạn cần **đo chuẩn (benchmark)** cách endpoint hoạt động trong điều kiện bình thường. Bạn có thể làm điều này trong **Burp Repeater** bằng cách **gom tất cả yêu cầu** và dùng tùy chọn **Send group in sequence (separate connections)**. Để biết thêm thông tin, xem _Sending requests in sequence_.

Tiếp theo, gửi **cùng nhóm yêu cầu đó đồng thời** bằng cách dùng **single-packet attack** (hoặc **last-byte sync** nếu máy chủ không hỗ trợ HTTP/2) để **giảm thiểu network jitter**. Bạn có thể làm điều này trong **Burp Repeater** bằng cách chọn **Send group in parallel**. Để biết thêm thông tin, xem _Sending requests in parallel_. Ngoài ra, bạn có thể dùng tiện ích mở rộng **Turbo Intruder**, có sẵn trên **BApp Store**.

**Bất cứ điều gì** cũng có thể là manh mối. Hãy tìm **bất kỳ sai lệch** nào so với những gì bạn quan sát được trong bước đo chuẩn. Điều này bao gồm **thay đổi ở một hoặc nhiều phản hồi**, nhưng đừng quên các **hiệu ứng bậc hai** như nội dung email khác đi hoặc **sự thay đổi có thể quan sát** trong hành vi của ứng dụng sau đó.

> **Lưu ý (Professional)**
> 
> Để kiểm thử lỗ hổng race condition một cách **nhanh và dễ dàng**, bạn có thể dùng **Trigger race conditions** (custom action). Tính năng này gửi các yêu cầu song song chỉ với **một lần nhấp**, loại bỏ nhu cầu tạo và nhóm tab thủ công trong Repeater.

---

### Chứng minh khái niệm

---

Hãy cố gắng **hiểu điều gì đang xảy ra**, loại bỏ các yêu cầu thừa, và đảm bảo rằng bạn vẫn có thể **tái tạo được hiệu ứng**.

Các race condition nâng cao có thể tạo ra những **primitive bất thường và độc đáo**, vì vậy con đường để đạt đến mức độ tác động tối đa không phải lúc nào cũng rõ ràng ngay lập tức. Sẽ hữu ích nếu bạn coi **mỗi race condition như một điểm yếu trong cấu trúc tổng thể** thay vì một lỗ hổng riêng lẻ.

> **PortSwigger Research**
> 
> Để có phương pháp chi tiết hơn, hãy tham khảo whitepaper: _Smashing the state machine: The true potential of web race conditions_.

## Multi-endpoint
Dạng trực quan nhất của race condition loại này là khi chúng liên quan đến việc gửi **yêu cầu tới nhiều endpoint cùng lúc**.

Hãy nghĩ đến lỗi logic kinh điển trong các cửa hàng trực tuyến: bạn thêm một món hàng vào giỏ, thanh toán, sau đó lại thêm nhiều món khác vào giỏ trước khi **forced browsing** tới trang xác nhận đơn hàng.

> **Lưu ý**
> 
> Nếu bạn chưa quen với kiểu khai thác này, hãy tham khảo lab **Insufficient workflow validation** trong chủ đề _Business logic vulnerabilities_.

Một biến thể của lỗ hổng này có thể xảy ra khi **xác thực thanh toán** và **xác nhận đơn hàng** được thực hiện trong quá trình xử lý **một yêu cầu duy nhất**.

Máy trạng thái (state machine) cho trạng thái đơn hàng có thể trông như sau:
![[Pasted image 20260502011031.png]]
Vấn đề phổ biến này chủ yếu do hai yếu tố sau:

- **Độ trễ do kiến trúc mạng** – Ví dụ, có thể phát sinh độ trễ mỗi khi máy chủ front-end thiết lập kết nối mới tới back-end. **Giao thức** được sử dụng cũng có thể tạo ra ảnh hưởng lớn.
- **Độ trễ do xử lý đặc thù của từng endpoint** – Các endpoint khác nhau vốn dĩ có **thời gian xử lý khác nhau**, đôi khi chênh lệch đáng kể, tùy thuộc vào các thao tác mà chúng kích hoạt.

May mắn thay, có những **cách khắc phục tiềm năng** cho cả hai vấn đề này.

Độ trễ kết nối với back-end thường **không cản trở** các cuộc tấn công race condition vì chúng thường làm chậm **đều nhau** tất cả các yêu cầu song song, nhờ đó các yêu cầu vẫn được giữ đồng bộ.

Điều quan trọng là bạn phải **phân biệt được** loại độ trễ này với độ trễ do các yếu tố đặc thù của từng endpoint. Một cách để làm điều này là thực hiện **“làm ấm” kết nối** (warming) bằng một hoặc nhiều yêu cầu không quan trọng để xem liệu chúng có giúp làm trơn tru thời gian xử lý của các yêu cầu sau hay không.

Trong **Burp Repeater**, bạn có thể thử:

- Thêm một yêu cầu **GET tới trang chủ** vào đầu nhóm tab.
- Sau đó dùng tùy chọn **Send group in sequence (single connection)**.
- Nếu yêu cầu đầu tiên vẫn có thời gian xử lý dài hơn, nhưng các yêu cầu tiếp theo được xử lý trong một khoảng thời gian ngắn → bạn có thể **bỏ qua độ trễ ban đầu** này và tiếp tục kiểm thử như bình thường.
- Nếu bạn vẫn thấy thời gian phản hồi không nhất quán trên **một endpoint duy nhất**, ngay cả khi dùng kỹ thuật **single-packet**, điều đó cho thấy độ trễ từ back-end đang can thiệp vào cuộc tấn công.
Trong trường hợp này, bạn có thể thử khắc phục bằng cách sử dụng Turbo Intruder để gửi một số yêu cầu warming trước, rồi mới gửi các yêu cầu tấn công chính.
Nếu việc **làm ấm kết nối (connection warming)** không tạo ra khác biệt, có nhiều cách khác để giải quyết vấn đề này.

- Với **Turbo Intruder**, bạn có thể thêm một **độ trễ ngắn phía client**. Tuy nhiên, vì cách này chia nhỏ các yêu cầu tấn công thực tế ra nhiều gói TCP, bạn sẽ **không thể sử dụng kỹ thuật single-packet attack**. Do đó, trên các mục tiêu có mức jitter cao, cuộc tấn công sẽ khó hoạt động ổn định, bất kể bạn đặt độ trễ như thế nào.
![[Pasted image 20260502011103.png]]
Thay vì vậy, bạn có thể giải quyết bằng cách lợi dụng một cơ chế bảo mật phổ biến.

Các web server thường trì hoãn xử lý request nếu nhận quá nhiều trong thời gian ngắn. Bằng cách gửi một lượng lớn **yêu cầu giả (dummy requests)** để **cố tình kích hoạt giới hạn tốc độ hoặc tài nguyên**, bạn có thể khiến server tạo ra một độ trễ phù hợp phía back-end.

Điều này giúp cho kỹ thuật **single-packet attack** trở nên khả thi ngay cả khi cần **thực thi trễ**.
![[Pasted image 20260502011123.png]]
## Single-endpoint
Việc gửi **các yêu cầu song song với giá trị khác nhau** tới **cùng một endpoint** đôi khi có thể kích hoạt những race condition nguy hiểm.

Ví dụ, xét một cơ chế **đặt lại mật khẩu (password reset)** lưu trữ **user ID** và **reset token** trong session của người dùng.

Trong tình huống này, nếu bạn gửi **hai yêu cầu đặt lại mật khẩu song song** từ cùng một session nhưng với **hai username khác nhau**, có thể dẫn đến va chạm (collision) như sau:

![[Pasted image 20260502011155.png]]
Khi tất cả thao tác đã hoàn tất, trạng thái cuối cùng có thể là:

```python
session['reset-user'] = victim
session['reset-token'] = 1234
```

👉 Điều này cho phép kẻ tấn công lợi dụng việc lưu trữ **không đồng bộ** trong session để gán token đặt lại mật khẩu của nạn nhân.

Phiên làm việc (**session**) lúc này chứa **user ID của nạn nhân**, nhưng **reset token hợp lệ** lại được gửi cho kẻ tấn công.

> **Lưu ý**
> 
> Để cuộc tấn công này hoạt động, các thao tác khác nhau do từng tiến trình thực hiện phải xảy ra theo **đúng thứ tự**. Điều này thường đòi hỏi nhiều lần thử, hoặc một chút may mắn, mới đạt được kết quả mong muốn.

Các cơ chế **xác nhận email**, hoặc bất kỳ thao tác nào dựa trên email, nhìn chung là mục tiêu tốt cho **single-endpoint race conditions**. Lý do là vì email thường được gửi trong **luồng xử lý nền (background thread)** sau khi máy chủ đã trả về HTTP response cho client, khiến khả năng xảy ra race condition **cao hơn**.
## Session-based locking mechanisms
Một số framework cố gắng ngăn chặn việc hỏng dữ liệu ngoài ý muốn bằng cách sử dụng **cơ chế khóa yêu cầu (request locking)**. Ví dụ: **PHP's native session handler module** chỉ xử lý **một request trên mỗi session** tại một thời điểm.

Việc nhận biết loại hành vi này là **cực kỳ quan trọng**, vì nếu không, nó có thể che giấu những lỗ hổng vốn dĩ rất dễ khai thác.

👉 Nếu bạn nhận thấy rằng tất cả các yêu cầu của mình đều được xử lý **tuần tự**, hãy thử gửi mỗi yêu cầu với **một session token khác nhau**.

## Partial construction
Nhiều ứng dụng tạo đối tượng theo **nhiều bước**, điều này có thể tạo ra một trạng thái trung gian tạm thời trong đó đối tượng có thể bị khai thác.

Ví dụ: Khi đăng ký người dùng mới, ứng dụng có thể:

1. Tạo user trong cơ sở dữ liệu.
2. Thiết lập API key cho user bằng một câu lệnh SQL riêng biệt.

Điều này tạo ra một **cửa sổ nhỏ** mà trong đó **user đã tồn tại nhưng API key chưa được khởi tạo**.

Kiểu hành vi này mở đường cho các khai thác, nơi bạn chèn một giá trị đầu vào sao cho khi trả về trùng với giá trị chưa khởi tạo trong DB (ví dụ: chuỗi rỗng `""`, hoặc `null` trong JSON), và giá trị này được đem đi so sánh như một phần của **cơ chế kiểm soát bảo mật**.
Nhiều framework cho phép bạn truyền vào **mảng hoặc cấu trúc dữ liệu phi chuỗi** bằng cú pháp không chuẩn. Ví dụ trong **PHP**:

- `param[]=foo` tương đương với `param = ['foo']`
- `param[]=foo&param[]=bar` tương đương với `param = ['foo', 'bar']`
- `param[]` tương đương với `param = []`

**Ruby on Rails** cũng cho phép thực hiện điều tương tự bằng cách gửi một query hoặc POST parameter với **key nhưng không có value**. Nói cách khác:

```ruby
param[key]
```

sẽ tạo ra đối tượng phía server như sau:

```ruby
params = {"param"=>{"key"=>nil}}
```

---

Trong ví dụ trên, điều này có nghĩa là trong **race window**, bạn có thể thực hiện các request API đã được xác thực như sau:
```
GET /api/user/info?user=victim&api-key[]= HTTP/2
Host: vulnerable-website.com
```

> **Lưu ý**
> 
> Cũng có thể gây ra va chạm trong quá trình khởi tạo một phần (partial construction collision) bằng **mật khẩu** thay vì API key. Tuy nhiên, do mật khẩu thường được băm (hashed), bạn sẽ cần chèn một giá trị sao cho **giá trị băm trùng khớp** với giá trị chưa khởi tạo.

## Time-sensitive
Đôi khi bạn có thể không tìm thấy **race condition**, nhưng các kỹ thuật gửi request với **thời gian chính xác** vẫn có thể giúp phát hiện sự tồn tại của các lỗ hổng khác.

Một ví dụ điển hình là khi ứng dụng sử dụng **timestamp có độ phân giải cao** thay vì các chuỗi ngẫu nhiên an toàn về mặt mật mã để sinh token bảo mật.

Ví dụ: xét một **password reset token** chỉ được tạo ngẫu nhiên dựa trên **timestamp**. Trong trường hợp này, có thể:

- Kích hoạt **hai yêu cầu đặt lại mật khẩu** cho **hai người dùng khác nhau**.
- Cả hai yêu cầu đều sử dụng **cùng một token**, nếu chúng được tạo ra trong cùng một thời điểm.

👉 Tất cả những gì bạn cần làm là **căn chuẩn thời gian request** sao cho chúng sinh ra **cùng timestamp**.

## Phòng tránh
Khi một yêu cầu đơn lẻ có thể khiến ứng dụng chuyển qua các trạng thái con (sub-state) “vô hình”, việc hiểu và dự đoán hành vi của nó là cực kỳ khó. Điều này khiến việc phòng thủ trở nên không khả thi. Để bảo vệ ứng dụng đúng cách, chúng tôi khuyến nghị **loại bỏ các sub-state khỏi mọi endpoint nhạy cảm** bằng cách áp dụng các chiến lược sau:

- **Tránh trộn lẫn dữ liệu từ các lớp/kho lưu trữ khác nhau.**
- **Đảm bảo các endpoint nhạy cảm thực hiện thay đổi trạng thái theo cách nguyên tử (atomic)** bằng cách sử dụng tính năng đồng thời (concurrency) của kho dữ liệu. Ví dụ: dùng **một giao dịch (transaction) duy nhất** của cơ sở dữ liệu để vừa kiểm tra thanh toán có khớp giá trị giỏ hàng vừa xác nhận đơn hàng.
- **Phòng thủ nhiều lớp (defense-in-depth):** tận dụng các tính năng toàn vẹn và nhất quán của kho dữ liệu như **ràng buộc duy nhất (uniqueness constraints)** trên cột.
- **Đừng cố dùng một lớp lưu trữ dữ liệu để bảo vệ lớp khác.** Ví dụ: **session** không phù hợp để ngăn các cuộc tấn công **limit overrun** nhắm vào cơ sở dữ liệu.
- **Đảm bảo framework xử lý phiên (session) giữ được tính nhất quán nội bộ.** Cập nhật biến session **từng biến** thay vì **theo lô/batch** có thể trông như tối ưu hóa, nhưng **rất nguy hiểm**. Điều này cũng áp dụng với **ORM**: khi ẩn đi các khái niệm như transaction, ORM phải **chịu hoàn toàn trách nhiệm** về chúng.
- **Trong một số kiến trúc, có thể phù hợp khi loại bỏ hoàn toàn state phía server.** Thay vào đó, có thể **mã hóa để đẩy state sang phía client**, ví dụ dùng **JWT**. Lưu ý cách làm này **có rủi ro riêng**, như đã được trình bày chi tiết trong chủ đề **tấn công JWT**.

# WU
- [ ] Limit overrun race conditions
- [ ] Multi-endpoint race conditions
- [ ] Bypassing rate limits via race conditions
- [ ] Race condition vulnerabilities in session handling
- [ ] Partial construction race conditions
- [ ] Exploiting time-sensitive vulnerabilities

## Limit overrun race conditions
- lỗ hổng bài lab xảy ra khi hệ thống kiểm tra điều kiện và hành động ko phải thao tác nguyên tử nên nếu ta gửi nhiều request 1 lúc thì hệ thống có thể chưa cập nhật trnag thái của mã giảm giá
![[Pasted image 20260502013845.png]]

- gửi gói tin POST /cart/coupon sang cho turbo intruder để gửi request
![[Pasted image 20260502013944.png]]
- ta phải chạy 1 vài lần vì hệ thống có thể xử lí khác biệt cho đến khi cái áo giảm còn dưới 50$

![[Pasted image 20260502014019.png]]
- remove để chạy lại, có thể configure để tăng số request gửi cùng lúc
![[Pasted image 20260502014518.png]]


## Multi-endpoint race conditions
- mua 1 giftcard trước, ở burp gửi gói tin sang burp repeater
![[Pasted image 20260502022341.png]]
- group request POST /cart/checkout và POST /cart vào 1 group và send parallel (đổi productid sang 1 là của cái áo và thử gửi 1 số lần)
![[Pasted image 20260502031422.png]]
## Bypassing rate limits via race conditions
- ơ bài lab này cần bruteforce để login vào tài khoản carlos, sau đó tìm cách vào panel của admin để xóa tài khoản carlos
- login thử vào carlos, sau đo gửi gói tin burpr đến repeater để xem response
khi thử sai vài lần, hệ thống thông báo
![[Pasted image 20260502015114.png]]

- gửi gói tin sang turbo intruder, sử dụng mẫu single attack, sửa password thành %s
- copy danh sách password được cấp ở bài lab vào script
![[Pasted image 20260502020714.png]]

![[Pasted image 20260502021839.png]]
- đa tìm ra mật khẩu của carlos


## Single-endpoint race conditions

- login vào tài khoản của wiener:peter và đổi email
- gửi gói tin sang repeater, đổi email sang email của carlos, và thêm 1 gói tin tương tự để gửi email confirmed tới hòm thư để confiremd (nhớ đổi @ sang %40)
![[Pasted image 20260502023929.png]]
![[Pasted image 20260502024023.png]]


- thử send parallel vài lần cho đến khi confirmed email và reload lại trang chủ ta có được email của carlos thành công
![[Pasted image 20260502023825.png]]
- nó sẽ mất 1 vài lần vì 2 gói tin gửi song song nên khả năng là 50 50
![[Pasted image 20260502024050.png]]
## Exploiting time-sensitive vulnerabilities

![[Pasted image 20260502024957.png]]

- copy phpsesssion vừa sinh ra từ request GET (làm 2 lần) sang 2 gói tin post
![[Pasted image 20260502025133.png]]
![[Pasted image 20260502025118.png]]

- nhóm 2 gói tin thành group rồi send parallel
- sau khi thành công trả về 200, vào xác nhận email
![[Pasted image 20260502025716.png]]
- ở url nếu user là wiener thì đổi sang carlos
![[Pasted image 20260502030115.png]]

## Partial construction race conditions
- ở burp, thấy ở file users.js này sẽ tự đông gene ra 1 cái form ở trang confirm link vơi email đăng kí, sửa request theo mẫu đó, đổi thành post và /confirm?token

![[Pasted image 20260502032113.png]]

- gửi thử request và nhận thấy token có thể xử lí cả mảng

![[Pasted image 20260502032513.png]]
![[Pasted image 20260502032540.png]]

- bây giờ gửi request register sang turbo intruder
![[Pasted image 20260502032736.png]]
- mẫu đã được lab gợi ý, copy phần POST vào biến confirmationReq
![[Pasted image 20260502033052.png]]

- ![[Pasted image 20260502033235.png]]
- thấy response phản hồi là victim4 đã đang wkis thành công
![[Pasted image 20260502033315.png]]
