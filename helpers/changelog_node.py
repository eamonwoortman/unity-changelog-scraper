import enum


class ChangelogNodeType(enum.Enum):
    MainCategory = 0, # Known Issues, Changed in ...
    ChangeType = 1, # Improvements, Changes, Fixes, ...
    ModificationType = 2 # Added, Removed, ...

class ChangelogNode:
    name:str = ''
    type:ChangelogNodeType = ChangelogNodeType.MainCategory
    children = []
    entries = []

    def __init__(self, name='', type:ChangelogNodeType = ChangelogNodeType.MainCategory):
        self.name = name
        self.type = type
        self.children = []
        self.entries = []

    def key_exists(self, name:str):
        child_node = self.get(name)
        return child_node is not None

    def get(self, name:str) -> 'ChangelogNode':
        if len(self.children) == 0:
            return None
        return next((f for f in self.children if f.name == name), None) 

    def create_child(self, name:str, type:ChangelogNodeType = ChangelogNodeType.MainCategory):
        new_node = ChangelogNode(name, type)
        self.children.append(new_node)
        return new_node

    def add_child(self, new_node:'ChangelogNode'):
        self.children.append(new_node)
        return new_node

    def add_children(self, new_node:list):
        self.children += new_node

    def add_entries(self, new_entries:list):
        self.entries += new_entries

    def toJSON(self):
        d = dict()
        for k,v in self.__dict__.items():
            if k == 'children':
                if len(v) != 0:
                    d[k] = [o.toJSON() for o in v]
            elif k == 'entries':
                if len(v) != 0:
                    d[k] = [o for o in v]
            elif k == 'name':
                if len(v) != 0:
                    d[k] = v
            elif k == 'type':
                d[k] = v.name
        return d
