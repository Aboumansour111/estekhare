import html
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = 27461
DATA_FILE = "/opt/estekhare/quran_pages.json"
INDEX_FILE = "/opt/estekhare/index.html"


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, typ):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", typ + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)

        if u.path == "/":
            with open(INDEX_FILE, encoding="utf-8") as f:
                return self.send(200, f.read(), "text/html")

        if u.path == "/health":
            return self.send(200, '{"status":"ok"}', "application/json")

        if u.path in ("/result", "/api/result"):
            try:
                query = urllib.parse.parse_qs(u.query)
                page = int(query.get("page", [""])[0])
                if not 1 <= page <= 603:
                    raise ValueError("شماره صفحه باید بین ۱ تا ۶۰۳ باشد.")

                with open(DATA_FILE, encoding="utf-8") as f:
                    database = json.load(f)

                result = database["pages"].get(str(page))
                if not result:
                    raise ValueError("اطلاعات این صفحه موجود نیست.")

                if u.path == "/api/result":
                    return self.send(
                        200,
                        json.dumps(result, ensure_ascii=False),
                        "application/json"
                    )

                p = html.escape(str(result["page"]).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")))
                surah = html.escape(result["surah"])
                ayah = html.escape(str(result["ayah"]))
                text = html.escape(result["text"].lstrip("\ufeff"))

                page_html = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>صفحه {p} قرآن</title>
<style>
body{{margin:0;background:#eef3ed;color:#26382c;font-family:Tahoma,Arial;line-height:2}}
main{{max-width:700px;margin:30px auto;padding:14px}}
article{{background:white;border:1px solid #dce5db;border-radius:16px;padding:24px}}
h1{{text-align:center;color:#245b40;font-size:25px}}
.meta{{text-align:center;color:#536858}}
.verse{{font-family:serif;font-size:27px;line-height:2.3;text-align:justify;margin:30px 0;color:#202e23}}
a{{display:block;text-align:center;background:#245b40;color:white;text-decoration:none;padding:10px;border-radius:9px}}
</style>
</head>
<body><main><article>
<h1>صفحه {p} قرآن</h1>
<div class="meta">سوره {surah} ـ آیه {ayah}</div>
<div class="verse" lang="ar" dir="rtl">{text}</div>
<a href="/">بازگشت به انتخاب صفحه</a>
</article></main></body></html>"""
                return self.send(200, page_html, "text/html")

            except (ValueError, KeyError, OSError, json.JSONDecodeError) as e:
                return self.send(
                    400,
                    json.dumps({"error": str(e)}, ensure_ascii=False),
                    "application/json"
                )

        return self.send(404, "Not found", "text/plain")

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


if __name__ == "__main__":
    print(f"Listening on {HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
