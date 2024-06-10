import argparse
import pathlib

from .extract import Extractor
from .summarise import Summariser


def extract():
    parser = argparse.ArgumentParser(description="Extract text from an EPUB")
    parser.add_argument("--path", type=pathlib.Path, help="Path")
    args = parser.parse_args()

    extractor = Extractor()
    extractor.process(args.path)


def summarise():
    parser = argparse.ArgumentParser(description="Summarise text from an EPUB")
    parser.add_argument("--chapter", type=int, help="Chapter number")
    args = parser.parse_args()

    summariser = Summariser()
    summariser.process(args.path)
