```table-of-contents
```
# Insecure Deserialization 

## 1. Insecure deserialization là gì?

**Serialization** là quá trình chuyển một object/dữ liệu trong bộ nhớ thành dạng có thể lưu trữ hoặc truyền đi, ví dụ chuỗi text, byte stream, cookie, session token, file cache.

**Deserialization** là quá trình ngược lại: lấy dữ liệu serialized và khôi phục lại thành object trong ứng dụng.

**Insecure deserialization** xảy ra khi ứng dụng **deserialize dữ liệu do user kiểm soát** mà không kiểm tra an toàn. Nếu attacker sửa được serialized object trước khi server deserialize, họ có thể thay đổi logic ứng dụng, leo quyền, đọc/xóa file, gây DoS, hoặc trong trường hợp nghiêm trọng là RCE.

Ví dụ đơn giản:

```text
Cookie chứa object user đã serialize:
O:4:"User":2:{s:8:"username";s:6:"wiener";s:7:"isAdmin";b:0;}
```

Nếu attacker sửa:

```text
isAdmin = false
```

thành:

```text
isAdmin = true
```

và server tin object sau khi deserialize, attacker có thể thành admin.

---

## 2. Vì sao serialization được dùng?

Ứng dụng dùng serialization để:

```text
- Lưu session hoặc trạng thái người dùng.
- Truyền object giữa client và server.
- Lưu cache.
- Truyền message giữa service.
- Lưu object vào database/file.
- Gửi object qua queue.
```

Ví dụ một website có thể lưu thông tin user trong cookie:

```json
{
  "username": "wiener",
  "isAdmin": false
}
```

Sau đó encode/base64 để đưa vào cookie:

```text
eyJ1c2VybmFtZSI6IndpZW5lciIsImlzQWRtaW4iOmZhbHNlfQ==
```

Nếu server chỉ decode và deserialize mà không xác thực tính toàn vẹn, attacker có thể sửa dữ liệu.

---

## 3. Serialization vs Deserialization

### Serialization

```text
Object trong app
→ chuyển thành chuỗi/bytes
→ lưu hoặc gửi đi
```

Ví dụ object PHP:

```php
$user = new User();
$user->username = "wiener";
$user->isAdmin = false;
```

Serialized PHP có thể giống:

```text
O:4:"User":2:{s:8:"username";s:6:"wiener";s:7:"isAdmin";b:0;}
```

### Deserialization

```text
Chuỗi/bytes
→ parse lại
→ tạo object trong app
```

Nếu input đến từ attacker, đây là điểm nguy hiểm.

---

## 4. Vấn đề bảo mật nằm ở đâu?

Lỗi không phải là “serialization” tự nó nguy hiểm, mà là:

```text
Deserialize dữ liệu không đáng tin cậy.
```

Đặc biệt nguy hiểm khi:

```text
- Serialized object nằm trong cookie, request parameter, hidden field.
- Server không ký hoặc kiểm tra integrity.
- Object chứa property ảnh hưởng đến quyền hạn hoặc luồng logic.
- Ngôn ngữ/framework tự động gọi magic method khi deserialize.
- Trong codebase có gadget chain có thể bị lạm dụng.
```

---

## 5. Impact thường gặp

Insecure deserialization có thể dẫn đến:

```text
- Authentication bypass
- Privilege escalation
- Access control bypass
- Thay đổi trạng thái object
- Arbitrary file read/write/delete
- Denial of Service
- Server-side request forgery trong một số chain
- Remote Code Execution nếu có gadget chain phù hợp
```

Không phải lab nào cũng RCE. Nhiều lab chỉ cần sửa field logic như `isAdmin`, `role`, `user_id`, `avatar_link`, `deleteToken`.

---

## 6. Dấu hiệu nhận biết serialized data

Khi kiểm thử, chú ý các vị trí:

```text
- Cookie
- Session token
- Request parameter
- Hidden input
- JSON body
- Header tùy chỉnh
- URL parameter dài bất thường
- Base64 blob
- File upload metadata
```

Một số dấu hiệu theo ngôn ngữ:

### PHP serialized object

```text
O:4:"User":2:{s:8:"username";s:6:"wiener";s:7:"isAdmin";b:0;}
```

Các ký hiệu hay gặp:

```text
O:<len>:"ClassName":<property_count>:{...}   object
a:<count>:{...}                              array
s:<len>:"text";                              string
i:<number>;                                  integer
b:0; / b:1;                                  boolean
N;                                           null
```

### Java serialized object

Java serialized stream thường bắt đầu bằng magic bytes:

```text
AC ED 00 05
```

Nếu base64 encode, có thể bắt đầu bằng:

```text
rO0AB
```

### Python pickle

Có thể thấy bytes hoặc base64 blob liên quan đến pickle. Pickle rất nguy hiểm nếu deserialize dữ liệu không tin cậy.

### .NET

Có thể gặp ViewState hoặc BinaryFormatter/NrBF payload. Một số hệ thống cũ dùng BinaryFormatter rất nguy hiểm.

---

## 7. Kỹ thuật 1 — Sửa thuộc tính object

Đây là kỹ thuật cơ bản nhất trong các lab.

Ví dụ serialized object chứa:

```text
username = wiener
isAdmin = false
```

Attacker sửa thành:

```text
username = wiener
isAdmin = true
```

Nếu server deserialize và dùng object này để quyết định quyền:

```php
if ($user->isAdmin) {
    showAdminPanel();
}
```

thì attacker leo quyền.

### Cốt lõi

```text
Server tin trạng thái object do client gửi.
```

### Writeup mẫu ngắn

```text
Ứng dụng lưu object user đã serialize trong cookie. Tôi decode cookie và thấy property `isAdmin=false`. Sau khi sửa thành `isAdmin=true`, encode lại và gửi request, server deserialize object đã bị sửa và cấp quyền admin. Lỗi nằm ở việc server tin dữ liệu serialized do client kiểm soát mà không kiểm tra integrity.
```

---

## 8. Kỹ thuật 2 — Sửa kiểu dữ liệu

Một số ngôn ngữ có so sánh lỏng. Ví dụ PHP có loose comparison:

```php
if ($user->token == $storedToken) {
    login();
}
```

Nếu attacker thay token string bằng integer hoặc boolean, có thể bypass trong một số điều kiện.

Ví dụ ý tưởng:

```text
token = "abc123"
```

thành:

```text
token = 0
```

Nếu code dùng `==` thay vì `===`, có thể xảy ra so sánh sai.

### Cốt lõi

```text
Không chỉ sửa value, attacker còn sửa được type.
```

### Phòng chống

```text
- Dùng strict comparison.
- Validate schema sau khi deserialize.
- Không tin type lấy từ serialized object.
```

---

## 9. Kỹ thuật 3 — Lạm dụng chức năng hợp lệ của ứng dụng

Ngay cả khi không RCE, attacker có thể thay đổi object để khiến ứng dụng gọi chức năng nguy hiểm.

Ví dụ object có property:

```text
avatar = "/home/wiener/avatar.png"
```

Server có chức năng xóa avatar cũ khi user đổi avatar. Nếu attacker sửa:

```text
avatar = "/home/carlos/morale.txt"
```

Khi object bị xử lý, server có thể xóa file của Carlos.

### Cốt lõi

```text
Không cần code execution.
Chỉ cần ép ứng dụng dùng dữ liệu object đã sửa trong chức năng có sẵn.
```

---

## 10. Magic methods là gì?

Nhiều ngôn ngữ có các method đặc biệt tự chạy trong một số thời điểm.

### PHP

Một số magic method quan trọng:

```text
__wakeup()      chạy khi unserialize()
__destruct()    chạy khi object bị hủy
__toString()    chạy khi object bị convert sang string
__call()        chạy khi gọi method không tồn tại
```

Ví dụ:

```php
class User {
    public $file;

    function __destruct() {
        unlink($this->file);
    }
}
```

Nếu attacker kiểm soát `$file`, khi object bị hủy, file có thể bị xóa.

### Java

Java có các method liên quan deserialization như:

```text
readObject()
readResolve()
```

Một số class trong thư viện có thể bị lạm dụng trong gadget chain.

---

## 11. Gadget là gì?

**Gadget** là một đoạn code/class/method có sẵn trong ứng dụng hoặc thư viện, có thể bị attacker lạm dụng khi deserialize.

Một gadget đơn lẻ có thể chưa đủ nguy hiểm, nhưng nhiều gadget nối lại thành **gadget chain**.

Ví dụ ý tưởng:

```text
Gadget 1: __destruct() gọi method A
Gadget 2: method A đọc property attacker kiểm soát
Gadget 3: property đó đi vào file operation / command / template / eval
```

### Gadget chain / POP chain

Trong PHP, người ta hay gọi là **POP chain** — Property-Oriented Programming. Attacker không inject code trực tiếp, mà sắp xếp các property object để các magic method có sẵn tự gọi nhau theo hướng có lợi cho attacker.

### Cốt lõi

```text
Vulnerability = deserialize user-controllable data.
Gadget chain = phương tiện để biến vulnerability thành impact.
```

---

## 12. PHP deserialization format cơ bản

Ví dụ object:

```php
class User {
    public $username = "wiener";
    public $isAdmin = false;
}
```

Serialized:

```text
O:4:"User":2:{s:8:"username";s:6:"wiener";s:7:"isAdmin";b:0;}
```

Giải thích:

```text
O:4:"User"      object class User, tên class dài 4 ký tự
2               có 2 property
s:8:"username"  string dài 8
s:6:"wiener"    string dài 6
s:7:"isAdmin"   string dài 7
b:0             boolean false
```

Nếu sửa độ dài string, phải sửa đúng số length.

Ví dụ:

```text
s:6:"wiener"
```

Nếu đổi thành:

```text
administrator
```

phải thành:

```text
s:13:"administrator"
```

Sai length có thể làm unserialize fail.

---

## 13. PHP magic method example

Ví dụ nguy hiểm:

```php
class CustomTemplate {
    public $template_file_path;

    function __destruct() {
        unlink($this->template_file_path);
    }
}
```

Payload ý tưởng:

```text
O:14:"CustomTemplate":1:{s:18:"template_file_path";s:24:"/home/carlos/morale.txt";}
```

Khi object bị hủy, `__destruct()` chạy và xóa file.

---

## 14. PHAR deserialization là gì?

Trong PHP, PHAR archive có thể chứa metadata đã serialize. Một số function xử lý file như `file_exists()`, `fopen()`, `exif_read_data()` có thể trigger đọc metadata khi path dùng wrapper:

```text
phar://...
```

Nếu ứng dụng upload file và sau đó gọi file operation trên path do user kiểm soát, attacker có thể lợi dụng PHAR metadata để trigger deserialization.

### Cốt lõi

```text
Không cần gọi unserialize() trực tiếp.
Một số luồng file operation có thể gián tiếp trigger deserialization qua PHAR metadata.
```

---

## 15. Java deserialization

Java native serialization dùng `ObjectInputStream.readObject()` để deserialize object.

Dấu hiệu:

```text
AC ED 00 05
rO0AB...
```

Nếu Java app deserialize dữ liệu user kiểm soát và classpath có gadget chain phù hợp, attacker có thể RCE.

### ysoserial

`ysoserial` là tool tạo Java deserialization payload dựa trên gadget chain đã biết. Trong lab/CTF, nó thường dùng để tạo payload gọi command.

Ví dụ ý tưởng trong môi trường lab:

```bash
java -jar ysoserial-all.jar CommonsCollections4 'touch /tmp/pwned' > payload.bin
```

Lưu ý:

```text
- Chỉ dùng trong lab hoặc hệ thống có ủy quyền.
- Gadget chain phụ thuộc vào thư viện có trong classpath của target.
- Không phải cứ Java deserialization là tự động RCE.
```

---

## 16. Các bước kiểm thử Insecure Deserialization

### Bước 1 — Tìm serialized data

Tìm trong:

```text
- Cookies
- Parameters
- Hidden fields
- Authorization/session tokens
- Base64 blobs
- Request bodies
```

Dấu hiệu:

```text
O:...        PHP object
a:...        PHP array
rO0AB        Java serialized base64
AC ED 00 05  Java serialized bytes
```

### Bước 2 — Decode

Dùng Burp Decoder hoặc Hackvertor để:

```text
- URL decode
- Base64 decode
- Gzip decompress nếu có
- Hex decode nếu cần
```

### Bước 3 — Sửa field đơn giản

Thử sửa:

```text
isAdmin=false → true
role=user → admin
user_id=123 → 1
price=100 → 0
```

### Bước 4 — Encode lại đúng format

Nếu PHP serialized string, nhớ sửa length.

Nếu có base64, encode lại.

Nếu có URL encoding, encode lại.

### Bước 5 — Kiểm tra integrity/signature

Nếu dữ liệu có dạng:

```text
payload.signature
```

hoặc cookie có HMAC, sửa payload có thể fail. Khi đó cần tìm lỗi khác như:

```text
- Secret yếu
- Algorithm confusion
- key leak
- signed but still dangerous if server signs attacker-controlled object
```

### Bước 6 — Tìm gadget/magic method

Nếu có source code, tìm:

```text
__wakeup
__destruct
__toString
readObject
ObjectInputStream
unserialize
pickle.loads
BinaryFormatter.Deserialize
```

Tìm property đi vào sink:

```text
file path
command
template
SQL
URL
redirect
include/require
delete/read/write file
```

---

## 17. Tools hữu ích

### Burp Suite

```text
- Proxy HTTP history
- Repeater
- Decoder
- Comparer
- Intruder
- Scanner trong Burp Pro
```

### Hackvertor

Hữu ích để tự động encode/decode nhiều lớp trong Burp.

### PHPGGC

Tool tạo payload PHP gadget chain cho các framework/thư viện phổ biến.

Ví dụ ý tưởng:

```bash
phpggc Laravel/RCE1 system 'id'
```

### ysoserial

Tool tạo payload Java deserialization cho lab Java.

### SerializationDumper

Dùng để inspect Java serialized stream.

---

## 18. Các lỗi thường gặp khi làm lab

### 18.1 Quên sửa string length PHP

Sai:

```text
s:6:"wiener"
```

nhưng đổi thành:

```text
s:13:"administrator"
```

mà vẫn giữ `s:6`.

### 18.2 Sửa đúng nhưng quên encode lại

Ví dụ cookie ban đầu base64 + URL encode. Sau khi sửa phải encode lại đúng thứ tự.

### 18.3 Payload bị signature chặn

Nếu dữ liệu được ký HMAC đúng cách, sửa payload sẽ bị phát hiện.

### 18.4 Nhầm giữa exploit local và victim

Một số lab yêu cầu exploit chạy trong context victim hoặc admin. Chạy payload trên tài khoản mình chưa đủ.

### 18.5 Gadget chain không tồn tại

RCE payload chỉ chạy nếu target có đúng class/library gadget.

---

## 19. Phòng chống Insecure Deserialization

### 19.1 Không deserialize dữ liệu không tin cậy

Cách tốt nhất:

```text
Không bao giờ deserialize object từ user input nếu không thật sự cần.
```

Thay object serialization bằng format dữ liệu đơn giản hơn:

```text
JSON schema rõ ràng
Primitive values
Server-side session storage
```

### 19.2 Ký dữ liệu serialized

Nếu bắt buộc gửi serialized data cho client, phải dùng HMAC/signature để kiểm tra integrity.

Ví dụ:

```text
payload = base64(serialized_data)
signature = HMAC(secret, payload)
cookie = payload.signature
```

Server phải verify signature trước khi deserialize.

Lưu ý:

```text
Mã hóa không thay thế được integrity.
Encryption without authentication vẫn có thể nguy hiểm.
```

### 19.3 Validate schema sau khi parse

Chỉ cho phép property hợp lệ:

```text
username: string
user_id: integer
role: enum(user, admin)
```

Reject object/class ngoài allowlist.

### 19.4 Không deserialize arbitrary class

Một số framework cho phép allowlist class khi deserialize. Nên chỉ cho phép class cần thiết.

### 19.5 Tránh magic method nguy hiểm

Không để magic method thực hiện hành động nguy hiểm dựa trên property có thể kiểm soát:

```text
delete file
execute command
include template
make HTTP request
write arbitrary path
```

### 19.6 Cập nhật dependency

Nhiều gadget chain đến từ thư viện. Cập nhật dependency giúp giảm gadget đã biết, nhưng không thay thế việc fix deserialization source.

### 19.7 Giám sát và logging

Log các dấu hiệu bất thường:

```text
- Serialized payload lạ
- Class name lạ
- Base64 blob bất thường
- Deserialize error
- Magic method exception
```

---

## 20. Checklist học/làm lab

```text
1. Tìm serialized data.
2. Decode và xác định format/ngôn ngữ.
3. Sửa field đơn giản để kiểm tra server có tin object không.
4. Nếu PHP, sửa đúng string length.
5. Nếu có signature, kiểm tra có bypass/secret leak không.
6. Tìm magic method/gadget nếu có source code.
7. Xác định impact: privilege escalation, file operation, RCE.
8. Encode lại đúng định dạng.
9. Gửi request qua Repeater.
10. Viết writeup theo Source → Deserialization → Manipulation/Gadget → Impact.
```

---

## 21. Mẫu writeup chung

```text
Ứng dụng sử dụng serialized object trong cookie/request để lưu trạng thái người dùng. Tôi decode giá trị này và phát hiện các property có ảnh hưởng đến logic ứng dụng, ví dụ `isAdmin` hoặc `user_id`.

Do serialized object nằm ở phía client và không được bảo vệ bằng integrity check, tôi có thể sửa property rồi encode lại. Khi server nhận request, nó deserialize object đã bị sửa và sử dụng các property này để quyết định quyền truy cập. Kết quả là tôi thay đổi được hành vi ứng dụng, dẫn đến [impact].

Nguyên nhân gốc rễ là server deserialize dữ liệu do người dùng kiểm soát và tin tưởng trạng thái object sau khi deserialize. Cách khắc phục là không deserialize dữ liệu không tin cậy, hoặc ít nhất phải ký dữ liệu bằng HMAC, validate schema nghiêm ngặt và tránh magic method/gadget nguy hiểm.
```

---

## 22. Tóm tắt cực ngắn

```text
Insecure deserialization = server deserialize dữ liệu attacker sửa được.
```

Công thức khai thác:

```text
Serialized object do user kiểm soát
→ sửa property/type/class
→ server deserialize
→ app dùng object đã sửa
→ bypass / leo quyền / file operation / RCE
```

Công thức phòng chống:

```text
Không deserialize untrusted data
+ ký integrity bằng HMAC
+ validate schema/class allowlist
+ tránh magic method nguy hiểm
+ cập nhật dependency
```


# WU
- [ ] Modifying serialized objects
- [ ] Modifying serialized data types
- [ ] Using application functionality to exploit insecure deserialization
- [ ] Arbitrary object injection in PHP
- [ ] Exploiting Java deserialization with Apache Commons
- [ ] Exploiting PHP deserialization with a pre-built gadget chain
- [ ] Exploiting Ruby deserialization using a documented gadget chain
- [ ] Developing a custom gadget chain for Java deserialization
- [ ] Developing a custom gadget chain for PHP deserialization
- [ ] Using PHAR deserialization to deploy a custom gadget chain

## Modifying serialized objects
- mục tiêu là sửa serialized objec trong session cookie để đổi quyền admin từ false sang true
sau khi login, bắt request trong burp
![[Pasted image 20260517081729.png]]
ở cookie, giá trị thường đc url encode + base64 encode

- decode giá trị
![[Pasted image 20260517081819.png]]
có thể thấy là giá trị admin boolean = 0 nghĩa là false, sửa 0 thành 1

- vào web đổi cookie session sang giá trị mới hoặc gửi lại request, ta đã vào được admin panel
![[Pasted image 20260517082312.png]]

## Modifying serialized data types
- mục tiêu là Khai thác insecure deserialization bằng cách **đổi kiểu dữ liệu** trong serialized object để bypass kiểm tra mật khẩu/authorization, sau đó xóa user carlos
- tương tự, giá trị cookie lần nãy cũng là chuỗi kí tự
![[Pasted image 20260517082601.png]]

, vậy cần đổi username sang administartor, và 6 thành 13 kí tự ,
access_token từ string sang integer
`s:12:"access_token";s:32:"abc123...";`
sang `s:12:"access_token";i:0;`
![[Pasted image 20260517082832.png]]


- sau đó đổi giá trị cookie trong web
![[Pasted image 20260517082846.png]]

## Using application functionality to exploit insecure deserialization
- mục tiêu là khai thác insecure deserialization bằng cách **sửa property trong serialized object**, rồi lợi dụng chức năng hợp lệ của ứng dụng để xóa file: morale.txt
giá trị cookie lần này dài hơn
![[Pasted image 20260517083119.png]]
chú ý đến phần avatar link
ta có thể sửa đổi path thành /home/carlos/morale.txt và độ dài từ 19 lên 23

- sau khi sửa xong vào web để đổi cookie sang cookie mới
![[Pasted image 20260517083331.png]]
vì ta đã sủa avatar link sang path tới file nên khi delete account thì wweb sẽ xóa avatar hiện tại tức là xóa file morale.txt

## Arbitrary object injection in PHP

- mục tiêu là Tạo serialized object của class có sẵn trong source code để lợi dụng magic method PHP, từ đó xóa file morale.txt
giá trị cookie ở đây

![[Pasted image 20260517083534.png]]

object sang php serialized, ta ko chỉ sửa object user mà cần injection object khác có trong source code

=> cần tìm source code bị leak
![[Pasted image 20260517083703.png]]

![[Pasted image 20260517083828.png]]
- hàm destruct() tự chạy khi object bị hủy unlink() xóa file theo template_file_bath

ta cần tạo object CustomTemplate với property:  `template_file_path = /home/carlos/morale.txt`
thay toàn bộ giá trị cookie
```
O:14:"CustomTemplate"       object class CustomTemplate, tên dài 14 ký tự
1                           có 1 property
s:18:"template_file_path"   tên property dài 18 ký tự
s:23:"/home/carlos/morale.txt"  path dài 23 ký tự
```
![[Pasted image 20260517084136.png]]

![[Pasted image 20260517084118.png]]
khi server nhận cookie
```
server unserialize(cookie)
→ tạo object CustomTemplate
→ cuối request object bị hủy
→ __destruct() chạy
→ unlink('/home/carlos/morale.txt')
```
## gọi là arbitrary object injection?
Vì attacker không chỉ sửa property của object có sẵn, mà có thể tự chỉ định class object được tạo khi server `unserialize()`.
Thay vì object `User`, ta inject object:
```
CustomTemplate
```
Miễn là class này tồn tại trong codebase, PHP có thể khởi tạo nó khi unserialize.
Sau đó magic method:
```
__destruct()
```
tự động chạy và gây impact
Vì attacker không chỉ sửa property của object có sẵn, mà có thể tự chỉ định class object được tạo khi server `unserialize()`.
Thay vì object `User`, ta inject object:
```
CustomTemplate
```
Miễn là class này tồn tại trong codebase, PHP có thể khởi tạo nó khi unserialize.
Sau đó magic method:
```
__destruct()
```
tự động chạy và gây impact

## Exploiting Java deserialization with Apache Commons
- muc jtieeu là khai thác java deserialization bằng gadget chain Apache common collection để xóa fiele morale.txt

## Exploiting PHP deserialization with a pre-built gadget chain
- muc jtieeu là 

## Exploiting Ruby deserialization using a documented gadget chain

- mục tiêu là xóa morale.txt, lab này dùng **Ruby Marshal deserialization** và một **documented gadget chain** để RCE
