import logging
import os
import random
from time import sleep
import requests
import json
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path

from http.server import BaseHTTPRequestHandler

from backends.private import *
from backends.annotation import handle, HANDLERS

from speculum.swfutil import SWFUtil


@handle("get", "", r"(?P<path>.+?\.swf)")
def swf(self: BaseHTTPRequestHandler, query, path):
    logging.info(f"GET SWF {path}")
    cache_dir = (Path("out") / "cache").resolve()
    cache_path = cache_dir.joinpath(path.strip("/")).resolve()
    assert cache_path.is_relative_to(cache_dir), f"{cache_path} not in {cache_dir}"

    if self.no_cache or not cache_path.exists():
        logging.info(f"Downloading at {self.base_url + path}")
        retry = 3
        while True:
            try:
                response = requests.get(
                    self.base_url + path,
                    headers={"Referer": "http://www.4399.com"},
                )
                response.raise_for_status()
                break
            except Exception as e:
                logging.warning(f"Failed to fetch {path}: {e}")
                retry -= 1
                logging.info(f"Retry {retry} times")
                if retry == 0:
                    self.send_response(500)
                    logging.error(f"Failed to fetch {path}")
                    return

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if self.inject_nested:
            logging.info(f"Processing {path} to {cache_path}")
            rawfile = cache_path.with_suffix(".raw" + cache_path.suffix)
            rawfile.write_bytes(response.content)

            merged_file = cache_path.with_suffix(".merged" + cache_path.suffix)
            util = SWFUtil(os.environ["FLEX_PATH"])
            util.merge(rawfile, Path("out") / "_Interceptor.swf", merged_file)
            util.inject(merged_file, cache_path)
        else:
            cache_path.write_bytes(response.content)
    else:
        logging.info(f"Cache hit {path}")

    logging.info(f"Cache {cache_path}")
    data = cache_path.read_bytes()
    self.send_response(200)
    self.send_header("Content-Type", "application/x-shockwave-flash")
    self.send_header("Content-Length", len(data))
    self.end_headers()
    self.wfile.write(data)


@handle("get", "cdn.comment.4399pk.com", r"/control/ctrl_mo_v5.swf")
def control_swf(self, query):
    self.send_response(418)
    self.end_headers()


@handle("get", "stat.api.4399.com", r"/flash_ctrl_version.xml")
def control_version_xml(self, query):
    self.send_response(418)
    self.end_headers()


@handle("get", "stat.api.4399.com", r"/archive_statistics/log.js")
def archive_statistics_log_js(self, query):
    self.send_response(200)


@handle("get", "save.api.4399.com", r"/index\.php")
def save_index(self, query):
    logging.info(f"GET /save/index, {query=}")
    if query.get("c") == ["realname"] and query.get("ac") == ["status"]:
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            json.dumps({"success": 1, "cert": 1, "reconfirm": 0, "status": 1}).encode()
        )
    else:
        self.send_response(404)
        self.end_headers()


@handle("get", "api.speculum.fake", r"/save/get/(?P<index>\d+)")
def save_get(self, query, index):
    logging.info(f"GET /save/get, {index=}")
    game_save = Path("out") / "game_save.json"
    if game_save.exists():
        save = json.loads(game_save.read_text(encoding="utf-8"))["saves"][int(index)]
    else:
        save = None

    self.send_response(200)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.end_headers()
    self.wfile.write(json.dumps({"data": save}).encode())


@handle("post", "api.speculum.fake", r"/save/save")
def save_save(self, data):
    logging.info("POST /save/save")
    game_save = Path("out") / "game_save.json"
    if game_save.exists():
        saves = json.loads(game_save.read_text(encoding="utf-8"))
    else:
        saves = {"saves": [None] * 7}

    saves["saves"][data["index"]] = data
    game_save.write_text(json.dumps(saves), encoding="utf-8")
    self.send_response(200)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.end_headers()
    self.wfile.write(json.dumps({"success": 1}).encode())


@handle("get", "api.speculum.fake", r"/save/list")
def save_list(self, query):
    logging.info("GET /save/list")
    game_save = Path("out") / "game_save.json"
    if game_save.exists():
        saves = json.loads(game_save.read_text(encoding="utf-8"))["saves"]
    else:
        saves = [None] * 7

    self.send_response(200)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.end_headers()
    self.wfile.write(json.dumps(saves).encode())


class SpeculumHandler(BaseHTTPRequestHandler):
    def __init__(self, base_url, no_cache, inject_nested, *args, **kwargs):
        self.base_url = base_url
        self.no_cache = no_cache
        self.inject_nested = inject_nested
        super().__init__(*args, **kwargs)

    def normalize_url(self):
        """
        Normalize the URL to handle different URL formats

        Examples:
        - `/http://example.com` -> `http://example.com`
        - `/https://example.com` -> `https://example.com`
        - `//example.com` -> `http://example.com`
        - `/abc.swf` -> `/abc.swf`
        """
        path = unquote(self.path.removeprefix("/+"))

        self.url = urlparse(path)
        logging.debug(f"Normalized {self.path} to {repr(self.url)}")

    def do_GET(self):
        self.normalize_url()
        query = parse_qs(self.url.query)
        handlers = HANDLERS["get"].get(self.url.netloc, [])
        for handler in handlers:
            match = handler["pattern"].match(self.url.path)
            if match:
                try:
                    handler["handler"](self, query, **match.groupdict())
                except Exception as e:
                    logging.error(f"Failed to handle GET {self.url}, {query=}")
                    logging.exception(e)
                    self.send_response(500)
                finally:
                    break
        else:
            logging.error(f"Unhandled GET {self.url}, {query=}")
            self.send_response(404)

    def do_POST(self):
        self.normalize_url()
        query = parse_qs(self.url.query)
        data = self.rfile.read(int(self.headers["Content-Length"]))
        if self.headers.get("Content-Type") == "application/json":
            data = json.loads(data)
        elif self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
            data = parse_qs(data.decode())

        handlers = HANDLERS["post"].get(self.url.netloc, [])
        for handler in handlers:
            match = handler["pattern"].match(self.url.path)
            if match:
                try:
                    handler["handler"](self, data, **match.groupdict())
                except Exception as e:
                    logging.error(
                        f"Failed to handle POST {self.url}, {self.headers=}, {data=}, {query=}"
                    )
                    logging.exception(e)
                    self.send_response(500)
                finally:
                    break
        else:
            logging.error(f"Unhandled POST {self.url}, {data=}, {query=}")
            self.send_response(404)
