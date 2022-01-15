#!/usr/bin/env python3
from changelog_scraper import (clear_output_folder, scrape_changelog_version,
                               write_catalog)
from helpers.unity_version import UnityVersion
from version_scraper import find_unity_versions


def test_scrapes(unity_versions: list[UnityVersion]):
    overwrite_output = True
    test_full_set = False
    test_versions = [
#       '2022.1.0.13', 
#       '2021.1.21', 
#       '2021.2.5', 
#       '5.1.2',
#       '5.6.4',
#        '5.2.1',
#        '2021.2.0'    
        '2018.2.4'
    ]
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
    print_versions = False
    # clear our output folder
    clear_output_folder()

    # get unity versions
    unity_versions = find_unity_versions()
    if print_versions:
        print([x.name for x in unity_versions])

    # scrape each changelog page
    test_scrapes(unity_versions)

main()
