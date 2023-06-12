from typing import List
from html.parser import HTMLParser


class Parser(HTMLParser):
    """
    Customer HTML Parser.
    """

    def __init__(self):
        super().__init__()
        self.data: List[str] = []
        self.capture: bool = False

    def handle_starttag(self, tag: str, *args, **kwargs):
        if tag in ("p", "h1"):
            self.capture = True

    def handle_endtag(self, tag: str):
        if tag in ("p", "h1"):
            self.capture = False

    def handle_data(self, data: str):
        if self.capture:
            self.data.append(data.strip())
