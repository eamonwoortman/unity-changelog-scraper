import re
import urllib

UNITY_WHATS_NEW_URL = "https://unity.com/releases/editor/whats-new/"
VERSION_REGEX_PATTERN = r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:[\.|\-]?(?P<prerelease>[fab]?\d+))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?'

def versiontuple(v):
    if isinstance(v, str):
        return tuple(map(int, (v.split("."))))
    return tuple(map(int, v))

def parse_unity_version(version_string):
    version_match = re.search(VERSION_REGEX_PATTERN, version_string)
    if (version_match is None or len(version_match.groups()) == 0):
        return None
    return version_match.group(0)

def parse_version_tuple(version_string):
    regex_match = re.search(VERSION_REGEX_PATTERN, version_string)
    match_groups = regex_match.groups()[0:3]
    return versiontuple(filter(lambda x: x is not None, match_groups))

class UnityVersion:
    def __init__(self, name, url, changeset_url):
        self.version_string = name
        self.name = name
        self.file_name = f'{self.version_string}.json'
        self.url = url
        self.is_valid = self.parse_version_object()
        self.hash = self.create_hash()
        if url != None:
            self.url = url
        else:
            self.url = urllib.parse.urljoin(UNITY_WHATS_NEW_URL, '.'.join(map(str,self.version_tuple)))
        self.changeset_url = changeset_url
        
    def parse_version_object(self):
        if self.name == 'Archive':
            return False
        self.version_tuple = parse_version_tuple(self.version_string)
        self.create_version_object(self.version_tuple)
        return True

    def create_version_object(self, version):
        self.object = {
            'major': version[0],
            'minor': version[1],
            'patch': version[2]
        }
        if len(version) == 4:
            self.object['pre_release'] = version[3]

    def create_hash(self):
        hash = (self.object['major'] * 100000000) + (self.object['minor'] * 1000000) + (self.object['patch'] * 10000)
        if 'pre_release' in self.object:
            hash = hash + (1 + self.object['pre_release'])
        return hash