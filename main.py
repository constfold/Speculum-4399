from speculum.swfutil import SWFUtil
from speculum.resolve_swf_url import resolve_swf_url
from backends.server import SpeculumServer
from backends.handler import SpeculumHandler

import json
import tempfile
from urllib.parse import unquote, urlparse
from threading import Thread
from dotenv import load_dotenv
import requests
import logging
import os
from pathlib import Path, PurePosixPath
from rich.logging import RichHandler
from rich.progress import Progress
from http.server import HTTPServer
import subprocess as sp

from argparse import ArgumentParser


def init(args):
    cwd = Path(os.getcwd()).resolve()
    out = cwd / "out"
    logging.info(f"Run at {cwd}, output to {out}")
    util = SWFUtil(os.environ["FLEX_PATH"])

    logging.info(f"Initializing {args.url}")

    if not args.skip_download:
        swf_url = resolve_swf_url(args.url)
        logging.info(f"Resolve to {swf_url}")
        response = requests.get(
            swf_url, headers={"Referer": "http://www.4399.com"}, stream=True
        )
        response.raise_for_status()
        game_swf = out / "_Game.swf"
        with Progress() as progress, open(game_swf, "wb") as tmp:
            task = progress.add_task(
                "Downloading", total=int(response.headers.get("content-length", 0))
            )
            for chunk in response.iter_content(chunk_size=50 * 1024):
                progress.update(task, advance=len(chunk))
                tmp.write(chunk)

        logging.info("Trying to extract")

        extracted = out / "_Game.bin"
        if util.extract(game_swf, extracted):
            game_swf = extracted
        else:
            logging.error("Failed to extract")
            return
    else:
        game_swf = out / "_Game.bin"
        if not game_swf.exists():
            logging.error("Game file not found")
            return
        game_config_file = out / "game.json"
        if not game_config_file.exists():
            logging.error("Game configuration not found")
            return

    logging.info("Retrieve necessary informaton of the game")
    info = util.get_info(game_swf)
    frame_rate = int(info["frame_rate"])
    width = info["width"]
    height = info["height"]
    logging.info(f"{width=}, {height=}, {frame_rate=}")

    logging.info("Building interceptor")
    util.build_interceptor(out / "_Interceptor.swf")
    logging.info("Injecting")
    util.merge(game_swf, out / "_Interceptor.swf", out / "_Merged.swf")
    util.inject(out / "_Merged.swf", out / "Game.swf")
    game_swf = out / "Game.swf"

    logging.info("Building loader")
    util.build_loader(width, height, frame_rate, out / "Main.swf")

    if not args.skip_download:
        logging.info("Saving configuration")
        baseurl = urlparse(swf_url)
        basepath = PurePosixPath(unquote(baseurl.path))
        baseurl = baseurl._replace(path=f"{basepath.parent}").geturl() + "/"
        game_config = {
            "gamefile": str(game_swf),
            "baseurl": str(baseurl),
            "saveName": "test",
            "savePath": "/",
        }
        with open(out / "game.json", "w") as f:
            json.dump(game_config, f, ensure_ascii=False, indent=4)
    logging.info("Done")


def run(args):
    # Check if the game is initialized
    cwd = Path(os.getcwd()).resolve()
    out = cwd / "out"
    game_config = out / "game.json"
    if not game_config.exists():
        logging.error("Game not initialized")
        return
    flash_player = Path(os.environ["FLASH_PLAYER_PATH"])
    if not flash_player.exists():
        logging.error("Flash player not found")
        return
    logging.info(f"{flash_player=}")
    config = json.loads(game_config.read_text())
    baseurl = config["baseurl"]
    logging.info(f"Proxy to {baseurl}")

    with SpeculumServer(
        ("localhost", int(os.environ["BACKEND_PORT"])),
        SpeculumHandler,
        base_url=baseurl,
        no_cache=args.no_cache,
        inject_nested=args.inject_nested,
    ) as server:
        port = server.server_port
        config["server"] = f"http://localhost:{port}/+"
        game_config.write_text(json.dumps(config, ensure_ascii=False, indent=4))
        logging.info(f"Server started at http://localhost:{port}")

        def run_flash_player():
            try:
                sp.run([flash_player, out / "Main.swf"], check=True)
            finally:
                server.shutdown()

        Thread(target=run_flash_player).start()
        server.serve_forever()


parser = ArgumentParser()
parser.set_defaults(func=lambda _: parser.print_help())
subparsers = parser.add_subparsers()

parser_get = subparsers.add_parser("init", help="Initialize with game URL")
parser_get.add_argument("url", type=str, help="URL of the Game")
parser_get.add_argument("--skip-download", action="store_true", help="use local file")
parser_get.set_defaults(func=init)

parser_run = subparsers.add_parser("run", aliases=["r"], help="Start the game")
parser_run.add_argument("--no-cache", action="store_true", help="Do not use cache")
parser_run.add_argument(
    "--inject-nested", action="store_true", help="Inject nested swf"
)
parser_run.set_defaults(func=run)

parser_clean = subparsers.add_parser("clean", help="Clean up the generated files")
parser_clean.set_defaults(
    func=lambda _: sp.run(
        [
            "powershell",
            "Remove-Item",
            "out\\*",
            "-Include",
            '@("game.json", "*.bin", "*.swf")',
            "-Recurse",
        ]
    )
)

if __name__ == "__main__":
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    load_dotenv(".env", override=True)

    args = parser.parse_args()
    args.func(args)
