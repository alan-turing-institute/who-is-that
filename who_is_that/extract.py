from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup


class Extractor:
    def process(self, epub_path: str) -> str:
        print(f"Extracting text from EPUB {epub_path}")

        book = epub.read_epub(epub_path)
        text_content = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'lxml')
                text_content.append(soup.get_text())

        return '\n'.join(text_content)
