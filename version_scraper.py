import urllib.parse

import requests
from bs4 import BeautifulSoup
from slugify import slugify

from helpers.unity_version import UnityVersion, versiontuple

# constants
UNITY_WHATS_NEW_URL = "https://unity.com/releases/editor/whats-new/"
UNITY_BASE_URL = "https://unity.com/"
MIN_SUPPORTED_UNITY_VERSION = versiontuple('5.1.0')

def create_version_object(list_entry):
    version_name = list_entry.text
    version_url = urllib.parse.urljoin(UNITY_BASE_URL, list_entry['href']) # https://unity3d.com/releases/editor/whats-new/2018.4.0
    return UnityVersion(version_name, version_url)

def filter_unity_version_entries(version_object: UnityVersion, min_unity_version: versiontuple):
    """Filters unity version from our list
    
    For now, we ignore version older than < 5.1 and "Archive"
    """
    if not version_object.is_valid:
        #print('version object not valid: %s'%version_object.version_string)
        return False
    if version_object.version_tuple < MIN_SUPPORTED_UNITY_VERSION:
        #print('version not supported: %s'%version_object.version_tuple)
        return False
    if min_unity_version is not None and  version_object.version_tuple < min_unity_version:
        #print('version doesnt satisfy min version: %s, min_unity_version: %s'%(version_object.version_tuple, min_unity_version))
        return False
    return True
    
def find_unity_versions(min_unity_version:versiontuple = None):
    """Return a list of "UnityVersion" objects

    Queries the Unity 'whats new' website and scrapes a list of Unity versions and their changelog urls
    """
    agent_headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    page = requests.get(UNITY_WHATS_NEW_URL, headers=agent_headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    sidebar_div = soup.find('div', {"class", 'releases-item-list'})
    version_li_entries = sidebar_div.findAll('a')
    version_list = list(map(lambda x: create_version_object(x), version_li_entries))
    filtered_version_list = list(filter(lambda x: filter_unity_version_entries(x, min_unity_version), version_list))
    return filtered_version_list
