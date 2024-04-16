from playwright.sync_api import sync_playwright
import logging
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath

BYPASS_FLASH_DETECTION = """
(function() {
    'use strict';
    try {
        Object.defineProperty(window, "showBlockFlashIE", {
            value: () => { },
            writable: false,
        });
    } catch (e) { console.log(e) }
    try {
        Object.defineProperty(window, "showBlockFlash", {
            value: () => { },
            writable: false,
        });
    } catch (e) { console.log(e) }
})();
"""

RESOLVE_SWF_URL = """
(function(){
    'use strict';
    let flash = document.querySelector("#flashgame");
    if (!flash) {
        flash = document.querySelector("#swf1");
    }
    if (flash) return flash.querySelector("param[name=movie]").value;
})();
"""

RESOLVE_SWF_IFRAME_URL = """
(function() {
    'use strict';
    const subframes = document.querySelectorAll("iframe");
    if (!subframes) return;
    for (const subframe of subframes) {
        const src = subframe.src;
        console.log(src)
        if (src.indexOf("upload_swf") !== -1) {
            return subframe.src;
        }
    }
})();
"""


def _handle_route(route):
    if "antijs" in route.request.url:
        route.fulfill(status=404)
    elif "baidu.com" in route.request.url:
        route.abort()
    elif "cnzz" in route.request.url:
        route.abort()
    else:
        route.continue_()


def resolve_swf_url(url):
    with sync_playwright() as p:
        logging.info("launching browser")
        browser = p.chromium.launch()
        page = browser.new_page()
        page.route("**/*", _handle_route)
        page.add_init_script(BYPASS_FLASH_DETECTION)
        logging.info(f"goto {url}")
        page.goto(url, wait_until="domcontentloaded")

        result = page.evaluate(RESOLVE_SWF_URL)
        if not result:
            logging.info("SWF URL not found, trying to resolve iframe")
            iframe = page.evaluate(RESOLVE_SWF_IFRAME_URL)
            logging.info(f"iframe: {iframe}")
            assert iframe, "SWF URL not found"
            assert iframe.endswith(".htm") or iframe.endswith(
                ".html"
            ), f"Invalid iframe URL {iframe}"
            page.close()
            page = browser.new_page()
            page.goto(iframe, referer=url, wait_until="domcontentloaded")
            result = page.evaluate(RESOLVE_SWF_URL)
            if (
                not result.startswith("http")
                or not result.startswith("https")
                or not result.startswith("//")
            ):
                logging.info(f"Resolving relative URL: {result}")
                baseurl = urlparse(iframe)
                basepath = PurePosixPath(unquote(baseurl.path))
                result = baseurl._replace(path=f"{basepath.parent}/{result}").geturl()

        assert result, "SWF URL not found"
        assert result.endswith(".swf"), f"Invalid SWF URL {result}"

        browser.close()
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    url = "https://www.4399.com/flash/130396.htm"
    logging.info(resolve_swf_url(url))
    url = "https://www.4399.com/flash/205551_4.htm"
    logging.info(resolve_swf_url(url))
    url = "https://www.4399.com/flash/yzzrhj.htm?g=2"
    logging.info(resolve_swf_url(url))
