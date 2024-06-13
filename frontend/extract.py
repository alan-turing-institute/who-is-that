from __future__ import annotations

import pathlib
import tempfile
import typing
import warnings
from dataclasses import dataclass

import ebooklib
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from ebooklib import epub


@dataclass
class Chapter:
    name: str
    html: str
    text: str


class Extractor:
    def __init__(
        self: typing.Self,
        chapters: list[Chapter],
        cover: bytes | None = None,
        authors: list[str] | None = None,
        title: str | None = None,
    ) -> None:
        self.chapters = chapters
        self.cover = cover
        self.authors = authors
        self.title = title

    @staticmethod
    def get_metadata(book: epub.EpubBook, data_type: str) -> list[str]:
        metadata = book.get_metadata("DC", data_type)
        if metadata:
            return [md[0] for md in metadata]
        return [f"{data_type} not found"]

    @staticmethod
    def get_cover(book: epub.EpubBook) -> None:
        # book = epub.read_epub(epub_path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_COVER:
                return item.get_content()
        return None

    @staticmethod
    def process(book: epub.EpubBook) -> list[Chapter]:
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        action="ignore",
                        category=XMLParsedAsHTMLWarning,
                    )
                    soup = BeautifulSoup(item.get_content(), features="lxml")

                    # Remove images which we will not try to display
                    if soup.figure:
                        soup.figure.decompose()
                    if soup.img:
                        soup.img.decompose()
                    if soup.svg:
                        soup.svg.decompose()

                    # Remove navigation elements which are not part of the text
                    if soup.nav:
                        soup.nav.decompose()

                    # Remove Project Gutenberg boilerplate
                    for element in soup.find_all(True, {"class": "pg-boilerplate"}):
                        element.decompose()

                    # Look for elements marked as epub:type="chapter"
                    elements = soup.find_all(attrs={"epub:type": "chapter"})
                    if len(elements) > 0:
                        for element in elements:
                            chapters.append(
                                Chapter(
                                    name=element.get("id", ""),
                                    html=element.prettify(),
                                    text=element.get_text(),
                                ),
                            )

                    # Otherwise we take the body content of each page
                    elif elements := soup.find_all("body"):
                        for element in elements:
                            chapters.append(
                                Chapter(
                                    name=element.get("title", ""),
                                    html=element.prettify(),
                                    text=element.get_text(),
                                ),
                            )

        return chapters

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
            chapters=cls.process(book),
            cover=cls.get_cover(book),
            authors=cls.get_metadata(book, "creator"),
            title=cls.get_metadata(book, "title")[0],
        )
