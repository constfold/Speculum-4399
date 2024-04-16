import requests
import json

from http.server import BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def __init__(self, base_url):
        self.base_url = base_url

    def do_GET(self):
        if self.path.endswith(".swf"):
            try:
                response = requests.get(
                    self.base_url + self.path,
                    headers={"Referer": "http://www.4399.com"},
                )
            except:
                self.send_response(500)
                return
            self.send_response(200)
            self.wfile.write(response.content)
        else:
            # TODO: Serve other resources
            pass

    def do_POST(self):
        # TODO: Handle POST requests
        pass
