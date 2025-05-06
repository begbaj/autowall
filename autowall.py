#!/bin/python
"""
File: autowall.py
Author: Began Bajrami
Email: beganbajrami@email.com
Github: https://github.com/begbaj
Description: Simple wallpaper setter script
"""

import requests
import textwrap
import builtins as __builtin__
import re
import argparse
import shutil
import random
import logging as log
from urllib.parse import quote
from os import getenv as env
import os
from sys import argv

ALLOW = False
PROVIDER = "wallhavenh"
PROVIDER_HINT = ""
AVAILABLE_PROVIDERS = ["wallhaven", "bing"]
WALLHAVEN_URL_API = "https://wallhaven.cc/api/v1/"
BING_API = "https://bing.biturl.top"
API_KEY = None

autodir = os.path.expanduser("~/.local/share/autowall/")


class CustomFormatter(argparse.RawTextHelpFormatter):
    pass


def main():
    global ALLOW
    log.basicConfig(level=log.ERROR)
    check_default()

    if env("AUTOWALL_API") is None:
        log.warning("No api key provided!")
    else:
        API_KEY = env("AUTOWALL_API")

    parser = argparse.ArgumentParser(
        prog="autowall",
        description="Simple wallpaper setter",
        usage="autowall [OPTIONS] [PROVIDER] [PROVIDER OPTIONS]",
        epilog="author: began bajrami",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Globally available options
    parser.add_argument("-a", action="store_true", help="Use the last used wallpaper")
    parser.add_argument(
        "-d", action="store_true", help="Use the last downloaded wallpaper"
    )
    parser.add_argument("-k", type=str, help="Save current wallpaper", metavar="NAME")
    parser.add_argument("-l", action="store_true", help="List downloaded wallpapers")
    parser.add_argument(
        "-u",
        default=None,
        type=str,
        help="Use one of the previously downloaded wallpapers",
        metavar="NAME",
    )
    parser.add_argument("-v", action="store_true", help="Debug verbose output")

    # Add subparsers
    subparsers = parser.add_subparsers(dest="provider", required=False)
    # Wallhaven provider specific arguments
    wallhavenp = subparsers.add_parser(
        "wh",
        help="wallhaven provider",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    wallhavenp.add_argument(
        "--id", type=str, metavar="id", default=None, help="Wallpaper ID"
    )
    wallhavenp.add_argument(
        "-q",
        "--query",
        type=str,
        metavar="query",
        default=None,
        help="Search query - Your main way of finding what you're looking for.",
    )
    wallhavenp.add_argument(
        "-c",
        "--categories",
        type=str,
        metavar="categories",
        default=None,
        help="Turn categories on(1) or off(0). Must provide 3 bits, default is 111",
    )
    wallhavenp.add_argument(
        "-p",
        "--purity",
        type=str,
        metavar="purity",
        default=None,
        help="Turn purities on(1) or off(0). Must provide 3 bits, default is 100, where last one is available only if using API for turning on NSFW content.",
    )
    wallhavenp.add_argument(
        "-s",
        "--sorting",
        type=str,
        metavar="sorting",
        default=None,
        help=textwrap.dedent("""
        Method of sorting results (default is 0):
              0 - date
              1 - relevance
              2 - random
              3 - views
              4 - favorites
              5 - toplist
              6 - hot
        """),
    )
    wallhavenp.add_argument(
        "--ai", action=argparse.BooleanOptionalAction, help="Allow AI art"
    )
    wallhavenp.add_argument(
        "-o",
        "--order",
        type=str,
        metavar="order",
        default=None,
        help="Sorting order (default is 0): 0 (desc) | 1 (asc) ",
    )
    wallhavenp.add_argument(
        "-r",
        "--resolution",
        type=str,
        metavar="resolution",
        default=None,
        help="Minimum resolution allowed",
    )
    wallhavenp.add_argument(
        "--exact-res",
        type=str,
        metavar="exact_resolution",
        default=None,
        help="Exact resolution",
    )
    wallhavenp.add_argument(
        "--seed",
        type=str,
        metavar="seed",
        default=None,
        help="Optional seed for random results",
    )
    wallhavenp.add_argument(
        "-R",
        "--ratio",
        type=str,
        metavar="ratio",
        default="16x9",
        help="Aspect ratio (default: 16x9)",
    )
    wallhavenp.add_argument(
        "-C",
        "--color",
        type=str,
        metavar="color",
        default=None,
        help="Search by color.",
    )
    wallhavenp.add_argument(
        "--random", action=argparse.BooleanOptionalAction, help="Select a random result"
    )

    # Bing provider specific arguments
    bingp = subparsers.add_parser("bing", help="bing provider")
    bingp.add_argument("-d", action="store_true", help="Use the daily Bing wallpaper.")
    bingp.add_argument("-r", action="store_true", help="Use a random Bing wallpaper.")
    bingp.add_argument("--uhd", action="store_true", help="4K wallpaper")
    bingp.add_argument(
        "--region", help="Set a specific region, by default it is random"
    )
    bingp.add_argument(
        "--resolution", help="Set a specific resolution, by default it is 1920"
    )

    if len(argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.v:
        ALLOW = True

    # Handle global options first
    if args.a:
        setw()
        return

    if args.d:
        last = config("last_downloaded")
        setw(last)
        config("last_used", last)
        return

    if args.u is not None:
        filename = config("last_used")
        if args.u != "":
            filename = args.u
        try:
            setw(filename)
        except FileNotFoundError:
            print(f"File was not found in {autodir}/{filename}", 1)
        finally:
            return

    if args.l:
        files = os.listdir(autodir)
        for file in files:
            print(file, 1)
        return

    if args.k is not None:
        if args.k == "":
            print("Please provide a name for the wallpaper.", 1)
        else:
            paper = f"{autodir}{config('last_downloaded')}"
            name = f"{autodir}{args.k}"
            shutil.copy(paper, name)
            if os.path.exists(name):
                print(f"Wallpaper successfully saved to {name}", 1)
                config("last_downloaded", str(args.k))
            else:
                print("Something went wrong while saving the wallpaper.", 1)
        return

    # Handle provider-specific logic
    if args.provider == "wh":
        handle_wh(args)
    elif args.provider == "bing":
        handle_bing(args)
    else:
        parser.print_help()
        return


def handle_wh(args):
    r = None
    if args.id is not None:
        query = WALLHAVEN_URL_API + "w/" + quote(args.id)
        print(query)
        header = None
        try:
            r = requests.get(query, headers=header)
            jsonres = r.json()
            lenjson = len(jsonres["data"])
            if lenjson == 0:
                print("No results found")
                return
            url = jsonres["data"]["path"]
            id = jsonres["data"]["id"]
            download(url, id)
            setw()
        except requests.JSONDecodeError:
            print(
                "There was an error decoding query response, check wallhaven.cc status (probably server is down).",
                1,
            )

    elif (
        args.query is not None
        or args.categories is not None
        or args.purity is not None
        or args.sorting is not None
        or args.order is not None
        or args.resolution is not None
        or args.color is not None
        or args.ratio is not None
    ):
        (query, header) = url_composer(args)
        r = requests.get(query, headers=header)
        try:
            jsonres = r.json()
            lenjson = len(jsonres["data"])
            if lenjson == 0:
                print("No results found")
                return
            result = 0
            if args.random:
                result = random.randint(0, lenjson - 1)
            url = jsonres["data"][result]["path"]
            id = jsonres["data"][result]["id"]
            download(url, id)
            setw()
        except requests.JSONDecodeError:
            print(
                "There was an error decoding query response, check wallhaven.cc status (probably server is down).",
                1,
            )
        except Exception as err:
            print(f"There was an unexpected error: {err}", 1)
    else:
        print("Something's wrong")
        return


def handle_bing(args):
    resolution = "1920"
    if args.uhd:
        resolution = "UHD"
    if args.r:
        bing_url = (
            f"{BING_API}/?resolution={resolution}&format=image&index=random&mkt=random"
        )
    else:
        bing_url = f"{BING_API}/?resolution=1920&format=image"
    download_bing_wallpaper(bing_url)
    setw()


def download_bing_wallpaper(url):
    try:
        os.remove(f"{autodir}/{config('last_downloaded')}")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        if not os.path.isdir(autodir):
            os.mkdir(autodir)
        filename = "bing_wallpaper.jpg"
        with open(f"{autodir}{filename}", "wb") as img_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, img_file)
        config("last_downloaded", filename)
    else:
        print("Failed to download Bing wallpaper.")


def url_composer(args) -> tuple:
    http_args = ""
    http_header = None

    if args.query is not None:
        http_args += f"q={args.query}"
    if args.categories is not None:
        http_args += f"&categories={str(args.categories).zfill(3)}"
    if args.purity is not None:
        log.debug(args.purity)
        if str(args.purity)[-1] == "1":
            if API_KEY is None:
                log.error("No API key provided")
                print("You must provide an API key to get NSFW content")
                exit(-1)
            http_header = {"X-API-Key": f"{API_KEY}"}
            log.info("API key set")
        http_args += f"&purity={str(args.purity).zfill(3)}"
    if args.sorting is not None:
        sorting_options = {
            "1": "relevance",
            "2": "random",
            "3": "views",
            "4": "favorites",
            "5": "toplist",
            "6": "hot",
        }
        sorting_value = sorting_options.get(args.sorting, "date_added")
        http_args += f"&sorting={sorting_value}"
    if args.order is not None:
        if args.order == "1":
            http_args += "&order=asc"
    if args.resolution is not None:
        http_args += f"&atleast={args.resolution}"
    if args.exact_res is not None and args.resolution is None:
        http_args += f"&resolution={args.exact_res}"
    if args.seed is not None:
        http_args += f"&seed={args.seed}"
    if args.categories is not None:
        http_args += f"&categories={args.categories}"
    if args.ratio is not None:
        http_args += f"&ratios={args.ratio}"
    if args.color is not None:
        http_args += f"&colors={args.color}"
    if args.ai:
        http_args += "&ai_art_filter=0"

    search_query = WALLHAVEN_URL_API + "search/?" + quote(http_args, "?=&")
    return (search_query, http_header)


def download(url, id):
    # DOWNLOAD
    try:
        os.remove(f"{autodir}/{config('last_downloaded')}")
    except FileNotFoundError:
        print(f"File not found. Skipped.")
    except PermissionError:
        print(f"You do not have permission to delete. Skipped.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")
    finally:
        img_raw = requests.get(url, stream=True).raw
        img_raw.decode_content = True
        if not os.path.isdir(autodir):
            os.mkdir(autodir)
        with open(f"{autodir}{id}", "wb") as img_file:
            shutil.copyfileobj(img_raw, img_file)
        config("last_downloaded", id)


def check_default():
    config("last_used")
    config("last_downloaded")


def config(name: str, value="") -> str:
    """
    name:   configuration name
    """
    path = f"{autodir}.{name}"
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write("")

    if value != "":
        rw = "w"
    else:
        rw = "r"

    with open(path, f"{rw}") as file:
        if rw == "r":
            return str(file.read())
        elif rw == "w" and value:
            file.write(str(value))
            return str(value)
        else:
            return ""


def setw(filename: str = ""):
    try:
        if filename == "":
            filename = config("last_used")
            if not os.path.exists(f"{autodir}/{filename}") or filename == "":
                filename = config("last_downloaded")
        if os.path.exists(f"{autodir}/{filename}"):
            os.system(f"feh --no-fehbg --bg-scale {autodir}/{filename}")
            config("last_used", filename)
        else:
            config("last_used", "")
            config("last_downloaded", "")
            print(
                f"Wallpaper {filename} moved or deleted: use autowall --list to show available wallpapers and autowall -u <name> to set a wallpaper",
                1,
            )
    except Exception as e:
        print(f"Error: {e}")


def print(msg, bypass=0):
    if ALLOW or bypass == 1:
        __builtin__.print(msg)


if __name__ == "__main__":
    main()
