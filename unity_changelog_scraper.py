#!/usr/bin/env python3
from changelog_scraper import (clear_output_folder, scrape_changelog_version,
                               write_catalog)
from helpers.unity_version import UnityVersion, versiontuple
from version_scraper import find_unity_versions
import argparse
import re
import os
import aiohttp
import asyncio
import platform

def semver_type(string):
    # Use a regular expression to check that the string is a valid SemVer string
    if not re.fullmatch(r'\d+\.\d+\.\d+', string):
        raise argparse.ArgumentTypeError(f"'{string}' is not a valid SemVer string")
    return string

async def scrape_pages(output_path: str, unity_versions: list[UnityVersion]):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[scrape_changelog_version(session, output_path, idx, unity_version) for idx, unity_version in enumerate(unity_versions)])
    # write_catalog(output_path, unity_versions)

def main():
    parser = argparse.ArgumentParser(description='Scrape Unity editor changelogs.')

    # Optional flag: --print-versions or -p
    parser.add_argument('--print-versions', '-p', action='store_true', help='Print available versions')

    # Optional flag: --full-set
    parser.add_argument('--full-set', action=argparse.BooleanOptionalAction, default=True, help='Scrape with full versions set')

    # Optional flag: --min-version or -m
    parser.add_argument('--min-version', '-m', type=semver_type, help='Minimal Unity Version to scrape from')

    # Optional flag: --max-scrapes or -m
    parser.add_argument('--max-scrapes', '-s', type=int, default=-1, help='Maximum amount of versions to scrape')

    # Required parameter: output folder (default value: 'output')
    parser.add_argument('--output-folder', default='output', nargs='?', help='Output folder')

    args = parser.parse_args()

    # Print the values of the arguments
    print(f"print_versions: {args.print_versions}")
    print(f"full_set: {args.full_set}")
    print(f"min_version: {args.min_version}")
    print(f"max_scrapes: {args.max_scrapes}")
    output_folder = args.output_folder if 'output_folder' in args else 'output'
    output_path = output_folder if os.path.isabs(output_folder) else os.path.abspath(output_folder)
    print(f"output_folder: {output_folder}, output_path: {output_path}")

    min_unity_version = versiontuple(args.min_version) if args.min_version else None

    # clear our output folder
    clear_output_folder(output_path)

    # get unity versions
    unity_versions = find_unity_versions(min_unity_version, args.full_set, args.max_scrapes)
    if args.print_versions:
        print(f"processing {len(unity_versions)} changelogs")
        print([x.name for x in unity_versions])

    # workaround for Windows bug
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # scrape each changelog page
    asyncio.run(scrape_pages(output_path, unity_versions))


main()
