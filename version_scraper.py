import urllib.parse

import requests
from bs4 import BeautifulSoup
from slugify import slugify

from helpers.unity_version import UnityVersion, versiontuple

# constants
UNITY_WHATS_NEW_URL = "https://unity3d.com/unity/whats-new/"
UNITY_BASE_URL = "https://unity3d.com/"
MIN_UNITY_VERSION = versiontuple('5.1')

def create_version_object(list_entry):
    version_name = list_entry.text
    version_url = urllib.parse.urljoin(UNITY_BASE_URL, list_entry['href'])
    return UnityVersion(version_name, version_url)

def filter_unity_version_entries(version_object: UnityVersion):
    """Filters unity version from our list
    
    For now, we ignore version older than < 5.1 and "Archive"
    """
    if not version_object.is_valid:
        return False
    if version_object.version_tuple < MIN_UNITY_VERSION:
        return False
    return True
    
def find_unity_versions():
    """Return a list of "UnityVersion" objects

    Queries the Unity 'whats new' website and scrapes a list of Unity versions and their changelog urls
    """
    page = requests.get(UNITY_WHATS_NEW_URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    version_li_entries = soup.find(id='content-wrapper').select('.select-box a')
    version_list = list(map(lambda x: create_version_object(x), version_li_entries))
    filtered_version_list = list(filter(lambda x: filter_unity_version_entries(x), version_list))
    return filtered_version_list
