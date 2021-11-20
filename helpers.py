import re
from slugify import slugify

def versiontuple(v):
    if isinstance(v, str):
        return tuple(map(int, (v.split("."))))
    return tuple(map(int, v))

class UnityVersion:
    def __init__(self, name, url):
        self.name = name
        self.file_name = '%s.json'%slugify(name)
        self.url = url
        self.is_valid = self.parse_version_object()

    def parse_version_object(self):
        if self.name == 'Archive':
            return False
        version_url_friendly = self.url.rsplit('/', 1)[-1]
        version_string = version_url_friendly.replace('unity-', '')
        regex_match = re.match('^([0-9]+)\.([0-9]+)(?:\.([0-9]+))?(?:[abf]([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?', version_string)
        self.version_tuple = versiontuple(filter(lambda x: x is not None, regex_match.groups()))
        return True
