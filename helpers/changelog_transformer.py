import re

from config import options

Object = lambda **kwargs: type("Object", (), kwargs)

class ChangelogTransformer:
    def __init__(self) -> None:
        self.transformers = {}
        self.transform_cache = {}
        self.transform_cache['category_types'] = {}
        self.transform_data = options['transformers']
        for key in self.transform_data:
            self.transformers[key] = list(map(self.compile_regex, self.transform_data[key]))
        self.category_type_transforms = self.transformers['category_types']

    def compile_regex(self, transformer):
        return Object(pattern = re.compile(transformer['pattern']), replacement = transformer['replacement'])

    def transform_part(self, part, part_transforms):
        for transform in part_transforms:
            pattern = transform.pattern
            replacement = transform.replacement
            match = pattern.search(part)
            if match is not None:
                return replacement
        return part

    def transform_category_type(self, category_type):
        if category_type in self.transform_cache['category_types']:
            return self.transform_cache['category_types'][category_type]
        transformed_type = self.transform_part(category_type, self.category_type_transforms)
        if transformed_type not in self.transform_cache['category_types']:
            self.transform_cache['category_types'][category_type] = transformed_type
        return transformed_type
