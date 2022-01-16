import datetime
import glob
import json
import os
from itertools import groupby
from pathlib import Path
from typing import List

import jsontree
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from helpers.changelog_entry import ChangelogEntry
from helpers.changelog_node import ChangelogNode, ChangelogNodeType
from helpers.collection_helpers import unique
from helpers.unity_version import UnityVersion, parse_version_tuple

MAIN_CATEGORIES=['Release Notes', 'Fixes', 'Known Issues', 'Entries since']
IGNORE_CATEGORIES=['System Requirements', 'System Requirements Changes']
OUTPUT_FOLDER_NAME='./output'


def is_main_category(category_name: str):
    for main_category_name in MAIN_CATEGORIES:
        if main_category_name in category_name:
            return True
    return False

def is_header_tag_parent(header_tag1, header_tag2):
    return (header_tag1.name > header_tag2.name)

def key_exists(json_tree:jsontree, key:str):
    return json_tree.get(key, None) is not None

def create_entries_list(list_entries: ResultSet[Tag], override_modification = None) -> List['ChangelogEntry']:
    return list(map(lambda x: ChangelogEntry(x, override_modification), list_entries))

def create_list_entry(changelog:ChangelogEntry):
    if changelog.modification is not None:
        return { 'label': changelog.modification, 'title': changelog.content }
    return "%s" % (changelog.content)


def create_category_node(current_group):
    key = current_group[0]
    entries = list(current_group[1])
    new_node = ChangelogNode(key, ChangelogNodeType.ModificationType)
    new_node.add_entries([create_list_entry(entry) for entry in entries])
    return new_node


last_checked = []

def get_modification_override(category_label):
    override_keywords = { 'Fixed': 'Fixed', 'Fixes': 'Fixed', 
    'Known issues': 'Bug', 'Known Issues': 'Bug', 
    'Improvement': 'Improvements', 'Improvements': 'Improved', 
    'API Changes': 'API Change', 
    'Change':'Changed', 'Changes': 'Changed',  
    'Feature': 'New', 'Features': 'New' }

    for key, value in override_keywords.items():
        if key in category_label:
            return value

    # debugging only
    if category_label not in last_checked:
        print('Not matching label: %s'%category_label)
        last_checked.append(category_label)

    return None

def scrape_changelog_page(version_name, file_name, changelog_url, slug):
    print('Scraping version from url: %s'%changelog_url)

    page = requests.get(changelog_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    json_root = jsontree.jsontree() # our root json tree
    json_root['version'] = version_name
    json_root['slug'] = slug
    json_root['url'] = changelog_url
    category_types = []
    json_root['category_types'] = category_types 
    root_node = ChangelogNode()

    change_types = []
    current_category_label = None # known issues, release notes, new entries since ...
    current_sub_category_label = None # improvements, changes, fixes, etc 
    current_main_category_node = None
    current_sub_category_node = None
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
        override_modification = get_modification_override(current_sub_category_label) or get_modification_override(current_category_label)
        changelog_entries = create_entries_list(list_entries, override_modification)
        change_types += list(map(lambda x: x.modification, changelog_entries))

        # create a category node for each changelog entry that has 'type' assigned
        grouped_changelog_entries = list(map(create_category_node, groupby(changelog_entries, lambda f: (f.type if f.type else 'General'))))
        category_types += list(map(lambda x: x.name, list(filter(lambda x: x.name not in category_types, grouped_changelog_entries))))

        # if the sub cateogry is the same as the main category, directly assign the list
        if current_sub_category_label == current_category_label:
            type = ChangelogNodeType.MainCategory if is_main_category(current_category_label) else ChangelogNodeType.ChangeType
            current_main_category_node = ChangelogNode(current_category_label, type)
            # add the entries (list of strings or objects), grouped by its type
            current_main_category_node.add_children(grouped_changelog_entries)
            root_node.add_child(current_main_category_node)
        else: # otherwise, append it to the sub category node, but only if it exists
            # check if our sub category already exists
            current_main_category_node = root_node.get(current_category_label)
            current_sub_category_node = current_main_category_node and current_main_category_node.get(current_sub_category_label)
            if current_sub_category_node is not None: 
                # add the entries (list of strings)
                current_sub_category_node.add_children(grouped_changelog_entries)
            else: # otherwise, add a new entry
                if current_main_category_node is None:
                    current_main_category_node = root_node.create_child(current_category_label, ChangelogNodeType.MainCategory)
                if current_main_category_node.key_exists(current_sub_category_label) is False:
                    current_sub_category_node = current_main_category_node.create_child(current_sub_category_label, ChangelogNodeType.ChangeType)
                # add the entries (list of strings)
                current_sub_category_node.add_children(grouped_changelog_entries)

    
    json_root['change_types'] = unique(change_types)
    json_root['categories'] = root_node.toJSON()
    json_text = jsontree.dumps(json_root, indent=3)
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
    scrape_changelog_page(unity_version.name, unity_version.file_name, unity_version.url, unity_version.version_string)

def scrape_changelog_versions(unity_versions: list[UnityVersion]):
    for version in unity_versions:
        try:
            scrape_changelog_version(version, True)
        except Exception as ex:
            print('Failed to scrape version "%s", exception: %s'%(version['name'], ex))
    write_catalog(unity_versions)

def sort_changelog_files(file_dict):
    file_name_no_ext = os.path.splitext(file_dict['file_name'])[0]
    version_tuple = parse_version_tuple(file_name_no_ext)
    return version_tuple

def load_version_file(file_path:str):
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data

def create_catalog_entry(file_path:Path, unity_versions: list[UnityVersion]):
    entry = dict()
    version = next((f for f in unity_versions if f.file_name == file_path.name), "none")
    entry['version'] = version.name
    entry['file_name'] = file_path.name
    entry['slug'] = version.version_string
    return entry


def accumulate_meta_data(files:list, category_types, change_types):
    for file_path in files:
        version_file = load_version_file(str(file_path))
        version_category_types = list(filter(lambda x: x not in category_types, version_file['category_types']))
        category_types += version_category_types
        version_change_types = list(filter(lambda x: x not in change_types, version_file['change_types']))
        change_types += version_change_types
    
def clear_output_folder():
    try:
        filelist = glob.glob(os.path.join(OUTPUT_FOLDER_NAME, "*"))
        for f in filelist:
            os.remove(f)
    except:
        pass

def write_catalog(unity_versions: list[UnityVersion]):
    # get the files in the output folder
    p = Path(OUTPUT_FOLDER_NAME).glob('**/*.json')
    # filter on files and ignore catalog file
    version_files = list(filter(lambda x: x.is_file() and "catalog", p))
    files = [create_catalog_entry(x, unity_versions) for x in version_files]
    files.sort(reverse=True, key=sort_changelog_files)
    # get the meta data
    category_types = []
    change_types = []
    accumulate_meta_data(version_files, category_types, change_types)
    # construct our json
    root_node = jsontree.jsontree() 
    root_node.date_modified = datetime.datetime.utcnow()
    root_node.category_types = sorted(unique(category_types))
    root_node.change_types = sorted(unique(change_types))
    root_node.changelogs = files
    # export to text and write
    json_text = jsontree.dumps(root_node, indent=3)
    write_json_file('catalog.json', json_text)
