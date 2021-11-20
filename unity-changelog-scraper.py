#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from slugify import slugify
from helpers import UnityVersion, versiontuple
from version_scraper import find_unity_versions

UNITY_BASE_URL = "https://unity3d.com/"
UNITY_WHATS_NEW_URL = "https://unity3d.com/unity/whats-new/"
#UNITY_BETA_RSS = "https://unity3d.com/unity/beta/latest.xml"
#UNITY_LTS_RSS = "https://unity3d.com/unity/lts-releases.xml"
#UNIT_RELEASES_RSS = "https://unity3d.com/unity/releases.xml"


def is_header_tag_parent(header_tag1, header_tag2):
    return (header_tag1.name > header_tag2.name)

def scrape_changelog_page(file_name, changelog_url):
    page = requests.get(changelog_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    print('Scraping version from url: %s'%changelog_url)
    
    current_category_label = None # known issues, release notes, new entries since ...
    current_sub_category_label = None # improvements, changes, fixes, etc 
    for label in soup.find_all(lambda tag: tag.name == "ul" and (tag.find_previous_sibling('h3') or tag.find_previous_sibling('h4'))):
        list_entries = label.find_all('li')
        entry_count = len(list_entries)
        if (entry_count == 0):
            continue

        neighbour_header = label.find_previous_sibling('h3') or label.find_previous_sibling('h2')
        if current_category_label is None or current_category_label.text != neighbour_header.text:
            current_category_label = neighbour_header

        neighbour_header_small = label.find_previous_sibling('h4')
        if neighbour_header_small is not None:
            current_sub_category_label = neighbour_header_small
        else:
            current_sub_category_label = current_category_label

        # current category is also a sub category
        if current_category_label == current_sub_category_label:
            print('[%s] %d entries'%(current_category_label.text, entry_count))
        else:
            print('[%s] [%s] %d entries'%(current_category_label.text, current_sub_category_label.text, entry_count))

def changelog_json_exists(file_name):
    return False

def scrape_changelog_version(unity_version):
    version_file_name = '%s.json'%slugify(unity_version['name'])
    if (changelog_json_exists(version_file_name)):
        return
    scrape_changelog_page(version_file_name, unity_version['url'])

def scrape_changelog_versions(unity_versions):
    for version in unity_versions:
        try:
            scrape_changelog_version(version)
        except Exception as ex:
            print('Failed to scrape version "%s", exception: %s'%(version['name'], ex))


unity_versions = find_unity_versions()
print([x.name for x in unity_versions])
#scrape_changelog_versions(unity_versions)

# individual tests
#scrape_version = 'Unity 2021.1.21' 
#scrape_version = 'Unity 5.6.4'
#scrape_version = 'Unity 2022.1.0 Alpha 13'
#unity_version = next((e for e in unity_versions if e['name'] == scrape_version), None)
#scrape_changelog_version(unity_version)