#!/usr/bin/env python3

from project import Project
import os, sys

argc = len(sys.argv)
name = '_main'
path = 'projects'
if argc > 1:
    name = sys.argv[1]
    if argc > 2:
        path = sys.argv[2]

if '/' in path and not os.path.isfile(path + '/{}.txt'.format(name)):
    # parent needs to know about new sub_project being added to
    prev_name_ind = path.rindex('/')
    prev_name = path[prev_name_ind:]
    prev_path = path[:prev_name_ind]
    prev = Project(prev_name, path=prev_path)
    proj = prev.create_sub_project(name, path=path)
else:
    # adding to main, or adding to known sub_project
    proj = Project(name, path=path)

section = '-' * 50
print('', '#' * 50, '',
      'Enter item names, with optional elaboration.',
      "To quit, enter nothing as the name of the next item.",
      'To elaborate, enter parameters and values in the form:',
      'param = value,',
      'making sure to denote values with appropriate Python syntax',
      "(e.g. my_str = 'String',).\n",
      section,
      'Elaboration options include:',
      "details = '''Your detail string''',",
      "sub_projects = ['sub1', ...],",
      "due_date = '20/Mar/2020 - 23:59',",
      "completion_date = 'dd/Mmm/yyyy - hh:mm',",
      "duration = '10.5h' (or '5d'),",
      "scheduled_time = 'xh' or 'xd',",
      "precursors = ['name1', ...],",
      "complete = True (defaults to False)",
      "To finish elaborating, press enter on a blank line.\n",
      section, '', sep='\n')

while True:
    name = input('Next item: ')
    if not name:
        break
    info = ''
    elaboration = input('parameters:\n')
    while elaboration:
        info += elaboration + '\n'
        elaboration = input()

    proj.create_sub_project(name, **eval('dict({})'.format(info)))

proj.save()
print('New items saved\n')
proj.print()
