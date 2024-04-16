import logging
import subprocess as sp
from pathlib import Path
import shutil
import os
import json


class SWFBuilder:
    def __init__(self, flex_sdk, game_swf):
        self.game_swf = game_swf
        self.java = shutil.which("java")
        if not self.java:
            raise "Java not found in PATH"

        self.cwd = Path(os.getcwd())
        flex_sdk = Path(flex_sdk)
        self.mxmlc = flex_sdk / "bin" / "mxmlc.bat"
        self.injector = self.cwd / "out" / "artifacts" / "injector_jar" / "injector.jar"

        assert self.mxmlc.exists(), "mxmlc not found"
        assert self.injector.exists(), "injector jar not found"

    def build_loader(self, width, height, frame_rate):
        compiler_options = [str(self.mxmlc)]
        compiler_options.extend(
            [str(self.cwd / "injector" / "speculum" / "loader" / "SpeculumLoader.as")]
        )
        compiler_options.extend(["-strict"])
        compiler_options.extend(["-output", str(self.cwd / "out" / "_Main.swf")])
        compiler_options.extend(
            ["-source-path", str(self.cwd / "injector"), str(self.cwd / "external")]
        )
        compiler_options.extend(["-target-player=32.0"])
        compiler_options.extend(["-swf-version=32"])
        compiler_options.extend(["-use-network"])
        compiler_options.extend(["-default-size", str(width), str(height)])
        compiler_options.extend(["-default-frame-rate", str(frame_rate)])
        logging.debug(compiler_options)
        sp.run(compiler_options, check=True)

    def build_interceptor(self):

        compiler_options = [str(self.mxmlc)]
        compiler_options.extend(
            [
                self.cwd
                / "injector"
                / "speculum"
                / "interceptor"
                / "SpeculumInterceptor.as"
            ]
        )
        compiler_options.extend(["-strict"])
        compiler_options.extend(["-output", self.cwd / "out" / "_Interceptor.swf"])
        compiler_options.extend(["-source-path", self.cwd / "injector"])
        compiler_options.extend(["-target-player=32.0"])
        compiler_options.extend(["-swf-version=32"])
        compiler_options.extend(["-use-network"])
        compiler_options.extend(["-default-size", "800", "600"])
        compiler_options.extend(["-default-frame-rate", "30"])

        sp.run(compiler_options, check=True)

    def get_swf_info(self):
        info = sp.run(
            [self.java, "-jar", self.injector, "info", self.game_swf],
            stdout=sp.PIPE,
            check=True,
        ).stdout
        info = json.loads(info)

        # twip to pixie
        info["width"] = info["width"] // 20
        info["height"] = info["height"] // 20
        return info

    def build_injected_swf(self):
        sp.run(
            [
                self.java,
                "-jar",
                self.injector,
                "merge",
                self.game_swf,
                self.cwd / "out" / "_Interceptor.swf",
                self.cwd / "out" / "_Merged.swf",
            ],
            check=True,
        )
        sp.run(
            [
                self.java,
                "-jar",
                self.injector,
                "inject",
                self.cwd / "out" / "_Merged.swf",
                "speculum.interceptor",
                "SpeculumInterceptor",
                self.cwd / "out" / "_Game.swf",
            ],
            check=True,
        )


if __name__ == "__main__":
    from dotenv import dotenv_values

    config = dotenv_values(".env")

    logging.basicConfig(level=logging.DEBUG)
    logging.info("SDK Path: " + config["SDK_PATH"])

    sdk_path = Path(config["SDK_PATH"])
    game_swf = Path(config["GAME_PATH"])

    builder = SWFBuilder(sdk_path, game_swf)
    info = builder.get_swf_info()
    frame_rate = int(info["frame_rate"])
    width = info["width"]
    height = info["height"]
    logging.info(f"{width=}, {height=}, {frame_rate=}")
    builder.build_loader(info["width"], info["width"], frame_rate)
    builder.build_interceptor()
    builder.build_injected_swf()
