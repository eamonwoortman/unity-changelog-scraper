#!/usr/bin/env python3
from changelog_scraper import scrape_changelog_versions, test_scrapes
from version_scraper import find_unity_versions

UNITY_BASE_URL = "https://unity3d.com/"
UNITY_WHATS_NEW_URL = "https://unity3d.com/unity/whats-new/"
#UNITY_BETA_RSS = "https://unity3d.com/unity/beta/latest.xml"
#UNITY_LTS_RSS = "https://unity3d.com/unity/lts-releases.xml"
#UNIT_RELEASES_RSS = "https://unity3d.com/unity/releases.xml"

# get unity versions
unity_versions = find_unity_versions()
print([x.name for x in unity_versions])

# scrape each changelog page
test_scrapes(unity_versions)


# individual tests
#scrape_version = 'Unity 2021.1.21'
#scrape_version = 'Unity 5.6.4'
#scrape_version = 'Unity 2022.1.0 Alpha 13'
#unity_version = next((e for e in unity_versions if e['name'] == scrape_version), None)
#scrape_changelog_version(unity_version)
