import datetime
import json
import re
from pathlib import Path

import jsontree
import requests
from bs4 import BeautifulSoup

from helpers.unity_version import UnityVersion

MAIN_CATEGORIES=['Release Notes', 'Fixes', 'Known Issues', 'Entries since']
IGNORE_CATEGORIES=['System Requirements', 'System Requirements Changes']
OUTPUT_FOLDER_NAME='./output'

class ChangelogEntry:
    def __init__(self, list_entry):
        self.list_entry = list_entry
        self.parse_list_entry()

    def parse_list_entry(self):
        entry_text = self.list_entry.text
        #regex_match = re.match("^(.*?)(?:\:\s)(.*)", entry_text)
        regex_match = re.match("^((.*?)[?:\:]\s)?(Added|Removed|Changed|Fixed|Updated|Deprecated)?\s?(.*)", entry_text)
        match_groups = regex_match.groups()
        if len(match_groups) != 4:
            print("Failed to parse entry: %s"%entry_text)
            return
        if match_groups[1] is not None:
            self.type = self.strip_type(match_groups[1])
        else:
            self.type = None
        self.modification = match_groups[2] # optional group
        self.title = match_groups[3].title()

    def strip_type(self, type_text):
        return re.sub("^(?:\(.*\) - )", '', type_text).strip()


def is_main_category(category_name: str):
    for main_category_name in MAIN_CATEGORIES:
        if main_category_name in category_name:
            return True
    return False

def is_header_tag_parent(header_tag1, header_tag2):
    return (header_tag1.name > header_tag2.name)

def key_exists(json_tree:jsontree, key:str):
    return json_tree.get(key, None) is not None

def create_entries_list(list_entries):
    return list(map(lambda x: ChangelogEntry(x), list_entries))

def create_list_entry(changelog:ChangelogEntry):
    if changelog.modification is not None:
        return "[%s] [%s] --> %s"%(changelog.type, changelog.modification, changelog.title)
    return "[%s] --> %s"%(changelog.type, changelog.title)

def scrape_changelog_page(file_name, changelog_url):
    print('Scraping version from url: %s'%changelog_url)

    page = requests.get(changelog_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    root_node = jsontree.jsontree() # our root json tree
    current_category_label = None # known issues, release notes, new entries since ...
    current_sub_category_label = None # improvements, changes, fixes, etc 

    for ul_element in soup.find_all(lambda tag: tag.name == "ul" and (tag.find_previous_sibling(name='h3') or tag.find_previous_sibling(name='h4'))):
        list_entries = ul_element.find_all('li', recursive=False)
        # ignore empty lists 
        if (len(list_entries) == 0):
            continue

        # find the main category
        neighbour_header = ul_element.find_previous_sibling('h3') or ul_element.find_previous_sibling('h2')
        if current_category_label is None or current_category_label != neighbour_header.text:
            current_category_label = neighbour_header.text

        # find the sub category
        neighbour_header_small = ul_element.find_previous_sibling('h4')
        if neighbour_header_small is not None: 
            if current_sub_category_label != neighbour_header_small.text:
                current_sub_category_label = neighbour_header_small.text
        else: # no subheader found, use the main category...            
            current_sub_category_label = current_category_label

        # skip if this category is to be ignored
        if current_sub_category_label in IGNORE_CATEGORIES:
            continue

        # create a list of ChangelogEntry items
        changelog_entries = create_entries_list(list_entries)
        # transform those entries to a temporary label that we can read
        changelog_labels = list(map(lambda x:create_list_entry(x), changelog_entries))

        # if the sub cateogry is the same as the main category, directly assign the list
        if current_sub_category_label == current_category_label:
            root_node[current_category_label] = changelog_labels
        else: # otherwise, append it to the sub category node, but only if it exists
            # check if our sub category already exists
            if key_exists(root_node, current_category_label) and key_exists(root_node.get(current_category_label), current_sub_category_label): 
                root_node[current_category_label][current_sub_category_label] += changelog_labels
            else: # otherwise, add a new entry
                root_node[current_category_label][current_sub_category_label] = changelog_labels

    json_text = jsontree.dumps(root_node, indent=3)
    write_json_file(file_name, json_text)

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def write_json_file(file_name, json_text):
    ensure_dir(OUTPUT_FOLDER_NAME)
    file_path = Path(OUTPUT_FOLDER_NAME).joinpath(file_name)
    with open(file_path, 'w') as f:
        f.write(json_text)

def changelog_json_exists(file_name):
    file_path = Path(OUTPUT_FOLDER_NAME).joinpath(file_name)
    return Path.exists(file_path)

def scrape_changelog_version(unity_version : UnityVersion, overwrite_output):
    if (not overwrite_output and changelog_json_exists(unity_version.file_name)):
        print ('Skipping \'%s\', output already exists...'%unity_version.name)
        return
    scrape_changelog_page(unity_version.file_name, unity_version.url)

def scrape_changelog_versions(unity_versions: list[UnityVersion]):
    for version in unity_versions:
        try:
            scrape_changelog_version(version)
        except Exception as ex:
            print('Failed to scrape version "%s", exception: %s'%(version['name'], ex))


def write_catalog():
    # get the files in the output folder
    p = Path(OUTPUT_FOLDER_NAME).glob('**/*.json')
    # filter on files and ignore catalog file
    files = [x.name for x in p if x.is_file() and "catalog" not in x.name]
    # construct our json
    root_node = jsontree.jsontree() 
    root_node.date_modified = datetime.datetime.utcnow()
    root_node.changelogs = files
    # export to text and write
    json_text = jsontree.dumps(root_node, indent=3)
    write_json_file('catalog.json', json_text)

def test_scrapes(unity_versions: list[UnityVersion]):
    overwrite_output = False
    #scrape_changelog_version(unity_versions[0])
    #for i in range(10, len(unity_versions), 5):
    #    scrape_changelog_version(unity_versions[i], overwrite_output)
    for i in range(10, len(unity_versions), 5):
        scrape_changelog_version(unity_versions[i], overwrite_output)

    write_catalog()
