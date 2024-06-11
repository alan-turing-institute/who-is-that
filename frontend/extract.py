from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup
import tempfile
import pathlib
import typing


class Extractor:
    def __init__(self, text_content: list[tuple[str, str]], cover: typing.Optional[bytes] = None, authors: typing.Optional[list[str]] = None, title: typing.Optional[str] = None) -> None:
        self.text_content = text_content
        self.cover = cover
        self.authors = authors
        self.title = title

    @staticmethod
    def get_metadata(epub_path: pathlib.Path, data_type: str) -> str:
        book = epub.read_epub(epub_path)
        metadata = book.get_metadata('DC', data_type)
        if metadata:
            return [md[0] for md in metadata]
        else:
            return f"{data_type} not found"

    @staticmethod
    def get_cover(epub_path: pathlib.Path) -> None:
        book = epub.read_epub(epub_path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_COVER:
                return item.get_content()
        return None

    @staticmethod
    def process(epub_path: pathlib.Path) -> list[tuple[str, str]]:
        print(f"Extracting text from EPUB {epub_path}")

        book = epub.read_epub(epub_path)
        text_content = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "lxml")

                for container in soup.find_all(attrs={"epub:type": "chapter"}):
                    text_content.append((container["id"], container.get_text()))

        return text_content

    @classmethod
    def from_bytes(cls, epub_contents: bytes) -> "Extractor":
        tf = tempfile.NamedTemporaryFile()
        print(f"Writing to {tf.name}")
        tf.write(epub_contents)
        obj = cls(
            text_content=cls.process(tf.name),
            cover=cls.get_cover(tf.name),
            authors=cls.get_metadata(tf.name, 'creator'),
            title=cls.get_metadata(tf.name, 'title')[0],
        )
        return obj

    @classmethod
    def from_path(cls, epub_path: pathlib.Path) -> "Extractor":
        return cls(
            text_content=cls.process(epub_path),
            cover=cls.get_cover(epub_path),
            authors=cls.get_metadata(epub_path, 'creator'),
            title=cls.get_metadata(epub_path, 'title')[0]
            )
