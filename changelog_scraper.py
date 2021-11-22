import datetime
import json
from pathlib import Path

import jsontree
import requests
from bs4 import BeautifulSoup

from helpers.unity_version import UnityVersion

MAIN_CATEGORIES=['Release Notes', 'Fixes', 'Known Issues', 'Entries since']
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

def scrape_changelog_page(file_name, changelog_url):
    page = requests.get(changelog_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    print('Scraping version from url: %s'%changelog_url)
    
    root_node = jsontree.jsontree()

    current_category_label = None # known issues, release notes, new entries since ...
    current_sub_category_label = None # improvements, changes, fixes, etc 
    current_main_category_list = None
    current_sub_category_list = None
    for label in soup.find_all(lambda tag: tag.name == "ul" and (tag.find_previous_sibling('h3') or tag.find_previous_sibling('h4'))):
        list_entries = label.find_all('li')
        entry_count = len(list_entries)
        if (entry_count == 0):
            continue

        # find the main category
        neighbour_header = label.find_previous_sibling('h3') or label.find_previous_sibling('h2')
        if current_category_label is None or current_category_label.text != neighbour_header.text:
            print('setting new category: %s'%neighbour_header.text)
            current_category_label = neighbour_header
            #current_main_category_list = {}
            #root_node[current_category_label.text] = current_main_category_list

        # find the sub category
        neighbour_header_small = label.find_previous_sibling('h4')
        if neighbour_header_small is not None: 
            if current_sub_category_label.text != neighbour_header_small.text:
                #current_sub_category_list = []
                #current_main_category_list[current_sub_category_label.text] = current_sub_category_list
                print('setting sub category: %s, was %s %s'%(neighbour_header_small.text, current_sub_category_label.text, current_sub_category_label.text is not neighbour_header_small.text))
                current_sub_category_label = neighbour_header_small
        else: # no subheader found, use the main category...            
            current_sub_category_label = current_category_label
            #current_sub_category_list = []
            #current_main_category_list[current_sub_category_label.text] = current_sub_category_list
            #current_sub_category_label = current_category_label
            #current_sub_category_list = []
            #current_main_category_list[current_sub_category_label.text] = current_sub_category_list
            
            #print('setting sub category2: %s'%current_category_label.text)

        entry_texts = list(map(lambda x: '%s...'%x.text[0:10], list_entries))
        if current_sub_category_label.text == current_category_label.text:
            root_node[current_category_label.text] = entry_texts
        else: 
            # check if our sub category already exists
            if key_exists(root_node, current_category_label.text) and key_exists(root_node.get(current_category_label.text), current_sub_category_label.text): 
                root_node[current_category_label.text][current_sub_category_label.text] += entry_texts
            else: # otherwise, add a new entry
                root_node[current_category_label.text][current_sub_category_label.text] = entry_texts
        #current_sub_category_list += entry_texts
        # current category is also a sub category
        #if current_category_label == current_sub_category_label:
        #    print('[%s] %d entries'%(current_category_label.text, entry_count))
        #else:
        #    print('[%s] [%s] %d entries'%(current_category_label.text, current_sub_category_label.text, entry_count))

    json_text = jsontree.dumps(root_node, indent=3)
    write_changelog_file(file_name, json_text)
    #print(json_text)


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def write_changelog_file(file_name, json_text):
    ensure_dir(OUTPUT_FOLDER_NAME)
    file_path = Path(OUTPUT_FOLDER_NAME).joinpath(file_name)
    with open(file_path, 'w') as f:
        f.write(json_text)

def changelog_json_exists(file_name):
    return False

def scrape_changelog_version(unity_version : UnityVersion):
    if (changelog_json_exists(unity_version.file_name)):
        return
    scrape_changelog_page(unity_version.file_name, unity_version.url)

def scrape_changelog_versions(unity_versions: list[UnityVersion]):
    for version in unity_versions:
        try:
            scrape_changelog_version(version)
        except Exception as ex:
            print('Failed to scrape version "%s", exception: %s'%(version['name'], ex))


def test_scrapes(unity_versions: list[UnityVersion]):
    scrape_changelog_version(unity_versions[0])
    #for i in range(10, len(unity_versions), 5):
    #    scrape_changelog_version(unity_versions[i])


def json_test():
    data = jsontree.jsontree()
    data.username = 'doug'
    data.meta.date = datetime.datetime.now()
    data.somethingelse = [1,2,3]

    data['username'] == 'doug'

    ser = jsontree.dumps(data)
    ser = ser.encode("utf-8")

    #backagain = jsontree.loads(ser)
    #cloned = jsontree.clone(data)
    backagain = json.loads(ser)
    print(backagain)
