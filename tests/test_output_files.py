import json
import unittest
from pathlib import Path
from unittest import TestCase, mock

from ddt import ddt, idata


class NamedDict(dict):
    pass

def get_file_data(glob_pattern):
    result = []

    for file in Path(__file__).parent.glob(glob_pattern):
        if 'catalog' in file.name:
            continue
        with open(file) as reader:
            json_data = json.load(reader)
            dataitem = NamedDict(json_data)
            setattr(dataitem, '__name__', file.name)
            result.append(dataitem)

    return result


@ddt
class TestFileDatas(TestCase):
    @idata(get_file_data('../output/*.json'))
    def test_file_data(self, changelog):
        self.assert_categories_types_valid(changelog)


    def assert_category_type_valid(self, category_type):
        self.longMessage = True
        self.assertFalse(not category_type, 'Category type is empty')
        #self.assertFalse(not category_type, 'Category type: "%s"'%category_type)
        
        return True

    def assert_categories_types_valid(self, changelog):
        categories_types = changelog['category_types']
        for category_type in categories_types:
            self.assert_category_type_valid(category_type)

