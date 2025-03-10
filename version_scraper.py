import urllib.parse

from python_graphql_client import GraphqlClient

from helpers.unity_version import UnityVersion, versiontuple

# constants
UNITY_RELEASES_ENDPOINT = "https://services.unity.com/graphql"
UNITY_WHATS_NEW_URL = "https://unity.com/releases/editor/whats-new/"
UNITY_BASE_URL = "https://unity.com/"
MIN_SUPPORTED_UNITY_VERSION = versiontuple('5.1.0')
UNITY_RELEASES_QUERY = '''
query GetRelease($limit: Int, $skip: Int, $version: String, $stream: [UnityReleaseStream!])
{
  getUnityReleases(
    limit: $limit
    skip: $skip
    stream: $stream
    version: $version
    entitlements: []
  ) {
    totalCount
    edges {
      node {
        version
        releaseDate
        releaseNotes {
            url
        }
      }
    }
    pageInfo {
      hasNextPage
    }
  }
}
'''

def create_version_object_old(list_entry):
    version_name = list_entry.text
    version_url = urllib.parse.urljoin(UNITY_BASE_URL, list_entry['href']) # https://unity3d.com/releases/editor/whats-new/2018.4.0
    return UnityVersion(version_name, version_url)

def create_version_object(list_entry):
    version_name = list_entry['version']
    changelog_url = list_entry['release_notes_url']
    release_date = list_entry['release_date']
    return UnityVersion(version_name, None, changelog_url, release_date)

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
    if min_unity_version is not None and version_object.version_tuple < min_unity_version:
        #print('version doesnt satisfy min version: %s, min_unity_version: %s'%(version_object.version_tuple, min_unity_version))
        return False
    return True
    
def get_unity_releases():
    client = GraphqlClient(endpoint=UNITY_RELEASES_ENDPOINT)
    stream = []
    version = ''

    #variables = {
    #    "limit": "1000", 
    #    "skip": 0
    #}
    variables = {
        "limit": 1000,
        "skip": 0
    }

    results = []
    while (True):
        result = client.execute(query=UNITY_RELEASES_QUERY, variables=variables)
        data = result['data']
        edges = data['getUnityReleases']['edges']
        for edge in edges:
            node = edge['node']
            version = node['version']
            url = node['releaseNotes']['url']
            release_date = node['releaseDate']
            version_object = { 
                "version": version,
                "release_notes_url": url,
                "release_date": release_date 
            }
            results.append(version_object)
      
        if (data['getUnityReleases']['pageInfo']['hasNextPage'] == False):
            break  

        variables['skip'] += variables['limit'];
    

    return results;
    #print(result)

def find_unity_versions(min_unity_version:versiontuple, test_full_set: bool, max_scrapes: int):
    """Return a list of "UnityVersion" objects

    Queries the Unity 'whats new' website and scrapes a list of Unity versions and their changelog urls
    """
    version_li_entries = get_unity_releases()
    version_list = list(map(lambda x: create_version_object(x), version_li_entries))
    version_objects = list(filter(lambda x: filter_unity_version_entries(x, min_unity_version), version_list))

    print('-'*10)
    print('Starting scrape test with \033[1m%s\033[0m test set'%('full' if test_full_set else 'partial'))
    print('-'*10)

    if not test_full_set:
        version_objects = version_objects[slice(10, len(version_objects), 5)]

    # sort
    version_objects = sorted(version_objects, key=lambda x: x.version_tuple)

    # clamp the maximum amount of versions if max_scrapes is defined
    num_versions = len(version_objects)
    if max_scrapes != -1:
        num_versions = max(1, min(max_scrapes, num_versions))
        version_objects = version_objects[0:num_versions]

    return version_objects
