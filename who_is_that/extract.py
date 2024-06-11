from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup
import tempfile
import pathlib
import typing

class Extractor:
    def __init__(self, text_content: list[tuple[str, str]], author: typing.Optional[str] = None, title: typing.Optional[str] = None) -> None:
        self.text_content = text_content
        self.author = author
        self.title = title

    @staticmethod
    def get_metadata(epub_path: pathlib.Path, data_type: str) -> str:
        book = epub.read_epub(epub_path)
        metadata = book.get_metadata('DC', data_type)
        if metadata:
            return metadata[0][0]
        else:
            return f"{data_type} not found"

    @staticmethod
    def process(epub_path: pathlib.Path) -> list[tuple[str, str]]:
        print(f"Extracting text from EPUB {epub_path}")

        book = epub.read_epub(epub_path)
        text_content = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "lxml")
                # text_content.append(soup.get_text())

                for container in soup.find_all(attrs={"epub:type": "chapter"}):
                    print("get_text", container.attrs, container.get_text())
                    text_content.append((container["id"], container.get_text()))

        return text_content

    @classmethod
    def from_bytes(cls, epub_contents: bytes) -> "Extractor":
        tf = tempfile.NamedTemporaryFile()
        print(f"Writing to {tf.name}")
        tf.write(epub_contents)
        obj = cls(
            text_content=cls.process(tf.name), 
            author=cls.get_metadata(tf.name, 'creator'), 
            title=cls.get_metadata(tf.name, 'title')
        )
        # tf.delete()
        return obj

    @classmethod
    def from_path(cls, epub_path: pathlib.Path) -> "Extractor":
        return cls(text_content=cls.process(epub_path))



    # @classmethod
    # def from_diameter(cls, diameter):
    #     return cls(radius=diameter / 2)
