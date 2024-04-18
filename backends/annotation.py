import re


HANDLERS = {
    "get": {},
    "post": {},
}


def handle(method, url, pattern):
    def wrapper(func):
        method_handler = HANDLERS[method]
        if url not in method_handler:
            method_handler[url] = []
        method_handler[url].append(
            {
                "pattern": re.compile(pattern),
                "handler": func,
            }
        )
        return func

    return wrapper
