
# define transforms
transformers = {
    'category_types': [
        { "pattern": "(?i)asset\\s(Import.*|pipeline|management)", "replacement": "Asset Importer" }
    ]
}

# main options dict
options = {
    'transformers': transformers,
}
