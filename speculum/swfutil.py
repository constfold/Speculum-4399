import logging
import subprocess as sp
from pathlib import Path
import shutil
import os
import json


class SWFUtil:
    def __init__(self, flex_sdk):
        self.java = shutil.which("java")
        if not self.java:
            raise "Java not found in PATH"

        self.cwd = Path(os.getcwd())
        flex_sdk = Path(flex_sdk)
        self.mxmlc = flex_sdk / "bin" / "mxmlc.bat"
        self.swfutil = (
            self.cwd / "out" / "swfutil" / "swfutil-1.0-jar-with-dependencies.jar"
        )

        assert self.mxmlc.exists(), "mxmlc not found"
        assert self.swfutil.exists(), "swfutil jar not found"

    def build_loader(self, width: int, height: int, frame_rate: int, output: Path):
        compiler_options = [self.mxmlc]
        compiler_options.extend(
            [self.cwd / "core" / "speculum" / "loader" / "SpeculumLoader.as"]
        )
        compiler_options.extend(["-strict"])
        compiler_options.extend(["-debug"])
        compiler_options.extend(["-output", output])
        compiler_options.extend(
            ["-source-path", self.cwd / "core", self.cwd / "external"]
        )
        compiler_options.extend(["-target-player=32.0"])
        compiler_options.extend(["-swf-version=32"])
        compiler_options.extend(["-use-network"])
        compiler_options.extend(["-default-size", str(width), str(height)])
        compiler_options.extend(["-default-frame-rate", str(frame_rate)])
        logging.debug(compiler_options)
        sp.run(compiler_options, check=True)

    def build_interceptor(self, output: Path):

        compiler_options = [self.mxmlc]
        compiler_options.extend(
            [self.cwd / "core" / "speculum" / "interceptor" / "SpeculumInterceptorMain.as"]
        )
        compiler_options.extend(["-strict"])
        compiler_options.extend(["-debug"])
        compiler_options.extend(["-output", output])
        compiler_options.extend(["-source-path", self.cwd / "core"])
        compiler_options.extend(["-target-player=32.0"])
        compiler_options.extend(["-swf-version=32"])
        compiler_options.extend(["-use-network"])
        compiler_options.extend(["-default-size", "800", "600"])
        compiler_options.extend(["-default-frame-rate", "30"])

        sp.run(compiler_options, check=True)

    def get_info(self, swf: Path):
        info = sp.run(
            [self.java, "-jar", self.swfutil, "info", swf],
            check=True,
            stdout=sp.PIPE,
        ).stdout
        logging.info(info)
        info = json.loads(info)

        # twip to pixie
        info["width"] = info["width"] // 20
        info["height"] = info["height"] // 20
        return info

    def merge(self, original: Path, new: Path, output: Path):
        sp.run(
            [
                self.java,
                "-jar",
                self.swfutil,
                "merge",
                original,
                new,
                output,
            ],
            check=True,
        )

    def inject(self, swf: Path, output: Path):
        sp.run(
            [
                self.java,
                "-jar",
                self.swfutil,
                "inject",
                swf,
                "speculum.interceptor",
                output,
            ],
            check=True,
        )

    def extract(self, swf: Path, output: Path) -> bool:
        returncode = sp.run(
            [self.java, "-jar", self.swfutil, "extract", swf, output]
        ).returncode
        return returncode == 0


if __name__ == "__main__":
    from dotenv import dotenv_values

    config = dotenv_values(".env")

    logging.basicConfig(level=logging.DEBUG)
    logging.info("SDK Path: " + config["FLEX_PATH"])

    sdk_path = Path(config["FLEX_PATH"])

    builder = SWFUtil(sdk_path)
    info = builder.get_swf_info("out/_Game.swf")
    frame_rate = int(info["frame_rate"])
    width = info["width"]
    height = info["height"]
    logging.info(f"{width=}, {height=}, {frame_rate=}")
    builder.build_loader(info["width"], info["width"], frame_rate)
    builder.build_interceptor()
    builder.build_injected_swf()
