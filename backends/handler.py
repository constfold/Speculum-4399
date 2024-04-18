import logging
import re
import requests
import json
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path

from http.server import BaseHTTPRequestHandler

from backends.private import *
from backends.annotation import handle, HANDLERS


@handle("get", "", r"(?P<path>.+?\.swf)")
def swf(self, query, path):
    logging.info(f"GET SWF {path}")
    cache_dir = (Path("out") / "cache").resolve()
    cache_path = cache_dir.joinpath(path.strip("/")).resolve()
    assert cache_path.is_relative_to(cache_dir), f"{cache_path} not in {cache_dir}"

    if cache_path.exists():
        logging.info(f"Cache hit {cache_path}")
        self.send_response(200)
        self.wfile.write(cache_path.read_bytes())
        return
    try:
        response = requests.get(
            self.base_url + path,
            headers={"Referer": "http://www.4399.com"},
        )
    except Exception as e:
        logging.error(f"Failed to fetch {path}: {e}")
        self.send_response(500)
        return

    logging.info(f"Caching {path} to {cache_path}")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(response.content)

    self.send_response(200)
    self.wfile.write(response.content)


@handle("get", "cdn.comment.4399pk.com", r"/control/ctrl_mo_v5.swf")
def control_swf(self, query):
    self.send_response(418)


@handle("get", "stat.api.4399.com", r"/flash_ctrl_version.xml")
def control_version_xml(self, query):
    self.send_response(418)


class SpeculumHandler(BaseHTTPRequestHandler):
    def __init__(self, base_url, *args, **kwargs):
        self.base_url = base_url
        super().__init__(*args, **kwargs)

    def do_GET(self):
        url = urlparse(self.path.replace("/http:", "http:"))
        query = parse_qs(url.query)
        handlers = HANDLERS["get"].get(url.netloc, [])
        for handler in handlers:
            match = handler["pattern"].match(url.path)
            if match:
                handler["handler"](self, query, **match.groupdict())
                return
        logging.error(f"Unhandled GET {url.geturl()}")
        self.send_response(404)

    def do_POST(self):
        url = urlparse(
            self.path.replace("/http:", "http:").replace("/https:", "https:")
        )
        data = self.rfile.read(int(self.headers["Content-Length"]))
        if self.headers.get("Content-Type") == "application/json":
            data = json.loads(data)
        elif self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
            data = parse_qs(data.decode())

        handlers = HANDLERS["post"].get(url.netloc, [])
        for handler in handlers:
            match = handler["pattern"].match(url.path)
            if match:
                handler["handler"](self, data, **match.groupdict())
                return
        logging.error(f"Unhandled POST {url.geturl()}")
        self.send_response(404)
