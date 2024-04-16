from script.buildswf import SWFBuilder
from script.resolve_swf_url import resolve_swf_url
from backends.server import Handler

import requests
import logging
import os
from pathlib import Path
from rich.logging import RichHandler
from rich.progress import Progress

from argparse import ArgumentParser


def download(args):
    logging.info(f"Downloading {args.url}")
    swf_url = resolve_swf_url(args.url)
    logging.info(f"Resolve to {swf_url}")
    response = requests.get(
        swf_url, headers={"Referer": "http://www.4399.com"}, stream=True
    )
    response.raise_for_status()
    with Progress() as progress, open(
        Path(os.getcwd()) / "out" / "_Game.swf", "wb"
    ) as f:
        task = progress.add_task(
            "Downloading", total=int(response.headers.get("content-length", 0))
        )
        for chunk in response.iter_content(chunk_size=8192):
            progress.update(task, advance=len(chunk))
            f.write(chunk)
    logging.info("Unpacking SWF")
    # TODO: Unpack
    # TODO: Save config


def build(args):
    builder = SWFBuilder(args.swf)
    builder.build()


def run(args):
    # TODO: Set up a server
    # TODO: Check flash player policy
    # TODO: Run the game
    pass


parser = ArgumentParser()
parser.set_defaults(func=lambda _: parser.print_help())
subparsers = parser.add_subparsers()

parser_get = subparsers.add_parser(
    "get", aliases=["g"], help="Download the real game SWF"
)
parser_get.add_argument("url", type=str, help="URL of the Game")
parser_get.set_defaults(func=download)

parser_build = subparsers.add_parser(
    "build", aliases=["b"], help="Modify the game and create a loader for it"
)
parser_build.set_defaults(func=build)

parser_run = subparsers.add_parser("run", aliases=["r"], help="Run the game")
parser_run.set_defaults(func=run)


if __name__ == "__main__":
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    args = parser.parse_args()
    args.func(args)
