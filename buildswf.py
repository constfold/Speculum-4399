from dotenv import dotenv_values
import logging as log
import subprocess as sp
from pathlib import Path
import shutil
import os
import json

config = dotenv_values(".env")

log.basicConfig(level=log.DEBUG)
log.info("SDK Path: " + config["SDK_PATH"])

cwd = Path(os.getcwd())
sdk_path = Path(config["SDK_PATH"])
game_path = Path(config["GAME_PATH"])


def build_loader(width, height, frame_rate):
    compiler_options = [str(sdk_path / "bin" / "mxmlc.bat")]
    compiler_options.extend(
        [str(cwd / "injector" / "speculum" / "loader" / "SpeculumLoader.as")]
    )
    compiler_options.extend(["-strict"])
    compiler_options.extend(["-output", str(cwd / "out" / "_Main.swf")])
    compiler_options.extend(
        ["-source-path", str(cwd / "injector"), str(cwd / "external")]
    )
    compiler_options.extend(["-target-player=32.0"])
    compiler_options.extend(["-swf-version=32"])
    compiler_options.extend(["-use-network"])
    compiler_options.extend(["-default-size", str(width), str(height)])
    compiler_options.extend(["-default-frame-rate", str(frame_rate)])
    log.debug(compiler_options)
    sp.run(compiler_options, check=True)


def build_interceptor():
    compiler_options = [str(sdk_path / "bin" / "mxmlc.bat")]
    compiler_options.extend(
        [str(cwd / "injector" / "speculum" / "interceptor" / "SpeculumInterceptor.as")]
    )
    compiler_options.extend(["-strict"])
    compiler_options.extend(["-output", str(cwd / "out" / "_Interceptor.swf")])
    compiler_options.extend(["-source-path", str(cwd / "injector")])
    compiler_options.extend(["-target-player=32.0"])
    compiler_options.extend(["-swf-version=32"])
    compiler_options.extend(["-use-network"])
    compiler_options.extend(["-default-size", "800", "600"])
    compiler_options.extend(["-default-frame-rate", "30"])

    sp.run(compiler_options, check=True)


def get_swf_info():
    injector_jar = cwd / "out" / "artifacts" / "injector_jar" / "injector.jar"
    java = shutil.which("java")
    if not java:
        log.error("Java not found in PATH")
        return
    info = sp.run(
        [java, "-jar", str(injector_jar), "info", game_path], stdout=sp.PIPE
    ).stdout
    return json.loads(info)


def build_injected_swf():
    injector_jar = cwd / "out" / "artifacts" / "injector_jar" / "injector.jar"
    java = shutil.which("java")
    if not java:
        log.error("Java not found in PATH")
        return
    sp.run(
        [
            java,
            "-jar",
            str(injector_jar),
            "merge",
            game_path,
            str(cwd / "out" / "_Interceptor.swf"),
            str(cwd / "out" / "_Merged.swf"),
        ],
        check=True,
    )
    sp.run(
        [
            java,
            "-jar",
            str(injector_jar),
            "inject",
            str(cwd / "out" / "_Merged.swf"),
            "speculum.interceptor",
            "SpeculumInterceptor",
            str(cwd / "out" / "_Game.swf"),
        ],
        check=True,
    )


if __name__ == "__main__":
    info = get_swf_info()
    # twip to pixie
    width = info["width"] // 20
    height = info["height"] // 20
    frame_rate = int(info["frame_rate"])
    log.info(f"{width=}, {height=}, {frame_rate=}")
    build_loader(width, height, frame_rate)
    build_interceptor()
    build_injected_swf()
