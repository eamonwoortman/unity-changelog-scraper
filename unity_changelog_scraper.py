#!/usr/bin/env python3
from changelog_scraper import scrape_changelog_version, write_catalog, clear_output_folder
from helpers.unity_version import UnityVersion
from version_scraper import find_unity_versions

def test_scrapes(unity_versions: list[UnityVersion]):
    overwrite_output = True
    test_versions = [
#        '2022.1.0.13', 
#        '2021.1.21', 
        '2021.2.5', 
#        '5.6.4'
        ]
    
    version_objects = (x for x in unity_versions if any(x.version_string in w for w in test_versions)) # filter(lambda x: all(x.version_string in g for g in test_versions) in x, unity_versions)
    for version in version_objects:
        scrape_changelog_version(version, overwrite_output)

    #for i in range(10, len(unity_versions), 5):
    #    scrape_changelog_version(unity_versions[i], overwrite_output)

    write_catalog(unity_versions)

def main():
    #clear our output folder
    clear_output_folder()

    # get unity versions
    unity_versions = find_unity_versions()
    print([x.name for x in unity_versions])

    # scrape each changelog page
    test_scrapes(unity_versions)

main()