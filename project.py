#!/usr/bin/env python3

import os


class Project(object):
    ''' A class for storing project information, big and small. '''
    TAB = ' ' * 2

    def __init__(self, name, details='', path='projects', children=None,
                 due_date=None, dependencies=None, level=0):
        ''' Initialise a project.

        'name' must be a unique string in the project tree
        'path' is absolute, or relative to the script running location
        'children' is a dictionary of child projects keyed by name, or a list
            of children names !!! TODO: List initialisation !!!
        'due_date' is a datetime instance
        'dependencies' is a dictionary of projects which must be completed
            before this one can be started, or a list of their names.
        '''
        if not os.path.isdir(path):
            os.makedirs(path) # create target and intermediate directories
        self.name = name
        self.details = details
        self.path = path
        self.child_path = path + '/' + name
        self.children = children if children else {}
        self.due_date = due_date
        self.dependencies = dependencies if dependencies else {}
        self._level = level

    def add_child(self, child):
        ''' '''
        self.children[child.name] = child
        return child

    def create_child(self, name, details='', due_date=None, dependencies={}):
        ''' '''
        return self.add_child(Project(name, details=details,
                path=self.child_path, due_date=due_date,
                dependencies=dependencies, level=self._level+1))

    def remove_child(self, child):
        ''' '''
        self.children.pop(child.name, None)

    def save(self):
        ''' '''
        pass

    def print(self):
        ''' '''
        print(self)
        print()

    def __str__(self):
        ''' '''
        ret_val = 'Project({}'.format(self.name)
        if self.due_date:
            ret_val += ', due:{}'.format(self.due_date)
        ret_val += ')'
        prefix = (self._level + 1) * self.TAB
        if self.details:
            ret_val += '\n' + prefix
            detail_string = '{!r}'.format(self.details)
            if '\n' in detail_string:
                ret_val += ('\n' + prefix).join(detail_string.split('\n'))
            else:
                ret_val += detail_string
        for child in self.children:
            ret_val += '\n'
            ret_val += prefix + '{!s}'.format(self.children[child])

        return ret_val

if __name__ == '__main__':
    p = Project('testing')
    p.print()
    m = p.create_child('more_testing', due_date='12/03/2020')
    m.print()
    p.print()
    e = p.create_child('even_more')
    p.print()
    g = e.create_child('grandchild', due_date='14/03/2020',
                       details='Quite nested down here...')
    g.print()
    p.print()
    p.create_child('some_more', due_date='10/03/2020')
    p.print()
    g.create_child('greatgrand', due_date='13/03/2020')
    g.print()
    p.print()
