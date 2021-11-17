#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from slugify import slugify
from packaging import version

UNITY_BASE_URL = "https://unity3d.com/"
UNITY_WHATS_NEW_URL = "https://unity3d.com/unity/whats-new/"
#UNITY_BETA_RSS = "https://unity3d.com/unity/beta/latest.xml"
#UNITY_LTS_RSS = "https://unity3d.com/unity/lts-releases.xml"
#UNIT_RELEASES_RSS = "https://unity3d.com/unity/releases.xml"
MIN_UNITY_VERSION = version.parse('5.0')

def create_unity_version_object(list_entry):
    version_name = list_entry.text
    version_url = urllib.parse.urljoin(UNITY_BASE_URL, list_entry['href'])
    return {'name': version_name, 'url': version_url}

def versiontuple(v):
    return tuple(map(int, (v.split("."))))

def filter_unity_version_entries(version_entry):
    """Filters unity version from our list
    
    For now, we ignore version older than < 5.0 and "Archive"
    """
    version_name = version_entry.text
    version_url_friendly = version_entry['href'].rsplit('/', 1)[-1]
    if version_name == 'Archive':
        return False
    return True
    version_string = version_url_friendly.replace('unity-', '') #version_name.replace('Unity', '').strip().replace(' ', '.')
    regex_match = re.match('^([0-9]+)\.([0-9]+)(?:\.([0-9]+))?(?:[abf]([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?', version_string)
    current_version_tuple = regex_match.groups()
    #if (versiontuple(current_version_tuple) < versiontuple('5.0')):
    #    print('skipping: %s'%','.join(current_version_tuple))
    #print(regex_match.groups())
    return False
    unity_version = version.parse(version_string) 
     
    if unity_version < MIN_UNITY_VERSION:
        return False
    return True

def find_unity_versions():
    """Return a list of "{name, url}" objects

    Queries the Unity 'whats new' website and scrapes a list of Unity versions and their changelog urls
    """
    page = requests.get(UNITY_WHATS_NEW_URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    version_li_entries = soup.find(id='content-wrapper').select('.select-box a')
    filtered_li_entries = filter(lambda x: filter_unity_version_entries(x), version_li_entries)
    version_list = list(map(lambda x: create_unity_version_object(x), filtered_li_entries))
    return version_list

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
print(unity_versions)
#scrape_changelog_versions(unity_versions)

# individual tests
#scrape_version = 'Unity 2021.1.21' 
#scrape_version = 'Unity 5.6.4'
#scrape_version = 'Unity 2022.1.0 Alpha 13'
#unity_version = next((e for e in unity_versions if e['name'] == scrape_version), None)
#scrape_changelog_version(unity_version)