#!/usr/local/bin/python3.10
import cgi
import cgitb
import os
import sys
import json


cgitb.enable()

status_code = {
    400: ["Bad Request", "一時的にエラーが発生しています。"],
    403: ["Forbidden", "このページを見る権限がありません。"],
    404: ["Not Found", "ページが見つかりませんでした。"],
    408: ["Request Timeout", "時間がかかりすぎました。"],
    423: ["Locked", "このページは編集中です。"],
    425: ["Too Early", "ページで繰り返し処理が発生すると判断しました。"],
    426: ["Upgrade Required", "HTTP/1.1へのアップデートが必要です。"],
    429: ["Too Many Requests", "サーバーダウンを防ぐため、アクセスを一時的に拒否しました。"],
    431: ["Request Header Fields Too Large", "リクエストヘッダーが長すぎます。"],
    500: ["Internal Server Error", "サーバー内でエラーが発生しました。"],
    503: ["Service Unavailable", "一時的にサーバーにアクセスできません。"],
    511: ["Network Authentication Required", "ネットワーク認証が必要です。"]
}


def status(statuscode):
    statuscode = int(statuscode)
    if statuscode in list(status_code.keys()):
        return status_code[statuscode]
    else:
        return ["Error", "ページまたはサーバーでエラーが発生しました。"]

print("Content-Type: text/html; charset=UTF-8")
print()

if "REDIRECT_STATUS" not in list(os.environ):
    print("""\
    <html>
        <head>
            <meta charset="utf-8" />
            <script>
                location.replace("/");
            </script>
        </head>
    </html>
    """)
else:
    print(f"""\
<html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="/sprite/guild_icon.png">
        <meta content="Arkプレイヤーの集い" property="og:title" />
        <meta content="Steam版の非公式サーバー運営中 MB/CS大歓迎" property="og:description" />
        <meta content="http://ark-tsudoi.f5.si/" property="og:url" />
        <meta content="/sprite/guild_icon.png" property="og:image" />
        <meta content="#409fff" data-react-helmet="true" name="theme-color" />
        <title>Arkプレイヤーの集い</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c&family=Noto+Sans+JP&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/style/body.css">
        <link rel="stylesheet" href="/style/header.css">
    </head>
    <body>
        <header id="header">
            <div class="logo"><a href="/">Arkプレイヤーの集い</a></div>
        </header>
        <hr class="content_border">
        <div id="root">
            <center>
                <h3>{os.environ["REDIRECT_STATUS"]} - {status(os.environ["REDIRECT_STATUS"])[0]}</h3>
                <div>{status(os.environ["REDIRECT_STATUS"])[1]}</div>
                <div>10秒後に自動的にTOPに戻ります。</div>
            <center>
        </div>
""" + """
        <script>
            setTimeout("link()", 10000);

            function link(){
                location.replace("/");
            }
        </script>
    </body>
</html>
""")
