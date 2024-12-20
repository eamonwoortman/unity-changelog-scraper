import re

from bs4.element import Tag

from helpers.changelog_transformer import ChangelogTransformer

transformer = ChangelogTransformer()

class ChangelogEntry:
    regex = r"""
    ^(
        (?P<bugprefix>
            (?P<bugcontent>\(.*?\))                          # Bug content enclosed in parentheses
            (?:
                (?P<prefixseperator>[ ]*-[ ]*[:]?[ ]*)       # Optional separator: dash and colon patterns
            )?
            (?:
                (?P<alt_category>
                    (?:\b\w+\b[\s\r\n]*){0,5}               # Alternative category: up to 5 words
                )
                (?:(?:[ ]*[\:][ ]*))?                        # Optional colon after alt category
            )?
        )
        |
        (?:
            (?P<category>
                (?:(?!http|https)\b\w+\b[\s\r\n]*){0,5}     # Category (excluding URLs), up to 5 words
            )
            (?:(?:[ ]*:[ ]*))?                              # Optional colon after category
        )
    )?
    (?P<modification>
        Added|Removed|Changed|Fixed|Updated|Deprecated|Improved|Obsoleted # Specific modification keywords
    )?
    (?:(?:[ ]*:[ ]*))?                                     # Optional colon after modification
    [\s]?
    (?P<content>.*)                                       # Remaining content
    $
    """
    def __init__(self, list_entry:Tag, override_modification):
        self.parse_list_entry(list_entry, override_modification)

    def parse_list_entry(self, list_entry: Tag, override_modification = None):
        has_extended_markup = list_entry.p is not None and len(list_entry.p.contents) > 0
        if has_extended_markup:
            entry_p = list_entry.p
            entry_text_content = str(entry_p.contents[0])
            entry_text = entry_text_content.replace('\n', ' ')
        else:
            entry_text = list_entry.text

        # groups:
        #   [bugprefix, bugcontent, prefixseperator]: '(24241) - )' (optional)
        #   [category, alt_category]: '2D, AI, Android, Linux, ...' (optional)
        #   [modification]: 'Added, Removed, Fixed' (optional)
        #   [content]: 'A crash that occurred when ...'  
        regex_match = re.match(self.regex, entry_text, re.VERBOSE)
        match_groups = regex_match.groupdict()

        # prefix group
        bug_prefix_content = None
        if match_groups['bugprefix']:
            bug_prefix_content = match_groups['bugcontent']

        # category group
        if match_groups['category']:
            self.type = self.strip_type(match_groups['category'])
        elif match_groups['alt_category']:
            self.type = self.strip_type(match_groups['alt_category'])
        else:
            self.type = None
            
        # transform the type / category
        if self.type is not None:
            transformed_type = transformer.transform_category_type(self.type)
            self.type = transformed_type
        else: # otherwise, force it to a 'General' category
            self.type = 'General'

        # modification group
        modification = None
        if match_groups['modification']:
            modification = match_groups['modification'] # optional group
        self.modification = override_modification if override_modification is not None else modification
        
        # content group
        content = self.capitalize(match_groups['content'])
        if has_extended_markup:
            title_rest = map(lambda x: str(x), entry_p.contents[1:])
            self.content = content + ''.join(title_rest)
        else:
            self.content = content

        # append the bug prefix content
        if bug_prefix_content is not None and '(none)' not in bug_prefix_content:
            self.content += ' ' + bug_prefix_content

    def capitalize(self, str):
        if len(str) == 0:
            return str
        return str[0].upper() + str[1:]

    def strip_type(self, type_text):
        return re.sub(r"^(?:\(.*\) - )", '', type_text).strip()
