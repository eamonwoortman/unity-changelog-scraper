import json
from pathlib import Path
from unittest import TestCase

from ddt import ddt, idata


# wrapper class to allow asignment of __name__
class NamedDict(dict):
    pass

def get_file_data(glob_pattern):
    result = []

    for file in Path(__file__).parent.glob(glob_pattern):
        if 'catalog' in file.name:
            continue
        with open(file, mode="r", encoding="utf-8") as reader:
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
        return True

    def assert_category_type_valid(self, category_type):
        self.longMessage = True
        self.assertFalse(not category_type, 'Category type is empty')
        self.assertLess(len(category_type), 50,'Category type is too long: %s(%d)'%(category_type, len(category_type)))
        self.assertLess(len(category_type.split()), 4, 'Category type is too long: %s(%d)'%(category_type, len(category_type)))

    def assert_categories_types_valid(self, changelog):
        categories_types = changelog['category_types']
        for category_type in categories_types:
            self.assert_category_type_valid(category_type)

