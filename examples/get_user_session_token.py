from __future__ import annotations

import cgi
import json
import logging
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

API_ROOT = "https://api.revolt.chat"
HTML_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>Get Revolt Session Token</title>
    <script src="https://js.hcaptcha.com/1/api.js" async="async" defer="defer"></script>
  </head>
  <body>
    <form method="post">
      <input type="text" name="device_name" placeholder="Device name"
        required="required" />
      <br />
      <input type="text" name="email" placeholder="Email" required="required" />
      <br />
      <input type="password" name="password" placeholder="Password"
        required="required" />
      <div class="h-captcha" data-sitekey="{captcha_key}"></div>
      <br />
      <input type="submit" value="Submit" />
    </form>
  </body>
</html>
""".strip()


def _get_captcha_key() -> str:
    with urllib.request.urlopen(f"{API_ROOT}") as f:
        data = json.loads(f.read().decode())
    return data["features"]["captcha"]["key"]


def _create_session(post_vars: dict[str, Any]) -> dict[str, Any]:
    request_data = {
        "email": post_vars["email"],
        "password": post_vars["password"],
        "device_name": post_vars["device_name"],
        "captcha": post_vars["h-captcha-response"],
    }
    request = urllib.request.Request(
        f"{API_ROOT}/auth/session/login",
        data=json.dumps(request_data).encode(),
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(request) as f:
        data = json.loads(f.read().decode())
    return {"session_token": data["session_token"]}


class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self) -> None:
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()

    def do_GET(self) -> None:
        captcha_key = _get_captcha_key()
        self._set_response()
        self.wfile.write(HTML_TEMPLATE.format(captcha_key=captcha_key).encode())

    def do_POST(self) -> None:
        content_type, pdict = cgi.parse_header(self.headers["content-type"])
        if content_type != "application/x-www-form-urlencoded":
            self.send_response(400)
            self.send_header("content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bad Request")
            return

        content_length = int(self.headers["content-length"])
        post_vars = dict(
            urllib.parse.parse_qsl(self.rfile.read(content_length).decode())
        )
        session_data = _create_session(post_vars)

        self._set_response()
        self.wfile.write(json.dumps(session_data).encode())


class Server(HTTPServer):
    def server_activate(self) -> None:
        super().server_activate()
        webbrowser.open_new_tab("http://127.0.0.1:8000")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    server = Server(("", 8000), RequestHandler)
    logging.info("Starting server...\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logging.info("Stopping server...\n")


if __name__ == "__main__":
    main()
