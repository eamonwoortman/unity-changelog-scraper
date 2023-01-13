import re
import json
                            
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
    return versiontuple(filter(lambda x: x is not None, regex_match.groups()))

class UnityVersion:
    def __init__(self, name, url):
        self.name = name
        self.version_string = url.rsplit('/', 1)[-1].replace('unity-', '')
        self.file_name = f'{self.version_string}.json'
        self.url = url
        self.is_valid = self.parse_version_object()

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
