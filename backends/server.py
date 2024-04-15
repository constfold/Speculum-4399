import requests
import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import dotenv_values

from .. import buildswf

config = {**dotenv_values(".env")}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith(".swf"):
            try:
                response = requests.get("http://localhost:8080")
            except:
                self.send_response(500)
                return
            self.send_response(200)
            self.wfile.write(response.content)
        else:
            pass


with HTTPServer((config["BACKEND_ADDR"], config["BACKEND_PORT"]), Handler) as httpd:
    httpd.serve_forever()
