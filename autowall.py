#!/bin/python
"""
File: autowall.py
Author: Began Bajrami
Email: beganbajrami@email.com
Github: https://github.com/begbaj
Description: Simple wallpaper setter script

"""
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
    global ALLOW
    global PROVIDER
    global PROVIDER_HINT
    global AVAILABLE_PROVIDERS
    global URL_SEARCH
    global API_KEY
    if len(argv) == 1:
        ALLOW = True
        print("No arguments passed")
        return

    log.basicConfig(level=log.ERROR)
    if env("AUTOWALL_API") is None:
        log.warning("No api key provided!")
    else:
        API_KEY = env("AUTOWALL_API")

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
    parser.add_argument("--keep", type=bool,action=argparse.BooleanOptionalAction, help="Set the last wallpeper downloaded")

    args = parser.parse_args()

    http_args=""
    http_header = None
    
    if args.keep:
        set_wallpaper(keep=True)
        return

    if args.v is not None:
        ALLOW = True
    if args.q is not None:
        http_args += f"q={args.q}"
    if args.c is not None:
        http_args += f"&categories={str(args.c).zfill(3)}"

    if args.p is not None:
        log.debug(args.p)
        if str(args.p)[-1] == "1":
            if API_KEY is None:
                log.error("no api key provided")
                print("you must provide a API key to get NSFW content")
                return
            http_header = {"X-API-Key":f"{API_KEY}"}
            log.info("api key setted")
        http_args += f"&purity={str(args.p).zfill(3)}"

    if args.s is not None:
        if args.s == "1":
            http_args += "&sorting=relevance"
        elif args.s == "2":
            http_args += "&sorting=random"
        elif args.s == "3":
            http_args += "&sorting=views"
        elif args.s == "4":
            http_args += "&sorting=favorites"
        elif args.s == "5":
            http_args += "&sorting=toplist"

    if args.o is not None:
        if args.o == 1:
            http_args += "&order=asc"

    if args.r is not None:
        http_args += f"&atleast={args.r}"

    if args.exact_res is not None and args.r is None:
        http_args += f"&resolution={args.exact_res[0]}"

    if args.seed is not None:
        http_args += f"&seed={args.seed}"

    if args.c is not None:
        http_args += f"&categories={args.c}"

    if args.R is not None:
        http_args += f"&ratios={args.R}"

    if args.C is not None:
        http_args += f"&colors={args.C}"

    search_query = URL_SEARCH + "/?" + quote(http_args, "?=&")
    r = requests.get(search_query,  headers=http_header)
    print(search_query)
    jsonres = r.json()
    lenjson = len(jsonres["data"])
    if lenjson == 0:
        print("no results found")
        return
    result = 0
    if args.random:
        result = random.randint(0, lenjson)
    url = r.json()["data"][result]["path"]
    print(url)
    download_and_set(url)

def download_and_set(url):
    # DOWNLOAD
    img_raw = requests.get(url, stream=True).raw
    img_raw.decode_content = True
    set_wallpaper(img_raw, img_file)

def set_wallpaper(img_raw=None, keep=False):
    autodir = path.expanduser("~/.local/share/autowall/")
    if not keep:
        if not path.isdir(autodir):
           mkdir(autodir) 
        with open(autodir + "paper", "wb") as img_file:
            shutil.copyfileobj(img_raw, img_file)
    system(f"feh --no-fehbg --bg-scale {autodir}/paper")

def print(msg):
    if ALLOW:
        __builtin__.print(msg)

if __name__ == "__main__":
    main()
