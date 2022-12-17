#!/usr/bin/env python3
from changelog_scraper import (clear_output_folder, scrape_changelog_version,
                               write_catalog)
from helpers.unity_version import UnityVersion, versiontuple
from version_scraper import find_unity_versions
import argparse
import re

def semver_type(string):
    # Use a regular expression to check that the string is a valid SemVer string
    if not re.fullmatch(r'\d+\.\d+\.\d+', string):
        raise argparse.ArgumentTypeError(f"'{string}' is not a valid SemVer string")
    return string



def test_scrapes(unity_versions: list[UnityVersion], overwrite_output: bool, test_full_set: bool):
    test_versions = [
#       '2022.1.0.13', 
#       '2021.1.21', 
#       '2021.2.5', 
#       '5.1.2',
#       '5.6.4',
#        '5.2.1',
#        '2021.2.0'    
#        '2018.2.4'
    ]
    
    print('-'*10)
    print('Starting scrape test with \033[1m%s\033[0m test set'%('full' if test_full_set else 'partial'))
    print('-'*10)

    test_specific_version = len(test_versions) > 0
    if test_specific_version:
        version_objects = (x for x in unity_versions if any(x.version_string == w for w in test_versions))
    elif test_full_set:
        version_objects = unity_versions
    else:
        version_objects = unity_versions[slice(10, len(unity_versions), 5)]

    for version in version_objects:
        scrape_changelog_version(version, overwrite_output)

    #for i in range(10, len(unity_versions), 5):
    #    scrape_changelog_version(unity_versions[i], overwrite_output)

    write_catalog(unity_versions)

def main():
    parser = argparse.ArgumentParser(description='Scrape Unity editor changelogs.')

    # Optional flag: --print-versions or -p
    parser.add_argument('--print-versions', '-p', action='store_true', help='Print available versions')

    # Optional flag: --overwrite-output or -o
    parser.add_argument('--overwrite-output', '-o', action='store_true', default=True, help='Overwrite existing output')

    # Optional flag: --full-set
    parser.add_argument('--full-set', action='store_true', help='Scrape with full versions set')

    # Optional flag: --min-version or -m
    parser.add_argument('--min-version', '-m', type=semver_type, help='Minimal Unity Version to scrape from')

    # Required parameter: output folder (default value: 'output')
    parser.add_argument('output-folder', default='output', nargs='?', help='Output folder')

    args = parser.parse_args()

    # Print the values of the arguments
    print(f"print_versions: {args.print_versions}")
    print(f"overwrite_output: {args.overwrite_output}")
    print(f"full_set: {args.full_set}")
    print(f"min_version: {args.min_version}")
    output_folder = args.output_folder if 'output_folder' in args else 'output'
    print(f"output_folder: {output_folder}")

    min_unity_version = versiontuple(args.min_version) if args.min_version else None
    overwrite_output = args.overwrite_output

    # clear our output folder
    clear_output_folder()

    # get unity versions
    unity_versions = find_unity_versions(min_unity_version)
    if args.print_versions:
        print([x.name for x in unity_versions])

    # scrape each changelog page
    test_scrapes(unity_versions, overwrite_output, args.full_set)

main()
