#!/usr/bin/env python3
from changelog_scraper import (clear_output_folder, scrape_changelog_version,
                               write_catalog)
from helpers.unity_version import UnityVersion, versiontuple
from version_scraper import find_unity_versions
import argparse
import re
import os

def semver_type(string):
    # Use a regular expression to check that the string is a valid SemVer string
    if not re.fullmatch(r'\d+\.\d+\.\d+', string):
        raise argparse.ArgumentTypeError(f"'{string}' is not a valid SemVer string")
    return string



def test_scrapes(output_path: str, unity_versions: list[UnityVersion], overwrite_output: bool):
    for version in unity_versions:
        scrape_changelog_version(output_path, version, overwrite_output)
    write_catalog(output_path, unity_versions)

def main():
    parser = argparse.ArgumentParser(description='Scrape Unity editor changelogs.')

    # Optional flag: --print-versions or -p
    parser.add_argument('--print-versions', '-p', action='store_true', help='Print available versions')

    # Optional flag: --overwrite-output or -o
    parser.add_argument('--overwrite-output', '-o', action='store_true', default=True, help='Overwrite existing output')

    # Optional flag: --full-set
    parser.add_argument('--full-set', action=argparse.BooleanOptionalAction, default=True, help='Scrape with full versions set')

    # Optional flag: --min-version or -m
    parser.add_argument('--min-version', '-m', type=semver_type, help='Minimal Unity Version to scrape from')

    # Required parameter: output folder (default value: 'output')
    parser.add_argument('--output-folder', default='output', nargs='?', help='Output folder')

    args = parser.parse_args()

    # Print the values of the arguments
    print(f"print_versions: {args.print_versions}")
    print(f"overwrite_output: {args.overwrite_output}")
    print(f"full_set: {args.full_set}")
    print(f"min_version: {args.min_version}")
    output_folder = args.output_folder if 'output_folder' in args else 'output'
    output_path = output_folder if os.path.isabs(output_folder) else os.path.abspath(output_folder)
    print(f"output_folder: {output_folder}, output_path: {output_path}")

    min_unity_version = versiontuple(args.min_version) if args.min_version else None
    overwrite_output = args.overwrite_output

    # clear our output folder
    clear_output_folder(output_path)

    # get unity versions
    unity_versions = find_unity_versions(min_unity_version, args.full_set)
    if args.print_versions:
        print(f"processing {len(unity_versions)} changelogs")
        print([x.name for x in unity_versions])

    # scrape each changelog page
    test_scrapes(output_path, unity_versions, overwrite_output)

main()
