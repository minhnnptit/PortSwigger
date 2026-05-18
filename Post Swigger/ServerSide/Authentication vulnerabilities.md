```table-of-contents
```

# Authentication vulnerabilities
#### Authentication là gì?
Xác thực là quá trình xác minh danh tính của người dùng, khách hàng.  Các websites có tiềm năng bị xâm nhập bởi bất kì ai kết nối tới internet. Điều này khiến cho các cơ chế xác thực mạnh mẽ trở thành 1 phần thiết yếu trong bảo mật web

Có 3 loại xác thực chính:
- **something you know** - thứ bạn biết: như là mật khẩu, câu trả lời cho câu hỏi bảo mật. Loại này gọi là **yếu tố tri thức - knowledge factors**
- **something you have - thứ bạn sở hữu**: một vật thể vật lí như là điện thoại hoặc token bảo mật. Loại này gọi là yếu tố sở hữu - **possesions factors**.
- **something you are or do - thứ bạn là hoặc làm**: ví dụ, sinh trắc học, các mẫu hành vi. Loại này gọi là **yếu tố vốn có**

#### khác biệt giữa xác thực và phân quyền : authentication vs authorization
- **authentication** là quá trình xác minh 1 người dùng đúng là người họ khai báo
- **authorization** tham gia vào việc xác minh 1 người dùng có quyền hoặc được phép làm gì đó hay ko
ví dụ: xác thực xác định xem ai đó cố gắng truy cập với username là **carlos123** có thực sự đúng là người đó tạo tài khoản hay ko. một khi xác minh xong, quyền của họ xác định những thứ mà họ có quyền làm. ví dụ, họ có quyền truy cập thông tin cá nhận của người dùng khác, hoặc có thể xóa tài khoản người dùng khác.

#### nguyên nhân phát sinh lỗ hổng xác thực
hầu hết lỗ hổng trong cơ chế xác thực xảy ra dưới 2 con đường:
- cơ chế xác thực yếu vì họ thất bại trong các cuộc tấn công bruteforce
- lỗi logic hoặc lập trình kém trong quá trình triển khai cho phép cơ chế xác thực bị vượt qua hầu hết bởi các hacker. Đây là những lỗi gọi chung là: **broken authentication**
trong rất nhiều khía cạnh phát triển web, các lỗi logic là nguyên nhân dẫn tới website hành xử lạ ngoài mong đợi, đôi khi ko phải là vấn đề bảo mật. tuy nhiên, vì xác thực có vài trò tối quan trọng trong bảo mật, nên các lỗi logic bảo mật xác thực gần như chắc chắn sẽ khiến các website dễ bị khai thác

#### tác động của lỗ hổng xác thực
hậu quả của lỗ hổng này có thể rất nghiêm trọng. 
- nếu 1 kẻ tấn công có thể vượt qua xác thực hoặc bruteforce theo cách của họ vào được tài khoản của người dùng khác, họ có thể truy cập dữ liệu và chức năng mà tài khoản bị chiếm đoạt sở hữu. 
- Nếu họ có thể xâm phạm 1 tài khoản có đặc quyền cao, chẳng hạn như quản trị viên hệ thống, họ có thể kiểm soát hoàn toàn phần còn lại của ứng dụng và có khả năng truy cập vào cơ sở hạ tầng nội bộ.
- Ngay cả khi chiếm quyền 1 tài khoản có quyền thấp, vẫn có khả năng kẻ tấn công truy cập đc vào dữ liệu họ ko đc phép, như là thông tin kinh doanh nhạy cảm.
- kể cả khi 1 tài khoản ko có quyền nào truy cập dữ liệu nhạy cảm, vẫn có khả năng kẻ tấn công truy cập được những trang khác, có thể cung cấp attacker surface mới.
- trong nhiều TH, các cuộc tấn công có mức độ nghiêm trọng ko khả thi trong việc truy cập từ các trang public, nhưng họ có thể tấn công từ các trang nội bộ.
### lỗ hổng trong trong cơ chế xác thực
1 hệ thống xác thực của website thường bao gồm một số cơ chế riêng biệt có thể xảy ra các lỗ hổng.
#### lỗ hổng trong password-base login
đối với các trang web sử dụng cơ chế login bằng password, người dùng đăng kí 1 tài khoản hoặc quản trị viên cung cấp. trong bối cảnh này, việc người dùng biết mật khẩu đc coi là đủ để chứng minh danh tính của họ. điều này nghĩa là bảo mật của website sẽ bị ảnh hướng nếu kẻ tấn công có thể lấy cắp hoặc đoán thông tin đăng nhập của user khác. Bằng một số cách như:
- **bruteforce attack**: kẻ tấn công sử dụng phuong pháp thử và sai để đoán thông tin của user. kiểu tấn công này thường đc tự động hóa với wordlists username và password bằng các tool chuyên dụng. nếu có 1 số thông tin của mục tiêu, có thể tinh chỉnh wordlist
- **username enumeration**: xảy ra khi kẻ tấn công có thể quan sát sự thay đổi trong hành vi website để xác định xem 1 username nào đó có hợp lệ hay ko. khi bruteforce cần chú ý 1 số điểm như:
	- **status code**: Trong quá trình brute-force, hầu hết các thử sai sẽ trả về cùng một HTTP status code. Nếu một lần thử trả về mã trạng thái khác, đây là dấu hiệu mạnh cho thấy username đó đúng. Best practice là website nên luôn trả về cùng một status code bất kể kết quả, nhưng thực tế điều này không phải lúc nào cũng được tuân thủ.
	- **thông báo lỗi**: Đôi khi thông báo lỗi khác nhau tùy thuộc vào việc cả username và password đều sai, hay chỉ password sai. Best practice là website nên hiển thị thông báo giống nhau, dạng chung chung cho cả hai trường hợp, nhưng lỗi gõ (typo) nhỏ có thể xuất hiện. Chỉ cần một ký tự khác biệt, dù không hiển thị rõ trên trang, cũng khiến hai thông báo trở nên khác nhau.
	- **response time**: Nếu hầu hết các request có thời gian xử lý tương tự, bất kỳ request nào lệch đáng kể đều gợi ý rằng có điều gì khác đang diễn ra phía backend. Đây là một dấu hiệu khác cho thấy username được đoán có thể đúng. Ví dụ: một website có thể chỉ kiểm tra password nếu username hợp lệ. Bước kiểm tra thêm này có thể khiến thời gian phản hồi tăng lên một chút. Mặc dù khác biệt này thường rất nhỏ, nhưng kẻ tấn công có thể làm rõ độ trễ bằng cách nhập một mật khẩu quá dài khiến website mất nhiều thời gian xử lý hơn.
	2 cách phổ biến ngăn bruteforce là:
	- **khóa tài khoản**: nếu truy cập sai quá nhiều
	- **chặn ip**: nếu quá nhiều request trong thời gian ngắn
- **IP locking**: 
Ví dụ:

- Trong một số hệ thống, IP của bạn có thể bị chặn nếu đăng nhập sai quá nhiều lần.
- Tuy nhiên, bộ đếm số lần đăng nhập sai có thể **được reset nếu IP đó đăng nhập thành công**.

Điều này đồng nghĩa với việc kẻ tấn công chỉ cần **thỉnh thoảng đăng nhập vào tài khoản của chính chúng** trong quá trình brute-force để tránh chạm đến giới hạn.

Trong trường hợp này, chỉ cần **chèn thông tin đăng nhập hợp lệ của bản thân vào wordlist theo chu kỳ**, kẻ tấn công đã có thể **vô hiệu hóa gần như hoàn toàn biện pháp phòng thủ này**.
- **Account locking**: 
Một cách mà website thường sử dụng để ngăn chặn brute-force là **khóa tài khoản** nếu phát hiện các tiêu chí nghi ngờ, thường là khi có một số lần đăng nhập sai vượt quá giới hạn cho phép.

Tuy nhiên, cũng giống như lỗi đăng nhập thông thường, các phản hồi từ server báo rằng một tài khoản đã bị khóa có thể giúp kẻ tấn công **liệt kê (enumerate) username hợp lệ**.

Việc khóa tài khoản mang lại một mức độ bảo vệ nhất định đối với các cuộc brute-force **nhắm mục tiêu vào một tài khoản cụ thể**. Nhưng phương pháp này lại **không hiệu quả** trong việc ngăn chặn các cuộc brute-force mà kẻ tấn công chỉ đơn giản là muốn chiếm quyền truy cập vào **bất kỳ tài khoản nào**.

Ví dụ, kẻ tấn công có thể sử dụng phương pháp sau để **vượt qua biện pháp bảo vệ này**:

1. **Xây dựng danh sách username tiềm năng** có khả năng hợp lệ. Điều này có thể thực hiện bằng cách **username enumeration** hoặc đơn giản là dựa vào danh sách các username phổ biến.
2. **Chọn một danh sách mật khẩu rút gọn** (rất ít) mà bạn cho rằng ít nhất một người dùng sẽ sử dụng. Quan trọng là **số lượng mật khẩu chọn không được vượt quá số lần thử đăng nhập tối đa cho phép**. Ví dụ: nếu giới hạn là **3 lần thử**, bạn chỉ được chọn tối đa **3 mật khẩu**.
3. Sử dụng công cụ như **Burp Intruder**, thử lần lượt từng mật khẩu đã chọn với từng username trong danh sách.

Bằng cách này, bạn có thể **brute-force trên toàn bộ danh sách tài khoản** mà **không kích hoạt khóa tài khoản**. Bạn chỉ cần **một người dùng** sử dụng một trong ba mật khẩu đã chọn là đã có thể **chiếm đoạt được tài khoản**.

Khóa tài khoản cũng **không thể bảo vệ** trước các cuộc tấn công **credential stuffing**.

- **Credential stuffing** là hình thức sử dụng một **dictionary khổng lồ chứa các cặp username:password thật**, vốn bị đánh cắp trong các vụ rò rỉ dữ liệu.
- Kiểu tấn công này dựa vào thực tế rằng nhiều người có thói quen **tái sử dụng cùng một username và mật khẩu trên nhiều website khác nhau**. Do đó, luôn có khả năng một số thông tin đăng nhập trong dictionary sẽ hợp lệ trên website mục tiêu.

Cơ chế khóa tài khoản không ngăn chặn được credential stuffing, vì mỗi username trong dictionary chỉ bị thử **một lần duy nhất**.

Credential stuffing đặc biệt nguy hiểm vì đôi khi nó có thể giúp kẻ tấn công **chiếm đoạt nhiều tài khoản khác nhau chỉ bằng một cuộc tấn công tự động duy nhất**.- 

### HTTP Basic Authentication

---

Mặc dù khá cũ, nhưng do có **tính đơn giản** và **dễ triển khai**, nên đôi khi bạn vẫn có thể bắt gặp cơ chế **HTTP Basic Authentication** được sử dụng.

Trong HTTP Basic Authentication:

- Client nhận một **authentication token** từ server.
- Token này được tạo bằng cách **nối (concatenate) username và password**, sau đó **mã hóa bằng Base64**.
- Token được trình duyệt lưu trữ và quản lý, rồi **tự động thêm vào header `Authorization` của mọi request tiếp theo**, theo định dạng sau:

```
Authorization: Basic base64(username:password)
```

Vì nhiều lý do, **HTTP Basic Authentication thường không được coi là phương thức xác thực an toàn**:

1. **Gửi lặp lại thông tin đăng nhập:** Cơ chế này liên tục gửi **thông tin đăng nhập (username và password)** trong mỗi request. Nếu website không triển khai **HSTS**, thông tin này có thể bị đánh cắp qua tấn công **Man-in-the-Middle (MitM)**.
2. **Không hỗ trợ chống brute-force:** Nhiều triển khai của HTTP Basic Authentication **không có cơ chế bảo vệ brute-force**. Do token chỉ bao gồm **giá trị tĩnh** (username:password mã hóa Base64), nó có thể dễ dàng trở thành mục tiêu brute-force.
3. **Dễ bị tấn công liên quan đến session:** HTTP Basic Authentication **đặc biệt dễ bị khai thác** bởi các tấn công liên quan đến session, điển hình là **CSRF**, và bản thân nó **không có cơ chế bảo vệ** chống lại kiểu tấn công này.

Trong một số trường hợp, việc khai thác lỗ hổng trong HTTP Basic Authentication có thể chỉ giúp kẻ tấn công truy cập một trang có vẻ **không quan trọng**. Tuy nhiên:

- Trang này vẫn có thể mở rộng **bề mặt tấn công**.
- Quan trọng hơn, **thông tin đăng nhập bị lộ** có thể được **tái sử dụng** trong các ngữ cảnh khác, nhạy cảm hơn nhiều.

---
## **Multi-factor authentication**
---
Trong phần này, chúng ta sẽ tìm hiểu một số lỗ hổng có thể xuất hiện trong các cơ chế **xác thực đa yếu tố (Multi-Factor Authentication – MFA).**

Nhiều website chỉ dựa vào **xác thực một yếu tố (single-factor authentication)** bằng mật khẩu để xác minh người dùng. Tuy nhiên, một số website yêu cầu người dùng phải chứng minh danh tính của mình bằng **nhiều yếu tố xác thực**.

Việc xác minh yếu tố **sinh trắc học (biometric)** là **khó khả thi** đối với hầu hết website. Tuy nhiên, hiện nay ngày càng phổ biến cả **bắt buộc** lẫn **tùy chọn** hình thức **xác thực hai yếu tố (2FA)** dựa trên:

- **Something you know (thứ bạn biết):** ví dụ mật khẩu.
- **Something you have (thứ bạn sở hữu):** ví dụ mã xác minh tạm thời từ thiết bị vật lý ngoài băng (out-of-band device).

Trong đó, người dùng thường phải nhập cả **mật khẩu truyền thống** và **mã xác minh tạm thời** từ thiết bị họ sở hữu.

Mặc dù kẻ tấn công đôi khi có thể lấy được một yếu tố dựa trên tri thức (chẳng hạn mật khẩu), nhưng khả năng đồng thời lấy được **yếu tố từ nguồn ngoài băng** là **khó hơn rất nhiều**. Vì vậy, 2FA **chứng minh được là an toàn hơn nhiều** so với xác thực một yếu tố.

Tuy nhiên, cũng giống như bất kỳ biện pháp bảo mật nào, 2FA chỉ **an toàn đúng bằng mức độ triển khai của nó**. Nếu được triển khai kém, 2FA hoàn toàn có thể bị **đánh bại** hoặc thậm chí **bị bypass hoàn toàn**, giống như xác thực một yếu tố.

Một điểm đáng chú ý khác là: **lợi ích thực sự của xác thực đa yếu tố chỉ đạt được khi xác minh nhiều loại yếu tố khác nhau**. Nếu chỉ xác minh **cùng một yếu tố theo hai cách**, thì đó **không phải là 2FA thực sự**.

Ví dụ: **2FA dựa trên email**. Người dùng cần cung cấp cả mật khẩu và mã xác minh gửi qua email. Tuy nhiên, việc truy cập mã này chỉ phụ thuộc vào việc người dùng biết **thông tin đăng nhập email** của mình. Nghĩa là yếu tố tri thức (knowledge factor) đã bị **xác minh hai lần**, chứ không phải hai yếu tố riêng biệt.

---

### **Two-factor authentication tokens**

---

Mã xác minh thường được người dùng đọc từ **một thiết bị vật lý** nào đó. Nhiều website có yêu cầu bảo mật cao hiện nay cung cấp cho người dùng **thiết bị chuyên dụng** cho mục đích này, ví dụ như **RSA token** hoặc **thiết bị bàn phím (keypad device)** dùng để truy cập vào dịch vụ ngân hàng trực tuyến hoặc máy tính công việc.

Ngoài việc được thiết kế chuyên biệt cho bảo mật, các thiết bị này còn có ưu điểm là **tự tạo mã xác minh trực tiếp**. Bên cạnh đó, nhiều website cũng sử dụng **ứng dụng di động chuyên dụng**, như **Google Authenticator**, vì lý do tương tự.

Ngược lại, một số website gửi mã xác minh đến **điện thoại di động của người dùng qua SMS**. Về mặt kỹ thuật, đây vẫn là xác minh yếu tố **“something you have” (thứ bạn sở hữu)**, nhưng lại dễ bị lạm dụng:

1. **Mã được truyền qua SMS** thay vì được sinh ra trực tiếp trên thiết bị, tạo khả năng bị **chặn và đánh cắp trong quá trình truyền**.
2. Nguy cơ **SIM swapping**: kẻ tấn công có thể gian lận để chiếm đoạt một SIM card có cùng số điện thoại với nạn nhân. Khi đó, chúng sẽ nhận được toàn bộ tin nhắn SMS gửi cho nạn nhân, bao gồm cả mã xác minh.

Trong một số trường hợp, việc triển khai **xác thực hai yếu tố (2FA)** có thể bị lỗi đến mức cho phép **bỏ qua hoàn toàn**.

Ví dụ: nếu người dùng được yêu cầu nhập **mật khẩu trước**, sau đó được yêu cầu nhập **mã xác minh trên một trang riêng biệt**, thì thực chất người dùng đã ở trong trạng thái **“đã đăng nhập”** trước khi nhập mã xác minh.

Trong tình huống này, bạn nên thử kiểm tra xem có thể **truy cập trực tiếp các trang chỉ dành cho người đã đăng nhập** sau khi hoàn thành bước xác thực đầu tiên hay không. Thỉnh thoảng, bạn sẽ phát hiện website **không hề kiểm tra** việc người dùng có thực hiện bước thứ hai hay không trước khi tải trang.

---

### Flawed two-factor verification logic

---

Đôi khi, do **lỗi logic trong cơ chế xác thực hai yếu tố (2FA)**, sau khi người dùng hoàn thành bước đăng nhập đầu tiên, website lại **không xác minh đầy đủ** rằng cùng một người dùng đang thực hiện bước thứ hai.

Ví dụ:

- Người dùng đăng nhập bằng thông tin bình thường ở bước đầu tiên:

```
POST /login-steps/first HTTP/1.1
Host: vulnerable-website.com
...
username=carlos&password=qwerty
```

- Sau đó, server gán cho họ một cookie liên quan đến tài khoản:

```
HTTP/1.1 200 OK
Set-Cookie: account=carlos
```

- Người dùng được chuyển sang bước thứ hai:

```
GET /login-steps/second HTTP/1.1
Cookie: account=carlos
```

- Khi gửi mã xác minh, request sẽ sử dụng cookie này để xác định tài khoản mà người dùng muốn truy cập:

```
POST /login-steps/second HTTP/1.1
Host: vulnerable-website.com
Cookie: account=carlos
...
verification-code=123456
```

👉 Trong trường hợp này, kẻ tấn công có thể:

- Đăng nhập bằng **thông tin của chính mình**.
- Sau đó **thay đổi giá trị cookie `account`** thành bất kỳ username nào khi gửi mã xác minh:

```
POST /login-steps/second HTTP/1.1
Host: vulnerable-website.com
Cookie: account=victim-user
...
verification-code=123456
```

Điều này **cực kỳ nguy hiểm** nếu kẻ tấn công có thể brute-force mã xác minh, vì nó cho phép chúng **đăng nhập vào tài khoản của bất kỳ người dùng nào chỉ dựa trên username**, mà **không bao giờ cần biết mật khẩu của họ**.

---

### **Brute-forcing 2FA verification codes**

---

Cũng giống như mật khẩu, các website cần triển khai biện pháp để **ngăn chặn brute-force mã xác minh 2FA**. Điều này đặc biệt quan trọng vì mã 2FA thường chỉ là một số **4 hoặc 6 chữ số**. Nếu không có cơ chế bảo vệ brute-force thích hợp, việc crack mã này trở nên **quá đơn giản**.

Một số website cố gắng ngăn brute-force bằng cách **tự động đăng xuất người dùng** nếu họ nhập sai quá nhiều mã xác minh. Tuy nhiên, biện pháp này **không hiệu quả trên thực tế**, bởi vì một kẻ tấn công tinh vi có thể **tự động hóa toàn bộ quy trình nhiều bước** này bằng cách sử dụng **macro cho Burp Intruder**. Ngoài ra, extension **Turbo Intruder** cũng có thể được dùng cho mục đích này.

---

## **Other authentication mechanisms**

---

Ngoài chức năng đăng nhập cơ bản, hầu hết các website còn cung cấp các chức năng bổ sung để người dùng **quản lý tài khoản** của mình. Ví dụ, người dùng thường có thể:

- **Thay đổi mật khẩu.**
- **Đặt lại mật khẩu khi quên**.

Tuy nhiên, chính những cơ chế này cũng có thể tạo ra **lỗ hổng** mà kẻ tấn công có thể khai thác.

Thông thường, các website sẽ cẩn trọng trong việc tránh những lỗ hổng đã biết trên trang đăng nhập. Nhưng lại dễ **bỏ qua việc áp dụng các biện pháp bảo mật tương tự** cho những chức năng liên quan. Điều này đặc biệt nguy hiểm trong trường hợp kẻ tấn công có thể **tự tạo tài khoản** và từ đó dễ dàng tiếp cận, nghiên cứu các trang bổ sung này.

---

### Keeping users logged in

---

Một tính năng phổ biến là tùy chọn cho phép người dùng **duy trì trạng thái đăng nhập ngay cả sau khi đóng trình duyệt**. Thường được hiển thị dưới dạng một checkbox với nhãn như **“Remember me”** hoặc **“Keep me logged in”**.

Chức năng này thường được triển khai bằng cách tạo ra một loại **token “remember me”**, sau đó lưu trong **persistent cookie**. Vì việc sở hữu cookie này đồng nghĩa với việc **bỏ qua toàn bộ quá trình đăng nhập**, nên best practice là cookie này phải **không thể đoán được**.

Tuy nhiên, một số website lại tạo cookie dựa trên **chuỗi nối (concatenation) có thể đoán trước** của các giá trị tĩnh, chẳng hạn như:

- **Username + timestamp**, hoặc thậm chí
- **Sử dụng password** như một phần của cookie.

Cách triển khai này **đặc biệt nguy hiểm** nếu kẻ tấn công có thể **tự tạo tài khoản**:

- Họ sẽ phân tích cookie của chính mình để tìm ra cách nó được sinh ra.
- Sau đó, khi đã xác định được công thức, họ có thể **brute-force cookie của người dùng khác** để chiếm quyền truy cập vào tài khoản.

Một số website cho rằng nếu cookie được **mã hóa theo một cách nào đó**, thì nó sẽ không thể đoán được, ngay cả khi sử dụng các giá trị tĩnh. Điều này chỉ đúng khi việc mã hóa được thực hiện đúng cách.

- Nếu chỉ “mã hóa” cookie bằng các phương pháp **mã hóa hai chiều đơn giản** như **Base64**, thì hoàn toàn **không có giá trị bảo mật**.
- Ngay cả khi sử dụng **hàm băm một chiều (hash function)** hợp lệ, nó vẫn không hoàn toàn an toàn. Nếu kẻ tấn công dễ dàng xác định được thuật toán băm và cookie không sử dụng **salt**, chúng có thể brute-force cookie bằng cách đơn giản là **băm wordlist** của mình.

Cách này thậm chí có thể được sử dụng để **vượt qua giới hạn số lần đăng nhập** nếu hệ thống **không áp dụng giới hạn tương tự cho việc thử cookie**.

Ngay cả khi kẻ tấn công **không thể tự tạo tài khoản**, lỗ hổng này vẫn có thể bị khai thác. Ví dụ:

- Bằng các kỹ thuật thường thấy như **XSS**, kẻ tấn công có thể đánh cắp cookie “remember me” của người dùng khác và từ đó phân tích cách cookie được sinh ra.
- Nếu website được xây dựng bằng **framework mã nguồn mở**, thì **chi tiết về cơ chế sinh cookie** có thể đã được **công khai trong tài liệu**, giúp kẻ tấn công dễ dàng hơn trong việc khai thác.

Trong một số trường hợp hiếm gặp, kẻ tấn công thậm chí có thể lấy được **mật khẩu gốc (cleartext password)** của người dùng trực tiếp từ cookie, ngay cả khi mật khẩu đó đã được băm.

Nguyên nhân là do:

- Các phiên bản băm của **các danh sách mật khẩu phổ biến** đã được công khai rộng rãi trên Internet.
- Nếu mật khẩu của người dùng nằm trong những danh sách này, việc "giải mã" hash đôi khi **đơn giản như việc dán hash đó vào công cụ tìm kiếm**.

Điều này cho thấy **tầm quan trọng của việc sử dụng salt trong quá trình mã hóa/băm** để đảm bảo an toàn cho mật khẩu.

---

### **Resetting user passwords**

---

Trong thực tế, một số người dùng sẽ quên mật khẩu, vì vậy hầu hết các website đều cung cấp **chức năng đặt lại mật khẩu**. Do trong tình huống này **không thể áp dụng cơ chế xác thực bằng mật khẩu thông thường**, website buộc phải dựa vào **các phương pháp thay thế** để đảm bảo rằng **chính chủ tài khoản** là người đang thực hiện việc đặt lại mật khẩu.

Chính vì lý do này, chức năng đặt lại mật khẩu vốn dĩ đã **tiềm ẩn nguy hiểm** và cần phải được triển khai một cách **an toàn tuyệt đối**.

Có một số cách triển khai tính năng này khá phổ biến, nhưng mỗi cách lại tồn tại những **mức độ lỗ hổng khác nhau**.

> **Qua Email**

Hiển nhiên rằng, nếu một website xử lý mật khẩu một cách an toàn ngay từ đầu thì việc **gửi mật khẩu hiện tại của người dùng qua email** là điều **tuyệt đối không bao giờ được phép xảy ra**.

Thay vào đó, một số website chọn cách **tạo mật khẩu mới** và gửi mật khẩu này cho người dùng qua email.

Tuy nhiên, về nguyên tắc, việc **gửi mật khẩu có giá trị lâu dài qua các kênh không an toàn** là điều cần tránh. Trong trường hợp này, độ an toàn phụ thuộc vào việc:

- Mật khẩu được sinh ra **hết hạn sau một khoảng thời gian rất ngắn**, hoặc
- Người dùng **ngay lập tức thay đổi lại mật khẩu** của mình.

Nếu không, phương pháp này sẽ **rất dễ bị tấn công Man-in-the-Middle (MitM)**.

Ngoài ra, **email nhìn chung không được coi là kênh an toàn**, bởi vì:

- Hộp thư đến thường là **lưu trữ lâu dài** và không được thiết kế để bảo mật thông tin nhạy cảm.
- Nhiều người dùng còn **đồng bộ hóa hộp thư giữa nhiều thiết bị** thông qua các kênh tiềm ẩn rủi ro.

> **Qua URL**

Một phương pháp **an toàn hơn** để đặt lại mật khẩu là gửi cho người dùng một **URL duy nhất** dẫn đến trang reset mật khẩu.

Tuy nhiên, những triển khai kém an toàn của phương pháp này lại sử dụng **URL với tham số dễ đoán** để xác định tài khoản cần đặt lại. Ví dụ:

```
<http://vulnerable-website.com/reset-password?user=victim-user>
```

Trong trường hợp này, kẻ tấn công có thể thay đổi giá trị của tham số `user` để tham chiếu đến bất kỳ username nào mà chúng đã xác định được. Từ đó, chúng có thể được đưa thẳng đến trang cho phép **đặt lại mật khẩu mới cho tài khoản bất kỳ**.

Một cách triển khai **an toàn hơn** là sinh ra một **token có entropy cao, khó đoán** và xây dựng URL reset dựa trên token đó. Trong kịch bản tốt nhất, URL này **không tiết lộ bất kỳ thông tin nào về người dùng** đang được đặt lại mật khẩu.

Ví dụ:

```
<http://vulnerable-website.com/reset-password?token=a0ba0d1cb3b63d13822572fcff1a241895d893f659164d4cc550b421ebdd48a8>
```

Khi người dùng truy cập URL này, hệ thống sẽ kiểm tra token ở backend để xác định:

- Token có tồn tại hay không.
- Nếu có, token đó gắn với tài khoản nào để tiến hành reset mật khẩu.

Token này cần phải:

- **Hết hạn sau một khoảng thời gian ngắn**, và
- **Bị hủy ngay lập tức** sau khi mật khẩu đã được đặt lại.

Tuy nhiên, một số website lại **không kiểm tra lại token khi form reset được submit**. Trong tình huống này, kẻ tấn công có thể:

1. Truy cập form reset mật khẩu từ chính tài khoản của chúng.
2. Xóa token khỏi request.
3. Lợi dụng trang này để **đặt lại mật khẩu cho tài khoản bất kỳ**.

Nếu URL trong email reset được sinh ra **một cách động (dynamically)**, thì cơ chế này cũng có thể dễ dàng bị tấn công theo kiểu **password reset poisoning**.

Trong tình huống này, kẻ tấn công có thể **đánh cắp token reset của người dùng khác** và sử dụng nó để **thay đổi mật khẩu** của họ.

---

### Changing user passwords

---

Thông thường, việc thay đổi mật khẩu yêu cầu người dùng nhập:

1. **Mật khẩu hiện tại**
2. **Mật khẩu mới** (nhập hai lần để xác nhận)

Các trang này về cơ bản dựa vào cùng một quy trình như **trang đăng nhập thông thường** để kiểm tra sự khớp giữa **username** và **mật khẩu hiện tại**. Do đó, chúng cũng có thể bị khai thác bằng **các kỹ thuật tấn công tương tự**.

Chức năng đổi mật khẩu đặc biệt **nguy hiểm** nếu cho phép kẻ tấn công **truy cập trực tiếp** mà **không cần đăng nhập bằng tài khoản nạn nhân**.

Ví dụ: nếu **username** được truyền trong một **trường ẩn (hidden field)**, kẻ tấn công có thể chỉnh sửa giá trị này trong request để nhắm đến tài khoản tùy ý. Điều này có thể bị khai thác để:

- **Liệt kê username (username enumeration)**
- **Brute-force mật khẩu**

---

# Ngăn chặn

---

Chúng ta đã xem qua nhiều cách mà các website có thể trở nên **dễ bị tấn công** do cách triển khai cơ chế xác thực.

Để giảm thiểu rủi ro các cuộc tấn công như vậy trên website của bạn, có một số **nguyên tắc quan trọng** mà bạn nên luôn tuân theo.

---

## User credentials

---

Ngay cả những cơ chế xác thực mạnh mẽ nhất cũng sẽ trở nên **vô dụng** nếu bạn vô tình làm lộ **thông tin đăng nhập hợp lệ** cho kẻ tấn công.

- Hiển nhiên, bạn **không bao giờ được gửi dữ liệu đăng nhập qua các kết nối không mã hóa**.
- Ngay cả khi bạn đã triển khai **HTTPS cho các request đăng nhập**, hãy đảm bảo rằng bạn **ép buộc sử dụng HTTPS** bằng cách **chuyển hướng toàn bộ HTTP request sang HTTPS**.

Ngoài ra, bạn cũng nên **kiểm tra (audit)** website để đảm bảo rằng:

- Không có **username** hoặc **địa chỉ email** nào bị lộ qua các **profile công khai**.
- Không bị phản hồi trong **HTTP response** theo bất kỳ cách nào.

---

## Don’t count on users

---

Các biện pháp xác thực nghiêm ngặt thường yêu cầu người dùng phải bỏ ra thêm một chút nỗ lực. Tuy nhiên, **bản chất con người** gần như chắc chắn sẽ khiến một số người tìm cách **lách luật để tiết kiệm công sức**. Vì vậy, bạn cần **cưỡng chế hành vi an toàn** ở bất cứ nơi nào có thể.

Ví dụ rõ ràng nhất là việc triển khai **chính sách mật khẩu hiệu quả**.

- Nhiều chính sách truyền thống thất bại vì người dùng cố gắng **“biến tấu” mật khẩu dễ đoán** của mình để khớp với yêu cầu chính sách.
- Thay vào đó, một giải pháp hiệu quả hơn là sử dụng **trình kiểm tra độ mạnh mật khẩu (password checker)**, cho phép người dùng thử nghiệm mật khẩu và nhận được phản hồi về độ mạnh **theo thời gian thực**.

Một ví dụ phổ biến là **thư viện JavaScript zxcvbn** do **Dropbox** phát triển. Bằng cách chỉ cho phép người dùng sử dụng các mật khẩu được trình kiểm tra đánh giá ở mức cao, bạn có thể **ép buộc sử dụng mật khẩu an toàn hiệu quả hơn** so với các chính sách truyền thống.

---

## **Prevent username enumeration**

---

Việc phá vỡ cơ chế xác thực của bạn sẽ trở nên **dễ dàng hơn nhiều** nếu bạn vô tình tiết lộ rằng một người dùng nào đó **tồn tại trong hệ thống**. Trong một số trường hợp, chỉ riêng việc biết rằng một cá nhân có tài khoản trên website cũng đã là **thông tin nhạy cảm**.

Để phòng tránh:

- Bất kể username thử có hợp lệ hay không, hãy sử dụng **các thông báo lỗi giống hệt nhau, dạng chung chung**, và đảm bảo rằng chúng **thực sự giống nhau**.
- Luôn trả về **cùng một HTTP status code** cho mọi request đăng nhập.
- Đảm bảo **thời gian phản hồi (response time)** trong các kịch bản khác nhau càng khó phân biệt càng tốt.

---

## **Implement robust brute-force protection**

---

Vì việc xây dựng một cuộc tấn công brute-force là **tương đối đơn giản**, nên việc triển khai các biện pháp để **ngăn chặn hoặc ít nhất là làm gián đoạn** các nỗ lực brute-force đăng nhập là điều **cực kỳ quan trọng**.

Một trong những phương pháp hiệu quả hơn là:

- **Triển khai cơ chế giới hạn tốc độ (rate limiting) nghiêm ngặt dựa trên IP**.
- Bao gồm các biện pháp để ngăn kẻ tấn công **giả mạo hoặc thao túng địa chỉ IP**.
- Lý tưởng nhất, sau khi đạt đến một giới hạn nhất định, người dùng cần phải **hoàn thành bài kiểm tra CAPTCHA** cho mỗi lần đăng nhập tiếp theo.

Lưu ý rằng những biện pháp này **không đảm bảo loại bỏ hoàn toàn mối đe dọa brute-force**. Tuy nhiên, việc khiến quy trình trở nên **thủ công và rườm rà** sẽ làm tăng khả năng kẻ tấn công **từ bỏ và chuyển sang mục tiêu dễ khai thác hơn**.

---

## **Triple-check your verification logic**

---

Các lỗi logic đơn giản rất dễ len lỏi vào mã và, trong trường hợp xác thực, chúng có thể dẫn đến việc xâm phạm hoàn toàn website và người dùng của bạn. Việc audit kỹ lưỡng mọi logic xác minh/kiểm tra hợp lệ để loại bỏ lỗi là yếu tố then chốt của một cơ chế xác thực vững chắc. Một bước kiểm tra có thể bị bỏ qua rốt cuộc cũng không tốt hơn nhiều so với việc không kiểm tra.

---

## **Don't forget supplementary functionality**

---

Hãy bảo đảm bạn không chỉ tập trung vào các trang đăng nhập trung tâm mà bỏ qua những chức năng bổ sung liên quan đến xác thực. Điều này đặc biệt quan trọng trong các trường hợp kẻ tấn công có thể tự do đăng ký tài khoản của riêng mình và khám phá các chức năng này. Hãy nhớ rằng việc đặt lại hoặc thay đổi mật khẩu cũng là một **bề mặt tấn công** hợp lệ như cơ chế đăng nhập chính và, do đó, phải vững chắc tương đương.

---

## **Implement proper multi-factor authentication**

---

Mặc dù xác thực đa yếu tố (MFA) có thể không thực tế với mọi website, nhưng khi được triển khai đúng cách, nó an toàn hơn nhiều so với chỉ đăng nhập dựa trên mật khẩu. Hãy nhớ rằng việc xác minh nhiều lần của **cùng một yếu tố** không phải là xác thực đa yếu tố thực sự. Gửi mã xác minh qua email về bản chất chỉ là một dạng kéo dài hơn của xác thực **một yếu tố**.

Về mặt kỹ thuật, 2FA dựa trên SMS xác minh hai yếu tố (thứ bạn biết và thứ bạn sở hữu). Tuy nhiên, khả năng bị lạm dụng qua **SIM swapping**, chẳng hạn, khiến hệ thống này có thể **không đáng tin cậy**.

Lý tưởng nhất, 2FA nên được triển khai bằng **thiết bị hoặc ứng dụng chuyên dụng** tạo mã xác minh trực tiếp. Do được thiết kế chuyên biệt cho bảo mật, chúng thường **an toàn hơn**.

Cuối cùng, cũng như với **logic xác thực** chính, hãy bảo đảm **logic kiểm tra 2FA** của bạn chặt chẽ để không thể dễ dàng bị **bỏ qua (bypass)**.

# WU 14 lab

- [x] Username enumeration via different responses
- [x] 2FA simple bypass
- [x] Password reset broken logic
- [x] Username enumeration via subtly different responses
- [x] Username enumeration via response timing
- [x] Broken brute-force protection - IP block
- [x] Username enumeration via account lock
- [x] 2FA broken logic
- [x] Brute-forcing a stay-logged-in cookie
- [x] Offline password cracking
- [x] Password reset poisoning via middleware
- [x] Password brute-force via password change
- [x] Broken brute-force protection - multiple credentials per request
- [x] 2FA bypass using a brute-force attack

## Username enumeration via different responses
- dùng burp intruder để bruteforce
![](../../image/Pasted%20image%2020260429220111.png)
- dùng clusterbomd và wordlist được cung cấp để dành cho việc bruteforce bài lab nhanh hơn
![](../../image/Pasted%20image%2020260429220332.png)

![](../../image/Pasted%20image%2020260429220658.png)
- bruteforce thành công, status code trả về 302, web đã redirect sang trang khác => login thành công
![](../../image/Pasted%20image%2020260429220752.png)

## 2FA simple bypass
![](../../image/Pasted%20image%2020260429223258.png)
- tài khoản wiener sau khi đã qua login 2 bước, ta thấy url trang cá nhân của tài khoản thường là /my-account ....

Thông thường, quy trình đăng nhập 2FA đúng phải là:
1. Nhập Username/Password $\rightarrow$ Server tạo Session tạm thời (chưa xác thực).
2. Nhập mã 2FA $\rightarrow$ Server kiểm tra, nếu đúng thì nâng cấp Session đó thành "Đã xác thực".
3. Chỉ cho phép truy cập `/my-account` nếu Session đã được xác thực hoàn toàn.

- bây giờ ta đăng xuất ra và login bằng tài khoản carlos:montoya, vì ko có mã code của carlos nên ta ko thể nhập mã, thử xóa url login2 đi và nhập /my-account?id=carlos vào
![](../../image/Pasted%20image%2020260429223850.png)

![](../../image/Pasted%20image%2020260429223757.png)
## Password reset broken logic

một quy trình đổi mật khẩu an toàn sẽ hoạt động như sau:
1. gửi yêu cầu reset mật khẩu.
2. Server gửi token duy nhất vào email của bạn.
3. Khi bạn nhấn vào link, server kiểm tra token đó có khớp với tài khoản của bạn không.
4. Nếu đúng, nó cho phép bạn đổi mật khẩu cho chính tài khoản đó.

- thử ấn vào quên mật khẩu với tài khoản wiener:peter được cấp
![](../../image/Pasted%20image%2020260429235031.png)

- ở gói tin này, server sử dụng token để cho phép bạn truy cập vào trang này, nhưng lại dùng tham số `username` để quyết định mật khẩu của ai sẽ bị đổi.

- dùng repeater để sửa username thành carlos và send, password của carlos sẽ thành 1
![](../../image/Pasted%20image%2020260430000845.png)

## Username enumeration via subtly different responses
- bruteforce với burp để tìm username và password hợp lệ
![](../../image/Pasted%20image%2020260430003525.png)
## Username enumeration via response timing

- ở bài lab này, ta vẫn cần bruteforce và dựa vào thời gian response trả về để xác định tài khoản tồn tại (thường response sẽ lâu hơn)
![](../../image/Pasted%20image%2020260430040409.png)
- cần thêm một Header tùy chỉnh vào request (ví dụ: `X-Forwarded-For: §1§`) để tránh bị chặn IP; để tạo sự khác biệt giữa các request.
- dùng pitchfork attack, cho header chạy từ 1-100 và dùng username list đc cấp
![](../../image/Pasted%20image%2020260430040853.png)

![](../../image/Pasted%20image%2020260430041015.png)

- thấy ở cột response, username appserver có response chậm hơn tất cả
- bruteforce 1 lần nữa để tìm password
![](../../image/Pasted%20image%2020260430041253.png)

![](../../image/Pasted%20image%2020260430041509.png)
## Broken brute-force protection, IP block
- bài lab này server sẽ khóa  sau một số lần thử sai nhất định (thường là 3 lần). Tuy nhiên, nó lại có một lỗi logic là bộ đếm số lần thử sai sẽ bị reset nếu bạn đăng nhập thành công một tài khoản hợp lệ
- vậy nên không thể Brute-force liên tục mật khẩu của Carlos vì sẽ bị chặn IP ngay lập tức. Thay vào đó, ta phải:
	- - Thử 1 mật khẩu cho `carlos`.
	- Đăng nhập thành công bằng `wiener` (tài khoản của bạn) để reset bộ đếm.
	- Thử mật khẩu tiếp theo cho `carlos`.
	- Lại đăng nhập bằng `wiener`...
- dùng turbo intruder trong burp: chỉnh sửa request Post: phần username và password để thành %s
- script sử dụng:
```
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1, # Quan trọng: để 1 để xử lý tuần tự
                           requestsPerConnection=100,
                           pipeline=False
                           )

    # Đọc danh sách mật khẩu của Carlos từ file (hoặc dán trực tiếp)
    passwords = open('C:\Users\ivanesk315\Desktop\password_list.txt').read().splitlines()

    for pwd in passwords:
        # 1. Thử mật khẩu cho Carlos
        engine.queue(target.req, ['carlos', pwd])
        
        # 2. Đăng nhập Wiener để reset bộ đếm (Sửa 'peter' nếu bạn đã đổi pass)
        engine.queue(target.req, ['wiener', 'peter'])

def handleResponse(req, interesting):
    # Chỉ hiển thị những request có phản hồi khác thường (như 302 Found)
    if req.status == 302:
        table.add(req)
```

![](../../image/Pasted%20image%2020260430042704.png)

- đã thấy response với tài khoản carlos và password là 11111111

## Username enumeration via account lock
- bài lab này có cơ chế khóa tài khoản : Sau $N$ lần nhập sai mật khẩu (ví dụ 5 lần), tài khoản đó sẽ bị khóa trong một khoảng thời gian (ví dụ 1 phút).

	=> **Nếu Username không tồn tại:** Bạn có thử sai 100 lần thì server vẫn chỉ báo: _"Invalid username or password"_. Nó không có gì để khóa cả. Ngược lại thì sau n lần thử sai, thông báo lỗi sẽ có dạng kiểu: "Too many incorrect login attempts. Please try again in 1 minute." Nếu user có trong db
Dựa vào sự thay đổi thông báo này, ta biết chắc chắn Username đó có thực hay không.
- vào burp intruder và chỉnh sang clusterbomb và sửa username với list username được cấp, ở password, ta sử dụng null payload với số lượng là 5
![](../../image/Pasted%20image%2020260430050143.png)

- kết quả cho thấy username là au có độ dài trả về bất thường 
![](../../image/Pasted%20image%2020260430050250.png)


- bruteforce lại mật khẩu
![](../../image/Pasted%20image%2020260430050857.png)

- ta thấy chỉ có request này là response trả về ngắn hơn 
- **Lẽ ra:** Khi tài khoản đã bị khóa, mọi mật khẩu (dù đúng hay sai) đều phải nhận được thông báo là tài khoản bị khóa. ở đây khi ta nhập **đúng** mật khẩu, nó lại "quên" kiểm tra trạng thái khóa và response ko trả về thông báo nào nên response ngắn hơn các response khác
![](../../image/Pasted%20image%2020260430051240.png)

## 2FA broken logic
![](../../image/Pasted%20image%2020260430051357.png)
- đây là tài khoản wiener sau khi login thành công

ở burp, có 1 request /login có cookie `verify=wiener` rất khả nghi
![](../../image/Pasted%20image%2020260430051551.png)

- ở burp repeater, đổi cookie sang carlos rồi gửi, điều này đảm bảo rằng có 1 mã code đã tạo cho tài khoản carlos
![](../../image/Pasted%20image%2020260430052028.png)

- bây giờ login lại bằng wiener:peter, tiếp theo là nhập mã code, vì server vẫn đang xử lí 1 mã code cho carlos, ta cần bruteforce mã code đó, gửi gói tin sang intruder, đảm bảo chỉnh lại verify sang carlos và bruteforce từ 0 đến 9999, chỉnh min digit thành 4 để hiển thị chuẩn 4 chữ số
![](../../image/Pasted%20image%2020260430052557.png)

- login lại bằng wiener:peter, sau đó bật intercept để chặn gói tin, sửa phần verify sang carlos và nhập 1231 để login thành công
![](../../image/Pasted%20image%2020260430052827.png)

## Brute-forcing a stay-logged-in cookie
![](../../image/Pasted%20image%2020260430173329.png)
![](../../image/Pasted%20image%2020260430180019.png)
- trong request này, có thể thấy phần cookie có stay-logged-in = ....
![](../../image/Pasted%20image%2020260430180145.png)
- sau khi decode sang base64, thấy nó có dạng username và mã băm của password 
=> với danh sách password được cấp, ta có thể bruteforce tài khoản của carlos với định dạng tương tự
- trong tab intruder để simple attack và thêm danh sách password vào
![](../../image/Pasted%20image%2020260430181038.png)
ở phần configure, cần cấu hình lần lượt để chuuyeenr password sang md5, thêm tiền tố là carlos: rồi mã hóa base64 toàn bộ. khi thực hiên attack, thấy có 1 status 200 là đã solved thành công
![](../../image/Pasted%20image%2020260430214645.png)

==lưu ý: cần đổi thủ công cả phần id sang carlos vì phiên bản HTTP/2  thường kiểm tra nghiêm ngặt hơn so với HTTP/1==

## Offline password cracking

- bài lab này cũng có cookie tương tự đã đc mã hóa để quản lí session của user
![](../../image/Pasted%20image%2020260430215226.png)

- login vào tài khoản của wiener, khai thác xss bằng cách comment vào 1 bài lab bất kỳ
![](../../image/Pasted%20image%2020260430225832.png)
- sang tab exploit vào phần accesss log, ta thấy 1 địa chỉ lạ có cookie đã mã hóa base64
![](../../image/Pasted%20image%2020260430225910.png)
![](../../image/Pasted%20image%2020260430225917.png)

- bruteforce để tìm mật khẩu đã hash của carlos
![](../../image/Pasted%20image%2020260430230029.png)
password là onceuponatime

## Password reset poisoning via middleware

- ở lab này, khi ta ấn forgot password thì có 1 link gửi qua email
![](../../image/Pasted%20image%2020260430230758.png)
![](../../image/Pasted%20image%2020260430230926.png)

![](../../image/Pasted%20image%2020260430230933.png)
- ta thấy server sử dụng Header `Host` trong HTTP Request để tự động tạo ra phần Domain của link reset. Nếu chúng ta thay đổi `Host` thành địa chỉ server của mình, server có thể sẽ gửi một link reset cho nạn nhân => thêm header: X-forwarded-host: và copy url của trang exploit vào và thay username thành carlos rồi send
- ta truy cập vào trang exploit sẽ có 1 link reset gửi tới email của wiener, copy link đó sang tab mới 
- ở trang accesslog, có 1 request get, đây là token bí mật của carlos đã gửi đến server của ta, đổi link reset của wiener thành token này và reset password cho carlos
![](../../image/Pasted%20image%2020260430233131.png)

## Password brute-force via password change
- ở bài lab này thay vì brute-force ở trang Login, chúng ta sẽ lợi dụng tính năng **đổi mật khẩu** để dò mật khẩu hiện tại. lỗ hổng này xảy ra khi tính năng đổi mật khẩu yêu cầu nhập "Mật khẩu cũ" nhưng lại không giới hạn số lần nhập sait
- request post reset password  có các parameter như hình
![](../../image/Pasted%20image%2020260430234936.png)


- đổi username thành carlos và bruteforce current -password, đổi new-password thành 1-2 để hiển thị thông báo lỗi nếu mật khẩu hiện tại đúng
![](../../image/Pasted%20image%2020260430235900.png)

![](../../image/Pasted%20image%2020260430235828.png)

## Broken brute-force protection, multiple credentials per request

Thông thường, cơ chế bảo vệ (Rate Limiting) của server sẽ đếm số lượng request gửi đến.
- **Cách cũ:** 100 mật khẩu = 100 request $\rightarrow$ Server chặn sau request thứ 5
- **Lỗ hổng:** Nếu server cho phép tham số mật khẩu nhận vào là một **mảng (Array)**, nó có thể kiểm tra toàn bộ mảng đó trong một lần xử lý.
=>  thử 100 mật khẩu nhưng server chỉ tính là **1 request**.
![](../../image/Pasted%20image%2020260501001234.png)
- có thể thấy là username và password được cho vào định dạng JSON
- thử dùng repeater và đưa vào mảng password
![](../../image/Pasted%20image%2020260501001351.png)
=> server có khả năng xử lý mảng 
![](../../image/Pasted%20image%2020260501001613.png)
- truyền vào toàn bộ password, sau đó chuột phải để request in brower và solved bài lab

## 2FA bypass using a brute-force attack
- ở bài lab này, khi nhập sai quá 2 lần mã 2FA, ta sẽ bị văng khỏi session hiện tại
![](../../image/Pasted%20image%2020260501002806.png)
- chúng ta cần dùng tính năng **Macro** để tự động đăng nhập lại trước mỗi lần thử.
![](../../image/Pasted%20image%2020260501003419.png)
mỗi lần chạy thì burp sẽ tự động chạy các request trên trước khi gửi mã 2fa ở tab intruder
![](../../image/Pasted%20image%2020260501005004.png)
