#!/bin/python
import requests
import builtins as __builtin__
import re
import argparse
import shutil
import random
import logging as log
from urllib.parse import quote
from os import getenv as env
from os import path
from os import mkdir
from os import system
from sys import argv

ALLOW = False
PROVIDER = "wallheavenh"
PROVIDER_HINT = ""
AVAILABLE_PROVIDERS = ["wallheaven"]
URL_SEARCH = "https://wallhaven.cc/api/v1/search"
API_KEY = None

def main():
    log.basicConfig(level=log.ERROR)
    parser = argparse.ArgumentParser(description="Simple wallpaper setter")
    parser.add_argument("-q", type=str, metavar="query",
            default=None, help="Search query - Your main way of finding what you're looking for.")
    parser.add_argument("-c", type=str, metavar="categories",
            default=None, help="Turn categories on(1) or off(0). Must provide 3 bits, default is 111")
    parser.add_argument("-p", type=str, metavar="purity",
            default=None, help="Turn purities on(1) or off(0). Must provide 3 bits, default is 100")
    parser.add_argument("-s", type=str, metavar="sorting",
            default=None, help="Method of sorting results:\n"\
                            "0 - date added (default)\n"\
                            "1 - relevance\n"\
                            "2 - random\n"\
                            "3 - views\n"\
                            "4 - favorites\n"\
                            "5 - toplist")
    parser.add_argument("-o", type=str, metavar="order",
					default=None, help="Sorting order: 0 - desc (default); 1 - asc")

    parser.add_argument("-r", type=str, metavar="resolution",
					default=None, help="Minimum resolution allowed")
    parser.add_argument("--exact-res", type=str, metavar="exact_resolution",
					default=None, help="")
    parser.add_argument("--seed", type=str, metavar="seed",
					default=None, help="Optional seed for random results")
    parser.add_argument("-R", type=str, metavar="ratio",
					default="16x9", help="Aspect ratio (default: 16x9)")
    parser.add_argument("-C", type=str, metavar="color",
					default=None, help="Search by color.")
    parser.add_argument("-v", action=argparse.BooleanOptionalAction)
    parser.add_argument("--random", help="select a random result", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

def print(msg):
    if ALLOW:
        __builtin__.print(msg)
