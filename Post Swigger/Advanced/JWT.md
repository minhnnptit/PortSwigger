<!-- TOC -->
## Mục lục

- [Giới thiệu](#giới-thiệu)
- [JWTs là gì?](#jwts-là-gì)
  - [JWT format](#jwt-format)
  - [JWT signature](#jwt-signature)
  - [JWT / JWS / JWE](#jwt--jws--jwe)
- [JWT attacks](#jwt-attacks)
- [Hậu quả](#hậu-quả)
- [Nguyên nhân](#nguyên-nhân)
- [Xâm nhập](#xâm-nhập)
  - [**JWT signature verification**](#jwt-signature-verification)
    - [Chấp nhận chữ ký tùy ý](#chấp-nhận-chữ-ký-tùy-ý)
    - [Chấp nhận không chữ ký](#chấp-nhận-không-chữ-ký)
  - [**Brute-forcing secret keys**](#brute-forcing-secret-keys)
    - [Hashcat](#hashcat)
  - [**JWT header parameter injections**](#jwt-header-parameter-injections)
    - [jwk](#jwk)
    - [jku](#jku)
    - [kid](#kid)
    - [other parameters](#other-parameters)
  - [**Algorithm confusion attacks**](#algorithm-confusion-attacks)
    - [**Symmetric vs asymmetric algo**](#symmetric-vs-asymmetric-algo)
    - [Nguyên nhân](#nguyên-nhân-1)
    - [Thực hiện tấn công](#thực-hiện-tấn-công)
    - [**Deriving public keys from existing tokens**](#deriving-public-keys-from-existing-tokens)
- [Bảo mật](#bảo-mật)
- [WU](#wu)
  - [JWT authentication bypass via unverified signature](#jwt-authentication-bypass-via-unverified-signature)
  - [JWT authentication bypass via flawed signature verification](#jwt-authentication-bypass-via-flawed-signature-verification)
  - [JWT authentication bypass via weak signing key](#jwt-authentication-bypass-via-weak-signing-key)
  - [JWT authentication bypass via jwk header injection](#jwt-authentication-bypass-via-jwk-header-injection)
  - [JWT authentication bypass via jku header injection](#jwt-authentication-bypass-via-jku-header-injection)
  - [JWT authentication bypass via kid header path traversal](#jwt-authentication-bypass-via-kid-header-path-traversal)
  - [JWT authentication bypass via algorithm confusion](#jwt-authentication-bypass-via-algorithm-confusion)
  - [JWT authentication bypass via algorithm confusion with no exposed key](#jwt-authentication-bypass-via-algorithm-confusion-with-no-exposed-key)
<!-- /TOC -->

# Giới thiệu

Trong phần này, chúng ta sẽ xem xét cách các vấn đề thiết kế và xử lý sai JSON Web Token (JWT) có thể khiến các website dễ bị tổn thương trước nhiều loại tấn công có mức độ nghiêm trọng cao. Vì JWT thường được dùng trong xác thực, quản lý phiên và cơ chế kiểm soát truy cập, những lỗ hổng này có khả năng làm tổn hại toàn bộ website và người dùng của nó.

Đừng lo nếu bạn chưa quen với JWT và cách chúng hoạt động - chúng ta sẽ trình bày tất cả những chi tiết liên quan khi đi tiếp. Chúng tôi cũng đã cung cấp một số phòng lab có lỗ hổng được bố trí cố ý để bạn có thể thực hành khai thác những lỗ hổng này một cách an toàn trên các mục tiêu thực tế.

# JWTs là gì?


JSON Web Token (JWT) là một định dạng tiêu chuẩn để truyền dữ liệu JSON được ký bằng mật mã giữa các hệ thống. Về lý thuyết, chúng có thể chứa bất kỳ loại dữ liệu nào, nhưng thường được dùng để gửi thông tin (“claims”) về người dùng như một phần của các cơ chế xác thực, quản lý phiên và kiểm soát truy cập.

Khác với token phiên truyền thống, toàn bộ dữ liệu mà máy chủ cần đều được lưu ở phía client trong chính JWT. Điều này khiến JWT trở thành lựa chọn phổ biến cho các website phân tán cao, nơi người dùng cần tương tác liền mạch với nhiều máy chủ back-end.

## JWT format

Một JWT gồm 3 phần: một header (tiêu đề), một payload (phần tải), và một signature (chữ ký). Các phần này được phân tách bằng dấu chấm, như trong ví dụ sau:

```json
eyJraWQiOiI5MTM2ZGRiMy1jYjBhLTRhMTktYTA3ZS1lYWRmNWE0NGM4YjUiLCJhbGciOiJSUzI1NiJ9.
eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTY0ODAzNzE2NCwibmFtZSI6IkNhcmxvcyBNb250b3lhIiwic3ViIjoiY2FybG9zIiwicm9sZSI6ImJsb2dfYXV0aG9yIiwiZW1haWwiOiJjYXJsb3NAY2FybG9zLW1vbnRveWEubmV0IiwiaWF0IjoxNTE2MjM5MDIyfQ.
SYZBPIBg2CRjXAJ8vCER0LA_ENjII1JakvNQoP-Hw6GG1zfl4JyngsZReIfqRvIAEi5L4HV0q7_9qGhQZvy9ZdxEJbwTxRs_6Lb-fZTDpW6lKYNdMyjw45_alSCZ1fypsMWz_2mTpQzil0lOtps5Ei_z7mM7M8gCwe_AGpI53JxduQOaB5HkT5gVrv9cKu9CsW5MS6ZbqYXpGyOG5ehoxqm8DL5tFYaW3lB50ELxi0KsuTKEbD0t5BCl0aCR2MBJWAbN-xeLwEenaqBiwPVvKixYleeDQiBEIylFdNNIMviKRgXiYuAvMziVPbwSgkZVHeEdF5MQP1Oe2Spac-6IfA
```

Các phần header và payload của JWT chỉ là các đối tượng JSON được mã hóa theo base64url. Header chứa siêu dữ liệu về chính token, trong khi payload chứa các “claims” (tuyên bố) thực tế về người dùng. Ví dụ, bạn có thể giải mã payload từ token ở trên để thấy các claims sau:

```json
{
	"iss": "portswigger",
	"exp": 1648037164,
	"name": "Carlos Montoya",
	"sub": "carlos",
	"role": "blog_author",
	"email": "carlos@carlos-montoya.net",
	"iat": 1516239022
}
```

Trong hầu hết các trường hợp, dữ liệu này có thể được bất kỳ ai có quyền truy cập vào token đọc hoặc sửa đổi một cách dễ dàng. Do đó, tính bảo mật của bất kỳ cơ chế dựa trên JWT nào phụ thuộc nặng nề vào chữ ký mật mã.

## JWT signature

Máy chủ phát hành token thường tạo chữ ký bằng cách băm (hash) phần header và payload. Trong một vài trường hợp, họ còn mã hóa kết quả băm. Dù theo cách nào, quá trình này đều sử dụng một **khóa ký bí mật**. Cơ chế này cho phép máy chủ xác minh rằng không có dữ liệu nào trong token bị chỉnh sửa kể từ khi nó được phát hành:

Vì chữ ký được suy ra trực tiếp từ phần còn lại của token, việc thay đổi chỉ một byte trong header hoặc payload sẽ dẫn tới chữ ký không khớp.

Nếu **không biết khóa ký bí mật** của máy chủ, sẽ không thể tạo ra chữ ký đúng cho một header hoặc payload bất kỳ.

> **Mẹo**
> 
> Nếu bạn muốn hiểu rõ hơn cách JWT được cấu thành, bạn có thể dùng công cụ gỡ lỗi trên `jwt.io` để thử nghiệm với các token tùy ý.

## JWT / JWS / JWE


Đặc tả JWT thực ra khá hạn chế. Nó chỉ định nghĩa một định dạng để biểu diễn thông tin (“claims”) dưới dạng một đối tượng JSON có thể truyền giữa hai bên. Trên thực tế, JWT hiếm khi được dùng như một thực thể độc lập. Đặc tả JWT được mở rộng bởi cả JSON Web Signature (JWS) và JSON Web Encryption (JWE), những đặc tả định nghĩa các cách triển khai JWT một cách cụ thể.

Nói cách khác, một JWT thường là token JWS hoặc JWE. Khi mọi người dùng thuật ngữ “JWT”, họ gần như luôn ám chỉ token JWS. JWE rất giống JWS, ngoại trừ việc nội dung thực của token được **mã hóa** chứ không chỉ **mã hóa biểu diễn (encode)**.

> Lưu ý
> 
> Để đơn giản, trong toàn bộ tài liệu này, “JWT” chủ yếu đề cập tới token JWS, mặc dù một số lỗ hổng được mô tả cũng có thể áp dụng cho token JWE.

# JWT attacks

Các cuộc tấn công JWT xảy ra khi kẻ tấn công gửi các JWT đã bị chỉnh sửa tới máy chủ nhằm đạt được mục đích độc hại. Thông thường, mục tiêu là vượt qua cơ chế xác thực và kiểm soát truy cập bằng cách mạo danh một người dùng khác đã được xác thực.
# Hậu quả

Hậu quả thường rất nghiêm trọng. Nếu kẻ tấn công có thể tự tạo các token hợp lệ với giá trị tùy ý, họ có thể leo thang đặc quyền của chính mình hoặc mạo danh người dùng khác, giành toàn quyền kiểm soát tài khoản của họ.

# Nguyên nhân

Các lỗ hổng JWT thường xuất hiện do việc xử lý JWT không chuẩn trong chính ứng dụng. Các đặc tả liên quan tới JWT được thiết kế tương đối linh hoạt, cho phép nhà phát triển quyết định nhiều chi tiết triển khai. Điều này có thể vô tình tạo ra lỗ hổng ngay cả khi dùng các thư viện đã dày dạn thực chiến.

Những sai sót triển khai này thường dẫn đến việc chữ ký của JWT không được xác minh đúng cách. Điều này cho phép kẻ tấn công can thiệp vào các giá trị được truyền vào ứng dụng thông qua payload của token. Ngay cả khi chữ ký được xác minh chặt chẽ, việc có thể thực sự tin cậy hay không còn phụ thuộc nhiều vào việc **khóa ký bí mật** của máy chủ có được giữ bí mật không. Nếu khóa này bị rò rỉ theo cách nào đó, hoặc có thể bị đoán/Brute-force, kẻ tấn công có thể tạo chữ ký hợp lệ cho bất kỳ token tùy ý nào, từ đó phá vỡ toàn bộ cơ chế.

# Xâm nhập
## **JWT signature verification**


Theo thiết kế, máy chủ thường không lưu trữ bất kỳ thông tin nào về các JWT mà nó phát hành. Thay vào đó, mỗi token là một thực thể hoàn toàn độc lập. Điều này đem lại vài lợi ích, nhưng cũng nảy sinh một vấn đề cơ bản - máy chủ thực tế không biết gì về nội dung gốc của token, hoặc thậm chí chữ ký gốc là gì. Do đó, nếu máy chủ không xác minh chữ ký đúng cách, sẽ không có gì ngăn kẻ tấn công thực hiện các thay đổi tùy ý lên phần còn lại của token.

Ví dụ, hãy xem xét một JWT chứa các claims sau:

```json
{
	"username": "carlos",
	"isAdmin": false
}
```

Nếu máy chủ xác định phiên dựa trên trường username này, việc sửa giá trị nó có thể cho phép kẻ tấn công mạo danh các người dùng đã đăng nhập khác. Tương tự, nếu giá trị `isAdmin` được dùng để kiểm soát truy cập, điều này có thể cung cấp một vector đơn giản để leo thang đặc quyền.

Trong vài lab đầu, bạn sẽ thấy một số ví dụ về cách những lỗ hổng này xuất hiện trong các ứng dụng thực tế.

### Chấp nhận chữ ký tùy ý


Các thư viện JWT thường cung cấp một phương thức để **xác minh** token và một phương thức chỉ để **giải mã** (decode) chúng. Ví dụ, thư viện Node.js `jsonwebtoken` có `verify()` và `decode()`.

Đôi khi, các nhà phát triển nhầm lẫn hai phương thức này và chỉ truyền token nhận được vào `decode()`. Điều này về bản chất có nghĩa là ứng dụng **không xác minh chữ ký** chút nào.

### Chấp nhận không chữ ký

Trong số những thứ khác, header của JWT chứa một tham số `alg`. Tham số này cho máy chủ biết thuật toán nào đã được dùng để ký token và do đó thuật toán nào cần dùng khi xác minh chữ ký.

```json
{
    "alg": "HS256",
    "typ": "JWT"
}
```

Thiết kế này vốn đã có vấn đề vì máy chủ buộc phải ngầm tin vào dữ liệu do người dùng điều khiển trong token, mà tại thời điểm đó dữ liệu chưa được xác minh. Nói cách khác, kẻ tấn công có thể trực tiếp ảnh hưởng đến cách máy chủ kiểm tra tính tin cậy của token.

JWT có thể được ký bằng nhiều thuật toán khác nhau, nhưng cũng có thể để không ký. Trong trường hợp này tham số `alg` được đặt thành `none`, biểu thị một JWT “không được bảo vệ” (unsecured JWT). Do những mối nguy rõ ràng của việc này, máy chủ thường từ chối các token không có chữ ký. Tuy nhiên, vì kiểu lọc này dựa trên phân tích chuỗi, đôi khi bạn có thể vượt qua các bộ lọc bằng các kỹ thuật ẩn danh cổ điển, chẳng hạn như chữ hoa/chữ thường hỗn hợp hoặc các kiểu mã hóa không ngờ tới.

> Lưu ý
> 
> Ngay cả khi token không được ký, phần payload vẫn phải kết thúc bằng một dấu chấm ở cuối.

## **Brute-forcing secret keys**


Một số thuật toán ký, chẳng hạn HS256 (HMAC + SHA-256), sử dụng một chuỗi độc lập bất kỳ làm **khóa bí mật**. Cũng giống như mật khẩu, điều then chốt là khóa này không được dễ bị đoán hoặc bẻ khóa bằng phương pháp brute-force. Nếu không, kẻ tấn công có thể tạo JWT với bất kỳ header và payload nào chúng muốn, rồi dùng khóa đó để **ký lại** token với chữ ký hợp lệ.

Khi triển khai ứng dụng sử dụng JWT, các nhà phát triển đôi khi mắc phải sai lầm như quên thay đổi các khóa mặc định hoặc khóa giữ chỗ (placeholder). Họ thậm chí có thể sao chép và dán các đoạn mã tìm thấy trên mạng, rồi quên thay khóa bí mật **được mã cứng trong mã nguồn** mà ví dụ cung cấp. Trong trường hợp này, kẻ tấn công có thể dễ dàng dùng wordlist chứa các khóa phổ biến để brute-force (bẻ khóa) khóa bí mật của máy chủ.

### Hashcat


Chúng tôi khuyên dùng **hashcat** để bẻ khóa khóa bí mật. Bạn có thể cài đặt hashcat thủ công, nhưng công cụ này cũng được cài sẵn và sẵn sàng sử dụng trên Kali Linux.

> **Lưu ý**
> 
> Nếu bạn đang dùng ảnh VirtualBox dựng sẵn của Kali thay vì cài lên phần cứng thật (bare-metal), ảnh đó có thể không được cấp đủ bộ nhớ để chạy hashcat.

Bạn chỉ cần một JWT hợp lệ đã được ký từ máy chủ mục tiêu và một wordlist (danh sách từ) chứa các khóa phổ biến. Sau đó chạy lệnh sau, truyền JWT và wordlist làm đối số:

```
hashcat -a 0 -m 16500 <jwt> <wordlist>
```

Hashcat sẽ lấy header và payload từ JWT, ký lại bằng từng khóa trong wordlist, rồi so sánh chữ ký thu được với chữ ký gốc từ máy chủ. Nếu bất kỳ chữ ký nào khớp, hashcat sẽ in ra khóa tìm được theo định dạng sau, kèm một số thông tin khác:

```
<jwt>:<identified-secret>
```

> Lưu ý
> 
> Nếu bạn chạy lệnh này nhiều lần, cần thêm cờ `--show` để hiển thị kết quả.

Vì hashcat chạy cục bộ trên máy của bạn và không gửi yêu cầu tới máy chủ, quá trình này rất nhanh ngay cả khi dùng wordlist rất lớn.

Khi bạn đã xác định được khóa bí mật, có thể dùng khóa đó để tạo chữ ký hợp lệ cho bất kỳ header và payload JWT nào bạn muốn. Để biết chi tiết cách ký lại (re-sign) một JWT đã chỉnh sửa trong Burp Suite, xem phần _Editing JWTs_.

## **JWT header parameter injections**

Theo đặc tả JWS, chỉ có tham số `alg` trong header là bắt buộc. Tuy nhiên, trên thực tế, header của JWT (còn gọi là header JOSE) thường chứa nhiều tham số khác. Những tham số sau đây đặc biệt đáng chú ý đối với kẻ tấn công.

- `jwk` (JSON Web Key) — Cung cấp một đối tượng JSON nhúng biểu diễn khóa.
- `jku` (JSON Web Key Set URL) — Cung cấp một URL mà từ đó máy chủ có thể tải xuống một tập khóa (key set) chứa khóa đúng.
- `kid` (Key ID) — Cung cấp một ID mà máy chủ có thể dùng để xác định khóa đúng trong trường hợp có nhiều khóa để lựa chọn. Tùy vào định dạng của khóa, khóa tương ứng có thể có tham số `kid` khớp.

Như bạn thấy, những tham số do người dùng điều khiển này đều chỉ cho máy chủ nhận token biết khóa nào cần dùng khi xác minh chữ ký. Trong phần này, bạn sẽ học cách lợi dụng những tham số này để chèn các JWT đã chỉnh sửa được ký bằng khóa tùy ý của bạn thay vì bằng khóa bí mật của máy chủ.

### jwk


Đặc tả JSON Web Signature (JWS) mô tả một tham số header tùy chọn là `jwk`, cho phép máy chủ nhúng trực tiếp **khóa công khai** của họ ngay bên trong token dưới định dạng JWK.

> **JWK**
> 
> Một JWK (JSON Web Key) là định dạng chuẩn để biểu diễn khóa dưới dạng một đối tượng JSON.

Bạn có thể thấy một ví dụ về điều này trong header JWT sau:

```json
{
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
    "typ": "JWT",
    "alg": "RS256",
    "jwk": {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
        "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m"
    }
}
```

> **Khóa công khai và khóa riêng**
> 
> Trong trường hợp bạn chưa quen với các khái niệm "khóa công khai" và "khóa riêng", chúng tôi đã đề cập điều này trong tài liệu về các cuộc tấn công nhầm lẫn thuật toán (algorithm confusion attacks). Để biết thêm, xem phần _Symmetric vs asymmetric algorithms_.

Lẽ ra, máy chủ chỉ nên sử dụng một whitelist (danh sách trắng) hạn chế các khóa công khai để xác minh chữ ký JWT. Tuy nhiên, những máy chủ cấu hình sai đôi khi chấp nhận bất kỳ khóa nào được nhúng trong tham số `jwk`.

Bạn có thể khai thác hành vi này bằng cách ký một JWT đã chỉnh sửa dùng **khóa riêng RSA** của chính bạn, sau đó nhúng khóa công khai tương ứng vào header `jwk`.

Mặc dù bạn có thể tự tay thêm hoặc sửa tham số `jwk` bằng Burp, tiện ích mở rộng **JWT Editor** cung cấp một tính năng hữu ích để kiểm thử lỗ hổng này:

1. Sau khi load extension, trong thanh tab chính của Burp, vào tab **JWT Editor → Keys**.
2. Tạo (generate) một khóa RSA mới.
3. Gửi một yêu cầu chứa JWT tới Burp Repeater.
4. Trong message editor, chuyển sang tab **JSON Web Token** do extension tạo và chỉnh sửa payload theo ý bạn.
5. Nhấn **Attack**, rồi chọn **Embedded JWK**. Khi được hỏi, chọn khóa RSA bạn vừa tạo.
6. Gửi yêu cầu để kiểm tra phản ứng của máy chủ.

Bạn cũng có thể thực hiện tấn công này thủ công bằng cách thêm header `jwk` vào token. Tuy nhiên, bạn có thể cần cập nhật tham số `kid` trong header JWT để khớp với `kid` của khóa được nhúng. Tính năng tấn công tích hợp của extension sẽ lo bước này cho bạn.
### jku

Thay vì nhúng khóa công khai trực tiếp bằng tham số header `jwk`, một số máy chủ cho phép bạn sử dụng tham số header `jku` (JWK Set URL) để tham chiếu tới một JWK Set chứa khóa. Khi xác minh chữ ký, máy chủ sẽ truy xuất (fetch) khóa tương ứng từ URL này.

> JWK Set
> 
> Một JWK Set là một đối tượng JSON chứa một mảng các JWK đại diện cho các khóa khác nhau. Ví dụ như sau:

```json
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
            "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
        },
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA",
            "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ_cb33HocCuJolwDqmk6GPM4Y_qTVX67WhsN3JvaFYw-dfg6DH-asAScw"
        }
    ]
}

```

Các JWK Set như vậy đôi khi được công khai tại một endpoint tiêu chuẩn, ví dụ `/.well-known/jwks.json`.

Các website có bảo mật cao hơn chỉ truy xuất khóa từ các miền đáng tin cậy, nhưng đôi khi bạn có thể lợi dụng các khác biệt khi phân tích URL để vượt qua loại lọc này. Chúng tôi đã trình bày một vài ví dụ về điều đó trong chủ đề về SSRF.

### kid
Máy chủ có thể sử dụng nhiều khoá mật mã khác nhau để ký các loại dữ liệu khác nhau, không chỉ JWT. Vì lý do này, header của một JWT có thể chứa tham số `kid` (Key ID), giúp máy chủ xác định khoá nào sẽ dùng khi xác minh chữ ký.

Các khoá xác minh thường được lưu dưới dạng JWK Set. Trong trường hợp này, máy chủ có thể đơn giản là tìm JWK có `kid` trùng với token. Tuy nhiên, đặc tả JWS không định nghĩa một cấu trúc cụ thể cho ID này - nó chỉ là một chuỗi tùy ý do nhà phát triển chọn. Ví dụ, họ có thể dùng tham số `kid` để trỏ tới một mục cụ thể trong cơ sở dữ liệu, hoặc thậm chí là tên của một tệp tin.

Nếu tham số này cũng dễ bị tấn công bằng khai thác lỗ hổng duyệt thư mục (directory traversal), kẻ tấn công có thể ép máy chủ sử dụng một tệp bất kỳ trên hệ thống tập tin của nó làm khoá xác minh.

```json
{
    "kid": "../../path/to/file",
    "typ": "JWT",
    "alg": "HS256",
    "k": "asGsADas3421-dfh9DGN-AFDFDbasfd8-anfjkvc"
}
```

Điều này đặc biệt nguy hiểm nếu máy chủ cũng hỗ trợ JWT được ký bằng thuật toán đối xứng (symmetric). Trong trường hợp đó, kẻ tấn công có thể trỏ tham số `kid` tới một tệp tĩnh, dự đoán được, rồi ký JWT bằng một secret khớp với nội dung của tệp này.

Về lý thuyết bạn có thể làm điều này với bất kỳ tệp nào, nhưng một trong những cách đơn giản nhất là dùng `/dev/null`, tồn tại trên hầu hết hệ thống Linux. Vì đây là một tệp rỗng, đọc nó trả về chuỗi rỗng. Do đó, ký token bằng một chuỗi rỗng sẽ dẫn tới một chữ ký hợp lệ.

> Lưu ý
> 
> Nếu bạn sử dụng tiện ích mở rộng JWT Editor, lưu ý rằng tiện ích này không cho phép bạn ký token bằng chuỗi rỗng. Tuy nhiên, do một lỗi trong extension, bạn có thể vượt qua hạn chế này bằng cách sử dụng một byte null được mã hóa Base64.

Nếu máy chủ lưu khoá xác minh trong cơ sở dữ liệu, tham số header `kid` cũng là một vector tiềm năng cho các cuộc tấn công SQL injection.

### other parameters

Các tham số header sau cũng có thể thu hút sự chú ý của kẻ tấn công:

- **cty (Content Type)** - Đôi khi được dùng để khai báo kiểu media cho nội dung trong payload của JWT. Thông thường tham số này bị bỏ qua trong header, nhưng thư viện phân tích cú pháp ở phía dưới có thể vẫn hỗ trợ. Nếu bạn tìm được cách vượt qua việc xác minh chữ ký, bạn có thể thử chèn header `cty` để thay đổi kiểu nội dung thành `text/xml` hoặc `application/x-java-serialized-object`, điều này có thể mở ra các vector mới cho các tấn công XXE và tấn công deserialization.
- **x5c (X.509 Certificate Chain)** - Đôi khi được dùng để truyền chứng chỉ công khai X.509 hoặc chuỗi chứng chỉ của khóa dùng để ký JWT. Tham số header này có thể bị lợi dụng để chèn chứng chỉ tự ký (self-signed), tương tự như các cuộc tấn công chèn `jwk` đã thảo luận ở trên. Do tính phức tạp của định dạng X.509 và các tiện ích mở rộng của nó, việc phân tích những chứng chỉ này cũng có thể giới thiệu các lỗ hổng. Chi tiết về các cuộc tấn công này nằm ngoài phạm vi tài liệu, nhưng để biết thêm, xem CVE-2017-2800 và CVE-2018-2633.
## **Algorithm confusion attacks**

Tấn công nhầm lẫn thuật toán (còn gọi là _key confusion attacks_) xảy ra khi kẻ tấn công có thể buộc máy chủ xác minh chữ ký của một JSON Web Token (JWT) bằng một thuật toán khác so với thuật toán mà nhà phát triển trang web dự định sử dụng. Nếu tình huống này không được xử lý đúng cách, nó có thể cho phép kẻ tấn công giả mạo các JWT hợp lệ chứa giá trị tùy ý mà không cần biết khóa bí mật dùng để ký của máy chủ.

### **Symmetric vs asymmetric algo**


JWT có thể được ký bằng nhiều loại thuật toán khác nhau. Một số thuật toán, chẳng hạn như **HS256 (HMAC + SHA-256)**, sử dụng **khóa đối xứng (symmetric key)**. Điều này có nghĩa là máy chủ dùng **cùng một khóa** để vừa ký vừa xác minh token. Rõ ràng, khóa này phải được giữ bí mật tuyệt đối, giống như mật khẩu.

Ngược lại, các thuật toán khác như **RS256 (RSA + SHA-256)** sử dụng **cặp khóa bất đối xứng (asymmetric key pair)**. Cặp này bao gồm:

- **Khóa riêng (private key):** máy chủ dùng để ký token.
- **Khóa công khai (public key):** có quan hệ toán học với khóa riêng và được dùng để xác minh chữ ký.

Như tên gọi, **khóa riêng phải được giữ bí mật**, trong khi **khóa công khai thường được chia sẻ rộng rãi** để bất kỳ ai cũng có thể xác minh chữ ký của các token do máy chủ phát hành.

### Nguyên nhân

Lỗ hổng nhầm lẫn thuật toán thường xuất hiện do việc triển khai thư viện JWT bị lỗi. Mặc dù quá trình xác minh thực tế khác nhau tùy theo thuật toán được sử dụng, nhiều thư viện cung cấp một phương thức duy nhất **(không phụ thuộc vào thuật toán**) để xác minh chữ ký. Những phương thức này dựa vào tham số **`alg`** trong header của token để xác định kiểu xác minh cần thực hiện.

Đoạn pseudo-code sau cho thấy một ví dụ đơn giản hóa về khai báo cho phương thức verify() tổng quát này có thể trông như thế nào trong một thư viện JWT:

```jsx
function verify(token, secretOrPublicKey){
    algorithm = token.getAlgHeader();
    if(algorithm == "RS256"){
        // Use the provided key as an RSA public key
        // Sử dụng khóa được cung cấp như một khóa công khai RSA
    } else if (algorithm == "HS256"){
        // Use the provided key as an HMAC secret key
        // Sử dụng khóa được cung cấp như một khóa bí mật HMAC
    }
}
```

Vấn đề phát sinh khi các nhà phát triển trang web, khi sử dụng phương thức này, giả định sai rằng nó sẽ chỉ xử lý các JWT được ký bằng thuật toán bất đối xứng như RS256. Do giả định sai này, họ có thể luôn truyền một **khóa công khai cố định** vào phương thức như sau:

```jsx
publicKey = <public-key-of-server>;
token = request.getCookie("session");
verify(token, publicKey);
```

Trong trường hợp này, nếu máy chủ nhận một token được ký bằng thuật toán đối xứng như HS256, phương thức verify() tổng quát của thư viện sẽ coi khóa công khai là **khóa bí mật HMAC**. Điều này có nghĩa là một kẻ tấn công có thể ký token bằng HS256 sử dụng khóa công khai, và máy chủ sẽ dùng cùng khóa công khai đó để xác minh chữ ký.

> Lưu ý
> 
> Khóa công khai mà bạn dùng để ký token **phải hoàn toàn giống** với khóa công khai được lưu trên máy chủ. Điều này bao gồm việc sử dụng cùng định dạng (chẳng hạn X.509 PEM) và giữ nguyên mọi ký tự không in được như ký tự xuống dòng. Trong thực tế, bạn có thể cần thử nghiệm với các cách định dạng khác nhau để cuộc tấn công này hoạt động.

### Thực hiện tấn công


Một cuộc tấn công nhầm lẫn thuật toán thường bao gồm các bước tổng quan sau:

- Lấy khóa công khai của máy chủ
- Chuyển đổi khóa công khai sang định dạng phù hợp
- Tạo một JWT độc hại với payload bị sửa đổi và header `alg` đặt thành `HS256`
- Ký token bằng HS256, sử dụng khóa công khai làm secret

Trong phần này, chúng ta sẽ đi qua quy trình chi tiết hơn, minh họa cách thực hiện kiểu tấn công này bằng Burp Suite.

> Lấy khóa công khai của máy chủ

Máy chủ đôi khi phơi bày khóa công khai của họ dưới dạng các đối tượng JSON Web Key (JWK) thông qua một điểm cuối chuẩn, thường được ánh xạ tới `/jwks.json` hoặc `/.well-known/jwks.json`. Các khóa này có thể được lưu trong một mảng JWK có tên là `keys`. Điều này được gọi là một **JWK Set**.

```json
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
            "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
        },
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA",
            "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ_cb33HocCuJolwDqmk6GPM4Y_qTVX67WhsN3JvaFYw-dfg6DH-asAScw"
        }
    ]
}
```
Ngay cả khi khóa không được công khai, bạn vẫn có thể trích xuất nó từ một cặp JWT hiện có.

> Chuyển đổi khóa công khai sang định dạng phù hợp

Mặc dù máy chủ có thể phơi bày khóa công khai của họ dưới dạng JWK, khi xác minh chữ ký của một token, nó sẽ dùng bản sao khóa của chính máy chủ từ hệ thống tệp cục bộ hoặc cơ sở dữ liệu. Bản sao này có thể được lưu ở định dạng khác.

Để cuộc tấn công hoạt động, phiên bản khóa mà bạn dùng để ký JWT **phải** giống hệt bản sao cục bộ của máy chủ. Ngoài việc ở cùng định dạng, **từng byte một** phải trùng khớp, bao gồm cả những ký tự không in được.

Cho ví dụ này, giả sử chúng ta cần khóa ở định dạng X.509 PEM. Bạn có thể chuyển JWK sang PEM bằng tiện ích JWT Editor trong Burp như sau:

1. Tải extension, trong thanh tab chính của Burp, vào tab **`JWT Editor` → `Keys`**.
2. Nhấn **`New RSA Key**.` Trong hộp thoại, dán JWK mà bạn đã lấy được.
3. Chọn nút radio `PEM` và sao chép khóa PEM thu được.
4. Chuyển sang tab `Decoder` và Base64-encode PEM đó.
5. Quay lại tab **`JWT Editor` → `Keys`** và nhấn **`New Symmetric Key`**.
6. Trong hộp thoại, nhấn `Generate` để tạo một khóa mới ở định dạng JWK.
7. Thay giá trị được tạo cho tham số `k` bằng khóa PEM đã được Base64 hóa mà bạn vừa sao chép.
8. Lưu khóa.

> Tạo một JWT độc hại với payload bị sửa đổi và header `alg` đặt thành `HS256`

Khi bạn đã có khóa công khai ở định dạng phù hợp, bạn có thể sửa đổi JWT theo ý muốn. Chỉ cần đảm bảo rằng header `alg` được đặt thành `HS256`.

> Ký token bằng HS256, sử dụng khóa công khai làm secret

Ký sử dụng thuật toán HS256 với khóa công khai RSA như khóa bí mật.

### **Deriving public keys from existing tokens**


Trong những trường hợp khóa công khai không có sẵn, bạn vẫn có thể thử kiểm tra lỗ hổng nhầm lẫn thuật toán bằng cách suy ra khóa từ một cặp JWT hiện có. Quá trình này tương đối đơn giản khi sử dụng các công cụ như `jwt_forgery.py`. Bạn có thể tìm công cụ này, cùng một số script hữu ích khác, trong repository **`rsa_sign2n`** trên GitHub.

Chúng tôi cũng tạo một phiên bản đơn giản hóa của công cụ này, có thể chạy bằng một lệnh duy nhất:

```
docker run --rm -it portswigger/sig2n <token1> <token2>
```

> **Lưu ý**
> 
> Bạn cần Docker CLI để chạy cả hai phiên bản của công cụ. Lần đầu chạy lệnh này, Docker sẽ tự động kéo image từ Docker Hub, có thể mất vài phút.

Công cụ sẽ sử dụng các JWT bạn cung cấp để tính toán một hoặc nhiều giá trị khả dĩ của `n`. Đừng quá bận tâm về ý nghĩa chi tiết của điều này - tất cả những gì bạn cần biết là chỉ có một trong các giá trị này khớp với giá trị `n` mà khóa của máy chủ đang sử dụng. Đối với mỗi giá trị khả dĩ, script của chúng tôi xuất ra:

- Một khóa PEM được mã hóa Base64 ở cả định dạng **X.509** và **PKCS1**.
- Một JWT giả mạo được ký bằng từng khóa trong số các khóa này.

Để xác định khóa đúng, dùng Burp Repeater gửi từng yêu cầu chứa các JWT giả mạo. Chỉ có một trong số này sẽ được máy chủ chấp nhận. Bạn sau đó có thể dùng khóa khớp đó để dựng một cuộc tấn công nhầm lẫn thuật toán.

Để biết thêm thông tin về cách quy trình này hoạt động, và chi tiết về cách sử dụng công cụ `jwt_forgery.py` chuẩn, hãy tham khảo tài liệu có trong repository.

# Bảo mật


Bạn có thể bảo vệ các trang web của mình khỏi nhiều cuộc tấn công đã nêu bằng cách thực hiện các biện pháp tổng quát sau:

- Sử dụng một thư viện xử lý JWT cập nhật và đảm bảo các nhà phát triển hiểu rõ cách hoạt động của nó cùng với mọi hệ quả bảo mật. Các thư viện hiện đại giúp bạn khó vô tình triển khai không an toàn hơn, nhưng điều này không hoàn toàn loại trừ rủi ro do tính linh hoạt vốn có của các đặc tả liên quan.
- Đảm bảo thực hiện xác minh chữ ký **mạnh mẽ** đối với mọi JWT nhận được, và tính đến các trường hợp biên như JWT được ký bằng các thuật toán không mong đợi.
- Thiết lập danh sách trắng nghiêm ngặt các host được phép cho header `jku`.
- Đảm bảo bạn không bị lộ với tấn công path traversal hoặc SQL injection qua tham số header `kid`.

# WU
- [x] JWT authentication bypass via unverified signature
- [x] JWT authentication bypass via flawed signature verification
- [x] JWT authentication bypass via weak signing secret
- [x] JWT authentication bypass via jwk header injection
- [x] JWT authentication bypass via jku header injection
- [x] JWT authentication bypass via kid header path traversal
- [x] JWT authentication bypass via algorithm confusion
- [x] JWT authentication bypass via algorithm confusion without exposed key

## JWT authentication bypass via unverified signature

- đây là lỗi cơ bản nhất khi mà backend nhận được JWT từ client (decode đê lấy thông tin user) nhưng ko verify signature.
- login bằng tài khoản wiener:peter
- trong burp, cookie session chứa chuỗi jwt (header.payload.sig)
- gửi request tới repeater (chuyển sang tab JSON token web) để đổi wiener sang administrator
![](../../image/Pasted%20image%2020260506013925.png)


![](../../image/Pasted%20image%2020260506015141.png)![[Pasted !
- gửi lại request khi đã đổi id sang administrator, ta thấy repsonse đã trả về 200, có admin panel
![[Pasted image 20260506020207.png]]
[[Pasted image 20260506015847.png]]

- cuối cùng gửi request hoặc vào web để xóa carlos
![](../../image/Pasted%20image%2020260506015816.png)

## JWT authentication bypass via flawed signature verification

- như ở bên trên trình bày, header của jwt chứa tham số alg để khai báo thuật toán tạo chữ ký. Nhưng jwt cũng có 1 thuật toán đặc biệt là `none` - ko cần chữ ký
- login vào wiener:peter, đổi alg thành none và wiener thành admin

![](../../image/Pasted%20image%2020260506023954.png)

- đã vào được panel của admin và xóa tài khoản carlos


## JWT authentication bypass via weak signing key
- jwt thường dùng thuật toán mã hóa đối xứng như HS256 để tạo chữ ký, đồng nghĩa server dùng cùng 1 khóa bí mật để ký và xác minh token.
- ta có thể bruteforce bằng từ điển để tìm khóa bí mật

- tải jwt.secret list từ link:  
`https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list`

- trên kali: chạy hashcat trên terminal:
`hashcat -a 0 -m 16500 jwt.txt(copy từ cookie của request) jwt.secret.list`
- kết quả trả về là secret1

- ở tab JWT Editor (extension trên burp), chọn new symetric key, thay k bằng giá trị base64 của `secret1` và ấn ok

-  quay trở lại repeater, sửa sub từ wiener sang administrator, ấn sign của cuối tab và chọn key vừa tạo
![](../../image/Pasted%20image%2020260506032231.png)
- bây giờ gửi request, ta đã vào được admin panel
![](../../image/Pasted%20image%2020260506032323.png)

## JWT authentication bypass via jwk header injection

- vào tab jwt editor tạo 1 khóa rsa
![](../../image/Pasted%20image%2020260506033335.png)

- ở repeater sang tab json web token, chọn sign để nhúng thêm jwk vào header
```
{  
    "kid": "4961d348-6232-41a1-8cdf-07fb868d5ef6",  
    "typ": "JWT",  
    "alg": "RS256",  
    "jwk": {  
        "kty": "RSA",  
        "e": "AQAB",  
        "kid": "4961d348-6232-41a1-8cdf-07fb868d5ef6",  
        "n": "uKYO-ol4M0qBpwnSjygUhhB6I812EP-LNjDAIPjl0M5oFGt8cPDi-HlK6YC3kP-KIMwYyTsmusr4E1Eei7z6H1dKnOj2APCnljEqmB16JaxHqjkyE48f3GdRyVQVNH2_rWYn4SEFKoDAWWDvZTdHiLfF8gShfuBPXmz9JDyGhukVJrdeXGFtGHT2QWCCjQJc315yS1-oqUhKKjGRgOKFFB4xUCZrcJPDFSohgtI7fdpQPNDJLffK73ctsnrdlLx4SablkHWcbKEV_EHa0DXnVdMrm6wLvTcYokWwBqVZq3ypDTVzv9m2ZlWyfygF2tG2JFN1LUrxJ2-VVCMoC9Pliw"  
    }  
}


```

![](../../image/Pasted%20image%2020260506034215.png)

## JWT authentication bypass via jku header injection

- tham số jku trong header của jwt được thiết kế để trỏ đến 1 đường dẫn url chứa tập hợp các khóa công khai dưới dạng jsson. máy chủ nhận token sẽ truy cập url này để tải khóa và xác minh chữ kí của token dó
- lỗ hổng xảy ra khi: máy chủ ko giới hạn danh sách tên miền tin tường cho url trong jku. kẻ tấn công có thể:
	- - Tạo một cặp khóa RSA riêng.
	- Lưu trữ khóa công khai lên một máy chủ do mình kiểm soát (Exploit Server).
	- Chèn URL dẫn đến khóa đó vào Header `jku` của JWT.
	- Máy chủ mục tiêu sẽ vô tình dùng chính khóa của kẻ tấn công để xác minh và chấp nhận token giả mạo.

- vào jwt editor để sinh 1 cặp khóa mới (rsa)
- chuột phải và copy public key as jwk
```
{
    "kty": "RSA",
    "e": "AQAB",
    "kid": "8227d72f-6354-4166-93bf-284c9139678a",
    "n": "ilCdkccHLs4p7CFMxn4AAf3cgLIQ-LSZTi72aayfdgswOVxneJmCw0_HHa_ks8H_2lJmHC5LV3v9yXqNc-_WroADqH78Un8_dsadBPIJbBuZlJEsYQlmieFQ1-JAk72NYyUUiWOxEtZVCQHNPW3drNJmWdqn1ceATy1UQc3cJRlD29--GJpvBUAT_w9f5QtS599LN92gOj3MspMBGzNxOnzCRNL7JPVCdfe07xxZZkFD9f647YW8ljhS8sqBiXlK3dufFSwaiqX_BI2m_cy9XOVg-AjmAXUp34u0c2GiMvwkLZITWYwxp28FC2nnFyBhwPrs4dDMcMXw8ghg6xqxtw"
}
```
trên trang exploit, dán public key vào mảng keys:
```
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "8227d72f-6354-4166-93bf-284c9139678a", 
            "n": "ilCdkccHLs4p7CFMxn4AAf3cgLIQ-LSZTi72aayfdgswOVxneJmCw0_HHa_ks8H_2lJmHC5LV3v9yXqNc-_WroADqH78Un8_dsadBPIJbBuZlJEsYQlmieFQ1-JAk72NYyUUiWOxEtZVCQHNPW3drNJmWdqn1ceATy1UQc3cJRlD29--GJpvBUAT_w9f5QtS599LN92gOj3MspMBGzNxOnzCRNL7JPVCdfe07xxZZkFD9f647YW8ljhS8sqBiXlK3dufFSwaiqX_BI2m_cy9XOVg-AjmAXUp34u0c2GiMvwkLZITWYwxp28FC2nnFyBhwPrs4dDMcMXw8ghg6xqxtw"
        }
    ]
}
```
- ấn stored và copy url
- trên repeater, ở json web token, thêm header jku vào, giá trị là url vừa tạo
- đổi giá trị của kid để trùng với kid của khóa vừa tạo
- ấn sign để chọn khóa rsa, cuối cùng gửi request đến admin

![](../../image/Pasted%20image%2020260506041340.png)

## JWT authentication bypass via kid header path traversal
- tham số kid trong header để chỉ định khóa nào trong 1 bộ khóa mà máy chủ nên sử dụng để xác minh chữ ký. Nhiều hệ thống lại để giá trị của kid là 1 đường dẫn đến tệp tin chứa khóa
- ở bài này, mục tiêu là path traversal thông qua tham số kid để trỏ đến 1 tệp tin trên server có nội dung cố định như /dev/null (luôn rỗng, khi đó server sẽ sử dụng 1 chuỗi rỗng, hoặc null dể làm khóa bí mật)

- vào jwt editor để gene 1 khóa đối xứng mới, xóa tham số trong trường k đi thành rỗng
- ở repeater, ở tab json web token, sửa kid thành đường dẫn deeder path traversal (nhiều chuỗi ../ để đảm bảo nó quay về thư mục gốc), đổi thành admin và sign với khóa vừa tạo

gửi request
![](../../image/Pasted%20image%2020260506042842.png)


## JWT authentication bypass via algorithm confusion
- lỗ hổng algorithm confusion xảy ra khi attacker lừa máy chủ sử dụng thaauaajttoans đối xứng để xác minh 1 token đáng lẽ phải đc ký bằng thuật toán bất đối xứng
- nếu backend lỏng lẻo, attacker sẽ đổi thuật toán từ RS256 sang HS256. lúc này server sẽ lấy khóa công khai (xác minh RS256) và dùng nó như khóa bí mật để xác minh chữ ký HS256. vì khóa công khai có thể lấy nên có thể dùng để tự kí token bằng hs256

	- thường thì các hệ thống sẽ công khai khóa của họ ở endpoint: `/jwks.json; /key'
![](../../image/Pasted%20image%2020260506044710.png)

- sinh khóa rsa mới và thay giá trị json từ khóa công khai vào
![](../../image/Pasted%20image%2020260506045142.png)

- copy public key as PEM (để máy chủ nhận diện đúng khi dùng HS256) rồi encode base64
- tạo khóa đối xứng symmetric và thay k bằng public key bên trên

- quay lại repeater, sửa alg thành HS256 và sub thành admin
![](../../image/Pasted%20image%2020260506045923.png)


## JWT authentication bypass via algorithm confusion with no exposed key
- vẫn là lỗ hổng algorithm confusion (tráo đổi rs256 và hs256). Ở bài này, hệ thống giấu khóa công, ko có endpoint nào để lấy khóa
- khóa rsa: nếu có 2 chữ kí (signature) được tạo từ 1 `Private key` kết hợp với `payload` tương ứng, có thể tính toán ra public key
- bài lab đã cung cấp tool để tính toán
`docker run --rm -it portswigger/sig2n <token1> <token2>`
![](../../image/Pasted%20image%2020260506052456.png)

- gene key đối xưng symetric rồi thay giá trị k bằng base64 encode x509 key vừa tìm được, 1 trong 3 giá trị của n sẽ là key chuẩn, cứ thử lần lượt nếu ko đúng

- vào json web token đổi alg sang HS256 và wiener sang admin, cuối cùng sign với key vừa tạo
![](../../image/Pasted%20image%2020260506053121.png)
