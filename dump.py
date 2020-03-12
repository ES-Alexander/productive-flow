#!/usr/bin/env python3

from project import Project

main = Project('main')

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

    main.create_sub_project(name, **eval('dict({})'.format(info)))

main.save()
print('new items saved')
