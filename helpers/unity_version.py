from numbers import Number
import re
import urllib

UNITY_WHATS_NEW_URL = "https://unity.com/releases/editor/whats-new/"
VERSION_REGEX_PATTERN = regex = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:(?P<prereleasetype>[abf])(?P<prereleasenumber>\d+))?"

def versiontuple(v):
    if isinstance(v, str):
        return tuple(map(int, (v.split("."))))
    return tuple(v)

def parse_unity_version(version_string):
    version_match = re.search(VERSION_REGEX_PATTERN, version_string)
    if (version_match is None or len(version_match.groups()) == 0):
        return None
    return version_match.group(0)

def parse_version_tuple(version_string):
    regex_match = re.search(VERSION_REGEX_PATTERN, version_string)
    match_groups = regex_match.groups()
    return versiontuple(filter(lambda x: x is not None and isinstance(x, Number), match_groups))

class UnityVersion:
    def __init__(self, name, url, changeset_url, release_date):
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
        self.release_date = release_date
        
    def parse_version_object(self):
        if self.name == 'Archive':
            return False

        regex_match = re.search(VERSION_REGEX_PATTERN, self.version_string)
        match_groups = tuple(filter(lambda x: x is not None, regex_match.groups()))

        if (len(match_groups) > 4):
            version = (int(match_groups[0]), int(match_groups[1]), int(match_groups[2]), int(match_groups[4]))
        else:
            version = (int(match_groups[0]), int(match_groups[1]), int(match_groups[2]))

        self.version_tuple = version
        self.object = {
            'major': int(version[0]),
            'minor': int(version[1]),
            'patch': int(version[2])
        }

        if len(version) > 3:
            self.object['prereleasetype'] = match_groups[3]
            self.object['prereleasenumber'] = int(version[3])
        
        return True

    def create_hash(self):
        hash = (self.object['major'] * 100000000) + (self.object['minor'] * 1000000) + (self.object['patch'] * 10000)
        if 'prereleasenumber' in self.object:
            hash = hash + (1 + self.object['prereleasenumber'])
        return hash