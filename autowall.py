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
import os
from sys import argv

ALLOW = False
PROVIDER = "wallheavenh"
PROVIDER_HINT = ""
AVAILABLE_PROVIDERS = ["wallheaven"]
URL_SEARCH = "https://wallhaven.cc/api/v1/search"
API_KEY = None
autodir = os.path.expanduser("~/.local/share/autowall/")

def main():
    log.basicConfig(level=log.ERROR)
    check_default()

    if len(argv) == 1:
        print("No arguments passed", 1)
        return

    if env("AUTOWALL_API") is None:
        log.warning("No api key provided!")
    else:
        API_KEY = env("AUTOWALL_API")

    parser = argparse.ArgumentParser(description="Simple wallpaper setter")
    parser.add_argument("--id", type=str, metavar="id",
            default=None, help="wallpaper id")
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
    parser.add_argument("--ai", type=bool,
                        action=argparse.BooleanOptionalAction, help="Allow AI art")

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
    parser.add_argument("-v", help="Verbose output", action=argparse.BooleanOptionalAction)
    parser.add_argument("--random", help="select a random result", action=argparse.BooleanOptionalAction)

    parser.add_argument("--use-last", type=bool,action=argparse.BooleanOptionalAction, help="Set the last used wallpaper")
    parser.add_argument("--use-downloaded", type=bool,action=argparse.BooleanOptionalAction, help="Set the last downloaded wallpaper")
    parser.add_argument("-u","--use", default=None, type=str, help="Set one of the previously downloaded wallpapers")
    parser.add_argument("-l","--list-all", type=bool,action=argparse.BooleanOptionalAction, help="List downloaded wallpapers")
    parser.add_argument("--keep", type=str, help="Save current wallpaper")

    args = parser.parse_args()
    r = None
    neww = False

    if args.v is not None:
        ALLOW = True

    if args.id is not None:
        download_id(args.id)
        return

    if args.use_last:
        setw()
        return

    if args.use_downloaded:
        last = config('last_downloaded')
        setw(last)
        config('last_used', last)
        return

    if args.use is not None:
        filename = config("last_used")
        if args.use != "":
            filename = args.use
        try:
            setw(filename)
        except FileNotFoundError:
            print(f"File was not found in {autodir}/{filename}")
        finally:
            return
    # todo: list available papers
    if args.list_all:
        files = os.listdir(autodir)
        for file in files:
            print(file, 1)
        return
    if args.keep is not None:
        if args.keep == "":
            print("what should we name it?", 1)
        else:
            paper = f"{autodir}{config('last_downloaded')}"
            name = f"{autodir}{args.keep}"
            shutil.copy(paper, name)
            if os.path.exists(name):
                print(f"wallpaper successfully saved to {name}", 1)
                config('last_downloaded', str(args.keep))
            else:
                print(f"something went wrong :/", 1)
        return

    if args.q is not None or args.c is not None or args.p is not None or \
    args.s is not None or args.o is not None or args.r is not None or \
    args.c is not None or args.R is not None or args.C is not None:
        neww = True
        (query, header) = url_composer(args)
        r = requests.get(query,  headers=header)
        jsonres = r.json()
        lenjson = len(jsonres["data"])
        if lenjson == 0:
            print("no results found")
            return
        result = 0
        if args.random:
            result = random.randint(0, lenjson)
        jsonres = r.json()
        url = jsonres["data"][result]["path"]
        id = jsonres["data"][result]["id"]
        download(url,id)
        setw()

def download_id(id):
    url = f"https://w.wallhaven.cc/full/gp/wallhaven-{id}.jpg"
    download(url, id)
    setw()

def url_composer(args) -> tuple:
    http_args=""
    http_header = None

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
                exit(-1)
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
    if args.ai:
        http_args += f"&ai_art_filter=0"

    search_query = URL_SEARCH + "/?" + quote(http_args, "?=&")
    return (search_query, http_header)

def download(url,id):
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

        config('last_downloaded', id)
    

def check_default():
    config('last_used')
    config('last_downloaded')

def config(name:str, value='') -> str:
    """
    name:   configuration name
    rw:     'r' or 'w'
    """
    path = f"{autodir}.{name}"
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write('')

    if value != '':
        rw = 'w'
    else:
        rw = 'r'

    with open(path, f'{rw}') as file:
        if rw == 'r':
            return str(file.read())
        elif rw == 'w' and value:
            file.write(str(value))
            return str(value)

def setw(filename:str=''):
    try:
        if filename == '':
            filename = config('last_used') 
            if not os.path.exists(f"{autodir}/{filename}") or filename == "":
                filename = config('last_downloaded')
        if os.path.exists(f"{autodir}/{filename}"):
            os.system(f"feh --no-fehbg --bg-scale {autodir}/{filename}")
            config('last_used', filename)
        else:
            config('last_used','')
            config('last_downloaded','')
            print(f"Wallpaper {filename} moved or deleted: use autowall --list to show available wallpapers and autowall -u <name> set a wallpaper", 1)
    except Exception as e:
        print(f"Error: {e}")

def print(msg, bypass=0):
    if ALLOW or bypass == 1:
        __builtin__.print(msg)

if __name__ == "__main__":
    main()
