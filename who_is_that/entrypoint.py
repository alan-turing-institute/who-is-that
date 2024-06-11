import argparse
import pathlib

from .extract import Extractor


def extract():
    parser = argparse.ArgumentParser(description="Extract text from an EPUB")
    parser.add_argument("--path", type=pathlib.Path, help="Path")
    args = parser.parse_args()

    extractor = Extractor()
    extractor.process(args.path)
