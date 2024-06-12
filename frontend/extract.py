from __future__ import annotations
import warnings

import pathlib
import tempfile
import typing

import ebooklib
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from ebooklib import epub


class Extractor:
    def __init__(
        self: typing.Self,
        text_content: list[tuple[str, str]],
        cover: bytes | None = None,
        authors: list[str] | None = None,
        title: str | None = None,
    ) -> None:
        self.text_content = text_content
        self.cover = cover
        self.authors = authors
        self.title = title

    @staticmethod
    def get_metadata(book: epub.EpubBook, data_type: str) -> str:
        metadata = book.get_metadata("DC", data_type)
        if metadata:
            return [md[0] for md in metadata]
        return f"{data_type} not found"

    @staticmethod
    def get_cover(book: epub.EpubBook) -> None:
        # book = epub.read_epub(epub_path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_COVER:
                return item.get_content()
        return None

    @staticmethod
    def process(book: epub.EpubBook) -> list[tuple[str, str]]:
        text_content = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                with warnings.catch_warnings():
                    warnings.filterwarnings(action="ignore", category=XMLParsedAsHTMLWarning)
                    soup = BeautifulSoup(item.get_content(), features="lxml")
                for container in soup.find_all(attrs={"epub:type": "chapter"}):
                    text_content.append((container["id"], container.get_text()))

        return text_content

    @classmethod
    def from_bytes(cls: type[typing.Self], epub_contents: bytes) -> Extractor:
        tf = tempfile.NamedTemporaryFile()
        tf.write(epub_contents)
        return cls.from_path(tf.name)

    @classmethod
    def from_path(cls: type[typing.Self], epub_path: pathlib.Path) -> Extractor:
        # Read book ignoring warnings
        with warnings.catch_warnings():
            warnings.filterwarnings(action="ignore", category=UserWarning)
            warnings.filterwarnings(action="ignore", category=FutureWarning)
            book = epub.read_epub(epub_path, {"ignore_ncx": False})

        # Construct a book
        return cls(
            text_content=cls.process(book),
            cover=cls.get_cover(book),
            authors=cls.get_metadata(book, "creator"),
            title=cls.get_metadata(book, "title")[0],
        )
